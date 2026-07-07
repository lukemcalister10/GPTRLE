#!/usr/bin/env python3
# D7 ASK 4d — lean full-population sweep (one engine load): evs for every non-retired player at 2026,
# keyed player|year|pick, + Gothard detail. Usage: d7_ask4_sweep.py <label> <out.json>
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
ev, MA = G['ev'], G['MA']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired'):
            continue
        try:
            EV[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = float(ev(p, 2026))
        except Exception:
            EV[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = None
g = [p for p in MA.data if p['player'] == 'Phoenix Gothard' and not p.get('_retired')][0]
with contextlib.redirect_stdout(io.StringIO()):
    goth = float(ev(g, 2026))
json.dump(dict(label=label, engine=ENG, gothard=goth, evs=EV), open(outp, 'w'), indent=0)
print(f'[{label}] engine={ENG} n={sum(1 for v in EV.values() if v is not None)} Gothard={goth:.0f}')
print('wrote', outp, 'md5', hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8])
