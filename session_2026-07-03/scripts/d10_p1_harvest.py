#!/usr/bin/env python3
# GAMES-RAMP D10 phase 1 — ONE ENGINE LOAD (scratch deploy, v2 pair 4a134d05/5ac8b162):
#  (a) smoke: reproduce v2 anchor values (Annable 936 / Patterson 982 / Taylor 690 / Cumming 1982)
#  (b) live start values V0 = raw_ev(p, draft year) * iso  — the pick+position-adjusted assignment;
#      verify the Dean-below / Robey-above property vs PVC pick values
#  (c) B6 ramp at v2 (gate-identical synth) — locate the dips/jackpot precisely
#  (d) HARVEST historical sit-out cells (ns==0 through Y, listed at Y) with V0 anchor + realized
#      forward outcome O (price6 of realized best qualifying level in Y+1..Y+4, era-adj to REF; busts=0)
#      + the graduated boundary population (depth-1, 6..9 games) for the lambda endpoint.
# CONVENTIONS: LISTED-WINDOW rule (D8); era-adjust to REF (bestlvl convention); WQ6/price6 ruler.
import os, sys, io, json, hashlib, contextlib
SC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RA = os.path.join(SC, 'deploy', 'rl_after')
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, os.path.join(SC, 'deploy', 'forward_valuation'), '/home/claude/rl_vendor']
os.chdir(RA)
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
MA, PR, cp, dp, era, REF = G['MA'], G['PR'], G['cp'], G['dp'], G['era'], G['REF']
ev, raw_ev, iso_corr, draftval, nseas, price6, b6 = (G['ev'], G['raw_ev'], G['iso_corr'],
    G['draftval'], G['nseas'], G['price6'], G['b6'])
GRPPOS = G['GRPPOS']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
print(f'engine={ENG} (expect 4a134d05)')

def findp(nm, year=None, pick=None):
    cs = [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))
          and not p.get('_double_count')]
    if year is not None: cs = [p for p in cs if p.get('year') == year]
    if pick is not None: cs = [p for p in cs if p.get('pick') == pick]
    return cs

# ---------- (a) smoke ----------
print('\n== (a) v2 smoke (expect Annable 936 / Patterson 982 / Cumming 1982) ==')
anchors = [('Annable', 2025, None), ('Dylan Patterson', 2025, None), ('Taylor', 2025, None),
           ('Sam Cumming', 2025, None), ('Emmett', None, None), ('Ison', None, None),
           ('Cooper Lord', None, None), ('Travaglia', None, None), ('Angus Clarke', None, None),
           ('Jacob Farrow', None, None), ('Harry Dean', None, None), ('Sullivan Robey', None, None)]
with contextlib.redirect_stdout(io.StringIO()):
    A = {}
    for nm, yr, pk in anchors:
        for p in findp(nm, yr, pk):
            k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
            A[k] = dict(v2=ev(p, 2026), dv=round(draftval(p)), pos=MA.gfut(p), type=p.get('type'),
                        ns=nseas(p, 2026), ten=PR.tenure(p, 2026),
                        g26=sum(x['games'] for x in p['scoring'] if x['year'] == 2026),
                        avg26=next((x['avg'] for x in p['scoring'] if x['year'] == 2026), None))
for k, d in sorted(A.items()):
    print(f"  {k:38s} pos={d['pos']:8s} type={d['type']} ns={d['ns']} ten={d['ten']} g26={d['g26']} "
          f"avg26={d['avg26']} dv={d['dv']} v2={d['v2']}")

# ---------- (b) live start values ----------
print('\n== (b) V0 = raw_ev(p, draftyr)*iso vs PVC pick value ==')
def draftyr(p): return cp.debutyr(p) - 1
V0C = {}
def V0(p):
    k = id(p)
    if k not in V0C:
        with contextlib.redirect_stdout(io.StringIO()):
            V0C[k] = raw_ev(p, draftyr(p)) * iso_corr(MA.gfut(p), MA.effpk(p))
    return V0C[k]
