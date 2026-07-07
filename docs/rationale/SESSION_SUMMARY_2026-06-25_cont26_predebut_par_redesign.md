# SESSION SUMMARY — cont.26 PRE-DEBUT FIX + PRODUCTION REDESIGN (par-centred) — 2026-06-25

**Type: DESIGN + diagnosis. NO code committed.** The engine/prior/HTML are byte-identical to the cont.25
checkpoint. What changed this session is the *design understanding*, and it **supersedes a cont.25 conclusion** —
read §0 first or you will rebuild the wrong thing.

> **THE TWO STANDING BEHAVIOURAL RULES (both from past failures, non-negotiable — also in KICKOFF):**
> 1. **Keep the handover docs current AND SHARE them** (`present_files` / checkpoint tarball) in the SAME turn,
>    proactively. Docs left only in the working dir are lost when the chat ends.
> 2. **Do NOT go off-book.** If you want to build something sensible that wasn't explicitly agreed, STOP, surface
>    it, get Luke's sign-off + before/after numbers. Surface, don't decide.
>
> Plus standing rules: player reads + realized outcomes are GROUND TRUTH; validate PER-PLAYER **and** at COHORT
> level; VERIFY on a REAL native player before asserting (never strip games to fake a clean prospect — mis-prices
> rucks); concise, no walls; data-grounded opinion first; ONE combined rebuild per session on explicit "go";
> **BANDING RULE** — never wide-band a statistic; finest resolution the sample supports, smoothed over log(pick),
> pool deliberately where thin and say so.

---

## 0. HOW THIS SUPERSEDES cont.25 — READ THIS BEFORE TOUCHING THE FLOOR

- **cont.25 concluded:** the soft floor anchors at the wrong thing (the conditional-prior at-draft *pole*); revert
  it to a **β×PVC HARD floor**, `value = max(production, 0.85 × PVC-pedigree)`. That was logged as "the fix."
- **cont.26 found that hard floor is TOO BLUNT, and the real culprit is the PRODUCTION model, not the floor.**
  Proof (Cumming, pk7): a kid averaging **61 over 3 games** and a kid averaging **21 over 3 games** both value at
  the **same** 1667 under the hard floor — because the broken production drags BOTH miles below the floor (831 and
  670, both << 1667), so the floor swallows both and erases the difference. Most young players end up hard-floored
  in years 1–2 → totally generic, no personalisation. That is the opposite of what we want.
- **The key realisation:** the genericness is *not* the floor's fault. It is the **shrink-toward-zero** production
  estimate dumping everyone beneath the floor. **Fix the production and the floor stops being generic** — near-par
  players project *above* it (personalised), only genuinely-poor players get floored. The soft floor was never a
  better mechanism; it was a **band-aid** that blended back toward pedigree to compensate for production being too
  low.
- **NEW DIRECTION (the cont.26 design):** a **par-centred production model with availability-aware evidence
  weighting** (§4). The β×PVC hard floor *stays*, but only as the **absolute downside cap**, not the primary
  mechanism. So: **do NOT just wire the β×PVC hard floor and call it done.** Build par first.
- Status of the cont.25 problem list under the new frame: **B (floor anchor)** is reframed — β×PVC becomes the
  downside cap, fine. **A (GEN_DEF under-projects)** and **C (RUC backwards gradient)** are still real prior
  defects, but they get absorbed into the par rebuild (estimating par per position over a smoothed pick curve *is*
  the per-position calibration). Don't fix A and C as isolated patches if the par rebuild is going ahead — do them
  inside it.

---

## 1. ERRORS I MADE THIS SESSION + THE LESSONS (so the next chat doesn't repeat them)

Luke's explicit ask: new chats "get up to speed from docs but have context gaps and repeat mistakes past chats
learnt from." These are this session's, with the lesson each teaches:

1. **Mislabelled the pre-debut pedestal as "the pick value."** I quoted `MA.value(stripped Farrow) = 1371` as
   "pick 10's value." It is NOT. It is `PVC[10] × debut_factor` evaluated at the **current** `SEASON_PROG = 0.58`
   (≈ round 14), which bakes in the ~7% *mid-season* undebuted discount. The raw PVC at pick 10 is **1482**.
   → **LESSON: `MA.value` on a stripped player at the live season point is NOT the raw/draft-day value.**
   `debut_factor` is **season-aware** (§2). To get the draft-day pedestal, evaluate at `SEASON_PROG = 0` (gives
   1.0 × PVC). I carried the round-14 point on a curve into a draft-day number where it doesn't belong.

