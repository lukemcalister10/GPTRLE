#!/usr/bin/env python3
# D3 ASK 3 — FINAL parameterisation check: replacement denominator = on-pace floor (11 games), so the
# pre-registered collateral population (11-14g) is inert BY CONSTRUCTION. Verifies zero movers empirically.
#   s(p,Y) = clip(1 - g_Y/11, 0, 1);  prior-decay exponent (in-progress season) = max(0,Y-yr-1) + 1 - s*(1-fhat)
import os, sys, io, json, contextlib, hashlib
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
RA = '/home/claude/rl_workspace/rl_after'
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/user/afl-rl-engine/vendor']
os.chdir(RA)
import numpy as np
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
ev, MA, cp = g['ev'], g['MA'], g['cp']
delisted, draftval = g['delisted'], g['draftval']
def E(p, Y):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, Y))
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)
def byname(nm):
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, nm
    return hits[0]
LISTED = [p for p in MA.data if MA.GRP.get(p.get('pos')) and not p.get('_double_count')
          and not p.get('_retired') and not delisted(p)]
FHAT = 0.545; DEN = 11.0
_exp0 = cp._exposure
FIX = {'on': False}
def _exposure_fix(p, Y):
    if not FIX['on']: return _exp0(p, Y)
    if Y != 2026: return _exp0(p, Y)
    rows = cp._season_rows(p, Y)
    gy = sum(gm for yr, gm, _ in rows if yr == Y)
    s = float(np.clip(1.0 - gy / DEN, 0.0, 1.0))
    if s <= 0.0: return _exp0(p, Y)
    ex = 1.0 - s * (1.0 - FHAT)
    return float(sum(gm * (1.0 if yr == Y else cp.RECENCY_DECAY ** (max(0, Y - yr - 1) + ex)) for yr, gm, _ in rows))
cp._exposure = _exposure_fix
OUT = {}
named = ['Connor Rozee', 'Josh Ward', 'Paul Curtis', 'Joshua Weddle', 'Jack Ginnivan', 'Charlie Curnow']
base26 = {nm: E(byname(nm), 2026) for nm in named}
base25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = True
fix26 = {nm: E(byname(nm), 2026) for nm in named}
fix25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = False
OUT['named'] = {nm: {'base26': base26[nm], 'fix26': fix26[nm],
                     'd_pct': round(100 * (fix26[nm] - base26[nm]) / base26[nm], 1)} for nm in named}
OUT['gates'] = {'A3_fix': round(fix26['Connor Rozee'] / fix25['Connor Rozee'], 3),
                'A10_fix': round(fix26['Charlie Curnow'] / fix25['Charlie Curnow'], 3)}
for nm in named: print(f'  {nm:16s} {base26[nm]:5.0f} -> {fix26[nm]:5.0f} ({OUT["named"][nm]["d_pct"]:+.1f}%)')
print('  A3 ->', OUT['gates']['A3_fix'], '| A10 ->', OUT['gates']['A10_fix'])
onpace = [p for p in LISTED if 11 <= gyr(p, 2026) <= 14]
res = []
for p in onpace:
    b = E(p, 2026); FIX['on'] = True; v = E(p, 2026); FIX['on'] = False
    if b > 0: res.append((p['player'], 100 * (v - b) / b))
mov = [r for r in res if abs(r[1]) > 2.0]
OUT['onpace'] = {'n': len(res), 'movers_gt2pct': len(mov), 'max_abs_pct': round(max(abs(r[1]) for r in res), 3)}
print(f"on-pace: n={len(res)} movers>2%={len(mov)} max|d|={OUT['onpace']['max_abs_pct']}%")
def b5_count():
    off = []
    for p in LISTED:
        if p.get('_pickless') or int(p.get('year') or 0) not in (2024, 2025): continue
        try: v = E(p, 2026)
        except Exception: continue
        if v < 0.25 * draftval(p): off.append(p['player'])
    return off
b5b = b5_count(); FIX['on'] = True; b5f = b5_count(); FIX['on'] = False
OUT['b5'] = {'base': len(b5b), 'fix': len(b5f)}
print('B5:', len(b5b), '->', len(b5f))
# g<6 cohort lift under final parameterisation
pop = [p for p in LISTED if gyr(p, 2025) >= 10 and 1 <= gyr(p, 2026) <= 5]
def bucket(p):
    ysd = 2026 - cp.debutyr(p) + 1
    return 'young(2-4)' if ysd <= 4 else ('mid(5-7)' if ysd <= 7 else 'old(8+)')
BB = {}
for p in pop:
    b25 = E(p, 2025); b26 = E(p, 2026); FIX['on'] = True; v26 = E(p, 2026); FIX['on'] = False
    if b25 > 0: BB.setdefault(bucket(p), []).append((100 * (b26 - b25) / b25, 100 * (v26 - b25) / b25))
OUT['g6pop'] = {}
for k in ['young(2-4)', 'mid(5-7)', 'old(8+)']:
    a = np.array(BB.get(k, []))
    if len(a):
        OUT['g6pop'][k] = {'n': len(a), 'drop_base': round(a[:, 0].mean(), 1), 'drop_fix': round(a[:, 1].mean(), 1)}
        print(f'  {k:11s} {a[:,0].mean():+.1f}% -> {a[:,1].mean():+.1f}%')
cp._exposure = _exp0
dst = '/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_ask3_final_out.json'
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True, default=float)
print('wrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
