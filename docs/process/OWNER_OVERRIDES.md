# OWNER OVERRIDES — signed, owner-set engine behaviours (data-derived elsewhere)

An OWNER OVERRIDE is a place where the engine value is **set by Luke's signed instruction**, not
by a data derivation. It is registered here so no future audit flags the override as a derivation
error: where the override binds, the value is OWNER-SET by design; everywhere else it stays
data-derived. Firing the directive that wires the override IS the signature.

---

## O1 · KPP sit-out retention FLOOR at the nonKPP surface

- **Name:** KPP retention floor (KPP sit-out retention carried up to the nonKPP level).
- **Scope:** KPP (KEY_FWD / KEY_DEF) sit-out retention surface, **BOARD PATH ONLY**. RUC is
  excluded from the comparator (own capped machinery — supervisor spec, stated to Luke pre-fire).
  The backtest/walk-forward machinery is untouched (Luke's D14 backtest exemption).
- **Owner's words (verbatim, Luke 2026-07-03):** "if their yearly value is lower than another
  position, it gets brought up to that level. So if it's higher, fine, but if it's lower, it's
  carried so it can never be the lowest ... whether it's logical or not I can't see KPPs losing
  value for sitting at a faster rate than non KPPs."
  Clarified same day: "I meant KPP sitting penalty by year. Non KPP only. Across each year it applies."
- **Date:** 2026-07-03 (Directive 14; wired at CANDIDATE v2.4).
- **Wired form:** in `engine/rl_after/_merged_recover.py`, `_R_surf('KPP', pick, tau)` returns the
  pointwise **MAX(KPP-derived surface, nonKPP-derived surface)** at every (log-pick, depth), guarded
  by `_BOARD_PATH`. Comparator = nonKPP only (RUC excluded). Applies at EVERY year/depth of the sit.
  Depth monotonicity re-asserted numerically (max of two isotonic-non-increasing curves is
  non-increasing — gate D14c, printed green every gates-board run).
- **Where it binds (owner-set) vs data-derived:** binds where nonKPP > KPP (predominantly depth ≥3,
  and depth ≥1 for the mid-pick band 15–30 where raw KPP d1 retention sits just below nonKPP —
  exactly the "KPPs losing value faster" case the override removes). Binding map printed in
  `session_2026-07-03/d14/d14_ask2_floor.md`. Elsewhere (shallow deep-pick KPP, all RUC) the surface
  stays fully data-derived (D13 R_SURF).
- **Reversal ref:** remove the `if _BOARD_PATH and cls=='KPP'` max() branch of `_R_surf` in
  `engine/rl_after/_merged_recover.py` (returns the pure D13-derived KPP surface). One-line revert;
  no other path depends on the floor.
- **Status:** ACTIVE (candidate v2.4; owner-set; scoped re-audit before bake).
