# decay_proration_overlay.py — Phase-2 PROTOTYPE. NOT BAKED. NOT VIABLE AS SPECIFIED (rework needed).
# Apply at INFERENCE ONLY (after engine load; models never retrained). Kept DISTINCT from head 8aed420a.
# Prorates the prior-season recency decay by elapsed fraction f for the in-progress season (Y=curr_year);
# exact no-op for Y!=curr_year (f=1) -> historical book + M1+v7 curve untouched by construction.
#
# NON-VIABILITY FINDINGS (see docs/process + session_2026-07-01/BUILD_report_*_decay-proration-prototype.md):
#  - INERT at f=1: byte-identical historical (max|delta|=0 over 60 players x 2022-2025).
#  - Lifts ONLY ~10% of thin-2026 players (only 6/62 have exposure<LEVEL_RAMP=14; rest not in shrink regime).
#  - OVERCORRECTS ~35% of on-pace players (>2% move, bidirectional: jack-ross +22%, james-jordon -21.5% flat-rate).
#  - Mechanism pinned (turn 69): g<6 drop = EXPOSURE-FEATURE/recency-decay channel (NOT shrink multiplier,
#    NOT _lvl_wt, NOT aging); cohort-varying young -48% >> old -26%. Right target, wrong lever.
#  - REWORK: act on the _exposure decay clock for the in-progress season only, scoped to younger/low-exposure
#    players, kept OUT of _lvl_wt. Do NOT bake this overlay.
def apply(cp, curr_year=2026, rounds_elapsed=14, rounds_total=24):
    F=float(rounds_elapsed)/float(rounds_total); _orig=cp._swt
    def _swt_pro(yr,Y):
        f=F if Y==curr_year else 1.0
        return cp.RECENCY_DECAY**max(0.0,(Y-yr)-(1.0-f))
    cp._swt=_swt_pro; return _orig