2. **Silently switched conventions mid-conversation.** Between turns I changed the pick-value base (pedestal 1371 →
   raw PVC 1482) AND the prior (old ≤2020 → retrained 2003-2018), without flagging either, so my numbers stopped
   reconciling and Luke had to chase the discrepancy. → **LESSON: state which anchor (raw PVC vs pedestal vs
   β×PVC) and which prior (≤2020 vs 2003-2018) every number uses. Don't move the goalposts inside a thread.**

3. **Called the low-sample distortion a pure "error" before Luke corrected me.** I framed "you need to average 87
   over 3 games to look on-track" as a bug to be removed. Luke's correction: **low games is itself a signal** —
   "why didn't you play 20?" (injury, can't hold a spot) is real information; don't throw it away. The *actual*
   mistake is narrower (§4): we measure games against a **full ~22-game season**, so a full-availability player
   mid-season looks deficient when he's dead on-pace. → **LESSON: separate AVAILABILITY (did you play when you
   could) from CONFIDENCE (how much we've seen). Don't over-correct a real signal into noise.**

(Prior sessions' root-cause errors, still worth not repeating: claimed Emmett was undebuted — he has 5 games;
reported RUC pole 415 from a games-stripped Kyle-base synthetic — real native = 765; said rucks crater — they
balloon. ⇒ compute on a NATIVE real player of the position, never strip games to fake a clean prospect.)

---

## 2. THE MECHANISMS — exact, from reading the code (so you don't re-derive them)

**Two pricing paths exist and they hand off at a player's first game:**
- **Pre-debut pedestal** = `rl_model.MA.value(player)` for an undebuted draftee. = `PVC[pick] × debut_factor`.
  It is **position-FLAT** (every position = same number at a given pick; e.g. 1050 @ pk14 verified on all 6 native
  positions). Position differentiation does NOT live here — it lives in the prior.
- **Production (post-debut)** = the redesign path: `rd._price_repl(p, cp.cond_prior_band(p, cm), SC, 'bal')`. The
  conditional prior projects a career-peak distribution conditioned on `(position, pick, games, level, tenure)`.

**`debut_factor(p)` — rl_model.py ~line 588 — IS season-aware (this is the big cont.26 mechanism discovery):**
```
s = los(p)                                    # seasons of service
cg = career games
elapsed = clamp((s-1) + SEASON_PROG, 0, 1.6)  # opportunity-so-far, INCLUDES SEASON_PROG  ← season-aware
ref     = 0.58 * min(1, elapsed)              # expected establishment by now
sig     = _playsig(cg) - ref                  # _playsig(g) = 1 - exp(-g/6)  (saturating)
# asymmetric: Aneg ≈ 0.16–0.28 when below expected, Apos smaller/pick-scaled when above
return clamp(1 + A·sig, 0.78, 1.28)
```
- `SEASON_PROG` is a module global in rl_model.py, currently **0.58** (≈ round 14 of 24). 0 = preseason, 1 = season done.
- **At `SEASON_PROG = 0` (preseason): debut_factor = 1.0 → pre-debut pedestal = RAW PVC, no discount.** So the
  off-season / draft-to-round-1 case is ALREADY handled correctly. The undebuted discount **ramps** with the
  season: 0% preseason → ~7% at round 14 → up to ~12% (clamp floor 0.88) if never debuted all year. The "7.5%"
  Luke first saw was just the round-14 point on that ramp.

**`_lvl_eff(p,Y)` — conditional_prior.py ~line 58 — the SHRINK-TOWARD-ZERO that is the production flaw (§4):**
```
LEVEL_RAMP = 14
_lvl_eff = _lvl_wt(p,Y) * min(1, _exposure(p,Y) / LEVEL_RAMP)   # shrinks the observed level toward ZERO
```
- So a 61-average is fed into the prior as **13** at 3 games, **30** at 7, **52** at 12, full **61** only at ~14
  recency-weighted games. This is the lever to change for the par redesign (shrink toward PAR, not zero).
- `_feat(p,Y)` = `[position one-hot, log(pick), _exposure, tenure, _lvl_eff, age]`. The prior is a quantile GBR
  trained on RESOLVED careers (`build_cond_prior(resolved_cut=…)`), one row per (player, as-of-year).
- `_exposure` is recency-weighted reliable game-count (RECENCY_DECAY=0.72/yr); a long gap reads as ~no recent
  exposure (handles Conway-type 5g@80 stints).

**Existing season-availability machinery (RELEVANT to the §4 availability work — know it before building, or you'll
reinvent or collide with live code):**
- `P_estab` (rl_model.py ~L770) DOES already annualize current-season games (`Gn = hist_games + games_2026/SEASON_PROG`,
  L777) — BUT it is **DEACTIVATED** (`P_HOOK=None` since cont.20; the v4 projection replaced establishment-P gating),
  so it does NOT affect valuations today. It's a dormant *template* for the availability annualization, not a live input.
- The ONLY **active** current-season-availability mechanism is the **B2 haircut** (L800-811, Now-board only): an
  *established* player (≥3 seasons, recent peak ≥90) with **0 games in 2026** and the season >1/3 done gets an age-banded
  haircut (8.8% if <27, 3.9% if 27-29, 0 if 30+; transient, superseded by return data). The par/availability work MUST
  NOT double-count this for established non-players.
- **Neither touches the YOUNG-player availability case Luke raised** (§4b). `_lvl_eff` uses raw recency-weighted exposure
  with NO annualization — which is exactly why the break-even bar inflates at low games. So the availability term is
  genuinely new work, but it should align with the dormant Gn annualization and stay clear of the B2 haircut.

**Standard boilerplate to load everything (any diagnostic):**
```python
rd = Ld('rd','/home/claude/rl_workspace/forward_valuation/dist_redesign.py'); cp=rd.cp; dp=rd.dp; MA=cp.MA
import compute                       # builds the 805 board (needs the rl_after symlink for absolute imports)
cm = rd.build()                      # rebuilds the conditional prior, deterministic under PYTHONHASHSEED=0
MA.BASE_REF = MA.AGE_REF = 2026; MA._pe_clear()
SC = dp.SCALE_DIST
```
Run env: `PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_REPL_DROP_FWD=4 RL_REPL_DROP_OTHER=2
RL_RECENCY_DECAY=0.72 RL_LEVEL_RAMP=14`. (Defaults in code match this, so it reproduces even without the env as
long as `PYTHONHASHSEED=0`.) **TWO Uwlands** — always `f('Zeke Uwland')` for the prospect.

---

## 3. PRE-DEBUT VALUE & POSITION-ALIGNED PVC (the smaller, well-defined pending change)

**The gap (Luke's "Patterson point"):** position is known on draft night, but the engine ignores it pre-debut (the
pedestal is position-flat). After a player debuts, position IS in his value, via the position-aware production
projection. So the only missing piece is the **draft → first game** window.

**The fix — position-aligned PVC:** pre-debut value = `PVC[pick] × position-multiplier`. Multipliers are
LEVEL-space, smoothed over log(pick), derived from realized best-3 on the 2003-2018 cohort, and **conserving**
(prevalence-weighted multiplier = 1.0000 exactly → applying linearly to PVC preserves the board total; verified).
Rough values: **MID ≈ 1.10, GEN_DEF ≈ 1.03–1.06, GEN_FWD ≈ ?, KEY_DEF ≈ ?, KEY_FWD ≈ 0.86, RUC swings** (thin
sample, untrustworthy < pick 8 — pool/smooth). NOTE the **convexity catch**: if you price the multiplier in VALUE
space (convex) instead of level space, conservation breaks by +20–80% per pick (Jensen) → convex value-mults MUST
be renormalised to prevalence-weighted 1.0. (Decision C from cont.25: linear-on-PVC vs convex-renormalised — still
open, lean linear for simplicity/auto-conservation.)

**The pedestal-haircut TIMING fix (Luke, endorsed):** because `debut_factor` is season-aware, the off-season case
is already right (no discount preseason). The only refinement: add a **10% deadband** so the discount is exactly 0
until ~round 3 (10% of 24), then ramps to the same season-end endpoint. Mechanically, gate the current-season
opportunity: `cur_opp = max(0, (SEASON_PROG − 0.10)/(1 − 0.10))` inside `debut_factor`'s `elapsed`. Effect at the
current round is tiny (~0.6%); it matters for the off-season + opening-rounds valuations Luke will run. **Open
sub-q:** keep the season-end-undebuted endpoint at 12% (clamp 0.88) or shallower? Lean keep.
→ This also **dissolves the "keep or drop the pedestal haircut?" question** I put to Luke: for the *draft-day*
value there is nothing to decide — it is raw PVC × multiplier by construction, because the engine already zeroes
the discount when there's been no opportunity.

**Consequence for the redesign (§4):** under par-centring the pre-debut pedestal stops being a separate object —
it becomes "par with zero scoring evidence and a wide band," and the position multiplier is just par's
position-conditioning. So this section and §4 converge; don't build them as two disconnected mechanisms.

---

## 4. THE PRODUCTION REDESIGN — par-centred, availability-aware (THE BIG ONE)

### 4a. The diagnosis (numbers, verified this session)
Holding Cumming (pk7) at a constant 61.3 and varying games, the engine's **break-even average** (what he'd need to
average to stay valued at his pre-season position-adjusted value of 1962) is:

