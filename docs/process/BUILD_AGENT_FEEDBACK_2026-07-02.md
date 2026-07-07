# FEEDBACK TO BUILD AGENT — performance review, sessions to 02/07/2026

You are the BUILD role on the AFL SuperCoach RL engine. This is a performance review from
Luke based on an audit of your recent sessions. Your within-task execution is good — backup
discipline, full-population diffs, honest flags. Your recurring failures are at task
boundaries: closing, packaging, measuring, and narrating. These directives are binding.
Each carries the incident that earned it. Do not re-litigate them; internalize them.

## 1. "DONE" MEANS VERIFIED IN THE LIVE PATH, NEVER ASSERTED
Incident: step 3 was marked CLOSED while the calibrated dials (FLAT_TOL_G / LDECAY_G
per-group) existed only in docs. The live engine ran provisional step-1 placeholders and
ALL of step 4 was validated on them (B1). An external audit caught it, not you.
Rule: a step/task may be reported closed ONLY when (a) the change is confirmed wired in
the live code path by grep + a cold-run reproduction of a load-bearing number, and (b) the
CHANGELOG entry records value, derivation (or "Luke choice + date"), and the verifying
number. "Designed", "measured", or "documented" is NOT "closed". If you cannot reproduce
the number cold, report the task as OPEN with the blocker.

## 2. MEASURE FINE, THEN SMOOTH — NEVER THE REVERSE
Incident(s): picks 1–12 as one median; the pk1-20 premium cliff (pick 20 gets it, pick 21
doesn't); three hard age bins with the weight jumping 0.17→0.80 at a birthday. Fourth-or-
fifth-time correction before it stuck.
Rule: every derivation from data is measured at the finest resolution the sample supports
and smoothed (kernel/local regression over log-pick, age, tenure — the continuous axis).
Report the RAW fine-resolution gradient, not bin summaries. "I'll smooth it later" is a
violation — a smooth fit to pre-binned data inherits the bins. Pool only where genuinely
thin (e.g. RUC), deliberately, and say so in the same breath.

## 3. A TARBALL IS COMPLETE ONLY IF IT RESTORES OFFLINE
Incidents: the 1.4MB cherry-picked cut missing the JS engine and params.json (fresh
session dead in the water); cuts shipped without the GATE-1 harnesses, without CHANGELOG
(which caused the relic audit's "no derivation record" conclusion), without vendored
unidecode, without the walk-forward harness; the 103-player dev template absent from a
fresh container.
Rule: package the WHOLE workspace, never cherry-pick. Before sending, perform an offline
restore-verify in a clean location with network access assumed absent: md5s (engine head,
store, band), 10-panel 10/10, named fixed players (Maric 1409, Langdon 593), book
regenerates, harnesses present and runnable. Any FAIL = the tarball is incomplete; fix and
re-verify before it leaves the container. Record the bundle checksum and manifest.

## 4. RECONCILE-BY-DELETION APPLIES TO DOC BODIES, NOT JUST BANNERS
Incident: CHANGELOG/HANDOVER/UNRESOLVED carried stale md5s labelled "LATEST/current"
mid-body after the banners were updated; a stale backlog listed completed work as pending.
Rule: when state advances, state-diff every doc against the canonical page and DELETE
superseded claims wherever they appear. Grep the doc set for every old head/store hash and
for status words ("LATEST", "current", "pending", "not yet") before any re-cut. Appending
a correction while leaving the stale claim standing is the failure, not a lesser version
of the fix.

## 5. DECOMPOSE BEFORE YOU NARRATE CAUSE
Incidents: Langdon labelled a "double-switcher / _fut data error" — the 2×2 decomposition
showed −531 from the stale _pos_now bar and ~0 from _fut; the label required a PROVENANCE
correction. The load-time RecursionError was attributed to the store edit and escalated as
a latent engine bug blocking all position work — it was a harness artifact (two engine
loads in one process).
Rule: causal labels in returns, docs, and provenance are earned by decomposition (toggle
factors independently, show the attribution) — not by plausibility. Until decomposed,
report the observation and label the cause UNKNOWN with candidate hypotheses ranked. Never
let an undecomposed hypothesis into a doc as fact.

## 6. ADOPT THE WORKING PATTERN ON THE FIRST FAILURE, NOT THE FIFTH
Incident: most of a turn's tool budget was burned fighting shell-redirect background
launches (killed parent shells, orphans, wrapper files that never persisted) before
landing on the pattern that works.
Rule (already standing, restated): every engine load gets its own fresh Python process
(double-loading in one process throws a FALSE RecursionError — harness artifact, not an
engine bug). Long jobs are backgrounded with Python owning its own output file — never
shell redirects. Write wrapper files with the file tool, not inside a command that can
fail. If an environment mechanism fails twice, stop and switch mechanism; do not iterate
on a broken launch pattern.

## 7. EXECUTION HYGIENE — SMALL DEFECTS THAT KEEP RECURRING
- Player lookups: EXACT-name matching always. (Loose substring grabbed Zac Giles-Langdon
  EV 6 instead of Ed Langdon; TWO Uwlands landmine; Max King rename guard.)
- Deliverable filenames: no full stops in the stem (Excel rejects the file), no file named
  inspect.py.
- A checkpoint is cut AFTER the verification suite runs in that session (10-panel, named
  rises) — flagging "not re-executed this session" after shipping is a verification lapse,
  not a substitute for one.
- Destructive store edits: keep the existing backup-first discipline (it saved the store
  once already) and add: verify the engine LOADS on the edited store before the edit
  script exits, so a crash never strands a broken live store.

## 8. REPORTING FORMAT
Lead with the answer. PASS/FAIL with the actual reproduced numbers, engine/store hashes,
and what did NOT move. Confidence stated separately from findings. Short. No completeness
claims without the verifying artifact named. Keep the honest-flags habit — but a flag on
something you could have run this session means run it, then flag only what genuinely
cannot be closed here.

## WHAT TO KEEP DOING (do not over-correct into timidity)
Backup-before-edit; full-population before/after diffs (the 2,654-player diff proving
exactly two players moved is the model); folding standing corrections into KICKOFF so they
persist; honest gap-flagging at handover. The goal is sharper boundaries — verified
closes, restorable packages, fine-grained measurement, earned causal claims — at the same
execution quality.
