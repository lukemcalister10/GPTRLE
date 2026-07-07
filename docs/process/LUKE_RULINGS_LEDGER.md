# LUKE'S RULINGS LEDGER — repo-side authority trail
_Minted 2026-07-03 (DIRECTIVE 8 ASK 1). Until now the ledger lived supervisor-side only
(`docs/supervisor_handover_2026-07-02_rev93_ROTATION.md` §4). From D8 on, every Luke ruling the build
must honour is registered HERE verbatim (plus CHANGELOG), same session it lands. Rulings are quoted
exactly as relayed; the relaying directive is the provenance. Backfill for pre-D8 rulings is
POINTER-ONLY (CHANGELOG citations) — no historical wording is reconstructed here._

## Format
`R<N> · date · ruling name · Luke verbatim · consequence · status`

## D8 rulings (2026-07-03, relayed via DIRECTIVE 8 v1)

**R1 · 2026-07-03 · A3 accept-red at 0.7307**
Luke verbatim: "Accept-red on rozee."
Consequence: A3 ships red at 0.7307 vs the amended 0.75 bar, by ruling (joins A2/Curtis as a
Luke-ruled red). Real remedy = the LTI workstream, queued. No threshold motion.
Status: ACTIVE.

**R2 · 2026-07-03 · Tsatas accept-and-track at 1140**
Luke verbatim: "Accept and track on Tsatas."
Consequence: the M3-caused lift above his preferred 1083 is accepted; TRACK the fade to 979 as the
season completes (fE→1). A8 holds 2.12x.
Status: ACTIVE (tracking).

**R3 · 2026-07-03 · Staleness-cap fix Form A — endorsement WITHHELD**
Luke verbatim: "The two cap fix is odd, because someone like Cleary is far too low when he triggers
it and probably too high when he doesn't. That Hardeman doesn't get rescued is a challenging one for
me. And looking at Cooper Lord - he's another in the Cleary boat but worse - he shouldn't be so low
now, but the idea of him being over 1000 if it didn't catch him is a bit crazy to me."
Consequence: Form A (binary gap=0 exemption) is NOT endorsed and joins NO candidate. The D7 design
read stands as a derivation artifact, superseded by the D8 graded-form round (continuum ghost-floor →
full price, driven by evidence of live output). Also registered in SYMPTOM_REGISTER.md family 1.
Status: SUPERSEDING WORK IN FLIGHT (D8 ASK 2).

**R4 · 2026-07-03 · McAndrew release ENDORSED**
Luke verbatim: "McAndrew is fine."
Consequence: his D7 cap-fix release (99→1408, 13g @ 87.1 = 1.11×REPL) is Luke-approved; McAndrew is
an ANCHOR for the graded derivation (strong-evidence upper anchor: strong current output → full
release), no longer an open question.
Status: ACTIVE (anchor).

## Pre-D8 rulings (pointer-only backfill — verbatim lives in the cited CHANGELOG entries)
- Growth law redefined (cross-cohort AVERAGE, per-cohort ungated) — CHANGELOG 2026-07-02 D5 STEP 1.
- Overlay keep M1 + v7-asc, DELETE v7-cB — CHANGELOG 2026-07-02 D7 (ASK 1).
- A3 bar 0.80→0.75 ("Happy to adjust Rozee to 75%") — CHANGELOG 2026-07-02 D7 STEP 1.
- B5 alarm RETIRED → pricing floor feature, flat tail variant A — CHANGELOG 2026-07-02 D7 STEP 1.
- A2 unchanged at 0.90, ships red ("we can look at Curtis down the line") — CHANGELOG 2026-07-02 D7 STEP 1.
- A10 bar 0.70→0.50 (data-caused, provisional) — CHANGELOG 2026-07-02 D4 STEP 1.
- Gothard calibration "probably fine, a touch rich, happy to leave it" (~1790, no shaving) — CHANGELOG 2026-07-02 D6/D7 (ASK 4).
- Effort rule + downward-justification amendment — docs/process/PROCESS_CHANGES_2026-07-02.md §11.

## D10 rulings (2026-07-03, relayed via DIRECTIVE 10 — GAMES-RAMP REWORK)

