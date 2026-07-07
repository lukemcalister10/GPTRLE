#!/bin/bash
# ============================================================================
# COMPLETE COLD-START BOOTSTRAP — AFL RL engine, snapshot md5 8aed420a
# Recreates the exact layout the engine's absolute paths expect. OFFLINE-SAFE
# (unidecode is VENDORED, no pip/network needed). Idempotent.
# ============================================================================
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p /home/claude/rl_workspace /home/claude/rl_build /home/claude/rl_vendor

# 1. engine + support modules + harness + pipeline + data files
cp -rf "$HERE/engine/rl_after"          /home/claude/rl_workspace/
cp -rf "$HERE/engine/forward_valuation" /home/claude/rl_workspace/

# 2. absolute-path data deps
cp -f "$HERE/data/cm_400.pkl"                /home/claude/cm_400.pkl
cp -f "$HERE/data/rl_build/rl_app_data.json" /home/claude/rl_build/rl_app_data.json

# 3. VENDORED unidecode (offline; no pip). Placed on PYTHONPATH via run_panel/ENV.
cp -rf "$HERE/vendor/unidecode" /home/claude/rl_vendor/unidecode

# 4. the rl_after symlink par_redesign.py inserts on sys.path
ln -sfn /home/claude/rl_workspace/rl_after /home/claude/rl_after

# 5. AUTHORITATIVE STORE = the ONE source of truth engine/rl_after/rl_model_data.json, copied verbatim in step 1.
#    (One-source rewire 2026-07-05: the .pre_stage0 / .stage0 lookalikes are DELETED; the store is no longer
#    reconstituted from a backup here -- it stands alone. Nothing to do in this step.)

M=$(md5sum /home/claude/rl_workspace/rl_after/_merged_recover.py | cut -c1-8)
C=$(md5sum /home/claude/cm_400.pkl | cut -c1-8)
S=$(md5sum /home/claude/rl_workspace/rl_after/rl_model_data.json | cut -c1-8)
U=$(python3 -c "import sys; sys.path.insert(0,'/home/claude/rl_vendor'); import unidecode; print('OK')" 2>/dev/null || echo FAIL)
# GUARD 5 (boot-store): the seed above copies from THIS checkout, so the workspace store/head/band MUST now
# equal the pinned expected (data/expected_boot.json). Assert it hard and HALT — a bootstrap that leaves a
# stale store in the workspace is the exact failure this hardening exists to make impossible.
RL_REPO="$HERE" python3 "$HERE/boot_guard.py" bootstrap \
  /home/claude/rl_workspace/rl_after/rl_model_data.json \
  /home/claude/rl_workspace/rl_after/_merged_recover.py \
  /home/claude/cm_400.pkl || { echo "bootstrap FAILED: seeded workspace does not match the pinned store (see above)"; exit 1; }
echo "bootstrap OK"
echo "  engine md5     : $M   (candidate: F1/F2 one-source rewire)"
echo "  cm_400 md5     : $C   (expect 34faa865)"
echo "  store md5      : $S   (single source; no .pre_stage0/.stage0 lookalikes; Guard 5 asserted == pinned)"
echo "  unidecode      : $U   (vendored, offline)"
echo "  ENV (with vendor): PYTHONPATH=/home/claude/rl_workspace/rl_after:/home/claude/rl_vendor"
echo "  next: bash $HERE/run_panel.sh"
