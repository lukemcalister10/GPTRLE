# SHAKEDOWN — remote-container setup verify — 2026-07-02
_Branch `claude/shakedown-verify-setup-hahsox`. Head `8aed420a`, store `644d1254`, band `34faa865` (all md5 PASS). No engine work performed._

## verify_restore.sh — VERDICT: 7 PASS / 2 FAIL
- PASS: all three md5 axes (head/store/band); all four harnesses present.
- FAIL: `Maric ev(2026) = 1426` (expected 1409, +1.2%); `Langdon ev(2026) = 611` (expected 593, +3.0%).
- 10-panel: 5/10 exact — Daicos 7059, Moore 177, Goad 545, Smillie 896, Green 741 (all deterministic/no-games paths).
  Drifted: Bontempelli 3102/3101, Sheezel 7286/7287, Gawn 2111/2126, Reid 3511/3523, Ward 1775/1782.
- Drift is REPRODUCIBLE (identical across repeat runs and across numpy 2.4.6 vs 2.3.5) and confined to the
  GBR/prior-trained path. Cause UNKNOWN; ranked hypotheses: (1) Python 3.11.15 here vs original container
  interpreter (version undocumented); (2) scipy version; (3) platform libm float differences. Two mechanisms
  tried, stopping per CONTEXT_BUDGET_RULES.

## doc_lint.py — 0 FAIL, 4 WARN
Warns: stale status words in CHECKPOINT_MANIFEST.md:23, docs/UNRESOLVED.md:7,28, docs/KICKOFF_PROMPT.md:9. Cut-gating state: PASS.

## Environment differences from documented env
1. **numpy/sklearn/openpyxl/scipy were NOT importable on clean restore.** REQUIRED_INPUTS.md row "Vendored deps
   (numpy/sklearn/unidecode, etc.) | vendor/ | PRESENT" is inaccurate — `vendor/` holds ONLY unidecode.
   Installed via pip (network available here): scikit-learn==1.8.0 (the documented pin), numpy 2.3.5,
   scipy 1.17.1, openpyxl 3.1.5, joblib 1.5.3.
2. **Python 3.11.15** at /usr/local/bin/python3. Original interpreter version is undocumented — recommend pinning it.
3. **`bash verify_restore.sh` alone is insufficient on a clean tree** — the engine hardcodes
   `/home/claude/rl_workspace/...`; `bootstrap.sh` must run first (START_HERE §0 three-step resume omits it).
4. KICKOFF_PROMPT.md lives at `docs/KICKOFF_PROMPT.md`, not repo root.

## REQUIRED_INPUTS gaps (turn-one report)
Known: 103-player dev-position template ABSENT (Luke supplies); SHIP_GATES.md and BAKE_CHECKLIST.md not yet created.
New: the vendored-deps row above needs correction at next re-cut.

## Write access
This file's commit + push is the end-to-end write-access proof.
