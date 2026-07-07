# TASK-003F diagnostic evidence

These files preserve the compact accepted outputs from the TASK-003F diagnosis:

- `material_regressions.csv`: the exact 15 slice/lead combinations more than 3% worse on total-points MAE, ranked by severity and practical burden;
- `fold_repeatability.csv`: the number of legal origins in which each pooled regression also appeared.

The full component and per-origin outputs are reproducible from the accepted TASK-003E artifact with:

```bash
python vnext/analyse_task003e_regressions.py \
  --comparison-dir build/task-003e/comparison \
  --out build/task-003f
```

The authoritative interpretation and guardrails are recorded in `docs/current/TASK-003F-REGRESSION-DIAGNOSIS.md`.
