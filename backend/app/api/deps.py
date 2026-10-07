"""Auth dependencies shared across routers.

Access tokens travel as an httpOnly cookie, never read by page JavaScript,
so these read `request.cookies` rather than an Authorization header.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import Account
from app.services.auth_service import decode_access_token

ACCESS_COOKIE_NAME = "bn_access_token"
REFRESH_COOKIE_NAME = "bn_refresh_token"


def get_current_account(request: Request, db: Session = Depends(get_db)) -> Account | None:
    """Best-effort auth: returns the Account if a valid access token cookie
    is present, otherwise None (never raises) — for routes that behave
    differently for guests vs signed-in users without requiring login."""
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    account = db.get(Account, payload.get("sub"))
    if not account or not account.is_active:
        return None
    return account


def require_user(account: Account | None = Depends(get_current_account)) -> Account:
    if not account:
        raise HTTPException(status_code=401, detail="Sign in required.")
    return account


def require_admin(account: Account = Depends(require_user)) -> Account:
    if account.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return account
