from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS_OWNER = "business_owner"
    FREELANCER = "freelancer"
    UNEMPLOYED = "unemployed"


class LoanApplication(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier")
    name: str = Field(..., description="Full name of applicant")
    age: int = Field(..., ge=18, le=80, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income in USD")
    employment_type: EmploymentType
    credit_score: int = Field(..., ge=300, le=850, description="FICO credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount in USD")
    loan_tenure_months: int = Field(..., ge=6, le=360, description="Loan tenure in months")
    existing_liabilities: float = Field(default=0.0, description="Existing monthly debt obligations")
    location: str = Field(..., description="City, State")
    application_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ApplicantProfileResult(BaseModel):
    applicant_id: str
    income_stability_score: float = Field(..., ge=0, le=100)
    employment_risk: Literal["low", "medium", "high"]
    credit_history_summary: str
    application_completeness: bool
    completeness_flags: list[str] = []


class FinancialRiskResult(BaseModel):
    applicant_id: str
    debt_to_income_ratio: float
    credit_score_risk_level: Literal["low", "medium", "high", "very_high"]
    loan_amount_risk: Literal["low", "medium", "high"]
    anomaly_detected: bool
    anomaly_details: Optional[str] = None
    reasoning: str


class LoanDecisionResult(BaseModel):
    applicant_id: str
    classification: Literal["Approved", "Rejected", "Requires Manual Review"]
    risk_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=1)
    key_decision_factors: list[str]
    explanation: str


class ComplianceResult(BaseModel):
    applicant_id: str
    action_taken: str
    notification_sent: bool
    case_id: str
    timestamp: datetime
    summary: str


class OrchestratorState(BaseModel):
    application: LoanApplication
    profile_result: Optional[ApplicantProfileResult] = None
    financial_risk_result: Optional[FinancialRiskResult] = None
    decision_result: Optional[LoanDecisionResult] = None
    compliance_result: Optional[ComplianceResult] = None
    error: Optional[str] = None


class LoanApplicationResponse(BaseModel):
    applicant_id: str
    status: str
    classification: Optional[str] = None
    risk_score: Optional[float] = None
    confidence_level: Optional[float] = None
    explanation: Optional[str] = None
    key_factors: Optional[list[str]] = None
    case_id: Optional[str] = None
    full_analysis: Optional[dict] = None
