#!/usr/bin/env python3
# GAMES-RAMP D10 phase 3 — the NORM baseline b0 (one engine load, scratch v2 deploy):
# r0 = O(p, draft-year)/V0(p) for ALL draftees (busts=0, window dy+1..dy+4) — the from-draft
# realization ratio of the whole population, per class. This is the denominator that re-expresses
# sit-out retention RELATIVE to normal development (the daEV-convention "0.76 form", locked estimator
# family: still-listed conditioning, busts=0). Also: per-depth norms for robustness.
import os, sys, io, json, hashlib, contextlib
import numpy as np
SC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RA = os.path.join(SC, 'deploy', 'rl_after')
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, os.path.join(SC, 'deploy', 'forward_valuation'), '/home/claude/rl_vendor']
os.chdir(RA)
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
MA, PR, cp, era, REF = G['MA'], G['PR'], G['cp'], G['era'], G['REF']
raw_ev, iso_corr, price6, draftval = G['raw_ev'], G['iso_corr'], G['price6'], G['draftval']
CLS = G['_sitout_cls']
print('engine', hashlib.md5(open('_merged_recover.py','rb').read()).hexdigest()[:8])

def draftyr(p): return cp.debutyr(p) - 1
def min_window(p):
    t, pk = p.get('type'), p.get('pick')
    if t == 'ND' and pk and pk <= 20: return 4
    if t == 'ND' and pk and pk <= 40: return 3
    return 2
def listed_through(p):
    if p.get('_last_listed') is not None: return int(p['_last_listed'])
    if not p.get('_retired'): return 2026
    lg = max((x['year'] for x in p['scoring']), default=0)
    dy = p.get('year') or lg
    return max(dy + min_window(p) - 1, lg)
def outcome_r(p, Y, v0):
    fwd = [x for x in p['scoring'] if x['games'] >= 6 and Y < x['year'] <= Y + 4]
    if not fwd: return 0.0
    L = max(x['avg'] * REF / era.get(x['year'], REF) for x in fwd)
    with contextlib.redirect_stdout(io.StringIO()):
        return min(price6(p, [L] * 6, Y) / v0, 2.0) if v0 > 0 else 0.0

b0 = {c: [] for c in ('nonKPP', 'KPP', 'RUC')}
nd = {c: {d: [] for d in range(1, 7)} for c in ('nonKPP', 'KPP', 'RUC')}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        if not (p.get('pick') or p.get('_ft')): continue
        dy = draftyr(p)
        if dy < 2003 or dy > 2021: continue
        cls = CLS(MA.gfut(p))
        v0 = raw_ev(p, dy) * iso_corr(MA.gfut(p), MA.effpk(p))
        b0[cls].append(outcome_r(p, dy, v0))
        lt = listed_through(p)
        for d in range(1, 7):
            Y = dy + d
            if Y > min(lt, 2021): continue
            nd[cls][d].append(outcome_r(p, Y, v0))
print('\nb0 (from-draft realization ratio, ALL draftees dy 2003-2021, busts=0, winsor 2.0):')
for c in b0:
    a = np.array(b0[c]); print(f'  {c:7s} mean={a.mean():.4f} median={np.median(a):.3f} n={len(a)}')
print('\nper-depth norm E[r | all still-listed at depth d] (robustness view):')
for c in nd:
    print(f'  {c:7s} ' + ' '.join(f"d{d}:{np.mean(v):.3f}(n{len(v)})" for d, v in sorted(nd[c].items()) if v))
json.dump({c: dict(mean=float(np.mean(v)), n=len(v)) for c, v in b0.items()},
          open(os.path.join(SC, 'p3_b0.json'), 'w'), indent=1)
print('wrote p3_b0.json')
