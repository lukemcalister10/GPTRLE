# D8 ASK 3 — SWEEP HYGIENE (one-liners first; support beneath)
_2026-07-03 · canonical head `8aed420a` store `644d1254` · measured fresh this session (one rl_model-layer
read-only load; no engine mutation anywhere)._

**(i) The 2 double-counted sweep entries:** `Mark Keane (IRE credit)|2019|None` and `Lachlan McAndrew (MSD
credit)|2021|12` — DELIBERATE `_double_count` credit phantoms (rl_model.py:419, Luke cont.12: they boost
their draft pools BACKWARD only; the forward re-entry record is the real player), keyed distinctly from the
real records by player-string + cohort + pick, so the standing name-collision rule is honoured — and
separately verified on its canonical case: `Max King|2018|4` (St Kilda) and `Maxwell King|2025|49` (Sydney)
both survive as distinct keys in the 807 sweep, never merged. DECLARED, no fix. CONSEQUENCE FOR ASK 2
(reported there in full): the fire-population "McAndrew 99→1408" row IS the phantom; the real McAndrew was
re-entered at year 2024 (tenure 2 < onset), never hits the cap, and prices 1062 at head — fix-inert.

**(ii) The 59 "stale" sweep entries: DECLARED, NOT PRUNED — and the D7 label CORRECTED.** They are not
stale store rows: identity-level they are the 59 PRE-DEBUT 2024+ draftees' original store rows (Smillie et
al.), which the export deliberately supersedes with `_unplayed` copies carrying IDENTICAL keys and identical
values (rl_model.py:413-425; the originals fail `active()`'s played test, the copies pass by flag). At KEY
level, measured fresh: sweep 807 = board 805 + exactly the 2 credit phantoms (sweep-only keys = 2,
export-only keys = 0). D7 ASK-5i's set arithmetic (746+61 / 746+59) was identity-level and remains correct;
its "stale never-played" wording was a mislabel. EFFECT on the 0/807 M3 inertness check: NIL — the sweep
basis is unchanged, keys are unique, and every board-priced player is priced identically in the sweep.
EFFECT on gate denominators: NIL — the matrix/board populations already exclude `_double_count`, and B5's
ND-listed denominator contains neither phantoms nor pre-debut originals.

**(iii) verify_restore mixed-pair caveat: CLOSED WITH A FIX (instrument-side; engine untouched).** Root
cause pinned to source: `wire_redesign.py:14` hardcodes `_FV='/home/claude/rl_workspace/forward_valuation'`
(and `par_redesign.py:14` inserts a hardcoded sys.path head), so ANY tree's engine loads the WORKSPACE's
cp/PR chain — verify_restore's named-player axes therefore run repo-engine × workspace-forward_valuation
whenever the trees diverge. FIX: a PAIR-GUARD added to `verify_restore.sh` — md5-compares every
`engine/forward_valuation/*.py` against the hardcoded `_FV` target and FAILS loudly on any mismatch (NOTE
line when the workspace is absent: imports then fail loudly rather than mix). Verified live this session:
restore-verify now 10 PASS / 0 FAIL with the guard green (all 8 files repo==workspace today), panel 10/10.
RESIDUAL (one-line risk statement): the root fix — parameterizing `_FV` by tree root — is an ENGINE edit
and stays a candidate-branch item; until then any harness run outside the standard layout inherits the
hardcode, now loudly guarded in the standard ritual. (The D8 scratch deployment declared this pairing
explicitly and ran clean-paired by the same md5 test.)
