#!/usr/bin/env python3
# D3 ASK 3b-3d — SCOPED drop-fix prototype (design derivation; NOTHING WIRED).
# Scoping (derived after the unscoped variant failed the zero-collateral bar, d3_ask3_fixproto.py):
#   the artifact is prior-season evidence decaying a full year while the in-progress season has not yet
#   REPLACED it. Replacement is measured by the player's own banked games vs the elapsed schedule:
#     s(p,Y) = clip(1 - g_Y / (fhat*SEASON), 0, 1)          (0 = fully on pace, 1 = no current evidence)
#   prior-season decay exponent = max(0, Y-yr-1) + 1 - s*(1-fhat)   (in-progress season only)
#   -> byte-exact status quo for on-pace players (s=0) AND at fhat=1 AND for completed seasons.
#   Smooth in g_Y (no hard boundary). _lvl_wt untouched.
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
_nqual, _lvlcurr, _par_prior = g['_nqual'], g['_lvlcurr'], g['_par_prior']
PROVEN_N, DOWN_TOL, _agemult, _upS, _eo = g['PROVEN_N'], g['DOWN_TOL'], g['_agemult'], g['_upS'], g['_eo']
b6_orig = g['b6']; GRPPOS = g['GRPPOS']
OUT = {}
def E(p, Y):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, Y))
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)
def byname(nm):
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, nm
    return hits[0]
POPALL = [p for p in MA.data if MA.GRP.get(p.get('pos')) and not p.get('_double_count')]
LISTED = [p for p in POPALL if not p.get('_retired') and not delisted(p)]
SEASON = 22.0; FHAT = 0.545                                        # derived in d3_ask3_fixproto.py
_exp0 = cp._exposure
FIX = {'on': False, 'f': FHAT}
def _exposure_fix(p, Y):
    if not FIX['on']: return _exp0(p, Y)
    f = FIX['f'] if Y == 2026 else 1.0
    if f >= 1.0: return _exp0(p, Y)
    rows = cp._season_rows(p, Y)
    gy = sum(gm for yr, gm, _ in rows if yr == Y)
    s = float(np.clip(1.0 - gy / (f * SEASON), 0.0, 1.0))
    if s <= 0.0: return _exp0(p, Y)
    ex = 1.0 - s * (1.0 - f)
    return float(sum(gm * (1.0 if yr == Y else cp.RECENCY_DECAY ** (max(0, Y - yr - 1) + ex)) for yr, gm, _ in rows))
cp._exposure = _exposure_fix
named = ['Connor Rozee', 'Josh Ward', 'Paul Curtis', 'Joshua Weddle', 'Jack Ginnivan', 'Charlie Curnow']
FIX['on'] = False
base26 = {nm: E(byname(nm), 2026) for nm in named}
base25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = True; FIX['f'] = 1.0
inert_f1 = all(E(byname(nm), 2026) == base26[nm] for nm in named)
inert_25 = all(E(byname(nm), 2025) == base25[nm] for nm in named)
FIX['f'] = FHAT
fix26 = {nm: E(byname(nm), 2026) for nm in named}
fix25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = False
OUT['inertness'] = {'f1_byte_exact': inert_f1, 'hist2025_byte_exact': inert_25}
print('inert f=1:', inert_f1, '| inert 2025:', inert_25)
print('\n== named under SCOPED fix (f=%.3f) ==' % FHAT)
OUT['named'] = {}
for nm in named:
    OUT['named'][nm] = {'base26': base26[nm], 'fix26': fix26[nm],
                        'd_pct': round(100 * (fix26[nm] - base26[nm]) / base26[nm], 1)}
    print(f'  {nm:16s} 2026 {base26[nm]:5.0f} -> {fix26[nm]:5.0f} ({OUT["named"][nm]["d_pct"]:+.1f}%)')
OUT['gates'] = {'A3_base': round(base26['Connor Rozee'] / base25['Connor Rozee'], 3),
                'A3_fix': round(fix26['Connor Rozee'] / fix25['Connor Rozee'], 3),
                'A10_base': round(base26['Charlie Curnow'] / base25['Charlie Curnow'], 3),
                'A10_fix': round(fix26['Charlie Curnow'] / fix25['Charlie Curnow'], 3)}