| games | break-even avg to look "on-track" |
|---|---|
| 3 | **87.0** |
| 7 | 83.0 |
| 12 | 69.5 |
| 20 | **66.0** |

And the **empirical par** (median debut-season average, resolved MIDs, ≥6g): **picks 1–8 = 66.0 (n=56)**, picks
9–20 = 58.8 (n=44), picks 21–40 = 58.8 (n=55). So **at a full sample the engine is correctly calibrated to par**
(break-even 66 = empirical par 66; Cumming's 61.3 < 66 → correctly a touch under pedigree). **The distortion is
purely at LOW sample** — the shrink-toward-zero inflates the bar to 87 at 3 games. A pick-7 mid posting a perfectly
fine 61 over 3 rounds is treated as miles off. This is the flaw.

### 4b. Luke's reframe — the distortion is the SEASON DENOMINATOR, not small samples
"You need 87 at 3 games" is not pure error: **low games is a signal** (why aren't you playing?). The real mistake:
we measure games against a full ~22-game season, so a **full-availability** player mid-season looks like a deficient
half-season when he's on-pace. Cumming at 7 of ~13 *available* games is a full-availability player we've only seen 7
times — not half of a deficient 13. ⇒ **Separate AVAILABILITY (did you play when you could) from CONFIDENCE (how
much evidence we have).** This is the same thing as the "par-for-games conflates sample-size with establishment"
hole I flagged — Luke named its cause.

### 4c. The concept — ONE par-centred track (collapses pre/post-debut into one mechanism)
- Every player sits on a single **par-centred** track. Value = blend of a **pedigree** estimate (pick × position =
  the pre-season number) and a **performance** estimate expressed as **deviation from par** (par = the on-track
  trajectory for the player's stage: position × pick × tenure × season-stage).
- The **weight on performance grows with EVIDENCE**, where evidence = *availability-adjusted games × tenure*. Few
  games / fully-available / year 1 → mostly pedigree, light performance tilt. Many games / year 4 → performance
  governs. (Implementation: replace `_lvl_eff = level × min(1,games/14)` with **shrink-toward-par**:
  `effective = par + (observed − par) × weight(evidence)`. On-track player ⇒ effective = par ⇒ no drift.)
- **Not-playing and playing-poorly become the SAME mechanism.** Poor play = direct evidence below par. Not-playing
  = indirect (weak) evidence below par. Same scale ⇒ a season-long non-player and a season-long poor-player are
  commensurate *by construction* — the non-player can NOT be more protected than the poor-player. (This is exactly
  the balance Luke wanted; he has explicitly softened the old "pedigree never drags" axiom — see §6.)
- **The pre-debut pedestal dissolves** into "par with zero scoring evidence + a wide band" → kills the debut
  discontinuity (the value at game 1 = pedigree minus a hair, by construction, because evidence-weight starts ≈0).
- **The band carries the optionality** (Luke's Patterson intuition): less evidence → **wider** band. A non-player
  gets the widest — p50 pulled *down* a little by the non-play signal, p10 low (bust risk), **p90 high** (unseen
  upside intact). A proven-modest kid gets a **narrow** band — lower p90 (ceiling shown), higher p10 (proven to
  stick). Luke: "Patterson could have a higher p90 but a much lower p50 and p10" — yes, exactly.
- **The β×PVC HARD floor stays as the absolute downside CAP** — but now it only catches genuinely-poor evidence,
  because near-par players project above it. No longer generic; not-playing can drag you toward it.

### 4d. How it behaves (the three test cases to mock first)
- **Cumming** (7g, full availability, 61 vs par 66): slight below-par tilt, moderate weight → lands just under
  pedigree, **personalised, not floored**. (Today the broken production dumps him to the floor.)
- **61-vs-21 pair @3g**: today both = 1667 (productions 831 / 670, both < floor). Under par-centring the 61-kid
  projects near pedigree (above floor), the 21-kid drags toward the floor → **they separate**. (At 3g they should
  be *close* — low evidence — but not identical; the hard floor makes them identical, which is the bug.)
- **Patterson** (pk5, 0g, round 15): p50 discounted for prolonged non-play, fat right tail keeps value live on
  potential.

### 4e. THE FAILURE MODES — where this can go wrong (Luke asked me to hammer these; roughly worst-first)
1. **PAR is the load-bearing wall, and it's circular + data-hungry.** Everything centres on
   `par(pick, position, tenure, season-stage)` — many cells → thin samples → noisy par, worst exactly where we're
   already weak (rucks, rare pick×tenure). **Real risk: swap a KNOWN distortion (shrink-to-zero) for an UNKNOWN one
   (mis-estimated par).** Must be smoothed over log(pick) and tenure, pooled deliberately where thin (BANDING RULE),
   and proven stable across eras. **This is most of the work.**
2. **OPTIONALITY × CONVEXITY can silently INVERT the result.** The subtle trap. Wide early band (Patterson) +
   convex pricing (rewards spread) ⇒ a wide enough band can make an unproven kid worth MORE than a proven-modest
   kid — the opposite of the non-play penalty we also want. Net value sits on a knife-edge between "p50 drag pulls
   down" and "p90 optionality lifts up," calibrated on very few clean examples. Get band *shape* slightly wrong and
   Patterson is either punished for not playing or rewarded for it — both look wrong. **Watch this hardest; it's
   where the design most likely breaks.**
3. **Availability can't cleanly separate INJURY from BEING-DROPPED.** Both show low availability, opposite meanings.
   We have games + averages, NOT injury records or clean debut rounds. Within 2026 we can approximate
   (games ÷ rounds-since-debut); historically it's murky. Treat all missed games as negative ⇒ punish injured guns;
   ignore ⇒ lose the signal. Likely accept it as a soft *confidence-reducer*, not a hard penalty, and lose some
   signal. **May be no clean fix without better data.**
4. **Par-centring can drag genuine slow-developers DOWN in year 1** (KPD/ruck bloomers start below par). The
   tenure-fade (light performance weight early) protects them, but the rate is a knife-edge: too fast drags
   developers, too slow protects busts. This is the old "pedigree fades by year 5–6" dial, now load-bearing.
5. **The founding axiom is being SOFTENED — see the consequence plainly.** "Pedigree lifts, never drags" →
   "pedigree is a fading prior; the only true floor is the hard β-cap." Luke endorsed this (he dislikes non-players
   being more protected than poor-players). But it means the model will actively mark good-pedigree players DOWN on
   bad evidence, which it never did before — eyeball real cases (a high pick having a genuinely poor year) and
   confirm the drag feels right, not punitive.
6. **Double-count risk:** a fringe player with FEW games (availability penalty) who also plays POORLY (below-par
   penalty) gets hit twice. Directionally probably right, but the combined magnitude could crater him — check.
7. **Conservation:** par-centring + band-widening + non-play penalty all move the board total; the convexity in #2
   especially can inflate it. Check every piece against prevalence-weighted conservation; re-validate anchors after.
8. **Debut continuity + early-season jitter:** game 1 must = "pedigree minus a hair," not jump (enforced if
   evidence-weight starts ≈0 — verify). Early-season week-to-week swings must stay small (low weight damps them).

### 4f. BUILD ORDER (pin these before any rebuild; Luke's "get it right this time")
1. **PAR** — estimate + smooth per position over log(pick) and tenure; prove stable across eras. (Hardest; #1 lives here.)
2. **EVIDENCE / AVAILABILITY** — define availability-adjusted games (games ÷ rounds-available) and the tenure-fade weight.
3. **BAND SHAPE at low evidence** — where #2 lives; needs the most care.
4. **MOCK on Cumming, the 61-vs-21 pair, and Patterson** — read the numbers BEFORE any rebuild. (Luke offered to
   start with par + these three cases. That is the agreed immediate next step pending his "go".)

---

## 5. KEY NUMBERS (for verification on resume)

**Farrow reconciliation (the convention trap):** raw PVC[10] = **1482**; pre-debut pedestal `MA.value(stripped)` at
SEASON_PROG 0.58 = **1371** (= PVC×0.925, the round-14 discount); at-draft NEW (PVC × mult 1.04) = **1535**;
production old prior(≤2020) = **1770**; production retrained prior(2003-2018) = **1627**.

**Six-player before/at-draft/today** (at-draft = PVC × pos-mult, no haircut [draft-day]; today = max(production
[2003-2018 prior], 0.85 × PVC × mult)):

| Player | pos · pick · g | PVC | posMult | at-draft (PVC×M) | TODAY |
|---|---|---|---|---|---|
| Harry Kyle | DEF · 14 · 3 | 1141 | 1.06 | 1215 | 1033 (floored) |
| Willem Duursma | MID · 1 · 13 | 3000 | 1.10 | 3291 | 4152 (production) |
| Zeke Uwland | DEF · 2 · 10 | 2496 | 1.03 | 2575 | 2188 (floored) |
| Jacob Farrow | DEF · 10 · 12 | 1482 | 1.04 | 1535 | 1627 (production) |
| Sam Cumming | MID · 7 · 7 | 1784 | 1.10 | 1961 | 1667 (floored) |
| Cooper Duff-Tytler | FWD-key · 4 · 11 | 2076 | 0.86 | 1775 | 1509 (floored) |

**Cumming sensitivity (hold avg 61.3, vary games)** — lvl_eff / band p10·p50·p90 / spread / production / hard-floor value:
```
 3g: lvl 13.1 | 49/ 80/104 sp54 | prod  831 | floored 1667
 7g: lvl 30.6 | 62/ 83/103 sp41 | prod  961 | floored 1667
12g: lvl 52.5 | 64/ 89/108 sp44 | prod 1379 | floored 1667
20g: lvl 61.3 | 67/ 94/110 sp43 | prod 1691 | 1691 (production)
```
Note the band RISES (p90 104→110) rather than narrowing as games confirm the level — a symptom of shrink-to-zero
(under par-centring the band should NARROW: p90 down, p10 up). **61-vs-21 @3g:** 61 → prod 831, band 49/80/104;
21 → prod 670, band 33/75/104 (note: same p90, different p10 — the band already differentiates downside; the hard
floor erases it). Cumming pre-season value ≈ 1962 (PVC 1784 × 1.10; the six-player table's 1961 uses the unrounded kernel multiplier ~1.099 — same number, display rounding).

**debut_factor curve (Dylan Patterson, pk5, PVC 1957)** — current vs proposed 10% deadband:
```
preseason: 1.000 / 1.000   |  ~r1: 0.995 / 1.000  |  ~r2: 0.990 / 1.000  |  r3: 0.985 / 0.997
~r7: 0.964 / 0.973  |  ~r14: 0.930 / 0.936  |  r24 never-debuted: 0.880 / 0.880
```

**Conservation:** prevalence-weighted LEVEL multiplier = **1.0000** at every pick (linear-on-PVC conserves exactly);
convex pricing breaks it +20–80%/pick (renormalise). Prevalence e.g. pk3: MID 0.51, KEY_FWD 0.18, RUC 0.04.

**LOCKED decisions (cont.25, still hold):** cohort cutoff = DRAFT 2003-2018 (Decision A); retrain prior on
2003-2018 = YES (Decision B; retrain effect modest ±1–3 pts, young high-pick DEFENDERS rise most).

---

## 6. OPEN DECISIONS / WHAT'S NOT SETTLED

- **THE PRODUCTION REDESIGN (par-centred) — agreed in SHAPE, not built.** Luke endorsed the skeleton (§4) and the
  softened axiom (§6 below). Next step = build par + mock the 3 cases. Awaiting "go" to start with par.
- **Softened founding axiom — Luke's call, made:** "pedigree lifts, never drags" is NO LONGER absolute. Poor
  performance for your pedigree SHOULD drag you; the constraint is only that non-players can't be MORE protected
  than poor-players, and β×PVC is the hard downside cap. (Document so a new chat doesn't "restore" the old axiom.)
- **Pre-debut / position-aligned PVC + 10% deadband (§3)** — agreed in shape; folds into the par build (don't ship
  as a separate mechanism). Sub-q: deadband season-end endpoint 12% vs shallower (lean keep 12%).
- **Multiplier flavour (cont.25 Decision C):** linear-on-PVC (auto-conserves, milder) vs convex-renormalised
  (sharper, matches the engine's convex pricing). Lean linear. Tied to §4 band-shape work now.
- **Ruck monotonicity (cont.25 Decision D / problem C):** still real, but absorb into par (a smoothed par curve
  over log(pick) is monotone by construction if smoothed right). Don't ship the standalone running-floor if par is
  going ahead.
- **β anchor for the floor cap:** β=0.85, and the pedestal (PVC × ~0.925–0.93 at the live season point, pick-dependent: Farrow pk10 = 0.925, Patterson pk5 = 0.930) vs raw PVC (~7–8% apart) — under the new frame the
  cap should use a clean, position-aware reference; pin when building.

---

## 7. SELF-AUDIT / GOTCHAS (things the next chat must NOT assume settled)

- **NO code committed this session.** Engine, `peak_model_v4.pkl`, `rl_app_data.json`, `rl_draft_engine.html`,
  conditional prior = identical to the cont.25 checkpoint. The release HTML predates ALL of this and is NOT final.
- **The cont.25 SESSION_SUMMARY's "β×PVC hard floor is the fix" is SUPERSEDED by §0 here.** A new chat that wires
  the hard floor without building par will reproduce the generic-everyone problem. Read §0.
- **`MA.value(stripped)` is season-dependent** (debut_factor uses SEASON_PROG). For draft-day numbers set
  `MA.SEASON_PROG = 0.0` before calling, or just use `PVC[pick] × mult` directly. (My §5 reconciliation error.)
- **Reproduce the cont.26 numbers:** run `forward_valuation/cont26_diagnostics.py` (added this session — carries the
  boilerplate; prints the break-even table, par-by-pick, 61-vs-21, the Cumming sensitivity, the debut_factor curve,
  the six-player table). The cont.25 numbers: `forward_valuation/cal_audit_diagnostics.py`.
- **Transcripts are PER-CONVERSATION** — a new chat will NOT have `/mnt/transcripts/`. Use `conversation_search`
  (terms that work: "Cumming par break-even", "debut_factor season-aware", "shrink toward zero level", "position
  aligned PVC", "Patterson optionality band"). Everything load-bearing is in THIS file.
- **`bootstrap.sh` installs pinned deps (scikit-learn==1.8.0 etc.) + recreates the rl_after/rl_build symlinks +
  runs the gate.** A fresh container needs nothing else. The prior is REBUILT each session via `rd.build()` (not
  pickled), deterministic under PYTHONHASHSEED=0.
- **Gate:** `verify_anchors.py` PASSES on the current checkpoint (11 anchors + calib 11/30/49/70/90 + 805 board).
  Anchors WILL move once par lands — re-anchor then; that drift is expected, not a regression.
- **Do the par rebuild as ONE combined change** (par + availability + band-shape + floor-cap together), validate
  all anchors + calibration + conservation, THEN rebuild `rl_app_data.json` + `rl_draft_engine.html`, re-tar,
  present. Don't paper one piece over another.
