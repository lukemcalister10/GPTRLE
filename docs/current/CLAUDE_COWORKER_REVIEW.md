# Claude coworker review

## Read this first

This is a concise engineering handover from the vNext workstream to the Claude-era project. It is written to help improve the product, not to replace it.

The main conclusion is:

> Claude's strongest asset is its keeper-utility architecture. Its weakest area is forecast generation, validation discipline, and coupling between forecast, utility, export, and UI logic.

Do not discard the whole Claude engine. Keep the useful keeper-value structure, replace or isolate unvalidated forecasting assumptions, and make every change pass locked historical and production checks.

---

## What Claude currently does well

1. **It prices more than five years of production.** Young players retain option value and long-run asset value.
2. **It avoids the severe capital collapse of direct five-year surplus pricing.** Claude allocates about 47.4% of board value to the top 100 and about 10.1% to the bottom half. The rejected direct five-year vNext utility placed 85.3% in the top 100 and only 0.047% in the bottom half.
3. **It contains useful keeper-specific structure.** Pedigree, positional scarcity, developmental runway, upside, career duration and retained value are represented in some form.
4. **It is capable of sensible nonlinear treatment.** The project contains separate handling for established decliners, thin-career players, opportunity gates, age effects, recency and positional groups.

These are reasons to preserve the utility spine while improving the forecast inputs and engineering design.

---

## Highest-priority problems

### P0 — Forecast and keeper utility are entangled

Claude's code often mixes:

- prediction of future games and scoring;
- age and retirement probability;
- positional replacement;
- upside and pedigree;
- keeper asset value;
- UI/export scaling.

This makes it difficult to determine whether a board movement came from a better forecast or a different value judgement.

**Fix:** define explicit interfaces:

1. `ForecastProvider`: annual distributions or expectations by player and lead.
2. `KeeperUtility`: converts forecasts plus league rules into raw asset value.
3. `CapitalAllocator`: normalises values to the board's total capital.
4. `Exporter`: identity-safe output only.

No forecasting rule should directly change board scaling, and no UI code should affect model inference.

### P0 — No independent evidence that Claude is superior after year 5

Claude contains a full-career curve, but the project has not established that it predicts years 6+ better than a validated alternative.

A tested terminal model for years 6–10 failed:

- rolling-origin observations: 12,483;
- model MAE: 51.46;
- monotone decay MAE: 42.47;
- model was 21.16% worse overall and 34.00% worse for age-30+ boundary states.

**Fix:** treat Claude's long tail as incumbent keeper-utility structure, not proven forecast truth. Do not introduce discontinuous year-6 rebounds. Any future tail replacement must be trained and assessed under rolling-origin validation.

### P0 — Double survival and retirement fading is an active integration risk

TASK-003Q `exp_games` and `exp_points` are unconditional. They already include the probability of not producing a meaningful season.

**Fix:** never multiply those fields by another survival, retirement, delisting or opportunity probability. Conditional fields may be used only when the model explicitly needs conditional production.

### P0 — Identity must never depend on player name

The authoritative universe contains 804 players. Max King and Maxwell King are distinct records and have previously exposed identity risks.

**Fix:**

- primary join: `stable_player_id`;
- controlled bridge: `legacy_key`;
- fail closed on duplicate or missing identifiers;
- prohibit name-only joins in production and tests.

### P0 — Hidden mutable state and import-order behaviour

The legacy engine relies heavily on module globals, monkeypatching, environment variables, rebinding functions and runtime path assumptions. A confirmed defect occurred because a second `rl_model` module instance was executed, so object-identity membership checks silently failed for almost the entire real player store.

**Fix:**

- remove `id(object)` membership logic;
- use stable keys everywhere;
- replace monkeypatching with explicit dependency injection;
- move runtime configuration into an immutable config object;
- add a test that imports and executes the engine through every supported entry point and verifies byte-identical player outputs.

### P0 — Rule accumulation has outgrown explainability

`engine/rl_after/_merged_recover.py` contains numerous layered fixes, candidate rules, frozen tables, rejected experiments, clock pinning, age multipliers, fades, gates and special paths. Some are justified, but their interactions are difficult to reason about and easy to break.

