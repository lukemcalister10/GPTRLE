#!/usr/bin/env python3
# GAMES-RAMP D10 phase 2 — OFFLINE derivation (no engine load) from p1_harvest.json.
#  (1) R(tau) retention-by-depth curves per class, gY==0 cells, kernel-smoothed (eff-n>=35 bw rule),
#      clipped <=1, RUC pooled with KPP for SHAPE (thin+bimodal, declared) scaled by its own N1-2 level.
#  (2) lambda(g_eff) evidence-credit from depth-1 cells g 0..5 + graduated boundary 6..9;
#      evidence-axis test: g vs q vs g*q (Kendall tau within played cells); isotonic in g.
#  (3) q-modifier derivation (outcome vs q within g>=1, controlling g).
import json, os, sys, numpy as np
from collections import defaultdict
SC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(os.path.join(SC, 'p1_harvest.json')))
cells = [c for c in H['cells'] if c['wc']]
grad = [c for c in H['grad'] if c['wc']]
print(f"cells={len(cells)} grad={len(grad)}")

def kendall(x, y):
    x, y = np.asarray(x), np.asarray(y); n = len(x); s = 0
    for i in range(n):
        d = (x[i+1:] - x[i]) * (y[i+1:] - y[i])
        s += np.sum(np.sign(d))
    return 2.0 * s / (n * (n - 1)) if n > 1 else 0.0

# ---------- (1) retention by depth, gY==0 ----------
print('\n== (1) R(depth) from zero-game cells (outcome r=O/V0, busts=0, still-listed) ==')
z = [c for c in cells if c['gY'] == 0]
print('per-class raw means (n):')
RAW = {}
for cls in ('nonKPP', 'KPP', 'RUC'):
    row = {}
    for d in range(1, 8):
        v = [min(c['r'], 2.0) for c in z if c['cls'] == cls and min(c['d'], 7) == d]  # winsor 2.0 declared
        if v: row[d] = (float(np.mean(v)), float(np.median(v)), len(v))
    RAW[cls] = row
    print(f"  {cls:7s} " + " ".join(f"d{d}:{m:.3f}/{md:.2f}(n{n})" for d, (m, md, n) in sorted(row.items())))

# kernel smoothing over depth (gaussian on d, bw grown until eff-n>=35), then clip<=1, floor>=0.02
def ksm(pts, dgrid, minn=35):
    out = {}
    for d0 in dgrid:
        bw = 0.5
        while True:
            w = np.array([np.exp(-0.5 * ((c - d0) / bw) ** 2) for c, _ in pts])
            effn = w.sum() ** 2 / (w ** 2).sum() if w.sum() > 0 else 0
            if effn >= min(minn, len(pts) * 0.9) or bw > 4.0: break
            bw += 0.25
        vals = np.array([v for _, v in pts])
        out[d0] = (float((w * vals).sum() / w.sum()), float(bw), float(effn))
    return out

DG = [1, 2, 3, 4, 5, 6]
SM = {}
for cls in ('nonKPP', 'KPP'):
    pts = [(min(c['d'], 7), min(c['r'], 2.0)) for c in z if c['cls'] == cls]
    SM[cls] = ksm(pts, DG)
# RUC: pooled KPP+RUC shape, scaled to RUC's own d1-2 level (declared: thin bimodal sample)
pts_kr = [(min(c['d'], 7), min(c['r'], 2.0)) for c in z if c['cls'] in ('KPP', 'RUC')]
smkr = ksm(pts_kr, DG)
ruc12 = [min(c['r'], 2.0) for c in z if c['cls'] == 'RUC' and c['d'] <= 2]
kpp12 = [min(c['r'], 2.0) for c in z if c['cls'] in ('KPP', 'RUC') and c['d'] <= 2]
scale = float(np.mean(ruc12)) / float(np.mean(kpp12)) if kpp12 else 1.0
SM['RUC'] = {d: (smkr[d][0] * scale, smkr[d][1], smkr[d][2]) for d in DG}
print(f'\nsmoothed (kernel bw grown to eff-n>=35; RUC = pooled KPP+RUC shape x {scale:.3f} level from d1-2 n={len(ruc12)}):')
R_FINAL = {}
for cls in ('nonKPP', 'KPP', 'RUC'):
    vals = [min(1.0, max(0.02, SM[cls][d][0])) for d in DG]
    R_FINAL[cls] = [round(v, 3) for v in vals]
    print(f"  {cls:7s} " + " ".join(f"d{d}:{v:.3f}(bw{SM[cls][d][1]:.2f},en{SM[cls][d][2]:.0f})" for d, v in zip(DG, vals)))
