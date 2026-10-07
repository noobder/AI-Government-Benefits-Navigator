from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.database import get_db
from app.models.account import Account, AdminAuditLog
from app.schemas.auth import AccountOut
from app.schemas.scheme import SchemeAdminOut, SchemeIn, SchemeUpdate
from app.services import scheme_service

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _log(db: Session, admin: Account, action: str, target_type: str, target_id: str, detail: dict | None = None):
    db.add(
        AdminAuditLog(
            admin_account_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail or {},
        )
    )
    db.commit()


@router.get("/schemes", response_model=list[SchemeAdminOut])
def list_schemes(db: Session = Depends(get_db)):
    return [scheme_service.scheme_to_admin_out_dict(s) for s in scheme_service.list_schemes(db)]


@router.get("/schemes/{scheme_id}", response_model=SchemeAdminOut)
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    scheme = scheme_service.get_scheme(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme_service.scheme_to_admin_out_dict(scheme)


@router.post("/schemes", response_model=SchemeAdminOut, status_code=201)
def create_scheme(payload: SchemeIn, db: Session = Depends(get_db), admin: Account = Depends(require_admin)):
    try:
        scheme = scheme_service.create_scheme(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    _log(db, admin, "scheme.create", "scheme", scheme.id, {"scheme_name": scheme.scheme_name})
    return scheme_service.scheme_to_admin_out_dict(scheme)


@router.put("/schemes/{scheme_id}", response_model=SchemeAdminOut)
def update_scheme(
    scheme_id: str, payload: SchemeUpdate, db: Session = Depends(get_db), admin: Account = Depends(require_admin)
):
    scheme = scheme_service.update_scheme(db, scheme_id, payload)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    _log(db, admin, "scheme.update", "scheme", scheme_id, payload.model_dump(exclude_unset=True))
    return scheme_service.scheme_to_admin_out_dict(scheme)


@router.delete("/schemes/{scheme_id}", status_code=204)
def delete_scheme(scheme_id: str, db: Session = Depends(get_db), admin: Account = Depends(require_admin)):
    deleted = scheme_service.delete_scheme(db, scheme_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scheme not found")
    _log(db, admin, "scheme.delete", "scheme", scheme_id)
    return None


@router.get("/accounts", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).order_by(Account.created_at.desc()).all()


@router.get("/audit-log")
def get_audit_log(db: Session = Depends(get_db), limit: int = 100):
    rows = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": r.id,
            "admin_account_id": r.admin_account_id,
            "action": r.action,
            "target_type": r.target_type,
            "target_id": r.target_id,
            "detail": r.detail,
            "created_at": r.created_at,
        }
        for r in rows
    ]