**Fix:** extract each concept into a named pure function or component with:

- a single purpose;
- stated inputs and output semantics;
- historical evidence reference;
- unit tests at boundaries;
- an ablation result showing whether it helps.

A rule without an ablation or locked acceptance test should not be promoted to production.

---

## What the vNext work established

### Forecasting

TASK-003 benchmark:

- 5,622 player-origin snapshots;
- 20,094 player-origin-lead rows per model;
- 25 legal rolling-origin folds;
- zero target failures and zero fold failures.

Relative to the original baseline, vNext improved:

- meaningful-season Brier score by 30.1%;
- games MAE by 11.7%;
- total-points MAE by 13.5%.

TASK-003Q is the accepted forecast model. It uses an age-horizon hybrid for the meaningful-season event model while leaving conditional games, conditional average and thresholds unchanged.

Confirmed production output:

- 804 players;
- 4,020 annual player-lead rows;
- five leads per player;
- zero duplicate keys;
- valid probabilities, thresholds and quantiles;
- exact blend weights;
- Max King and Maxwell King separate.

### Utility experiments

1. **Direct five-year surplus pricing failed as a keeper board.** It concentrated 85.3% of value in the top 100 and nearly eliminated bottom-half value.
2. **A terminal years-6–10 model failed.** It was materially worse than monotone decay and did not repair concentration.
3. **TASK-006 passed.** It preserves Claude's utility spine and adds only the marginal five-year difference between TASK-003Q-fed and unchanged current-vNext-fed boards.

TASK-006 results:

- 804 players;
- 99-player top-100 overlap with Claude;
- mean absolute rank movement: 1.56;
- maximum movement: 33;
- 100% preservation of the TASK-003Q marginal direction;
- total board capital unchanged;
- top-100 share: 47.31%;
- bottom-half share: 10.19%.

This is the recommended current integration architecture.

---

## Recommended architecture now

### Production value formula

Use Claude as the incumbent keeper-utility spine and apply the validated marginal forecast adjustment:

```text
TASK006_value_raw = Claude_value
                  + (TASK003Q_fed_five_year_utility
                     - current_vNext_fed_five_year_utility)
```

Then rescale once to preserve total board capital.

This formula intentionally transfers only the difference caused by TASK-003Q. It does not claim the direct five-year utility is a complete keeper valuation model.

### Guardrails

- no second survival fade;
- no name-only joins;
- no negative or non-finite values;
- total capital conserved;
- deterministic repeat output;
- one authoritative player row each;
- version every forecast and utility component;
- retain Claude base value and adjustment separately for auditability.

### Required exported fields

At minimum:

- `stable_player_id`;
- `legacy_key`;
- player display fields;
- Claude base value/rank;
- current-vNext five-year utility;
- TASK-003Q five-year utility;
- TASK-003Q marginal adjustment;
- final TASK-006 value/rank;
- annual TASK-003Q lead 1–5 forecasts;
- model versions and generation timestamp;
- identity and validation status.

---

## Specific model improvements Claude should investigate

### 1. Benchmark each Claude component independently

Run ablations for:

- pedigree pole;
- exposure gate;
- developmental tenure fade;
- recency level;
- decliner shed;
- age multiplier;
- upside fade;
- positional replacement;
- captain premium;
- retention and staleness layers.

Measure both forecast metrics and board-distribution metrics. A component that makes current examples look better but does not improve historical outcomes should be removed or demoted to an explicit owner preference.

### 2. Separate expected outcome from upside distribution

Claude often uses upper bands and pedigree to represent future option value. Preserve that idea, but expose it explicitly:

- expected annual output;
- probability of meaningful season;
- upside quantiles;
- downside or zero mass;
- separate option-value conversion.

Do not hide upside inside an adjusted mean.

### 3. Replace hard thresholds with smooth, tested transitions

The project contains many thresholds around games, seasons, tenure and decline. Hard thresholds create rank cliffs.

Use continuous features or monotone splines where possible, and add boundary tests immediately below and above every retained threshold.

### 4. Calibrate by position, age and horizon

The TASK-003Q work showed that event-model performance varies by both age and lead. Do not use a single global retirement or survival curve without checking:

