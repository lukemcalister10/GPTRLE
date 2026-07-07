"""DIAG-B rev3 ASK 5b/5c/5d — 2025 cohort Yr1 shortfall decomposition at BAKE CANDIDATE v2 (4a134d05).
ONE engine load; sequential evals; counterfactuals are RUNTIME patches in this process only — no engine
file is modified. Outputs: /home/user/afl-rl-engine/session_2026-07-03/d8_2025_decomposition.md
"""
import io, contextlib, json, math, numpy as np
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA = g['MA']; cp = g['cp']; PR = g['PR']; ev = g['ev']; ev_prefloor = g['ev_prefloor']
raw_ev = g['raw_ev']; price6 = g['price6']; b6 = g['b6']; iso_corr = g['iso_corr']
nseas0 = g['nseas']; draftval = g['draftval']; SITOUT_RETAIN = g['SITOUT_RETAIN']
_sitout_cls = g['_sitout_cls']; _nqual0 = g['_nqual']; recover = g['recover']
FE = 14.0 / 24.0  # season progress at the store cut (R14 of 24)

out = []
def P(s=''): out.append(s); print(s, flush=True)

# ---- cohort selection: byte-match the matrix builder's eligibility + dedup ----
def eligible(p): return MA.GRP.get(p.get('pos')) and not p.get('_double_count') and not p.get('_phantom') and not p.get('_pvc_exclude')
best = {}
for p in MA.data:
    if not eligible(p): continue
    k = (p.get('key') or MA.slug(p['player']), p.get('type'), p.get('year'))
    if k not in best or len(p['scoring']) > len(best[k]['scoring']): best[k] = p
players = list(best.values())
coh25 = [p for p in players if p.get('year') == 2025 and p.get('type') in ('ND', 'RD')]
P(f'2025 ND+RD cohort: n={len(coh25)} (expect 64)')

def g26(p): return sum(x['games'] for x in p['scoring'] if x['year'] == 2026)
def avg26(p):
    r = [x for x in p['scoring'] if x['year'] == 2026 and x['games'] > 0]
    return r[0]['avg'] if r else 0.0

# ---- MA.PVC live check vs matrix draftvals (ASK 3 'live curve' requirement) ----
rec = json.load(open('/home/user/afl-rl-engine/data/s4_matrix_v2_4a134d05.json'))
R = list(rec.values())
mkey = {(r['player'], r['year'], r['type']): r for r in R}
mm = 0
for r in R:
    if r['year'] == 2020 and r['type'] in ('ND', 'RD') and not r.get('pickless'):
        if r['draftval'] != round(MA.PVC[min(r['pick'], 70)]): mm += 1
P(f'PVC live check (2020 cohort): matrix draftval vs live MA.PVC mismatches = {mm}')

# ---- book-vs-board: fresh v2 ev() vs matrix ASOF-2026 for all 64 ----
base = {}; diffs = []
for p in coh25:
    v = ev(p, 2026); base[id(p)] = v
    mr = mkey.get((p['player'], 2025, p['type']))
    if mr and mr['cur'] is not None: diffs.append(abs(v - mr['cur']))
S0 = sum(base.values())
P(f'BASE v2 sum = {round(S0)} (book 37875) · board-vs-book per-player |diff|: max={max(diffs)}, n_matched={len(diffs)}')

# ---- games-bucket census, and prior-cohort Yr1 sit-out share for contrast ----
buck = {'0g': [], '1-5g': [], '6-10g': [], '11+g': []}
for p in coh25:
    gg = g26(p)
    buck['0g' if gg == 0 else '1-5g' if gg <= 5 else '6-10g' if gg <= 10 else '11+g'].append(p)
P('\nGAMES CENSUS (2026 season, 14 rounds possible):')
for k, v in buck.items():
    P(f'  {k:6s}: n={len(v):3d} · draftval sum {round(sum(draftval(p) for p in v)):6d} · v2 value sum {round(sum(base[id(p)] for p in v)):6d}')
