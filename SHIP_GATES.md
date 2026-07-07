# SHIP_GATES.md — AFL SuperCoach RL engine — FROZEN ACCEPTANCE SUITE
### Status: FROZEN (02/07/2026) — all decisions resolved by Luke; the commit of
### this file to the repo WAS the freeze act (Luke, 02/07/2026).
### Rule: when every gate passes, the engine SHIPS and gets used for real trades.
### Post-freeze the list does not grow — new reads go to V_NEXT.md unless they
### demonstrate an existing gate is broken. Every line becomes a scripted PASS/FAIL
### check (ship_gates_check.py), run at each candidate head and at any bake.
###
### SCRIPTING NOTES (for the build):
### - EXACT-ID matching mandatory: the suite contains Harley Reid AND Zach Reid;
###   the league contains two Uwlands. No substring matching.
### - Line-ball = within ±20% (Luke, 02/07/2026).
### - A13-A14 are PVC-coupled: staged PENDING (not RED) until the pick curve exists.
### - A6 pick-matching: finest resolution with smoothing; pool the thin RUC slice
###   deliberately and say so (standing banding rule).
### - [DC] = DATA-CONDITIONAL gate (rests on current-season / thin-evidence facts as
###   of 02/07/2026); on failure, run the failure triage below FIRST.

### GATE STATUS VOCABULARY (registered D14 03/07/2026 — carried query ASK 3a; the scoreboard
### emitted these words with no governance definition before now):
### - PASS / FAIL — the gate's scripted assertion holds / does not hold.
### - PENDING — the gate cannot yet be evaluated (its input stage, e.g. the PVC, is not built).
###   Not a red; not counted against shipping.
### - NOT-RUN — the gate needs a prerequisite harness run this session that has not happened yet
###   (e.g. B2 needs _gate1_wf.py). Re-run the prerequisite; not a verdict.
### - STRUCK — the gate was deliberately removed by Luke (A15). Not counted.
### - FEATURE — the gate is NO LONGER a pass/fail alarm: it was AMENDED into a PRICING FEATURE by
###   Luke. Exactly ONE gate carries this status: **B5** (the signed year-schedule floor). Luke's
###   D7 ruling retired B5-as-alarm and made the floor a pricing feature at the ev() boundary; the
###   FLOOR-SAVES TABLE (printed every gates-board run) is the NEW alarm surface — a saves-list that
###   grows unexpectedly is the signal the old red used to fire on. FEATURE does NOT mask a red: the
###   signal is not suppressed, it is relocated to a visible, printed list (mispricings stay VISIBLE,
###   never silently clamped), and the pure-lower-bound property (0 lowered, 0 non-ND moved) is
###   re-verified every run. If the saves-list ever needs a hard bound again, B5 returns to pass/fail
###   by Luke's ruling; until then FEATURE = "wired, visible, owner-ruled non-blocking."

## SECTION A — LUKE'S NAMED CALLS (all confirmed)

A1.  Willem Duursma > Zeke Uwland.
A2.  Josh Ward below genuine producers: Ward < Paul Curtis AND Ward < Josh Weddle.
A3.  [DC] Connor Rozee: thin current season must not halve him — 2026 value >= 75%
     of 2025.
     [AMENDED 02/07/2026 (Luke, in writing, D7 directive; verbatim in CHANGELOG):
      threshold 0.80 -> 0.75, DATA-CAUSED — Rozee is out for the remainder of 2026
      (LTI register Section B, register-confirmed); Luke: "Happy to adjust Rozee
      to 75%". KNIFE-EDGE NOTE: the bar deliberately sits at reality's edge — the
      same design as A10/Curnow: the gate should fail the moment the engine
      over-punishes a thin season, not comfortably before. Evaluated PRE-LTI-layer
      (Luke, D4) unchanged.]
