from sqlalchemy.orm import Session

from app.db.models import AuditLog


def record_audit(db: Session, *, actor_id: str, actor_role: str, action: str, target_type: str, target_id: str, request_id: str, correlation_id: str, organization_id: str | None = None, before: dict | None = None, after: dict | None = None, metadata: dict | None = None) -> AuditLog:
    item = AuditLog(
        actor_id=actor_id, actor_role=actor_role, action=action, target_type=target_type, target_id=target_id,
        organization_id=organization_id, request_id=request_id, correlation_id=correlation_id,
        before_snapshot=before, after_snapshot=after, audit_metadata=metadata or {},
    )
    db.add(item)
    return item
