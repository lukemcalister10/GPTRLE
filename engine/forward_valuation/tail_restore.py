"""NAMESPACE SPINE (post ONE-price, D4 2026-07-02).

HISTORY: this module held the cont.27 TAIL-RESTORATION (empirical p70/p90 upper-tail restore for pre-debut
MID/KEY_FWD/GEN_DEF) and the cont.27 WIRE-IN ROUTER production_value() (pre-debut par-path / RUC
scorer-borrow pool / established rd.redesign_value) — the function that priced the traded board. Luke's
ONE-price ruling (02/07/2026, in writing) DELETED the board valuation path: the board renders engine ev().
Per deleted layer see BOARD_LAYERS_OBITUARY.md (magnitudes, rationale, deletion commit, resurrection refs).

WHAT REMAINS: bind(par_redesign) and the PR/MA/cp/rd/dp module references. _merged_recover.py (engine head,
frozen 8aed420a) reaches its base modules through this namespace (`TR=W.TR; rd=TR.rd; cp=TR.cp; dp=TR.dp`),
so the spine stays; it owns NO valuation code.
"""
PR = MA = cp = rd = dp = None; RAMP = 22.0

def bind(par_redesign):
    """Wire to a loaded par_redesign module (namespace only; no curves are built here any more)."""
    global PR, MA, cp, rd, dp, RAMP
    PR = par_redesign; MA = PR.MA; cp = PR.cp; rd = PR.rd; dp = PR.dp; RAMP = PR.RAMP
