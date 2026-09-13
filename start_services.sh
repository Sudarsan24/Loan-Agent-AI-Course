#!/bin/bash
# Start all services for the Loan Evaluation AI System

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Load env vars
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "=============================================="
echo "  🏦 Loan Evaluation AI System - Starting Up"
echo "=============================================="
echo ""

# Kill any existing processes on these ports
for PORT in 8000 8001 8002 8003 8004 8501; do
    fuser -k ${PORT}/tcp 2>/dev/null || true
done
sleep 1

echo "📡 Starting MCP Servers..."
echo "  → ApplicantDB MCP Server (port 8001)"
python3 mcp_servers/applicant_db_server.py &
MCP1_PID=$!
sleep 0.5

echo "  → RiskRulesDB MCP Server (port 8002)"
python3 mcp_servers/risk_rules_db_server.py &
MCP2_PID=$!
sleep 0.5

echo "  → DecisionSynthesis MCP Server (port 8003)"
python3 mcp_servers/decision_synthesis_server.py &
MCP3_PID=$!
sleep 0.5

echo "  → NotificationSystem MCP Server (port 8004)"
python3 mcp_servers/notification_system_server.py &
MCP4_PID=$!
sleep 2

echo ""
echo "🔌 Starting FastAPI Microservice (port 8000)..."
python3 fastapi_service.py &
FASTAPI_PID=$!
sleep 2

echo ""
echo "🌐 Starting Streamlit UI (port 8501)..."
~/.local/bin/streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
UI_PID=$!

echo ""
echo "=============================================="
echo "✅ All Services Started Successfully!"
echo "=============================================="
echo ""
echo "🌐 Streamlit UI:        http://localhost:8501"
echo "⚡ FastAPI Gateway:     http://localhost:8000"
echo "📖 API Documentation:   http://localhost:8000/docs"
echo "🔍 Health Check:        http://localhost:8000/health"
echo ""
echo "MCP Servers:"
echo "  ApplicantDB:          http://localhost:8001"
echo "  RiskRulesDB:          http://localhost:8002"
echo "  DecisionSynthesis:    http://localhost:8003"
echo "  NotificationSystem:   http://localhost:8004"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================="

# Wait and cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $MCP1_PID $MCP2_PID $MCP3_PID $MCP4_PID $FASTAPI_PID $UI_PID 2>/dev/null || true
    echo "All services stopped."
}
trap cleanup EXIT INT TERM

wait
