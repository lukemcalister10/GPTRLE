# staleness_graded_cap.py — D8 ASK 2 PROTOTYPE (GRADED staleness cap; WIRED NOWHERE — joins a candidate
# only on Luke's endorsement). Supersedes the D7 Form A binary design (endorsement WITHHELD, Luke verbatim
# 2026-07-03 in docs/process/SYMPTOM_REGISTER.md family 1). NOT in BAKE CANDIDATE v2.
#
# THE RULE (one sentence): where the stalled branch fires, the player's price moves from the ghost floor
# toward his full uncapped price in proportion to the measured re-realization rate of players with the
# same staleness (gap) and live-output quality (current-season scoring vs replacement) — gap=0 stays cap-
# exempt (the D7 structural piece, Luke-endorsed via McAndrew/Gothard), no live games stays at the floor.
#
#   e = min(e, cap + grade * (e - cap))          [cap = dv*frac, the existing ghost floor — UNCHANGED]
#   grade = 1                     if gap == 0    (sole qualifying season IS season Y — cannot have vanished)
#         = 0                     if g_Y == 0    (no live output this season — ghost anchor)
#         = G_gapclass(q)         otherwise      (q = era-adjusted season-Y avg / REPL[pos]; classes gap=1, gap>=2 POOLED)
#
# DERIVATION (D8, session_2026-07-03/d8_ask2_graded_cap.md; scripts d8_ask2_harvest/analyze/fit.py):
#  - 532 historical fire-population cells (Y=2008..2022, ns==1 & el>=onset & listed-at-Y per the standing
#    LISTED-WINDOW rule), outcome = re-realization of the stale season's level over the next 3 seasons
#    (v = min(fwd_peak/qual_lvl, 1), era-adjusted; robustness: survival + raw ratio give the same shape).
#  - AXIS SELECTED BY DATA: quality q beats the directive's example product g*q (tau +0.234 vs +0.124;
#    q > g*q in 100% of 2000 player-cluster bootstrap resamples); games volume carries NO independent
#    signal within 1-5 games (tau +0.038) — volume enters only structurally (0 games -> no live output;
#    6th game -> qualifying season -> the player graduates out of the population entirely).
#  - GAP CARRIES SIGNAL BEYOND q (gap=1 realizes 0.579 vs gap>=2 0.316 at matched live evidence) ->
#    two curves; gap>=2 POOLED DELIBERATELY (gap 3/4/5+ singly thin: n=29/11/4).
#  - G_c(q) = clip((R_c(q) - Rg) / (Rtop - Rg), 0, 1): R_c = Gaussian-kernel mean (bandwidth widened
#    until eff-n>=35, the D5 standing rule) + isotonic (monotone-in-evidence, structural); Rg = 0.2120
#    (true-ghost baseline: gap>=2 curve at q->0+); Rtop = 0.8024 (gap=0 curve top plateau — the
#    McAndrew/Gothard full-trust region). ZERO invented constants: every number below is a measured
#    kernel/isotonic level; the interpolation endpoints are the two Luke-ruled boundary populations.
#  - The q-matched normalization variant (grade vs R_0(q) at the same q) was computed and REJECTED:
#    non-monotone in q at finite sample (grade fell 0.664->0.595 as q rose 0.8->1.0).
#  - Bootstrap (player-clustered, B=400): Cleary-profile grade 90% CI [0.43, 0.75]; Hardeman-profile
#    [0.05, 0.43] — anchor verdicts hold across the CI.
#
# KNOTS (piecewise-linear, np.interp; flat outside [0.40, 0.80] — exact encoding of the fitted curves):
D8Q  = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
D8G1 = [0.25789, 0.25789, 0.25789, 0.30834, 0.36155, 0.42112, 0.49276, 0.56996, 0.59452]   # gap=1
D8G2 = [0.0,     0.00275, 0.00275, 0.04319, 0.08776, 0.13367, 0.18032, 0.20098, 0.20408]   # gap>=2 (pooled)
#
# EXACT PATCH against _merged_recover.py (canonical 8aed420a) — two anchored replacements:
OLD1 = "# ===== WIRED ev =====\ndef ev(p,Y=2026):"
NEW1 = ("# ===== WIRED ev =====\n"
        "_D8Q=[0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80]   # D8 graded-cap knots (derivation: d8_ask2_graded_cap.md)\n"
        "_D8G1=[0.25789,0.25789,0.25789,0.30834,0.36155,0.42112,0.49276,0.56996,0.59452]\n"
        "_D8G2=[0.0,0.00275,0.00275,0.04319,0.08776,0.13367,0.18032,0.20098,0.20408]\n"
        "def ev(p,Y=2026):")
