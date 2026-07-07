> ℹ DATED APPEND-LOG. Newest section is current; older sections are history. For current engine state (md5 7f7d7f76, GATE 1 PASSED, recover/fade) read START_HERE.md — do not read an old 'REMAINING/GATE-1 flatness' line here as live.

# MEASUREMENT — HISTORICAL COHORT VALUE-TRAJECTORY (2026-06-28)

THE governing-frame target. Run BEFORE Stage 2, on the **pre-Stage-0** engine (the real current-engine behavior).
Data shipped: `/tmp/traj_out.json` (in the tarball). Scripts: `rl_after/_traj_measure.py` (+ `_traj_sanity.py`,
`_traj_leakcheck.py`, `_traj_bisect2.py`, `_traj_unstripped.py`). Env: the standard redesign env, PAR_RAMPS=22.

## WHAT WAS MEASURED
For each player in cohorts **ND-with-pick, draft years 2014-2019 (n=437)**, the engine's value AS OF career-year t
(t=0=draft … t=5), survivorship-clean (every drafted player incl busts). Aggregate = MEAN SCAR per player by career-year.

## METHOD (point-in-time valuer) + the anti-circularity handling (load-bearing)
`value_asof(p,t)`: deepcopy, `scoring` truncated to seasons with year ≤ D+t, `BASE_REF=AGE_REF=D+t`. The engine's
`==2026` in-progress-season branches simply don't fire for historical years — correct: the D+t season is treated as a
complete past season, the most-recent for recency/level. Two corrections were essential and verified:

1. **LEAK-FREE (strip `_pos_now`/`_fut`; value on DRAFTED pos).** Diagnosis: McLarty (pk30, 0 career games) valued 17 at
   yr0 vs Ridley (pk22, also 0 games at yr0) 517 — a 30× gap between two observationally-identical fresh prospects.
   Bisected to `_pos_now`/`_fut`: McLarty (never played) carries neither → valued at his drafted KEY_DEF (low); Ridley
   *became* a GEN_DEF so carries `_pos_now=GDEF`/`_fut` → valued GEN_DEF (higher). Those fields encode the REALIZED role
   = a draft-day future-leak. Fix: strip them in the point-in-time copy → value on the drafted position (the info known
   at draft). NB this is the 22× KEY_DEF-vs-GEN_DEF pre-debut option gap surfacing — likely the known GEN_DEF/KEY_DEF
   young-end issue; surfaced, not a blocker. **Bound:** the un-stripped variant is essentially identical in aggregate
   (yr0 326 vs 325, ratio 0.37 both ways) → the strip does NOT manufacture the gap; un-stripped merely credits hindsight.

2. **Right-edge realized-bust floor.** Never-debuted (cumulative senior games through D+t == 0) at t≥3 → realized 0 (a
   3+yr non-debutant is a revealed bust; do NOT let the pre-debut path keep assigning it option value, which would
   inflate the anchor and flatten the V). Left edge (t≤2) keeps the engine option — the contested half being tested.
   Players who debuted then washed out are NOT floored; the engine reads their (recency-decayed, low) realized
   production via the established path. So the right edge is realized, not engine-projection.

Sanity (survivors behave): Bontempelli 1608→4236→6212→7236(peak yr3)→decline; Ridley holds yr1, dips yr2-3 on few
games, breaks out yr4 — per-individual, information-resolving.

## RESULT
POOLED mean SCAR/player by career-year (n=437):

| yr0 (draft) | yr1 | yr2 | yr3 | yr4 | yr5 |
|---|---|---|---|---|---|
| **326** | 594 | 745 | 797 | 875 | **876** |

- **Draft-day option = 326 = 0.37× the realized yr5 anchor (876).**
- Monotone RAMP, **no V** in the aggregate (no yr1 crash, no dip-then-recover).
- Per-cohort yr0→yr5: 2014 294→817, 2015 345→922, 2016 318→1096, 2017 291→709, 2018 336→701, 2019 378→1046. All rise.

YEAR-1 INTERCEPT TEST (no-predictable-round-trip): per-player dV1 = v(yr1)−v(yr0) regressed on realized yr5 quality
(external control): **slope +0.2001, INTERCEPT +92.7 SCAR (positive), n=437.** mean dV1 +268 (+82% of v0). Variant
(dV1 ~ draft-day v0): slope +0.218, intercept +197. Per-cohort mean dV1 all positive (190/383/254/297/225/275).

## INTERPRETATION vs THE FRAME (honest, with the nuance)
The engine's failure mode is NOT the doc's classic **V** (crash in yr1, recover by yr3-4). There is no yr1 crash — the
year-1 intercept is **positive**, so the no-predictable-round-trip test *as literally specified* (looking for a negative
crash) gives a **FALSE PASS**. The violation is the SAME underlying error in its OTHER face, exactly as the doc's prose
names it: the engine **anchors a no-games player near zero** (yr0 = 0.37× realized) and treats production as **ADDITIVE**
(the steep ramp, +82% in yr1 alone) rather than carrying the option from day one and having production REPLACE it. Under
the option frame the draft-day value should ≈ E[realized outcome] = the survivorship-clean realized mean (≈876), because
the per-player realized values already embed the convex payoff; the engine prices it at 326 and ramps up to where it
should have started.

⇒ **The right diagnostic for THIS engine is the draft-day/realized ratio (0.37) and the ramp — NOT the year-1 intercept**
(which was designed for a crash signature this engine doesn't have). Invariants in this language: #4 no-V — PASSES
literally (no crash) but for the wrong reason; #1 trajectory-match — VIOLATED at the draft-day anchor (curve ramps from a
low base, not flat-from-a-correctly-priced-option); #5 survivorship-up — holds trivially (the ramp). #2 elite reachability
and #3 prospect convexity were not separately probed this pass (next, if Luke wants, before/at U28-D).

## WHAT IT MEANS FOR U28-D
- The dominant lever is **raising the draft-day OPTION (yr0)**, not only the yr3+ staleness onset. The 326→876 gap is at
  yr0, before any staleness bites. KAPPA≈0 in yrs1-2 is necessary but not sufficient.
