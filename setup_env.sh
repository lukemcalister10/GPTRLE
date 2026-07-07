#!/usr/bin/env bash
# setup_env.sh — provision the PINNED engine environment (START_HERE §2).
# Pins (VERIFIED 9/9 exact + panel 10/10, 2026-07-02):
#   Python 3.12.3 · numpy 2.4.4 · scipy 1.17.1 · scikit-learn 1.8.0 · openpyxl 3.1.5
# Off-pin combos reproducibly drift the GBR/prior-trained path (SHAKEDOWN.md).
# Idempotent. Venv lives OUTSIDE the repo tree at $RL_VENV (default $HOME/rl_venv312).
# Usage:  bash setup_env.sh   then   export PATH="$RL_VENV/bin:$PATH"
set -euo pipefail
VENV="${RL_VENV:-$HOME/rl_venv312}"

PY=""
for c in python3.12 /usr/bin/python3.12; do
  command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
done
[ -z "$PY" ] && { echo "FAIL: no python3.12 on PATH (pin is Python 3.12.3)"; exit 1; }
PYV=$("$PY" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
[ "$PYV" = "3.12.3" ] || echo "WARN: python3.12 is $PYV, pin is 3.12.3 — values policy applies if drift appears"

[ -x "$VENV/bin/python" ] || "$PY" -m venv "$VENV"
"$VENV/bin/pip" install -q numpy==2.4.4 scipy==1.17.1 scikit-learn==1.8.0 openpyxl==3.1.5

GOT=$("$VENV/bin/python" -c 'import sys,numpy,scipy,sklearn,openpyxl; print(sys.version.split()[0], numpy.__version__, scipy.__version__, sklearn.__version__, openpyxl.__version__)')
WANT="3.12.3 2.4.4 1.17.1 1.8.0 3.1.5"
if [ "$GOT" = "$WANT" ]; then
  echo "setup_env PASS  (py numpy scipy sklearn openpyxl) = $GOT"
else
  echo "setup_env MISMATCH: got [$GOT] want [$WANT]"; exit 1
fi
echo "activate: export PATH=\"$VENV/bin:\$PATH\""
