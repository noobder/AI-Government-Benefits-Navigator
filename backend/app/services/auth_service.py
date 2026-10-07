"""Password hashing, JWT access tokens, and refresh-token handling.

Design choices, and why:
- Passwords are hashed with bcrypt directly (not stored, not reversible).
- Access tokens are short-lived JWTs (15 min default) carrying only
  {sub: account_id, role, exp} — enough for `require_user`/`require_admin`
  to authorize a request without a DB round trip on every call.
- Refresh tokens are opaque random strings; only their SHA-256 hash is
  stored in the `refresh_tokens` table, so a stolen DB dump can't be used
  to log in as anyone. They support real logout and rotation, which a
  purely stateless JWT scheme can't do.
- Both tokens are delivered as httpOnly cookies (see api/auth.py), never
  exposed to page JavaScript, to resist XSS token theft.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.account import Account, RefreshToken

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(account: Account) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": account.id,
        "role": account.role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def issue_refresh_token(db: Session, account: Account) -> str:
    settings = get_settings()
    raw_token = secrets.token_urlsafe(48)
    row = RefreshToken(
        account_id=account.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(row)
    db.commit()
    return raw_token


def consume_refresh_token(db: Session, raw_token: str) -> Account | None:
    """Validate a refresh token, revoke it, and return the associated
    account — the caller is expected to issue a fresh pair (rotation)."""
    token_hash = _hash_token(raw_token)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not row:
        return None
    now = datetime.now(timezone.utc)
    expires_at = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=timezone.utc)
    if row.revoked_at is not None or expires_at < now:
        return None
    row.revoked_at = now
    db.commit()
    return db.get(Account, row.account_id)


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token_hash = _hash_token(raw_token)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if row and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)
        db.commit()
