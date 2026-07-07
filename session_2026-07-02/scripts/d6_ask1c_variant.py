#!/usr/bin/env python3
# D6 ASK 1c — Gothard at a variant engine (candidate fb39d88a or candidate-minus-cB), one load.
# Also prints A2 named pair (Curtis/Ward) — fresh confirmation feed for ASK 4(i) — and the full
# gate-exact B5 offender sweep (feeds ASK 3 joiner verification at the candidate).
import os, sys, io, json, contextlib, hashlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
label, dst = sys.argv[1], sys.argv[2]
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
ev, MA, cp = g['ev'], g['MA'], g['cp']
draftval, delisted, nseas = g['draftval'], g['delisted'], g['nseas']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
CP = hashlib.md5(open('/home/claude/rl_workspace/forward_valuation/conditional_prior.py', 'rb').read()).hexdigest()[:8]
STORE = hashlib.md5(open('rl_model_data.json', 'rb').read()).hexdigest()[:8]

def E(nm, Y=2026):
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, nm
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(hits[0], Y))

goth = E('Phoenix Gothard')
curtis, ward = E('Paul Curtis'), E('Josh Ward')
# Gothard uncapped at this variant: recompute e_pre
p = [q for q in MA.data if q['player'] == 'Phoenix Gothard' and not q.get('_retired')][0]
with contextlib.redirect_stdout(io.StringIO()):
    e_pre = g['raw_ev'](p, 2026) * g['iso_corr'](MA.gfut(p), MA.effpk(p))

EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for q in MA.data:
        if q.get('_retired'):
            continue
        try:
            EV[id(q)] = float(ev(q, 2026))
        except Exception:
            EV[id(q)] = None
B5F = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}
off = []
for q in MA.data:
    if q.get('_retired') or q.get('_pickless') or delisted(q) or q.get('type') != 'ND':
        continue
    yis = 2026 - int(q.get('year') or 0)
    if yis < 1:
        continue
    v = EV.get(id(q))
    if v is None:
        continue
    dvq = draftval(q)
    fl = B5F.get(yis, 0.05)
    if v < fl * dvq:
        off.append(dict(player=q['player'], club=q.get('_club'), yis=yis, ev=round(v, 1),
                        draftval=round(dvq, 1), ratio=round(v / max(dvq, 1e-9), 4),
                        floor_frac=fl, floor=round(fl * dvq, 1), margin=round(v - fl * dvq, 1),
                        pick=q.get('pick'), year=q.get('year'), key=q.get('key'),
                        g26=sum(x['games'] for x in q['scoring'] if x['year'] == 2026)))
off.sort(key=lambda r: (r['yis'], r['margin']))
out = dict(label=label, engine_md5=ENG, cp_md5=CP, store_md5=STORE,
           gothard=goth, gothard_uncapped=round(e_pre, 1),
           curtis=curtis, ward=ward, a2_ratio=round(curtis / max(ward, 1e-9), 4),
           b5_count=len(off), b5_offenders=off)
json.dump(out, open(dst, 'w'), indent=1)
print(f'[{label}] engine={ENG} cp={CP} store={STORE} | Gothard={goth:.0f} (uncapped {e_pre:.0f}) | '
      f'A2 {curtis:.0f}/{ward:.0f}={curtis/ward:.3f} | B5={len(off)}')
