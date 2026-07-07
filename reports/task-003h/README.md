# TASK-003H support-diagnosis report placeholder

This directory is reserved for the diagnostic outputs from `vnext/analyse_task003h_support.py`.

The local checkout used for this change does not include the accepted TASK-003E build artifacts under `build/task-003e/comparison` or the corresponding fold artifacts under `build/task-003b-vnext-folds`, so no full-population CSV report is committed in this PR.

Run the documented command in `docs/current/TASK-003H-SUPPORT-DIAGNOSIS.md` after restoring those artifacts to generate:

- `transformed_support_summary.csv`
- `raw_feature_support.csv`
- `support_diagnosis.md`
- `manifest.json`

The diagnostic remains read-only with respect to model fitting, validation protocol, production forecast, values, keeper utility and UI.