A4.  Harley Reid uncratered — Reid remains TOP 40 on the board by value.
A5.  Improvers not slashed: Jack Ginnivan > 1600, Jake Bowey > 2100,
     Nick Blakey > 2600.
     [Absolute SCAR floors — RE-BASE if the PVC re-levels the currency.]
A6.  Early-career rucks: years-1-3 RUC cohort median <= pick-matched MID cohort
     median at the same stage.
A7.  Position fixes stay fixed: Ryan Maric prices off a MID pole; Ed Langdon off a
     GDEF-dominant future. (Regression insurance vs silent reversion.)
A8.  [DC] Sam Berry > Elijah Tsatas by at least 2x.
     (Luke, 02/07/2026: fair on the data available today; explicitly expected to be
      re-ruled if Tsatas's evidence base materially changes — the engine SHOULD
      respond to new data. The exemplar data-conditional gate.)
A9.  Jack Ginnivan > Josh Ward.
A10. [DC] Charlie Curnow: 2026 value >= 70% of 2025.
A11. [DC] Playing beats sitting — named pairs: Jacob Farrow > Dylan Patterson;
     Sam Cumming > Dan Annable.
A12. [DC] Sitting is not unreasonably punished — named pairs: Tobie Travaglia >
     Christian Moraes; Josh Smillie > Patrick Retschko.
     (A11+A12 bracket sit-out retention from both directions; jointly define
      acceptable outcomes for the 1.19x/retention rework.)

### Pick-vs-player anchors (PVC-coupled; PENDING until the curve exists)
A13. Pick 1 line-ball (±20%) with EACH of George Wardlaw and Levi Ashcroft.
A14. Pick ~8 line-ball (±20%) with EACH of Trent Rivers, Zach Reid, Jase Burgoyne.

A15. STRUCK (Luke, 02/07/2026): the Robey-shape package anchor. Reason: "not all
     firsts are equal — pick 1 and pick 15 have wildly different value," and the
     Robey trade itself is not a good exemplar of reasonable value. Consequence
     logged: package-vs-star CONVEXITY is the suite's one known untested dimension
     → seeded as V_NEXT entry #1 (re-poseable with exact pick numbers post-PVC).

### Deliberate NON-GATES (disagreement bounded on purpose; shipping does not wait)
N1. Mid-career (years 3-5) Parish valuation — decider: the matched same-player cut.
N2. The years-4-6 peak LEVEL — not a gate until the matched cut runs.

