# DIRECTIVE 6 — session notes — Gothard decomposition + floor-as-pricing prototype + annotated offender table
_2026-07-02 · BUILD · branch `claude/gothard-floor-pricing-1m9jdj` · post-merge main `b2671355` (PR #8 merged as STEP 0)._
_State: canonical head `8aed420a` / store `644d1254` / band `34faa865` UNTOUCHED (housekeeping doc commits only) · candidate `fb39d88a` measured READ-ONLY, zero commits · SHIP_GATES.md UNTOUCHED (B5 amendment text PREPARED only) · clamp prototype on this scratch branch only · 4 engine loads, all sequential · workspace restored + md5-verified (8aed420a / 346cffbb) after the variant block._

## ASK 1 — GOTHARD DECOMPOSITION (PASS; `d6_ask1_gothard_decomposition.md`)
- 1a: store AGREES with Luke's ground truth on every field (13g @ 70.2 · pick 12 · 2023 ND · GFWD, no switch · yr3). The hidden structural fact: 2026 is his ONLY scoring season.
- 1b: **the staleness cap owns the entire gap.** Uncapped, every channel prices him ~1790 (band 1815; REPL netting fair at 70.9 vs his 70.2; pole +12.6 already muted by tenure-fade × exposure-gate; iso −2%). Then `ev()`'s stalled-non-producer branch (`el>=3 AND ns<=1`) overwrites with 0.25×draftval = 317.25. The cap counts qualifying seasons without a recency or quality term — built for "played once long ago, nothing since" (Hardeman 2g@25.5, Collard 0g are its correct targets in the same branch), it cannot see that Gothard's one season is the current near-replacement breakout. Counterfactuals: tenure −1yr → 1480; one extra 2025 6g season → 1938; cap off → 1790. Every yr-3 offender at ratio ≈0.250 is this cap; the yr-3 offender block is the cap sitting 0.03 under the signed 0.28 floor.
- 1c: **317 at all four states** (head / candidate / candidate−cB / head+M3). cB is already 0 for his profile (effs=13/17<1); M3 is identity for him (g26=13 ≥ 11). The floor patches him to 355; the FIX is a recency/quality term in the staleness cap — candidate-branch item, needs Luke's word.

## ASK 2 — FLOOR-AS-PRICING-FEATURE (PASS; `d6_ask2_floor_saves.md`, prototype `engine/prototypes/floor_pricing_clamp.py` `66fbf0f6`)
- ev_final = max(ev, floor_yrs×draftval), ND-only, both tail variants wired in one prototype. Variant A (flat .05): **51 saves, +1287** — saves Haynes (+4) and Hopper (+48). Variant B (D5 kernel tail): **27 saves, +394** — dev-window saves identical to A (Gothard +38, Ugle-Hagan +57, Pedlar +2); **Haynes/Hopper NOT saved** (evs sit above the derived floors) — Luke's utility-value read is the argument FOR A's tail (or a listed exception channel).
- Pure lower bound VERIFIED on the wired run (n=807): 0 lowered, 0 non-ND moved; byte-identical count 757 (A) / 782 (B); saves-vs-lift deltas are integer rounding.
- new-B1 under the clamp: **PASS, peak N=4 @ 160.2** (vs 160.5 unclamped); IDENTICAL for A and B by construction (B1 window ends at d7; variants diverge at d8+). Delist-fingerprint cells excluded per the floor's own rule; no-skip sensitivity also passes (155.5).
- 2d: B5 amendment text PREPARED in the artifact (gate retired as alarm → pricing feature + mandatory saves-table print), Luke's ruling quoted as authorization. NOT committed to SHIP_GATES.md.

## ASK 3 — REGISTER-ANNOTATED OFFENDER TABLE (PASS; `d6_ask3_annotated_offenders.md`)
- Head-51 + 31 joiners re-verified FRESH (82−51, 0 leavers — matches D5 exactly). Added columns: REGISTER (4 joiners LTI: **Gibcus, Clarke, Motlop, McInnes** — LTI-haircut candidates, not floor-saves; head-51 all clear), LUKE'S READ (seeded verbatim), 2026 games.
- **Store as-of GAP flagged:** the store has NO explicit as-of timestamp field. Provenance-derived cut printed instead (R14/24, SEASON_PROG 0.58, captured 2026-07-01). Recommend adding a store metadata stamp at the next store touch.

## ASK 4 — D5 CONFIRMATIONS (PASS; `d6_ask4_confirmations.md`)
(i) A2@candidate−cB **0.822** (1358/1653) — re-measured fresh, supervisor's ~0.82 CONFIRMED. (ii) new-B1 peak @candidate−cB **N=4 156.6** (D5 committed cite; matrix not re-built). (iii) v7 residual movers: **NIL** — `_v7` is exactly cB (bb[3]/bb[4]) + asc (bb[5]); pivot and bb[0..2] untouched; all 31 joiners resolve to asc/cB/M2/joint.

## ASK 5 — HOUSEKEEPING (PASS)
- Effort rule registered: `docs/process/PROCESS_CHANGES_2026-07-02.md` §11 — amendment VERBATIM; the "original" effort rule was never registered in-repo (lived in the directive protocol), stated as-practiced with a supervisor-correction flag.
- CHANGELOG D6 entry appended; doc_lint 0 FAIL / 0 WARN.

## Hypothesis register (D6)
- h-Gothard-mispricing-is-engine-channel-interaction: **RESOLVED — it is ONE channel, the staleness cap** (not tenure×exposure×netting×position interaction; those all price him correctly). New hypothesis REGISTERED: h-staleness-cap-lacks-recency-term (the yr-3 0.250 block is a cap artifact; Gothard its only producing victim) — fix design awaits Luke's word.
- h-floor-clamp-breaks-B1-shape: **REFUTED** (PASS 160.2, both variants, by-construction identical).
- h-tail-variant-choice-matters-for-dev-window: **REFUTED** (A and B identical through yr7; the choice only prices the yr8+ veterans — and the Haynes/Hopper utility reads are the A-side evidence).

## Burn / process
Engine loads: 4 (head decomp+sweep · candidate · cB-off · clamp verify), all sequential; no matrix rebuilds (B1 re-prints were matrix post-processing; the one cited minus-cB matrix number is D5's committed same-state measurement). Estimate ~2.0h posted at session start; ran under it. Canonical restored + md5-verified after the variant block; panel re-run at session end (see PR).
