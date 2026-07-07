#!/usr/bin/env python3
# GAMES-RAMP D10 phase 5 — SCRATCH VERIFICATION of the wired v2.1 engine (one load).
# (a) B6 ramp (gate-identical synth avg 85) + low-rate spot ramp (avg 40) + output-monotone check
# (b) anchor players (three-column deltas come offline from pinned matrices)
# (c) movement census vs the v2 matrix (join player|year|pick on 'cur')
# (d) pre-season hold proof (ev at draft year == V0) + position-preservation proof
# (e) 2025 cohort sum + under-seam aggregate
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
ev, raw_ev, iso_corr, draftval = G['ev'], G['raw_ev'], G['iso_corr'], G['draftval']
v0_start, nseas, nseas_pro, GRPPOS = G['v0_start'], G['nseas'], G['nseas_pro'], G['GRPPOS']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
CPM = hashlib.md5(open(os.path.join(SC, 'deploy', 'forward_valuation', 'conditional_prior.py'), 'rb').read()).hexdigest()[:8]
print(f'v2.1 engine={ENG} cp={CPM}')

def synth(pos, pk, gm, avg, year=2025):
    return {'player': 'syn', 'pos': GRPPOS.get(pos), 'pick': float(pk), 'year': year, 'dob': '2006-03-01',
            'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': float(avg)}] if gm > 0 else []),
            'games': gm, '_pos_now': None, '_fut': []}
Q = lambda p, Y=2026: float(ev(p, Y))
print('\n== (a) B6 ramp avg85 (gate synth, games 0..14) ==')
with contextlib.redirect_stdout(io.StringIO()):
    vals = [Q(synth('MID', 10, gm, 85)) for gm in range(15)]
steps = [vals[i+1]-vals[i] for i in range(14)]
T = vals[6]-vals[0]; rise3 = vals[3]-vals[0]
print('  ramp:', [round(v) for v in vals]); print('  steps:', [round(s) for s in steps])
print(f'  dips={[(i,round(s)) for i,s in enumerate(steps) if s<-1.0] or "none"}; T={T:+.0f}; '
      f'steps>50%T(first6)={[(i,round(s)) for i,s in enumerate(steps[:6]) if s>0.5*max(T,1)] or "none"}; '
      f'rise3={rise3:+.0f} (need >={0.25*T:.0f})')
print('== low-rate spot ramp avg40 (seam proof at poor output) ==')
with contextlib.redirect_stdout(io.StringIO()):
    v40 = [Q(synth('MID', 10, gm, 40)) for gm in range(9)]
print('  ramp:', [round(v) for v in v40], ' steps:', [round(v40[i+1]-v40[i]) for i in range(8)])
print('== output-monotone at fixed games (g=2, avg 30..100) ==')
with contextlib.redirect_stdout(io.StringIO()):
    vo = [(a, Q(synth('MID', 10, 2, a))) for a in range(30, 101, 10)]
print('  ', [(a, round(v)) for a, v in vo], ' monotone:', all(vo[i+1][1] >= vo[i][1]-0.5 for i in range(len(vo)-1)))
print('== (d) pre-season hold (ev at draft year == V0) + position preservation ==')
with contextlib.redirect_stdout(io.StringIO()):
    sp = synth('MID', 10, 0, 0); hold = (Q(sp, 2025), v0_start(sp))
    pos_pair = {pos: (round(v0_start(synth(pos, 12, 0, 0))), Q(synth(pos, 12, 0, 0))) for pos in ('MID', 'KEY_DEF', 'GEN_DEF', 'RUC')}
print(f'  ev(draft yr)={hold[0]:.0f} vs V0={hold[1]:.0f} (equal={abs(hold[0]-round(hold[1]))<=1})')
print(f'  same-pick(12) sit-out values by pos (V0, ev2026): {pos_pair}  <- position basis carried')

print('\n== (b) anchors ==')
def findk(nm, yr=None):
    return [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))
            and not p.get('_double_count') and (yr is None or p.get('year') == yr)]
names = [('Daniel Annable', 2025), ('Dylan Patterson', 2025), ('Xavier Taylor', 2025), ('Oskar Taylor', 2025),
         ('Sam Cumming', 2025), ('Louis Emmett', 2025), ('Jack Ison', 2025), ('Cooper Lord', None),
         ('Tobie Travaglia', 2024), ('Angus Clarke', 2024), ('Jacob Farrow', 2025), ('Sullivan Robey', 2025),
         ('Harry Dean', 2025), ('Sam Berry', 2020), ('Elijah Tsatas', None), ('Paul Curtis', None),
         ('Josh Ward', None), ('Joshua Weddle', None), ('Jack Ginnivan', None), ('Christian Moraes', 2024),
         ('Caiden Cleary', None), ('Jedd Busslinger', None), ('Phoenix Gothard', None)]
