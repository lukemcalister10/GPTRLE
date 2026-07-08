# Decision Log

## D-001 — Objective outcome target
**Status:** accepted

Train and validate against realised future SuperCoach outcomes and keeper utility derived from league rules. Do not use historical trades, keeper drafts, market rankings, or named-player opinions as truth labels.

## D-002 — Two-track development
**Status:** accepted

Track A challenges the forecast while initially preserving the legacy utility transform. Track B separately validates the keeper-utility layer. This prevents simultaneous changes from hiding causality.

## D-003 — GitHub as source of truth
**Status:** accepted

Accepted code, documents, reports, model artifacts, and decisions live in Git. Chats are not durable project state.

## D-004 — Codex implementation, ChatGPT direction/review
**Status:** accepted

Codex receives bounded repository tasks and creates reviewable changes. ChatGPT designs tasks, reviews evidence and diffs, and maintains modelling coherence. Luke approves production releases.

## D-005 — Lean guardrails
**Status:** accepted

Retain data integrity, leakage prevention, deterministic artifacts, baseline comparison, full-population diffs, and explicit release approval. Retire agent-session rituals, named-player hard gates, duplicated hash prose, tarball-centric handoffs, and overlapping authoritative documents.

## D-006 — Model changes must beat baselines
**Status:** accepted

Complexity is not evidence. A challenger must beat declared simple baselines and the legacy engine on the locked outcome-based protocol before replacing a production component.

## D-007 — Current engine frozen during challenger development
**Status:** accepted

The legacy production engine remains unchanged and reproducible until vNext earns replacement. Necessary legacy adapters or exports should be side-effect-free and isolated wherever possible.

## D-008 — Board intuition is diagnostic
**Status:** accepted

Luke's football and keeper intuition is used to identify anomalies and formulate hypotheses, not as a training label or fixed player-ordering gate.

## D-009 — Chat rotation by milestone
**Status:** accepted

Use one ChatGPT Project and fresh chats at coherent milestone boundaries. Each new chat reads a generated repository handover and active task rather than relying on a long conversation.

## D-010 — TASK-006 release block
**Status:** accepted

TASK-006 and the TASK-007 package that exports it remain merged experimental history, but neither is eligible for promotion or release. The unchanged Claude board remains the production baseline while the identified defects are audited and addressed through separate one-hypothesis pull requests.
