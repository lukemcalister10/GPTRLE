# DIRECTIVE 7 — session notes (BUILD)
_2026-07-02 · branch `claude/ruled-bake-config-v2-ixq8ty` (PR) + `claude/d7-bake-candidate-v2` (candidate) · estimate posted ~3.5h · canonical untouched except Luke-ruled gate amendments._

## Hypothesis register updates
- **h-staleness-cap-lacks-recency-term (D6, NEW then)** → CONFIRMED + FIX DERIVED: gap=0 structural exemption; Gothard 317→1790 exact; 7/807 zero-collateral; gates hold. Awaits Luke's endorsement (design-only, in NO candidate).
- **h-supervisor-A3-range-0.74-0.78 at v2** → REFUTED: measured 0.7307 — BELOW the range; A3 red by 0.019 even at the amended 0.75 bar. Attribution: M3 +0.072 (0.6591→0.7307); cB deletion ≈ +0.001.
- **h-Tsatas-stays-below-1083 at v2** → REFUTED: 1140 (M3 full blend at g26=0); reverts to 979 as fE→1; A8 holds 2.12x. Luke flag.
- **h-cB-deletion-restores-2020-cohort (D5 prediction)** → CONFIRMED at v2: 2020 row 100/113/115/105/107/107 — above yr1 everywhere.
- **h-floor-clamp-breaks-nothing at v2** → CONFIRMED: 0 lowered / 0 non-ND moved / new-B1 156.2 PASS.
- **h-B1-clamp-average-anomaly (ASK 5 ii)** → RESOLVED: index-denominator arithmetic, record explained (not corrected — D6's number was right under its exclusion set).
- **NEW h-M3-blend-seam-noise:** B6 gains a −3pt micro-dip at 7g at v2 (per-rung s differences). Cliff-blend directive territory; logged, ungated.
- **NEW instrument caveat:** verify_restore.sh named-player axes read repo-engine × workspace-cp (par_redesign.py:12 sys.path[0]); mixed-pair reads possible when trees diverge. All D7 measurements were workspace-paired.

## Estimate + burn
Posted ~3.5h at start; ran ~2.5h of wall-clock work. 9 sequential engine loads (v2 default / v2 fE=1 / v2 no-M3 · cap population · head sweep · head+fix sweep · 2 board runs w/ matrix+gate1 chains · recon) + 2 matrix rebuilds + 2 gate1 runs. One wasted load (relative-path outfile bug, fixed). No split needed — all five ASKs delivered.

## What Luke needs to rule on next (in one place)
1. **A3 at 0.7307 vs his 0.75** — the knife-edge bar is now RED by 0.019 at the exact config he ruled. Options: accept red pending the Rozee-level channel work, or re-rule.
2. **Tsatas 1140 > his preferred 1083** (M3 lift, fades by season end) — accept or scope M3's s to exclude zero-current-evidence players.
3. **The staleness-cap fix** (Form A derived; Form B priced) — endorsement puts it in the NEXT candidate.
4. **A14 advisory:** Burgoyne 2092 leaves ±20% lineball at v2 (cB deletion) — PVC-staged, no action forced.
