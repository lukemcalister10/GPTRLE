#!/usr/bin/env python3
# D4 ASK 5 — M3 proportional-tenure/age backtest (PROTOTYPE — wires nothing; candidate base M1+v7+M2).
# Lever: v_M3 = w*ev(p,2026) + (1-w)*ev_pin(p,2026);  w = 1 - s*(1-fE);  s = clip(1-g26/11,0,1).
# ev_pin = ev at 2026 with ONLY the age/tenure clocks pinned to 2025:
#   cp._age_asof -1yr | MA.age -1yr | PR.tenure -1yr (floor 1) | _eo years-since-draft N-1 (data window untouched).
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
ev, MA, cp = g['ev'], g['MA'], g['cp']
delisted, draftval = g['delisted'], g['draftval']
PR = g['PR']
EMD5 = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]

# ---------- the clock pin (D3 split-axis machinery, inverted) ----------
PIN = {'age': False, 'ten': False}
_age_asof0 = cp._age_asof
_age0 = MA.age
_ten0 = PR.tenure
_eo0 = g['_eo']
def _age_asof_p(p, Y):
    a = _age_asof0(p, Y)
    return (a - 1) if (PIN['age'] and Y == 2026) else a
def _age_p(p):
    a = _age0(p)
    return (a - 1) if (PIN['age'] and a is not None) else a
def _ten_p(p, Y):
    t = _ten0(p, Y)
    return max(1, t - 1) if (PIN['ten'] and Y == 2026) else t
def _eo_p(p, Y):
    if not (PIN['ten'] and Y == 2026):
        return _eo0(p, Y)
    d = cp.debutyr(p); N = Y - d + 1 - 1                      # N-1: the clock; data window stays at Y
    yrw = float(np.clip((N - 2) / 4.0, 0.0, 1.0))
    gm = sum(x.get('games', 0) for x in p['scoring'] if (d - 1) < x['year'] <= Y)
    exp = float(np.clip(gm / (14.0 * max(N - 1, 1)), 0.0, 1.0))
    return yrw * exp
cp._age_asof = _age_asof_p
MA.age = _age_p
PR.tenure = _ten_p
g['_eo'] = _eo_p                       # rebinds the global the exec'd engine closures read
# _feat's ten term uses raw Y-arithmetic (not PR.tenure) — pin it explicitly so the q97 feature clock moves too
_feat0 = cp._feat
_efften = g['eff_ten']
def _feat_p(p, Y):
    f = list(_feat0(p, Y))
    if PIN['ten'] and Y == 2026:
        f[8] = _efften(p, Y, max(0, (Y - 1) - (cp.debutyr(p) - 1)))   # index 8 = ten (6 one-hots + logep, exposure, ten, lvl, age)
    return f
cp._feat = _feat_p
def E(p, Y=2026):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, Y))
def Epin(p, axes=('age', 'ten')):
    for a in axes: PIN[a] = True
    try: return E(p, 2026)
    finally: PIN['age'] = PIN['ten'] = False
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)
def s_of(p): return float(np.clip(1.0 - gyr(p, 2026) / 11.0, 0.0, 1.0))
def m3(p, fE, axes=('age', 'ten')):
    s = s_of(p)
    if s <= 0: return E(p)
    w = 1.0 - s * (1.0 - fE)
    return w * E(p) + (1.0 - w) * Epin(p, axes)
def byname(nm):
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, nm
    return hits[0]

OUT = {'engine': EMD5}
FE = 0.58                                                     # SEASON_PROG at this cut
named = ['Connor Rozee', 'Josh Ward', 'Paul Curtis', 'Joshua Weddle', 'Jack Ginnivan', 'Charlie Curnow']
print(f'M3 backtest on candidate {EMD5} (M1+v7+M2 base) — fE={FE} (SEASON_PROG), s=clip(1-g26/11,0,1)')
print('== per-axis ablation, named players (base -> age-pin-only -> ten-pin-only -> joint pin -> M3 blend) ==')
OUT['named'] = {}
for nm in named:
    p = byname(nm)
    b = E(p); pa = Epin(p, ('age',)); pt = Epin(p, ('ten',)); pj = Epin(p); v = m3(p, FE)
    OUT['named'][nm] = {'g26': gyr(p, 2026), 's': round(s_of(p), 3), 'base': b, 'pin_age': pa,
                        'pin_ten': pt, 'pin_joint': pj, 'm3': round(v, 1)}
    print(f'  {nm:16s} g26={gyr(p,2026):2d} s={s_of(p):.2f}  base={b:5.0f}  ageP={pa:5.0f}  tenP={pt:5.0f}  jointP={pj:5.0f}  M3={v:5.0f} ({100*(v-b)/b:+.1f}%)')
