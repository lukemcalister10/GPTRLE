#!/usr/bin/env python3
# D13 ASK1 verification — RUC prior cap ladder at rungs 1.1/1.3/1.5/1.73/2.0.
# For each rung: every listed ruck's V0 and V0/PVC, board ev, Emmett's board, RUC floor-saves.
# Proven-ruck safety check vs v2.2 baseline (must be byte-identical). Ratio-vs-pick scatter.
import os, sys, io, json, hashlib, contextlib
import numpy as np
from scipy.stats import spearmanr
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
MA, cp = G['MA'], G['cp']
ev, v0_start, draftval, delisted = G['ev'], G['v0_start'], G['draftval'], G['delisted']
nseas_pro, ev_prefloor, floor_frac = G['nseas_pro'], G['ev_prefloor'], G['floor_frac']
_REAL = G['_REAL']
base = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'd13_baseline.json')))
base_board = {r['key']: r['board'] for r in base['rucks']}

rucks = [p for p in MA.data if not p.get('_double_count') and MA.gfut(p) == 'RUC' and not delisted(p)]
def key(p): return f"{p['player']}|{p.get('year')}|{p.get('pick')}"
def emmett(): return next(p for p in MA.data if p['player'] == 'Louis Emmett')

RUNGS = [1.1, 1.3, 1.5, 1.73, 2.0]
print(f'engine={ENG} (expect the v2.3 candidate; default cap={G["RUC_PRIOR_CAP"]})')
print('\n=== RUC CAP LADDER: V0 / V0-PVC / board at each rung; Emmett board; RUC floor-saves ===')
ladder = {}
for rung in RUNGS:
    G['RUC_PRIOR_CAP'] = rung; G['_V0C'].clear()
    rows = []
    for p in rucks:
        with contextlib.redirect_stdout(io.StringIO()):
            v0 = v0_start(p); pvc = draftval(p); b = ev(p)
        rows.append(dict(key=key(p), player=p['player'], pick=(p.get('pick') or MA.effpk(p)),
                         ns=nseas_pro(p, 2026), V0=round(v0), ratio=round(v0/pvc, 3) if pvc else None, board=b))
    with contextlib.redirect_stdout(io.StringIO()):
        em = emmett(); emb = ev(em)
        fsaves = sum(1 for p in rucks if id(p) in _REAL and p.get('type') == 'ND' and not p.get('_retired')
                     and not delisted(p) and (2026-int(p.get('year') or 0)) >= 1
                     and ev_prefloor(p) < floor_frac(2026-int(p.get('year') or 0))*v0_start(p))
    ladder[rung] = dict(rows=rows, emmett=emb, floor_saves=fsaves)
    n_capped = sum(1 for r in rows if r['ratio'] is not None and r['ratio'] <= rung+1e-6 and r['ratio'] >= rung-0.02)
    print(f'  cap={rung:4.2f}: Emmett board={emb:5d}  RUC floor-saves={fsaves}  '
          f'rucks with ratio at/near cap={sum(1 for r in rows if r["ratio"] and abs(r["ratio"]-rung)<0.02)}')

# full ladder table for a few key rucks + Emmett
print('\n=== per-ruck V0/ratio/board across rungs (thin/prior-dominated rucks move; proven flat) ===')
print('%-22s %4s %3s | '%('player','pk','ns') + ' '.join('  cap%.2f(V0/rat/brd)'%r for r in RUNGS))
watch = ['Louis Emmett','Toby Conway','Harry Barnett','Aiden Riddle','Tristan Xerri','Brodie Grundy','Max Gawn','Rowan Marshall']
byname = {r['player']: {rung: next(x for x in ladder[rung]['rows'] if x['player']==r['player']) for rung in RUNGS} for r in ladder[RUNGS[0]]['rows'] if r['player'] in watch}
for nm in watch:
    if nm not in byname: continue
    r0 = byname[nm][RUNGS[0]]
    line = '%-22s %4s %3d | '%(nm[:22], r0['pick'], r0['ns'])
    for rung in RUNGS:
        x = byname[nm][rung]; line += ' %4d/%.2f/%4d'%(x['V0'], x['ratio'] or 0, x['board'])
    print(line)

# proven-ruck safety at default 1.73 vs v2.2 baseline
print('\n=== PROVEN-RUCK SAFETY at default 1.73 (board must == v2.2 baseline, cap binds thin only) ===')
G['RUC_PRIOR_CAP'] = 1.73; G['_V0C'].clear()
proven = [p for p in rucks if nseas_pro(p, 2026) >= 4]
nmoved = 0
for p in proven:
    with contextlib.redirect_stdout(io.StringIO()): b = ev(p)
    bb = base_board.get(key(p))
    if bb is not None and b != bb:
        nmoved += 1; print(f'  MOVED: {p["player"]:22s} {bb} -> {b}')
print(f'  proven rucks (ns>=4): {len(proven)}, moved from baseline: {nmoved}')

# ratio-vs-pick scatter (ND rucks, baseline uncapped ratios)
ndr = [r for r in base['rucks'] if r['type'] == 'ND' and r['ratio'] and r['pick']]
rho, pval = spearmanr([r['pick'] for r in ndr], [r['ratio'] for r in ndr])
print('\n=== RATIO-vs-PICK scatter (ND rucks, n=%d): Spearman rho=%.3f p=%.3f ===' % (len(ndr), rho, pval))
print('  patterned by pick?' , 'weak/none — scattered' if abs(rho) < 0.3 or pval > 0.05 else 'patterned')

json.dump(dict(engine=ENG, rungs=RUNGS, ladder={str(k): v for k, v in ladder.items()},
               proven_moved=nmoved, scatter_rho=float(rho), scatter_p=float(pval),
               ruc_nd_median=float(np.median([r['ratio'] for r in ndr]))),
          open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'd13_ask1_ladder.json'), 'w'), indent=0)
print('\nwrote d13_ask1_ladder.json')