- exact age;
- forecast lead;
- position group;
- tenure and games history;
- zero-history status.

### 5. Preserve zero-history players in all validation

Never train or validate only on players who later succeeded. Retain delistings, zero-game careers, rookies and busts. Otherwise pedigree and option value will be overstated.

### 6. Establish keeper-value evaluation targets

Forecast accuracy is measurable; keeper value is not yet independently grounded.

Create historical decision targets such as:

- future discounted above-replacement production;
- realised trade-price proxies, if available;
- retained top-N roster utility;
- regret from keep/drop decisions;
- rank correlation with future multi-year utility.

Until such a target exists, treat capital-shape and current-player plausibility as guardrails, not proof of optimal keeper valuation.

---

## Engineering changes Claude should make

1. Break `_merged_recover.py` into small modules; keep a compatibility wrapper initially.
2. Remove absolute `/home/claude/...` runtime dependencies from model code.
3. Replace module-global dates such as 2026 with an explicit `as_of_year` and season-progress object.
4. Store all parameters in versioned configuration files with provenance.
5. Create a single canonical CLI that produces forecasts, values, validation report and app output.
6. Add manifests with input hashes, code SHA, model versions and output hashes.
7. Add deterministic snapshot tests for named edge cases and the full board.
8. Add schema validation before HTML/app export.
9. Ensure production code never imports diagnostic modules with side effects.
10. Archive rejected experiments with results rather than leaving inactive candidate logic embedded in production files.

---

## Files and resources to use

### Authoritative identity and production forecast

- `vnext/active_universe.py`
- `vnext/train_model_artifacts.py`
- `vnext/model_artifacts_task003q.py`
- `vnext/task003q_hybrid.py`
- `vnext/validate_task003r_production.py`
- `.github/workflows/task003r-production-validation.yml`

### Historical validation

- `vnext/build_historical_cohorts.py`
- `vnext/run_historical_folds.py`
- `vnext/run_task003k_folds.py`
- `vnext/benchmark.py`

### Claude integration and utility evidence

- `vnext/task004_claude_adapter.py`
- `vnext/task006_claude_delta_overlay.py`
- `.github/workflows/task006-claude-delta-overlay.yml`
- `reports/task-006-claude-delta-overlay/README.md`

### Rejected terminal approach

- PR #32 and workflow run `28909455423`.
- Do not reuse its terminal model without a new hypothesis.

### Production evidence

- TASK-003R workflow run `28904555873`; artifact digest `sha256:068b78541b28b0e72db436c5dc5945a6dd629bdb11ebbd68c3274802fc377245`.
- TASK-006 workflow run `28909797978`; artifact digest `sha256:35f253042cc208c25a9f8a0a83be78f11bc6526354d8058c72d347e8abc33e95`.

---

## Suggested execution order

1. Productionise TASK-006 in the normal export and app path.
2. Preserve base value and adjustment separately in every output.
3. Add deterministic full-board and UI-load checks.
4. Refactor identity, configuration and side effects before adding more model rules.
5. Build a component-ablation harness around Claude utility features.
6. Define an independent keeper-value target before attempting a full utility rewrite.
7. Only then consider replacing Claude's long career tail.

---

## Things not to do

- Do not splice an unrelated Claude year-6 projection onto a declining TASK-003Q year-5 trajectory.
- Do not apply retirement or survival twice.
- Do not replace Claude's full utility with direct five-year above-replacement surplus.
- Do not tune against a handful of named current players.
- Do not join by name.
- Do not add another rule to `_merged_recover.py` without an ablation and locked gate.
- Do not interpret a healthy-looking value distribution as evidence of forecast accuracy.

---

## Definition of success

Claude has improved the product when:

- forecasts are generated by a leakage-safe, historically validated provider;
- keeper utility is a separate, auditable layer;
- TASK-003Q inputs cannot be double-faded;
- identity joins are stable and complete;
- every production board is reproducible from a manifest;
- component ablations explain why each rule exists;
- the app consumes one versioned production output;
- changes are judged by locked historical evidence plus explicit keeper-value objectives, not ad hoc current-player examples.
