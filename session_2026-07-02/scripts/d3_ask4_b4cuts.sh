#!/bin/bash
# D3 ASK 4 — B4 archaeology: canonical e0ac9c37 engine x 3 seed stores vs shipped b8f9e998.
# Protocol: swap _merged_recover.py to the canonical backup (provably OFF the export dep graph — grep shows
# no import anywhere on rl_export->rl_model->wire_redesign->FV; swap done for protocol fidelity), then run
# rl_export.py once per seed store. Band pinned at cm_400.pkl 34faa865 across all cuts (the pinned identity
# axis; per-store cm retrain would be a further axis, flagged not run). Backup/restore + verify at each step.
set -e
export PATH="/root/rl_venv312/bin:$PATH"
export PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22
export PYTHONPATH=/home/claude/rl_workspace/rl_after:/home/claude/rl_workspace/forward_valuation:/home/user/afl-rl-engine/vendor
RA=/home/claude/rl_workspace/rl_after
OUTDIR=/home/user/afl-rl-engine/session_2026-07-02/scripts/b4cuts
mkdir -p "$OUTDIR"
cd "$RA"
echo "== pre-state =="
md5sum _merged_recover.py rl_model_data.json rl_model_data.json.pre_stage0 rl_model_data.json.stage0 | sed 's|/home.*/||'
cp _merged_recover.py /tmp/_merged_recover.SAVE.py
cp rl_model_data.json /tmp/rl_model_data.SAVE.json
[ -f rl_app_data.json ] && mv rl_app_data.json /tmp/rl_app_data.PRE.json
cp /home/user/afl-rl-engine/backups/_merged_recover.py.e0ac9c37_CANONICAL _merged_recover.py
echo "engine swapped to canonical: $(md5sum _merged_recover.py | cut -c1-8)"
run_cut () {
  local tag=$1 src=$2
  cp "$src" rl_model_data.json
  echo "-- cut $tag: store $(md5sum rl_model_data.json | cut -c1-8) --"
  python3 rl_export.py > "$OUTDIR/export_$tag.log" 2>&1
  md5sum rl_app_data.json | cut -c1-8
  python3 - "$tag" << 'PYEOF'
import json, sys, hashlib
tag = sys.argv[1]
d = json.load(open('rl_app_data.json'))
row = {'tag': tag, 'md5': hashlib.md5(open('rl_app_data.json','rb').read()).hexdigest()[:8],
       'SCALE': d.get('SCALE'), 'intakePickSum': d.get('intakePickSum'), 'intakeFull': d.get('intakeFull'),
       'PVC1': d.get('PVC',{}).get('1'), 'PVC8': d.get('PVC',{}).get('8'), 'active': len(d.get('active',[])),
       'cohort': len(d.get('cohort',[]))}
print(json.dumps(row))
open('/home/user/afl-rl-engine/session_2026-07-02/scripts/b4cuts/summary.jsonl','a').write(json.dumps(row)+'\n')
PYEOF
  rm -f rl_app_data.json
}
: > "$OUTDIR/summary.jsonl"
run_cut reconciled /tmp/rl_model_data.SAVE.json
run_cut pre_stage0 rl_model_data.json.pre_stage0
run_cut stage0 rl_model_data.json.stage0
# shipped reference row
python3 - << 'PYEOF'
import json, hashlib
d = json.load(open('/home/claude/rl_build/rl_app_data.json'))
row = {'tag': 'SHIPPED', 'md5': hashlib.md5(open('/home/claude/rl_build/rl_app_data.json','rb').read()).hexdigest()[:8],
       'SCALE': d.get('SCALE'), 'intakePickSum': d.get('intakePickSum'), 'intakeFull': d.get('intakeFull'),
       'PVC1': d.get('PVC',{}).get('1'), 'PVC8': d.get('PVC',{}).get('8'), 'active': len(d.get('active',[])),
       'cohort': len(d.get('cohort',[]))}
print(json.dumps(row))
open('/home/user/afl-rl-engine/session_2026-07-02/scripts/b4cuts/summary.jsonl','a').write(json.dumps(row)+'\n')
PYEOF
echo "== restore =="
cp /tmp/_merged_recover.SAVE.py _merged_recover.py
cp /tmp/rl_model_data.SAVE.json rl_model_data.json
[ -f /tmp/rl_app_data.PRE.json ] && mv /tmp/rl_app_data.PRE.json rl_app_data.json
md5sum _merged_recover.py rl_model_data.json | sed 's|/home.*/||'
echo "B4CUTS DONE"