print('  A3 %.3f -> %.3f (need 0.80) | A10 %.3f -> %.3f (need 0.70)' %
      (OUT['gates']['A3_base'], OUT['gates']['A3_fix'], OUT['gates']['A10_base'], OUT['gates']['A10_fix']))
# on-pace collateral
onpace = [p for p in LISTED if 11 <= gyr(p, 2026) <= 14]
res = []
for p in onpace:
    b = E(p, 2026); FIX['on'] = True; v = E(p, 2026); FIX['on'] = False
    if b > 0: res.append((p['player'], b, v, 100 * (v - b) / b))
mov = [r for r in res if abs(r[3]) > 2.0]
OUT['onpace'] = {'n': len(res), 'movers_gt2pct': len(mov),
                 'max_abs_pct': round(max(abs(r[3]) for r in res), 3),
                 'worst': [{'player': r[0], 'pct': round(r[3], 2)} for r in sorted(res, key=lambda r: -abs(r[3]))[:5]]}
print(f"\n== on-pace collateral: n={len(res)}, movers>2% = {len(mov)}, max|d| = {OUT['onpace']['max_abs_pct']}% ==")
# g<6 population
pop = [p for p in LISTED if gyr(p, 2025) >= 10 and 1 <= gyr(p, 2026) <= 5]
def bucket(p):
    ysd = 2026 - cp.debutyr(p) + 1
    return 'young(2-4)' if ysd <= 4 else ('mid(5-7)' if ysd <= 7 else 'old(8+)')
BB = {}
for p in pop:
    b25 = E(p, 2025); b26 = E(p, 2026); FIX['on'] = True; v26 = E(p, 2026); FIX['on'] = False
    if b25 > 0: BB.setdefault(bucket(p), []).append((100 * (b26 - b25) / b25, 100 * (v26 - b25) / b25))
OUT['g6pop'] = {}
print('\n== g<6 population drop (base -> scoped fix) ==')
for k in ['young(2-4)', 'mid(5-7)', 'old(8+)']:
    a = np.array(BB.get(k, []))
    if not len(a): continue
    OUT['g6pop'][k] = {'n': len(a), 'drop_base_pct': round(a[:, 0].mean(), 1), 'drop_fix_pct': round(a[:, 1].mean(), 1)}
    print(f'  {k:11s} n={len(a):2d}  {a[:,0].mean():+.1f}% -> {a[:,1].mean():+.1f}%')
# B5 / B6
def b5_count():
    off = []
    for p in LISTED:
        if p.get('_pickless') or int(p.get('year') or 0) not in (2024, 2025): continue
        try: v = E(p, 2026)
        except Exception: continue
        if v < 0.25 * draftval(p): off.append(p['player'])
    return off
b5b = b5_count(); FIX['on'] = True; b5f = b5_count(); FIX['on'] = False
def ramp_p(gm):
    return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025, 'dob': '2006-03-01',
            'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []), '_pos_now': None, '_fut': []}
b6b = [E(ramp_p(gm), 2026) for gm in range(0, 15)]
FIX['on'] = True
b6f = [E(ramp_p(gm), 2026) for gm in range(0, 15)]
FIX['on'] = False
OUT['b5'] = {'base': len(b5b), 'fix': len(b5f)}; OUT['b6'] = {'identical': b6b == b6f}
print(f'\n== B5 {len(b5b)} -> {len(b5f)} | B6 ramp identical: {b6b == b6f} ==')
# B1 splice
mat = json.load(open('/home/user/afl-rl-engine/data/s4_matrix_nogames.json'))
deltas = {}
for p in POPALL:
    if p.get('year') in (2019, 2020):
        try:
            b = E(p, 2026); FIX['on'] = True; v = E(p, 2026); FIX['on'] = False
            deltas[(p['player'], p['year'])] = v - b
        except Exception: FIX['on'] = False
S = {}
for rec in mat.values():
    C = int(rec['year'])
    if not rec['incurve'] or not (2004 <= C <= 2020): continue
    for i, yy in enumerate(rec['yrs']):
        N = i + 1
        if N > 7: break
        v = float(rec['Vpath'][i] or 0.0)
        if yy == 2026 and (rec['player'], C) in deltas: v += deltas[(rec['player'], C)]
        S[(C, N)] = S.get((C, N), 0.0) + v
pooled = {N: 100.0 * sum(S.get((C, N), 0.0) for C in set(c for c, _ in S)) /
             max(sum(S.get((C, 1), 0.0) for C in set(c for c, _ in S)), 1e-9) for N in range(1, 8)}
