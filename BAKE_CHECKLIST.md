# BAKE_CHECKLIST — the bake ritual (PROCESS_CHANGES §8) — binding at every bake
_Created 2026-07-02 under DIRECTIVE 1. A bake moves the BAKED marker; nothing bakes without Luke's explicit go.
Steps run IN ORDER; any step failing stops the ritual (subject to the SHIP_GATES failure-triage rule for [DC] gates)._

## §REPORTING — THE THREE REPORTING RULES (Luke's word: BINDING, D10 03/07/2026 — bind ALL sessions, not just bakes)
1. **THREE COLUMNS.** Every gates/board output reports THREE COLUMNS: CONTROL (canonical) · PREVIOUS
   (the last verified candidate) · CURRENT (the state being measured), with deltas explicit. The
   CONTROL/PREVIOUS pointers live in `data/report_states.json` (snapshots in `data/gates_snapshots/`,
   pinned matrices in `data/`); update the pointers when the candidate line advances — never delete
   the old snapshots.
2. **LOUD STATE LABEL.** Every board/report carries a LOUD state label (CONTROL / CANDIDATE vX @ hash /
   PROTOTYPE-name) in its header; **no unlabelled player value anywhere Luke-facing.** An unregistered
   head prints `PROTOTYPE/UNREGISTERED @ <md5> — NOT AN ENDORSED STATE`.
3. **BINDING ON EVERY FUTURE SESSION.** These rules are permanent process (wired in
   `ship_gates_check.py` + the book renderer); a session that emits a Luke-facing value without state
   label + three columns has violated a Luke ruling. Origin: Luke's D10 directive, 2026-07-03 —
   confirmed cross-state confusion (DIAG-A: three engines' boards read as one timeline) is the failure
   class these rules close.

## 0. SCOPE PIN
- [ ] Name the exact candidate: engine head md5-8, store md5-8, band md5-8, branch/commit. The ritual applies to
      that byte-identity only — any file change after step 1 restarts the ritual.

## 1. COLD EXTERNAL AUDIT (scoped to the exact head)
- [ ] A fresh session/agent (no shared context with the build session) restores the tarball/branch, runs
      `setup_env.sh` + `bootstrap.sh` + `verify_restore.sh`, and reads the diff being baked against the last
      BAKED head. It reports: unexplained diffs, engine/store edits outside the declared scope, landmine
      violations (EXACT-name matching, xlsx stems, backup-before-edit). Verdict in writing, by filename+md5.

## 2. LUKE READ-PASS (ground truth)
- [ ] Luke reviews the fixed named panel (run_panel.sh players + the directive's named players) at the candidate
      head. His reads are GROUND TRUTH: a failed read = a red gate (triage below). Explicit go recorded verbatim.

## 3. SHIP GATES — FULL RUN (mandatory)
- [ ] `python3 ship_gates_check.py` at the candidate head; report file + md5 recorded.
- [ ] Any FAIL → failure triage per SHIP_GATES PROCESS before anything blocks: ENGINE-caused → blocks the bake;
      DATA-caused → escalate to Luke for uphold-or-amend (logged in CHANGELOG); AMBIGUOUS → decompose first.
      [DC]-tagged gates get the triage question first by default.

## 4. BYTE-EXACT VALUES IN THE BAKE ENVIRONMENT
- [ ] `setup_env.sh` gate PASSes (pins: Python 3.12.3 · numpy 2.4.4 · scipy 1.17.1 · sklearn 1.8.0 · openpyxl 3.1.5).
- [ ] Expected values reproduce byte-exact under the pins: Maric ev(2026)=1409, Langdon ev(2026)=593 (or the
      candidate's recorded successors), PANEL_EXPECTED 10/10. Off-pin numbers are not acceptance evidence.

## 5. DOC GATE AT THE BAKE COMMIT
- [ ] `python3 doc_lint.py` = 0 FAIL at the exact commit being baked. Five-state statuses updated: the baked
      claims move to BAKED with Luke's go quoted; CHANGELOG lineage line appended (old head → new BAKED head).

## 6. FULL RE-VERIFY (same session as the cut — never ship then flag "not re-run")
- [ ] `verify_restore.sh` 9/9 PASS (md5 axes + named players + harnesses).
- [ ] `run_panel.sh` 10/10.
- [ ] Named-player spot set re-priced and attached for Luke.
- [ ] Walk-forward book regenerated (s4 matrix + render) and B1 growth-law gate re-checked on the fresh matrix.
- [ ] JS parity: regenerated `rl_app_data.json` byte-agrees with the shipped board (ship_gates_check B4).
- [ ] Offline restore-verify of the new tarball BEFORE it leaves the container; bundle md5 + manifest recorded
      in CHECKPOINT_MANIFEST.md.

## 7. PUSH + CONFIRM
- [ ] Commit = checkpoint; push the bake commit + tarball identity; confirm to Luke with the dual state-stamp
      (engine head/store · main commit) and the ship-gates verdict line. BAKED marker moves only after his ack.
