"""Financial Risk Analysis Agent - Evaluates financial risk via RiskRulesDB MCP server"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client
from models.schemas import LoanApplication, FinancialRiskResult

MCP_URL = "http://localhost:8002/mcp"


async def run_financial_risk_agent(application: LoanApplication) -> FinancialRiskResult:
    """Invoke RiskRulesDB MCP tools and return financial risk analysis."""
    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "calculate_financial_risk",
            {
                "applicant_id": application.applicant_id,
                "income": application.income,
                "loan_amount": application.loan_amount,
                "loan_tenure_months": application.loan_tenure_months,
                "existing_liabilities": application.existing_liabilities,
                "credit_score": application.credit_score,
                "employment_type": application.employment_type.value,
                "age": application.age,
            },
        )
    return FinancialRiskResult(**result.data)
