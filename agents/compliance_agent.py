"""Compliance & Action Orchestrator Agent - Handles regulatory compliance and notifications"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from fastmcp import Client
from models.schemas import (
    LoanApplication,
    LoanDecisionResult,
    ComplianceResult,
)

MCP_URL = "http://localhost:8004/mcp"


async def run_compliance_agent(
    application: LoanApplication,
    decision: LoanDecisionResult,
) -> ComplianceResult:
    """Invoke NotificationSystem MCP to log compliance action and notify applicant."""
    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "process_compliance_action",
            {
                "applicant_id": application.applicant_id,
                "applicant_name": application.name,
                "classification": decision.classification,
                "risk_score": decision.risk_score,
                "explanation": decision.explanation,
                "loan_amount": application.loan_amount,
            },
        )
    data = result.data
    return ComplianceResult(
        applicant_id=data["applicant_id"],
        action_taken=data["action_taken"],
        notification_sent=data["notification_sent"],
        case_id=data["case_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        summary=data["summary"],
    )
