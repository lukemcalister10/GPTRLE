# AFL RL Engine vNext — Project Charter

## Mission
Build the most accurate available model of future SuperCoach scoring and convert those forecasts into values appropriate to this specific 16-team keeper league.

## League structure
- 16 teams with heterogeneous competitive timelines.
- 42 senior players plus 4 rookies in-season.
- Off-season senior cut to no more than 37, followed by AFL-aligned national drafts.
- Weekly field: 6 DEF (at least 2 key), 6 FWD (at least 2 key), 1 RUC, 5 MID, plus 5 unrestricted bench selections.
- SuperCoach DPP updates apply mid-season; eligibility may be gained but not lost.
- Captain scores double; vice-captain doubles only when captain is a withdrawal.
- Draft picks are reverse-ladder and tradable two drafts ahead.
- Replacement players are acquired only by trade, mid-season draft, or off-season draft.
- Players may be retained indefinitely. No trade limits outside lockouts and list limits.

## Development strategy: two tracks

### Track A — Forecast challenger
Preserve the current keeper utility layer initially. Replace or challenge only the future-performance forecast using leakage-safe historical snapshots and calibrated trajectory forecasts.

### Track B — Keeper utility validation
After Track A is measured, test whether the existing replacement, captaincy, runway, discounting and currency transformations accurately approximate marginal roster value under the league rules.

## Primary target
A blended decision target containing:
- one-season scoring and availability;
- three-season discounted production above replacement;
- five-season discounted production above replacement;
- remaining-career keeper utility.

Results will also be reported separately by horizon so a gain in one dimension cannot conceal a loss in another.

## Historical validation design
Use rolling-origin evaluation rather than one fixed split.

- 1-year targets: historical origins through 2025 where the following season is complete/usable.
- 3-year targets: origins through 2023, subject to 2026 completeness handling.
- 5-year targets: origins through 2021.
- Long-career/peak targets: older cohorts only, with right-censoring explicitly handled.

Final untouched test cohorts will be selected after the snapshot audit establishes reliable information availability. Candidate structure:
- model development/training: earliest available years through 2017;
- validation/model selection: 2018–2020 origins;
- final long-horizon test: 2021 origins where five-year outcomes are observable;
- supplementary recent tests: 2022–2025 for shorter horizons only.

## Non-negotiable validation rules
- Every historical prediction uses only information observable at its origin date.
- Zero-game players and all middle outcomes remain in cohort tests.
- No future position, retirement, delisting or current-list leakage.
- No silent exception-based row removal.
- Metrics reported by position, draft type, pick band, age and tenure.
- Challenger must beat simple baselines and the current engine on pre-declared metrics before replacement.

## Baselines
1. Draft pick × position × draft-age historical prior.
2. Recent scoring plus a simple position-specific age curve.
3. Regularised low-complexity statistical model.
4. Current production engine.

## Forecast outputs
For each future season and player:
- probability of remaining listed;
- probability of playing a meaningful season;
- games distribution;
- SuperCoach average distribution conditional on playing;
- position eligibility state/distribution where supportable;
- joint simulated career trajectories.

## Keeper conversion
Track A initially sends every simulated trajectory through the current value-above-replacement, captaincy, discounting and career-runway framework. This isolates whether forecast changes are genuinely better.

## Replacement criteria
A component changes only when it improves out-of-sample results and does not create unacceptable keeper-market behaviour. Sophistication alone is not evidence.