- The **p97 tail-restore is where the draft-day lift comes from** (the doc's central value driver): lifting the truncated
  upper tail is what raises the option toward E[outcome]. The GEN_DEF/KEY_DEF young-end gap (McLarty's KEY_DEF 17) is a
  concrete instance of the amputated tail.
- **RE-RUN this exact harness after U28-D** as the "after": target is yr0 lifting toward ~the realized anchor and the
  ramp flattening, WITHOUT introducing a young-player boost (per-individual pricing only; the curve is the diagnostic,
  never the control surface).

STOP point. Reported to Luke. Nothing builds past this without his word.

## DECOMPOSITION OF THE GAP (2026-06-28, requested before choosing any U28-D lever)
Scripts: `rl_after/_traj_decompose.py` (band-space body/tail), `_traj_reconcile.py` (state/pricer + right-edge). All
priced in the same v_at_peak space (SCALE_DIST=1.0, uniform REPL −3, 'bal') so terms are commensurable. n=437.

THE LADDER 330 → 876 (mean SCAR/player), four named increments:

| from | increment | to | what it is |
|---|---|---|---|
| 330 (engine yr0) | **+252 BAND BODY** | 582 | engine's projected band quantiles q10-q90 sit ~5-10 avg-pts below realized (p50 56.4 vs 61.0; p90 81.4 vs 91.6) |
| 582 | **+101 BAND TAIL** | 682 | realized mass ABOVE p90 (p95 99 / p97 104 / p99 109) that the 5-quantile band truncates; 682 = option value of the realized distribution priced via v_at_peak @yr0 |
| 682 | **+194 STATE+PRICER** | 876 | reconcile run: v_at_peak prices the SAME realized outcome **+269 lower at the yr0 0-games/age-18 state than at maturity** (the production-state discount — the purest frame violation), and the prospect pricer (v_at_peak) sits **+101 below** the established par-path (redesign_value) on the same outcomes at maturity. (The two realized-option estimates, 682 pool vs 506 own-outcome, differ by the comparable-pool convexity; the qualitative split is robust.) |

**HEADLINE: the tail is NOT the dominant lever.** BAND TAIL = +101; the banked p97 tail-restore (+8-11/position)
addresses only a slice of that +101. The dominant terms are the BAND BODY (+252 — re-centre the conditional-prior
median) and the PRODUCTION-STATE DISCOUNT (the bulk of +194 — the engine knocks ~269 off the option for being a
0-games prospect; this is U28-D's elapsed-opportunity / level=0-pole / par_centred NONPLAY territory). Tail ≈ 18% of
the 546 total (29% of the band-space gap).

PER POSITION (drafted group) — yr0/realized-opt ratio, then BODY/TAIL of the band gap:
| pos | n | v_eng | v_opt | ratio | BODY | TAIL | note |
|---|---|---|---|---|---|---|---|
| MID | 141 | 712 | 1027 | 0.69 | +190 | +126 | body-led, tail real |
| GEN_FWD | 99 | 36 | 569 | **0.06** | +444 | +89 | near-total crash; v_at_peak threshold knife-edge (band p50 54.6 just below the value floor → 36; realized 59.7 → 480) |
| KEY_FWD | 51 | 305 | 523 | 0.58 | +130 | +88 | |
| GEN_DEF | 83 | 238 | 377 | 0.63 | +61 | **+79** | the ONE position where TAIL ≥ BODY → tail-restore genuinely relevant here (GEN_DEF is in HIGH_TAIL) |
| KEY_DEF | 46 | 22 | 502 | **0.04** | +396 | +85 | near-total crash (McLarty-17 generalises); KEY_DEF NOT in HIGH_TAIL |
| RUC | 17 | 228 | 939 | 0.24 | +554 | +157 | thin n; borrow-pool |

⇒ The under-pricing is **massively position-uneven** (GEN_FWD 0.06 / KEY_DEF 0.04 crashed vs MID 0.69), so the lever is
position-specific (consistent with U28-D position-calibration). Tail-restore helps GEN_DEF/MID; the crashed forwards/key-
defs need BODY re-centring + the state-discount fix, not the tail.

RIGHT-EDGE CONFIRM (Task 2): curve plateaus yr4 875 ≈ yr5 876 (converged); cohort-halves both stable and the level
tracks realized cohort strength (2014-16 yr4 1008→yr5 946 ageing past peak; 2017-19 741→807 still maturing). The mature
end is priced consistently — the entire error is young-end. **No-re-prop constraint, now measured:** lift the YOUNG
distribution toward realized E[] without moving the already-correct mature end.

REVISED U28-D GUIDANCE: do NOT route this to the p97 tail-restore as the dominant lever. Target, in order of magnitude,
(1) the production-state discount on the 0-games option (elapsed-opportunity / live-pole), (2) the BAND BODY re-centring
(conditional-prior median, position-specific, biggest for GEN_FWD/KEY_DEF), (3) the band tail (p97) — smallest, and only
clearly load-bearing for GEN_DEF. Position-calibrate throughout. Re-run this harness + decomposition after U28-D.

## THREE REAL-PLAYER DIAGNOSTICS (2026-06-28, before 71/29 is final — analysis only)
Scripts: `rl_after/_traj_players.py`, `_traj_players2.py` (pick-kernel v_opt), `_traj_statecurve.py`. Board values pulled
from `rl_app_data.json` (UNTOUCHED) and reproduce Luke's reads (Patterson 837, Kyle 465, Sweid 366, Matthews 436,
Nairn 521, Dovaston 723). Board ≈ current engine (within ~10%) — the board is NOT stale.

### 1. GEN_DEF — the position mean WAS masking, but the crash is deep-pick, not the named top-picks
First pass used a coarse 3-pick-band v_opt that came out FLAT at 837 across picks 5/11/14/15 (the wide-bin artifact).
Re-priced v_opt with a Gaussian kernel over log-pick (H=0.40, per position). At that resolution the named young GEN_DEFs
are HEALTHY, not crashed: Patterson pk5 **1.25**, X.Taylor pk11 0.90, H.Kyle pk14 0.84, O.Taylor pk15 0.90, Carmichael
pk21 0.99. BUT the 2014-19 GEN_DEF cohort (n=83) is strongly BIMODAL: **mean 0.55, p10 0.01, p25 0.02, p50 0.75, p75
1.06, p90 1.23; 49% sit below 0.30.** Split by pick: pk≤10 mean 0.87 (healthy), **pk≥25 mean 0.44** (many near-zero).
⇒ The 0.63 position mean DID mask a crashed sub-cluster (Luke's instinct correct) — it's the DEEP-pick young GEN_DEFs
hitting the same v_at_peak value-floor knife-edge as GEN_FWD (band p50 below the value floor → near-0), NOT the named
top-pick players. The position-level "GEN_DEF tail-dominated, small BODY" read was a MEAN ARTIFACT; GEN_DEF's body
re-centre must be driven by the deep-pick young sub-population. (Realized GEN_DEF best-3 by pick: pk1-4 92, pk5-10 76,
pk11-18 80, pk19-30 62, pk31-60 47 — option does fall with pick but not the 2.3× the flat-band v_opt implied.)

### 2. STATE DISCOUNT IS A SMOOTH TAPER → no post-yr0 cliff (constraint on the live-pole)
v_at_peak of each player's OWN realized best-3, priced at the year-t state (mature t5 = 775):
| state | v_at_peak | discount from mature |
|---|---|---|
| yr0 | 506 | **269** |
| yr1 | 583 | 192 |
| yr2 | 644 | 131 |
| yr3 | 719 | 56 |
| yr4 | 763 | 12 |
| yr5 | 775 | 0 |
The discount decays ~70/yr, monotone — a smooth taper, NOT a step. Engine's own ramp today: yr0 326 → yr1 510 (**+57%**)
→ 697 → 797 → 875 → 876. Because the discount tapers, a live-pole that removes it state-by-state lifts yr0 most and yr1
less, COMPRESSING the +57% surge toward ~+18% (gentle positive) WITHOUT inverting (simulated lifted ramp 595→702→828→
853→887→876, monotone). **DESIGN CONSTRAINT: the live-pole's taper must MATCH this measured discount decay (≈ −77/−60/
−75/−44 per yr).** A steeper yr0-only lift (discount that stepped to ~0 by yr1) would convert +57% into a −14% cliff —
the measured smoothness is the safety property, and U28-D must reproduce it.

### 3. CLEAN pick-monotonicity breach in the conditional-prior band (held-equal guard is blind)
Sweid pk25 (GFWD, 0g, draft-age 18, yr0 294, board 366) vs Matthews pk30 (GFWD, 0g, draft-age 18, yr0 350, board 436):
EARLIER pick worth LESS. Equal on position/games/draft-age/tenure → not the maturation term; a CLEAN pick inversion.
Mechanism: the cond_prior_band itself inverts — Matthews [37.5, 53.9, 61.3, 69.3, 83.3] sits above Sweid [38.5, 52.0,
59.6, 65.6, 82.2] at q30/q50/q70/q90. The quantile-GBR is non-monotone in pick (tree artifact). The held-{games,tenure,
age,pos,pick} monotonicity guard cannot catch it because the two players DIFFER in the swept variable (pick). ⇒ The
cond_prior needs a pick-monotonicity guard (sort/isotonic over pick), independent of U28-D. Cross-position orderings Luke
flagged (Nairn 521 GFWD pk20 > Carmichael 455 GDEF pk21; Dovaston 723 GFWD pk16 > X.Taylor 609 / Kyle 465 GDEF) are
confounded by position-value scale + games (Dovaston 6g, Nairn 2g) — worth a separate GFWD-vs-GDEF efficiency look but not
clean monotonicity. The Sweid/Matthews within-position pair is the load-bearing breach.

### NET effect on 71/29
Rankings hold (tail smallest; body + state-discount dominant; position-uneven). The refinement: GEN_DEF is NOT cleanly
tail-dominated — at pick resolution it has a deep-pick BODY crash hidden by the mean, so the body-lever map is GEN_FWD +
KEY_DEF (all young) + GEN_DEF (deep-pick young); the state-discount live-pole applies across all and is taper-constrained;
tail-restore stays the smallest lever, load-bearing only for the healthy-tail top-pick positions. Pick-monotonicity guard
for the cond_prior is a separate banked fix. (Aggregate-sum-indexed bust-zeroing recut still pending; rankings robust to it.)

## FINAL PRE-SIZING CHECKS (2026-06-28) — gating year-1 move + taper robustness (script `rl_after/_traj_aggcut.py`)

### (1) THE GATING NUMBER — yr0→yr1 on the aggregate-sum-with-busts-as-zeros basis
Total cohort SCAR per state, non-debuted-by-year-t set to 0 (busts as zeros; yr0 = all at draft-day option), n=437:
| yr | TOTAL SCAR | mean/player | #non-debuted(=0) | move (ratio-of-sums) |
|---|---|---|---|---|
| yr0 | 142,267 | 326 | 0 | — |
| yr1 | 222,826 | 510 | 191 | **+57%** |
| yr2 | 304,389 | 697 | 101 | +37% |
| yr3 | 348,401 | 797 | 68 | +14% |
| yr4 | 382,339 | 875 | 61 | +10% |
| yr5 | 383,003 | 876 | 60 | +0% |

**GATING NUMBER: yr0→yr1 = +56.6%** (≈+57%, NOT the earlier +82%). Reconciliation: +82% = no yr1 bust-zeroing (yr1=594);
this aggregate-sum basis zeros the **191 of 437 (44%)** non-debuted at yr1, giving the honest +57%. This is the number that
gates the ≤5-10% tolerance, and it sits ~6-11× above it. SIZING IMPLICATION: to flatten +57% toward ~+5%, the aggregate
yr0 option must roughly DOUBLE (326 → ~600+) — i.e. close most of the body + state-discount gap at yr0. NOTE the composition
tension: 44% of yr0 option is carried by eventual non-debutants who drop to 0 at yr1, so the lift must be DISTRIBUTIONAL
(raise the option = E[outcome] incl bust-mass-at-0), not a flat per-player yr0 bonus, or the bust drop-off worsens.

### (2) TAPER ROBUSTNESS — the state discount split realizers / non-realizers / deep-pick
v_at_peak of own realized best-3 (busts R=0) at each state; discount from that group's mature:
| group | n | v_at_peak yr0..yr5 | discount yr0..yr5 |
|---|---|---|---|
| ALL | 437 | 506,583,644,719,763,775 | 269,192,131,56,12,0 |
| REALIZERS | 329 | 672,775,854,954,1014,1029 | 357,254,175,74,15,0 |
| **NON-REALIZERS** | 108 | **0,1,3,1,1,2** | **2,1,0,1,1,0** |
| DEEP pk≥25 | 293 | 278,322,353,392,418,430 | 151,108,76,38,12,0 |

**The taper is robust off-survivor.** Non-realizers price ~0 at EVERY state (their realized best-3 is 0 → v_at_peak(0)≈0)
and carry a state discount of ~2 — essentially none. So a pole calibrated to remove the v_at_peak state discount has NOTHING
to remove for the eventual busts → it CANNOT over-lift them, PROVIDED the lift acts on the OPTION (the bust-weighted
expectation), not as a flat per-player yr0 bonus on the band value (which the engine assigns before knowing the outcome).
Realizers carry the full smooth taper (357→0); deep-pick (the body-crash sub-pop) a smaller smooth taper (151→0). ⇒ The
live-pole must be PICK-SCALED (smaller lift for deep picks, matching their 151 vs the realizer 357) AND distributional. The
taper and the body-crash interact correctly ONLY under a distributional, pick-scaled lift — a uniform per-player pole would
over-lift the deep-pick eventual-busts and worsen their yr1 drop.

### LEVER MAP (stands, now sizing-ready)
(A) live-pole / state-discount FIRST — taper-constrained (match the measured ~70/yr decay) AND pick-scaled (151 deep vs 357
realizer) AND distributional (option, not flat bonus). (B) body re-centre SECOND — GEN_FWD + KEY_DEF (all young) + GEN_DEF
(deep-pick young), pick-resolved. (C) tail THIRD — top-pick healthy-tail positions only. Plus the standing pick-isotonic
cond_prior guard (separate from U28-D). Aggregate gating move to beat: **+57% → ≤5-10%**. Bust-zeroing recut now DONE (this
is it); rankings unchanged.

## PRE-SIZING RESOLUTIONS (2026-06-28) — GEN_DEF keying + REPL-hardness + the DISTRIBUTIONAL sizing lock
Script `rl_after/_traj_keying_repl.py`.

### (A) GEN_DEF anchor-keying (drafted vs current bucketing) — GEN_DEF STAYS in the body lever
GEN_DEF crash ratio (yr0/v_opt) re-keyed both ways: DRAFTED-keyed (p['pos'], the pedigree cohort — principled) mean 0.55,
p25 0.02, p50 0.75, 49%<0.30; CURRENT-keyed (gfut, realized role) mean 0.46, p25 0.02, **p50 0.30**, 49%<0.30. Only 6
drafted-GEN_DEFs have current≠GEN_DEF (movers), so the keying shifts MAGNITUDE not direction: the deep-pick crash is on the
principled drafted basis; the current basis makes the MEDIAN crash too (0.75→0.30). Either way GEN_DEF needs the body
re-centre — the keying choice does not flip it. The decomposition's drafted-keyed read is the one to build on (it's the
GEN_DEF draftee cohort); current-keying is the robustness bound (crash ≥ as bad). RESOLVED: GEN_DEF stays in the body lever,
deep-pick-focused, pick-resolved.

### (B) REPL-hardness scoping — the floor is a legitimate convexity; the crash is a BAND problem, keep REPL_DROP uniform −3
v_at_peak(L) swept near each position's replacement floor (REPL: MID 80.1, GEN_DEF 78.3, RUC 78.5, KEY_DEF 68.4, GEN_FWD
70.9, KEY_FWD 67.8):
| pos | v_at_peak @ repl−8 / repl / repl+8 | grad@floor (SCAR/avg-pt) |
|---|---|---|
| MID | 19 / 147 / 579 | 33 |
| GEN_FWD | 26 / 203 / 849 | **48** |
| KEY_FWD | 18 / 131 / 545 | 30 |
| GEN_DEF | 18 / 135 / 570 | 32 |
| KEY_DEF | 18 / 131 / 556 | 31 |
| RUC | 16 / 117 / 461 | 26 |
The floor is a STEEP CONVEXITY (≈near-0 at repl−8, ~30-48 SCAR/avg-pt ramp above) — legitimate, not a bug: a player peaking
8 below replacement IS marginal. KEY INSIGHT: for the crash positions (GEN_FWD, KEY_DEF, deep GEN_DEF) the realized
distribution straddles or sits BELOW a high replacement, so the lower band (p10-p50) is sub-replacement → contributes ~0,
and the position's value is concentrated in the UPPER quantiles (p70/p90, above repl). So the GEN_FWD "BODY +444" is NOT a
p50 move (p50 54.6 is sub-repl → 0 regardless) — it's the UPPER-band (p70/p90) sitting below realized, amplified by the
convex floor. ⇒ RESOLVED: keep REPL_DROP uniform −3 (no per-position REPL re-scope — the floor hardness is correct
v_at_peak convexity); the crash is a BAND problem, fixed by the (B) body lever, but the body re-centre for the crash
positions must target the UPPER-MIDDLE band (p70/p90), pick-resolved, and precisely (the convex floor turns small upper-band
errors into large value swings — GEN_FWD's 48 SCAR/avg-pt is the worst).

### THE U28-D SIZING SPEC — DISTRIBUTIONAL, not "double yr0"
"326 → ~600+ aggregate" is the OUTPUT, never the lever. 44% of the yr0 aggregate is carried by eventual non-debutants who
go to 0 at yr1, so a flat lift of the yr0 aggregate doubles the busts' option too — which WORSENS the bust drop-off and
does NOT flatten the move. The lever is stated distributionally:
  **lift the REALIZERS' option toward their realized E[outcome]; hold the bust mass weighted at ~0; let the aggregate move
  fall out.** This is smaller and differently shaped than doubling pooled yr0, and it must not be implementable as a flat
  per-player yr0 bonus. WHY it is safe (composition safety = taper safety, the same property): the pole acts on the
  bust-weighted expectation, and non-realizers price ~0 at every state (measured discount ~2), so the pole has nothing to
  over-lift for them.
LIVE-POLE (A) carries all three required properties: (i) **taper-matched** — lift follows the measured state-discount decay
(yr0 269 → yr1 192 → yr2 131 → yr3 56 → yr4 12, ~70/yr), so yr0→yr1 compresses gentle-positive with no cliff; (ii)
**pick-scaled** — 151 (deep pk≥25) vs 357 (realizer) discount, not a uniform pole; (iii) **distributional / bust-weighted**
— acts on the option (E over outcomes incl bust-mass-at-0), never a flat yr0 bonus.
LEVER MAP (locked): (A) live-pole / state-discount FIRST (taper-matched + pick-scaled + distributional); (B) **upper-band (p70-p90) re-centre**
SECOND (NOT a body/median move — median left at its correct sub-replacement level) — GEN_FWD + KEY_DEF + deep-pick GEN_DEF, pick-resolved, HIGH-PRECISION per position (convex floor: a 2-pt p90 miss = hundreds of SCAR, GEN_FWD 48 SCAR/avg-pt);
(C) tail THIRD — top-pick healthy-tail only. Standing: pick-isotonic cond_prior guard. GATING MOVE to beat: aggregate
yr0→yr1 **+57% → ≤5-10%**. With (A) and (B) resolved and keyed, **U28-D is sizing-ready** (still before Stage 2; nothing baked).

## LEVER (B) REDEFINED + 6-MOVERS CONFIRM + FIRST-ORDER SIZING (2026-06-28) — script `rl_after/_traj_movers.py`

### (B) is an UPPER-BAND move, not a body/median re-centre (corrected definition)
For the crash positions (GEN_FWD / KEY_DEF / deep-GEN_DEF) the p50 is CORRECTLY sub-replacement and prices to ~0 wherever
it sits (GEN_FWD p50 54.6 is sub-repl — no median move touches it). The gap is p70/p90 below realized, amplified by the
convex floor. So **(B) = lift the UPPER band (p70-p90) toward realized, pick-resolved, and LEAVE the median at its correct
sub-replacement level.** Built as a median re-centre it does NOTHING for GEN_FWD. And (B) is HIGH-PRECISION, not approximate:
the convex floor (GEN_FWD 48 SCAR/avg-pt at the floor) means a 2-pt p90 error is hundreds of SCAR — the p70/p90 targets must
be landed on realized precisely PER POSITION (measured-precise, pick-resolved).

### 6 GEN_DEF anchor-movers — healthy end undisturbed (keying choice is safe)
The 6 drafted-GEN_DEF whose current≠GEN_DEF: Caleb Windsor pk7→MID (48g, b3 57.8), **Hayden Young pk7→MID (95g, b3 96.5)**,
**Wanganeen-Milera pk11→MID (96g, b3 107.4)**, **Max Holmes pk21→MID (116g, b3 109.4)**, Ryan Lester pk36→KEY_DEF (243g,
b3 80.2), Conor McKenna →GEN_FWD (136g, b3 73.3). So the movers DO include top-pick producers (Young pk7, NWM pk11, Holmes
pk21 — GEN_DEF draftees who became elite mids). BUT: (i) the keying does NOT move THEIR values — they're priced on realized
production, pool-independent; (ii) the named top-pick GEN_DEF PROSPECTS are stable across keyings (Patterson Δ−0.05,
X.Taylor +0.01, Kyle −0.03, O.Taylor −0.05) — the healthy end is undisturbed, the keying shift is entirely at the crash end.
This REINFORCES drafted-keying: a GEN_DEF draftee CAN become an elite mid (NWM/Holmes/Young), and that positional-flexibility
upside IS part of the GEN_DEF draft option — drafted-keying retains it; current-keying would wrongly strip it. Build on
drafted-keyed; healthy end safe.

### FIRST-ORDER SIZING against +57% → ≤10% (the magnitude; precise per-position calibration is the build act)
Aggregate yr1 (busts=0) = 510 mean. For yr0→yr1 ≤ 10%: yr0 ≥ 510/1.10 = **464**. Current yr0 = 326 → required aggregate lift
= **+138 mean (+42%)**. This is NOT a flat +138 per player — it's allocated DISTRIBUTIONALLY by pick/pos toward each
prospect's E[outcome | pick, pos] (the v_opt target): top-picks lift most, deep-picks little (their bust-weighted option is
genuinely small), busts' contribution stays ~0. The +138 is delivered by (A) state-pole + (B) upper-band re-centre combined.
**DESIGN FORK to surface before the precise pass:** (1) the (A)/(B) split of the +138 — how much from the state-pole (lift the
realizers' option toward realized E[] at the yr0 state) vs the upper-band re-centre (p70/p90 to realized) — they overlap and
must be apportioned, not double-counted; (2) yr0-only flatten (raise yr0 to 464, leaves yr1→yr2 +37%) vs whole-ramp flatten
(taper-matched pole lifts every state, flattening yr0→yr1→yr2 together — the frame's intent). The gating number Luke set is
yr0→yr1 ≤ 10%; the whole-ramp question is the broader frame target. ⇒ Sizing magnitude established (+42% aggregate yr0,
distributional); the (A)/(B) apportionment and yr0-only-vs-whole-ramp are the two forks for the sizing pass.

## VALIDITY CHECKS before sizing (2026-06-28) — A/B/C/D + Fork 1 (scripts `_traj_validity_CD.py`, `_traj_walkforward.py`)
Several of these MOVE the +57%, so it is NOT sized to directly.

### A. IN-SAMPLE vs WALK-FORWARD — the option is MORE under-priced out-of-sample (lever sizes up)
cm_400 trains cond_prior on resolved careers debut≤2021 (`build_cond_prior(resolved_cut=2021)`), so the 2014-19 cohorts ARE
in-sample (retrodiction). Walk-forward: per cohort D, retrain cond_prior cap=D+1 / resolved_cut=D (ND debut at D+1 → cohort
auto-held-out), reprice its yr0 option; matched tree count both sides. Leakage = **−14%** on the yr0 option, consistent
across cohorts (2014 −17%, 2015 −12%, 2016 −16%, 2017 −15%, 2018 −11%, 2019 −13%). Applied to the shipped yr0=330 →
walk-forward yr0 ≈ **284** (ratio vs realized anchor 876 drops 0.37 → ~0.32). yr0→yr1: in-sample +55%; walk-forward
**+61% to +79%** (yr1 in-sample 510 → +79%; yr1 with the U21 ~10% production-leakage haircut ~459 → +61%). The robust number
is the −14% option leakage; the absolute 284 transfers that % onto the 400-tree basis. ⇒ the honest option gap is BIGGER
out-of-sample; sizing must use WALK-FORWARD realized targets, not in-sample.

### B. CONFIRMED: year 0 = DRAFT (option, 0 games); clock = YEARS-SINCE-DRAFT
Code: `debutyr = year+1` (ND), `d0 = draft year (0 games)` = year 0; states are D+t. yr0 is the pre-debut option, yr1 = end
of first season. 44% (191/437) non-debuted by yr1 — consistent with draft-day/years-since-draft.

### C. THE +57% IS 78% DEBUT-TIMING, only 22% genuine pricing drift (THE big mover)
Split the yr0→yr1 move (mean SCAR): v0_option 330 → v1_option (yr1, still pre-debut basis) 370 → v1_actual (yr1, prod or 0)
510. **PRICING (option drift, same basis) = +40 (22%); DEBUT-TIMING (cross to production/zero) = +140 (78%).** Debutants
(246/437, 56%) move option→production +459; non-debutants (191) hold option 201 but are zeroed (→ −179). ⇒ The +57% step is
mostly mechanical debut-revelation, NOT the engine re-pricing the option up. The genuine option-mispricing signal is the
yr0-option-vs-realized-anchor gap (the 0.37 ratio), not the year-1 step. Sizing implication (as Luke anticipated): the
year-1-STEP target is far below +57%, AND the lift MUST be debut-timing-weighted — lifting the yr0 option of a player who
won't debut for two more years over-prices him; non-debutants' options should stay low (they're heading to bust). The gate
belongs on the EXPECTED year-1 change (intercept), not the raw +57% mean.

### D. SAMPLE BASIS + WINDOW
(i) n=437, same 2014-2019 ND-with-pick as the trajectory. ✓
(ii) Window is widenable: cohorts 2008-2021 ALL resolve through yr5≤2026 (14 cohorts, n~60-80 each); 2022-2023 incomplete.
The 2014-2019 choice was conservative/somewhat arbitrary, not data-forced — widen (e.g. 2010-2021) to thicken slices.
(iii) Per-slice n (body lever): the **deep-pick GEN_DEF crash (pk≥25) = n=62** — ROBUST, not thin. Thin slices are the
TOP-pick GEN_DEF/KEY_DEF (n=5-6, but those are the healthy end, not the crash) and **RUC (n=1/1/15 across bands — thin
everywhere → pool/widen**, per the standing RUC-reliability item). So the GEN_DEF body lever is well-sampled; RUC is not.
(iv) Era drift ~5-6%: mean SC season-avg rose to 72-74 by 2019-2020 then DROPPED to ~69 in 2021+ (rule change). The yr5
anchor (2019-2024) straddles the 2020→2021 step, so the per-cohort split (2014-16 vs 2017-19) is ~5% era-confounded and the
precise pass should era-normalize the anchor; the pooled number is only mildly affected.

### Fork 1 — (A)/(B) apportionment: MEASURED directionally, but genuinely ENTANGLED (surfaced, not a choice)
From the existing decomposition (330 +252 BAND-BODY +101 BAND-TAIL → 682 +STATE/PRICER → 876; reconcile STATE +269, PRICER
+101): **(A) state-pole targets the STATE discount ≈ +269** (the production-state pricing of a given outcome at yr0 vs
mature); **(B) upper-band targets the BAND-TAIL +101 plus the upper-band share of the +252 body** (for the crash positions
the body IS upper-band; MID's body is median, a different/smaller lever); the **PRICER +101** (prospect-vs-established basis)
is neither — it's a Stage-4/bake calibration. CRUCIAL: (A) and (B) act on DIFFERENT axes — (A) on the state-pricing of a
level, (B) on the band level itself — so they COMPOUND, they do not double-count the same quantiles. BUT the SCAR each
delivers is ORDER-DEPENDENT because v_at_peak is convex and state-dependent: lifting the band level (B) first vs removing the
state discount (A) first changes the absolute SCAR of the other. The pool-vs-own-outcome gap (682 vs 506 = 176) is the
measure of that entanglement (~30%). ⇒ the split is clean in DIRECTION (A≈state +269, B≈tail+upper-body) but NOT cleanly
additive in SCAR — they must be sized JOINTLY (apply the taper-matched state-pole and the upper-band level-lift together and
read the combined per-step move), not apportioned to fixed independent SCAR budgets.

### Fork 2 — WHOLE-RAMP taper flatten (Luke's call, acknowledged)
The yr0→yr1≤10% gate is a proxy for "no predictable surge anywhere"; yr0-only relocates the cliff. The measured taper
(269→192→131→56→12, ~70/yr) IS the whole-ramp answer — a taper-matched pole on all states flattens the whole ramp by
construction. Target ≤5-10%/yr across the ramp. The "+42%/yr0→464" aggregate is the OUTPUT consistency-check, never the
lever: size by lifting realizers' options toward E[outcome | pick, pos] state-by-state (now: WALK-FORWARD targets,
debut-timing-weighted); the aggregate landing with per-step ≤10% is the verification.

### NET — the +57% is not the honest gap; the precise sizing pass must
use WALK-FORWARD realized targets (A: option −14% more under-priced OOS), gate on the EXPECTED year-1 change not the raw
step (C: 78% of +57% is debut-timing), weight the lift by debut-timing (C), pull targets at the finest pick-resolution with
the window optionally widened to 2008-2021 to thicken slices (D-ii) and RUC pooled (D-iii), era-normalize the anchor ~5%
[DELETED 2026-06-29: superseded — sizing pass produced -16,529 (dropped up-leg); up-leg built; merged engine done. See START_HERE.]

## PART 1 — CORRECTED SIZING TARGET (2026-06-28) — script `_traj_target_curve.py`
The single corrected target the draft-day option should equal: era-normalized (REF era-avg 70.8), bust-weighted realized
E[outcome | pick, pos], window WIDENED to 2008-2021 (14 cohorts), kernel over log-pick (H=0.40). This curve is what (A)+(B)
size to; the gate is option/this-curve → 1.0 (debut-timing-weighted), NOT the year-1 step.

E[best-3 LEVEL, era-norm] / E[priced SCAR] / bust% / effN:
| pos | pk3 | pk8 | pk15 | pk30 | pk50 |
|---|---|---|---|---|---|
| MID (n=302) | 96.8 / 1519 / 0% | 83.9 / 862 | 72.4 / 420 | 59.1 / 264 / 22% | 46.6 / 184 / 35% |
| GEN_FWD (n=220) | 84.5 / 817 (effN6) | 71.5 / 426 | 63.0 / 325 | 50.9 / 153 | 43.2 / 92 |
| KEY_FWD (n=119) | 71.0 / 866 (effN7) | 67.0 / 668 | 59.6 / 468 | 45.9 / 256 | 36.2 / 196 |
| GEN_DEF (n=208) | 78.6 / 850 (effN4) | 79.0 / 660 | 70.8 / 607 | 50.5 / 217 / 27% | 42.2 / 132 |
| KEY_DEF (n=98) | 68.0 / 766 (effN2) | 63.3 / 333 | 63.1 / 417 | 50.1 / 354 | 45.4 / 256 |
| RUC (n=46) | 112/3897 (effN2 NOISE) | 61/434 | 73/1348 | 71/988 | 60/638 |
Well-sampled and monotone for picks ≥8 across the five field positions; pk3 is thin for GEN_DEF/KEY_DEF/GEN_FWD (effN 2-6 →
kernel/pool caveat); **RUC is thin (effN 2-6 at top) and NON-MONOTONE → must be pooled/widened** (confirms the standing RUC
item). Current walk-forward option ≈ 0.32× the realized anchor, so the lift = (this target) − (wf option), debut-timing-
weighted, sized JOINTLY by (A)+(B) on the whole ramp. Confirmations locked: B settled; D window 2008-2021; deep-pick GEN_DEF
n=62 robust; RUC pooled; era-norm ~5% applied (REF 70.8); Fork 1 joint; Fork 2 whole-ramp.

## PART 2 — KYLE / EARLY-CAREER THIN-SAMPLE (2026-06-28) — scripts `_traj_kyle.py`, `_traj_thinsample.py`
(A) has a SECOND job: grade games→production by sample reliability so thin-sample early-career players stay mostly on option.

### 2.1 The thin-sample crash IS there — masked by the +132 aggregate (Kyle pattern confirmed)
The ≤15g-debutant bucket means (1-5g +132, 6-15g +477, 16+g +1103) all look positive — but they MASK a below-par sub-cluster.
Within ≤15g debutants (n=197), **22% (44) are below-par thin-sample** (yr1 prod-read < yr0 option): mean option 686 →
yr1 **471 (−216 crash)** → realized yr5 **803**. The crash is PREMATURE on average (realized 803 > option 686 ≫ yr1 471 —
3-game noise wrongly priced in). Individual cases are honestly mixed (Sam Flanders 5g: opt 1204→yr1 690→realized **4765**;
Florent 9g: 1200→736→1198 [premature]; vs McCartin 6g: 997→454→57, Boekhorst 11g: 1203→711→81 [justified busts]) — but the
44-player mean vindicates the option, not the yr1 crash. Same pooled-masking as the GEN_DEF deep-pick crash.

### 2.2 Mechanism = the DEAD POLE (a live pole fixes it)
`redesign_value = prod + w·max(0, pole − prod)`, `w = 1 − min(games,30)/30` (0.90 at 3g). Kyle (3g GEN_DEF): option 572,
prod-read 510, **pole `_adraft_band` = 119 (DEAD)**. Because the floor is LIFT-ONLY and pole(119) < prod(510), the pole does
NOTHING → ev = prod = 510 (−62 below option; higher-pedigree cases crash to −216). So it is NOT the transition being too fast
(w=0.90 holds 90% on pole) — it is the DEAD pole having nothing to hold them to. **LIVE-pole test:** ev = prod + 0.90·max(0,
572−510) = **566 ≈ option** — the live pole holds Kyle. ⇒ (A)'s live pole fixes the thin-sample crash automatically (same
pole that lifts the draft-day option). Dead pole broke BOTH jobs.

### 2.3 Linear vs reliability grading — a 15-30g refinement, not the 3-game fix
Sweeping w across games (Kyle's live pole 572 / prod 510): linear `1−g/30` and reliability `K/(g+K)` AGREE at 3-6g (both
~0.90 pole → both fix the crash with a live pole); they DIVERGE at 15-30g (linear → 0 pole by 30g; reliability K=30 → 0.50
pole at 30g; K=15 → 0.33). So the live pole is the load-bearing fix for the 3-6g crashers; the linear-vs-reliability choice
governs the 15-30g transition — whether 30 games fully resolves the option (linear) or below-par-pedigree players hold pedigree
longer (reliability, statistically principled: production weight ~ games/(games+K) ≈ 1/variance). RECOMMENDATION: adopt the
live pole (fixes Kyle + the 44 crashers regardless of shape); switch `_floor_w` to reliability/shrinkage weighting as the
principled 15-30g refinement, K calibrated against realized 15-30g outcomes of below-par-pedigree players (a follow-up
measurement, secondary to the live pole).

### (A)'s TWO JOBS — both fixed by the same live pole
(i) lift the draft-day option to the Part-1 target curve (the ratio gate); (ii) the `_floor_w` blend onto a LIVE pole holds
thin-sample early-career players at ~option until production accumulates (the Kyle gate). The dead pole broke both; the live
pole is the single fix. `_floor_w` shape (linear→reliability) is the 15-30g refinement on top. Both sized before the precise pass.

## THREE LOCKS BEFORE SIZING (2026-06-28) — script `_traj_locks.py`

### LOCK 1 — ONE BASELINE; 876 RETIRED
The sizing target is the per-cell era-normalized realized E[outcome | pick, pos] curve (Part 1), priced via v_at_peak (the
SAME prospect pricer the option uses). 876 was the IN-SAMPLE pooled engine yr5 mean and a diagnostic ratio reference — it is
RETIRED: not a normalizer, not a target, absent from the sizing math. The gate is simply **option(cell) → curve(cell)**, lift
= **curve(cell) − walk-forward-option(cell)** per cell, no separate anchor. The prospect-vs-established PRICER basis (+101 /
~13%, v_at_peak vs redesign_value at maturity) is a SEPARATE Stage-4/bake calibration, NOT folded into this lift [**SUPERSEDED 2026-06-28 — see PRICER-SEQUENCING LOCK below: the per-cell pricer is folded into the TARGET first (v_at_peak→established), then (A)+(B) size to the established curve; it is NOT deferred to Stage-4**] — keeping ONE
baseline (the v_at_peak curve) for the option sizing. The old pooled "0.32× / 876" framing is superseded by the per-cell ratio.

### LOCK 2 — DEBUT-TIMING is NOT in the curve; it is applied ALONG THE RAMP (composition trap's last hiding place, closed)
The curve bakes in SURVIVAL (bust-weighted at 0) but is POOLED over debut-timing. Measured timing-decay weight =
E[realized outcome | NOT debuted by yr t] / draft-day E[]:
| scope | draft-day E[] | not-deb-by-yr1 | not-deb-by-yr2 | not-deb-by-yr3 |
|---|---|---|---|---|
| ALL picks | 361 | 167 (**0.46×**) | 92 (**0.26×**) | 31 (**0.09×**) |
| pk≤18 | 779 | 348 (0.45×) | 214 (0.27×) | 0 (0.00×, n=3) |
| pk≥25 | 200 | 140 (0.70×) | 87 (0.43×) | 33 (0.16×) |
So a player who hasn't debuted by yr t realizes only 0.46× / 0.26× / 0.09× the draft-day E[] (steeper decay for TOP picks — a
top pick not debuting is a worse sign relative to expectation; gentler for deep picks). ⇒ The draft-day (yr0) option target =
the full curve (timing unknown). For yr1+, the option target = curve × the timing-decay weight, applied ALONG THE RAMP. This
does TWO things: (i) prevents OVER-LIFTING future-busts — a yr2-non-debutant is targeted at 0.26×curve, not full curve (the
trap's last hiding place — a raw "curve − wf option" lift would over-price him); (ii) shows the gating bust-zeroing (non-deb →
0 at yr1) was too harsh — the residual-option value is 0.46×curve, not 0. The state-discount taper (debutant side, 269→…→0)
and this timing decay (non-debutant side, 1.0→0.46→0.26→0.09) together define the whole-ramp option evolution.

### LOCK 3 — thin pk3 cells HANDLED (not caveated)
Raw pk3 (kernel H=0.40, effN 2-6) is retired for the thin positions. pk3 via raw / wide-kernel (H=0.70, borrows pk5-12) /
monotone log-pick fit (anchored on well-sampled pk8-50):
| pos | raw pk3 (effN) | wide pk3 | fit pk3 |
|---|---|---|---|
| MID | 1519 (25, OK) | 1338 | 989 |
| GEN_FWD | 817 (6) | 580 | 614 |
| KEY_FWD | 866 (7) | 791 | 880 |
| GEN_DEF | 850 (4) | 696 | 1070 |
| KEY_DEF | 766 (2) | 572 | 529 |
MID pk3 is well-sampled (effN 25) — keep the raw 1519 (the top-pick premium is CONVEX, steeper than log-linear, so the fit
UNDER-shoots it). For the thin positions (GEN_FWD/KEY_FWD/GEN_DEF/KEY_DEF, effN 2-7) retire the raw and use the wide-kernel
as primary, cross-checked against the fit (KEY_DEF ~530-570, GEN_FWD ~580-610, KEY_FWD ~790-880); where wide and fit diverge
(GEN_DEF 696 vs 1070, the log-fit over-extrapolates the steep slope) the precise pass should POOL the convex top-pick SHAPE
from well-sampled MID (pk3/pk8 ≈ 1.76) and apply per position, then validate. RUC stays FULLY POOLED (no pick resolution).
⇒ no pk3 prospect's lift is driven by a 2-6 player raw cell.

### NET — the curve is the sizing target, fully specified
ONE baseline (the per-cell era-norm realized curve, 876 retired); gate option→curve per cell, lift = curve − wf-option;
SURVIVAL in the curve, TIMING applied along the ramp (decay 0.46/0.26/0.09, pick-dependent); thin pk3 handled by wide-kernel/
fit/cross-position pooling; RUC pooled. (A)+(B) size JOINTLY against it, whole-ramp, with (A)'s two jobs (option-lift +
live-pole thin-sample hold). Composition trap fully closed: busts weighted at 0 in the curve AND not over-lifted via the
ramp timing decay.

