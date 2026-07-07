#!/usr/bin/env python3
# D8 ASK 2a — FINAL FIT of the graded staleness-cap curves (no engine load) + offline anchor test.
# Axis: q = era-adjusted season-Y avg / REPL[gfut] (selected by data: player-cluster bootstrap,
# tau(q,v)=+0.234 beats E=g*q +0.124 in 100% of resamples; games carries no independent signal).
# Gap classes: gap=1 vs gap>=2 (POOLED DELIBERATELY: gap 3/4/5+ singly thin at n=29/11/4).
# Absence rule: gY==0 -> grade 0 (ghost anchor; the measured elevated returner realization is the
# LTI channel, declared + queued). gap==0 -> cap exempt (Form A structural piece, Luke-endorsed).
# Smoothing: Gaussian kernel, bandwidth widened until eff-n >= 35 (D5 standing rule) + isotonic (PAVA).
# Two normalization variants computed for the anchor test:
#   V-FIXED : grade_c(q) = clip((R_c(q) - Rg) / (Rtop   - Rg), 0, 1), Rtop = gap-0 top plateau
#   V-QMATCH: grade_c(q) = clip((R_c(q) - Rg) / (R_0(q) - Rg), 0, 1), q-matched live reference
# Rg = R_{2+}(q->0+) (the true-ghost baseline: lowest realization plateau, gap>=2 minimal live output).
import json, sys, hashlib
import numpy as np

d = json.load(open(sys.argv[1]))
meta = d['meta']
cells = [c for c in d['cells'] if c['window_complete']]

def curve(cs, xkey='q', ykey='v', grid=None, min_eff=35.0):
    xs = np.array([c[xkey] for c in cs]); ys = np.array([c[ykey] for c in cs])
    raw, bws, effs = [], [], []
    for x in grid:
        bw = 0.05
        while True:
            w = np.exp(-0.5 * ((xs - x) / bw) ** 2)
            eff = float(w.sum())
            if eff >= min_eff or bw >= 2.0:
                break
            bw += 0.05
        raw.append(float((w * ys).sum() / w.sum())); bws.append(bw); effs.append(eff)
    # PAVA isotonic (level, weight)
    out = []
    for val in raw:
        out.append([val, 1.0])
        while len(out) >= 2 and out[-2][0] > out[-1][0]:
            v2, w2 = out.pop(); v1, w1 = out.pop()
            out.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2])
    iso = []
    for val, wt in out:
        iso.extend([val] * int(round(wt)))
    return np.array(raw), np.array(iso), bws, effs

GRID = np.round(np.arange(0.0, 1.61, 0.05), 3)
g1 = [c for c in cells if c['gap'] == 1 and c['gY'] >= 1]
g2 = [c for c in cells if c['gap'] >= 2 and c['gY'] >= 1]
g0 = [c for c in cells if c['gap'] == 0]
print(f'fit populations: gap=1 n={len(g1)} (uniq {len({c["key"] for c in g1})}) · '
      f'gap>=2 pooled n={len(g2)} (uniq {len({c["key"] for c in g2})}) · gap=0 n={len(g0)}')
raw1, R1, bw1, ef1 = curve(g1, grid=GRID)
raw2, R2, bw2, ef2 = curve(g2, grid=GRID)
raw0, R0c, bw0, ef0 = curve(g0, grid=GRID)
Rg = float(R2[0])
Rtop = float(R0c[-1])
print(f'Rg (true-ghost baseline, R2+ at q->0+) = {Rg:.4f} · Rtop (gap-0 top plateau) = {Rtop:.4f}')
print(f'R1 low plateau = {R1[0]:.4f} · R1 @q=1.0 = {R1[GRID == 1.0][0]:.4f} · '
      f'R2 @q=1.0 = {R2[GRID == 1.0][0]:.4f} · R0 low plateau = {R0c[0]:.4f}')
print('\n q     R1     R2     R0    | gFIX1 gFIX2 | gQM1  gQM2   (bw1/eff1)')
gF1 = np.clip((R1 - Rg) / (Rtop - Rg), 0, 1); gF2 = np.clip((R2 - Rg) / (Rtop - Rg), 0, 1)
gQ1 = np.clip((R1 - Rg) / np.maximum(R0c - Rg, 1e-9), 0, 1)
gQ2 = np.clip((R2 - Rg) / np.maximum(R0c - Rg, 1e-9), 0, 1)
for i, x in enumerate(GRID):
    if round(x * 100) % 10 == 0:
        print(f'{x:4.2f}  {R1[i]:.3f}  {R2[i]:.3f}  {R0c[i]:.3f} | {gF1[i]:.3f} {gF2[i]:.3f} | '
              f'{gQ1[i]:.3f} {gQ2[i]:.3f}   ({bw1[i]:.2f}/{ef1[i]:.0f})')

# ---- offline anchor test on the D7 population (both variants) ----
pop = json.load(open(sys.argv[2]))['rows']
era = {int(k): v for k, v in meta['era'].items()}
REF = meta['REF']
adj26 = REF / era.get(2026, REF)
print(f'\nera-adj 2026 factor = {adj26:.4f}')

def grade_of(r, variant):
    if r['gap'] == 0: return 1.0
    if not r['g26'] or not r['avg26']: return 0.0
    q = (r['avg26'] * adj26) / r['repl']
    G1, G2 = (gF1, gF2) if variant == 'FIX' else (gQ1, gQ2)
    G = G1 if r['gap'] == 1 else G2
    return float(np.interp(q, GRID, G))

print(f"\n{'player':26s} {'gap':>3s} {'g26':>3s} {'q26':>5s} {'capped':>7s} {'uncap':>7s} {'FIX':>6s} {'QM':>6s}")
for r in sorted(pop, key=lambda r: (r['gap'], -r['uncapped'])):
    q26 = (r['avg26'] * adj26) / r['repl'] if (r['g26'] and r['avg26']) else 0.0
    vals = {}
    for var in ('FIX', 'QM'):
        g = grade_of(r, var)
        cap = min(r['uncapped'], r['cap_value'])
        vals[var] = r['uncapped'] if r['gap'] == 0 else min(r['uncapped'], cap + g * max(0.0, r['uncapped'] - cap))
    print(f"{r['player'][:26]:26s} {r['gap']:3d} {r['g26']:3d} {q26:5.2f} {r['capped_ev']:7.0f} "
          f"{r['uncapped']:7.0f} {vals['FIX']:6.0f} {vals['QM']:6.0f}")

json.dump(dict(grid=[float(x) for x in GRID],
               R1=[round(float(x), 5) for x in R1], R2=[round(float(x), 5) for x in R2],
               R0=[round(float(x), 5) for x in R0c], Rg=Rg, Rtop=Rtop,
               gFIX1=[round(float(x), 5) for x in gF1], gFIX2=[round(float(x), 5) for x in gF2],
               gQM1=[round(float(x), 5) for x in gQ1], gQM2=[round(float(x), 5) for x in gQ2],
               raw1=[round(float(x), 5) for x in raw1], raw2=[round(float(x), 5) for x in raw2],
               raw0=[round(float(x), 5) for x in raw0],
               bw1=bw1, eff1=[round(e, 1) for e in ef1], bw2=bw2, eff2=[round(e, 1) for e in ef2],
               adj26=adj26),
          open(sys.argv[3], 'w'), indent=0)
print('\nwrote', sys.argv[3], 'md5', hashlib.md5(open(sys.argv[3], 'rb').read()).hexdigest()[:8])
