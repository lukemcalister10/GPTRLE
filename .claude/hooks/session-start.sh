#!/bin/bash
# SessionStart hook — Claude Code on the web only. Provisions the PINNED engine
# environment (setup_env.sh) and the absolute /home/claude/... layout
# (bootstrap.sh), and puts the pinned venv first on PATH for the session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
VENV="${RL_VENV:-$HOME/rl_venv312}"

bash "$REPO/setup_env.sh"
bash "$REPO/bootstrap.sh"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export RL_VENV=\"$VENV\"" >> "$CLAUDE_ENV_FILE"
  echo "export PATH=\"$VENV/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
echo "session-start hook: pinned env + bootstrap ready (venv=$VENV)"
