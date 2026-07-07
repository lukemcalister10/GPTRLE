#!/usr/bin/env python3
# D13 BASELINE HARVEST (single engine load, v2.2 af1fc6aa) — pulls the raw material for ALL asks:
#   A) RUC LADDER (ASK1): every listed ruck -> V0, PVC, V0/PVC, ns, gY, board ev, age, pick; class median.
#   B) RETENTION CELLS (ASK3): sit-out cells (ns==0 through Y, listed at Y) + grad depth-1 boundary,
#      with V0 anchor, realized forward outcome O, r=O/V0, depth d, class, pick, dv, complete-window flag.
#   C) V0 INVERSION CELLS (ASK2): every real store player w/ recorded pick -> pos, draftage, draftyr,
#      recorded pick, effpk, V0 (recorded-vs-effective divergence flagged).
#   D) ANCHORS (ASK3/5): named-player board values.
#   E) FLOOR state (ASK1/5): which real ND players sit at the floor; RUC floor-saves.
# CONVENTIONS carried verbatim from session_2026-07-03/scripts/d10_p1_harvest.py.
import os, sys, io, json, hashlib, contextlib
from collections import Counter, defaultdict
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
ev, raw_ev, iso_corr, draftval = G['ev'], G['raw_ev'], G['iso_corr'], G['draftval']
v0_start, nseas, nseas_pro, price6 = G['v0_start'], G['nseas'], G['nseas_pro'], G['price6']
era, REF, delisted, _sitout_cls = G['era'], G['REF'], G['delisted'], G['_sitout_cls']
FLOOR_YRS, FLOOR_TAIL = G['FLOOR_YRS'], G['FLOOR_TAIL']
floor_frac, ev_prefloor = G['floor_frac'], G['ev_prefloor']
_REAL = G['_REAL']
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # session_2026-07-03/d13

def draftyr(p): return cp.debutyr(p) - 1
def gY(p, Y): return sum(x['games'] for x in p['scoring'] if x['year'] == Y)
def age_at(p, Y):
    with contextlib.redirect_stdout(io.StringIO()):
        return cp._age_asof(p, Y)

# ---------------- A) RUC LADDER ----------------
rucks = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or MA.gfut(p) != 'RUC': continue
        if delisted(p): continue
        v0 = v0_start(p); pvc = draftval(p)
        rucks.append(dict(
            key=f"{p['player']}|{p.get('year')}|{p.get('pick')}", player=p['player'],
            year=p.get('year'), pick=p.get('pick'), effpk=MA.effpk(p), type=p.get('type'),
            age=age_at(p, 2026), ns=nseas_pro(p, 2026), g26=gY(p, 2026),
            V0=round(v0, 1), PVC=round(pvc, 1), ratio=round(v0/pvc, 4) if pvc > 0 else None,
            board=ev(p), prefloor=ev_prefloor(p), floored=bool(ev(p) > ev_prefloor(p))))
import numpy as np
ruc_ratios = sorted(r['ratio'] for r in rucks if r['ratio'] is not None)
ruc_median = float(np.median(ruc_ratios)) if ruc_ratios else None

# ---------------- B) RETENTION CELLS (verbatim d10 harvest logic) ----------------
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
    if not fwd: return 0.0, 0.0
    L = max(x['avg'] * REF / era.get(x['year'], REF) for x in fwd)
    with contextlib.redirect_stdout(io.StringIO()):
        o = price6(p, [L] * 6, Y)
    return o, L

cells, grad = [], []
selection = defaultdict(lambda: dict(present=0, exit_after=0))  # per (cls,depth): present count, exits after this depth
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        if not (p.get('pick') or p.get('_ft')): continue
        dy = draftyr(p)
        if dy < 2003 or dy > 2024: continue
        lt = listed_through(p)
        rows = sorted(p['scoring'], key=lambda x: x['year'])
        pos = MA.gfut(p); cls = _sitout_cls(pos)
        for Y in range(dy + 1, min(lt, 2025) + 1):
            quals = [x for x in rows if x['games'] >= 6 and x['year'] <= Y]
            yrow = [x for x in rows if x['year'] == Y]
            g = yrow[0]['games'] if yrow else 0
            avgY = (yrow[0]['avg'] * REF / era.get(Y, REF)) if yrow else 0.0
            d = Y - dy
            base = dict(player=p['player'], key=f"{p['player']}|{p.get('year')}|{p.get('pick')}",
                        type=p.get('type'), pos=pos, cls=cls, pick=p.get('pick'),
                        effpk=MA.effpk(p), dy=dy, Y=Y, d=d, gY=g, avgY=round(avgY, 2),
                        dv=round(draftval(p), 1), wc=bool(Y <= 2021),
                        lt=lt, delist_next=bool(Y == lt and lt < 2026))
            if not quals:
                v0 = v0_start(p); O, L = outcomeO(p, Y)
                base.update(V0=round(v0, 1), O=round(O, 1), L=round(L, 2),
                            r=round(O / v0, 4) if v0 > 0 else 0.0)
                cells.append(base)
            elif d == 1 and len(quals) == 1 and quals[0]['year'] == Y and g <= 9:
                v0 = v0_start(p); O, L = outcomeO(p, Y)
                base.update(V0=round(v0, 1), O=round(O, 1), L=round(L, 2),
                            r=round(O / v0, 4) if v0 > 0 else 0.0)
                grad.append(base)

