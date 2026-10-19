#!/usr/bin/env bash
# Start the minister-confirmed backend and frontend.
# Run from anywhere: bash experiments/minister-confirmed/start.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/backend/venv"

echo ""
echo "  ⚔  Minister Confirmed — The SuperNaturals 2026"
echo "  ────────────────────────────────────────────────"

# ── Backend ──────────────────────────────────────────────────────────────────
echo "  Starting backend on http://localhost:8001 …"
cd "$ROOT/backend"

lsof -ti :8001 | xargs kill -9 2>/dev/null || true

nohup "$VENV/bin/uvicorn" main:app --host 0.0.0.0 --port 8001 --reload \
  > /tmp/minister_backend.log 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID  (log: /tmp/minister_backend.log)"

for i in {1..12}; do
  sleep 1
  if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "  Backend ready ✓"
    break
  fi
done

# ── Frontend ─────────────────────────────────────────────────────────────────
echo "  Starting frontend on http://localhost:5175 …"
cd "$ROOT/frontend"
npm run dev -- --port 5175 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

echo ""
echo "  Open: http://localhost:5175"
echo "  API:  http://localhost:8001/health"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT INT TERM
wait
