# cont.28 VALUATION AUDIT (2026-06-27) — CORRECTED FINAL RECORD + GEN_DEF FIX SHIPPED

> Read after `START_HERE.md`. Began as a read-only audit of the SHIPPED 400-tree board; the one real bug it found
> (mid-pick GEN_DEF ceiling) has now been **SHIPPED + RE-BAKED** (`rl_app_data.json` 603,839 → 605,719).
> **This doc was rewritten after the investigation overturned its first conclusion. The early framing — "non-MID
> positions are under-drafted, calibrate every position's draft/cost to ≈1.0" — was WRONG and is recorded below as a
> CLOSED dead-end so it is not reopened.** Net result: exactly ONE real bug (mid-pick GEN_DEF ceiling); everything else
> is validated or sound.
>
> **SHIP OUTCOME (2026-06-27):** `HIGH_TAIL` += GEN_DEF. Board +0.31% (+1880); **8 movers, ALL pre-debut GEN_DEF**, 4
> guards hold (pk1-6 untouched; KEY_DEF/KEY_FWD/MID unmoved). Cohort book: **GEN_DEF draft/cost 0.44 → 0.53** (genuine
> under-valuation recovered; yr4 peak/cost 1.02 unchanged → the fix touches only the pre-debut/draft column). SCOPE:
> PROSPECTS only — Kyle/Zeke (established, 3g/10g) unreachable; temporary pre/just-debuted inconsistency logged → closed
> by **U28-D** (the asymmetry thread, now sized; see UNRESOLVED). Side-observation (eyeballed, not a guard breach): a few
> deep-pick low-games prospects moved large (Jakob Ryan pk28 g1 74→515; Tew Jiath pk37 g1 83→443) and the prospect curve
> is mildly non-monotonic in pick — the flat-realized-ceiling property the restoration already uses for MID/KEY_FWD.