# ---------------- C) V0 INVERSION CELLS ----------------
v0cells = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        if id(p) not in _REAL: continue
        rec_pick = p.get('pick')
        if rec_pick is None: continue
        v0cells.append(dict(
            key=f"{p['player']}|{p.get('year')}|{p.get('pick')}", player=p['player'],
            pos=MA.gfut(p), year=p.get('year'), type=p.get('type'),
            rec_pick=rec_pick, effpk=MA.effpk(p),
            draftage=round(age_at(p, p.get('year') or draftyr(p)), 2),
            V0=round(v0_start(p), 2), board=ev(p),
            diverge=bool(abs((rec_pick or -1) - MA.effpk(p)) > 1e-6)))

# ---------------- D) ANCHORS ----------------
anchor_names = ['Emmett', 'Annable', 'Dylan Patterson', 'Taylor', 'Ison', 'Smillie',
                'Tsatas', 'Berry', 'Cumming', 'Robey', 'Gawn', 'Goad']
anchors = {}
with contextlib.redirect_stdout(io.StringIO()):
    for nm in anchor_names:
        for p in MA.data:
            if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos')) and not p.get('_double_count'):
                k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
                anchors[k] = dict(player=p['player'], pos=MA.gfut(p), pick=p.get('pick'),
                                  effpk=MA.effpk(p), year=p.get('year'), type=p.get('type'),
                                  ns=nseas_pro(p, 2026), g26=gY(p, 2026), cls=_sitout_cls(MA.gfut(p)),
                                  V0=round(v0_start(p), 1), PVC=round(draftval(p), 1),
                                  ratio=round(v0_start(p)/draftval(p), 4) if draftval(p) > 0 else None,
                                  board=ev(p), prefloor=ev_prefloor(p))

# ---------------- E) FLOOR STATE ----------------
floored = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if id(p) not in _REAL or p.get('type') != 'ND' or p.get('_retired') or p.get('_pickless') or delisted(p):
            continue
        v = ev_prefloor(p); yis = 2026 - int(p.get('year') or 0)
        if yis < 1: continue
        fl = floor_frac(yis) * v0_start(p)
        if v < fl:
            floored.append(dict(key=f"{p['player']}|{p.get('year')}|{p.get('pick')}", player=p['player'],
                                pos=MA.gfut(p), cls=_sitout_cls(MA.gfut(p)), yis=yis,
                                prefloor=v, floor=round(fl), board=ev(p)))

out = dict(engine=ENG, ruc_median_ratio=ruc_median, n_ruck=len(rucks), rucks=sorted(rucks, key=lambda r: (r['pick'] or 999)),
           n_cells=len(cells), n_grad=len(grad), cells=cells, grad=grad,
           n_v0cells=len(v0cells), v0cells=v0cells, anchors=anchors,
           n_floored=len(floored), floored=floored, REF=REF)
op = os.path.join(OUT, 'd13_baseline.json')
json.dump(out, open(op, 'w'), indent=0)
print(f'engine={ENG} (expect af1fc6aa)')
print(f'RUC: {len(rucks)} listed rucks, median V0/PVC={ruc_median:.4f}')
print(f'RETENTION: {len(cells)} sit-out cells ({sum(1 for c in cells if c["wc"])} complete-window), {len(grad)} grad depth-1')
wc = [c for c in cells if c['wc']]
print('  cells by cls (complete):', dict(Counter(c['cls'] for c in wc)))
print('  cells by depth (complete):', dict(sorted(Counter(c['d'] for c in wc).items())))
print(f'V0-CELLS: {len(v0cells)} real picked players, {sum(1 for c in v0cells if c["diverge"])} recorded!=effective')
print(f'FLOORED: {len(floored)} real ND at floor ({sum(1 for f in floored if f["cls"]=="RUC")} RUC)')
print('wrote', op, 'md5', hashlib.md5(open(op, 'rb').read()).hexdigest()[:8])
