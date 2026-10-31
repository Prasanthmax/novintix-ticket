"""HAESS Support Platform – configuration constants."""

import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")  # "none" | "ollama" | "gemini"

ROUTING: dict[tuple[str, str], str] = {
    ("HRMS", "PAYROLL_DISCREPANCY"): "HR",
    ("HRMS", "LEAVE"): "HR",
    ("HRMS", "HIRING_QUERY"): "HR",
    ("CRM", "ACCESS"): "CRM",
    ("FIN", "REIMBURSEMENT"): "FIN",
}

RESTRICTED_CATEGORIES: set[str] = {
    "GRIEVANCE", "HARASSMENT", "LEGAL", "SECURITY_INCIDENT",
}

REQUEST_TYPES: dict[str, dict] = {
    "payroll_verification": {
        "target_dept": "FIN",
        "title": "Payroll verification request",
        "fields": {
            "deduction_ref": r"^DED-\d{6}$",
            "payroll_period": r"^\d{4}-(0[1-9]|1[0-2])$",
            "txn_status": ["PENDING", "POSTED", "FAILED", "REVERSED"],
        },
        "reason_codes": ["VERIFY_DEDUCTION", "VERIFY_TXN"],
        "approval_required": True,
        "ttl_hours": 48,
    },
    "technical_diagnosis": {
        "target_dept": "IT",
        "title": "Technical diagnosis request",
        "fields": {
            "service_id": r"^SVC-\d{4}$",
            "error_code": r"^ERR-\d{3,5}$",
            "time_window": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$",
        },
        "reason_codes": ["DIAGNOSE_ERROR"],
        "approval_required": False,
        "ttl_hours": 24,
    },
    "hiring_status_check": {
        "target_dept": "TAG",
        "title": "Hiring status check",
        "fields": {
            "job_req_id": r"^REQ-\d{5}$",
            "candidate_ref": r"^CAND-\d{6}$",
            "stage": ["APPLIED", "SCREENING", "OFFER", "JOINED"],
        },
        "reason_codes": ["VERIFY_STATUS", "VERIFY_OFFER", "DUPLICATE_CHECK"],
        "approval_required": True,
        "ttl_hours": 48,
    },
}

SLA_HOURS: dict[str, int] = {"assign": 1, "task": 24}
ESCALATION_CHAIN: list[str] = ["assignee", "lead", "manager", "TRIAGE coordinator"]

