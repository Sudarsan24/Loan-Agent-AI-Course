"""Applicant Profile Agent - Analyzes applicant background via ApplicantDB MCP server"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client
from models.schemas import LoanApplication, ApplicantProfileResult

MCP_URL = "http://localhost:8001/mcp"


async def run_applicant_profile_agent(application: LoanApplication) -> ApplicantProfileResult:
    """Invoke ApplicantDB MCP tools and return applicant profile analysis."""
    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "analyze_applicant_profile",
            {
                "applicant_id": application.applicant_id,
                "age": application.age,
                "income": application.income,
                "employment_type": application.employment_type.value,
                "credit_score": application.credit_score,
                "loan_amount": application.loan_amount,
                "loan_tenure_months": application.loan_tenure_months,
                "existing_liabilities": application.existing_liabilities,
                "location": application.location,
                "name": application.name,
            },
        )
    return ApplicantProfileResult(**result.data)
