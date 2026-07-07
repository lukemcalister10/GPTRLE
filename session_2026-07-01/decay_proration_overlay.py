# decay_proration_overlay.py — Phase-2 PROTOTYPE. STATE: PROPOSED (NOT wired, NOT baked, NON-VIABLE as specified).
# Kept DISTINCT from the unbaked head (_merged_recover.py); the engine does NOT import this.
#
# WHAT IT DOES: rebinds cp._swt at INFERENCE ONLY to prorate the prior-season recency decay by the elapsed
# season fraction f for the in-progress season. f = ROUNDS_ELAPSED/ROUNDS_TOTAL (Luke-set, currently 14/24).
#   _swt(yr,Y) = RECENCY_DECAY ** max(0, (Y-yr) - (1-f))   for Y == CURR_YEAR ; original for Y != CURR_YEAR.
# At f=1 (any completed/historical season) it is an EXACT no-op.
#
# HARD RULE: apply AFTER the engine load; NEVER retrain the models (they are loaded from the band pickle).
# Applying before/at training would move historical columns.
#
# NON-VIABILITY FINDINGS (turn-68 prototype; full: session_2026-07-01/BUILD_report_2026-07-01_decay-proration-prototype.md):
#   - INERT at f=1: byte-identical historical (max|Δ|=0 over 60 players × as-of 2022-2025). Bake stays separable. [VERIFIED]
#   - Lifts only ~10% of thin-2026 players: only 6/62 have exposure < LEVEL_RAMP(14); the other 90% are not in the
#     reliability-shrink regime, so the intended channel is inactive (Liberatore +0%, O'Brien +0%). [VERIFIED]
#   - Overcorrects ~35% of on-pace players: 42/121 move >2%, bidirectional (jack-ross +22%, james-jordon -21.5% on a
#     dead-flat 63->63 rate) — the whole-_swt lever also perturbs _lvl_wt and propagates nonlinearly. [VERIFIED]
#   - WHY: the current-season drop is the EXPOSURE-FEATURE / recency-decay channel (cohort-varying, young -48% >> old
#     -26%), not the shrink multiplier, not _lvl_wt, not aging. Right target (decay asymmetry) WRONG lever.
#   - REWORK DIRECTION (for successor, NOT designed): act on the _exposure decay clock for the in-progress season only,
#     scoped to younger/low-exposure players where the model is sensitive, and kept OUT of _lvl_wt. Await Luke's read
#     on whether the exposure/decay loss is fully artifact vs partly correct. See mechanism-pinned report.
#
# Reproduce: load engine in a FRESH process, then `import decay_proration_overlay as O; O.apply(cp)`.
def apply(cp, curr_year=2026, rounds_elapsed=14, rounds_total=24):
    F = float(rounds_elapsed) / float(rounds_total)
    _orig = cp._swt
    def _swt_pro(yr, Y):
        f = F if Y == curr_year else 1.0
        return cp.RECENCY_DECAY ** max(0.0, (Y - yr) - (1.0 - f))
    cp._swt = _swt_pro
    return _orig  # caller may restore with cp._swt = _orig
