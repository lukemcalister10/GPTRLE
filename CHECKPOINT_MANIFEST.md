# CHECKPOINT_MANIFEST — rl_complete_8aed420a — FINAL cut 2026-07-02
_This chat retired; fresh build chat (new model) takes over from this bundle._

## Identity (all re-verified this cut by verify_restore.sh)
- head `engine/rl_after/_merged_recover.py` = **c47cb43d** (BAKED v2.4; was 8aed420a) · REPL dial `rl_model.py` = **ce4468d6** · store `rl_model_data.json` = **644d1254** · band `data/cm_400.pkl` = **34faa865**
- bundle md5: see the transmittal verdict block (computed on the final tarball).
- BAKED = nothing past `e0ac9c377d1e`. Diagnostic-only session preceded this cut (no head/store/band change).

## verify_restore.sh result (scripted; run on staging AND clean extraction)
```
PASS head=c47cb43d  PASS store=644d1254  PASS band=34faa865
PASS Maric ev(2026)=1409  PASS Langdon ev(2026)=593
PASS harnesses present: _gate1_wf, _gate1_picksplit, s4_matrix_M1v7, s4_render_M1v7
run_panel.sh: RESULT PASS 10/10
VERDICT: 9 PASS / 0 FAIL => RESTORE-VERIFY PASS
```

## Contents (query with tar/grep; not listed here)
whole workspace + vendored deps; engine (rl_after + forward_valuation); store + band; GATE-1 + walk-forward harnesses; board/HTML + JS-parity pipeline (rl_build_html/rl_export/rl_model); rationale docs; `session_2026-07-01/` (reports, notepads, `scripts/`, `decay_proration_overlay.py`); resume docs (START_HERE, CHANGELOG, UNRESOLVED, KICKOFF_PROMPT, PROVENANCE, REQUIRED_INPUTS); `docs/process/` (4 process docs); `docs/archive/HANDOVER_historical.md`; gates `verify_restore.sh` + `doc_lint.py` (doc_lint: 0 FAIL this cut).

## Gaps (see REQUIRED_INPUTS.md)
- **103-player dev-position template ABSENT** — Luke supplies at next kickoff (blocks the dev-position fold-in workstream).
- SHIP_GATES.md and BAKE_CHECKLIST.md not yet created (to be written before the PVC stage / first bake).
