# Implementation Guide

## Target setup

```text
GitHub repository
├── legacy production engine (frozen)
├── vNext challenger
├── current specifications and decision log
├── tests and CI
├── persisted model artifacts
└── accepted reports

ChatGPT Project
├── milestone planning and model review
├── PR review and result interpretation
└── release decisions

Codex
├── bounded implementation tasks
├── experiments and test execution
└── focused pull requests
```

## What Luke needs to do once
1. Ensure the current repository is on GitHub.
2. Create a `vnext` branch from the current production branch.
3. Connect the repository to Codex.
4. Create a ChatGPT Project named `AFL RL Engine` and connect or add the GitHub repository.
5. Apply the transition bundle on a branch named `feature/task-001-bootstrap` or ask Codex to apply it using the supplied task prompt.
6. Open a pull request into `vnext`.

After this, routine work should not require exchanging large ZIP files through chat.

## Recommended ChatGPT Project layout
Use fresh chats at milestone boundaries:
- `M00 — Repository transition`
- `M01 — Player universe and legacy benchmark`
- `M02 — Distributional coherence`
- `M03 — Career trajectories`
- `M04 — Keeper utility`
- `M05 — Currency and UI`
- `M06 — Release review`

At the start of each chat, provide the pull-request link or branch name. The chat should read `docs/current/HANDOVER.md` and the active task from GitHub before reviewing work.

## Normal task loop
1. ChatGPT writes or updates a task file.
2. Luke submits the task to Codex.
3. Codex opens a focused PR.
4. CI runs.
5. ChatGPT reviews the diff, tests, metrics, and report.
6. Luke approves the modelling or release decision.
7. The decision log and handover are updated before merge.

Luke should not need to mediate implementation details. His main decisions are:
- approve or reject a modelling hypothesis;
- confirm a league-rule interpretation;
- approve a production release.

## First three tasks

### TASK-001 — bootstrap
Migration and reproducibility only. No model or value changes.

### TASK-002 — authoritative player universe
Resolve the 752-versus-805 population discrepancy and export a stable player/position contract from the legacy engine.

### TASK-003 — fair legacy benchmark
Run legacy, vNext, and simple baselines on identical leakage-safe historical snapshots and outcome targets.

TASK-003 is the first major decision point. Its result determines whether the current vNext direction is genuinely better than the legacy forecast, not merely better than a naive baseline.

## What ChatGPT can do directly
- design the model and validation protocol;
- inspect repository code and results;
- write task specifications and acceptance criteria;
- review Codex PRs;
- run independent analyses on exported artifacts;
- create documentation, tests, and implementation patches when repository access permits;
- recommend acceptance, revision, or rejection.

## What requires Luke or Codex
- account-level GitHub/Codex connection;
- creating or merging GitHub branches and PRs when ChatGPT lacks write access;
- running long repository experiments in the durable development environment;
- production release approval.

## Completion discipline
Do not move to a later phase because an agent has produced code. Move only when the phase exit gate in `ROADMAP_TO_PRODUCTION.md` has passed and the result is recorded in `DECISION_LOG.md`.
