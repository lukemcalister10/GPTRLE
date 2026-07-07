#!/usr/bin/env python3
# D3 — ASK 2 (A2 residual decomposition) + ASK 3a (split bundle 2x2) + TASK Q diagnostics + G3-CLEAN data.
# SCRATCH: no engine/store edits. One engine load. ENG path (_merged_recover.ev), gate-script method (ev(p,Y)).
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
ev, MA, cp, PR = g['ev'], g['MA'], g['cp'], g['PR']
delisted, draftval = g['delisted'], g['draftval']
_nqual, _lvlcurr, _par_prior = g['_nqual'], g['_lvlcurr'], g['_par_prior']
PROVEN_N, DOWN_TOL, _agemult, _upS, _eo = g['PROVEN_N'], g['DOWN_TOL'], g['_agemult'], g['_upS'], g['_eo']
b6_orig = g['b6']
OUT = {}
def E(p, Y):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, Y))
def no26(p):
    q = copy.deepcopy(p); q['scoring'] = [r for r in p['scoring'] if r['year'] <= 2025]; return q
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)

# ---------- B. full 2026 EV dump (aggregate ruler + G3-CLEAN + Q5) ----------
rows = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if not MA.GRP.get(p.get('pos')) or p.get('_double_count'): continue
        try: v = float(ev(p, 2026))
        except Exception: v = None
        rows.append({'key': p.get('key'), 'player': p['player'], 'pos': MA.gfut(p), 'type': p.get('type'),
                     'pick': p.get('pick'), 'effpk': (None if p.get('_pickless') else MA.effpk(p)),
                     'year': p.get('year'), 'age': MA.age(p), 'retired': bool(p.get('_retired')),
                     'delisted': bool(delisted(p)), 'pickless': bool(p.get('_pickless')),
                     'cat': p.get('_cat'), 'g25': gyr(p, 2025), 'g26': gyr(p, 2026),
                     'nq26': _nqual(p, 2026), 'ev26': v,
                     'dv': (float(draftval(p)) if not p.get('_pickless') else None)})
OUT['eng_dump_n'] = len(rows)
json.dump(rows, open('/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_eng_dump.json', 'w'))
print('eng dump rows:', len(rows))

def byname(nm):
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, f'{nm}: {len(hits)}'
    return hits[0]
FOUR = ['Josh Ward', 'Paul Curtis', 'Joshua Weddle', 'Jack Ginnivan']
FIVE = ['Connor Rozee'] + FOUR

# ---------- C. baseline channel decomposition ----------
print('\n== C. baseline (at-head) channel decomposition ==')
OUT['baseline_decomp'] = {}
for nm in FIVE:
    p = byname(nm); q = no26(p)
    e25, e26, e26n = E(p, 2025), E(p, 2026), E(q, 2026)
    a, b = e26n - e25, e26 - e26n
    d = {'g25': gyr(p, 2025), 'g26': gyr(p, 2026), 'age': MA.age(p), 'effpk': MA.effpk(p),
         'nq25': _nqual(p, 2025), 'nq26': _nqual(p, 2026),
         'ev25': e25, 'ev26': e26, 'ev26_no26row': e26n,
         'ch_a_decay_age': round(a), 'ch_b_level26': round(b),
         'a_pct_of_25': round(100 * a / e25, 1), 'b_pct_of_25': round(100 * b / e25, 1),
         'exp25': round(cp._exposure(p, 2025), 1), 'exp26': round(cp._exposure(p, 2026), 1),
         'lvlwt25': round(cp._lvl_wt(p, 2025), 1), 'lvlwt26': round(cp._lvl_wt(p, 2026), 1)}
    OUT['baseline_decomp'][nm] = d
    print(f"  {nm:16s} ev25={e25:5.0f} ev26={e26:5.0f} no26={e26n:5.0f}  a(decay/age)={a:+5.0f} ({d['a_pct_of_25']:+.1f}%)  b(level26)={b:+5.0f} ({d['b_pct_of_25']:+.1f}%)  exp {d['exp25']}->{d['exp26']}")