for C in (2023, 2024):
    cohC = [p for p in players if p.get('year') == C and p.get('type') in ('ND', 'RD')]
    sat = sum(1 for p in cohC if not any(x['games'] >= 6 for x in p['scoring'] if x['year'] == C + 1))
    P(f'  contrast {C} cohort END-of-Yr1 ({C+1}, 24 rounds): {sat}/{len(cohC)} had no >=6g season (sit-out-classed)')
sat25 = sum(1 for p in coh25 if nseas0(p, 2026) == 0)
P(f'  2025 cohort at R14: {sat25}/{len(coh25)} sit-out-classed (nseas==0, bar = >=6 games UNPRORATED)')

# ---- counterfactual machinery (runtime patches; restore after each) ----
LR0 = cp.LEVEL_RAMP; PRAMP0 = g['POLE_RAMP']; MFE0 = g['M3_FE']
def nseas_pro(p, Y=2026):  # sit-out/qual bar prorated to season progress for the in-progress season only
    return sum(1 for x in p['scoring'] if x['year'] <= Y and x['games'] >= (6 * FE if x['year'] == 2026 else 6))
def nqual_pro(p, Y):
    return sum(1 for x in p['scoring'] if (cp.debutyr(p) - 1) < x['year'] <= Y and x['games'] >= (10 * FE if x['year'] == 2026 else 10))
def run_all(tag):
    s = 0; vals = {}
    for p in coh25:
        v = ev(p, 2026); vals[id(p)] = v; s += v
    P(f'  {tag:34s} sum={round(s):6d}  delta vs base={round(s - S0):+6d}')
    return vals, s
def restore():
    cp.LEVEL_RAMP = LR0; g['POLE_RAMP'] = PRAMP0; g['M3_FE'] = MFE0
    g['nseas'] = nseas0; g['_nqual'] = _nqual0

P('\nCOHORT COUNTERFACTUALS (runtime patches, this process only — engine files untouched):')
P(f'  {"BASE v2 (as shipped)":34s} sum={round(S0):6d}')
g['nseas'] = nseas_pro; cf_sit, S_sit = run_all('CF1 sit-out bar prorated (6->3.5)'); restore()
g['POLE_RAMP'] = PRAMP0 * FE; cf_pole, S_pole = run_all('CF2 POLE_RAMP prorated (22->12.8)'); restore()
cp.LEVEL_RAMP = LR0 * FE; cf_lvl, S_lvl = run_all('CF3 LEVEL_RAMP prorated (14->8.2)'); restore()
g['_nqual'] = nqual_pro; cf_nq, S_nq = run_all('CF4 nqual bar prorated (10->5.8)'); restore()
g['nseas'] = nseas_pro; g['POLE_RAMP'] = PRAMP0 * FE; cp.LEVEL_RAMP = LR0 * FE; g['_nqual'] = nqual_pro
cf_c, S_c = run_all('CF5 = CF1+CF2+CF3+CF4 combined'); restore()

# CF6: full-season-equivalent games (g26 -> g26*24/14, avg unchanged, M3 off = season complete)
saved = {}
for p in coh25:
    rows = [x for x in p['scoring'] if x['year'] == 2026]
    if rows: saved[id(p)] = rows[0]['games']; rows[0]['games'] = int(round(rows[0]['games'] / FE))
g['M3_FE'] = 1.0; MA._pe_clear()
cf_x, S_x = run_all('CF6 full-season-equiv games, M3 off')
for p in coh25:
    if id(p) in saved: [x for x in p['scoring'] if x['year'] == 2026][0]['games'] = saved[id(p)]
restore(); MA._pe_clear()

