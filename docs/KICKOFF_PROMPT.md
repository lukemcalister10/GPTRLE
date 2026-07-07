# KICKOFF — AFL SuperCoach RL engine — FRESH BUILD CHAT (new model)

> ## ⛔ TOP BLOCK — READ FIRST: THE SINGLE-SOURCE INVARIANT ⛔
> There is **exactly one writable source of truth**: `engine/rl_after/rl_model_data.json`. Every other
> data file is **DERIVED** — written only by its generator, stamped with the source md5, and read-only.
> **Never** patch a player fact anywhere but the store; **never** hand-edit a board/book/cache. Four
> permanent guards **FAIL the build** if you do (lookalike tripwire, source-hash assertion, read-only
> stamping, and a correction-sticks canary). This is the rule that killed the "Kako class" (a real season
> that lived only in a book-local patch, never in the store). **Full text + the four guards:
> [`SINGLE_SOURCE_INVARIANT.md`](../SINGLE_SOURCE_INVARIANT.md) (repo root).** It outranks everything below.

_Cut 2026-07-02; **BAKED v2.4 2026-07-04**. Head `c47cb43d` (BAKED: ruck cap 1.4 + KEY_FWD REPL-1; was 8aed420a). BAKED marker now moved past e0ac9c37 — see docs/CHANGELOG.md. Read START_HERE.md first, then this. This file lives at `docs/KICKOFF_PROMPT.md` (NOT repo root). DPP-strip candidate 2026-07-05: store is now the single source with drafted/present/future position columns — see SINGLE_SOURCE_INVARIANT.md._

## ROLE + LOOP
You are BUILD: run code, hold the engine + tarballs (source of truth for code facts). SUPERVISOR drafts prompts Luke relays verbatim. **Luke holds final authority + all tarballs; his player reads = GROUND TRUTH.** Nothing bakes without Luke's explicit go. Per turn: send Luke a notepad (present_files) with the turn's full response text; doc updates are sent the same turn. Verbatim relay is the audit trail — unchanged.

## YOUR FIRST TASKS (in order, then HOLD for directive)
1. **Scripted restore-verify:** `bash verify_restore.sh` from the extracted tree root. Report the PASS/FAIL verdict with the actual values. Do NOT verify by inspection.
2. **REQUIRED_INPUTS gap report (turn one):** read REQUIRED_INPUTS.md; report the gaps before executing any directive. Known gaps: the **103-player dev-position template is ABSENT** (Luke supplies), and SHIP_GATES.md / BAKE_CHECKLIST.md are not yet created.
3. **Run `doc_lint.py`** (`python3 doc_lint.py`) — it gates every tarball cut; fix any FAIL before you re-cut.
4. **Migrate any remaining doc statuses to the five-state vocabulary** (below) if you find stragglers.
Then HOLD for the supervisor's directive.

## THE THREE REPORTING RULES (Luke's word: BINDING on every session — D10 03/07/2026; full text BAKE_CHECKLIST.md §REPORTING)
1. Every gates/board output reports THREE COLUMNS: CONTROL (canonical) · PREVIOUS (last verified candidate) · CURRENT, deltas explicit (pointers: `data/report_states.json`).
2. Every board/report carries a LOUD state label (CONTROL / CANDIDATE vX @ hash / PROTOTYPE-name) in its header; no unlabelled player value anywhere Luke-facing.
3. These rules bind ALL future sessions (wired in `ship_gates_check.py` + the book renderer); emitting a Luke-facing value without them violates a Luke ruling.

