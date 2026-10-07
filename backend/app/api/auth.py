from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.api.deps import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, get_current_account
from app.config import get_settings
from app.database import get_db
from app.models.account import Account
from app.schemas.auth import AccountOut, LoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    settings = get_settings()
    secure = settings.cookie_secure_effective
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 3600,
        path="/api/auth",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth")


@router.post("/register", response_model=AccountOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    account = Account(email=payload.email.lower(), password_hash=auth_service.hash_password(payload.password))
    db.add(account)
    db.commit()
    db.refresh(account)

    access_token = auth_service.create_access_token(account)
    refresh_token = auth_service.issue_refresh_token(db, account)
    _set_auth_cookies(response, access_token, refresh_token)
    return account


@router.post("/login", response_model=AccountOut)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.email == payload.email.lower()).first()

    generic_error = HTTPException(status_code=401, detail="Incorrect email or password.")
    if not account or not account.is_active:
        raise generic_error

    now = datetime.now(timezone.utc)
    locked_until = account.locked_until
    if locked_until is not None:
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > now:
            raise HTTPException(status_code=423, detail="Too many failed attempts. Please try again later.")

    if not auth_service.verify_password(payload.password, account.password_hash):
        account.failed_login_attempts += 1
        if account.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            account.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        db.commit()
        raise generic_error

    account.failed_login_attempts = 0
    account.locked_until = None
    account.last_login_at = now
    db.commit()

    access_token = auth_service.create_access_token(account)
    refresh_token = auth_service.issue_refresh_token(db, account)
    _set_auth_cookies(response, access_token, refresh_token)
    return account


@router.post("/refresh", response_model=AccountOut)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Not signed in.")

    account = auth_service.consume_refresh_token(db, raw_token)
    if not account or not account.is_active:
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Session expired, please sign in again.")

    access_token = auth_service.create_access_token(account)
    new_refresh_token = auth_service.issue_refresh_token(db, account)
    _set_auth_cookies(response, access_token, new_refresh_token)
    return account


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        auth_service.revoke_refresh_token(db, raw_token)
    _clear_auth_cookies(response)
    return {"logged_out": True}


@router.get("/me", response_model=AccountOut | None)
def me(account: Account | None = Depends(get_current_account)):
    return account
