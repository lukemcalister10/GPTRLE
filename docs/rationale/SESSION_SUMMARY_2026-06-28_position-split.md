# SESSION 2026-06-28 — DPP STRIP / POSITION SPLIT (pre-build)

State: PRE-BAKE. No board bake. cm_400 unchanged (md5 34faa8659cc8f19794f5cb9584fa19b2).
Code edits this session: dist_redesign.py (REPL_DROP -> uniform -3); verify_anchors.py (bootstrap-gate fix, below);
inert docstring run-commands tidied (FWD=4/OTHER=2 -> RL_REPL_DROP=3, cosmetic).

## BOOTSTRAP-GATE FIX (2026-06-28, post-handover correction)
The REPL_DROP -> uniform -3 edit broke verify_anchors.py and staled its canaries. Both FIXED:
- CRASH: verify_anchors.py printed rd.REPL_DROP_FWD/OTHER (deleted this session) -> AttributeError before any check.
  Now prints rd.REPL_DROP_PTS. (Swept the whole tree: this was the ONLY crash-causer; all other refs were inert
  docstring text, now also cleaned.)
- STALE CANARIES: the 14 EXPECT anchors were calibrated at the OLD per-group REPL (fwd-4/other-2); under uniform -3
  they all drifted by construction. REFRESHED to the -3 values (gate now 14/14 OK, deterministic across 2 runs):
  Daicos 7089, Bont 3163, Petracca 3087, McCarthy 2666, J.Cameron 1132, Gawn 2567, Madden 1508, Conway 1051,
  McAndrew 1719, Keane 2349, Bice 786, Uwland 1518, Walter 1087, Faull 757.
- Integrity confirmed independently of the anchors: Sharman proj_value(0)=310 (engine untouched), 805 players,
  CALIB GATE exact (11/30/49/70/90). Only the REPL-sensitive anchors moved; 13/14 the REPL direction, Petracca DOWN
  (DPP: bnow=GEN_FWD, _fut MID70/GFWD30 -> rides the forward bar, which rose -4->-3; vanishes at Stage-0 _fut strip).
- NOTE the verify_anchors issue was a REPL remnant, NOT a DPP one. DPP value-path is clean via _fut (decision 5);
  the Stage-0 strip + assert is what guarantees it.

## DECISIONS BANKED THIS SESSION
1. **REPL_DROP -> uniform -3** (DONE, code). dist_redesign.py: collapsed the per-group
   (fwd -4 / other -2) split to uniform -3. Legacy env RL_REPL_DROP_FWD/OTHER now INERT;
   reads RL_REPL_DROP (default 3). Flagged placeholder -> re-validate on clean base.
   Mechanic confirmed: REPL_DROP applies ONLY in _price_repl (the redesign's v_at_peak
   pricing); current board IS the redesign so every baked value uses REPL-3. Raw REPL
   (70.9) is read only by legacy value() + as the -3 base + (erroneously) my U28-D pole
   prototype (bare v_at_peak, not _price_repl -> those Kyle pole numbers need redoing).

