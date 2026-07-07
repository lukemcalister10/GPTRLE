#!/usr/bin/env python3
# D5 measurement suite — ONE engine load per fresh process (run sequentially).
# Usage: python3 d5_measure_state.py <label> <out.json>
# Reports: A2 trio (Curtis/Ward/Weddle) · A3 (Rozee 26/25, pre-LTI basis) · A8 pair (Berry/Tsatas) ·
# B5 FULL offender detail under the signed year-schedule (gate-exact logic) · ND-only clean value/draftval
# rows by years-in-system (G3-CLEAN machinery, uncapped depth — feeds the ASK-3c yr8+ derivation).
import os, sys, io, json, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)

label, outp = sys.argv[1], sys.argv[2]
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, cp = G['ev'], G['MA'], G['cp']
draftval, delisted = G['draftval'], G['delisted']
ENG_MD5 = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
CP_MD5 = hashlib.md5(open('/home/claude/rl_workspace/forward_valuation/conditional_prior.py', 'rb').read()).hexdigest()[:8]
STORE_MD5 = hashlib.md5(open('rl_model_data.json', 'rb').read()).hexdigest()[:8]

ALIAS = {'Josh Weddle': 'Joshua Weddle'}
def E(name, yr=2026):
    name = ALIAS.get(name, name)
    hits = [p for p in MA.data if p['player'] == name and not p.get('_retired')]
    assert len(hits) == 1, f'match {name}: {len(hits)}'
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(hits[0], yr))

named = {}
for nm in ['Paul Curtis', 'Josh Ward', 'Josh Weddle', 'Sam Berry', 'Elijah Tsatas']:
    named[nm] = round(E(nm), 1)
named['Connor Rozee 2026'] = round(E('Connor Rozee', 2026), 1)
named['Connor Rozee 2025'] = round(E('Connor Rozee', 2025), 1)

# full sweep (gate-exact population handling)
EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired'):
            continue
        try:
            EV[id(p)] = float(ev(p, 2026))
        except Exception:
            EV[id(p)] = None

# B5 — signed year-schedule, gate-exact
B5_FLOORS = {1: 0.45, 2: 0.35, 3: 0.28, 4: 0.21, 5: 0.13, 6: 0.09}
B5_TAIL = 0.05
off = []
for p in MA.data:
    if p.get('_retired') or p.get('_pickless') or delisted(p) or p.get('type') != 'ND':
        continue
    yis = 2026 - int(p.get('year') or 0)
    if yis < 1:
        continue
    v = EV.get(id(p))
    if v is None:
        continue
    dv = draftval(p)
    fl = B5_FLOORS.get(yis, B5_TAIL)
    if v < fl * dv:
        off.append(dict(player=p['player'], club=p.get('_club'), yis=yis, type=p.get('type'),
                        ev=round(v, 1), draftval=round(dv, 1), ratio=round(v / max(dv, 1e-9), 4),
                        floor_frac=fl, floor=round(fl * dv, 1), margin=round(v - fl * dv, 1),
                        pick=p.get('pick'), year=p.get('year'), key=p.get('key')))
off.sort(key=lambda r: (r['yis'], r['margin']))

# G3-CLEAN rows: ND-only, listed, picked — value/draftval by years-in-system (UNCAPPED depth)
clean = []
for p in MA.data:
    if p.get('_retired') or p.get('_pickless') or delisted(p) or p.get('type') != 'ND':
        continue
    yis = 2026 - int(p.get('year') or 0)
    if yis < 1:
        continue
    v = EV.get(id(p))
    if v is None:
        continue
    dv = draftval(p)
    clean.append(dict(player=p['player'], yis=yis, ratio=round(v / max(dv, 1e-9), 4),
                      ev=round(v, 1), draftval=round(dv, 1)))

out = dict(label=label, engine_md5=ENG_MD5, cp_md5=CP_MD5, store_md5=STORE_MD5,
           named=named,
           a2_ratio=round(named['Paul Curtis'] / max(named['Josh Ward'], 1e-9), 4),
           a3_ratio=round(named['Connor Rozee 2026'] / max(named['Connor Rozee 2025'], 1e-9), 4),
           a8_ratio=round(named['Sam Berry'] / max(named['Elijah Tsatas'], 1e-9), 4),
           b5_count=len(off), b5_offenders=off, clean_rows=clean,
           n_active_evald=sum(1 for v in EV.values() if v is not None))
json.dump(out, open(outp, 'w'), indent=1)
print(f"[{label}] engine={ENG_MD5} cp={CP_MD5} store={STORE_MD5} | "
      f"A2 Curtis/Ward={out['a2_ratio']:.3f} ({named['Paul Curtis']:.0f}/{named['Josh Ward']:.0f}) | "
      f"A3 Rozee={out['a3_ratio']:.3f} | A8 Berry/Tsatas={out['a8_ratio']:.2f}x "
      f"({named['Sam Berry']:.0f}/{named['Elijah Tsatas']:.0f}) | B5 offenders={len(off)}")
print('wrote', outp, 'md5', hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8])
