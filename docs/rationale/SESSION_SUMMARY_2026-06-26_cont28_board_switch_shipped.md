# cont.28 — BOARD SWITCH (Option 1: re-bake static) — SHIPPED at 400 trees

## Decision (Luke)
Option 1: re-bake the board static through the router (NOT the Option-2 live-dials hybrid). Rationale: the live REPL/lens
dials never lived in the shipped `rl_after` board (it was already baked-static; the dials only ran in the older closed-form
dev build), so Option 2 would be a speculative migration, not a regression-fix. Hybrid parked as a cheap additive upgrade.
Bake at 400 trees (full fidelity), decided AFTER measuring 200-vs-400 (not 200-by-default, not 400-blind).

## Scoping findings (all verified by reading the chain, not assumed)
1. **Switch point is `wire_redesign.py`, not `rl_export.py`.** `rl_export.py`'s `val=g['val']` is inert for board values;
   `wire_redesign.wire()` sets `p['_v']` (+ the four shifts), and the export reads them.
2. **Two coupled changes, both required** (a naive 1-liner silently breaks pre-debut):
   - cm source `rd.build()` (default feature) → `PR.retrain()` (par-centred `cp._lvl_eff=lvl_par`). Validated pre-debut
     REQUIRES the par-centred cm (pre-debut runs `rval→rband→band5=cond_prior_band`, i.e. THROUGH the GBM).
   - value fn `rd.redesign_value` → `TR.production_value` (router: pre-debut→par-path, established→redesign_value verbatim).
3. **Pre-debut is GBM-dependent ⇒ tree-count-sensitive** (the milestone's "pre-debut byte-exact at 400" premise was WRONG;
   verified by retraining at 250: MID pk1 2596→2515). So 400 shifts BOTH pre-debut and established off the 200 mock.
4. Year-shifts (`vP1/vP2/vM1/vM2`) are FLAT placeholders (==v, 805/805); `_rl_parity.js` is tautological on a baked board
   (recompute sets `p.val:=p.v`), so it does not false-alarm. Confirmed both empirically.
5. `p['_bands']` (cond_prior_band peak + at-draft pole) captured as a NAMED intermediate, computed-not-serialized, so a
   future Option-1→2 hybrid is purely additive (serialize in `player_rec` + ~40-line JS pricing layer).

## 200-vs-400 measurement (drove the bake decision)
SHIPPED 400 blend = **2086/1473/1126/635/396** (grad 1.61x; unrounded pk5=1472.5, pk40=395.5 — .5 rounding seam).
200 mock = 2176/1505/1131/647/392 (SUPERSEDED). Shift = genuine accuracy: concentrated at pk1, largest in THIN positions
(KEY_DEF pk1 −11.7%, GEN_FWD −9.8%, GEN_DEF −7.4%; MID −3.3%, KEY_FWD −1.4%), washing out by pk10–40. Clean refinement,
not erratic. Judgment checks HELD: pk1-8 shape preserved (no threshold crossed); KEY_FWD undebuted pk5 KPF 1143→1140
(~53% of a median gun, dominance intact). Established at 400 ≈ live board (±1.5%, mostly ~0%) — so 400 keeps established
stable (200 would have DE-fidelitied it ~3%, since the live board is already 400-tree).

## Execution + gates
- `wire_redesign.py` rewritten (par-centred cm cached/retrain + router + `_capture_bands`). Backups: `*.pre_cont27switch`.
- Baked via `rl_export.py` @ RL_PRIOR_TREES=400 PAR_RAMPS=22 (cached `cm_400.pkl`, 76s) → `rl_app_data.json`; then
  `rl_build_html.py` → `rl_draft_engine.html` (+ /mnt/user-data/outputs/). Board total 603,839; n=805; top: Sheezel 7264,
  Daicos 6942, Jackson 6128, Xerri 5951, Wanganeen-Milera 5408.
- **Two-part parity gate PASSED at 400** (same fidelity, no tree-shift caveat): (a) pre-debut router==per_pos_value Δ=0;
  (b) established router==redesign_value Δ=0. Base gate (verify_anchors) clean at 400. JS parity `_rl_parity.js` 0/805 max 0.
- Baked anchors == validated probe (Daicos 6942, Bonte 3096, Petracca 3154, Gulden 4470, Gawn 2521, Cameron 1196,
  Sheezel 7264, Walsh 2688).

## Housekeeping
- RUC docstring fix: stale "2157" removed; canonical RUC pk1 = 2155.54 (→%.0f 2156) recorded in `pickcurve_build.py` +
  milestone. The historical 2155/2156/2157 are the SAME number under different rounding/snapshots.

## NEXT (deferred queue, unchanged order)
Season-aware pre-debut haircut (the sequenced next piece) · best-3 partial-sample shrinkage · aging quality-interaction
(the ONE backlog item that would cross into JS under a future hybrid) · PVC→realized-level-floor migration · RUC per-pos
reliability. Option-2 hybrid parked (additive). Build the hybrid AFTER the aging work so JS mirrors settled logic once.
