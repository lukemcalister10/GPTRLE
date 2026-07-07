# Stale-boot hardening — Guard 5 (boot-store assertion) — 2026-07-05

Tooling/guard hardening only. **No engine, store, board, or band change** (store `e1b4d8bf`,
engine `efea88e5`, rl_model `121a45d0`, band `34faa865`, board `7d1eeef8` — all byte-identical).
Work off `baked-v2.5-2026-07-05` (`e1d8d78`); store asserted `e1b4d8bf` at ground.

## The gap
The four data guards (`single_source.py`) resolve `HERE = dirname(__file__)`, so they validate
whichever **directory** they are imported from. Run from the persistent workspace copy
`/home/claude/rl_workspace/rl_after`, they validate the workspace against **itself** — a
stale-but-self-consistent workspace passes all four. They protect the data *model*, not which
*directory* a script reads. That is the hole that let builds boot on the baked-v2.4 store
`644d1254` (sitting in the workspace) while the real candidate `e1b4d8bf` lived in the checkout.

## STEP 1 — stale-boot map (file:line)
- **Class A (reads workspace by hardcoded path, no hash check):**
  - `run_panel.sh:3,5` — `cd /home/claude/rl_workspace/rl_after`; PYTHONPATH workspace; no store assertion.
  - `ship_gates_check.py:49,52,54` — `RA='/home/claude/rl_workspace/rl_after'`; sys.path + chdir workspace.
  - `ship_gates_check.py:58` — `STORE` computed + printed (`:494,:533`) but **never asserted**.
- **Class B (reads repo but delegates to a workspace-reader):**
  - `verify_restore.sh:46` — asserts repo md5s (`:12-15`) then runs `run_panel.sh`, which reads the workspace.
  - `verify_restore.sh:12-15` — four expected md5s hardcoded per-bake in this one script (only pin, not reusable).
- **Class C (path-only resolution, no HALT):**
  - `bootstrap.sh:29-38` — seeds workspace from repo (good) but only **echoes** md5s ("expect 34faa865"); never fails.
  - `single_source.py:20`, `one_source_selftest.py:31` — `HERE=dirname(__file__)`; validate the workspace vs itself.

## The fix
- **`boot_guard.py` (Guard 5)** — repo-anchored (RL_REPO / CLAUDE_PROJECT_DIR / own dir, never workspace).
  Asserts the store a script is about to read == `data/expected_boot.json` == the checked-out repo store;
  optional engine-head + band parity. HALTs (non-zero) with a loud message; never warns.
- **`data/expected_boot.json`** — the ONE pinned manifest of expected md5s (the manual three-assertion check,
  automated). `verify_restore.sh`, `bootstrap.sh`, `run_panel.sh`, `ship_gates_check.py`, `one_source_selftest.py`
  all read it instead of carrying their own hex.
- Guard wired as the mandatory first line of `run_panel.sh`, `bootstrap.sh`, `ship_gates_check.py`
  (pre-flight, before engine load), and `one_source_selftest.py` (as GUARD 5 in the guard block);
  `verify_restore.sh` sources its expected md5s from the manifest.
- Workspace **kept** (engine hardcoded absolute imports + build-write isolation) but re-seeded from the
  checkout and hash-asserted — not deleted. See SINGLE_SOURCE_INVARIANT.md "Why the workspace stays".

## STEP 3 — proof
### Negative (stale baked-v2.4 store `644d1254` staged into the workspace)
```
run_panel.sh        -> HALT  (exit 1)  "md5 644d1254 != expected e1b4d8bf ... STALE BOOT ... re-run bootstrap.sh"
ship_gates_check.py -> HALT  (exit 1)  same message, on entry, before the engine loads
one_source_selftest -> GUARD 5 FAIL    (fails the self-test)
```
No engine load, no ghost values — the build stops on line one.

### Positive (correct candidate store `e1b4d8bf`)
```
boot_guard CLI      -> Guard 5 PASS  store e1b4d8bf == pinned e1b4d8bf (baked-v2.5-2026-07-05)
bootstrap.sh        -> Guard 5 PASS ; engine efea88e5 / cm_400 34faa865 / store e1b4d8bf
run_panel.sh        -> PASS 10/10
verify_restore.sh   -> 11 PASS / 0 FAIL  (head efea88e5, store e1b4d8bf, rl_model 121a45d0, band 34faa865,
                       Maric 1271, Langdon 567, cp-pair guard clean, panel 10/10)
ship_gates_check.py -> every CURRENT-column verdict identical to the committed baked report
                       (A2/A3/A12 the standing Luke-ruled reds, B5 FEATURE, B2 PASS after _gate1_wf,
                       B4 7d1eeef8==7d1eeef8); VERDICT FAIL=3 FEATURE=1 PASS=17 PENDING=4 STRUCK=1.
                       Key numbers byte-identical (A1 4110 vs 1984; A2 1355 vs 1485; B1 AVG(peak)=143;
                       B5 52 saves +1296; B6 ramp [1260,1530,1825,2474,3072,...]).
one_source_selftest -> GUARD 5 PASS after re-seed.
```

## Frozen-gate flag (A7 precedent) — OWNER RULING RECORDED
`ship_gates_check.py` is the FROZEN acceptance suite (ref `764a0d91`). The change is a **pre-flight
addition only** — no gate assertion, threshold, or value is touched; on the pinned store the board is
byte-identical. It changes behaviour **only** in the previously-broken case (a stale boot now HALTs
instead of emitting ghost values). It was flagged for owner sign-off per the A7 precedent.

**Owner ruling 2026-07-05 (Luke, in writing, verbatim):** "the Guard 5 pre-flight is a safety addition,
not a frozen-gate amendment; apply and keep it." Disposition: the frozen suite `764a0d91` is **unamended**;
Guard 5 stays. No further sign-off outstanding.