**R5 · 2026-07-03 · The games-ramp design statement (BINDING SPEC — the old-PVC sit-out anchor is retired)**
Luke verbatim: "B6 - fix first. But I do not accept the 'half of draft value' as that is derived from
the old PVC, which I believe is a relic and retired. So it makes no sense. All players are being given
a value 'the moment they are drafted' that they hold over the pre-season before their first season
starts, and then it starts responding to matches throughout the season. [...] what is happening
currently is that Annable and Cumming are being drafted, assigned a value based on their draft pick
and position, and then when matches start and Annable does not play, his rating is flipping back to
50% of the old, historical PVC." · "we should not be punishing players like Patterson for not playing
a full season when the full season has not concluded. And we should not be considering players like
Annable a full 'no sit' when he has played 1 game, that penalty should smooth in between games 0-6."
Consequence: the flat SITOUT_RETAIN×draftval anchor DELETED (obituary E2); every penalty path
re-anchored to the LIVE start value V0 (pick+position); smoothed, season-prorated, scoring-aware
games-ramp treatment derived from historical outcomes and wired at CANDIDATE v2.1 (engine e15bafa9);
B6 taken to green. The Luke-signed B5 floor stays dv-based (declared exception, pricing feature).
Status: ACTIVE (candidate v2.1; cold audit before any bake).

**R6 · 2026-07-03 · The three reporting rules (BINDING, permanent)**
Luke's word (relayed as BINDING, D10 ASK 5): (1) every gates/board output reports THREE COLUMNS —
CONTROL · PREVIOUS · CURRENT, deltas explicit; (2) every board/report carries a LOUD state label; no
unlabelled player value anywhere Luke-facing; (3) the rules bind all future sessions.
Consequence: wired in ship_gates_check.py + the book renderer + BAKE_CHECKLIST.md §REPORTING +
KICKOFF_PROMPT.md + START_HERE.md; state registry data/report_states.json; snapshots data/gates_snapshots/.
Status: ACTIVE (permanent process).

## D12 rulings (2026-07-03, relayed via DIRECTIVE 12 — CONCAVE RAMP + FLOOR RE-ANCHOR)

**R7 · 2026-07-03 · Concave penalty ramp (Luke-signed OPTION A — SUPERSEDES the D10 linear form)**
Luke verbatim: "I'm not sure that the proration should be strictly linear... especially when it comes
as a penalty, it should be slightly more generous as the sample is smaller... it will be 100% after 24
games, as it should... something like 33-40% at half way." · Ruling: OPTION A — penalty fraction =
(season progress)^1.5.
Consequence: the sit-out retention's within-season proration goes linear -> concave (sitout_ev tau term
fe -> fe**1.5), PENALTY PATH ONLY; the reward-side M1 G_ADQ gate (its harder-than-linear proration is BY
DESIGN and conforms to this same principle) is left untouched, verified by diff. Penalty fraction printed
R6/12/18/24 = .125/.354/.650/1.0; halfway .354 in the stated 33-40% band; 100% at R24. B6 seam re-proven
green at v2.2. Wired at CANDIDATE v2.2 (engine 05d38c65 after ASK1). REVISIT HOOK: a PVC-era derivation
may replace the t^1.5 SHAPE from partial-season snapshots (recorded open, not a block).
Status: ACTIVE (candidate v2.2; scoped re-audit before any bake).

**R8 · 2026-07-03 · B5 floor basis re-anchored draftval -> V0 (schedule unchanged)**
Luke verbatim: "DV floor should be now aligned with v0. Yes, some issues with rucks, but we can refine
them before baking or wiring."
Consequence: the B5 pricing-floor denominator moves from old-PVC draftval to the live V0 start value
(ev() floor line: floor_frac(yis)*draftval -> *v0_start); the signed schedule FLOOR_YRS .45/.35/.28/.21/
.13/.09 + .05 tail is UNCHANGED (only the denominator re-anchored, joining every other penalty path D10
re-anchored). Floor-saves 58 (+2117) -> 52 (+1330); Patterson floor 884->511 no longer binds (EV 849).
RUC floors PROVISIONAL — the ruck V0 is Luke-ruled hot (h-ruc-startvalue-hot); its nerf lands NEXT
directive before any bake. Obituary E3. Wired at CANDIDATE v2.2 (engine af1fc6aa).
Status: ACTIVE (candidate v2.2; RUC floors provisional pending ruck-V0 nerf; scoped re-audit before bake).

## D13 rulings (2026-07-03, relayed via DIRECTIVE 13 — RUCK CAP + V0 PICK-ORDER + RETENTION RE-DERIVE)

**R9 · 2026-07-03 · RUC prior cap at the 1.73 class median (parameterised dial)**
Luke verbatim: "I'd be inclined to just cap ruck prior at the 1.73 median. But that's just a thought."
Consequence: `RUC_PRIOR_CAP` (env `RL_RUC_PRIOR_CAP`, default **1.73** = the ND-ruck class median V0/PVC,
measured 1.7274) caps the RUC band prior as a max V0/PVC ratio at the raw_ev/band level — flows into V0, the
sit-out blend, the B5 floor and the prior-dominated production leg; proven-ruck production byte-exact. This
RESOLVES the R8 ⚠PROVISIONAL RUC floor and the `h-ruc-startvalue-hot` register item (the ruck-V0 nerf R8
deferred to "next directive"). Dial is Luke's to move at the board view — at 1.73, Emmett = 1054 (above his
stated 650–800; that range sits at ~1.1–1.3). Wired at CANDIDATE v2.3.
Status: ACTIVE (candidate v2.3; dial default 1.73, Luke may re-set; scoped re-audit before bake).

