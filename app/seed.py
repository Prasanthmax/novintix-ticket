"""Seed data – 6 departments, ~10 users across roles, 2 requesters."""

from app.db import SessionLocal
from app.models import Department, User


def seed_data(session=None):
    """Insert seed departments and users. Idempotent."""
    own_session = session is None
    if own_session:
        session = SessionLocal()
    try:
        if session.query(Department).count() > 0:
            return

        depts = {
            "HR": Department(id="dept-hr", code="HR", name="Human Resources"),
            "FIN": Department(id="dept-fin", code="FIN", name="Finance"),
            "IT": Department(id="dept-it", code="IT", name="IT"),
            "CRM": Department(id="dept-crm", code="CRM", name="CRM"),
            "TAG": Department(id="dept-tag", code="TAG", name="Talent Acquisition"),
            "TRIAGE": Department(id="dept-triage", code="TRIAGE", name="Triage"),
        }
        session.add_all(depts.values())
        session.flush()

        users = [
            # Engineers
            User(id="user-hr-eng1", name="Anita HR", role="engineer", dept_id="dept-hr"),
            User(id="user-hr-eng2", name="Ravi HR", role="engineer", dept_id="dept-hr"),
            User(id="user-fin-eng1", name="Meena FIN", role="engineer", dept_id="dept-fin"),
            User(id="user-it-eng1", name="Karthik IT", role="engineer", dept_id="dept-it"),
            User(id="user-tag-eng1", name="Priya TAG", role="engineer", dept_id="dept-tag"),
            User(id="user-crm-eng1", name="Suresh CRM", role="engineer", dept_id="dept-crm"),
            # Leads
            User(id="user-hr-lead", name="Deepa HR Lead", role="lead", dept_id="dept-hr"),
            # Managers
            User(id="user-hr-mgr", name="Vijay HR Mgr", role="manager", dept_id="dept-hr"),
            User(id="user-fin-mgr", name="Latha FIN Mgr", role="manager", dept_id="dept-fin"),
            User(id="user-triage-mgr", name="Arjun Triage Mgr", role="manager", dept_id="dept-triage"),
            # Requesters (no dept)
            User(id="user-req1", name="Requester One", role="requester", dept_id=None),
            User(id="user-req2", name="Requester Two", role="requester", dept_id=None),
        ]
        session.add_all(users)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()

