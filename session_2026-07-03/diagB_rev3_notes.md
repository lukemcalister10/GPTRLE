# DIAG-B rev3 — session notes (BUILD)
_2026-07-03 · branch `claude/2025-cohort-shortfall-diagnostic-ohwym2` · TARGET = BAKE CANDIDATE v2 (engine `4a134d05`) · estimate posted ~60 min at start._

## Hypothesis register
- **h-Luke-2020-above-pick-sum** → REFUTED: 2020 current/pick-sum = 80.6% (43831/54355). The >100% Luke eyeballed is Measure-1's Current column (vs the cohort's OWN end-of-Yr1 total) = 107% — a denominator misread of TABLE 1, not an engine state. Measure-2 (vs universal PVC) remains the unbuilt view that would answer his question at a glance.
- **h-Luke-2025-unprorated-penalties (the directive's core)** → PARTIAL: channel REAL (+3871 = +10.2% cohort value suppressed by unprorated games machinery; ~78% of the gate-level effect is the ≥6-games sit-out bar alone, the ramps are minor: pole +351, level +0, nqual +150) but NOT most of the gap — 46% of the shortfall vs the recent-5 mean, 28% vs 2023/24. Remainder: cohort size/pick mix (smallest pick sum on record), 35 not-yet-debuted players lawfully at retain×dv, 2023/24 being the two richest Yr1 ratio cohorts in the book, and the sit-out anchor's pre-registered ~16% over-discount.
- **h-book-equals-board for 2025 Yr1** → CONFIRMED byte-exact: 64/64 fresh v2 evals == matrix, max diff 0.
- **NEW finding:** played (≥6g) 2025 draftees price ABOVE nearest-pick 2024 end-of-Yr1 comparables (Duursma 4183 vs Lalor 3280; Lindsay 1454 vs Oliver 398) — the shortfall is concentrated ENTIRELY in the 49 sit-out-classed players.
- **NEW instrument note:** CF3 (LEVEL_RAMP proration) moved the cohort sum by exactly 0 — the GBR band's tree plateaus absorb small lvl_eff shifts; the level ramp is not a live mid-season channel at this cohort's feature values.

## Deliverable ledger
- Two-view book: `s4_render_7147.py` (permanent, display-only; S4_TAG env) + regenerated `docs/AFL_RL_WALKFORWARD_book_v2_4a134d05.xlsx` (28 sheets).
- `d8_matrix_analysis.md` (ASKs 3/4/5a) · `d8_2025_shortfall_verdict.md` (ASK 5 full) · `d8_penalty_code_paths.md` (ASK 5c quotes) · `d8_decomp_log.txt` + `d8_decomp_raw.json` (run evidence) · `scripts/` (both analysis scripts).
- Engine untouched: repo diff = render script + book + session dir + CHANGELOG; canonical workspace restored (md5 8aed420a / 346cffbb verified).

## Estimate + burn
Posted ~60 min; ran ~65 min wall-clock. Engine loads: **1** (v2, workspace-paired, sequential evals: 64-player base + 6 counterfactual passes + 10-player decomposition internals ≈ 500 sequential evals in one process, ~12 min). No blowout. Matrix work (ASKs 1/3/4/5a) needed zero engine loads — the committed v2 matrix carried it.

## What Luke needs to rule on next
1. **The games-ramp rework scope** (owns 2025 mid-season channel + A12 Travaglia/Annable + B6 seam in one fix): the binding item is the unprorated ≥6-games sit-out bar and, larger, the sit-out anchor discarding scoring evidence entirely (Annable: 1 game @ 40.0 → priced 936 while the raw path holds 1571).
2. Whether Measure-2 (vs universal PVC) should be built now — it is the view that would have answered his 2020 eyeball directly.