## THE ONE REAL BUG — mid-pick GEN_DEF ceiling excluded from tail restoration  [SHIPPED — pre-debut only]
`tail_restore` is applied only to `HIGH_TAIL={'MID','KEY_FWD'}`; GEN_DEF was excluded on a cont.27 call ("no high tail to
clip, 103 vs 102") made at the TOP pick, which missed the mid-pick gap. Per-tier test (`_pertier_ceiling.py`):

| GEN_DEF tier | realized best-3 p90/p95/max | pooled band p90 | sliced band p90 | verdict |
|---|---|---|---|---|
| pk1-6 | 109/110/110 | 112 | 110 | reaches elite — LEAVE |
| pk7-12 | 94/99/100 | 94 | 93 | **CAPPED** |
| pk13-20 | 99/102/111 | 94 | 91 | **CAPPED** (max 111, band 94) |
| pk21-40 | 92/97/109 | 91 | 93 | **CAPPED** |

A young mid-pick defender's UPPER tail is clipped below what defenders drafted in his own tier actually achieved — so his
optionality (the chance he becomes elite, which the established board proves happens) is underpriced. This is what starves
the young defenders (Kyle pk14→43, Carmichael, Zeke). KEY_DEF is NOT capped (band tracks its genuinely lower realized
elite — leave it, like KEY_FWD). pk1-6 GEN_DEF already reaches elite (112 ≥ 110) — leave it.

**FIX (surgical, awaiting Luke's go — NOT yet built):** add `GEN_DEF` to `HIGH_TAIL`. The existing max-guarded restore
then lifts ONLY tiers below their own realized anchor (pk7-40 → defenders' realized p95 ≈ 100) and leaves pk1-6 untouched.
Anchored to **defenders' own** realized elite, per tier. Explicitly NOT KEY_DEF, NOT KEY_FWD, NOT pk1-6, NOT a 1.0 target.
After building: re-run `_pertier_ceiling.py` (ceilings), `_backtest_book.py` (cohort), and re-price Kyle/Carmichael/Zeke +
a guard that the proven defenders and pk1-6 don't move.

## CLOSED DEAD-ENDS — do NOT reopen
1. **"Calibrate every position's draft/cost to ≈1.0."** WRONG — position-blind, it would re-flatten positions and rebuild
   PVC, destroying the differentiation that is the redesign's entire point. Positions are correctly worth different
   fractions of pick cost (`_backtest_book.py` by-position): MID 0.99, GEN_FWD 0.81, KEY_DEF 0.62, KEY_FWD 0.66, GEN_DEF
   0.44, RUC 1.04. The target is each position's OWN validated worth, never 1.0.
2. **"Non-MID positions are under-drafted (a bug)."** WRONG for the position FRACTIONS. KEY_FWD 0.66 ∈ its validated 40-70%
   (Luke's trade history: Thilthorpe pk7-not-2, Darcy 8-not-2, Kings sliding; + economic check: undebuted pk5 KPF ≈ 53% of
   an established gun). Defender low MEDIAN is validated (β floor 0.28; Quaynor pk13→369, the 370-1000 cluster — par-level
   defenders sit on the replacement cliff). These markdowns STAY.
3. **Cross-position band pooling depressing thin positions.** RULED OUT (`_pooling_check.py`, `_pertier_ceiling.py`): the
   GBM is architecturally pooled (one quantile GBR per quantile, position via one-hot) BUT a position-ONLY sliced model
   matches the pooled band within ±2-3 in every tier. Slicing by position changes nothing — it is NOT the lever. Also: the
   shipped par-path DRAFT band already reproduces each position's realized best-3 (p90 within ±8).
4. **Exposure ramp too fast (the Kyle/Zeke crater).** RULED OUT as the cause (`_ramp_test.py`): for a low-early defender
   (first-season 40-55) the model projects peak p50=79 vs realized 64 — GENEROUS, not crating; a 3-game sample is
   par-protected (w=0.14, value 684) and only falls as games CONFIRM a sub-par level (20g→316, correct for a 49-avg
   defender below replacement); defender recovery from a low start (34%) ≈ MID (36%). The crater is replacement-proximity
   (proj 79 ≈ REPL 78) + the capped ceiling (bug #1), NOT ramp speed. Year-1-then-climb = option resolution; the cohort
   book is coherent in aggregate (draft 0.78 → yr4 1.27, no crater-then-balloon).

## VALIDATED / SOUND (confirmed this session — leave alone)
- Per-position draft/cost fractions (the markdowns are the redesign working). The draft→yr4 cohort climb (GEN_DEF
  0.44→1.02) is option resolution: busts delist to 0, the upper-tail hits (already priced at draft) survive. No arbitrage —
  you cannot pick the survivor at draft.
- The shipped draft bands are faithful to realized per-position outcomes (p90 ±8). KEY_FWD markdown correct. KEY_DEF
  ceiling correct. Architecture sound.
- REPL by group (the value floor): MID 80.1, RUC 78.5, GEN_DEF 78.3, GEN_FWD 70.9, KEY_DEF 68.4, KEY_FWD 67.8. (A defender
  projected to ~79 is ~1 above replacement → low value; this is why the GEN_DEF MEDIAN is correctly low.)

## SECONDARY ITEMS (real, individual-level, separate from the GEN_DEF ceiling)
- Recency decay 0.72 lags improvers (B.Smith lvl_wt 106 vs 2025-26-only 118.7; 41% of weight pre-2024) → Smith≈Serong;
  captaincy computed off the regressed band (p90 117.8) not his 122 → elite captains under-credited. Lever: faster decay.

## CONSERVATION / BOARD TOTAL — held PROVISIONAL
Board total below PVC-sum is mostly PVC being ~28% rich (picks over-priced as assets; cohort reaches 1.27× cost by yr4).
BUT the GEN_DEF ceiling cap is genuine under-valuation of young defenders' upside, so the ceiling fix will recover SOME
real value. Do NOT attribute the whole gap to PVC until the ceiling fix is built and `_backtest_book.py` + board total are
re-run. The PVC→realized-floor migration remains the separate lever for the residual.

## DIAGNOSTIC SCRIPTS (all banked in `forward_valuation/`; env below; run from `/home/claude/rl_after`)
- `_backtest_book.py` — cohort book, aggregate + by-position (the coherence/objection test).
- `_pertier_ceiling.py` — THE decisive test: per-tier band vs that tier's own realized elite + sliced-vs-pooled (pooling check).
- `_ramp_test.py` — ramp vs realized recovery + the crater curve.
- `_pooling_check.py` — shipped par-path draft band vs realized best-3 per position.
- `_ceiling_test.py` — realized best-3 distribution + elite-defender peaks vs young band.
- `_decomp.py` / `_par_check.py` / `_hard_check.py` / `_gendef_check.py` — the earlier per-player / par-mechanism / VOR work.

**ENV (par-centred / shipped):**
```
PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_REPL_DROP_FWD=4 RL_REPL_DROP_OTHER=2 \
RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22
```
All load `/home/claude/cm_400.pkl` (banked in workspace; placed by `bootstrap.sh`; regenerable via `PR.retrain()` @400).

## SURVIVORSHIP (standing rule, honoured throughout)
Every test here retains busts (as 0/low) and excludes censored cohorts. The realized per-tier elite includes the players
who washed out. This is the pattern that's bitten repeatedly — the established board proves an outcome (elite defenders)
that a young-side model can miss; the per-tier test is how it was caught.

## STATUS
Shipped board UNCHANGED. One fix specified and awaiting go (GEN_DEF mid-pick tail restoration). Nothing built.
