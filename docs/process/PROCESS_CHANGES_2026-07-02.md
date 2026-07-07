# PROCESS CHANGES — AFL RL engine — effective 02/07/2026
### For folding into BUILD + SUPERVISOR kickoffs and Luke's operating practice.
### Scope: process/rules/guidelines only — no engine content changes.

META-PRINCIPLE: the project's rules are mostly right; enforcement lives in per-instance
discipline, which resets every rotation. Wherever a rule can become a MECHANISM — a
script, template, state machine, or manifest — make it one. Rules decay across
handovers; mechanisms don't.

## DO FIRST (before further engine work)

### 1. Five-state workstream vocabulary — "closed"/"done" are banned words
PROPOSED → DERIVED → WIRED → VERIFIED → BAKED.
Every backlog line, CHANGELOG entry, and handover claim carries exactly one state.
VERIFIED requires naming the cold-reproduction artifact (script + number). BAKED
requires Luke's explicit go. Rationale: B1 was a vocabulary failure ("STEP 3 — CLOSED"
meant measured, was read as wired; step 4 validated on placeholders). Current
exposure: "M1+v7 bake-ready" carries the same ambiguity today.

### 2. doc_lint.py — mechanized doc hygiene, gating every tarball cut
Build writes once; every re-cut runs it and FAILS on hits: grep the doc set for every
superseded head/store hash and stale status words ("LATEST", "current", "pending",
"not yet") outside a SUPERSEDED banner. Rationale: reconcile-by-deletion has been a
standing rule for weeks and keeps failing in doc bodies (stale "LATEST" mid-body;
backlog headed 7147b824 listing done work as pending). A gate cannot forget.

### 3. SHIP_GATES.md — frozen acceptance suite, created BEFORE the PVC stage
Contents (Luke picks): ~15-20 named relativities he'd stake his league record on +
cohort growth gate + book gates + JS parity. Frozen on creation. New player reads go
to V_NEXT.md unless they break a gate. The engine ships when the suite passes.
Rationale: reads are an infinite queue; the PVC is the last major stage and three
parked items (1.19×, SITOUT tail, no-games tail derivation) already point at it — the
stopping rule must exist before curve work begins or the treadmill restarts on the
most expensive stage.

## STANDING CHANGES

### 4. Fixed build-return template (supervisor-enforced)
≤30 lines: state header (head / store / tarball id) · PASS/FAIL with reproduced
numbers · what did NOT move · artifacts by filename+md5 (never inlined) · hypotheses
with status · next action. Supervisor BOUNCES nonconforming returns rather than
ingesting them. Rationale: full pastes killed the strongest supervisor instance;
compressed returns also shrink Luke's relay burden and the over-validation surface.

### 5. State-stamped, latest-only relays (Luke's practice)
Every relayed message opens: as-of <time> · head <hash> · store <hash> · supersedes
<doc/turn>. Never relay an intermediate return once a later one exists. One live
instance per role; no revived instances. Rationale: the recursion false-blocker
propagated between chats; a revived supervisor carried findings four candidates
behind head.

### 6. Hypothesis register + enforced causal vocabulary
Observations (facts) vs mechanisms (H1/H2/... with UNTESTED / FALSIFIED / CONFIRMED
+ the isolation test that settles each). NO strategy, descoping, or blocker status
may reference an UNTESTED mechanism — enforced by the supervisor on FAILURE reports
as strictly as success reports. Steelman rule: when a Luke read is falsified, its
strongest form is tested before the thread closes. Rationale: the recursion "real
latent bug" endorsement; the 2026-drop answer being Luke's own instinct in strong
form after the weak form was falsified.

### 7. REQUIRED_INPUTS manifest in every kickoff/directive
Build verifies presence at restore-verify time and reports gaps TURN ONE, before any
directive executes. Rationale: the 103-player dev template discovered absent
mid-session in the A1 chat; that fold-in is imminent.

### 8. BAKE_CHECKLIST.md — written before its first use (M1+v7)
Cold audit at head → Luke read-pass on a fixed named panel → bake → full re-verify
suite (md5s, 10-panel, named players, book, parity) → tarball with doc_lint pass →
send. First execution sets the precedent; the ritual must precede it.

### 9. DECISIONS.md — defaults + expiries
Every open Luke-decision listed with its default action and expiry; one batched
decision turn per session; optional pre-delegated class ("proceed if it moves no
player >X% and passes all gates; log for review"). Rationale: the 1.19× pattern —
parked decisions spanning rotations, re-litigated at each handover.

### 10. Cadence rules
Rotate any heavy chat at ~70-80% as scheduled maintenance (mint rev, refresh kickoff,
seed successor). Cold audit: before any bake, after any rotation, on any
VERIFIED→BAKED transition — always scoped to the current head; auditor shares no
context with the instances it checks. WIP cap: TWO live tracks maximum; everything
else queues behind, not beside.

### 11. Effort rule — original + amendment (registered per DIRECTIVE 6, 2026-07-02)
ORIGINAL RULE (as practiced in the supervisor↔build directive protocol; its verbatim
text was NOT previously registered in-repo — this section is the registration; the
supervisor corrects the original's wording here if it differs): every directive
carries an EFFORT line naming the level (medium / high / xhigh) with a rationale tied
to the work's hardest step.
AMENDMENT (verbatim, DIRECTIVE 6): every effort recommendation includes one sentence
answering "why is this not one level lower?"; medium = floor, no downward line; high
names the step that degrades at medium; xhigh names the derivation that needs it;
specificity test — no namable step → drop a level.
BASE RULE (verbatim, registered per DIRECTIVE 7, 2026-07-02 — the operating baseline the
original registration and the D6 amendment sit on): high default · xhigh with
justification · max with explicit sign-off · every directive carries level + wall-clock
band + walk-away note.

## EXPLICITLY UNCHANGED
Verbatim relay (fidelity is the audit trail; the state stamp fixes its weakness).
Nothing-bakes-without-Luke's-go. Player reads as ground truth. Per-turn notepads and
proactive handover sends. Finest-resolution-then-smooth. Backup-before-edit.
One-engine-load-per-process. Reconcile-by-deletion (now mechanized via doc_lint).
