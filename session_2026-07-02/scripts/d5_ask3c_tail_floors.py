#!/usr/bin/env python3
# D5 ASK 3c — yr8+ tail floors under Luke's generating rule: floor_d = 0.9 x smoothed clean p5 (ND-only),
# d = 8, 9, 10, 11+. Standing statistics instruction honoured: finest resolution the sample supports with
# smoothing on the continuous depth axis (Gaussian-kernel weighted 5th percentile; bandwidth widened per
# depth until effective n >= 35 — the rule is stated, not tuned); the 11+ slice is POOLED DELIBERATELY
# (n per single depth runs 30 -> 1 by d=21; a kernel there would just be a noisy pool). NUMBERS ONLY —
# the schedule amendment waits for Luke's word.
import json, sys, hashlib
import numpy as np

SCRATCH = sys.argv[1]
d = json.load(open(SCRATCH + '/meas_head.json'))
rows = d['clean_rows']                      # ND-only, listed, picked, at head 8aed420a
dep = np.array([r['yis'] for r in rows], float)
rat = np.array([r['ratio'] for r in rows], float)

def wquant(vals, w, q):
    i = np.argsort(vals)
    v, w = vals[i], w[i]
    cw = np.cumsum(w) - 0.5 * w
    cw /= np.sum(w)
    return float(np.interp(q, cw, v))

def smoothed_p5(target, min_eff=35.0):
    bw = 0.75
    while True:
        w = np.exp(-0.5 * ((dep - target) / bw) ** 2)
        eff = float(np.sum(w))
        if eff >= min_eff or bw >= 3.0:
            return wquant(rat, w, 0.05), bw, eff
        bw += 0.25

CUR = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}   # signed schedule; 7+ flat .05
L = []
L.append('# D5 ASK 3c — yr8+ tail floors from the generating rule (0.9 x smoothed clean p5, ND-only)')
L.append('_Basis: head `8aed420a` store `644d1254`, ND-only LISTED picked (n=590; B5 population). Smoothing: '
         'Gaussian kernel over years-in-system, weighted 5th percentile; bandwidth widened per depth until '
         'effective n >= 35 (rule stated up front, not tuned). The 11+ slice is POOLED DELIBERATELY (single-depth '
         "n runs 30 at d=11 down to 1 at d=21). NUMBERS ONLY — no schedule change without Luke's word._")
L.append('')
L.append('| depth d | n at d | raw clean p5 | smoothed clean p5 (bw / eff-n) | derived floor 0.9xp5 | current floor |')
L.append('|---|---|---|---|---|---|')
per = {}
for r in rows:
    per.setdefault(r['yis'], []).append(r['ratio'])
for t in range(1, 11):
    sp5, bw, eff = smoothed_p5(t)
    raw = float(np.percentile(per[t], 5)) if t in per else float('nan')
    cur = CUR.get(t, 0.05)
    L.append(f'| {t} | {len(per.get(t, []))} | {raw:.3f} | {sp5:.3f} (bw {bw:.2f} / eff {eff:.0f}) | '
             f'**{0.9 * sp5:.3f}** | {cur:.2f} |')
pool = [r['ratio'] for r in rows if r['yis'] >= 11]
p5p = float(np.percentile(pool, 5))
L.append(f'| 11+ (POOLED deliberately) | {len(pool)} | {p5p:.3f} | {p5p:.3f} (pooled, no kernel) | '
         f'**{0.9 * p5p:.3f}** | 0.05 |')
L.append('')
L.append('Notes: (i) depths 1-6 shown for continuity with the signed dev-window schedule (derived from the same '
         "generating rule at D3/D4); (ii) the signed schedule's 7+ flat .05 vs the derived tail: the generating "
         'rule gives materially LOWER floors from d=8 on — the .05-forever tail binds beyond its generating data; '
         '(iii) 11+ pooled composition is dominated by d=11-13 (75/120 rows) — the pooled p5 leans on the younger '
         'end of the bucket; (iv) raw vs smoothed at thin depths (d>=9) differ exactly where smoothing is doing '
         'its declared job.')
out = '/home/user/afl-rl-engine/session_2026-07-02/d5_ask3c_tail_floors.md'
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
print('wrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
