# BUILD notepad — 2026-07-01 — restore verify + Langdon pole-vs-bar decomposition

## Restore: VERIFIED CLEAN
Bundle `89459a9b` (audit-close re-cut) / engine head `8aed420a` / store pre_stage0 `644d1254` / cm_400 `34faa865` / unidecode vendored-offline.
Panel **PASS 10/10** (byte-identical). Re-price anchors: Maric **1409**, Ed Langdon **593** — both on the FIXED store (OLD store gives 1427 / 1122; not on it).
Practical note: 3 "Langdon"s in the store (Ed, Zac Giles-, Tom) — substring find() collides; target `player=='Ed Langdon'` exactly.

## Task 1 — Langdon pole-vs-bar decomposition
In-process toggle validated (593->1122->593 round-trip, no memoization). Both 2x2 corner anchors reproduce exactly => pre-fix state faithful.

2x2 grid (EV):
                    _fut 50/50 (OLD)   _fut 70/30 (NEW)
  _pos_now GFWD(OLD)     1122 [anchor]      1122
  _pos_now GDEF(NEW)      591               593 [anchor]

Decomposition of the -529 move:
- BAR  (_pos_now GFWD->GDEF) alone: -531  (~100%)
- POLE (_fut 50/50->70/30)   alone: +0 (GFWD row) / +2 (GDEF row)  (~0%)
- interaction +2 (negligible). Shapley: BAR -530, POLE +1.
=> The entire drop is the present-position replacement BAR. The _fut POLE did essentially nothing.

### Mechanism (why)
_pos_now / _fut feed 3 fns: bnow (present bar, rl_model.py:35 = the BAR), gfut (max-weight pos -> curve/peak/runway, :36),
futblend (yr1+ REPL blend, :41), + dual cap-lift (:233, IMPROVING branch only, wt>=45).
For Langdon's fix: gfut=max(_fut) returns GDEF in BOTH 50/50 (tie->first-listed) and 70/30 (70>30) -> curve/peak/runway channel never moved.
Only futblend changed (MID 0.5->0.3), a minor term for a 215-game short-runway veteran -> +2. Cap-lift never fires (declining, not improving).
Meanwhile bar swung GEN_FWD (~67.9) -> GEN_DEF (~75.3) = +7.4 pts/gm on the dominant year-0 term -> the -530.

### PROVENANCE CORRECTION (flag, do NOT re-cut just for this — fold into next real re-cut)
PROVENANCE + CHANGELOG say the drop was "driven by removing the 50% MID pole inflation." Numbers refute on BOTH counts:
 1. Driver is _pos_now (bar), NOT _fut (pole): ~100% vs ~0%.
 2. MID pole weight is DEFLATIONARY not inflationary: adding MID (gfut->MID) LOWERS him (1122->1103; 591->574).
The FIX DECISION is correct (593 is right; both field corrections individually justified; 70/30 fine and near-irrelevant to price).
Only the causal story in the docs is wrong. Worth correcting because attribution accuracy is exactly what the mediocre-overvaluation
work turns on.

### _fut sensitivity (context)
bnow=GDEF, populated mixes: 574-596 (~22 pt span). bnow=GFWD, populated: 1103-1122. MID-heavy LOWERS value (deflationary).
Pole is NOT globally inert for veterans: across DISSIMILAR positions even Langdon moves ~490 pts (KFWD pole->930 vs GDEF->472).
Near-inert in HIS case only because GDEF & MID are similar-bar GENERAL positions.

### Generalisation (apples-to-apples: full GDEF<->MID pole swap at common bar=MID)
  veteran Langdon (215g): 472 vs 443 = 29 pts
  young   Sheezel (79g):  7692 vs 7287 = 405 pts
=> ~14x fade with runway. Pole is a YOUNG-PLAYER / long-runway lever (drives peak/curve/runway, mostly spent for a veteran);
it correctly shrinks for veterans switching among similar positions -> points-over-replacement (bnow) dominates veteran value, as intended.
Residual narrower risk: a veteran whose _fut spans DISSIMILAR buckets (KEY/RUC vs GEN) would still get a large pole contribution.
OFFER (not started unprompted): pole value-share across ALL switchers by career stage, to confirm the fade holds population-wide.

## Status / next
- No state changed, nothing baked, NO re-cut. Store/engine still 644d1254 / 8aed420a. Tarball source dir untouched.
- Pending doc items for next real re-cut: (1) PROVENANCE causal correction for Langdon; (2) md5-axes clarity line for START_HERE (from kickoff).
- HOLDING on the main event (mediocre-overvaluation decomposition) until the supervisor relays the diagnosis-first prompt, per the kickoff.