OLD2 = ("    if el>=onset and ns<=1:                                   # stalled: essentially no production after the window\n"
        "        frac=0.25*max(0.4,1-0.10*(el-onset))*(1.6 if keyruc else 1.0)\n"
        "        e=min(e, dv*frac)")
NEW2 = ("    if el>=onset and ns<=1:                                   # stalled: D8 GRADED release by live-output evidence\n"
        "        frac=0.25*max(0.4,1-0.10*(el-onset))*(1.6 if keyruc else 1.0)\n"
        "        if not any(x['games']>=6 and x['year']==Y for x in p['scoring']):   # gap=0 (sole qual season IS Y) -> exempt (D7 structural piece)\n"
        "            cap=dv*frac; gr=0.0\n"
        "            yrow=[x for x in p['scoring'] if x['year']==Y and x['games']>0]\n"
        "            if yrow:                                          # live output -> graded trust; none -> ghost floor (grade 0)\n"
        "                qv=(yrow[0]['avg']*REF/era.get(Y,REF))/max(MA.REPL.get(pos,1e-9),1e-9)\n"
        "                gp=Y-max(x['year'] for x in p['scoring'] if x['games']>=6 and x['year']<=Y)\n"
        "                gr=float(np.interp(qv,_D8Q,_D8G1 if gp==1 else _D8G2))\n"
        "            e=min(e, cap+gr*max(0.0,e-cap))")

def apply(src):
    """Return the patched engine source. Raises if either anchor is not exactly unique (drift guard)."""
    assert src.count(OLD1) == 1, 'ev() header anchor not unique — engine drifted; re-derive the patch'
    assert src.count(OLD2) == 1, 'stalled-branch anchor not unique — engine drifted; re-derive the patch'
    return src.replace(OLD1, NEW1).replace(OLD2, NEW2)

# INTERACTIONS (proven in d8_ask2_graded_cap.md):
#  (i) floor feature (v2/v3): application order = graded cap INSIDE ev(), then ev_final = max(ev, floor)
#      at the boundary — the floor can only lift a post-grade value that still sits under the ND schedule;
#      order-sensitivity enumerated per player in the D8 read (no double-lift: max() after min() composes
#      to the pointwise upper envelope; grade never reads the floored value).
#  (ii) games-ramp seam: the evidence axis is a RATE (avg vs replacement), not a games count — the grade is
#      invariant to season progress except through the structural gates (first live game arms the grade;
#      the 6th game graduates the player out). The g26 gates share M2/M3's seam variable — composition with
#      M2/M3 at a future v3 is UNMEASURED (v2 untouched this directive); h-M3-blend-seam-noise stays open.
# KNOWN LIMITS (flagged, not silent): forward-year views re-cap at the year click (same as Form A, D7);
#  the gY=0 -> first-game step is a small residual cliff (grade 0 -> 0.258 base for gap=1 — e.g. Clay Hall
#  136 -> ~328 the day he plays); the elevated realized outcomes of zero-games returners (v=0.68 gap=1,
#  survivorship-biased up) are the LTI/returner channel — deliberately NOT priced here, queued to the LTI
#  workstream (hypothesis register: h-gap1-zero-games-returners).
