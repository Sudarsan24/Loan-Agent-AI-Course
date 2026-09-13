"""Loan Decision Agent - Synthesizes final loan decision via DecisionSynthesis MCP server and Claude LLM"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
from fastmcp import Client
from models.schemas import (
    LoanApplication,
    ApplicantProfileResult,
    FinancialRiskResult,
    LoanDecisionResult,
)

MCP_URL = "http://localhost:8003/mcp"


async def run_loan_decision_agent(
    application: LoanApplication,
    profile: ApplicantProfileResult,
    financial_risk: FinancialRiskResult,
) -> LoanDecisionResult:
    """Use DecisionSynthesis MCP to get preliminary decision, then Claude to produce final explanation."""
    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "synthesize_loan_decision",
            {
                "applicant_id": application.applicant_id,
                "credit_score": application.credit_score,
                "debt_to_income_ratio": financial_risk.debt_to_income_ratio,
                "credit_score_risk_level": financial_risk.credit_score_risk_level,
                "loan_amount_risk": financial_risk.loan_amount_risk,
                "anomaly_detected": financial_risk.anomaly_detected,
                "income_stability_score": profile.income_stability_score,
                "employment_risk": profile.employment_risk,
                "application_completeness": profile.application_completeness,
                "loan_amount": application.loan_amount,
                "income": application.income,
                "employment_type": application.employment_type.value,
            },
        )
    synthesis_data = result.data

    # Enhance decision explanation with Claude LLM
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    if api_key:
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        model_id = os.getenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "claude-sonnet-4-5")
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        claude_client = anthropic.Anthropic(**client_kwargs)

        prompt = f"""You are a senior loan underwriter. Based on the analysis below, provide a clear, concise explanation
for the loan decision. Be specific about the key factors and actionable advice for the applicant.

Application Summary:
- Applicant: {application.name} (ID: {application.applicant_id})
- Age: {application.age}, Income: ${application.income:,.0f}/year
- Employment: {application.employment_type.value}
- Credit Score: {application.credit_score}
- Loan Amount: ${application.loan_amount:,.0f} over {application.loan_tenure_months} months
- Existing Monthly Liabilities: ${application.existing_liabilities:,.0f}
- Location: {application.location}

Risk Analysis:
- Income Stability Score: {profile.income_stability_score}/100
- Employment Risk: {profile.employment_risk}
- Debt-to-Income Ratio: {financial_risk.debt_to_income_ratio:.1f}%
- Credit Score Risk: {financial_risk.credit_score_risk_level}
- Loan Amount Risk: {financial_risk.loan_amount_risk}
- Anomaly Detected: {financial_risk.anomaly_detected}
{f'- Anomaly Details: {financial_risk.anomaly_details}' if financial_risk.anomaly_details else ''}

Decision: {synthesis_data['classification']}
Risk Score: {synthesis_data['risk_score']}/100
Key Factors: {', '.join(synthesis_data['key_decision_factors'])}

Provide a 2-3 sentence explanation of the decision suitable for the applicant, then 1-2 sentences
of actionable advice. Keep it professional and empathetic. Format: just the explanation text, no headers."""

        message = claude_client.messages.create(
            model=model_id,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        synthesis_data["explanation"] = message.content[0].text

    return LoanDecisionResult(**synthesis_data)
