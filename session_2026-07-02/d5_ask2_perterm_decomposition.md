# D5 ASK 2 — M1+v7 PER-TERM DECOMPOSITION — design + measurement (NOTHING WIRED)
_2026-07-02 · candidate basis engine `fb39d88a` / cp `5ac8b162` (M2 on) · store `644d1254` · same-builder (7147) matrix rebuilds per term · all engine evals sequential · canonical head restored + md5-verified after every swap._

## Design — what the overlay's terms ARE and how each was toggled
The M1+v7 overlay decomposes into exactly three separable terms (plus M2, which rides in the candidate basis and is toggled by its own kill-switch as context):

| term | what it does | the off-toggle (anchored one-line patch on the candidate engine) | variant md5 |
|---|---|---|---|
| **M1** | level up-branch lift: a proven player earns S_M1=0.46 of a current-over-recency gap when gap ≥ TOL_M1=5 and a recent ≥12-game season sits above the recency level | rebind `cp._lvl_eff` from `_inferM1` back to `_lvl_eff_infer` (v7 + M2 stay on) | `34343293` |
| **v7-cB** | upper-quantile band compression: cB = 0.47·clip((effs−1)/3, 0, 1) squeezes bb[3]/bb[4] toward the band median — bites players WITH accumulated evidence (effs ≥ ~1), i.e. the band's speculative upside above proven level | `cB=0.0` (M1 + asc + M2 stay on) | `ca9df823` |
| **v7-asc** | age-scaled q97 tail: asc = interp(age, [20,22,24,27] → [1.0,0.76,0.58,0.40]) compresses bb[5] — bites by AGE, hardest ≥24y | `asc=1.0` (M1 + cB + M2 stay on) | `442b92a3` |
| M2 (context) | in-progress-season exposure proration (f=0.545, s=clip(1−g26/11,0,1)) | `RL_EXPO_F=1` kill-switch (byte-exact identity, D4-verified) | engine unchanged |

Each term-off state got the full measurement suite (A2 trio / A3 / A8 / full B5 sweep) AND a same-builder walk-forward matrix rebuild (`s4_matrix_7147.py`, the D4 candidate/control builder) — five sequential engine loads + three matrix builds this session.

## The term table
| state | A2 Curtis/Ward | 2020 cohort d4/d5/d6 idx | new-B1 avg row (d1..d7) | new-B1 verdict | A3 (pre-LTI) | B5 count | note |
|---|---|---|---|---|---|---|---|
| CANDIDATE (all on) | 0.875 (1163/1329) | 97/98/95 | 100 130 138 148 142 134 119 | PASS pk4 147.6 | 0.658 | 82 | baseline |
| M1 OFF | 0.737 (979/1329) | 94/92/93 | 100 130 138 145 138 130 115 | PASS pk4 145.2 | 0.692 | 82 | M1's marginal effect: Curtis **+184**, Ward +0 (TOL knife-edge), A3 **−0.034**, 2020 **+3.9%** (a lift), B5 ±0 |
| v7-cB OFF | 0.822 (1358/1653) | 105/106/103 | 100 132 143 157 154 145 128 | PASS pk4 156.6 | 0.659 | 76 | cB's marginal effect: Curtis **−195** (−14.4%), Ward **−324** (−19.6%), 2020 **−8.0%**, B5 +6 |
| v7-asc OFF | 0.858 (1254/1462) | 105/106/102 | 100 131 142 154 151 142 126 | PASS pk4 154.3 | 0.666 | 53 | asc's marginal effect: Curtis −91, Ward −133, A3 −0.008, 2020 **−7.9%**, B5 **+29** |
| M2 OFF (RL_EXPO_F=1, context) | 0.873 (1156/1324) | — (matrix cells byte-shared on completed seasons) | — | — | 0.642 | 83 | M2's marginal effect: A3 **+0.016**, B5 −1, else ~nil |
| CONTROL / HEAD (all off) | 0.652 (1162/1782) | 109/110/110 | 100 132 146 160 158 148 131 | PASS pk4 160.5 | 0.692 | 51 | head engine; same-builder control matrix |