# ---------- D. ASK 3a split bundle: 2x2 factorial on the no-26-row player ----------
# E-axis = the year the _exposure clock reads (patch cp._exposure); A-axis = evaluation year (age/tenure/pricing).
EX = {'Y': None}
_exp0 = cp._exposure
def _expw(p, Y): return _exp0(p, EX['Y'] if EX['Y'] is not None else Y)
cp._exposure = _expw
def split22(q):
    v25 = E(q, 2025); v26 = E(q, 2026)
    EX['Y'] = 2025; v_age = E(q, 2026); EX['Y'] = 2026; v_exp = E(q, 2025); EX['Y'] = None
    am, em = v_age - v25, v_exp - v25
    return v25, v26, am, em, (v26 - v25) - am - em
print('\n== D. ASK 3a — split bundle (channel a decomposed): age/tenure-alone vs decay/exposure-alone ==')
OUT['split22'] = {}
for nm in FIVE:
    v25, v26, am, em, ix = split22(no26(byname(nm)))
    OUT['split22'][nm] = {'v25': v25, 'v26_no26row': v26, 'age_alone': round(am), 'exp_alone': round(em),
                          'interaction': round(ix), 'age_pct': round(100 * am / v25, 1), 'exp_pct': round(100 * em / v25, 1)}
    print(f"  {nm:16s} v25={v25:5.0f} v26n={v26:5.0f}  age/ten={am:+5.0f} ({100*am/v25:+.1f}%)  decay/exp={em:+5.0f} ({100*em/v25:+.1f}%)  interact={ix:+4.0f}")
# g<6 population (Task F def: 2025 >=10g, 2026 1-5g), bucketed by years-since-debut
pop = [p for p in MA.data if MA.GRP.get(p.get('pos')) and not p.get('_double_count') and not p.get('_retired')
       and not delisted(p) and gyr(p, 2025) >= 10 and 1 <= gyr(p, 2026) <= 5]
def bucket(p):
    ysd = 2026 - cp.debutyr(p) + 1
    return 'young(2-4)' if ysd <= 4 else ('mid(5-7)' if ysd <= 7 else 'old(8+)')
B = {}
for p in pop:
    q = no26(p)
    try: v25, v26, am, em, ix = split22(q)
    except Exception: continue
    if v25 <= 0: continue
    B.setdefault(bucket(p), []).append((am / v25, em / v25, ix / v25, (v26 - v25) / v25))
OUT['split22_cohorts'] = {}
print(f'  g<6 population n={len(pop)}')
for k in ['young(2-4)', 'mid(5-7)', 'old(8+)']:
    a = np.array(B.get(k, []))
    if not len(a): continue
    m = 100 * a.mean(axis=0)
    OUT['split22_cohorts'][k] = {'n': len(a), 'age_pct': round(m[0], 1), 'exp_pct': round(m[1], 1),
                                 'interact_pct': round(m[2], 1), 'total_pct': round(m[3], 1)}
    print(f"  {k:11s} n={len(a):2d}  age/ten={m[0]:+.1f}%  decay/exp={m[1]:+.1f}%  interact={m[2]:+.1f}%  total(a)={m[3]:+.1f}%")

# ---------- E. M1+v7 overlay (s4_matrix_M1v7.py injection, verbatim) ----------
print('\n== E. M1+v7 overlay ==')
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
    asc = float(np.interp(a, [20, 22, 24, 27], [1.0, 0.76, 0.58, 0.40]))
    bb[3] = m + (1 - cB) * (bb[3] - m); bb[4] = m + (1 - cB) * (bb[4] - m); bb[5] = m + asc * (bb[5] - m); return bb
_REAL = set(id(p) for p in MA.data)
_saved_lvl = cp._lvl_eff
def _b6fix(p, Y=2026):
    bb = b6_orig(p, Y)
    if id(p) in _REAL:
        try: return _v7(bb, p, Y)
        except Exception: return bb
    return bb
