# THE SINGLE-SOURCE INVARIANT — read this before touching data or code
### Binding on every build and every supervisor. This is not guidance; it is the acceptance bar. If a change would violate it, STOP.

## THE ONE RULE (plain)
There is **exactly one** authored source of truth: `engine/rl_after/rl_model_data.json`.
- **Never create a second copy of it.** No `.bak`, no `.stageN`, no `_v2`, no "working copy."
- **Every other data file is DERIVED** — generated from the source, read-only, and disposable. The board, the book, the matrices: all regenerated, never hand-edited.
- **If you need different data, change the source.** Not a copy. The source.
- **Retire a feature → strip its fields from the source and code.** Delete, don't disable. A copy earns its existence only as a generated, stamped, read-only artifact — never a hand-edit.

Why this exists: every failure in this project's history — the phantom-repo scare, the `.pre_stage0` revert, the Kako wipe, the stale-boot day — was the same thing: a stale copy read as if current, or an edit made to a derived copy the next rebuild overwrote. Rules in prose didn't stop it. The guards below do, because they make a stale read **fail the build loudly** instead of sitting silent.

## THE FIVE GUARDS (mechanical — each must FAIL/HALT the build, never warn)
1. **One writable source; derived files read-only + source-stamped.** The generator is the only writer of derived files; it marks them read-only and writes the source md5 into each. A hand-edit to a derived file does not survive the next rebuild — so forking earns nothing.
2. **Source-hash assertion on startup.** Every derived artifact carries the md5 of the source it was built from. Every build's first step asserts that stamp == current source md5. Mismatch → HALT.
3. **Lookalike tripwire in the self-test.** The self-test scans the source directory and FAILS if more than one file matches the source pattern (`rl_model_data*.json`). A second lookalike becomes a red test the next build can't pass, the moment it's created.
4. **Correction-sticks canary (permanent).** Write a throwaway edit to the source, run a full rebuild, assert it survives to board + book. Kept in the suite forever: "did a copy or a revert path sneak back?" is answered automatically every build, not discovered when a player's data vanishes again.
5. **Boot-store assertion (added 2026-07-06, `boot_guard.py` + `data/expected_boot.json`).** The other four guards validate whichever directory they run from — so a stale *workspace* (v2.4 data agreeing with v2.4 data) passes them all while the board is wrong. Guard 5 pins the expected store in one manifest and asserts, on ENTRY of every gate/bake/panel/self-test script (before the engine loads), that the store being read matches the pinned source md5. A build that boots on the wrong store HALTS on line one instead of running five confused turns deep. This closes the *base* half of the divergence problem; guards 1-4 close the *data* half.

## THE DISCIPLINE THAT MAKES THEM REAL
- Each guard is wired to **STOP the build**, never to log a warning. A tripwire nobody reads is worse than nothing.
- The pipeline is **not "done" until all five pass** from a fresh bootstrap.
- This block sits at the top of the kickoff every build and supervisor reads (KICKOFF v8 §0). It cannot be satisfied by intention — only by the guards going green.
- **Navigate by branch name + git SHA, never a store md5.** A store hash is a content check, not a place to stand. (Confusing the two cost real time on 2026-07-05.)
