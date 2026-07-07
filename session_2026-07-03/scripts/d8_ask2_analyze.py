#!/usr/bin/env python3
# D8 ASK 2a — ANALYSIS of the harvested cells (no engine load). Explores the evidence signal,
# tests secondary axes at finest resolution, fits the smoothed grade curve, writes the knots.
import json, sys, hashlib
import numpy as np

src = sys.argv[1]
d = json.load(open(src))
cells = [c for c in d['cells'] if c['window_complete']]
print(f"primary cells n={len(cells)} (engine {d['engine']}, file md5 {hashlib.md5(open(src,'rb').read()).hexdigest()[:8]})")

E = np.array([c['E'] for c in cells])
v = np.array([c['v'] for c in cells])
rr = np.array([c['rr'] for c in cells])
sv = np.array([c['surv'] for c in cells], float)
gap = np.array([c['gap'] for c in cells])
gY = np.array([c['gY'] for c in cells])
q = np.array([c['q'] for c in cells])
qq = np.array([c['qual_q'] for c in cells])
keys = np.array([c['key'] for c in cells])

def stat(mask, label):
    if mask.sum() == 0:
        print(f'  {label:34s} n=0'); return
    u = len(set(keys[mask]))
    print(f'  {label:34s} n={mask.sum():4d} (uniq {u:3d})  mean v={v[mask].mean():.3f}  surv={sv[mask].mean():.3f}  mean rr={rr[mask].mean():.3f}  median rr={np.median(rr[mask]):.3f}')

print('\n== outcome by gap ==')
for g in range(0, 6):
    stat(gap == g, f'gap={g}')
stat(gap >= 5, 'gap>=5')

print('\n== gap>=1 cells: outcome by games-in-season-Y ==')
for g in range(0, 6):
    stat((gap >= 1) & (gY == g), f'gap>=1, gY={g}')

print('\n== gap>=1 cells: outcome by E bins ==')
bins = [(0, 0.0001), (0.0001, 1), (1, 2), (2, 3), (3, 4), (4, 10)]
for lo, hi in bins:
    stat((gap >= 1) & (E >= lo) & (E < hi), f'gap>=1, E in [{lo},{hi})')

print('\n== gap=0 cells: outcome by E bins (the live reference) ==')
for lo, hi in [(0, 4), (4, 6), (6, 8), (8, 12), (12, 30)]:
    stat((gap == 0) & (E >= lo) & (E < hi), f'gap=0, E in [{lo},{hi})')

print('\n== SECONDARY AXIS TESTS (finest resolution; pooled if thin) ==')
print('-- does gap matter beyond E? (gap=1 vs gap>=2 at matched E) --')
for lo, hi in [(0, 0.0001), (0.0001, 1.5), (1.5, 10)]:
    stat((gap == 1) & (E >= lo) & (E < hi), f'gap=1,  E in [{lo},{hi})')
    stat((gap >= 2) & (E >= lo) & (E < hi), f'gap>=2, E in [{lo},{hi})')
print('-- product pooling: quality vs volume at matched E (gap>=1, E in [1,4)) --')
m = (gap >= 1) & (E >= 1) & (E < 4)
hi_q = m & (q >= np.median(q[m]))
stat(hi_q, 'high-q (fewer games, better)')
stat(m & ~hi_q, 'low-q (more games, worse)')
print('-- does the STALE season quality matter? (gap>=1, split qual_q) --')
for lo, hi in [(0, 0.0001), (0.0001, 1.5), (1.5, 10)]:
    mm = (gap >= 1) & (E >= lo) & (E < hi)
    if mm.sum() == 0: continue
    med = np.median(qq[mm])
    stat(mm & (qq >= med), f'E[{lo},{hi}) qual_q>=med({med:.2f})')
    stat(mm & (qq < med), f'E[{lo},{hi}) qual_q< med')