## (a) WHICH term produces the Curtis compression (the improver-profile squeeze)
**v7-cB.** Curtis's per-term ledger at the candidate point: cB **−195** (−14.4% off his no-cB level 1358), asc −91, M1 **+184** — netting to 1163 ≈ his head value 1162. The prior fingerprint (Curtis 66% vs Ward 77% of matched-producer medians, D3) is the cB squeeze: cB bites exactly the players whose value rides the band's upper quantiles above a modest proven level — the improver profile. Note the A2 ratio is NOT the right lens for this: cB squeezes Ward even harder (−19.6%), so turning cB off makes A2 look worse (0.822) while making both players richer — the squeeze is absolute, the ratio motion is Ward-side. M1 is the term doing the intended discrimination: Curtis's real 2026 step-up earns +184; Ward's +3.0 gap (< TOL 5) earns nothing.

## (b) WHICH term produces the 2020 markdown — and is it the mediocrity channel?
**Split verdict, and the split IS the finding.** Per-term markdown on the 2020 cohort (d4-6 value, candidate matrix vs each term-off matrix), with the concentration profile as the discriminating test:

| term (ON at the margin) | 2020 d4-6 markdown | on top-quartile (producers) | middle | bottom half | Spearman(control value, Δ%) |
|---|---|---|---|---|---|
| M1 | **+3.9%** (a lift) | +4.6% | +0.1% | −0.0% | +0.466 (p=6.5e-04) |
| v7-cB | −8.0% | −6.8% | −15.1% | −8.8% | **−0.024 (p=0.87 — NO value-rank structure)** |
| v7-asc | −7.9% | −5.0% | −19.4% | **−33.6%** | **+0.706 (p=1e-08 — strongly mediocrity-concentrated)** |
| WHOLE OVERLAY | −11.6% | −7.2% | −30.4% | −32.5% | +0.527 (p=8.5e-05) |

- **v7-asc IS the mediocrity-compression channel** — its markdown climbs monotonically down the value order (producers −5%, bottom half −34%; Errol Gulden, the cohort's star, −1.4% under the whole overlay). This is the engine agreeing with Luke's shocking-draft read: the 2020 markdown concentrates on its mediocre members.
- **v7-cB's share is INDISCRIMINATE** — no correlation with value rank (ρ=−0.02): it marks the cohort down roughly evenly, producers included, the same squeeze that compresses Curtis. On the concentration test this half of the markdown behaves like an artifact, not a quality judgment.
- Either single term off restores the 2020 index above 100 at d4-6 (105/106/103 without cB; 105/106/102 without asc): the below-100 dip needs BOTH compressions stacked.
- Full per-player rows: `d5_ask2_2020_concentration.md` (whole-overlay); term tables regenerable from `scripts/d5_ask2_termtable.py`.

**Discriminating evidence in one sentence: the 2020 markdown is two channels — the age-tail term (v7-asc) concentrates it on the cohort's mediocre members exactly as Luke's read predicts (ρ=+0.71, bottom half −34% vs producers −5%), while the band-compression term (v7-cB) marks the cohort down indiscriminately (ρ≈0) and is simultaneously the term that squeezes Curtis — so the mediocrity mechanism is real AND it travels with an artifact that Luke's overlay ruling can now separate.**

## What this hands Luke for the overlay ruling
- M1: repairs A2's discrimination (Curtis lift, Ward none) at a cost of A3 −0.034 — M1 is the WHOLE M1+v7 A3 cost; v7 contributes ~nothing to A3.
- v7-asc: the desired mediocrity/veteran markdown (2020 concentration + A8's Berry compression) — but owns the B5 blowout (+29 offenders, all in the veteran tail the ASK-3c floors re-derive).
- v7-cB: the one term with no clean defense on this evidence — indiscriminate cohort markdown + the improver squeeze; its A2-ratio "help" is Ward-side compression, not Curtis-side repair.
- New-B1 (Luke's redefined law) passes at EVERY state measured — the overlay ruling is free of B1 blockage.