# validation targets (D2 Task A): Ward 1253 Curtis 1087 Weddle 1414 Ginnivan 1677
cp._lvl_eff = _inferM1; g['b6'] = _b6fix
tgt = {'Josh Ward': 1253, 'Paul Curtis': 1087, 'Joshua Weddle': 1414, 'Jack Ginnivan': 1677}
print('  overlay validation vs D2:')
OUT['overlay'] = {}
for nm in FOUR:
    p = byname(nm); v = E(p, 2026)
    print(f'   {nm:16s} {v:.0f} (D2 target {tgt[nm]})')
    OUT['overlay'][nm] = {'ev26_overlay': v, 'd2_target': tgt[nm]}
# overlay channel decomposition + M1-only / v7-only splits
for nm in FIVE:
    p = byname(nm); q = no26(p)
    e25, e26, e26n = E(p, 2025), E(p, 2026), E(q, 2026)
    cp._lvl_eff = _saved_lvl                    # v7-only
    v7only = E(p, 2026)
    g['b6'] = b6_orig; cp._lvl_eff = _inferM1   # M1-only
    m1only = E(p, 2026)
    g['b6'] = _b6fix                            # back to full overlay
    OUT['overlay'].setdefault(nm, {}).update({'ev25': e25, 'ev26': e26, 'ev26_no26row': e26n,
        'ch_a': round(e26n - e25), 'ch_b': round(e26 - e26n), 'a_pct': round(100 * (e26n - e25) / e25, 1),
        'b_pct': round(100 * (e26 - e26n) / e25, 1), 'ev26_m1only': m1only, 'ev26_v7only': v7only})
    print(f"  {nm:16s} OVERLAY ev25={e25:5.0f} ev26={e26:5.0f} no26={e26n:5.0f} a={e26n-e25:+5.0f} b={e26-e26n:+5.0f}  m1only={m1only:5.0f} v7only={v7only:5.0f}")
# matched genuine producers (pick+age matched), post-overlay
def producers_pool():
    o = []
    for p in MA.data:
        if not MA.GRP.get(p.get('pos')) or p.get('_double_count') or p.get('_retired') or delisted(p): continue
        if p.get('_pickless') or p['player'] in FOUR + ['Josh Weddle']: continue
        if _nqual(p, 2026) < 3: continue
        par = _par_prior(p, 2026)
        if par and cp._lvl_wt(p, 2026) >= 0.90 * par: o.append(p)
    return o
POOL = producers_pool()
OUT['matched'] = {}
for tgt_nm in ['Paul Curtis', 'Josh Ward']:
    t = byname(tgt_nm); tep, tage = MA.effpk(t), MA.age(t)
    scored = sorted(POOL, key=lambda p: abs(math.log(MA.effpk(p) / tep)) + abs((MA.age(p) or 23) - tage) * 0.25)[:5]
    tab = []
    for p in scored:
        tab.append({'player': p['player'], 'pos': MA.gfut(p), 'age': MA.age(p), 'effpk': MA.effpk(p),
                    'g25': gyr(p, 2025), 'g26': gyr(p, 2026), 'nq26': _nqual(p, 2026),
                    'ev26_overlay': E(p, 2026)})
    med = float(np.median([r['ev26_overlay'] for r in tab]))
    tv = E(t, 2026)
    OUT['matched'][tgt_nm] = {'target_overlay': tv, 'matched_median': med, 'vs_matched_pct': round(100 * tv / med, 1), 'table': tab}
    print(f"\n  {tgt_nm}: overlay {tv:.0f} vs matched median {med:.0f} ({100*tv/med:.0f}%)")
    for r in tab: print(f"    {r['player']:22s}{r['pos']:8s} age{r['age']} pk{r['effpk']:3d} g25/26 {r['g25']}/{r['g26']} nq{r['nq26']}  {r['ev26_overlay']:.0f}")
