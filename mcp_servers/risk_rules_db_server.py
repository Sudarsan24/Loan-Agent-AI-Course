"""MCP Server: RiskRulesDB - Provides financial risk analysis tools"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP

mcp = FastMCP("RiskRulesDB")


@mcp.tool()
def calculate_financial_risk(
    applicant_id: str,
    income: float,
    loan_amount: float,
    loan_tenure_months: int,
    existing_liabilities: float,
    credit_score: int,
    employment_type: str,
    age: int,
) -> dict:
    """Calculate comprehensive financial risk metrics including DTI ratio, credit risk level, and anomaly detection."""
    monthly_income = income / 12.0
    monthly_loan_payment = loan_amount / loan_tenure_months
    total_monthly_debt = existing_liabilities + monthly_loan_payment
    dti_ratio = (total_monthly_debt / monthly_income) * 100 if monthly_income > 0 else 100.0

    if credit_score >= 750:
        credit_risk = "low"
    elif credit_score >= 700:
        credit_risk = "medium"
    elif credit_score >= 620:
        credit_risk = "high"
    else:
        credit_risk = "very_high"

    loan_to_income = loan_amount / income if income > 0 else 100.0
    if loan_to_income <= 3:
        loan_risk = "low"
    elif loan_to_income <= 5:
        loan_risk = "medium"
    else:
        loan_risk = "high"

    anomalies = []
    if dti_ratio > 60:
        anomalies.append(f"Extremely high DTI ratio: {dti_ratio:.1f}%")
    if credit_score < 500 and loan_amount > 50000:
        anomalies.append("High loan amount requested with very poor credit score")
    if employment_type == "unemployed" and loan_amount > 10000:
        anomalies.append("Significant loan requested by unemployed applicant")
    if age < 22 and loan_amount > 30000:
        anomalies.append("Young applicant requesting large loan amount")

    risk_parts = []
    if dti_ratio > 43:
        risk_parts.append(f"DTI ratio of {dti_ratio:.1f}% exceeds 43% guideline")
    if credit_risk in ("high", "very_high"):
        risk_parts.append(f"Credit score {credit_score} indicates {credit_risk} risk")
    if loan_risk == "high":
        risk_parts.append(f"Loan-to-income ratio of {loan_to_income:.2f}x is elevated")
    if not risk_parts:
        risk_parts.append("Financial metrics within acceptable ranges")

    return {
        "applicant_id": applicant_id,
        "debt_to_income_ratio": round(dti_ratio, 2),
        "credit_score_risk_level": credit_risk,
        "loan_amount_risk": loan_risk,
        "anomaly_detected": len(anomalies) > 0,
        "anomaly_details": "; ".join(anomalies) if anomalies else None,
        "reasoning": " | ".join(risk_parts),
    }


@mcp.tool()
def get_risk_thresholds() -> dict:
    """Return current risk evaluation thresholds used by the bank."""
    return {
        "max_dti_ratio": 43.0,
        "min_credit_score_approve": 680,
        "min_credit_score_review": 620,
        "max_loan_to_income_ratio": 5.0,
        "min_income": 25000,
        "high_risk_dti": 50.0,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002)
