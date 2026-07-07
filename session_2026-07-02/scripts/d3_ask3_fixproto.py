#!/usr/bin/env python3
# D3 ASK 3b-3d — DROP-FIX PROTOTYPE (design derivation; NOTHING WIRED — scratch overlay only).
# Lever (pinned mechanism): the _exposure decay clock runs at elapsed-season pace for the in-progress season.
#   w(yr) = 1.0 for the current season's own games; 0.72^(max(0, Y-yr-1) + f(Y)) for prior seasons,
#   f(Y) = elapsed fraction of season Y (1.0 for every completed season -> BYTE-EXACT reduction to status quo).
# ZERO touch of _lvl_wt (it keeps its own _swt reads); only cp._exposure is patched.
import os, sys, io, json, copy, math, contextlib, hashlib
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

# ---- f-hat derivation (finest store-derivable resolution + robustness band) ----
SEASON = 22.0
dur = [p for p in LISTED if gyr(p, 2025) >= 18]                     # durable = played ~every week last season
g26d = sorted(gyr(p, 2026) for p in dur)
med26 = float(np.median(g26d)); p90_26 = float(np.percentile(g26d, 90))
allg26 = [gyr(p, 2026) for p in LISTED if gyr(p, 2026) > 0]
f_med = med26 / SEASON
f_p90 = p90_26 / SEASON
f_max = max(allg26) / SEASON
g25d = [gyr(p, 2025) for p in dur]
f_ratio = med26 / float(np.median(g25d))
FHAT = round(f_med, 3)
OUT['fhat'] = {'f_median_durable_over22': round(f_med, 3), 'f_p90_over22': round(f_p90, 3),
               'f_max_over22': round(f_max, 3), 'f_ratio_med26_med25': round(f_ratio, 3),
               'n_durable': len(dur), 'med_g26_durable': med26, 'CHOSEN': FHAT}
print('f-hat variants:', json.dumps(OUT['fhat']))

# ---- the lever ----
_exp0 = cp._exposure
FIX = {'on': False, 'f': FHAT}
def _exposure_fix(p, Y):
    if not FIX['on']: return _exp0(p, Y)
    f = FIX['f'] if Y == 2026 else 1.0                              # only the in-progress season has f<1
    if f >= 1.0: return _exp0(p, Y)
    rows = cp._season_rows(p, Y)
    return float(sum(gm * (1.0 if yr == Y else cp.RECENCY_DECAY ** (max(0, Y - yr - 1) + f)) for yr, gm, _ in rows))
cp._exposure = _exposure_fix

# ---- 0. byte-exact reduction checks ----
named = ['Connor Rozee', 'Josh Ward', 'Paul Curtis', 'Joshua Weddle', 'Jack Ginnivan', 'Charlie Curnow']
FIX['on'] = False
base25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = True; FIX['f'] = 1.0
chk25 = {nm: E(byname(nm), 2025) for nm in named}
chk26_f1 = {nm: E(byname(nm), 2026) for nm in named}
FIX['on'] = False
base26 = {nm: E(byname(nm), 2026) for nm in named}
inert_hist = all(chk25[nm] == base25[nm] for nm in named)
inert_f1 = all(chk26_f1[nm] == base26[nm] for nm in named)
print(f'inert at f=1 (2026): {inert_f1}; inert historical (2025): {inert_hist}')
OUT['inertness'] = {'f1_2026_byte_exact': inert_f1, 'historical_2025_byte_exact': inert_hist}

# ---- 1. named players + A3/A10 under fix ----
FIX['f'] = FHAT; FIX['on'] = True
fix26 = {nm: E(byname(nm), 2026) for nm in named}
fix25 = {nm: E(byname(nm), 2025) for nm in named}
FIX['on'] = False
OUT['named'] = {}
print('\n== named under fix (f=%.3f) ==' % FHAT)
for nm in named:
    OUT['named'][nm] = {'base26': base26[nm], 'fix26': fix26[nm], 'd_pct': round(100 * (fix26[nm] - base26[nm]) / base26[nm], 1),
                        'base25': base25[nm], 'fix25': fix25[nm]}
    print(f'  {nm:16s} 2026 {base26[nm]:5.0f} -> {fix26[nm]:5.0f} ({OUT["named"][nm]["d_pct"]:+.1f}%)   2025 {base25[nm]:5.0f} -> {fix25[nm]:5.0f}')
a3_base = base26['Connor Rozee'] / base25['Connor Rozee']; a3_fix = fix26['Connor Rozee'] / fix25['Connor Rozee']
a10_base = base26['Charlie Curnow'] / base25['Charlie Curnow']; a10_fix = fix26['Charlie Curnow'] / fix25['Charlie Curnow']
OUT['gates'] = {'A3_base': round(a3_base, 3), 'A3_fix': round(a3_fix, 3), 'A3_need': 0.80,
                'A10_base': round(a10_base, 3), 'A10_fix': round(a10_fix, 3), 'A10_need': 0.70}
print(f'  A3 ratio {a3_base:.3f} -> {a3_fix:.3f} (need 0.80) | A10 {a10_base:.3f} -> {a10_fix:.3f} (need 0.70)')

# ---- 2. on-pace collateral (D1 bar: 11-14g in 2026; ZERO players >2%) ----
onpace = [p for p in LISTED if 11 <= gyr(p, 2026) <= 14]
res = []
for p in onpace:
    b = E(p, 2026); FIX['on'] = True; v = E(p, 2026); FIX['on'] = False
    if b > 0: res.append((p['player'], b, v, 100 * (v - b) / b))
