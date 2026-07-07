#!/usr/bin/env python3
# GAMES-RAMP D10 phase 6 — ramp COMPONENT PROBE + anchor/census re-run after nqual re-scoping.
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
MA, PR, cp = G['MA'], G['PR'], G['cp']
ev, raw_ev, iso_corr = G['ev'], G['raw_ev'], G['iso_corr']
v0_start, nseas, nseas_pro, GRPPOS = G['v0_start'], G['nseas'], G['nseas_pro'], G['GRPPOS']
evc, sit = G['_ev_click'], G['sitout_ev']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
print(f'v2.1 engine={ENG}')
def synth(pos, pk, gm, avg, year=2025):
    return {'player': 'syn', 'pos': GRPPOS.get(pos), 'pick': float(pk), 'year': year, 'dob': '2006-03-01',
            'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': float(avg)}] if gm > 0 else []),
            'games': gm, '_pos_now': None, '_fut': []}
print('\n== ramp probe avg85 (MID pk10) ==')
print('  g | final  vclick |  ns lam  anchor  efull |  L(lvl_eff) expo')
rows = []
for gm in range(15):
    p = synth('MID', 10, gm, 85)
    with contextlib.redirect_stdout(io.StringIO()):
        fin = float(ev(p, 2026)); vc = float(evc(p, 2026))
        e_full = raw_ev(p, 2026) * iso_corr(MA.gfut(p), MA.effpk(p))
        ns = nseas_pro(p, 2026)
        fe = 0.58
        lam = float(np.interp(min(gm / fe, 6.0), [0, 1, 2, 3, 4, 5, 6], G['LAM_SIT']))
        R = float(np.interp(fe, [0, 1, 2, 3, 4, 5, 6], [1.0] + G['R_SIT']['nonKPP']))
        anch = R * v0_start(p)
        L = float(cp._lvl_eff(p, 2026)); ex = float(cp._exposure(p, 2026))
    rows.append((gm, fin, vc, ns, lam, anch, e_full, L, ex))
    print(f'  {gm:2d} | {fin:6.0f} {vc:6.0f} | {ns} {lam:5.3f} {anch:7.1f} {e_full:7.1f} | {L:6.2f} {ex:5.1f}')
steps = [rows[i+1][1]-rows[i][1] for i in range(14)]
T = rows[6][1]-rows[0][1]
print('  steps:', [round(s) for s in steps], f' T={T:.0f} cap={0.5*T:.0f} rise3={rows[3][1]-rows[0][1]:.0f}')
print('  dips:', [(i, round(s)) for i, s in enumerate(steps) if s < -1.0] or 'none')

print('\n== key anchors (post re-scope) ==')
def findk(nm, yr=None):
    return [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))
            and not p.get('_double_count') and (yr is None or p.get('year') == yr)]
with contextlib.redirect_stdout(io.StringIO()):
    out = {}
    for nm, yr in [('Elijah Tsatas', None), ('Sam Berry', 2020), ("Nathan O'Driscoll", None), ('Sam Darcy', 2021),
                   ('Aaron Cadman', None), ('Jed Walter', None), ('Isaac Kako', None), ('Daniel Annable', 2025),
                   ('Dylan Patterson', 2025), ('Sam Cumming', 2025), ('Louis Emmett', 2025), ('Jack Ison', 2025),
                   ('Cooper Lord', 2024), ('Tobie Travaglia', 2024), ('Christian Moraes', 2024),
                   ('Paul Curtis', None), ('Josh Ward', None), ('Connor Rozee', None), ('Charlie Curnow', None),
                   ('Jacob Farrow', 2025), ('Willem Duursma', 2025), ('Zeke Uwland', 2025)]:
        for p in findk(nm, yr):
            out[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = float(ev(p, 2026))
for k, v in out.items(): print(f'  {k:36s} {v:.0f}')

print('\n== census vs v2 matrix (re-scoped) ==')
MATV2 = json.load(open('/home/user/afl-rl-engine/data/s4_matrix_v2_4a134d05.json'))
jk = lambda r: f"{r['player']}|{r['year']}|{r['pick']}"
v2cur = {jk(r): r for r in MATV2.values()}
delta = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
        r = v2cur.get(k)
        if r is None or r.get('cur') is None or r.get('retired_now'): continue
        n = float(ev(p, 2026))
        delta.append((n - r['cur'], k, r['cur'], n, r['year'],
                      sum(x['games'] for x in p['scoring'] if x['year'] == 2026), nseas(p, 2026), nseas_pro(p, 2026)))
mv = [d for d in delta if abs(d[0]) > 0.5]
print(f'  joined={len(delta)} movers={len(mv)} aggregate={sum(d[0] for d in delta):+.0f}')
nonramp = [d for d in mv if not (d[6] == 0 or (d[6] <= 1 and d[7] >= 2) or d[4] >= 2024)]
print(f'  movers OUTSIDE the games-ramp family (ns_old>0, not released, cohort<2024): n={len(nonramp)}')
for d in sorted(nonramp, key=lambda x: -abs(x[0]))[:12]:
    print(f"    {d[1]:36s} v2={d[2]:6.0f} new={d[3]:6.0f} d={d[0]:+6.0f} g26={d[5]} ns{d[6]}->{d[7]}")
c25 = [d for d in delta if d[4] == 2025 and v2cur[d[1]].get('incurve')]
print(f"  2025 cohort: v2 SUM={sum(d[2] for d in c25):.0f} -> new SUM={sum(d[3] for d in c25):.0f} (D={sum(d[0] for d in c25):+.0f})")
json.dump(dict(engine=ENG, rows=rows, anchors=out,
               movers=[[d[1], d[2], d[3], round(d[0],1), d[5], d[6], d[7], d[4]] for d in sorted(delta, key=lambda x:-abs(x[0]))]),
          open(os.path.join(SC, 'p6_probe.json'), 'w'), indent=0)
print('wrote p6_probe.json')