AN = {}
with contextlib.redirect_stdout(io.StringIO()):
    for nm, yr in names:
        for p in findk(nm, yr):
            k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
            AN[k] = dict(new=Q(p), v0=round(v0_start(p), 1), ns_old=nseas(p, 2026), ns_pro=nseas_pro(p, 2026),
                         g26=sum(x['games'] for x in p['scoring'] if x['year'] == 2026))
for k, d in AN.items():
    print(f"  {k:34s} g26={d['g26']:2d} ns {d['ns_old']}->{d['ns_pro']}  V0={d['v0']:7.1f}  NEW={d['new']:.0f}")

print('\n== (c) movement census vs v2 matrix ==')
MATV2 = json.load(open('/home/user/afl-rl-engine/data/s4_matrix_v2_4a134d05.json'))
MATC = json.load(open('/home/user/afl-rl-engine/data/s4_matrix_control_8aed420a.json'))
jk = lambda r: f"{r['player']}|{r['year']}|{r['pick']}"
v2cur = {jk(r): r for r in MATV2.values()}
ctl = {jk(r): r.get('cur') for r in MATC.values()}
delta, missing = [], 0
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count') or not MA.GRP.get(p.get('pos')): continue
        k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
        r = v2cur.get(k)
        if r is None or r.get('cur') is None or r.get('retired_now'): continue
        n = Q(p)
        delta.append((n - r['cur'], k, r['cur'], n, r['year'],
                      sum(x['games'] for x in p['scoring'] if x['year'] == 2026),
                      nseas(p, 2026), nseas_pro(p, 2026), ctl.get(k)))
mv = [d for d in delta if abs(d[0]) > 0.5]
print(f'  joined={len(delta)} movers={len(mv)} aggregate={sum(d[0] for d in delta):+.0f}')
print('  top +25:')
for d in sorted(mv, reverse=True)[:25]:
    print(f"    {d[1]:36s} ctl={d[8]} v2={d[2]:6.0f} new={d[3]:6.0f} d={d[0]:+7.0f} g26={d[5]:2d} ns{d[6]}->{d[7]}")
print('  top -15:')
for d in sorted(mv)[:15]:
    print(f"    {d[1]:36s} ctl={d[8]} v2={d[2]:6.0f} new={d[3]:6.0f} d={d[0]:+7.0f} g26={d[5]:2d} ns{d[6]}->{d[7]}")
print('\n== (e) cohort/seam aggregates ==')
c25 = [d for d in delta if d[4] == 2025 and v2cur[d[1]].get('incurve')]
print(f"  2025 cohort (incurve n={len(c25)}): v2 SUM={sum(d[2] for d in c25):.0f} -> new SUM={sum(d[3] for d in c25):.0f} (D={sum(d[0] for d in c25):+.0f})")
seam = [d for d in delta if d[6] == 0 and 1 <= d[5] <= 5]
print(f"  under-seam (old-ns==0, 1-5 g26; n={len(seam)}): aggregate D={sum(d[0] for d in seam):+.0f}")
sit0 = [d for d in delta if d[6] == 0 and d[5] == 0]
print(f"  zero-game sit-outs (n={len(sit0)}): aggregate D={sum(d[0] for d in sit0):+.0f}")
rel = [d for d in delta if d[6] <= 1 and d[7] >= 2]
print(f"  stalled-released by prorated bar (ns_old<=1 -> ns_pro>=2; n={len(rel)}): " +
      '; '.join(f"{d[1].split('|')[0]} {d[2]:.0f}->{d[3]:.0f}" for d in rel[:8]))
json.dump(dict(engine=ENG, cp=CPM, ramp=vals, ramp40=v40, anchors=AN,
               movers=[[d[1], d[8], d[2], d[3], round(d[0], 1), d[5], d[6], d[7]] for d in sorted(delta, key=lambda x: -abs(x[0]))],
               n_joined=len(delta)),
          open(os.path.join(SC, 'p5_verify.json'), 'w'), indent=0)
print('wrote p5_verify.json')
