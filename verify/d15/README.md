# D15 v2 — Independent Verification Artifacts

Re-runnable reproductions of the three load-bearing claims behind candidate **v2.4**
(git `fa6abd0`, engine `_merged_recover.py` md5 `7c199a1f`) plus the live
Cooper Duff-Tytler materiality read. PR #21's audit returned CLEAR on narrative
reproductions; this bundle commits the **scripts + outputs** so the owner or a second
seat can re-derive each claim from a fresh clone.

**These are verification artifacts only. No engine file is touched. Nothing is baked.**

## What each script proves

| # | Script | Output | Claim | Result |
|---|--------|--------|-------|--------|
| V1 | `refit_v0_curve.py` | `refit_output.txt` | The D14 V0 board curve re-derived from source (`_v0_raw`) with an independent re-implementation of the fit reproduces the engine's live `star()` curve. | **PASS** — max abs dev `0.000e+00` over 2700 probe points |
| V2 | `floor_sweep.py` | `floor_sweep_output.txt` | The KPP retention floor (Owner Override O1 = `max(KPP,nonKPP)`) never lowers a value — pure lower bound over every cell. | **PASS** — 540 cells, 0 violations, 0 monotonicity breaks |
| V3 | `book_hashcheck.py` | `book_hashes.txt` | The walk-forward book regenerated on fa6abd0 (`_BOARD_PATH=False`, backtest exemption) is byte-identical to the committed `s4_matrix_v24.json`. | **PASS** — stable-keyed sha256 identical, maxΔ=0, 2649 players |
| V4 | `dufftytler_decomp.py` | `dufftytler_decomp_output.txt` | Three-column CONTROL/v2.3/v2.4 decomposition of Duff-Tytler's price + V0, the position field the curve keys on, the RUC-toggle exposure, and the next-draft ruck entrant probe. | materiality read |

## How to reproduce (from a fresh clone of fa6abd0)

```bash
bash setup_env.sh && export PATH="$HOME/rl_venv312/bin:$PATH"   # pinned venv (py3.12.3/numpy2.4.4/scipy1.17.1/sklearn1.8.0)
python verify/d15/refit_v0_curve.py
python verify/d15/floor_sweep.py
python verify/d15/book_hashcheck.py
python verify/d15/dufftytler_decomp.py
```

## Harness (`_d15_common.py`)

- Each engine tree is run in an **isolated subprocess** (no cross-tree module cache) —
  "sequential engine loads only". The tree is materialised by `git archive <sha>` of the
  full `engine/rl_after` + `engine/forward_valuation` subtrees, so `wire_redesign.py` /
  `par_redesign.py` (which differ across trees) travel with their `_merged_recover.py`.
  **No tree-mixing.**
- The engine-file md5 is **asserted** against the pinned value before any computation:
  - CONTROL `8aed420a` = git `f4a4d34`
  - v2.3 `f3e537ba` = git `def39f5`
  - v2.4 `7c199a1f` = git `fa6abd0`
- Pinned env (relay STEP 0): `PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25
  RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22`, `RL_RUC_PRIOR_CAP` at its 1.73 default.
- The prior model `cm` (md5 `34faa865`) is seeded from the committed `data/cm_400.pkl`
  for speed; if that cache is absent the engine deterministically retrains it byte-for-byte.
