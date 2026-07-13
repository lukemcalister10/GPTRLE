```bash
python vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild
python vnext/run_task049_three_state_point_distribution.py
python vnext/analyse_task049_three_state_point_distribution.py
PYTHONPATH=vnext pytest -q vnext/tests/test_task049_three_state_distribution.py
cd vnext && pytest -q
python scripts/verify_legacy_manifest.py
python scripts/generate_handover.py
```
