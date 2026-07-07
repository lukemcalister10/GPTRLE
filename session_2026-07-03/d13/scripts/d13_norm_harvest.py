#!/usr/bin/env python3
# D13 NORM HARVEST (single engine load, v2.2) — every STILL-LISTED draftee cell (2003-2024) at each depth,
# regardless of qualifying status, so the same-depth all-draftee NORM (developer-inclusive) can be built
# alongside the sit-out subset. This is the D10 "0.76 daEV form" denominator, re-harvested for the D13
# continuous log-pick x depth re-derivation. Per cell: pick, cls, depth, sitout-flag, V0, O, dv, wc.
import os, sys, io, json, hashlib, contextlib
from collections import Counter
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
MA, cp, PR = G['MA'], G['cp'], G['PR']
raw_ev, iso_corr, draftval = G['raw_ev'], G['iso_corr'], G['draftval']
v0_start, price6, era, REF, _sitout_cls = G['v0_start'], G['price6'], G['era'], G['REF'], G['_sitout_cls']
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
def outcomeO(p, Y):
    fwd = [x for x in p['scoring'] if x['games'] >= 6 and Y < x['year'] <= Y + 4]
    if not fwd: return 0.0
    L = max(x['avg'] * REF / era.get(x['year'], REF) for x in fwd)
    with contextlib.redirect_stdout(io.StringIO()):
        return price6(p, [L] * 6, Y)

allcells = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        if not (p.get('pick') or p.get('_ft')): continue
        dy = draftyr(p)
        if dy < 2003 or dy > 2024: continue
        lt = listed_through(p)
        rows = sorted(p['scoring'], key=lambda x: x['year'])
        pos = MA.gfut(p); cls = _sitout_cls(pos)
        v0 = v0_start(p); dv = draftval(p)
        for Y in range(dy + 1, min(lt, 2025) + 1):
            quals = [x for x in rows if x['games'] >= 6 and x['year'] <= Y]
            d = Y - dy
            O = outcomeO(p, Y)
            allcells.append(dict(key=f"{p['player']}|{p.get('year')}|{p.get('pick')}",
                                 cls=cls, pos=pos, pick=(p.get('pick') or MA.effpk(p)),
                                 effpk=MA.effpk(p), d=d, sitout=bool(not quals),
                                 V0=round(v0, 2), O=round(O, 2), dv=round(dv, 2),
                                 wc=bool(Y <= 2021)))
out = dict(engine=ENG, n=len(allcells), cells=allcells)
op = os.path.join(OUT, 'd13_normcells.json')
json.dump(out, open(op, 'w'), indent=0)
wc = [c for c in allcells if c['wc']]
print(f'engine={ENG} (expect af1fc6aa)')
print(f'ALL still-listed cells: {len(allcells)} ({len(wc)} complete-window)')
print('  sitout share (complete):', sum(1 for c in wc if c['sitout']), '/', len(wc))
print('  by depth (complete, all):', dict(sorted(Counter(c['d'] for c in wc).items())))
print('  norm E[O/V0] by depth (complete, all still-listed):')
import numpy as np
for depth in range(1, 8):
    v = [min(c['O']/max(1e-9, c['V0']), 2.0) for c in wc if c['d'] == depth]
    if v: print('    d%d: norm=%.3f (n=%d)' % (depth, np.mean(v), len(v)))
print('wrote', op, 'md5', hashlib.md5(open(op, 'rb').read()).hexdigest()[:8])