ppk = max(pooled, key=pooled.get)
rises = [max({N: 100.0 * S[(C, N)] / max(S[(C, 1)], 1e-9) for N in range(1, 8) if (C, N) in S}.get(N, 0)
             for N in (4, 5, 6)) > 100.0 for C in sorted({c for c, _ in S})]
path_ok = all(pooled[N + 1] >= 0.95 * pooled[N] for N in range(1, ppk) if N + 1 in pooled)
OUT['b1_spliced'] = {'pass': bool(all(rises) and ppk in (4, 5, 6) and pooled[ppk] > 100 and path_ok),
                     'peak_N': ppk, 'R_peak': round(pooled[ppk]), 'rises': f'{sum(rises)}/{len(rises)}'}
print('== B1 spliced:', OUT['b1_spliced'], '==')
# M1+v7 interaction
TOL_M1 = 5.0; G_ADQ = 12; WIN = 2; S_M1 = 0.46; GCAP = 17.0
def _radq(p, Y, Lo): return any(x['games'] >= G_ADQ and x['avg'] > Lo for x in p['scoring'] if Y - WIN < x['year'] <= Y and (cp.debutyr(p) - 1) < x['year'])
def _coreM1(p, Y):
    Lo = cp._lvl_eff_orig(p, Y); n = _nqual(p, Y)
    if n == 0: return Lo
    Lc = _lvlcurr(p, Y)
    if n >= PROVEN_N:
        if Lc >= Lo: return (Lo + S_M1 * (Lc - Lo)) if ((Lc - Lo) >= TOL_M1 and _radq(p, Y, Lo)) else Lo
        drop = Lo - Lc
        if drop <= DOWN_TOL: return Lo
        sw = float(np.clip((drop - DOWN_TOL) / 5, 0, 1)); return (1 - sw) * Lo + sw * Lc * _agemult(cp._age_asof(p, Y))
    c = n / PROVEN_N; return c * Lc + (1 - c) * _par_prior(p, Y)
def _inferM1(p, Y):
    L0 = _coreM1(p, Y); eo = _eo(p, Y)
    if eo <= 0: return L0
    avs = [x['avg'] for x in p['scoring'] if x.get('games', 0) >= 6 and (cp.debutyr(p) - 1) < x['year'] <= Y]
    if not avs: return L0
    bar = MA.REPL.get(MA.gfut(p), 0.0) - 3.0; N = Y - cp.debutyr(p) + 1
    return (1 - eo) * L0 + eo * min(L0, max(_upS(max(avs) - bar, N), _lvlcurr(p, Y)))
def _effs(p, Y): return sum(min(x['games'] / GCAP, 1.0) for x in p['scoring'] if x['games'] >= 6 and (cp.debutyr(p) - 1) < x['year'] <= Y)
def _v7(bb, p, Y):
    bb = list(bb); m = bb[2]; a = cp._age_asof(p, Y); cB = 0.47 * float(np.clip((_effs(p, Y) - 1) / 3, 0, 1))
    asc = float(np.interp(a, [20, 22, 24, 27], [1.0, .76, .58, .40]))
    bb[3] = m + (1 - cB) * (bb[3] - m); bb[4] = m + (1 - cB) * (bb[4] - m); bb[5] = m + asc * (bb[5] - m); return bb
def _b6fix(p, Y=2026):
    bb = b6_orig(p, Y)
    try: return _v7(bb, p, Y)
    except Exception: return bb
_sav = cp._lvl_eff
cp._lvl_eff = _inferM1; g['b6'] = _b6fix
rz = byname('Connor Rozee')
ov26, ov25 = E(rz, 2026), E(rz, 2025)
FIX['on'] = True
ovf26, ovf25 = E(rz, 2026), E(rz, 2025)
FIX['on'] = False
cp._lvl_eff = _sav; g['b6'] = b6_orig
OUT['m1v7_interaction'] = {'A3_overlay_base': round(ov26 / ov25, 3), 'A3_overlay_fix': round(ovf26 / ovf25, 3)}
print('== M1+v7 interaction (Rozee):', OUT['m1v7_interaction'], '==')
cp._exposure = _exp0
dst = '/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_ask3_scoped_out.json'
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True, default=float)
print('wrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
