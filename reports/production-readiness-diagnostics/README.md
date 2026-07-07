# Production readiness diagnostic scaffold report

Diagnostic only: this report does not approve a model, alter production, fit models, or transform keeper utility.

## Coverage summary
| dataset | universe_players | dataset_players | covered | missing_from_dataset | extra_not_in_universe |
| --- | --- | --- | --- | --- | --- |
| vnext | 804 | 752 | 751 | 53 | 1 |

## Validity summary
| dataset | column | rows | missing | non_finite | prob_out_of_bounds | monotonicity_violations |
| --- | --- | --- | --- | --- | --- | --- |
| vnext | pick | 3760 | 0 | 0 | nan | nan |
| vnext | tenure | 3760 | 0 | 0 | nan | nan |
| vnext | age | 3760 | 0 | 0 | nan | nan |
| vnext | p_meaningful | 3760 | 0 | 0 | 0.0 | nan |
| vnext | cond_games | 3760 | 0 | 0 | nan | nan |
| vnext | cond_avg | 3760 | 0 | 0 | nan | nan |
| vnext | exp_games | 3760 | 0 | 0 | nan | nan |
| vnext | exp_avg | 3760 | 0 | 0 | nan | nan |
| vnext | exp_points | 3760 | 0 | 0 | nan | nan |
| vnext | p80 | 3760 | 0 | 0 | 0.0 | nan |
| vnext | p90 | 3760 | 0 | 0 | 0.0 | nan |
| vnext | p100 | 3760 | 0 | 0 | 0.0 | nan |
| vnext | p110 | 3760 | 0 | 0 | 0.0 | nan |
| vnext | p120 | 3760 | 0 | 0 | 0.0 | nan |
| vnext | lead | 3760 | 0 | 0 | nan | nan |
| vnext | forecast_year | 3760 | 0 | 0 | nan | nan |
| vnext | games_resid_sd | 3760 | 0 | 0 | nan | nan |
| vnext | avg_resid_sd | 3760 | 0 | 0 | nan | nan |
| vnext | p80>p90>p100>p110>p120 | 3760 | 0 | 0 | nan | 0.0 |

## Artifact loading / reproducibility
| path | exists | kind | file_count | sha256 | loaded_without_fitting |
| --- | --- | --- | --- | --- | --- |
| vnext/output/artifacts | True | directory | 6 | 95e125f647371c917b52726136e50eca3ab28f953d05507eb09aea9a47cbf3bc | True |

## Acceptance thresholds for future shadow mode
{
  "hard_player_coverage_min": 804,
  "probability_bounds": "all probability columns within [0,1]",
  "threshold_probabilities": "non-increasing p80>=p90>=p100>=p110>=p120",
  "non_finite_required_outputs": 0,
  "inference_fitting_allowed": false,
  "shadow_mode_min_duration": "one full refresh cycle before release decision",
  "approval": "requires separate release PR and explicit owner approval"
}

## Rejection thresholds
Reject or block release if any hard gate fails: player-key coverage below threshold, non-finite required outputs, invalid probabilities, threshold/quantile crossing, model fitting during inference, missing rollback artifact, or undocumented production/vNext incompatibility.

## Rollback requirements
Keep the frozen legacy export path and hashes available; record exact input/output artifact hashes; verify the candidate can be disabled without changing keeper utility or UI behaviour.