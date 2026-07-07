#!/usr/bin/env python3
# D5 ASK 2(b) — the discriminating test: is the candidate's 2020-cohort markdown CONCENTRATED on the
# cohort's mediocre members (mediocrity-compression — consistent with Luke's shocking-draft read) or
# INDISCRIMINATE across the cohort (exposure/recency-style artifact)?
# Matrix-only (candidate vs same-builder control); join on (player, year, type, pick) — ids differ per run.
import json, sys, hashlib
import numpy as np

SCRATCH = sys.argv[1]
CTRL = '/home/user/afl-rl-engine/data/s4_matrix_control_8aed420a.json'
CAND = SCRATCH + '/s4_matrix_candidate_fb39d88a.json'

def load(mp):
    mat = json.load(open(mp))
    out = {}
    for v in mat.values():
        if not v['incurve'] or int(v['year']) != 2020:
            continue
        k = (v['player'], v['year'], v['type'], round(float(v['pick']), 1))
        out[k] = v
    return out

ctrl, cand = load(CTRL), load(CAND)
assert set(ctrl) == set(cand), f'population mismatch: {len(ctrl)} vs {len(cand)}'

# depths 4-6 = calendar 2024/2025/2026 for cohort 2020 (indices 3,4,5 of yrs C+1..)
rows = []
for k in ctrl:
    c, d = ctrl[k], cand[k]
    def dsum(v):
        vp = v['Vpath']
        return sum(float(vp[i] or 0.0) for i in (3, 4, 5) if i < len(vp))
    cv, dv_ = dsum(c), dsum(d)
    rows.append(dict(player=k[0], pick=k[3], ctrl=cv, cand=dv_, delta=dv_ - cv,
                     pct=(100.0 * (dv_ - cv) / cv) if cv > 0 else None,
                     yr1=float(c['Vpath'][0] or 0.0)))
rows.sort(key=lambda r: -r['ctrl'])
tot_ctrl = sum(r['ctrl'] for r in rows)
tot_delta = sum(r['delta'] for r in rows)

n = len(rows)
q = max(1, n // 4)
top_q, mid, bot = rows[:q], rows[q:n - n // 2], rows[n - n // 2:]
def blk(rs, name):
    c = sum(r['ctrl'] for r in rs); d = sum(r['delta'] for r in rs)
    return dict(name=name, n=len(rs), ctrl=c, delta=d,
                pct=100.0 * d / c if c else 0.0,
                share=100.0 * d / tot_delta if tot_delta else 0.0)
blocks = [blk(top_q, f'top quartile by control value (n={len(top_q)})'),
          blk(mid, f'middle (n={len(mid)})'),
          blk(bot, f'bottom half by control value (n={len(bot)})')]

# rank correlation: control value vs relative markdown (players with ctrl>0)
sub = [r for r in rows if r['ctrl'] > 0 and r['pct'] is not None]
from scipy.stats import spearmanr
rho, pval = spearmanr([r['ctrl'] for r in sub], [r['pct'] for r in sub])

L = []
L.append('# D5 ASK 2(b) — 2020-cohort markdown concentration (candidate vs same-builder control, depths 4-6)')
L.append(f'_Cohort 2020 incurve n={n}; total ctrl d4-6 value={tot_ctrl:.0f}; total markdown={tot_delta:+.0f} '
         f'({100.0 * tot_delta / tot_ctrl:+.1f}%)._')
L.append('')
L.append('## Concentration blocks (sorted by control value)')
L.append('| block | n | ctrl d4-6 value | markdown | markdown % of own value | share of total markdown |')
L.append('|---|---|---|---|---|---|')
for b in blocks:
    L.append(f"| {b['name']} | {b['n']} | {b['ctrl']:.0f} | {b['delta']:+.0f} | {b['pct']:+.1f}% | {b['share']:.0f}% |")
L.append('')
L.append(f'Spearman(control value, markdown %) = {rho:+.3f} (p={pval:.2g}, n={len(sub)}) — negative = markdown '
         'grows with value (hits producers); positive = markdown concentrates down the value order (hits mediocrity).')
L.append('')
L.append('## Per-player rows (all cohort members with any d4-6 value, sorted by control value)')
L.append('| player | pick | ctrl d4-6 | cand d4-6 | Δ | Δ% |')
L.append('|---|---|---|---|---|---|')
for r in rows:
    if r['ctrl'] <= 0 and r['cand'] <= 0:
        continue
    pc = f"{r['pct']:+.1f}%" if r['pct'] is not None else '—'
    L.append(f"| {r['player']} | {r['pick']:.0f} | {r['ctrl']:.0f} | {r['cand']:.0f} | {r['delta']:+.0f} | {pc} |")

out = '/home/user/afl-rl-engine/session_2026-07-02/d5_ask2_2020_concentration.md'
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:16]))
print('...')
print('wrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