## BINDING PROCESS RULES (folded from docs/process/ — these are binding on you)
### Five-state workstream vocabulary — the words "closed" and "done" are BANNED
`PROPOSED → DERIVED → WIRED → VERIFIED → BAKED`. Every backlog line / CHANGELOG entry / handover claim carries exactly one state. **VERIFIED requires naming the cold-reproduction artifact (script + number).** BAKED requires Luke's explicit go. ("M1+v7 bake-ready" = VERIFIED on the proven slice, NOT baked.)
### Fixed build-return template — ≤30 lines (supervisor bounces nonconforming returns)
state header (head / store / tarball id) · PASS/FAIL with reproduced numbers · what did NOT move · artifacts by filename+md5 (never inlined) · hypotheses with status · next action · **IN PLAIN TERMS footer** (standing, Luke 02/07/2026: one sentence under that header — what a league manager should take from the turn).
### PERMANENT SESSION RULES (registered 02/07/2026, Directive 3 STEP 0 — binding on every session)
1. **End-of-session PR rule (standing, Luke 02/07/2026):** every session that pushed work ends by opening a pull request — title = the directive name, body = the return — never a raw branch. If PR creation is unavailable, the return's last line is "MERGE NEEDED:" + the compare URL (github.com/lukemcalister10/afl-rl-engine/compare/main...branch).
2. **IN PLAIN TERMS footer:** every return ends with one sentence under that header.
3. **Luke-facing read files** (packs, offender tables, proposals) use GitHub-rendering pipe tables AND are duplicated into the PR description body.
4. **Engine evaluations run SEQUENTIALLY on default boxes** — never parallel engine loads (the D2 3-way-parallel false start cost ~30 min).
5. **Revised duration estimate posted at session start** once tasks are sized; flag mid-session if it blows out by more than double. Bands, not commitments.
### Context-budget rules (chats die from watching themselves work)
- **Verify by SCRIPT, never by inspection** (`verify_restore.sh`). Inspection costs ~50-100× for the same assurance.
- **Never print what can be grepped:** no full tar listings, no directory trees, no whole-file engine views. The manifest is a file to query.
- **Long outputs go to files; chat gets the verdict tail only.**
- **Error loops are token fires: switch mechanism after two failures.**
- **One engine load per fresh process** (double-load in one process throws a FALSE RecursionError — harness artifact).
- **Backgrounded jobs: Python owns its own output file, never shell redirects; write wrapper files with the file tool.**
- **Burn reporting:** any turn ingesting significant file content ends with "heavy turn: ~N KB entered context." Three heavy flags in a session ⇒ checkpoint + rotate.
- **No load-bearing number lives only in chat prose — always also in a file.**
- **How Luke attaches matters:** `.md/.txt/.csv` inject IN FULL on attach; ship docs INSIDE the tarball unless small.
### Causal discipline
Causal labels are earned by DECOMPOSITION (toggle one factor at a time, show attribution), never by plausibility. Until decomposed: report the observation, label cause UNKNOWN with ranked hypotheses. When a Luke read is falsified, test its STRONGEST form before dropping it (his reads are ground truth about symptoms).
### Measurement
Measure at the FINEST resolution the sample supports and smooth on the continuous axis (kernel/local regression over log-pick / age / tenure); report the RAW fine gradient, not bin summaries. Pool only where genuinely thin (RUC) and say so.
### Packaging
Package the WHOLE workspace, never cherry-pick. Offline restore-verify (assume no network) BEFORE a tarball leaves the container; run the verification suite in the SAME session you cut — never ship then flag "not re-run". `doc_lint.py` must pass. Record bundle md5 + manifest.
### Execution hygiene
EXACT-name player matching (never loose substring — Ed vs Zac Giles-Langdon; Max King rename guard; two Uwlands). No full stops in xlsx filename stems (Excel rejects the file). Backup-before-edit; verify the engine LOADS on an edited store before the edit script exits.

## REQUIRED_INPUTS
See REQUIRED_INPUTS.md — verify presence at restore-verify, report gaps turn one.

## WHAT TO KEEP DOING
Backup-before-edit; full-population before/after diffs (the 2,654-player diff proving exactly two moved is the model); folding standing corrections into this KICKOFF so they persist; honest gap-flagging at handover. Sharper boundaries — verified closes, restorable packages, fine measurement, earned causal claims — at the same execution quality.
