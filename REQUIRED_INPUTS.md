# REQUIRED_INPUTS — verify presence at restore-verify; report gaps TURN ONE (PROCESS_CHANGES §7)

| input | where | status at handover | needed for |
|---|---|---|---|
| This tarball (whole workspace + vendored deps) | the bundle itself | PRESENT | everything |
| Engine head `_merged_recover.py` (c47cb43d, BAKED v2.4; was 8aed420a) | engine/rl_after/ | PRESENT (md5 verified) | all pricing |
| Store `rl_model_data.json` (73d23a8e, SINGLE SOURCE) | engine/rl_after/ | PRESENT | all pricing |
| Band pickle `cm_400.pkl` (34faa865) | data/ | PRESENT | conditional prior |
| GATE-1 + walk-forward harnesses | engine/rl_after/ (`_gate1_wf.py`, `_gate1_picksplit.py`, `s4_matrix_M1v7.py`, `s4_render_M1v7.py`) | PRESENT | book / gates |
| Vendored dep — **unidecode ONLY** (nothing else is vendored) | vendor/ | PRESENT (offline-safe) | engine load (name normalisation) |
| Pinned env — **Python 3.12.3, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0** (+openpyxl 3.1.5 for xlsx) | `setup_env.sh` (auto per web session via `.claude/hooks/session-start.sh`) | VERIFIED 2026-07-02: 9/9 exact + panel 10/10 under these pins; other combos drift the GBR/prior path (SHAKEDOWN.md) | exact ev reproduction |
| **103-player dev-position template** | repo root `AFL_RL_DEVELOPMENT_position_template.xlsx` | PRESENT (Development sheet, 103 data rows; README + DevPaths sheets) | dev-position fold-in workstream |
| Board / HTML + JS-parity pipeline | engine/rl_after/ (`rl_build_html.py`, `rl_export.py`, `rl_model.py`) | PRESENT (confirm JS-parity harness runs) | board build / parity gate |
| SHIP_GATES.md (named relativities + structural + baseline gates) | repo root | **PRESENT — FROZEN (02/07/2026)**; post-freeze additions go to V_NEXT.md | stopping rule |
| BAKE_CHECKLIST.md | repo root | PRESENT (created under DIRECTIVE 1, 2026-07-02) | M1+v7 bake |
| ship_gates_check.py | repo root | PRESENT (created under DIRECTIVE 1; run at each candidate head + every bake) | acceptance suite |

**Turn-one action for successor:** `bash bootstrap.sh` FIRST (the engine hardcodes `/home/claude/...` paths — verify FAILs on a clean tree without it), then `bash verify_restore.sh`; then emit a REQUIRED_INPUTS gap report. No known gaps as of 2026-07-02 (DIRECTIVE 1). Web sessions: the SessionStart hook has already run setup_env + bootstrap.
