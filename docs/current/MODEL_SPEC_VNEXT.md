# vNext Model Specification

## Design principle
Separate objective future-outcome forecasting from keeper-league utility and from any optional owner policy.

```text
Historical Player Snapshot
    -> Future Outcome Distribution
    -> Correlated Career Trajectories
    -> Keeper Utility
    -> Currency Mapping
    -> Optional Transparent Policy Layer
    -> UI Export
```

## Layer 1 — historical snapshot
A typed `PlayerSnapshot` contains only facts observable at the forecast origin. Time-dependent fields must be reconstructed, not copied from a current player object.

Minimum fields:
- stable player key;
- origin year and data cutoff;
- draft facts;
- age and tenure;
- historically known position eligibility;
- observed games and SuperCoach scoring through origin;
- recency, trend, exposure, and sample-size features.

## Layer 2 — future outcome distribution
For each future season, estimate:
- probability listed/active;
- probability of a meaningful season;
- games distribution conditional on state;
- SuperCoach average distribution conditional on playing;
- threshold probabilities (80/90/100/110/120);
- position eligibility where historical data supports it.

The continuous distribution and threshold probabilities must be coherent. Separate models may contribute, but the final simulated distribution must reproduce calibrated probabilities and non-crossing quantiles.

## Layer 3 — trajectory dependence
Future seasons are correlated. The simulator must represent:
- persistent establishment or non-establishment;
- persistent scoring quality;
- development and decline;
- availability persistence;
- position- and career-stage-specific dependence where supported.

A single future peak plus a generic age curve remains a baseline, not the target architecture.

## Layer 4 — keeper utility
Initially retain the legacy concepts so forecasting improvements can be isolated:
- position-specific cheap replacement;
- smooth value above replacement;
- captaincy value;
- temporal discounting;
- career runway.

Then test these against explicit roster marginal utility under:
- 16 teams;
- 42 senior + 4 rookie lists;
- offseason senior cut to 37;
- 6 DEF with at least 2 key;
- 6 FWD with at least 2 key;
- 1 RUC;
- 5 MID;
- 5 free bench positions;
- captain double scoring;
- constrained replacement acquisition;
- indefinite retention.

## Layer 5 — currency mapping
Currency mapping should be monotonic and documented. It must not conceal the raw forecast or utility.

Every exported player should expose:
- raw forecast statistics;
- raw one/three/five-year utility;
- remaining-career utility;
- current final currency value;
- +1/+2 expected future value distributions;
- downside, median, and upside;
- probability of appreciation;
- probability and expected count of elite seasons;
- policy adjustment, if any.

## Layer 6 — optional policy
Owner-set retention floors, special risk preferences, or other policy choices must be explicit and removable. They are never part of the objective forecast and are not used to prove predictive accuracy.

## Current progress-05 status
Implemented experimentally:
- leakage-safe draft/scoring snapshots;
- one-to-five-year hurdle models;
- persisted annual artifacts;
- calibrated event and threshold models;
- correlated five-year simulation;
- existing replacement/captaincy/discounting utility concepts;
- simulated +1/+2 utility distributions.

Still required:
- authoritative active-player universe;
- legacy benchmark on identical snapshots;
- coherent continuous/threshold distribution;
- better position/career-stage dependence;
- survival and decline beyond five years;
- utility-layer validation;
- current currency mapping and UI integration.
