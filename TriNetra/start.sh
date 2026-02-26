#!/usr/bin/env bash
# TriNetra – Start backend (Flask + Supabase) and React frontend together
# Usage: ./start.sh
# Stop:  Press Ctrl+C  (kills both processes)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend-react"
ENV_FILE="$SCRIPT_DIR/.env"
VENV="$BACKEND_DIR/venv/bin/python3"

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ████████╗██████╗ ██╗███╗   ██╗███████╗████████╗██████╗  █████╗ "
echo "     ██╔══╝██╔══██╗██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗"
echo "     ██║   ██████╔╝██║██╔██╗ ██║█████╗     ██║   ██████╔╝███████║"
echo "     ██║   ██╔══██╗██║██║╚██╗██║██╔══╝     ██║   ██╔══██╗██╔══██║"
echo "     ██║   ██║  ██║██║██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║"
echo "     ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝"
echo -e "${NC}"

# ── Check .env ────────────────────────────────────────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
  echo -e "${RED}✗  .env not found. Copy .env.example → .env and fill in your Supabase keys.${NC}"
  exit 1
fi

SUPABASE_URL=$(grep -E "^SUPABASE_URL=" "$ENV_FILE" | cut -d= -f2-)
SUPABASE_KEY=$(grep -E "^SUPABASE_KEY=" "$ENV_FILE" | cut -d= -f2-)

if [[ -z "$SUPABASE_URL" || "$SUPABASE_URL" == "https://your-project-ref.supabase.co" ]]; then
  echo -e "${YELLOW}⚠  SUPABASE_URL not set – running in SQLite fallback mode.${NC}"
else
  echo -e "${GREEN}✓  Supabase: $SUPABASE_URL${NC}"
fi

# ── Check Node / npm ──────────────────────────────────────────────────────────
if ! command -v npm &>/dev/null; then
  echo -e "${RED}✗  npm not found. Install Node.js first.${NC}"
  exit 1
fi

# ── Install Python deps if needed ─────────────────────────────────────────────
if [[ ! -f "$BACKEND_DIR/venv/bin/python3" ]]; then
  echo -e "${CYAN}→  Creating Python venv…${NC}"
  python3 -m venv "$BACKEND_DIR/venv"
fi

echo -e "${CYAN}→  Checking Python dependencies…${NC}"
# Only install if key packages are missing (avoids rebuilding pandas from source)
if ! "$BACKEND_DIR/venv/bin/python3" -c "import flask, pandas, supabase" 2>/dev/null; then
  echo -e "${CYAN}   Installing missing packages (this may take a moment)…${NC}"
  "$BACKEND_DIR/venv/bin/pip" install -q --prefer-binary -r "$SCRIPT_DIR/requirements.txt"
else
  echo -e "${GREEN}✓  Python dependencies already satisfied.${NC}"
fi

# ── Install JS deps if needed ─────────────────────────────────────────────────
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo -e "${CYAN}→  Installing npm packages…${NC}"
  npm --prefix "$FRONTEND_DIR" install --silent
fi

# ── Cleanup handler ───────────────────────────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo -e "\n${YELLOW}→  Shutting down…${NC}"
  [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null
  echo -e "${GREEN}✓  All services stopped.${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${CYAN}→  Running Supabase setup / seed check…${NC}"
(
  cd "$SCRIPT_DIR"
  set -a; source "$ENV_FILE"; set +a
  "$VENV" setup_supabase.py
)
SETUP_STATUS=$?
if [[ $SETUP_STATUS -ne 0 ]]; then
  echo -e "${RED}✗  Supabase setup failed – see above. Fix .env and retry.${NC}"
  exit 1
fi
echo ""

# ── Start Flask backend ───────────────────────────────────────────────────────
echo -e "${CYAN}→  Starting Flask backend on http://localhost:5001 …${NC}"
(
  cd "$BACKEND_DIR"
  set -a; source "$ENV_FILE"; set +a
  "$VENV" app.py
) &
BACKEND_PID=$!

# Give backend a moment to start before launching frontend
sleep 2

# ── Start React frontend ──────────────────────────────────────────────────────
echo -e "${CYAN}→  Starting React dev server on http://localhost:5173 …${NC}"
npm --prefix "$FRONTEND_DIR" run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅  TriNetra is running!${NC}"
echo -e "   Frontend : ${CYAN}http://localhost:5173${NC}"
echo -e "   Backend  : ${CYAN}http://localhost:5001${NC}"
echo -e "   API docs : ${CYAN}http://localhost:5001/api/health${NC}"
echo -e "   Press ${YELLOW}Ctrl+C${NC} to stop both services.\n"

# ── Wait for either process to exit ──────────────────────────────────────────
wait "$BACKEND_PID" "$FRONTEND_PID"
