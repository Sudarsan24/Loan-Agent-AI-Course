"""LangGraph-based Orchestration Engine for Loan Processing Multi-Agent System"""

import asyncio
from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from models.schemas import (
    LoanApplication,
    ApplicantProfileResult,
    FinancialRiskResult,
    LoanDecisionResult,
    ComplianceResult,
)
from agents.applicant_profile_agent import run_applicant_profile_agent
from agents.financial_risk_agent import run_financial_risk_agent
from agents.loan_decision_agent import run_loan_decision_agent
from agents.compliance_agent import run_compliance_agent


class LoanState(TypedDict):
    application: LoanApplication
    profile_result: Optional[ApplicantProfileResult]
    financial_risk_result: Optional[FinancialRiskResult]
    decision_result: Optional[LoanDecisionResult]
    compliance_result: Optional[ComplianceResult]
    error: Optional[str]
    processing_log: list[str]


async def applicant_profile_node(state: LoanState) -> LoanState:
    """Node: Run Applicant Profile Agent"""
    try:
        state["processing_log"].append("Applicant Profile Agent: analyzing applicant background...")
        result = await run_applicant_profile_agent(state["application"])
        state["profile_result"] = result
        state["processing_log"].append(
            f"Applicant Profile Agent: complete. Stability={result.income_stability_score:.0f}, "
            f"Employment Risk={result.employment_risk}"
        )
    except Exception as e:
        state["error"] = f"Applicant Profile Agent failed: {str(e)}"
        state["processing_log"].append(f"ERROR in Applicant Profile Agent: {e}")
    return state


async def financial_risk_node(state: LoanState) -> LoanState:
    """Node: Run Financial Risk Analysis Agent"""
    try:
        state["processing_log"].append("Financial Risk Agent: computing risk metrics...")
        result = await run_financial_risk_agent(state["application"])
        state["financial_risk_result"] = result
        state["processing_log"].append(
            f"Financial Risk Agent: complete. DTI={result.debt_to_income_ratio:.1f}%, "
            f"Credit Risk={result.credit_score_risk_level}"
        )
    except Exception as e:
        state["error"] = f"Financial Risk Agent failed: {str(e)}"
        state["processing_log"].append(f"ERROR in Financial Risk Agent: {e}")
    return state


async def loan_decision_node(state: LoanState) -> LoanState:
    """Node: Run Loan Decision Agent (requires profile and risk results)"""
    if state.get("error"):
        return state
    if not state["profile_result"] or not state["financial_risk_result"]:
        state["error"] = "Missing upstream agent results for decision"
        return state
    try:
        state["processing_log"].append("Loan Decision Agent: synthesizing decision with Claude LLM...")
        result = await run_loan_decision_agent(
            state["application"],
            state["profile_result"],
            state["financial_risk_result"],
        )
        state["decision_result"] = result
        state["processing_log"].append(
            f"Loan Decision Agent: complete. Decision={result.classification}, "
            f"Risk Score={result.risk_score}/100, Confidence={result.confidence_level:.0%}"
        )
    except Exception as e:
        state["error"] = f"Loan Decision Agent failed: {str(e)}"
        state["processing_log"].append(f"ERROR in Loan Decision Agent: {e}")
    return state


async def compliance_node(state: LoanState) -> LoanState:
    """Node: Run Compliance & Action Orchestrator Agent"""
    if state.get("error"):
        return state
    if not state["decision_result"]:
        state["error"] = "Missing decision result for compliance processing"
        return state
    try:
        state["processing_log"].append("Compliance Agent: logging decision and sending notification...")
        result = await run_compliance_agent(state["application"], state["decision_result"])
        state["compliance_result"] = result
        state["processing_log"].append(
            f"Compliance Agent: complete. Case={result.case_id}, Notification Sent={result.notification_sent}"
        )
    except Exception as e:
        state["error"] = f"Compliance Agent failed: {str(e)}"
        state["processing_log"].append(f"ERROR in Compliance Agent: {e}")
    return state


def route_after_profile_risk(state: LoanState) -> str:
    """Route to decision node after parallel profile+risk processing"""
    if state.get("error"):
        return "end"
    return "loan_decision"


def build_loan_graph() -> StateGraph:
    """Build the LangGraph workflow for loan processing."""
    graph = StateGraph(LoanState)

    graph.add_node("applicant_profile", applicant_profile_node)
    graph.add_node("financial_risk", financial_risk_node)
    graph.add_node("loan_decision", loan_decision_node)
    graph.add_node("compliance", compliance_node)

    # Sequential flow: profile -> risk -> decision -> compliance
    graph.set_entry_point("applicant_profile")
    graph.add_edge("applicant_profile", "financial_risk")
    graph.add_edge("financial_risk", "loan_decision")
    graph.add_edge("loan_decision", "compliance")
    graph.add_edge("compliance", END)

    return graph.compile()


async def process_loan_application(application: LoanApplication) -> LoanState:
    """Main entry point: process a loan application through the full agent pipeline."""
    compiled_graph = build_loan_graph()

    initial_state: LoanState = {
        "application": application,
        "profile_result": None,
        "financial_risk_result": None,
        "decision_result": None,
        "compliance_result": None,
        "error": None,
        "processing_log": [f"Orchestrator: received application {application.applicant_id}"],
    }

    final_state = await compiled_graph.ainvoke(initial_state)
    return final_state
