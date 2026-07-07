# floor_pricing_clamp.py — D6 PROTOTYPE (Luke's ruling 2026-07-02: the crater floor becomes a PRICING
# FLOOR). NOT BAKED. SCRATCH-BRANCH ONLY. Canonical ev() untouched; this wraps it at the boundary.
#
# Luke's ruling (in writing, D6 directive): the listed ordinary players are "saved by the floor" —
# the B5 crater floor becomes a value clamp standing in for the unpriced q90-97 upside tail, with a
# printed saves-list for visibility on every board run.
#
#   ev_final(p) = max(ev(p), floor_yrs(p) * draftval(p))
#
# Scope: NATIONAL-DRAFT entrants only (type=='ND'); MSD/SSP (type!='ND'), delisted, retired and
# pickless players are NEVER floored — for them ev_final == ev byte-exact. The clamp is a pure lower
# bound: any player whose ev is already at/above floor is untouched byte-exact by construction (max()).
#
# floor_yrs — the signed dev-window schedule (B5, D4) for yrs 1-6, then TWO TAIL VARIANTS:
#   variant 'A' (as signed):        yr7+ flat .05
#   variant 'B' (D5 ASK-3c kernel): yr7 .05, then the derived tail d8 .011 / d9 .012 / d10 .021 / d11+ .012
# Variant choice is LUKE'S RULING — both are wired here so the saves-lists price the decision.
DEV_WINDOW = {1: 0.45, 2: 0.35, 3: 0.28, 4: 0.21, 5: 0.13, 6: 0.09}
TAIL_A = {7: 0.05}                                     # .05 forever (signed schedule)
TAIL_B = {7: 0.05, 8: 0.011, 9: 0.012, 10: 0.021}      # 11+ -> .012 (D5 ASK-3c derived kernel floors)
TAIL_B_DEEP = 0.012

def floor_yrs(yis, variant='A'):
    if yis in DEV_WINDOW:
        return DEV_WINDOW[yis]
    if variant == 'A':
        return TAIL_A.get(yis, 0.05)
    return TAIL_B.get(yis, TAIL_B_DEEP)

def make_ev_final(ev, draftval, delisted, variant='A', year=2026, saves=None):
    """Wrap the engine's ev with the pricing floor. `saves` (optional list) collects
    (player, yis, raw, floor, saved_to) rows for the mandatory saves-list print."""
    def ev_final(p, Y=year):
        v = ev(p, Y)
        if p.get('type') != 'ND' or p.get('_retired') or p.get('_pickless') or delisted(p):
            return v                                   # out of scope: byte-exact passthrough
        yis = Y - int(p.get('year') or 0)
        if yis < 1:
            return v
        fl = floor_yrs(yis, variant) * draftval(p)
        if v >= fl:
            return v                                   # pure lower bound: at/above floor untouched
        if saves is not None:
            saves.append(dict(player=p.get('player'), yis=yis, raw=v, floor=round(fl, 1),
                              saved_to=round(fl), lift=round(fl - v, 1)))
        return round(fl)
    return ev_final
