#!/usr/bin/env python3
# D4 ASK 5 addendum — M2+M3 on the PRE-OVERLAY (canonical 8aed420a) engine: quantifies the M1+v7 overlay's
# cost to A3. M2 = scratch _exposure patch (d3_ask3_final.py form); M3 = clock-pin blend (d4_ask5_m3_backtest.py form).
import os, sys, io, json, contextlib, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', os.path.join(ROOT, 'vendor')]
os.chdir(RA)
import numpy as np
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
ev, MA, cp, PR = g['ev'], g['MA'], g['cp'], g['PR']
EMD5 = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
# --- M2 scratch patch (identical to d3_ask3_final.py) ---
FHAT, DEN = 0.545, 11.0
_exp0 = cp._exposure
M2 = {'on': True}
def _exposure_fix(p, Y):
    if not M2['on'] or Y != 2026: return _exp0(p, Y)
    rows = cp._season_rows(p, Y)
    gy = sum(gm for yr, gm, _ in rows if yr == Y)
    s = float(np.clip(1.0 - gy / DEN, 0.0, 1.0))
    if s <= 0.0: return _exp0(p, Y)
    ex = 1.0 - s * (1.0 - FHAT)
    return float(sum(gm * (1.0 if yr == Y else cp.RECENCY_DECAY ** (max(0, Y - yr - 1) + ex)) for yr, gm, _ in rows))
cp._exposure = _exposure_fix
# --- M3 clock pin (identical hooks to d4_ask5_m3_backtest.py) ---
PIN = {'age': False, 'ten': False}
_age_asof0, _age0, _ten0, _eo0 = cp._age_asof, MA.age, PR.tenure, g['_eo']
cp._age_asof = lambda p, Y: (_age_asof0(p, Y) - 1) if (PIN['age'] and Y == 2026) else _age_asof0(p, Y)
def _age_p(p):
    a = _age0(p)
    return (a - 1) if (PIN['age'] and a is not None) else a
MA.age = _age_p
PR.tenure = lambda p, Y: max(1, _ten0(p, Y) - 1) if (PIN['ten'] and Y == 2026) else _ten0(p, Y)
def _eo_p(p, Y):
    if not (PIN['ten'] and Y == 2026): return _eo0(p, Y)
    d = cp.debutyr(p); N = Y - d + 1 - 1
    yrw = float(np.clip((N - 2) / 4.0, 0.0, 1.0))
    gm = sum(x.get('games', 0) for x in p['scoring'] if (d - 1) < x['year'] <= Y)
    return yrw * float(np.clip(gm / (14.0 * max(N - 1, 1)), 0.0, 1.0))
g['_eo'] = _eo_p
_feat0, _efften = cp._feat, g['eff_ten']
def _feat_p(p, Y):
    f = list(_feat0(p, Y))
    if PIN['ten'] and Y == 2026:
        f[8] = _efften(p, Y, max(0, (Y - 1) - (cp.debutyr(p) - 1)))
    return f
cp._feat = _feat_p
def E(p, Y=2026):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, Y))
def Epin(p):
    PIN['age'] = PIN['ten'] = True
    try: return E(p)
    finally: PIN['age'] = PIN['ten'] = False
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)
def m3(p, fE):
    s = float(np.clip(1.0 - gyr(p, 2026) / 11.0, 0.0, 1.0))
    if s <= 0: return E(p)
    w = 1.0 - s * (1.0 - fE)
    return w * E(p) + (1.0 - w) * Epin(p)
r = [p for p in MA.data if p['player'] == 'Connor Rozee' and not p.get('_retired')][0]
r25 = E(r, 2025)
out = {'engine': EMD5, 'base_M2_A3': round(E(r) / r25, 3)}
print(f'PRE-OVERLAY engine {EMD5} + M2 scratch: A3 = {out["base_M2_A3"]} (Rozee {E(r):.0f} / {r25:.0f})')
for fE in (0.50, 0.545, 0.58):
    a3 = m3(r, fE) / r25
    out[f'M2M3_A3_fE{fE}'] = round(a3, 3)
    print(f'  + M3 @fE={fE}: A3 = {a3:.3f}')
M2['on'] = False
print(f'  (control: M2 off, plain head A3 = {E(r)/r25:.3f})')
M2['on'] = True
dst = os.path.join(ROOT, 'session_2026-07-02', 'scripts', 'd4_ask5_m3_preoverlay_out.json')
json.dump(out, open(dst, 'w'), indent=1, sort_keys=True)
print('wrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
