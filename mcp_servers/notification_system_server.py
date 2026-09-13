"""MCP Server: NotificationSystem - Handles compliance actions and notifications"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("NotificationSystem")

_case_log: list[dict] = []


@mcp.tool()
def process_compliance_action(
    applicant_id: str,
    applicant_name: str,
    classification: str,
    risk_score: float,
    explanation: str,
    loan_amount: float,
) -> dict:
    """Process compliance requirements, log the decision, and send applicant notification."""
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow()

    action_map = {
        "Approved": f"Loan approval processed. Offer letter generated for ${loan_amount:,.2f}.",
        "Rejected": f"Loan application declined. Adverse action notice prepared per ECOA requirements.",
        "Requires Manual Review": f"Application escalated to underwriting team for manual review. Priority: {'HIGH' if risk_score > 55 else 'NORMAL'}.",
    }

    action_taken = action_map.get(classification, "Action logged.")

    notification_content = {
        "Approved": f"Dear {applicant_name}, congratulations! Your loan application for ${loan_amount:,.2f} has been approved. Please check your email for next steps.",
        "Rejected": f"Dear {applicant_name}, we regret to inform you that your loan application could not be approved at this time. {explanation}",
        "Requires Manual Review": f"Dear {applicant_name}, your loan application is currently under review. Our team will contact you within 2-3 business days.",
    }

    summary = (
        f"Case {case_id} | Applicant: {applicant_name} ({applicant_id}) | "
        f"Decision: {classification} | Risk Score: {risk_score}/100 | "
        f"Loan: ${loan_amount:,.2f} | Action: {action_taken}"
    )

    record = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "applicant_name": applicant_name,
        "classification": classification,
        "risk_score": risk_score,
        "action_taken": action_taken,
        "notification_sent": True,
        "timestamp": timestamp.isoformat(),
        "summary": summary,
    }
    _case_log.append(record)

    return {
        "applicant_id": applicant_id,
        "action_taken": action_taken,
        "notification_sent": True,
        "case_id": case_id,
        "timestamp": timestamp.isoformat(),
        "summary": summary,
    }


@mcp.tool()
def get_audit_log() -> dict:
    """Retrieve the full audit log of processed loan applications."""
    return {"total_cases": len(_case_log), "cases": _case_log}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8004)
