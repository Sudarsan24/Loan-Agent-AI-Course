"""MCP Server: DecisionSynthesis - Synthesizes loan decision from agent analyses"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from typing import Optional

mcp = FastMCP("DecisionSynthesis")


@mcp.tool()
def synthesize_loan_decision(
    applicant_id: str,
    credit_score: int,
    debt_to_income_ratio: float,
    credit_score_risk_level: str,
    loan_amount_risk: str,
    anomaly_detected: bool,
    income_stability_score: float,
    employment_risk: str,
    application_completeness: bool,
    loan_amount: float,
    income: float,
    employment_type: str,
) -> dict:
    """Synthesize all risk signals into a final loan classification with risk score and confidence."""
    risk_score = 0.0
    factors = []

    # Credit score contribution (30%)
    if credit_score >= 750:
        risk_score += 10
        factors.append("Excellent credit score")
    elif credit_score >= 700:
        risk_score += 25
        factors.append("Good credit score")
    elif credit_score >= 650:
        risk_score += 45
        factors.append("Fair credit score - moderate risk")
    elif credit_score >= 580:
        risk_score += 65
        factors.append("Poor credit score - high risk")
    else:
        risk_score += 85
        factors.append("Very poor credit score - critical risk")

    # DTI contribution (25%)
    if debt_to_income_ratio <= 30:
        risk_score += 0
        factors.append(f"Healthy DTI ratio of {debt_to_income_ratio:.1f}%")
    elif debt_to_income_ratio <= 43:
        risk_score += 20
        factors.append(f"Acceptable DTI ratio of {debt_to_income_ratio:.1f}%")
    elif debt_to_income_ratio <= 55:
        risk_score += 40
        factors.append(f"Elevated DTI ratio of {debt_to_income_ratio:.1f}%")
    else:
        risk_score += 60
        factors.append(f"Critical DTI ratio of {debt_to_income_ratio:.1f}%")

    # Employment & income stability (20%)
    if employment_risk == "low" and income_stability_score >= 80:
        risk_score += 5
        factors.append("Stable employment with high income consistency")
    elif employment_risk == "medium" or income_stability_score >= 60:
        risk_score += 20
        factors.append("Moderate employment stability")
    else:
        risk_score += 40
        factors.append("Unstable employment or low income stability")

    # Loan amount risk (15%)
    if loan_amount_risk == "low":
        risk_score += 5
        factors.append("Loan amount proportionate to income")
    elif loan_amount_risk == "medium":
        risk_score += 20
        factors.append("Moderate loan-to-income ratio")
    else:
        risk_score += 35
        factors.append("High loan amount relative to income")

    # Anomaly penalty (10%)
    if anomaly_detected:
        risk_score += 20
        factors.append("Anomalies detected in application data")

    # Application completeness
    if not application_completeness:
        risk_score += 10
        factors.append("Incomplete application data")

    # Normalize to 0-100
    risk_score = min(100.0, risk_score / 2.5)

    # Classification logic
    if risk_score <= 35 and credit_score >= 680 and debt_to_income_ratio <= 43 and not anomaly_detected:
        classification = "Approved"
        confidence = 0.85 + (35 - risk_score) / 350
    elif risk_score >= 65 or credit_score < 580 or (anomaly_detected and credit_score < 650):
        classification = "Rejected"
        confidence = 0.80 + (risk_score - 65) / 500
    else:
        classification = "Requires Manual Review"
        confidence = 0.70

    confidence = round(min(0.99, confidence), 2)
    risk_score = round(risk_score, 1)

    return {
        "applicant_id": applicant_id,
        "classification": classification,
        "risk_score": risk_score,
        "confidence_level": confidence,
        "key_decision_factors": factors[:5],  # top 5 factors
        "explanation": f"Loan {classification.lower()} based on risk score of {risk_score}/100. "
                      f"Primary factors: {', '.join(factors[:3])}.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8003)
