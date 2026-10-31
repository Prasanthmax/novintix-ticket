"""Audit logging service – insert-only, no UPDATE or DELETE."""

from app.models import AuditLog


def log_audit(
    session,
    *,
    actor_id: str | None,
    action: str,
    resource: str | None = None,
    decision: str = "ALLOW",
    detail: str | None = None,
):
    row = AuditLog(
        actor_id=actor_id,
        action=action,
        resource=resource,
        decision=decision,
        detail=detail,
    )
    session.add(row)
    session.flush()
    return row

