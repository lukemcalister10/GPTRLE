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

## D-011 — Current partial season is recent but incomplete evidence
**Status:** accepted

Use the available 2026 data as recent partial-season evidence rather than discarding it or treating it as a completed season. Separate scoring rate from availability. Shrink small-sample performance toward the prior forecast and update negative availability conservatively: ambiguous missed games must not impose a penalty proportional to the fraction of the season missed. Positive demonstrated performance or selection may receive credibility faster than absence receives negative credibility. Do not mechanically prorate every player to a full-season games total.

The current snapshot is uniformly after 14 rounds. Every player has had one bye and therefore 13 possible matches. Use 13 as the current availability denominator for every player.

## D-012 — Keeper value is dynamic marginal roster utility
**Status:** accepted

With no salary, contract or draft-round retention cost, keeper value represents the risk-adjusted multi-year improvement created by retaining a player on a 42-player roster that must be reduced to 37 each offseason. Present contender, balanced and rebuilder views with heavier weight on the immediate and nearer future in every view. Forecast production, keeper utility and owner policy remain separate.

Replacement and positional scarcity must be derived from feasible roster allocation rather than a fixed positional-rank cutoff. The utility layer should optimise eligible starting, utility and bench assignments across a 16-team league and measure the marginal loss when a player is removed and the roster is re-optimised. This allows scarce lower-scoring positions to carry more value than plentiful higher-scoring positions when they solve a harder roster constraint.

## D-013 — Position eligibility uses current official data only
**Status:** accepted

Do not project future position eligibility pools. Apply the official positions currently known at the valuation date to every forecast season, and recalculate current and multi-year keeper utility whenever new preseason or in-season position updates are issued.

Dual-position value must emerge from roster optimisation rather than a symmetric fixed bonus. Adding midfield eligibility to a forward will usually provide little or no benefit, while adding forward eligibility to a midfielder may be valuable when it relieves a scarce forward constraint. The optimiser must be capable of producing zero flexibility value when the added eligibility does not improve the best feasible roster.

## D-014 — All selected players score; captaincy has vice fallback
**Status:** accepted

Each team selects 23 scoring players: 18 position-constrained players and five free-choice players. All 23 contribute their weekly score. The five free-choice slots therefore have full scoring value and accept every position.

A designated captain scores double. If the captain does not play, a designated vice captain receives the double-score bonus. If neither plays, no captain bonus is awarded.

Emergencies are outside the selected 23 and do not score automatically. A manager may deliberately activate an emergency into the selected side to cover an unavailable player; the activated player then scores as part of the 23 and the unavailable player does not.

## D-015 — Pooled Ridge accepted for conditional-average point forecasts only
**Status:** accepted

TASK-047 replaces the accepted TASK-012 pooled conditional-average `SGDRegressor` with a leakage-safe pooled Ridge estimator selected inside each rolling-origin training fold. It is accepted for conditional-average point forecasts because it materially improves conditional-average MAE overall and across the diagnosed ruck and elite-prior cohorts, while improving locked total-points MAE overall and preserving every non-average forecast output exactly.

This decision does not accept TASK-047 residual scales, point quantiles, keeper utility, current-board production or a release cutover. Uncertainty outputs remain blocked until a separate calibration audit evaluates pinball loss, quantile calibration and interval coverage against the locked `points` target.

## D-016 — TASK-048 keeps Ridge uncertainty outputs blocked
**Status:** accepted

TASK-048 is an evaluation-only audit of unchanged TASK-047 point quantiles against the locked `targets.csv` `points` target on the exact 20,094 rows per model and 25 legal folds. The audit improves primary mean pinball loss versus TASK-012, but uncertainty acceptance fails predeclared gates 3, 4, 5, 6 and 7: overall absolute quantile calibration error is too high, q25-q75 coverage is too wide, lead-level central interval coverage has material failures, and broad-position/prior-history subgroup coverage has material failures, and the locked target includes 1,776 one-to-five-game positive-point rows that the current exact non-meaningful zero-mass approximation cannot represent.

TASK-047 remains accepted only for conditional-average point forecasts. Its uncertainty outputs, keeper utility, current-board production and release promotion remain blocked. The next uncertainty work should be at most one isolated TASK-049 hypothesis for a target-compatible uncertainty repair; TASK-048 does not repair, recalibrate, blend or change the uncertainty model.

## D-017 — TASK-049 three-state point distribution rejected
**Status:** rejected

TASK-049 tested one locked uncertainty hypothesis: a deterministic three-state zero-game, one-to-five-game and meaningful-season point-distribution transformation of verified TASK-047 rows, preserving accepted TASK-047 point forecasts and every non-quantile output. The concise evidence records TASK-049 as rejected: mean pinball is approximately 141.71 versus TASK-047 141.11, gates 1-7 fail, and uncertainty remains blocked.

Integrity gates 8-9 pass after the corrected provenance checks: TASK-047 prediction-manifest, fold-failure and target-failure artifacts are hashed; candidate keys are inherited exactly from TASK-047; TASK-049 transformation failures are zero; baseline and candidate schemas are identical; and non-quantile outputs are unchanged. Large row-level predictions and diagnostics remain under `build/` and are represented in the committed report by hashes, row counts and concise aggregate tables.

Do not start TASK-050 in this branch. Another uncertainty hypothesis requires a separate decision.
