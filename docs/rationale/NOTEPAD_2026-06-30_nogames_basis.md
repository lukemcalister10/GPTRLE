# Notepad — turn response, 2026-06-30 (no-games override: data basis + estimator lock)

Method-lock, no re-levelling. Engine e0ac9c377d1e, nothing baked.

1. TERMINALS/SHAPE WERE PLACEHOLDER. The PEAK 0.85/0.70/0.50 + TERM 0.40/0.30/0.20 + linear interp were round
placeholders, not read off data (the clean -0.10 KPP steps were the tell). The ACTUAL data, on the authoritative
basis (daEV WQ6 ratio, still-listed-at-N, busts=0, vs group/normal-dev baseline = the canonical 0.76 form):
  RUC     N1-5: 0.76 0.97 0.50 0.40 0.44   (n 89,26,12,6,5)
  KPP     N1-5: 0.59 0.71 0.52 0.14 0.18
  nonKPP  N1-5: 0.45 0.47 0.39 0.31 0.45
Shape = hump at N2 (survival signal, washout 44%->1%) then decline to a NON-ZERO floor (sat3+ 0% washout -> kept
projects, not washouts; RUC terminal ~0.40 not 0). Per-position sat4-5 thin (n=4-6) -> pool. So the real shape is
hump-then-decline-to-nonzero, NOT the linear 0.40/0.30/0.20 placeholder. Levels still deferred to PVC.

2. 0.40 vs 0.76 DECOMPOSITION: 0.76 = daEV(realised|sat>=1)/daEV(realised|ALL) [daEV central tendency, GROUP-baseline
denom]. 0.40 = median(realised/draftval|sat>=1) [median, DRAFTVAL denom]. Gap = (i) central tendency p50 vs daEV
(same draftval denom: median 0.40 vs daEV 3.44) + (ii) denominator draftval vs group-baseline (daEV 3.44 vs 0.76).
Different measurement on two axes.

3. LOCKED estimator = daEV(WQ6) over still-listed-at-N, busts=0 (info a priced player has). That conditioning is why
the shape is non-monotone N1<N2.

4. "0.76" is STILL-LISTED-AT-N, not eventually-played: it includes never-played-but-listed as 0 (not over-credited);
_N>=N is itself ~still-listed (a delisted bust's record ends, dropping out once N>delist year). Correct conditioning.

5. WQ6 == CURVE weighting: YES. WQ6=[0.18x5,0.10] over [q10,30,50,70,90,97] is defined+used identically in price6
(_merged_recover) and the book/CURVE engine (_book_engine). dp.WQ=[0.2]x5 over quintiles is the internal prior-band
SHAPE, not the EV aggregator. The retention daEV uses WQ6 -> same basis as price6 and the curve.

6. FLAG for the level step (not resolved): the clean <1 retention reproduces 0.76/0.97 ONLY vs the group/normal-dev
baseline; the same daEV vs DRAFTVAL is >1 (RUC 3.44, sat cohort skews deep-pick). Since baseline=draftval is fixed,
the retention must be re-expressed on the draftval basis (or the override multiply the normal-dev value) so retention
and multiplicand share one ruler. Deferred with the levels.

Relativities remain the bake gate; levels wait for the PVC. Nothing baked.