# Q1 diagnostics: Ward/Ginnivan M1/v7 terms at basis 2025 vs 2026
print('\n== Q1 diagnostics ==')
OUT['q1'] = {}
for nm in ['Josh Ward', 'Jack Ginnivan']:
    p = byname(nm); d = {}
    for Y in (2025, 2026):
        Lo = cp._lvl_eff_orig(p, Y); Lc = _lvlcurr(p, Y); e_ = _effs(p, Y); a_ = cp._age_asof(p, Y)
        d[str(Y)] = {'Lo': round(Lo, 1), 'Lc': round(Lc, 1), 'nq': _nqual(p, Y),
                     'M1_fires': bool((Lc - Lo) >= TOL_M1 and _radq(p, Y, Lo) and _nqual(p, Y) >= PROVEN_N and Lc >= Lo),
                     'effs': round(e_, 2), 'cB': round(0.47 * float(np.clip((e_ - 1) / 3, 0, 1)), 3),
                     'asc': round(float(np.interp(a_, [20, 22, 24, 27], [1.0, .76, .58, .40])), 3), 'age_asof': a_}
    OUT['q1'][nm] = d
    print(f'  {nm}: ' + json.dumps(d))
cp._lvl_eff = _saved_lvl; g['b6'] = b6_orig   # restore

# ---------- Q5 population reconcile ----------
allrows = rows
listed = [r for r in allrows if not r['retired'] and not r['delisted']]
listed_picked = [r for r in listed if not r['pickless'] and r['dv']]
OUT['q5'] = {'store_valid_pos_rows': len(allrows),
             'non_retired': sum(1 for r in allrows if not r['retired']),
             'listed': len(listed), 'listed_picked_with_dv': len(listed_picked),
             'pickless_listed': sum(1 for r in listed if r['pickless'])}
print('\n== Q5 ==', json.dumps(OUT['q5']))
# ---------- Q4 nine offenders entry paths ----------
NINE = ['Jack Watkins', 'Flynn Perez', 'Zac Banch', 'Flynn Young', 'Saad El-Hawli', 'Lachlan Blakiston',
        'Jack Hutchinson', 'Mani Liddy', 'Roan Steele']
OUT['q4'] = []
for nm in NINE:
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    for p in hits:
        OUT['q4'].append({'player': nm, 'type': p.get('type'), 'raw_pick': p.get('pick'),
                          'effpk': MA.effpk(p), 'cat': p.get('_cat'), 'year': p.get('year'),
                          'dv': float(draftval(p)), 'pickless': bool(p.get('_pickless'))})
print('== Q4 ==')
for r in OUT['q4']: print('  ', json.dumps(r))
# ---------- G3-CLEAN: by-year ev/dv percentile tracks, ND-only vs with-MSD/SSP ----------
def track(sel, label):
    per = {}
    for r in sel:
        if not r['dv'] or r['ev26'] is None or not r['year']: continue
        y = min(2026 - int(r['year']), 12)
        if y < 1: continue
        per.setdefault(y, []).append(r['ev26'] / r['dv'])
    ks = sorted(per)
    t = {y: {'n': len(per[y]), 'p5': round(float(np.percentile(per[y], 5)), 2),
             'p10': round(float(np.percentile(per[y], 10)), 2), 'p50': round(float(np.percentile(per[y], 50)), 2)} for y in ks}
    print(f'  [{label}] ' + ' '.join(f"y{y}:n{t[y]['n']}/p5 {t[y]['p5']}" for y in ks))
    return t
print('\n== G3-CLEAN tracks (listed, ev/draftval by years-in-system) ==')
OUT['g3_all'] = track(listed_picked, 'ALL listed+picked')
OUT['g3_nd'] = track([r for r in listed_picked if r['type'] == 'ND'], 'ND only')
OUT['g3_no_msd_ssp'] = track([r for r in listed_picked if r['type'] not in ('MSD', 'SSP')], 'excl MSD/SSP')
OUT['g3_msd_ssp'] = track([r for r in listed_picked if r['type'] in ('MSD', 'SSP')], 'MSD/SSP only')
dst = '/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_ask2_out.json'
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True, default=float)
print('\nwrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