mov = [r for r in res if abs(r[3]) > 2.0]
OUT['onpace'] = {'n': len(res), 'movers_gt2pct': len(mov), 'max_abs_pct': round(max(abs(r[3]) for r in res), 2),
                 'mean_pct': round(float(np.mean([r[3] for r in res])), 3),
                 'worst': [{'player': r[0], 'base': round(r[1]), 'fix': round(r[2]), 'pct': round(r[3], 2)}
                           for r in sorted(res, key=lambda r: -abs(r[3]))[:5]]}
print(f"\n== on-pace collateral: n={len(res)}, movers>2% = {len(mov)}, max|d| = {OUT['onpace']['max_abs_pct']}% ==")
for w in OUT['onpace']['worst']: print('   ', w)

# ---- 3. g<6 population under fix (cohort totals vs the -43/-30/-21 baseline) ----
pop = [p for p in LISTED if gyr(p, 2025) >= 10 and 1 <= gyr(p, 2026) <= 5]
def bucket(p):
    ysd = 2026 - cp.debutyr(p) + 1
    return 'young(2-4)' if ysd <= 4 else ('mid(5-7)' if ysd <= 7 else 'old(8+)')
BB = {}
for p in pop:
    b25 = E(p, 2025); b26 = E(p, 2026); FIX['on'] = True; v26 = E(p, 2026); FIX['on'] = False
    if b25 > 0: BB.setdefault(bucket(p), []).append((100 * (b26 - b25) / b25, 100 * (v26 - b25) / b25, 100 * (v26 - b26) / max(b26, 1)))
OUT['g6pop'] = {}
print('\n== g<6 population (drop vs 2025, base -> fix) ==')
for k in ['young(2-4)', 'mid(5-7)', 'old(8+)']:
    a = np.array(BB.get(k, []))
    if not len(a): continue
    OUT['g6pop'][k] = {'n': len(a), 'drop_base_pct': round(a[:, 0].mean(), 1), 'drop_fix_pct': round(a[:, 1].mean(), 1),
                       'lift_pct': round(a[:, 2].mean(), 1)}
    print(f"  {k:11s} n={len(a):2d}  drop {a[:,0].mean():+.1f}% -> {a[:,1].mean():+.1f}%  (lift {a[:,2].mean():+.1f}%)")

# ---- 4. B5 under fix ----
def b5_count():
    off = []
    for p in LISTED:
        if p.get('_pickless') or int(p.get('year') or 0) not in (2024, 2025): continue
        try: v = E(p, 2026)
        except Exception: continue
        if v < 0.25 * draftval(p): off.append(p['player'])
    return off
b5_base = b5_count(); FIX['on'] = True; b5_fix = b5_count(); FIX['on'] = False
OUT['b5'] = {'base': len(b5_base), 'fix': len(b5_fix)}
print(f'\n== B5 offenders: base {len(b5_base)} -> fix {len(b5_fix)} ==')

# ---- 5. B6 ramp under fix (synth has no prior seasons -> must be identical) ----
def ramp_p(gm):
    return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025, 'dob': '2006-03-01',
            'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []), '_pos_now': None, '_fut': []}
b6b = [E(ramp_p(gm), 2026) for gm in range(0, 15)]
FIX['on'] = True
b6f = [E(ramp_p(gm), 2026) for gm in range(0, 15)]
FIX['on'] = False
OUT['b6'] = {'identical': b6b == b6f}
print('== B6 ramp identical under fix:', b6b == b6f, '==')

# ---- 6. B1 splice check (cohorts 2019-2020 have a 2026 cell inside N1..7) ----
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
rises = []
for C in sorted({c for c, _ in S}):
    R = {N: 100.0 * S[(C, N)] / max(S[(C, 1)], 1e-9) for N in range(1, 8) if (C, N) in S}
    rises.append(max(R.get(N, 0) for N in (4, 5, 6)) > 100.0)
path_ok = all(pooled[N + 1] >= 0.95 * pooled[N] for N in range(1, ppk) if N + 1 in pooled)
b1_ok = all(rises) and ppk in (4, 5, 6) and pooled[ppk] > 100.0 and path_ok
OUT['b1_spliced'] = {'pass': b1_ok, 'pooled_peak_N': ppk, 'R_peak': round(pooled[ppk]), 'rises': f'{sum(rises)}/{len(rises)}',
                     'n_2026_cells_moved': sum(1 for d in deltas.values() if abs(d) > 0.5)}
print('== B1 with fixed 2026 cells spliced:', OUT['b1_spliced'], '==')

# ---- 7. M1+v7 interaction (overlay reconstruction from s4_matrix_M1v7.py; ~5% reproduction caveat applies) ----
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
OUT['m1v7_interaction'] = {'rozee_overlay_A3_base': round(ov26 / ov25, 3), 'rozee_overlay_A3_fix': round(ovf26 / ovf25, 3),
                           'overlay26_base': ov26, 'overlay26_fix': ovf26}
print('\n== M1+v7 interaction (Rozee):', OUT['m1v7_interaction'], '==')

# ---- 8. f-sensitivity on A3 (Rozee) ----
sens = {}
for f in [0.4, 0.5, 0.6, FHAT, 0.7, 0.8, 0.9]:
    FIX['f'] = f; FIX['on'] = True
    sens[round(f, 3)] = round(E(rz, 2026) / E(rz, 2025), 3)
    FIX['on'] = False
FIX['f'] = FHAT
OUT['a3_f_sensitivity'] = sens
print('A3 ratio vs f:', sens)

cp._exposure = _exp0
dst = '/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_ask3_out.json'
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True, default=float)
print('\nwrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
