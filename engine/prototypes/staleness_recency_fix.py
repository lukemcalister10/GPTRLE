# staleness_recency_fix.py — D7 ASK 4 PROTOTYPE (Luke's GO to design; WIRED NOWHERE — joins a candidate
# only on Luke's endorsement). NOT in BAKE CANDIDATE v2. Scratch identity: head 8aed420a + this one-condition
# patch = a9e1c14b (verified: 7/807 movers, all gap=0 cap-population rows; gates incl. new-B1 hold).
#
# THE DEFECT: ev()'s stalled-non-producer branch counts qualifying seasons (>=6g) without asking WHEN the
# one season happened — it cannot tell "appeared once years ago, vanished" (its correct target) from "the
# breakout is happening right now" (Gothard 13g @ 70.2 vs REPL 70.9, engine price 1790, capped to 317).
#
# THE DERIVED EXEMPTION (Form A — structural, zero invented constants; derivation in
# session_2026-07-02/d7_ask4_staleness_recency_fix.md):
#   the cap must not fire when the sole qualifying season IS the season being evaluated (gap == 0):
#   a player cannot have VANISHED from a season still in progress, and the band already prices the
#   live season's quality (released values track output monotonically: 1790 / 1408 / ... / 44).
#
# EXACT PATCH against _merged_recover.py (canonical 8aed420a), inside ev(), replacing the stalled test:
OLD = "    if el>=onset and ns<=1:                                   # stalled: essentially no production after the window"
NEW = (
    "    live = ns==1 and any(x['games']>=6 and x['year']==Y for x in p['scoring'])   "
    "# D7 ASK4 RECENCY EXEMPTION: the sole qualifying season IS the season being evaluated -> not a ghost\n"
    "    if el>=onset and ns<=1 and not live:                      # stalled: essentially no production after the window"
)

def apply(src):
    """Return the patched engine source. Raises if the anchor is not exactly unique (drift guard)."""
    assert src.count(OLD) == 1, 'stalled-branch anchor not unique — engine drifted; re-derive the patch'
    return src.replace(OLD, NEW)

# Chain preserved: an exempted player falls through to the mediocre-for-years elif (el>=onset+2, pr<0.55),
# which stays armed. Generalizes across as-of years (the condition reads year Y's own season), so the
# walk-forward matrix applies the identical rule historically — measured: new-B1 avg peak N=4 RISES to
# 169.2 (vs 160.5 at head) and passes.
#
# Known limits (flagged): forward-year views (Y > store cut) re-cap a gap=0 player at the year click;
# a sub-6-game current breakout is not exempted until game 6 lands (the store's own qualifying bar, kept).