## SECTION B — STRUCTURAL GATES
B1. Cohort growth law — REDEFINED by Luke (in writing, confirmed, 02/07/2026 D5;
    amendment logged in CHANGELOG; supersedes the per-cohort form and the pooled
    re-script): at each years-in-system depth d, the SIMPLE (UNWEIGHTED) MEAN of
    indexed cohort value (yr1 = 100) across all cohorts observed at depth d must
    rise from year 1 to a peak occurring in years 4-6; pre-peak dips of the
    AVERAGE tolerated under 5% (tolerance carried from old B1 — now applies to
    the average only). Individual cohorts are UNGATED by design (Luke: "not all
    draft cohorts are equal; 2020 is a shocking draft — it should lose value")
    but the per-cohort curve table MUST be printed as a pipe table on every
    gates-board run (Luke's eyeball channel — visibility without a gate). The
    old per-cohort rise backstop is RETIRED — obituary in CHANGELOG (D5).
B2. GATE-1: leakage ~0 (IS vs WF, tree-matched) + clean good/bust separation.
B3. Walk-forward book gates pass at the ship head.
B4. JS parity: Python and board JS byte-agree on the shipped board.
B5. AMENDED 02/07/2026 (Luke-ruled, in writing — text prepared D6, committed D7;
    verbatim ruling in CHANGELOG): B5 as a pass/fail ALARM is RETIRED. The signed
    year-schedule floor becomes a PRICING FEATURE at the ev() boundary:
    ev_final(p) = max(ev(p), floor_yrs(p) × draftval(p)), NATIONAL-DRAFT entrants
    only (MSD/SSP, delisted, retired and pickless players are never floored),
    floor_yrs = .45/.35/.28/.21/.13/.09 for yrs 1-6 and FLAT .05 for yrs 7+
    (TAIL VARIANT A — as signed; Luke's D7 ruling). The FLOOR-SAVES TABLE
    (player · club · yrs-in-system · raw ev · floor · saved-to · lift · register
    status) prints on EVERY gates-board run — the saves-list is the new alarm
    surface: a list that grows unexpectedly is the signal the old gate used to
    fire on; mispricings stay VISIBLE, never silently clamped. The pure-lower-bound
    property (0 lowered, 0 non-ND moved) is re-verified on every board run.
    [Generating rule retained for the schedule: floor ≈ 0.9 × smoothed clean p5
     (ND-only) — RE-BASE at the PVC stage when the draftval denominator re-levels,
     by re-running the generating rule (sibling of A5's SCAR-floor note; this
     in-file reminder Luke-approved in writing 02/07/2026).]
B6. No hard lines: value continuous across the games ramp (no step at the 6-game
    seam) AND monotone in evidence — more games at the same scoring rate is never
    worth less.

### D14 BY-CONSTRUCTION LAWS (Luke-authorized amendment, in writing, 03/07/2026 D14;
### verbatim rulings in CHANGELOG + docs/process/LUKE_RULINGS_LEDGER.md R12/R13; scripted
### PASS/FAIL in ship_gates_check.py, printed green every gates-board run). BOARD PATH only;
### the backtest/walk-forward machinery is exempt by Luke's ruling.
D14a. V0 same-boat law (Luke's amended law): same position × draft-age × recorded pick ⇒
      IDENTICAL starting V0* across draft years (max cross-draft dispersion = 0).
D14b. V0 order law: 0 within-cell (position × draft-age × draft-year) inversions under V0*
      (the D13 spot-guard TRANSFORM converted to this ASSERTION; obituary E5).
D14c. KPP retention floor (Owner Override O1, docs/process/OWNER_OVERRIDES.md): the KPP
      sit-out retention surface = max(KPP, nonKPP) is depth-monotone (never gains by sitting).

## SECTION C — BASELINE GATE (complexity must earn its keep)
C1. Ship head beats the NAIVE BASELINE (last-2-season avg + simple age curve +
    position multipliers) on the walk-forward book headline metrics.
C2. Ship head beats the ORIGINAL V1 pick model on the same metrics.
    (If either fails: stop and re-scope before the PVC.)

## PROCESS
- FREEZE: on Luke's word; committed to the repo; build scripts every line into
  ship_gates_check.py, run at each candidate head and mandatorily at any bake.
- FAILURE TRIAGE (Luke's rule, 02/07/2026 — a live engine must respond to live
  data): on any gate failure, the build attributes the cause BEFORE anything blocks:
    * ENGINE-CAUSED (a code/calibration/store change moved the value) → the gate
      blocks the bake per normal rules.
    * DATA-CAUSED (new real-world results changed the facts the gate rests on,
      e.g. Tsatas returns and performs) → NOT a block; escalate to Luke for an
      uphold-or-amend ruling, logged in CHANGELOG per the amendment process.
    * AMBIGUOUS → decompose (isolate engine change vs data change) before either
      path; no undecomposed attribution.
  [DC]-tagged gates get the triage question first by default.
- V_NEXT.md: every post-freeze read/gripe lands there, dated, untouched until the
  suite passes. Entry #1 (seeded at freeze): package-vs-star convexity anchor,
  re-poseable with exact picks once the PVC exists.
- AMENDMENT: Luke-only, in writing, reason logged in CHANGELOG.
- Red gates at freeze time are allowed and expected (e.g., A3/A10 pre-decay-fix):
  a red gate is the definition of what a fix must achieve before shipping.
- ENVIRONMENT: gates evaluated in the canonical build environment per the values
  policy (byte-exact within environment; see BAKE_CHECKLIST).