## PER-CELL DAMAGE + CORRECTED HEADLINE + DEBUT CONTINUITY (2026-06-28) — scripts `_traj_damage.py`, `_traj_continuity.py`

### TASK 1 — the per-cell damage (the real "how much"; SIGNED, not a uniform 0.32×)
Walk-forward option (engine yr0 option ×0.86) / curve target, per cell (2008-2021), v_at_peak basis (Lock-1 baseline):
| pos | pk1-10 | pk11-24 | pk25+ |
|---|---|---|---|
| MID | 1.13 | **2.14** | 1.28 | ← OVER-priced (restore inflates / under-bust-weights the band) |
| GEN_FWD | **0.14** | **0.15** | 0.20 | ← catastrophic under (value-floor knife-edge) |
| KEY_FWD | 1.03 | 1.04 | 0.47 | ← fine at top, under deep |
| GEN_DEF | 0.82 | 0.81 | 0.72 | ← mild under |
| KEY_DEF | **0.10** | **0.04** | 0.06 | ← WORST (catastrophic under) |
The damage is SIGNED and hugely dispersed (0.04 → 2.14), NOT a uniform 0.32×. Worst cells = KEY_DEF (0.04-0.10) and
GEN_FWD (0.14-0.20) — the crash positions whose realized mass straddles a high REPL so v_at_peak prices it near 0. MID is
OVER-priced (1.1-2.1×) — the restore over-lifts / under-bust-weights mid-pick MIDs. ⇒ the lift LOWERS MID and RAISES
GEN_FWD/KEY_DEF/KEY_FWD-deep. **The old pooled "0.32×" is superseded** (it was a cohort-mean conflating these signed cells).
TOTAL: over n=211 rostered prospects (active, ≤15g, age≤23): Σ curve = 98,214, Σ wf-option = 72,693, **NET gap = +25,521
SCAR, aggregate ratio 0.74** — the net masks large GROSS signed moves (MID down, GEN_FWD/KEY_DEF up). NOTE: this is on the
v_at_peak curve basis; the prospect-vs-established PRICER basis (+101 / ~13%, Stage-4/bake) would lift the whole curve and
partly close the MID over-pricing — kept separate per Lock 1.

