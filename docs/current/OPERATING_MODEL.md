# Project Operating Model

## Purpose
This document defines the durable way the AFL RL Engine will be finished and maintained. GitHub is the source of truth. Chats are temporary workspaces, Codex is an implementation agent, automated tests enforce invariants, and Luke retains production-release authority.

## Roles

### Luke — product owner and league authority
- Defines league rules and the decision problem.
- Approves changes to keeper-utility policy and production releases.
- Flags implausible outputs as hypotheses to investigate.
- Does not need to provide subjective market data as model truth.

### ChatGPT — model and technical lead
- Designs experiments and acceptance criteria.
- Reviews architecture, code changes, metrics, and causal explanations.
- Writes bounded Codex tasks and reviews resulting pull requests.
- Updates the decision log after accepted or rejected experiments.
- May directly perform analysis or implementation where tools permit, but accepted work must be committed to GitHub.

### Codex — implementation agent
- Works from a narrow task file and repository instructions.
- Edits code, runs experiments and tests, and opens a focused pull request.
- Does not redefine the mission, acceptance criteria, or validation protocol.
- Must report uncertainty, failed tests, and deviations from the task.

### CI — mechanical arbiter
CI checks reproducibility and invariants. It does not decide whether football modelling assumptions are sensible.

## Source-of-truth hierarchy
1. Code, tests, data manifests, and model artifacts in Git.
2. Documents under `docs/current/`.
3. Accepted reports under `reports/`.
4. Pull-request discussion and decision-log entries.
5. Chat history.

When two sources disagree, the higher source wins. Claude-era kickoff, handover, session, bake, and supervisor documents are not binding unless their rule has been deliberately carried into `docs/current/`.

## Branch strategy
- `main`: reproducible current production engine and accepted releases.
- `vnext`: integration branch for accepted challenger work.
- `feature/<task-id>-<description>`: one bounded hypothesis or engineering task.
- `release/<version>`: production migration and final UI work.

`main` and `vnext` should be protected. Work enters them through pull requests.

## Work cycle
1. **Define:** create `docs/tasks/TASK-XXX.md` with scope, mechanism, exclusions, tests, metrics, and acceptance criteria.
2. **Implement:** Codex works on a short-lived feature branch.
3. **Verify:** CI runs integrity, leakage, deterministic artifact, and benchmark checks.
4. **Review:** ChatGPT reviews the diff, protocol adherence, results, and unintended effects.
5. **Decide:** Luke approves, rejects, or requests a revised experiment.
6. **Record:** update `DECISION_LOG.md`, generated handover, and accepted report.
7. **Merge:** only coherent, evidence-backed work reaches `vnext` or `main`.

## Pull-request boundaries
A PR should contain one of:
- repository or test infrastructure;
- one data-integrity repair;
- one forecasting hypothesis;
- one calibration change;
- one keeper-utility hypothesis;
- one UI/export feature;
- one release migration.

Do not combine a new model, changed validation, altered replacement levels, and UI redesign in one PR.

## Chat lifecycle
Use one ChatGPT Project for the AFL RL Engine. Start a fresh chat at a coherent boundary, normally one milestone or major PR review. Each new chat begins by reading:
1. `docs/current/HANDOVER.md`;
2. the active task file;
3. the relevant pull-request diff and report.

No critical decision may exist only in chat. `scripts/generate_handover.py` creates a compact current-state handover from repository facts.

## Reporting standard
Every model report must answer:
- What hypothesis was tested?
- What changed mechanically?
- What information was available at prediction time?
- What baselines were used?
- Did probability calibration improve?
- Did outcome accuracy improve at one, three, and five years?
- Which positions, ages, pick bands, and tenures improved or regressed?
- How did the current board move, and why?
- Is the result accepted, rejected, or still experimental?

## Release authority
No agent autonomously replaces the production board. A production release requires:
- all release gates in `ROADMAP_TO_PRODUCTION.md`;
- clean-checkout reproduction;
- a frozen model/data/artifact manifest;
- a rollback path to the legacy engine;
- Luke's explicit approval.
