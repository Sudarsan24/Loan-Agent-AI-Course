"""Streamlit Chatbot UI for Loan Application Submission and Status Display"""

import streamlit as st
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Loan Evaluation System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2e6da4 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        border-left: 4px solid #2e6da4;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .decision-approved {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .decision-rejected {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border: 2px solid #dc3545;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .decision-review {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border: 2px solid #ffc107;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-box {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .log-entry {
        font-family: monospace;
        font-size: 0.85rem;
        background: #1e1e1e;
        color: #00ff88;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        margin: 2px 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1e3a5f, #2e6da4);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 109, 164, 0.4);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "application_submitted" not in st.session_state:
        st.session_state.application_submitted = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def check_api_health():
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def submit_application(payload: dict) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/api/loan/evaluate",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def render_decision_card(classification: str, risk_score: float, confidence: float):
    css_class = {
        "Approved": "decision-approved",
        "Rejected": "decision-rejected",
        "Requires Manual Review": "decision-review",
    }.get(classification, "decision-review")

    icon = {"Approved": "✅", "Rejected": "❌", "Requires Manual Review": "⏳"}.get(classification, "⏳")
    color = {"Approved": "#28a745", "Rejected": "#dc3545", "Requires Manual Review": "#ffc107"}.get(classification, "#ffc107")

    st.markdown(f"""
    <div class="{css_class}">
        <h1 style="color:{color}; margin:0">{icon} {classification}</h1>
        <p style="font-size:1.2rem; margin-top:0.5rem">
            Risk Score: <strong>{risk_score}/100</strong> &nbsp;|&nbsp;
            Confidence: <strong>{confidence:.0%}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_processing_log(log: list[str]):
    st.markdown("**Agent Processing Log:**")
    for entry in log:
        icon = "🔴" if "ERROR" in entry else ("✅" if "complete" in entry.lower() else "⚙️")
        st.markdown(f'<div class="log-entry">{icon} {entry}</div>', unsafe_allow_html=True)


def main():
    init_session_state()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏦 AI-Powered Loan Evaluation System</h1>
        <p>Multi-Agent Agentic AI · Real-time Analysis · Explainable Decisions</p>
    </div>
    """, unsafe_allow_html=True)

    # API Health Check
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ All Systems Online — API, MCP Servers, and Agent Pipeline Ready")
    else:
        st.error("❌ API Service Unavailable — Please ensure all services are running")

    # Architecture diagram in sidebar
    with st.sidebar:
        st.markdown("### 🔧 System Architecture")
        st.markdown("""
        ```
        User (Streamlit UI)
              ↓
        FastAPI Gateway :8000
              ↓
        LangGraph Orchestrator
              ↓
        ┌─────────────────────┐
        │  Agent Pipeline     │
        │  1. Profile Agent   │ ← ApplicantDB :8001
        │  2. Risk Agent      │ ← RiskRulesDB :8002
        │  3. Decision Agent  │ ← DecisionSynth :8003
        │                     │   + Claude LLM
        │  4. Compliance Agent│ ← Notification :8004
        └─────────────────────┘
        ```
        """)

        st.markdown("### 📊 Agent Responsibilities")
        agents_info = [
            ("🧑", "Profile Agent", "Income, Employment, Credit History"),
            ("📊", "Risk Agent", "DTI Ratio, Credit Risk, Anomaly Detection"),
            ("🎯", "Decision Agent", "Classification + Claude LLM Explanation"),
            ("✅", "Compliance Agent", "Audit Log, Notifications, Case ID"),
        ]
        for icon, name, desc in agents_info:
            st.markdown(f"**{icon} {name}**  \n_{desc}_")

        st.markdown("---")
        st.markdown("**Tech Stack**")
        st.markdown("""
        - Streamlit · FastAPI
        - LangGraph · LangChain
        - FastMCP · Claude Sonnet
        - Anthropic Agent SDK
        """)

    # Main content - Application Form
    tab1, tab2, tab3 = st.tabs(["📝 Submit Application", "📈 Analysis Results", "💬 AI Chat Assistant"])

    with tab1:
        st.markdown("### Loan Application Form")
        st.markdown("Complete all fields below to submit your application for AI-powered evaluation.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Applicant Information")
            applicant_id = st.text_input("Applicant ID", value="APP-2024-001", placeholder="APP-XXXX-XXX")
            name = st.text_input("Full Name", value="Jane Smith", placeholder="First Last")
            age = st.number_input("Age", min_value=18, max_value=80, value=35)
            location = st.text_input("Location (City, State)", value="Austin, TX", placeholder="City, ST")

            st.markdown("#### Employment Details")
            employment_type = st.selectbox(
                "Employment Type",
                ["salaried", "self_employed", "business_owner", "freelancer", "unemployed"],
                index=0,
            )
            income = st.number_input("Annual Income ($)", min_value=1000, max_value=10000000, value=85000, step=1000)

        with col2:
            st.markdown("#### Credit & Financial Profile")
            credit_score = st.slider("Credit Score (FICO)", min_value=300, max_value=850, value=720)

            if credit_score >= 750:
                st.success(f"Excellent Credit: {credit_score}")
            elif credit_score >= 700:
                st.info(f"Good Credit: {credit_score}")
            elif credit_score >= 650:
                st.warning(f"Fair Credit: {credit_score}")
            else:
                st.error(f"Poor Credit: {credit_score}")

            existing_liabilities = st.number_input(
                "Existing Monthly Liabilities ($)",
                min_value=0,
                max_value=100000,
                value=500,
                step=100,
                help="Existing monthly debt payments (car, student loans, etc.)"
            )

            st.markdown("#### Loan Request")
            loan_amount = st.number_input(
                "Loan Amount ($)", min_value=1000, max_value=10000000, value=250000, step=5000
            )
            loan_tenure = st.select_slider(
                "Loan Tenure",
                options=[6, 12, 24, 36, 48, 60, 84, 120, 180, 240, 360],
                value=360,
                format_func=lambda x: f"{x} months ({x//12} yrs)" if x >= 12 else f"{x} months",
            )

        # Quick metrics preview
        st.markdown("---")
        st.markdown("#### Pre-submission Financial Health Check")
        monthly_income = income / 12
        monthly_payment = loan_amount / loan_tenure
        dti_preview = ((existing_liabilities + monthly_payment) / monthly_income * 100) if monthly_income > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Monthly Income", f"${monthly_income:,.0f}")
        with m2:
            st.metric("Est. Monthly Payment", f"${monthly_payment:,.0f}")
        with m3:
            dti_color = "normal" if dti_preview <= 43 else "inverse"
            st.metric("Estimated DTI", f"{dti_preview:.1f}%", delta="OK" if dti_preview <= 43 else "HIGH", delta_color=dti_color)
        with m4:
            lti = loan_amount / income if income > 0 else 0
            st.metric("Loan-to-Income", f"{lti:.1f}x")

        st.markdown("---")
        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
        with submit_col2:
            submit_clicked = st.button("🚀 Submit for AI Evaluation", use_container_width=True)

        if submit_clicked:
            if not api_healthy:
                st.error("Cannot submit — API service is not available. Please start all services.")
            else:
                payload = {
                    "applicant_id": applicant_id,
                    "name": name,
                    "age": age,
                    "income": income,
                    "employment_type": employment_type,
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "loan_tenure_months": loan_tenure,
                    "existing_liabilities": existing_liabilities,
                    "location": location,
                }

                with st.spinner("🤖 Multi-Agent AI Pipeline Processing..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("⚙️ Starting agent pipeline...")
                    progress_bar.progress(10)

                    try:
                        status_text.text("🧑 Applicant Profile Agent analyzing...")
                        progress_bar.progress(25)

                        result = submit_application(payload)

                        progress_bar.progress(50)
                        status_text.text("📊 Financial Risk Agent computing metrics...")
                        progress_bar.progress(75)
                        status_text.text("🎯 Decision Agent synthesizing with Claude LLM...")
                        progress_bar.progress(90)
                        status_text.text("✅ Compliance Agent logging decision...")
                        progress_bar.progress(100)

                        st.session_state.last_result = result
                        st.session_state.application_submitted = True

                        st.success("✅ Application processed successfully! View results in the Analysis Results tab.")

                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Application **{applicant_id}** for **{name}** has been processed.\n\n"
                                      f"**Decision: {result.get('classification', 'N/A')}**\n\n"
                                      f"{result.get('explanation', '')}\n\n"
                                      f"Case ID: `{result.get('case_id', 'N/A')}`",
                        })

                    except requests.exceptions.ConnectionError:
                        st.error("Connection error — ensure FastAPI service is running on port 8000")
                    except requests.exceptions.HTTPError as e:
                        st.error(f"API Error: {e.response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab2:
        if not st.session_state.application_submitted or not st.session_state.last_result:
            st.info("📝 Submit an application in the first tab to see detailed analysis results here.")

            # Show sample result structure
            st.markdown("#### Sample Output Preview")
            st.json({
                "classification": "Approved / Rejected / Requires Manual Review",
                "risk_score": "0-100",
                "confidence_level": "0.0-1.0",
                "explanation": "AI-generated explanation from Claude Sonnet",
                "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
                "case_id": "CASE-XXXXXXXX",
            })
        else:
            result = st.session_state.last_result
            full = result.get("full_analysis", {})

            # Main decision
            st.markdown("### Final AI Decision")
            render_decision_card(
                result.get("classification", "Unknown"),
                result.get("risk_score", 0),
                result.get("confidence_level", 0),
            )

            st.markdown(f"**AI Explanation:** {result.get('explanation', 'N/A')}")
            st.markdown(f"**Case ID:** `{result.get('case_id', 'N/A')}`")

            st.markdown("---")

            # Agent results in columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🧑 Applicant Profile Analysis")
                profile = full.get("applicant_profile", {})
                if profile:
                    st.metric("Income Stability Score", f"{profile.get('income_stability_score', 0):.0f}/100")
                    emp_risk = profile.get("employment_risk", "N/A")
                    st.metric("Employment Risk", emp_risk.upper())
                    st.markdown(f"**Credit History:** {profile.get('credit_history_summary', 'N/A')}")
                    flags = profile.get("completeness_flags", [])
                    if flags:
                        st.warning("⚠️ Application Flags:\n" + "\n".join(f"• {f}" for f in flags))
                    else:
                        st.success("✅ Application Complete")

                st.markdown("#### 📊 Financial Risk Analysis")
                risk = full.get("financial_risk", {})
                if risk:
                    dti = risk.get("debt_to_income_ratio", 0)
                    st.metric(
                        "Debt-to-Income Ratio",
                        f"{dti:.1f}%",
                        delta="✓ Healthy" if dti <= 43 else "✗ Elevated",
                        delta_color="normal" if dti <= 43 else "inverse",
                    )
                    st.metric("Credit Risk Level", risk.get("credit_score_risk_level", "N/A").upper())
                    st.metric("Loan Amount Risk", risk.get("loan_amount_risk", "N/A").upper())
                    if risk.get("anomaly_detected"):
                        st.error(f"⚠️ Anomaly: {risk.get('anomaly_details', 'Detected')}")
                    st.markdown(f"**Risk Reasoning:** {risk.get('reasoning', 'N/A')}")

            with col2:
                st.markdown("#### 🎯 Decision Factors")
                factors = result.get("key_factors", [])
                for i, factor in enumerate(factors, 1):
                    st.markdown(f"**{i}.** {factor}")

                st.markdown("#### ✅ Compliance & Audit")
                compliance = full.get("compliance", {})
                if compliance:
                    st.success(f"**Case ID:** {compliance.get('case_id', 'N/A')}")
                    st.info(f"**Action:** {compliance.get('action_taken', 'N/A')}")
                    notification = compliance.get("notification_sent", False)
                    st.markdown(f"**Notification Sent:** {'✅ Yes' if notification else '❌ No'}")
                    st.markdown(f"**Timestamp:** {compliance.get('timestamp', 'N/A')}")

            st.markdown("---")
            st.markdown("#### 🔍 Agent Processing Trace")
            log = full.get("processing_log", [])
            if log:
                render_processing_log(log)

            st.markdown("---")
            if st.button("📄 Export Full Analysis (JSON)"):
                st.download_button(
                    label="Download JSON Report",
                    data=json.dumps(result, indent=2, default=str),
                    file_name=f"loan_analysis_{result.get('applicant_id', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

    with tab3:
        st.markdown("### 💬 AI Loan Assistant")
        st.markdown("Chat with the AI assistant about your loan application, eligibility, or general questions.")

        # Display chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask about your loan application..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate contextual response
            with st.chat_message("assistant"):
                context = ""
                if st.session_state.last_result:
                    r = st.session_state.last_result
                    context = f"\n\nContext: Last application result - {r.get('classification')} with risk score {r.get('risk_score')}/100."

                # Simple rule-based responses + context
                response = generate_assistant_response(prompt, st.session_state.last_result)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


def generate_assistant_response(prompt: str, last_result: dict | None) -> str:
    prompt_lower = prompt.lower()

    if any(w in prompt_lower for w in ["approved", "rejected", "decision", "result", "status"]):
        if last_result:
            cls = last_result.get("classification", "Unknown")
            score = last_result.get("risk_score", 0)
            exp = last_result.get("explanation", "")
            case = last_result.get("case_id", "N/A")
            return (
                f"**Your Latest Application Decision: {cls}**\n\n"
                f"Risk Score: **{score}/100** | Case ID: `{case}`\n\n"
                f"{exp}"
            )
        return "No application has been submitted yet. Please fill out the form in the **Submit Application** tab."

    if any(w in prompt_lower for w in ["improve", "better", "increase", "tips", "advice"]):
        return (
            "**Tips to improve your loan approval chances:**\n\n"
            "1. **Improve Credit Score** — Pay bills on time, reduce credit utilization below 30%\n"
            "2. **Reduce DTI Ratio** — Pay down existing debts before applying\n"
            "3. **Stable Employment** — Salaried employment is viewed most favorably\n"
            "4. **Increase Income** — Consider co-applicant or income documentation\n"
            "5. **Request Appropriate Amount** — Keep loan-to-income ratio below 5x\n"
            "6. **Complete Application** — Ensure all fields are filled accurately"
        )

    if any(w in prompt_lower for w in ["credit score", "credit", "fico"]):
        return (
            "**Credit Score Evaluation Thresholds:**\n\n"
            "| Score Range | Rating | Typical Decision |\n"
            "|------------|--------|------------------|\n"
            "| 750-850 | Excellent | Fast Approval |\n"
            "| 700-749 | Good | Approval Likely |\n"
            "| 650-699 | Fair | Manual Review |\n"
            "| 580-649 | Poor | High Risk / Review |\n"
            "| 300-579 | Very Poor | Likely Rejection |"
        )

    if any(w in prompt_lower for w in ["dti", "debt", "ratio", "income"]):
        return (
            "**Debt-to-Income (DTI) Ratio Guidelines:**\n\n"
            "- **≤ 30%**: Excellent — Strong approval signal\n"
            "- **31-43%**: Acceptable — Standard approval threshold\n"
            "- **44-55%**: Elevated — Manual review likely\n"
            "- **> 55%**: Critical — High rejection risk\n\n"
            "DTI = (Monthly Debt Payments / Monthly Income) × 100"
        )

    if any(w in prompt_lower for w in ["mcp", "agent", "how", "work", "architecture", "system"]):
        return (
            "**How the Multi-Agent System Works:**\n\n"
            "1. **Applicant Profile Agent** → Connects to ApplicantDB MCP Server to analyze income stability, "
            "employment risk, and credit history\n\n"
            "2. **Financial Risk Agent** → Connects to RiskRulesDB MCP Server to compute DTI ratio, "
            "credit risk level, and detect anomalies\n\n"
            "3. **Loan Decision Agent** → Connects to DecisionSynthesis MCP Server + Claude Sonnet LLM "
            "to produce final classification with explanations\n\n"
            "4. **Compliance Agent** → Connects to NotificationSystem MCP Server to log the decision "
            "and send applicant notifications\n\n"
            "All agents are coordinated by a **LangGraph orchestration engine** via a **FastAPI** gateway."
        )

    return (
        "I'm your AI Loan Assistant. I can help you with:\n\n"
        "- Understanding your **application decision** (ask about 'my result')\n"
        "- **Credit score** guidance and thresholds\n"
        "- **DTI ratio** calculation and limits\n"
        "- Tips to **improve your approval chances**\n"
        "- How the **multi-agent system** works\n\n"
        "What would you like to know?"
    )


if __name__ == "__main__":
    main()
