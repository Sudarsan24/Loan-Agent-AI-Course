"""FastAPI Microservice - Loan Application REST API Gateway"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from models.schemas import LoanApplication, LoanApplicationResponse
from orchestrator.graph import process_loan_application

app = FastAPI(
    title="Loan Evaluation AI System",
    description="Multi-Agent Agentic AI system for automated loan application analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Loan Evaluation AI", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/loan/evaluate", response_model=LoanApplicationResponse)
async def evaluate_loan_application(application: LoanApplication):
    """
    Submit a loan application for AI-powered multi-agent evaluation.

    The request flows through:
    1. Applicant Profile Agent (ApplicantDB MCP)
    2. Financial Risk Analysis Agent (RiskRulesDB MCP)
    3. Loan Decision Agent (DecisionSynthesis MCP + Claude LLM)
    4. Compliance & Action Agent (NotificationSystem MCP)
    """
    try:
        final_state = await process_loan_application(application)

        if final_state.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Processing error: {final_state['error']}",
            )

        decision = final_state.get("decision_result")
        compliance = final_state.get("compliance_result")
        profile = final_state.get("profile_result")
        risk = final_state.get("financial_risk_result")

        full_analysis = {
            "processing_log": final_state.get("processing_log", []),
            "applicant_profile": profile.model_dump() if profile else None,
            "financial_risk": risk.model_dump() if risk else None,
            "decision": decision.model_dump() if decision else None,
            "compliance": {
                "case_id": compliance.case_id if compliance else None,
                "action_taken": compliance.action_taken if compliance else None,
                "notification_sent": compliance.notification_sent if compliance else False,
                "timestamp": compliance.timestamp.isoformat() if compliance else None,
                "summary": compliance.summary if compliance else None,
            } if compliance else None,
        }

        return LoanApplicationResponse(
            applicant_id=application.applicant_id,
            status="processed",
            classification=decision.classification if decision else "Error",
            risk_score=decision.risk_score if decision else None,
            confidence_level=decision.confidence_level if decision else None,
            explanation=decision.explanation if decision else "Processing failed",
            key_factors=decision.key_decision_factors if decision else [],
            case_id=compliance.case_id if compliance else None,
            full_analysis=full_analysis,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/api/loan/sample")
async def get_sample_application():
    """Return a sample loan application payload for testing."""
    return {
        "applicant_id": "APP-2024-001",
        "name": "Jane Smith",
        "age": 35,
        "income": 85000,
        "employment_type": "salaried",
        "credit_score": 720,
        "loan_amount": 250000,
        "loan_tenure_months": 360,
        "existing_liabilities": 500,
        "location": "Austin, TX",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