**R10 · 2026-07-03 · V0 pick-order law (isotonic non-increasing in pick within age/pos/year cells)**
Luke verbatim: "v0 for the same age and position cannot be higher for a lower pick in the same draft. I
understand mature age players rightfully will be calculated differently."
Consequence: within (position × draft-age × draft-year) cells, V0 is non-increasing in recorded pick
(downward-only guard, built at load time). Mature-age players in separate draft-age cells → exempt by
construction. Roster inversion scan 449 → 0. Wired at CANDIDATE v2.3.
Status: ACTIVE (candidate v2.3; scoped re-audit before bake).

**R11 · 2026-07-03 · sit-out penalty re-derived (retention surface), Luke's standing objection**
Luke verbatim: "I'm still not happy with the sit out penalty and think it is excessive especially for KPP
players." + "A player should never gain value by sitting out and doing nothing."
Consequence: the depth-only R_SIT table (which violated the no-gain law — nonKPP rose d3→d5, KPP rose d5→d6)
is superseded by a continuous log-pick × depth surface R_SURF, isotonic non-increasing in depth, per class.
R1: daEV(V0) denominator kept (KPP severity numerator-driven, not pole-inflated). R2: pick-conditioned
(fires all classes). Sit-out family +2,861; early-career KPP penalty relieved; residual deep-KPP harshness
is data-derived (honesty clause — further softening is Luke's signed override). Obituary E4. Wired at v2.3.
Status: ACTIVE (candidate v2.3; deep-KPP residual flagged for Luke's owner call; scoped re-audit before bake).

**R12 · 2026-07-03 · V0 BOARD CURVE — Luke's AMENDED LAW (supersedes the D13 spot-guard on the board)**
Luke verbatim: "For the backtesting this is not a rule and doesn't make sense to be, but for the current
values that end up in the engine/on the board, we can't have a situation where one player who was a mid at
pick 8 has a higher starting v0 than another in the same boat. It's illogical."
Consequence: on the BOARD PATH, every real-ND start anchor V0 := V0*(position, draft-age, recorded pick) — a
derived continuous kernel/local regression of the current roster's CAPPED V0s (ruck cap FIRST) over log
recorded pick, pooled ACROSS draft years, isotonic non-increasing in pick. Same pos×draft-age×pick ⇒ IDENTICAL
V0* across draft years (cross-draft dispersion 507→0, gate D14a); within-cell inversions 0 (gate D14b). Cells:
age≤18 per position (finest, eff-n≥35); mature≥19 pooled per position (R1, non-RUC pooled across position —
age-dominated & position-washed; RUC separate). Mature stays differentiated by age (non-increasing in draft-age).
BACKTEST EXEMPT (Luke, verbatim above): the D13 guard is retained off-board so the walk-forward book reproduces
(maxΔ=0). D13 guard-transform → assertion (obituary E5). Moves: 831 up / 740 down; R2 >35% movers=91 (63 mature,
board-ev impact ≤ a few points — production-driven). Wired at CANDIDATE v2.4.
Status: ACTIVE (candidate v2.4; scoped re-audit before bake).

**R13 · 2026-07-03 · KPP SIT-OUT RETENTION FLOOR — SIGNED OWNER OVERRIDE O1 (nonKPP comparator)**
Luke verbatim: "if their yearly value is lower than another position, it gets brought up to that level. So if
it's higher, fine, but if it's lower, it's carried so it can never be the lowest ... whether it's logical or
not I can't see KPPs losing value for sitting at a faster rate than non KPPs." Clarified same day: "I meant KPP
sitting penalty by year. Non KPP only. Across each year it applies."
Consequence: wired KPP retention surface := pointwise MAX(KPP-derived, nonKPP-derived) at every (log-pick, depth),
comparator nonKPP ONLY (RUC excluded — own capped machinery, supervisor spec stated to Luke pre-fire), BOARD PATH
only. Depth monotonicity re-asserted (gate D14c). Binds predominantly d3+ (and d1+ for mid-picks 15–30 where raw
KPP retention sat just below nonKPP — the exact "losing value faster" case). OWNER-SET where it binds, data-derived
elsewhere — registered docs/process/OWNER_OVERRIDES.md O1. Wired at CANDIDATE v2.4.
Status: ACTIVE (candidate v2.4; owner-set override O1; scoped re-audit before bake).