2. **REPL markers (current/future) are NOT re-derived** (Luke's call, agreed). Reclassification
   RE-ROUTES each player to their current-position marker; it does not change the marker
   VALUES. Replacement is the marginal player; moving high-scoring dual-mids between buckets
   is a 2nd-order marginal-slot effect only. (Corrected my earlier "re-derive baselines".)

3. **No historical drafted-position scrape** (sensitivity test, /tmp/sens.py). Calibration
   pool n=1839; only 47 (2.6%) have drafted(p['pos']) != current(gfut). Per-position realized
   best-3 shift (drafted - current keying): MID +1 p90; GEN_DEF -3 p90 / -1.9 mean (most-moved);
   KEY_DEF/GEN_FWD/KEY_FWD within +/-3; RUC 0 movers in/out (the doc's thin-pool concern does
   NOT materialise). => p['pos']-as-drafted is good enough; scrape moot. NOTE: GEN_DEF re-key
   nudges it slightly MORE pessimistic, so the split does NOT fix the GEN_DEF under-projection;
   that remains a separate band/par young-end job.

4. **No GBM retrain** (verified, /tmp/retrain_q.py + /tmp/prod_q.py). _feat keys the one-hot on
   gfut (training rows + production band). Under split: production band -> current (=gfut, query
   moves only for re-keyed currents); pole -> drafted (changes for 47 converts, mean |delta| 4.2,
   max 10.0 - the intended effect). All queries land on position one-hots the GBM saw in training
   => in-distribution, not extrapolation. cm is ONE model serving both keyings: current-keyed is
   correct for production; the pole's drafted query is off <=3 pts (the sensitivity bound) from a
   true drafted cohort; retraining to drafted-keyed would just move that <=3 pt error onto the
   production side (net zero). Two-model split is the only fully-correct option, unjustified by
   <=3 pts. => DECIDED -- keep cm_400, no retrain; build is RE-KEY + RE-BAKE. "Decided" = do NOT
   re-litigate the retrain DECISION; it does NOT mean skip the Stage-2 on-manifold sanity check, which
   STILL RUNS to CONFIRM the no-retrain cost story (known-good real player predicts sane at level=par,
   ~replacement at level=0 -> the <=3pt bound holds). The check CONFIRMS the cost story; it does not reopen.

5. **DPP confusion - traced clean.** ALL dual-position blending funnels through ONE field, _fut.
   Five paths, every one falls back to single when _fut empty: gfut (else bnow), futblend (else
   [(bnow,1.0)]), proj_from_peak years-1+ blend, the JS mirror (_engine_block_v23.js:38, reads
   baked fut), and the spike-cap lift (rl_model.py:233, Serong dual premium). No blend path
   bypasses _fut. Strip _fut -> all five collapse to single-position, Python + JS. _double_count
   is phantom-record dedup (NOT DPP) - leave it. _pos_now/p['pos'] are the two clean fields; the
   bnow comment already documents the Dangerfield drafted-MID-plays-FWD design. Re-add DPP later =
   deliberate _fut repopulation on a clean base (isolated layer).

## THE SEQUENCE (gated, pre-bake until Stage 7)
0. Reclassify (drafted+current per edited roster) + strip _fut + ASSERT (_fut empty all 805,
   one drafted + one current each, gfut==current). REPL-3 done.
1. P-freeze reconciliation [OPEN -- outcome NOT predetermined]. The open question is TEMPORAL, not
   field-identity: were the 34 drafted edits applied to the value P was frozen on, or does frozen-P
   PREDATE them? Check frozen-P vs corrected-drafted on the 34. Agree everywhere -> proceed. If frozen-P
   != corrected-drafted on ANY of the 34 -> STOP, do NOT auto-resolve; surface for Luke's ruling between
   (a) re-freeze P onto the correction, or (b) drafted accepts the divergence. Luke's call, not the build's.
2. Backward re-key to DRAFTED (pole _adraft_band, realized distributions, pick-curve, tails) via
   p['pos']. Existing cm_400, no retrain -- but RUN the on-manifold sanity check here (known-good real
   player sane at level=par, ~replacement at level=0) to CONFIRM the no-retrain cost story, not reopen it.
3. Forward re-key to CURRENT (REPL, cond_prior_band). Closes U28-MULTIPOS. Verify Duff-Tytler
   sensible + Holmes not broken.
4. Re-derive par/bands/pick-curve on single-position keying. Markers stay.
5. PRE-BAKE diagnostics: cohort book on clean base (GEN_FWD de-pollute, GEN_DEF landing),
   board-delta vs 605,719 gated on real converts (Dangerfield/Blakey/Sheezel), update guard
   held-equal set {games,tenure,age,drafted_pos,current_pos,pick}.
6. Review GEN_DEF: does split close young-end gap or is targeted band work still needed.
7. GATED BAKE (explicit go): board + rl_app_data.json + HTML + JS parity (single-position).
8. THEN U28-D: refresh anchors, convert-boundary test case, REPL-3-consistent pole pricing.

## OPEN / HELD
- U28-MULTIPOS: closes at Stage 3 (mark closed then, not before).
- U28-D: fully parked downstream of the bake. My earlier pole-prototype numbers priced on raw
  REPL (bare v_at_peak) vs prod on REPL-3 - inconsistent, redo when U28-D resumes.
- GEN_DEF young-end under-projection: separate band job, likely survives the split.
- DPP re-add: deferred to after the clean base.
