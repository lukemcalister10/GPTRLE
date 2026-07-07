#!/usr/bin/env python3
# GAMES-RAMP D10 phase 4 — FINAL derived constants (offline; reproducible from p1/p2/p3 artifacts).
# R_SIT[cls][d] = m_sit(d) / norm(d): kernel-smoothed sit-out realization (p2, eff-n>=35, RUC shape
#   pooled with KPP x measured RUC level) over the SAME-DEPTH all-still-listed norm (p3) — the locked
#   estimator's "0.76 form" (daEV ratio vs normal-dev baseline), on the V0 ruler. 3-pt smooth, clip
#   [0.05, 1.0]. tau=0 knot structural 1.0 (value held through pre-season — Luke 2a).
# LAM_SIT[g] = evidence-credit blend (p2): kernel-smoothed isotonic m(g), normalized (m(g)-m(0))/(m(6)-m(0)),
#   structural endpoints lam(0)=0, lam(6)=1 (continuity at graduation).
import json, os
import numpy as np
SC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P2 = json.load(open(os.path.join(SC, 'p2_curves.json')))
M_SIT = P2['R_FINAL']            # kernel-smoothed sit-out E[O/V0] by class, depths 1..6
LAM = P2['LAMBDA']
# same-depth norms from p3_baseline.py (2026-07-03 run, engine 4a134d05, logged in task output):
NORM = {'nonKPP': [0.462, 0.740, 0.891, 0.977, 1.068, 1.081],
        'KPP':    [0.423, 0.683, 0.868, 1.000, 1.077, 1.215],
        'RUC':    [0.299, 0.630, 0.851, 1.002, 1.084, 1.125]}
R = {}
for cls in ('nonKPP', 'KPP', 'RUC'):
    ratio = [m / n for m, n in zip(M_SIT[cls], NORM[cls])]
    sm = []
    for i in range(6):                       # 3-point [0.25,0.5,0.25] smoothing, reflective ends
        lo = ratio[max(0, i - 1)]; hi = ratio[min(5, i + 1)]
        sm.append(0.25 * lo + 0.5 * ratio[i] + 0.25 * hi)
    R[cls] = [round(float(np.clip(v, 0.05, 1.0)), 3) for v in sm]
print('== FINAL DERIVED CURVES (D10 games-ramp) ==')
print('R_SIT (retention of LIVE START VALUE, end-of-season depths 1..6; tau=0 structural 1.0):')
for cls in R: print(f'  {cls:7s} raw-ratio ' + ' '.join(f'{m/n:.3f}' for m, n in zip(M_SIT[cls], NORM[cls]))
                    + '  -> smoothed ' + ' '.join(f'{v:.3f}' for v in R[cls]))
print('LAM_SIT (games-credit blend, end-of-season games 0..6):', LAM)
print('\nmid-season examples at fE=0.583 (R14/24): tau=0.583 ->',
      {cls: round(1 - 0.583 * (1 - R[cls][0]), 3) for cls in R})
json.dump(dict(R_SIT=R, LAM_SIT=LAM, NORM=NORM, M_SIT=M_SIT), open(os.path.join(SC, 'p4_final.json'), 'w'), indent=1)
print('wrote p4_final.json')
