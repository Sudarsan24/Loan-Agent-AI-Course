"""MCP Server: ApplicantDB - Provides applicant profile analysis tools"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from models.schemas import LoanApplication, ApplicantProfileResult

mcp = FastMCP("ApplicantDB")

EMPLOYMENT_RISK_MAP = {
    "salaried": "low",
    "business_owner": "medium",
    "self_employed": "medium",
    "freelancer": "high",
    "unemployed": "high",
}

EMPLOYMENT_STABILITY_MAP = {
    "salaried": 85.0,
    "business_owner": 70.0,
    "self_employed": 65.0,
    "freelancer": 50.0,
    "unemployed": 10.0,
}


@mcp.tool()
def analyze_applicant_profile(
    applicant_id: str,
    age: int,
    income: float,
    employment_type: str,
    credit_score: int,
    loan_amount: float,
    loan_tenure_months: int,
    existing_liabilities: float,
    location: str,
    name: str,
) -> dict:
    """Analyze applicant profile and return income stability, employment risk, credit history summary."""
    flags = []

    if age < 21:
        flags.append("Applicant under 21 - limited credit history likely")
    if age > 65:
        flags.append("Applicant over 65 - retirement income risk")
    if income < 30000:
        flags.append("Income below $30,000 threshold")
    if not name or name.strip() == "":
        flags.append("Missing applicant name")
    if not location or location.strip() == "":
        flags.append("Missing location information")

    income_stability_score = EMPLOYMENT_STABILITY_MAP.get(employment_type, 50.0)

    if income > 80000:
        income_stability_score = min(100.0, income_stability_score + 10)
    elif income < 40000:
        income_stability_score = max(0.0, income_stability_score - 10)

    if credit_score >= 750:
        credit_history_summary = "Excellent credit history. Long track record of timely payments."
    elif credit_score >= 700:
        credit_history_summary = "Good credit history with minor blemishes."
    elif credit_score >= 650:
        credit_history_summary = "Fair credit history. Some late payments or high utilization."
    elif credit_score >= 580:
        credit_history_summary = "Poor credit history. Multiple delinquencies or defaults."
    else:
        credit_history_summary = "Very poor credit history. Significant risk indicators present."

    employment_risk = EMPLOYMENT_RISK_MAP.get(employment_type, "medium")
    is_complete = len(flags) == 0

    return {
        "applicant_id": applicant_id,
        "income_stability_score": income_stability_score,
        "employment_risk": employment_risk,
        "credit_history_summary": credit_history_summary,
        "application_completeness": is_complete,
        "completeness_flags": flags,
    }


@mcp.tool()
def get_applicant_credit_details(applicant_id: str, credit_score: int, income: float) -> dict:
    """Fetch detailed credit behavior indicators for the applicant."""
    payment_history = "on_time" if credit_score >= 700 else ("mixed" if credit_score >= 620 else "poor")
    credit_utilization = "low" if credit_score >= 720 else ("moderate" if credit_score >= 650 else "high")

    return {
        "applicant_id": applicant_id,
        "payment_history": payment_history,
        "credit_utilization": credit_utilization,
        "estimated_open_accounts": max(1, (credit_score - 300) // 100),
        "derogatory_marks": 0 if credit_score >= 700 else (1 if credit_score >= 620 else 3),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
