# BUILD notepad — 2026-07-01 — BEFORE vs AFTER value, all 805 players (one sheet)

Deliverable: AFL_RL_before_after_M1v7_805.xlsx — every current player's value BEFORE (baseline head 8aed420a) and AFTER
(M1 + refined-v7 prototype), in one sheet. MEASURE-ONLY, nothing baked. Value = SCAR, as-of 2026 (real engine ev()).

POPULATION = 805 = the current-listed universe: GRP position, not double-count, not phantom, NOT delisted (no dedup,
no pvc-exclude filter). Matches Luke's 805 exactly. 0 duplicate names.

COLUMNS: Player | DraftYr | Pos (drafted->current for switchers) | Pick | Type | Before | After | Δ | Δ%.
Sorted by Before (current value) desc; autofilter + frozen header + red/white/green colour scale on Δ%.

METHOD: Before = baseline ev(p,2026). After = ev(p,2026) with M1 (level bind) + refined-v7 (band wrap) applied. Using the
REAL engine ev() — which for never-played players routes through the SITOUT_RETAIN anchor and DISCARDS the band, so v7
cannot touch rookies (the earlier "rookie crater" was a price_band artifact, not a real-engine one). Rookie-safe by
construction.

RESULT: mean Δ -69 SCAR / -16.8%. down 466 | flat 324 | up 14.
  - 324 FLAT (Δ=0) = mostly never-played/sit-out players (protected via the sit-out anchor) + thin players where M1/v7 net 0.
  - Top by value: Luke Jackson 7731->6879, Sheezel 7287->7208, Daicos 7059->6799, NWM 5730->5770, Xerri 5469->5633 (elite
    move modestly; some down on v7 body-compression, some up on M1).
  - Biggest UP: Lachlan Ash +508 (+12.9%), Finn Callaghan +295, Peatling +71 — M1-fired risers.
  - Biggest DOWN by %: a few near-zero fringe players (e.g. 19->0) = immaterial floor rounding at the very bottom.

STATE unchanged, nothing baked. HOLD.