# A3/A10 across the fE sweep
r = byname('Connor Rozee'); c = byname('Charlie Curnow')
r25, c25 = E(r, 2025), E(c, 2025)
OUT['sweep'] = {}
print('== A3/A10 vs fE (2025 denominators fixed: Rozee %d, Curnow %d) ==' % (r25, c25))
for fE in (0.50, 0.545, 0.58, 0.65, 1.00):
    a3 = m3(r, fE) / r25; a10 = m3(c, fE) / c25
    OUT['sweep'][str(fE)] = {'A3': round(a3, 3), 'A10': round(a10, 3)}
    print(f'  fE={fE:5.3f}  A3={a3:.3f}  A10={a10:.3f}')
# on-pace collateral (bar: ZERO >2%)
LISTED = [p for p in MA.data if MA.GRP.get(p.get('pos')) and not p.get('_double_count')
          and not p.get('_retired') and not delisted(p)]
onp = [p for p in LISTED if 11 <= gyr(p, 2026) <= 14]
mov = []
for p in onp:
    b = E(p)
    if b > 0:
        d = 100 * (m3(p, FE) - b) / b
        if abs(d) > 2.0: mov.append((p['player'], d))
OUT['onpace'] = {'n': len(onp), 'movers_gt2pct': len(mov)}
print(f'== on-pace collateral: n={len(onp)} movers>2% = {len(mov)} (bar: 0) ==')
# B5 (signed schedule) recount under M3
B5F = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}
def b5count(fn):
    off = 0
    for p in MA.data:
        if p.get('_retired') or p.get('_pickless') or delisted(p) or p.get('type') != 'ND': continue
        yis = 2026 - int(p.get('year') or 0)
        if yis < 1: continue
        try: v = fn(p)
        except Exception: continue
        if v < B5F.get(yis, .05) * draftval(p): off += 1
    return off
b5b = b5count(E); b5m = b5count(lambda p: m3(p, FE))
OUT['B5'] = {'base': b5b, 'm3': b5m}
print(f'== B5 signed-schedule offenders: base {b5b} -> M3 {b5m} ==')
# B6 ramp under M3 (synthetic 2025-draftee, g26 = 0..14)
GRPPOS = g['GRPPOS']
def ramp_p(gm):
    return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025, 'dob': '2006-03-01',
            'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []),
            'games': gm,   # top-level games: the age pin makes _dev_advance's backward roll read it (wiring-time note)
            '_pos_now': None, '_fut': []}
base_r = [round(E(ramp_p(gm))) for gm in range(0, 15)]
m3_r = [round(m3(ramp_p(gm), FE)) for gm in range(0, 15)]
OUT['B6'] = {'base': base_r, 'm3': m3_r}
print('== B6 ramp (0..14g): base', base_r, '-> M3', m3_r, '==')
# read-pass panel spot rows (the 10-panel names)
spot = ['Ryan Maric', 'Ed Langdon', 'Josh Smillie', 'Will Green', 'Harley Reid', 'Sam Berry']
OUT['spot'] = {}
print('== read-pass spot rows ==')
for nm in spot:
    try:
        p = byname(nm); b = E(p); v = m3(p, FE)
        OUT['spot'][nm] = {'base': b, 'm3': round(v, 1)}
        print(f'  {nm:16s} {b:6.0f} -> {v:6.0f} ({100*(v-b)/max(b,1e-9):+.1f}%)  g26={gyr(p,2026)} s={s_of(p):.2f}')
    except AssertionError:
        print(f'  {nm:16s} (ambiguous/missing)')
dst = os.path.join(ROOT, 'session_2026-07-02', 'scripts', 'd4_ask5_m3_out.json')
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True, default=float)
print('wrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