print('R_FINAL =', R_FINAL)

# ---------- (2) evidence axis + lambda ----------
print('\n== (2) depth-1 in-season evidence: axis test + lambda(g) ==')
d1 = [c for c in cells if c['d'] == 1]
d1p = [c for c in d1 if c['gY'] >= 1]
for nm, xs in (('g', [c['gY'] for c in d1p]), ('q', [c['q'] for c in d1p]),
               ('gxq', [c['gY'] * c['q'] for c in d1p])):
    print(f"  tau(outcome r, {nm}) within played d1 cells (n={len(d1p)}): {kendall(xs, [c['r'] for c in d1p]):+.3f}")
allg = d1 + grad
m = {}
for g in range(0, 10):
    v = [min(c['r'], 2.0) for c in allg if c['gY'] == g]
    if v: m[g] = (float(np.mean(v)), len(v))
print('  raw m(g): ' + ' '.join(f"g{g}:{a:.3f}(n{n})" for g, (a, n) in sorted(m.items())))
# kernel-smooth m over g then isotonic (monotone up, declared structural: evidence never negative credit)
pts = [(c['gY'], min(c['r'], 2.0)) for c in allg]
smg = ksm(pts, list(range(0, 10)), minn=35)
mg = [smg[g][0] for g in range(0, 10)]
mono = np.maximum.accumulate(mg)
m0, m6 = mono[0], mono[6]
lam = [float(np.clip((v - m0) / (m6 - m0), 0, 1)) for v in mono]
print('  smoothed m(g):', [round(v, 3) for v in mg])
print('  isotonic m(g):', [round(float(v), 3) for v in mono])
print('  LAMBDA(g_eff 0..6) =', [round(l, 3) for l in lam[:7]])

# ---------- (3) q-modifier within g>=1 ----------
print('\n== (3) quality signal within g (partial: residual r vs q after g-mean removed) ==')
res = [(c['q'], min(c['r'], 2.0) - m[c['gY']][0]) for c in d1p if c['gY'] in m]
print(f"  tau(residual, q) n={len(res)}: {kendall([a for a, _ in res], [b for _, b in res]):+.3f}")
# binned read
for lo, hi in ((0.0, 0.45), (0.45, 0.7), (0.7, 3.0)):
    v = [b for a, b in res if lo <= a < hi]
    if v: print(f"  q in [{lo},{hi}): mean residual {np.mean(v):+.3f} (n={len(v)})")
# grad boundary m(6-7) split by q — does quality at the seam matter?
for lo, hi in ((0.0, 0.6), (0.6, 0.85), (0.85, 3.0)):
    v = [min(c['r'], 2.0) for c in grad if lo <= c['q'] < hi]
    if v: print(f"  graduated (6-9g) q in [{lo},{hi}): mean r {np.mean(v):.3f} (n={len(v)})")

# ---------- depth>=2 in-season evidence (pooled check that lambda transfers) ----------
d2p = [c for c in cells if c['d'] >= 2 and c['gY'] >= 1]
d2z = [c for c in cells if c['d'] >= 2 and c['gY'] == 0]
print(f"\n  depth>=2: played mean r={np.mean([min(c['r'],2) for c in d2p]):.3f} (n={len(d2p)}) vs "
      f"zero-game mean r={np.mean([min(c['r'],2) for c in d2z]):.3f} (n={len(d2z)})")
json.dump(dict(R_FINAL=R_FINAL, LAMBDA=[round(l, 4) for l in lam[:7]],
               ruc_scale=round(scale, 4), m_raw={str(k): v for k, v in m.items()}),
          open(os.path.join(SC, 'p2_curves.json'), 'w'), indent=1)
print('\nwrote p2_curves.json')