### TASK 2 — corrected year-1 headline (Lock 2 carried through; +57% RETIRED) — with an honest direction correction
yr0 option 330. RAW +57%-style (non-deb zeroed): yr1 510 = **+55%**. Lock-2 corrected (non-deb = 0.46×option, NOT 0):
yr1 546 = **+66%**. CONSISTENT-OPTION basis (both years priced as option, debut-revelation removed): 330→370 = **+12%**.
DIRECTION CORRECTION (honest): un-zeroing the non-debutants RAISES the raw step (+55%→+66%) — the zeroing UNDERSTATED, not
overstated, the raw number. But the raw step is a debut-revelation artifact either way (+55% / +66% both meaningless). The
genuine SYSTEMATIC year-1 change is **+12%** (= C's +40 option-aging drift, the 22% pricing component). **+57% is RETIRED**
as a live number, carried forward nowhere; the gate is the per-cell option→curve ratio (Lock 1), not any year-1 step.

### TASK 3 — the two ramp tracks are CONTINUOUS at debut (martingale holds exactly)
Non-debutant track = E[outcome | not-deb-by-yr t]; debutant track = E[outcome | debut AT yr t]. Law of total expectation at
each boundary:
| boundary | residual entering | DEBUT track (Pr) | STAY track (Pr) | Pr·deb+Pr·stay vs residual |
|---|---|---|---|---|
| yr1 | 361 | 507 (0.57) | 167 (0.43) | 361 = 361 ✓ |
| yr2 | 167 | 249 (0.48) | 92 (0.52) | 167 = 167 ✓ |
| yr3 | 92 | 223 (0.32) | 31 (0.68) | 92 = 92 ✓ |
CONTINUOUS at all three (|Δ|<2%). At debut value steps UP (361→507, 167→249, 92→223 — debut is good news), EXACTLY balanced
by the non-debutant decay (361→167, 167→92, 92→31) → no predictable round-trip arbitrage. Continuity is guaranteed BY
CONSTRUCTION because both tracks are anchored on the SAME realized E[outcome|debut-state] data. U28-D must anchor the debutant
production-state value on E[outcome|debut t] (the live pole holds it there) and the non-deb option on curve×decay — same
boundary-continuity principle as the level=0 pole and the 3-game line.

### NET — sizing-ready
Per-cell damage quantified (signed, KEY_DEF/GEN_FWD worst, MID over-priced, net +25,521 SCAR over 211 rostered prospects);
+57% retired (systematic year-1 = +12%); both ramp tracks continuous at debut. The per-cell curve is the sizing target;
(A)+(B) size JOINTLY against it, whole-ramp, with (A)'s two jobs (option-lift + live-pole thin-sample hold). Nothing baked.

## MID-OVERPRICING VERIFICATION + DESIGN AUDIT (2026-06-28) — scripts `_traj_mid_verify.py`, `_traj_mid_basis.py`, `_traj_audit.py`

### PART 1 — the MID over-pricing is NARROW (pk11-24 only), not a blanket "lower MID"
**1.1 conversion-keying — REFUTED.** Drafted-MID vs current-MID realized are essentially identical (pk1-10 0.99×, pk11-24
0.99×, pk25+ current LOWER 0.73×). The top-8 realized mids are ALL drafted MID (Bontempelli pk4, Oliver pk4, Macrae pk8,
Neale pk73, Butters pk12, Mitchell pk14, Daicos pk4, Fyfe pk20) — NONE converted in. Unlike GEN_DEF, MID's elite are native;
the conversion asymmetry washes out. The MID curve denominator is NOT understated by conversion.
**1.2 pricer basis — closes the top and deep, residual only at mid-picks.** MID over-pricing per band, bust-weighted,
wf-option vs curve on each basis:
| band | wf-option | v_at_peak curve (ratio) | ESTABLISHED curve (ratio) | n |
|---|---|---|---|---|
| pk1-10 | 1280 | 1305 (0.98) | 1256 (**1.02 FAIR**) | 63 |
| pk11-24 | 825 | 355 (2.33) | 408 (**2.02 over**) | 75 |
| pk25+ | 259 | 215 (1.20) | 289 (**0.90 UNDER**) | 164 |
VERDICT: top-pick MIDs (the best-realizing, the forensic concern) are FAIR (1.02×); deep MIDs are UNDER-priced (0.90×, the
pricer basis flips them); the over-pricing survives ONLY at pk11-24 (2.02× established). Mechanism: the pk11-24 MID pool is
~4% elite (Butters/Mitchell/Fyfe) + ~96% modest/bust (mean 408), and the restore over-weights that thin upper tail (option
825). ⇒ the MID correction is a NARROW, pick-restricted (B) upper-band DOWN-correction at pk11-24 ONLY — do NOT lower top-pick
MIDs (fair) or deep MIDs (under-priced). Most of the "2.14× lower MID hard" dissolved; a pk11-24 residual survives.

### PART 2 — which original U28-D layers the curve subsumes
**1. (A) option-lift vs (C) tail-restore — (C) ABSORBED (everywhere, not just-but-GEN_DEF).** Per-position realized priced
distribution is upper-band concentrated for ALL positions (median≈0: MID p50=3, GEN_FWD=3, GEN_DEF=1; top-10% hold 57-79% of
all value: MID 71%, GEN_FWD 79%, GEN_DEF 79%, KEY_DEF 67%, KEY_FWD 57%, RUC 58%). The bust-weighted curve MEAN integrates the
p97 by construction, so moving the option to the curve DELIVERS the tail. GEN_DEF is NOT a special exception — it is tail-
concentrated like the rest, carried by (B). ⇒ (C) DROPS as a separate layer; its job folds into (A)+(B) targeting the curve's
realized p70-p97.
**2. STALENESS DECAY — RETIRE the old KAPPA (subsumed by Lock-2 timing decay).** The Lock-2 timing decay (0.46/0.26/0.09×,
re-derived on realized data) IS the principled staleness (a stale prospect = an old non-debutant → low realized E[outcome|not-
deb]). The old in-sample KAPPA would STACK with it → overshoot below target. Drop the KAPPA; use the timing decay. No stack
with the (B) MID-pk11-24 down-correction (different axis: non-debutant timing vs producing-mid upper-band).
**3. MATURATION AGE-GATE (#5) vs LIVE POLE — INDEPENDENT, keep both.** Different surfaces and populations: the age credit
lives in v_at_peak (producing young players; Tai Hayes +293) and the live pole lives in `_adraft_band` (0-game/thin-sample
holders, age fixed 18.5). The live pole doesn't touch the age credit for producers. Not redundant.
**4. p97 SIZING — RE-READ off the curve (retire +11/+8/+5).** Realized p97 (priced) per position: MID 3889, GEN_FWD 1601,
KEY_FWD 2202, GEN_DEF 2425, KEY_DEF 2361, RUC 5208 — pick-resolved, folded into (B), not carried as a fixed add.
**5. +101 PRICER BASIS — sequencing (no double-count).** The MID verdict is on the ESTABLISHED basis (pricer folded in), and
the pricer CHANGES THE SIGN per cell (pk25+ flips over→under), so it cannot be deferred. SEQUENCE: (i) fold the per-cell pricer
basis into the target (v_at_peak curve → established target); (ii) (A)+(B) size to the ESTABLISHED curve, signed per cell.
Do NOT correct MID via the v_at_peak curve AND the pricer separately. Refines Lock 1: pricer is folded into the TARGET, not a
separate post-hoc step, so the signed corrections hit the right level.

### NET — reduced lever set (audited)
DROP (subsumed): (C) tail-restore (in the curve); staleness KAPPA (→ Lock-2 timing decay); old +11/+8/+5 p97 (re-read off
curve). KEEP (separate axes): (A) level-lift to the established curve; (B) upper-band re-centre to the realized p70-p97
(LOAD-BEARING — value is 57-79% upper-band — and SIGNED: lift crash positions, LOWER MID pk11-24); (A)'s 2nd job live-pole
thin-sample hold; Lock-2 timing decay (principled staleness); maturation age-gate #5 (independent v_at_peak surface); pricer
basis folded into the target before (B). Standing: pick-isotonic cond_prior guard; reliability `_floor_w` (15-30g). (A)+(B)
size JOINTLY, whole-ramp, signed per cell, respecting the debut-continuity anchor (both tracks on E[outcome|debut-state]).

## CONFIRM 1 (pk11-24 MID well-sampled) + CONFIRM 2 (PRICER-SEQUENCING LOCK) — SIZING-READY FINAL (2026-06-28) — script `_traj_mid_stability.py`

### CONFIRM 1 — the pk11-24 MID down-correction target is ROBUST, not thin-tail fragile
The pk11-24 MID band (4% elite / 96% bust) is the thin-upper-tail class, so checked before any down-correction. Established
target n=75, mean 408. **Kish effN of the value-weighted mean = 16.1** (adequate — vs the pk3 cells' 2-6, NOT fragile).
Bootstrap 90% CI of the mean = [270, 563]; the option to beat (825) exceeds even the CI-high (563) → over-pricing **ROBUST**.
Jackknife drop-top LOWERS the mean (Butters→346, top-2→318, top-3→291) so the over-pricing only worsens without the elite —
not fragile to over-counting. Wide-pick-kernel cross-check (borrow pk6-30): @pk15 = 474 (H=0.4) / 495 (H=0.7), still well
below 825. ⇒ the over-pricing is real and adequately sampled. REFINEMENT: size the down-correction to the STABLE WIDE-KERNEL
target (~480), not the narrow 408 — a conservative, robust target (option 825 vs ~480 ≈ 1.7×). Not the pk3-class error.

### CONFIRM 2 — PRICER-SEQUENCING LOCK (supersedes Lock 1's "defer pricer to Stage-4")
**LOCKED:** the per-cell prospect-vs-established pricer basis (+101 / ~13%) is **folded into the TARGET CURVE FIRST**
(v_at_peak realized curve → ESTABLISHED curve, per cell), and THEN (A)+(B) size the option to the established curve, signed
per cell. This **SUPERSEDES Lock 1's** statement that the pricer is a separate Stage-4/bake step — it CANNOT be deferred
because it flips the signed direction per cell (e.g. pk25+ MID over→under: v_at_peak 1.20× vs established 0.90×). No later
step re-defers it. Consequence: the signed corrections hit the right level once — MID pk11-24 lowers to its established target
(~480 wide-kernel), pk25+ MID LIFTS (under-priced on established basis), crash positions (GEN_FWD/KEY_DEF) lift hard. The MID
correction is NOT applied via the v_at_peak curve AND the pricer separately.

### SIZING-READY — final pre-Stage-2 state
Target = the per-cell ESTABLISHED curve (pricer folded in), era-normalized, bust-weighted, 2008-2021, survival-in-curve +
timing-along-ramp (Lock 2), thin pk3 + thin pk11-24-MID handled by wide-kernel, RUC pooled. Lever set (audited): (A) level-lift
+ live-pole thin-sample hold; (B) upper-band re-centre to realized p70-p97 (load-bearing, SIGNED — lift crash positions, lower
pk11-24 MID to ~480); Lock-2 timing decay (principled staleness, KAPPA retired); age-gate #5 (independent surface); (C)/old-p97
dropped. (A)+(B) size JOINTLY, whole-ramp, signed per cell, against the established curve, debut-continuity anchored (both
tracks on E[outcome|debut-state]). Nothing baked; live store Stage-0 (53728e6a); board/HTML untouched; before Stage 2.

## ═══ GATE 1 + GATE 2 (sizing-prep close, 2026-06-29) ═══
CONVENTION: RL_GAMMA not in value path (redesign_value/cond_prior/tail_restore undiscounted) -> VALUE line target = FLAT-100.

GATE 2 (responsiveness) = **FAIL** on current engine.
- L1 bands pick-BLIND: pk1 & pk20 MID @ same perf -> IDENTICAL band (q10=72,P50=91,P70=101,P90=110,P97~125). Pedigree asymmetry NOT in band; only via pole.
- L2/3 controlled (36g, only pick+perf vary): pk1@70(-5 par)=1700 < pk20@72(+9 par)=1899 -> FAIL prior does not dominate.
- ROOT = dead pole: _floor_w->0 at 30g => established young MID priced on pure performance (THE U28-D level=0/Kyle target). Falsifier for the fix: pk1@70 must out-price pk20@72 post-fix.
- MAGNITUDE: 20pt perf swing = +104%(pk1)/+203%(pk20) of base = heavy perf-chasing (band collapses to current perf).
- REAL players confounded: Lalor pk1(2703)/Reid pk1(2896) > Boekhorst pk19(6)/Dow pk21(57) but on ABSOLUTE perf not pedigree; Boekhorst pk19@72avg=6 = ANOMALY (separate flag).

GATE 1 (flatness) = NOT passed.
- (b) pick-resolved decay MEASURED E[mature|not-deb-by-t,band]/curve: pk1-10 0.28/0.32/0.12, pk11-24 0.11/0.02/0.12, pk25+ 0.01/0.00/0.00 -> gentle-top/steep-deep CONFIRMED. BUT pick-band pools delayed-debut top picks (O'Meara injured) with busts -> needs ELAPSED-OPPORTUNITY axis (injured/no-opp vs passed-over), not pick alone.
- (a) survivorship-clean position premium: measured-on-synthetic-vpk reconstruction FAILED to lift (my bug, too rough) -> pooled line climbed 23->91 again (haircut intact). Earlier pooled taper lifted to ~66 (undershoot). Clean flat construction OPEN. Constraint holds: must NOT pin debut-conditional (prices winners, sits >100 early); clean-check held (nothing >100) only because nothing lifted.
- CONCLUSION: GATE 2 fail is the U28-D dead-pole reason => responsiveness fix and flat-premium fix are the SAME work. Sequence: dead-pole/elapsed-opportunity FIRST (gives pedigree-shaped mass for premium to hold), THEN re-measure position state-discount clean.

## ═══ P97/BAND PROVENANCE — answered from CODE (2026-06-29) = CASE (B) REGRESSION ═══
(a) re-read p97 values (MID 3889/RUC 5208/KEY_FWD 2202/GEN_DEF 2425/KEY_DEF 2361/GEN_FWD 1601) appear in ZERO .py/.js — docs only. Lever B NEVER wired.
(b) live band = cond_prior_band, Q=[0.10,0.30,0.50,0.70,0.90] — caps at q90, NO q97. redesign_value (live established path) prices this 5-pt band via _price_repl with WQ=[0.2x5] — no tail extrapolation. This IS the engine's band (not a helper). GATE-2 P97 col was my own extrapolation, not engine.
(c) tail only live PRE-DEBUT: TR.rval=priceband(restore(band5)) lifts p70/p90 for HIGH_TAIL, fires only when level_now is None. On debut -> redesign_value drops the restore, caps q90. DEBUT-DISCONTINUITY: tail present pre-debut, vanishes when established.
VERDICT (B): value-holding upper tail MISSING from established young players. Drives early-year undervaluation (value falls at debut) AND is a 2nd independent cause of GATE-2 fail (pk1 edge lives in convex q90->q97 tail; engine caps both at q90 -> bands read identical). Dead pole AND capped tail both flatten pk1->pk20.
DOC-VS-CODE REGRESSION: docs claim p97 re-read into lever B + old +11/+8/+5 adds retired "because re-read into B". CODE: lever B never wired, established tail = ZERO. The +11/+8/+5 were removed without their replacement going live.
BUILD IMPLICATION: p97 re-implementation (1B) MERGES with pole fix (2) -> one build = restore pedigree-shaped upper tail to established young players = lever B = the "pedigree INTO the band" requirement. Lever B is joint-sizing -> construction choice (curve re-read / q97 GBM / carry-restore-through-debut) is Luke/supervisor's call. Floor(3) + pk1xpk20 grid + xlsx book all POST-tail-fix. HELD pending confirm(B) + tail-approach pick.

## ═══ TAIL-RECONSTRUCTION MEASUREMENT (3 options, 2026-06-29) — analysis only, NOTHING built ═══
TEST: Sheezel pk3 yr2=118 (WELL, mature116) vs Dylan Stephens pk5 yr2=26 (BADLY, mature69, 94g confirmed bust).
RESPONSIVENESS (top-tail level WELL/BADLY): raw-p90 125/80; opt1 restore-p90 125/80 (INERT-no-op, restore faded rw=0 for established); opt2 curve-p97 128/126 (FROZEN, perf-blind, over-values busts); opt3 q97-GBM 125/87 (RESPONDS). Only opt3 meets criterion.
SHAPE (yr2 good->bad, realized, ceiling p97 vs body p50/p70 drop):
  MID n246 p97 -14, body -27/-28 = BODY drops ceiling HOLDS (slow-dev)
  GEN_DEF n174 p97 -9 body -18/-16 = BODY/ceiling-holds
  KEY_FWD n91 p97 -4 body -13/-11 = BODY/ceiling-holds
  RUC n43 p97 +8 body -28/-29 = BODY/ceiling-holds (thin)
  GEN_FWD n198 p97 -16 body -20/-20 = both move
  KEY_DEF n83 p97 -25 body -17/-11 = CEILING drops (lost upside) — LONE exception
  -> tail must be POSITION-AWARE: hold ceiling early for slow-dev, drop for KEY_DEF, body responds everywhere.
CONTINUITY (pre0g->post, Sheezel): raw 96->125 (mechanical step we fix); opt1 115->125 (SMOOTHS, its value); opt2 128->128 (flat-frozen); opt3 110->125 (perf-driven update, not spurious step). All 3 remove mechanical drop.
COST: opt3 = retrain q97 off 400-tree bake; opt1/opt2 no retrain.
READ (Luke picks): opt3 = only responsive option; riders = retrain cost + MUST verify year-2-boundary ceiling-hold per shape (UNVERIFIED, the one check before trusting opt3 shape). opt1 = boundary-smoother not a tail fix (pair candidate). opt2 = cleanest wire but frozen/over-values busts. HELD for construction pick.

## ═══ TAIL VERIFICATION (3 conditions, opt3 q97 GBM, 2026-06-29) — analysis only ═══
(1) YEAR-2 CEILING-HOLD = PASS all pos. q97 early(2yr10g) vs mature(5yr18g) GOOD/BAD: Δearly 0-6 (bad~good early), Δmat 10-32 (gap opens at maturity). No early slash on slow developers. MID 6/31, GEN_DEF 2/23, KEY_FWD 4/28, KEY_DEF 4/25, RUC 0/10.
(2) POSITION SHAPE = PASS. q97 yr2-bad ceiling matches realized bad-yr2 mature p97 per pos: MID 101~108, GEN_DEF 95~102, KEY_DEF 78~73, RUC holds highest. Differentiation captured.
(3) PICK RESOLUTION: well-resolved (effN Kish pk1 283 -> pk50 8188, all high; RUC/deep-tail thin->widen+flag). Raw q97 slightly lumpy (pk2 108>pk1 104) -> log-pick kernel H=.30 cleans. ** KEY REFRAME: q97 LEVEL is FLAT across picks (pk1 104, pk5 103, pk15 101, pk45 99 = ~5pt spread). Elite CEILING is ~pick-independent; pedigree buys PROBABILITY of reaching tail (lives in BODY q50/q70, which DO separate by pick), NOT the tail level. => tail restoration = convex-UPSIDE fix (undervaluation), NOT the pk1>pk15 gradient carrier. The pk1>pk20 falsifier gradient is POLE+BODY-borne. Build expectation corrected: report P50/P70 clearly above for pk1, P90/P97 only marginally. **
COMMISSION-READY with (3) understanding: tail=flat-level convex-upside restorer (pos-aware ok, yr2-safe ok, pick-smoothed); responsiveness gradient from pole revival + body pick-gradient.

## ═══ PRE-BUILD CHECK: REPL + POLE-SUFFICIENCY (2026-06-29) — analysis only ═══
REPL: uniform -3 does NOT compress pk1-vs-pk20 at-draft pole gap. Priced gap 29->33 (+14%), pk1-pk40 100->117 (+17%) — PRESERVED (widens). Contingent graded-floor fix NOT triggered; uniform -3 stays.
LOCUS: at-draft pole pedigree advantage is in FLOOR q10/q30 (pk1 29/38 vs pk20 24/26), NOT body q50/q70 (46~47, 65~65 flat). Pure downside-protection. Falsifier shows q10/q30, not q50/q70.
** DECISIVE: reviving _floor_w ALONE does NOT pass falsifier. w=1: pk1@70 prod537/pole83/lift0/ev537 < pk20@72 prod586/pole105/lift0/ev586 = FAIL. At-draft band median q50=27 sits FAR below par~75 (forward-best3-from-draft = ramp+busts, not mature peak) -> pole can't hold pk1 at par. **
FIX: par-centred pole flips it: pk1(par75)pole598>prod537->ev598 ; pk20(par63)pole148<prod586->ev586. Posterior pk1@70 598 > pk20@72 586 = PASS (prior dominates narrowly/correctly).
BUILD IMPLICATION: pole revival must be PAR-CENTRED (mature pedigree expectation, source from par_redesign/PR par band per pick), NOT _adraft_band. Lift-only preserved. Tail(q97 convex upside) + REPL(-3) unaffected; this is the pole CONSTRUCTION. Naive _floor_w revival = failing falsifier = wasted rebuild. HELD for par-centred-pole source confirmation.

## ═══ MERGED BUILD — FALSIFIER CLEAN (2026-06-29) ═══
Engine (wrapper, NOT baked): ev = prod + w_age*recover(perf,par)*max(0,par_pole-prod). prod=price6(cond_prior+q97tail); par_pole=price6(young player @ par_at(pos,pk,T)); w_age=clip(1-(age-20)/6,0,1) [Kyle fix, RUC=0]; recover=clip((perf-0.5par)/(par-0.5par),0,1) [HYPOTHESIS shape, CONFIRM vs realized].
PAR CURVE (verified right): par_at(MID,1)=77..99, par_at(MID,20)=58..80 — matches Luke par~75/63.
FALSIFIER ALL PASS: PRIMARY pk1@70 2386 > pk20@72 1625; BUST pk1@40 ->355 (11% of par, recover=0, FALLS not rescued); ELITE pk20@95 4771 > pk1@62 1763; GRID pk1>pk20 every par-offset. Mechanism: marginal miss held toward par (recover 0.62), deep bust falls (recover 0), elite performance rises above pedigree.
EARLIER BUG FIXED: at-draft pole + linear lift over-held busts (pk1@40 2691=85% par). Recovery-gate fixes it.
CAVEAT: recover shape (BUST=0.5par, linear) is hand-picked HYPOTHESIS -> MEASURE realized recovery (P(reach par|below-par-by-d, games)) to confirm/correct, per discipline.
REMAINING BUILD: elapsed-opportunity (non-deb) + GATE-1 flatness (pole+tail alive, survivorship-clean) + slow-dev row (Patterson/Annable modestly below draft) + 1/4 GEN floor (Oscar/Tew/Jakob) + xlsx backtest book. Engine is falsifier-clean foundation.

## ═══ RECOVER SHAPE MEASURED + RECORD RECONCILED (2026-06-29) ═══
RECOVER (realized E[realized/par | early perf/par]): 0.45-0.60->0.64, 0.60-0.75->0.84, 0.75-0.90->1.05, 0.90-1.05->1.21 (vs hand-picked 2r-1: 0.11/0.38/0.67/0.95). Young below-par players RECOVER; hypothesis far too harsh. Measured curve REPLACES 0.5par-linear. Guardrails on measured: PRIMARY/ELITE/GRID PASS; BUST pk1@40=56% of par = realized recovery of STILL-PLAYING pick (NOT rescue) — genuine busts STALL/EXIT -> 1/4 floor handles them. recover gate + floor jointly satisfy bust guardrail. recover shape now REAL.
RECORD RECONCILED by DELETION: killed 'size (A)+(B)/run the sizing pass' NEXT instruction in HANDOVER/KICKOFF/SESSION_SUMMARY (the step that produced -16,529); SUPERSEDED banners added pointing to START_HERE; UNRESOLVED U28-D-OPEN->ACTIONED, floor 200-250->1/4-draft, p97-tail-restore->opt3/pedigree-in-floor all deleted. START_HERE rewritten as SINGLE authoritative page. -16,529 diagnosis banked (sizing pass dropped up-leg; up-leg then built).


## ═══ ENGINE WIRED — delist + staleness + isotonic (2026-06-29) — NAMED-PLAYER PROOF ═══
Engine _merged_recover.py md5 36d01244 now wires (into the engine, not post-hoc): (1) delist/_retired/_last_listed<2026 -> ~0.02*draft; (2) staleness floor ALL stalled (<=1 season after window) -> ~1/4 draft tenure-declining, KEY/RUC gentler+later, + mediocre-for-years branch; (3) isotonic pick guard (monotone non-increasing in pick# at par, per position).
BEFORE->AFTER: Ronin O'Connor 526->10, Will Martyn 554->9, Sam Philp 714->15 (delisted->~0). Oscar Ryan 570->156, Tew Jiath 509->139, Jakob Ryan 594->140 (stalled->1/4). KEY_FWD pk1<pk2 FIXED (pk1=pk2=pk3=2206 monotone). Coleman 723->767 >= Stephens 761 (inversion FIXED). 2019 deep picks (pk>40) 82%->25% of draft (collapse toward realized). FALSIFIER still clean: pk1@70 2879>pk20@72 1627, pk1@40 1791, pk20@95 4777>pk1@62 2595, grid PASS.
FLAGS: (5) GATE1 improved (KEY_FWD yr1 55->75, MID yr1 83->126; no early crash) but NOT cleanly flat -> remaining. Harrison Jones 521 + Stephens 761 price per RECENT data (Harrison recent 0.84*par serviceable; Stephens 2026=77.6 RECOVERING) -> "near-valueless/below-replacement" reads DISAGREE with 2026 scoring; engine logic correct given data — Luke to confirm inputs. BOOK RETRACTED (built on incomplete engine; rebuild only after GATE1 flat).


## ═══ PRODUCTION-READ METHODOLOGY FIX (2026-06-29) — engine md5 bcef17cc ═══
EXPOSED: the level FEATURE driving cond_prior (_lvl_eff=_lvl_wt*reliability) is ALREADY games x recency weighted: _lvl_wt = sum(g*0.72^Dyr*avg)/sum(g*0.72^Dyr) (uses RL_RECENCY_DECAY). It ranks correctly: prod Riccardi 368>Jones 222, Georgiades 1422>Kemp 799. The FLAT reads were (a) book PeakAvg display (max-season), (b) the recover-gate perf (flat mean), (c) fwd_best3 target.
ROOT of the value inversion (Jones 528>Riccardi 368) was NOT the read — it was the PAR-POLE LIFT over-crediting a mediocre SHALLOW pick (Jones pk30 prod 222 lifted to 528 by a high par-pole) while a proven DEEP pick (Riccardi pk51) barely lifted.
FIX (methodology, not patched-to-target): (1) recover-gate perf now uses WEIGHTED _lvl_wt not flat mean; (2) POLE FADES by demonstration: w *= clip(1-(tenure-2)/3) -> full at tenure<=2 (young, pedigree matters), OFF by ~5 seasons (level demonstrated). Established players settle to their correctly-weighted prod.
CONSEQUENCE (natural, not reverse-engineered): Riccardi>Jones OLD FAIL(368<528)->NEW PASS(368>222); Georgiades>Kemp NEW PASS(1422>799). WELL-SHAPED STAY PUT: Serong/Green/Daicos/Coleman all stable (prod~=pole, no lift either way). Only lopsided/mediocre cases moved.
BONUS: this RESOLVED the earlier Harrison/Stephens 'input-data discrepancy' flag — it was the POLE not the data; Luke's reads were correct. Harrison 528->219, Stephens 761->293, Coleman 767>>Stephens. delist/staleness/isotonic intact, falsifier still clean.

## ═══ POLE-FADE MEASURED + TARGET RULED OUT + BUST RE-CHECK (2026-06-29) — engine md5 7f7d7f76 ═══
V1 FADE MEASURED (not guessed): residual predictive value of PICK beyond demonstrated level decays on TENURE (controlling for level, partial r(pick|level) = 0.29/0.22/0.12/0.05/0.01/0.03 at T=1..6; corr(level,mature) climbs 0.44->0.93). GAMES does NOT decay cleanly (stays 0.17-0.29) -> fade on TENURE not games. MEASURED fade [T1..6]=[1.00,0.76,0.40,0.16,0.05,0.05] REPLACES guess [1,1,0.67,0.33,0,0] (guess faded TOO SLOW T2-4). Applied via np.interp.
V2 TARGET RULED OUT: fwd_best3 (flat best-3 of >=6g forward seasons) correlates 0.998 with a games-weighted forward target; models trained on each give near-identical predictions (mean|Dpred|=1.02; 4-player D=+0.2..+0.8). The >=6g filter already excludes thin seasons -> flat target does NOT contaminate. Feature fix (_lvl_wt) is real, not cosmetic.
V3 BUST RE-CHECK: earlier "57%=consistent with recovery" was a LEVEL-vs-VALUE error. Young below-par high picks recover to 0.70 of par in LEVEL but only ~0.08-0.15 of par in VALUE (convex pricing). So the bust was OVER-valued; the pole-fade did NOT over-correct, it under-corrected. Measured fade brings bust to ~38% (tenure2) -> right direction. RESIDUAL: recover-gate is level-calibrated, slightly over-reads in value terms; bust still ~38% vs realized ~8-15% (n=3 thin). Flagged.
HOLDS with measured fade: Riccardi 371>Jones 234, Georgiades 1439>Kemp 833; well-shaped STABLE (Serong 4305/Daicos 7115/Coleman 767); falsifier (young tenure-2, fade 0.76) pk1@70 2729>pk20@72 2481, elite/grid PASS; delist/staleness/isotonic intact.

## ═══ RECOVER-GATE VALUE-SPACE re-calibration + GATE 1 attempt (2026-06-29) — engine md5 7f7d7f76 UNCHANGED ═══
FINDING (against the instruction's premise — surfaced, not forced): the "bust should be 8-15% of par-value" target was itself a SURVIVORSHIP-BIASED fixed-synth read (n=3, excluded recoverers). Measured PROPERLY in value space:
  - survivorship-corrected (busts included as value~0), mature-par benchmark (removes the 2-season-par development confound), deep end POOLED for sample (n=427 total):
    deep-below(<0.62, BUST zone) n=8: 38% bust, E[value/mature-par]=0.66 median 1.00 (BIMODAL: ~38% bust to 0, ~62% recover to ~par)
    below(0.62-0.80) n=79: 37% bust, E=0.75 | near(0.80-0.95) n=122: 20% bust, E=1.20 | at n=117: E=1.34 | above n=101: E=1.54
  - So below-par-at-2yr players realize E[value]~0.66-0.75 (they mostly recover); the level-ratio RECY [.54,.64,.84,1,1,1] is ALREADY within ~0.1 of this. The "level-vs-value units error" is conceptually real but numerically tiny — below-par value recovery genuinely is ~0.7 because the survivors reach par. If anything the gate slightly UNDER-credits near-par (measured 1.20 vs 0.84).
RECOMMENDATION: do NOT reduce the recover curve to 8-15% (that fits a biased measurement and under-values the majority who recover). Keep the recover-gate. The bust guardrail for TRUE busts is enforced by DELIST + STALENESS (the ~37% who exit), not by slashing the gate. The bust synth at 38% is in line / slightly low. Earlier "57% bust" was NOT an over-valuation.
SUBTLETY noted: the recover-gate applies at valuation time (survival unknown), so it correctly targets the survivorship-CORRECTED unconditional E[value]; delist/staleness handle the actual exits separately. (Benchmark-alignment of par_pole at current-T vs mature-par is a small possible follow-up, not load-bearing.)
GATE 1 (NOT passed): cross-sectional engine-value-by-tenure over live native players (n=529) is confounded — heterogeneous draft cohorts at each tenure, n=3-14 cells. Lines noisy + declining (GEN_FWD 257->50, GEN_DEF 517->63 = partly correct pole-fade on young high-picks, partly small-n). corr(engine value, realized production)=0.53 over 452 mature players (mediocre — flag). CANNOT certify flatness. GATE 1 needs a winners-normalised WITHIN-PLAYER design (truncate each player's history to tenure T, track value vs own mature value). STILL OWED.

## ═══ GATE 1 — within-player, LEAKAGE-GUARDED — PASSED (2026-06-29) — engine md5 7f7d7f76 ═══
DESIGN: each test cohort (2014-2018) held ENTIRELY OUT of training (pool= excludes it); held-out cond_prior (matched 150 trees) prices its players at TRUNCATED tenures (only <=T info); structural pole (synthetic par) stays in-sample (contains no test-player career, so no leakage path). IS and WF both @150 -> the gap IS the leakage (tree-count-robust). Normalised to par-VALUE; split future-GOOD (real mature best-3 >=0.85 par) vs BUST (<0.55 par).
LEAKAGE ~ ZERO: IS vs WF profiles near-identical everywhere (e.g. MID GOOD WF[37,46,54,59,72,69] vs IS[36,45,52,60,72,69]; KEY_DEF GOOD WF[44,50,69,59,54,55] vs IS[39,49,55,58,48,49]). Holding one ~60-player cohort out of a 12,655-row model barely moves it -> the early read is GENUINE PREDICTION, not recall. The cohort-trajectory leakage (106->96) does NOT infect the within-player value read.
SEPARATION (early): future-GOOD sit 34-84% of par; future-BUST floored to ~0-1% (delist/staleness). Clean, large, present from T0-T1.
POLE PRICES PEDIGREE BEFORE PROVEN (pick-split, future-good, leakage-guarded): HIGH-pick (pk<=12, n=51) [T0:53 T1:57 T2:65 T3:78 T4:81 T5:84] — high at the DRAFT, climbs smoothly. LATE-pick (pk>=25, n=116) [T0:34 T1:43 T2:46 T3:46 T4:27 T5:37] — low early, production-driven, noisier. Exactly the intended mechanism.
SHAPE PRINCIPLE: no violent yr0/1 jumps or crashes; high-pick-good line is smooth & monotone; late-pick-good noisier but no crashes. GOOD tops ~84% (not 100%) of par at T5 = convex pricing + T5-truncation missing later-peak seasons + age, NOT a failure.
VERDICT: GATE 1 SOUND (leakage-guarded). This was the LAST engine gate. Engine validated end-to-end: recover-gate kept (value-recovery ~= level-ratio), pole-fade MEASURED on tenure, GATE 1 passed leakage-guarded. NOW cleared for the book (FULL format: every cohort, every player year-by-year, sum-ratio not mean-of-ratios).
