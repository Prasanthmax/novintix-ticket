"""SQLAlchemy ORM models – 9 tables per the spec."""

import uuid
import json
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Integer, ForeignKey, DateTime, Boolean,
)
from sqlalchemy.orm import relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=_uuid)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # requester | engineer | lead | manager
    dept_id = Column(String, ForeignKey("departments.id"), nullable=True)


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=_uuid)
    number = Column(String, unique=True, nullable=False)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    source_app = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="OPEN")
    owner_dept_id = Column(String, ForeignKey("departments.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    priority = Column(String, nullable=False, default="NORMAL")
    tier = Column(String, nullable=False, default="T1")
    audience_depts_json = Column(Text, nullable=False, default="[]")
    escalation_level = Column(Integer, nullable=False, default=0)
    assign_due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)

    @property
    def audience_depts(self) -> list[str]:
        return json.loads(self.audience_depts_json)

    @audience_depts.setter
    def audience_depts(self, val: list[str]):
        self.audience_depts_json = json.dumps(val)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    owner_dept_id = Column(String, ForeignKey("departments.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    template_title = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")
    due_at = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=_now)


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=_uuid)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)


class PublicUpdate(Base):
    __tablename__ = "public_updates"
    id = Column(String, primary_key=True, default=_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)


class SharedContext(Base):
    __tablename__ = "shared_contexts"
    id = Column(String, primary_key=True, default=_uuid)
    from_task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    to_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    request_type = Column(String, nullable=False)
    fields_json = Column(Text, nullable=False, default="{}")
    reason_code = Column(String, nullable=False)
    note = Column(String, nullable=True)
    payload_hash = Column(String, nullable=False)
    approval_required = Column(Boolean, nullable=False, default=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class TicketEvent(Base):
    __tablename__ = "ticket_events"
    id = Column(String, primary_key=True, default=_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    type = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(String, primary_key=True, default=_uuid)
    actor_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=True)
    decision = Column(String, nullable=False)  # ALLOW | DENY
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)