# ---- sample decomposition table (spans games buckets) ----
def pick_sample():
    smp = []
    for k, nwant in (('11+g', 3), ('6-10g', 2), ('1-5g', 3), ('0g', 2)):
        c = sorted(buck[k], key=lambda p: MA.effpk(p))
        take = [c[0], c[len(c)//2], c[-1]][:nwant] if len(c) >= nwant else c
        smp.extend(take[:nwant])
    return smp
sample = pick_sample()
P('\nSAMPLE DECOMPOSITION (v2, per player):')
hdr = ('player|pos|pick|g26|avg26|draftval|band_pr|pole_po|expgate|raw_ev|iso|e=raw*iso|sitout_branch|M3_s|prefloor|floor45|final|book|CF6_fullseas')
P(hdr)
rows_md = []
for p in sample:
    pos = MA.gfut(p); pk = MA.effpk(p); dv = draftval(p)
    pr = price6(p, b6(p, 2026), 2026)
    T = min(max(PR.tenure(p, 2026), 1), 6)
    po, par = g['par_pole'](pos, pk, T)
    a = MA.age(p)
    wage = 0.0 if pos == 'RUC' else float(np.clip(1 - ((a or 21) - 20) / 6, 0, 1))
    et = min(max(g['eff_ten'](p, 2026, PR.tenure(p, 2026)), 1), 6)
    tfade = float(np.interp(et, [1, 2, 3, 4, 5, 6], [1.00, 0.76, 0.40, 0.16, 0.05, 0.05]))
    expo = cp._exposure(p, 2026)
    expgate = 1.0 if _nqual0(p, 2026) >= g['PROVEN_N'] else min(1.0, expo / PRAMP0)
    rec_ = recover(cp._lvl_wt(p, 2026), par)
    raw = raw_ev(p, 2026); iso = iso_corr(pos, pk); e = raw * iso
    ns = nseas0(p, 2026)
    sit = f'YES ret={SITOUT_RETAIN[_sitout_cls(pos)][T-1]:.2f} -> {round(dv*SITOUT_RETAIN[_sitout_cls(pos)][T-1])}' if ns == 0 else 'no'
    s_m3 = g['_m3_s'](p, 2026)
    pf = ev_prefloor(p, 2026); fl = round(g['floor_frac'](1) * dv)
    fin = base[id(p)]
    mr = mkey.get((p['player'], 2025, p['type']))
    bookv = mr['cur'] if mr else None
    P(f"{p['player'][:20]}|{pos}|{pk}|{g26(p)}|{avg26(p):.1f}|{dv:.0f}|{pr:.0f}|{po:.0f}|{expgate:.2f}|{raw:.0f}|{iso:.3f}|{e:.0f}|{sit}|{s_m3:.2f}|{pf}|{fl}|{fin}|{bookv}|{cf_x[id(p)]}")
    rows_md.append((p, pos, pk, dv, pr, expgate, e, sit, s_m3, pf, fl, fin, bookv, cf_x[id(p)]))

# ---- comparable prior-cohort Yr1 players (2024 cohort end-of-Yr1 anchors, nearest pick) ----
P('\nCOMPARABLES (2024 cohort end-of-Yr1 anchor at nearest pick):')
m24 = [r for r in R if r['year'] == 2024 and r['type'] in ('ND', 'RD')]
for p, pos, pk, dv, pr, expgate, e, sit, s_m3, pf, fl, fin, bookv, cfx in rows_md:
    cand = sorted(m24, key=lambda r: (abs(r['pick'] - pk), r['player']))[:1]
    c = cand[0]
    P(f"  {p['player'][:20]:20s} pk{pk:3d} v2={fin:5d} CF6={cfx:5d} || 2024 comp {c['player'][:20]:20s} pk{c['pick']:3d} end-Yr1 anchor={round(c['anchor'] or 0):5d}")

json.dump({'base': {p['player']: base[id(p)] for p in coh25},
           'cf6': {p['player']: cf_x[id(p)] for p in coh25},
           'sums': {'base': S0, 'cf1_sit': S_sit, 'cf2_pole': S_pole, 'cf3_lvl': S_lvl, 'cf4_nq': S_nq, 'cf5_comb': S_c, 'cf6_extrap': S_x}},
          open('/home/user/afl-rl-engine/session_2026-07-03/d8_decomp_raw.json', 'w'), indent=1)
open('/home/user/afl-rl-engine/session_2026-07-03/d8_decomp_log.txt', 'w').write('\n'.join(out) + '\n')
print('DONE', flush=True)