for k in sorted(A):
    nm, yr, pk = k.rsplit('|', 2)
    p = findp(nm, int(yr), None)
    p = [q for q in p if str(q.get('pick')) == pk][0]
    print(f"  {k:38s} pos={MA.gfut(p):8s} PVC[pick]={draftval(p):6.0f}  V0={V0(p):7.1f}  "
          f"V0/PVC={V0(p)/draftval(p):.3f}")

# ---------- (c) B6 ramp at v2 ----------
print('\n== (c) B6 ramp at v2 (MID pk10 yr2025, avg 85, games 0..14) ==')
def ramp_p(gm):
    return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025,
            'dob': '2006-03-01', 'type': 'ND',
            'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []),
            'games': gm, '_pos_now': None, '_fut': []}
with contextlib.redirect_stdout(io.StringIO()):
    vals = [float(ev(ramp_p(gm), 2026)) for gm in range(0, 15)]
print('  ramp:', [round(v) for v in vals])
print('  steps:', [round(vals[i+1]-vals[i]) for i in range(14)])

# ---------- (d) harvest ----------
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
    """price6 value at Y of realized best qualifying level in (Y, Y+4]; era-adj to REF; none -> 0"""
    fwd = [x for x in p['scoring'] if x['games'] >= 6 and Y < x['year'] <= Y + 4]
    if not fwd: return 0.0, 0.0
    L = max(x['avg'] * REF / era.get(x['year'], REF) for x in fwd)
    with contextlib.redirect_stdout(io.StringIO()):
        o = price6(p, [L] * 6, Y)
    return o, L

cells, grad = [], []
CLS = G['_sitout_cls']
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        if not (p.get('pick') or p.get('_ft')): continue
        dy = draftyr(p)
        if dy < 2003 or dy > 2024: continue
        lt = listed_through(p)
        rows = sorted(p['scoring'], key=lambda x: x['year'])
        pos = MA.gfut(p); cls = CLS(pos)
        for Y in range(dy + 1, min(lt, 2025) + 1):
            quals = [x for x in rows if x['games'] >= 6 and x['year'] <= Y]
            yrow = [x for x in rows if x['year'] == Y]
            gY = yrow[0]['games'] if yrow else 0
            avgY = (yrow[0]['avg'] * REF / era.get(Y, REF)) if yrow else 0.0
            d = Y - dy
            base = dict(player=p['player'], key=f"{p['player']}|{p.get('year')}|{p.get('pick')}",
                        type=p.get('type'), pos=pos, cls=cls, pick=p.get('pick'), dy=dy, Y=Y,
                        d=d, gY=gY, avgY=round(avgY, 2),
                        q=round(avgY / max(1.0, MA.REPL.get(pos, 1.0)), 4),
                        dv=round(draftval(p), 1), wc=bool(Y <= 2021))
            if not quals:
                v0 = V0(p); O, L = outcomeO(p, Y)
                base.update(V0=round(v0, 1), O=round(O, 1), L=round(L, 2),
                            r=round(O / v0, 4) if v0 > 0 else 0.0)
                cells.append(base)
            elif d == 1 and len(quals) == 1 and quals[0]['year'] == Y and gY <= 9:
                v0 = V0(p); O, L = outcomeO(p, Y)
                base.update(V0=round(v0, 1), O=round(O, 1), L=round(L, 2),
                            r=round(O / v0, 4) if v0 > 0 else 0.0)
                grad.append(base)

out = dict(engine=ENG, anchors=A, ramp=vals, n_cells=len(cells), n_grad=len(grad),
           REPL=dict(MA.REPL), REF=REF, cells=cells, grad=grad)
op = os.path.join(SC, 'p1_harvest.json')
json.dump(out, open(op, 'w'), indent=0)
from collections import Counter
wc = [c for c in cells if c['wc']]
print(f'\n== (d) harvest: {len(cells)} sit-out cells ({len(wc)} complete-window Y<=2021), '
      f'{len(grad)} graduated depth-1 boundary cells ==')
print('  by depth (complete):', dict(sorted(Counter(c['d'] for c in wc).items())))
print('  depth-1 by gY (complete):', dict(sorted(Counter(c['gY'] for c in wc if c['d'] == 1).items())))
print('  by cls (complete):', dict(Counter(c['cls'] for c in wc)))
print('wrote', op, 'md5', hashlib.md5(open(op, 'rb').read()).hexdigest()[:8])
