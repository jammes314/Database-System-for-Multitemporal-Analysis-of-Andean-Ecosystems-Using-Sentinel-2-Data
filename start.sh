#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  EcoMonitor — Start everything after a reboot
#  Usage:  bash start.sh
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="$HOME/Desktop/dbFinalProject"
cd "$PROJECT_DIR" || { echo "ERROR: Project folder not found at $PROJECT_DIR"; exit 1; }

echo ""
echo "🌿 EcoMonitor — Starting services..."
echo "──────────────────────────────────────"

# 1. Start MySQL container
echo "▶ Starting MySQL container..."
docker compose up -d
sleep 5

# Check container is up
if docker ps | grep -q "project_advance_mysql"; then
  echo "  ✓ MySQL is running on port 3306"
else
  echo "  ✗ MySQL failed to start. Check: docker compose logs"
  exit 1
fi

# 2. Activate conda environment and start API
echo "▶ Starting FastAPI..."
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate base

# Start uvicorn in background, log to api.log
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/api.log" 2>&1 &
API_PID=$!
sleep 2

# Check API is responding
if curl -s http://localhost:8000/ > /dev/null; then
  echo "  ✓ API running on http://localhost:8000  (PID: $API_PID)"
else
  echo "  ✗ API did not respond. Check: cat api.log"
  exit 1
fi

echo ""
echo "──────────────────────────────────────"
echo "✅ Everything is running!"
echo ""
echo "  API:      http://localhost:8000"
echo "  Docs:     http://localhost:8000/docs"
echo "  GUI:      Open interfaz.html in your browser"
echo ""
echo "  To stop:  bash stop.sh"
echo "──────────────────────────────────────"
