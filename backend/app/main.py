import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import admin, auth, chat, dashboard, eligibility, help as help_api, profile, schemes, voice
from app.api.auth import limiter
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.services.auth_service import hash_password
from app.services.scheme_service import seed_database
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _run_migrations() -> None:
    """Bring the database schema up to date via Alembic instead of a bare
    Base.metadata.create_all(). create_all() only creates tables that don't
    exist yet — it silently does nothing when an existing deployment's table
    is missing a newly added column (exactly what happened when the
    `translations` column was added to `schemes`: the container crash-looped
    with "column schemes.translations does not exist" against the old
    volume). `alembic upgrade head` handles both a brand-new database (via
    the baseline migration) and an existing one that needs incremental
    changes applied, so this is safe to run unconditionally on every boot.
    """
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    backend_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    alembic_ini = os.path.join(backend_dir, "alembic.ini")
    cfg = Config(alembic_ini)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    cfg.set_main_option("sqlalchemy.url", get_settings().database_url)

    # Adopting Alembic on a database that pre-dates it (created by an older
    # version of this app's own create_all() bootstrap, before Alembic was
    # introduced): it already has the baseline tables but no alembic_version
    # row, so a plain "upgrade head" would try to CREATE TABLE things that
    # already exist. Detect that one-time case and stamp the baseline
    # revision first — a genuinely fresh database has neither table and
    # upgrades normally from scratch.
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if "schemes" in existing_tables and "alembic_version" not in existing_tables:
        logger.info("Adopting Alembic on a pre-existing database: stamping baseline revision.")
        command.stamp(cfg, "57cbad419aba")

    command.upgrade(cfg, "head")


def _seed_first_admin(db) -> None:
    from app.models.account import Account

    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        return
    email = settings.admin_email.lower()
    if db.query(Account).filter(Account.email == email).first():
        return
    db.add(Account(email=email, password_hash=hash_password(settings.admin_password), role="admin"))
    db.commit()
    logger.info("Seeded initial admin account for %s.", email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _run_migrations()
    except BaseException:
        # BaseException, not Exception: Alembic's command layer can raise
        # SystemExit on some failures, which would otherwise crash the
        # process silently (exactly what happened while debugging this —
        # the container crash-looped with no visible traceback at all).
        # Fall back to create_all so a fresh dev environment still boots
        # even if Alembic itself can't run for some reason — an existing
        # database genuinely missing a column will still fail loudly
        # downstream, which is correct: limping along on a stale schema
        # silently would be worse.
        logger.exception("Alembic migration failed; falling back to Base.metadata.create_all().")
        Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_database(db)
        logger.info("Seeded/verified %s schemes into the database.", count)
        _seed_first_admin(db)
    finally:
        db.close()
    yield


settings = get_settings()

app = FastAPI(
    title="AI Government Benefits Navigator",
    description="Helping citizens discover, understand, and access government benefits.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # Auth now uses httpOnly cookies (see api/auth.py), so credentials must
    # be allowed. Same-origin deployments (the docker-compose/nginx setup,
    # and local dev via the Vite proxy) don't strictly need this — cookies
    # are sent automatically for same-origin requests regardless — but a
    # split-origin deployment (frontend and backend on different hosts)
    # does, which is why CORS_ORIGINS must be an exact origin (not "*") for
    # cookie auth to work cross-origin at all; browsers refuse to combine a
    # wildcard origin with credentialed requests.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak stack traces or crash the process on an unexpected error.

    Per the app's trust principles: if something goes wrong server-side, say
    so plainly instead of returning a hallucinated or malformed response.
    """
    from fastapi.responses import JSONResponse

    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Something went wrong on our side. Please try again, or check the official government "
            "source directly if this keeps happening."
        },
    )

app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(schemes.router)
app.include_router(eligibility.router)
app.include_router(voice.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(help_api.router)


@app.get("/api/health")
def health():
    """Liveness + readiness check for orchestrators (docker-compose, k8s, etc).
    Verifies the database is actually reachable, not just that the process is up."""
    from sqlalchemy import text

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.exception("Health check: database is not reachable.")
        db_ok = False
    finally:
        db.close()

    status_code = 200 if db_ok else 503
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=status_code, content={"status": "ok" if db_ok else "degraded", "database": db_ok})


@app.get("/api/metrics")
def metrics():
    """Actual measured metrics only — never fabricated user numbers."""
    from app.database import SessionLocal
    from app.models.scheme import Scheme
    from app.models.user import User
    from app.models.conversation import Conversation

    db = SessionLocal()
    try:
        return {
            "schemes_indexed": db.query(Scheme).count(),
            "categories": sorted({s.category for s in db.query(Scheme).all()}),
            "languages_supported": ["en", "hi", "ta"],
            "profiles_created": db.query(User).count(),
            "conversations_handled": db.query(Conversation).count(),
            "note": "These are actual counts from the local database, not projected impact figures.",
        }
    finally:
        db.close()
