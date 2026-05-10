#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  EcoMonitor — Stop all services
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="$HOME/Desktop/dbFinalProject"
cd "$PROJECT_DIR"

echo "🛑 Stopping EcoMonitor..."

# Kill uvicorn
pkill -f "uvicorn main:app" && echo "  ✓ API stopped" || echo "  — API was not running"

# Stop Docker
docker compose down && echo "  ✓ MySQL container stopped"

echo "Done."