# ===== the fit: NW kernel (eff-n>=35 bw-widening rule, D5 convention) + isotonic projection =====
def kernel_mean(x, xs, ys, min_eff=35.0, bw0=0.25, bwstep=0.25, bwmax=6.0):
    bw = bw0
    while True:
        w = np.exp(-0.5 * ((xs - x) / bw) ** 2)
        eff = float(w.sum())
        if eff >= min_eff or bw >= bwmax:
            return float((w * ys).sum() / w.sum()), bw, eff
        bw += bwstep

def isotonic(y):
    y = list(y); n = len(y); w = [1.0] * n; i = 0
    ys = y[:]
    # PAVA
    lvl = [[ys[i], 1.0] for i in range(n)]
    out = []
    for val in ys:
        out.append([val, 1.0])
        while len(out) >= 2 and out[-2][0] > out[-1][0]:
            v2, w2 = out.pop(); v1, w1 = out.pop()
            out.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2])
    res = []
    for val, wt in out:
        res.extend([val] * int(round(wt)))
    return np.array(res)

grid = np.concatenate([np.arange(0, 6.01, 0.25), np.arange(6.5, 16.1, 0.5)])
raw_curve, bws, effs = [], [], []
for x in grid:
    m_, bw_, eff_ = kernel_mean(x, E, v)
    raw_curve.append(m_); bws.append(bw_); effs.append(eff_)
raw_curve = np.array(raw_curve)
iso_curve = isotonic(raw_curve)

R0 = iso_curve[0]
Rtop = iso_curve[-1]
grade = np.clip((iso_curve - R0) / (Rtop - R0), 0, 1)
print('\n== fitted curve (E -> raw kernel mean v -> isotonic -> grade) ==')
print(f'R0 (E=0 plateau) = {R0:.4f} · Rtop (max-E plateau) = {Rtop:.4f}')
for i, x in enumerate(grid):
    if x <= 6 or x % 1 < 0.01:
        print(f'  E={x:5.2f}  raw={raw_curve[i]:.4f}  iso={iso_curve[i]:.4f}  grade={grade[i]:.4f}  (bw {bws[i]:.2f}, eff {effs[i]:.0f})')

# robustness: same pipeline on surv and raw rr
for nm, ys in [('surv', sv), ('rr', rr)]:
    rc = np.array([kernel_mean(x, E, ys)[0] for x in grid])
    ic = isotonic(rc)
    gr = np.clip((ic - ic[0]) / (ic[-1] - ic[0]), 0, 1)
    half = grid[np.argmax(gr >= 0.5)]
    print(f'robustness [{nm}]: R0={ic[0]:.3f} Rtop={ic[-1]:.3f} grade half-point E={half:.2f} '
          f'grade@1={gr[grid == 1.0][0]:.2f} @2={gr[grid == 2.0][0]:.2f} @3={gr[grid == 3.0][0]:.2f} '
          f'@4={gr[grid == 4.0][0]:.2f} @6={gr[grid == 6.0][0]:.2f} @13={gr[np.argmin(abs(grid - 13))]:.2f}')
half = grid[np.argmax(grade >= 0.5)]
print(f'primary [v]: grade half-point E={half:.2f} '
      f'grade@1={grade[grid == 1.0][0]:.2f} @2={grade[grid == 2.0][0]:.2f} @3={grade[grid == 3.0][0]:.2f} '
      f'@4={grade[grid == 4.0][0]:.2f} @5={grade[grid == 5.0][0]:.2f} @6={grade[grid == 6.0][0]:.2f} '
      f'@8={grade[np.argmin(abs(grid - 8))]:.2f} @13={grade[np.argmin(abs(grid - 13))]:.2f}')

json.dump(dict(grid=[round(float(x), 3) for x in grid],
               raw=[round(float(x), 5) for x in raw_curve],
               iso=[round(float(x), 5) for x in iso_curve],
               grade=[round(float(x), 5) for x in grade],
               R0=float(R0), Rtop=float(Rtop),
               bw=[round(float(x), 2) for x in bws], eff=[round(float(x), 1) for x in effs]),
          open(sys.argv[2], 'w'), indent=0)
print('wrote', sys.argv[2], 'md5', hashlib.md5(open(sys.argv[2], 'rb').read()).hexdigest()[:8])
