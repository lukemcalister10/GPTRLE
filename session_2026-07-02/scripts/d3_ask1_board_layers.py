#!/usr/bin/env python3
# D3 ASK 1 — BOARD-path layer enumeration + toggle-off repricing + board-path gate pricing.
# SCRATCH: no engine/store edits. Replicates the EXPORT value path (rl_model module + wire_redesign
# -> TR.production_value), which is what rl_app_data.json ships as `v` and the JS displays verbatim
# (fallback valuePlayer chain is DEAD for every player with v != null — _engine_block_v23.js:97).
import os, sys, io, json, math, contextlib, hashlib
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
RA = '/home/claude/rl_workspace/rl_after'
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/user/afl-rl-engine/vendor']
os.chdir(RA)
import numpy as np
OUT = {}
with contextlib.redirect_stdout(io.StringIO()):
    import rl_model as MAmod            # module import == what wire_redesign/PR/TR bind to
LEGACY = {p['key']: p['_v'] for p in MAmod.players}          # pre-wire legacy v3 board values
with contextlib.redirect_stdout(io.StringIO()):
    import wire_redesign as W
    cm = W.wire()                        # baseline wire over MA.players (BASE_REF=2026)
MA = W.MA; TR = W.TR; rd = W.rd; PR = W.PR; cp = W.cp
players = MA.players
BASE = {p['key']: float(p['_v']) for p in players}

def sweep(tag):
    MA.BASE_REF = MA.AGE_REF = 2026; MA._pe_clear()
    out = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for p in players:
            try: out[p['key']] = float(TR.production_value(p, cm))
            except Exception: out[p['key']] = None
    return out

# sanity: un-patched recompute must reproduce the wire baseline exactly
chk = sweep('sanity')
mx = max(abs(chk[k] - BASE[k]) for k in BASE if chk[k] is not None)
print(f'sanity recompute max|delta| = {mx}')
assert mx == 0.0, 'harness does not reproduce the wire baseline'

NAME = {p['key']: (p['player'], MA.gfut(p)) for p in players}
def report(tag, vals, note):
    dd = [(k, BASE[k], vals[k]) for k in BASE if vals.get(k) is not None]
    moved = [(k, b, v) for k, b, v in dd if abs(v - b) > 0.5]
    tot = sum(b for _, b, _ in dd); dtot = sum(abs(v - b) for _, b, v in dd)
    top = sorted(moved, key=lambda t: -abs(t[2] - t[1]))[:10]
    OUT[tag] = {'note': note, 'n_moved': len(moved), 'n_players': len(dd),
                'pct_board_value_moved': round(100.0 * dtot / tot, 3),
                'top10': [{'player': NAME[k][0], 'pos': NAME[k][1], 'base': round(b), 'toggled': round(v),
                           'd': round(v - b), 'd_pct': round(100 * (v - b) / max(b, 1e-9), 1)} for k, b, v in top]}
    print(f'[{tag}] moved={len(moved)}/{len(dd)}  sum|d|/sum={OUT[tag]["pct_board_value_moved"]}%')

# L-A RUCK_TAX off
sav = rd.RUCK_TAX; rd.RUCK_TAX = 0.0
report('L_rucktax_off', sweep('rucktax'), 'tax 0.25 on established RUCs unrealised value (dist_redesign.py:110)')
rd.RUCK_TAX = sav
# L-B REPL_DROP off (uniform -3 acquirable-replacement recalibration)
sav = rd.REPL_DROP; rd.REPL_DROP = {}
report('L_repldrop_off', sweep('repl'), 'uniform -3 REPL around band pricing (dist_redesign.py:26-31)')
rd.REPL_DROP = sav
# L-C pedigree soft floor off
sav = rd._floor_w; rd._floor_w = lambda p: 0.0
report('L_softfloor_off', sweep('floor'), 'lift-only pedigree floor, young non-RUC (dist_redesign.py:66-95)')
rd._floor_w = sav
# L-D Brodie x0.5 off (python side; the JS brodieBase mirror is dead)
sav = MA.brodie_sig; MA.brodie_sig = lambda p: False
report('L_brodie_off', sweep('brodie'), 'role-reliability x0.5, non-RUC 5+yr never-durable level>=80 (rl_model.py:641)')
MA.brodie_sig = sav
# L-E tail restoration off (pre-debut MID/KEY_FWD/GEN_DEF upper-tail)
sav = TR.restore; TR.restore = lambda band, p, Y=2026, _w=None: band
report('L_tailrestore_off', sweep('tail'), 'pre-debut upper-quantile restore, picks<=46 (tail_restore.py:110)')
TR.restore = sav
# L-F RUC scorer-borrow pool off (pre-debut RUC -> plain rval)
vals = dict(BASE)
MA.BASE_REF = MA.AGE_REF = 2026; MA._pe_clear()
with contextlib.redirect_stdout(io.StringIO()):
    for p in players:
        if MA.level_now(p) is None and MA.gfut(p) == 'RUC':
            try: vals[p['key']] = float(TR.rval(p, cm))
            except Exception: vals[p['key']] = None
report('L_rucpool_off', vals, 'pre-debut RUC priced off scorer-pool shape at RUC level (tail_restore.py:157-162)')
# L-G lens tilt: verify inert at default lens ('bal' -> 1.0 for all)
lt = [MA.lens_tilt(p, 'bal') for p in players]
OUT['L_lenstilt'] = {'note': "ev*lens_tilt(p,lens) in redesign_value; board exports lens='bal'",
                     'inert_at_bal': bool(all(x == 1.0 for x in lt))}
print('[L_lenstilt] inert at bal:', OUT['L_lenstilt']['inert_at_bal'])
# L-H the WIRE overwrite itself (wired router vs legacy rl_model _v)
report('L_wire_off', {k: float(v) for k, v in LEGACY.items() if v is not None},
       'wire_redesign.wire overwrites _v with TR.production_value; off = legacy v3 chain (rl_export.py:17)')

# ---------- board-path gate pricing (INTERIM RULER, 1c) ----------
ALIAS = {'Josh Weddle': 'Joshua Weddle', 'Dan Annable': 'Daniel Annable'}
def byname(nm):
    nm = ALIAS.get(nm, nm)
    hits = [p for p in players if p['player'] == nm]
    if len(hits) != 1: raise LookupError(f'{nm}: {len(hits)} matches')
    return hits[0]
def BV(nm): return BASE[byname(nm)['key']]
def BV25(nm):
    p = byname(nm)
    MA.BASE_REF = MA.AGE_REF = 2025; MA._pe_clear()
    with contextlib.redirect_stdout(io.StringIO()):
        v = float(TR.production_value(p, cm, Y=2025))
    MA.BASE_REF = MA.AGE_REF = 2026; MA._pe_clear()
    return v
GB = {}
def g(gid, st, det):
    GB[gid] = (st, det); print(f'  {gid:4s} {st:8s} {det}')
print('=== BOARD-path gates (same definitions, export values) ===')
g('A1', 'PASS' if BV('Willem Duursma') > BV('Zeke Uwland') else 'FAIL',
  f"Duursma {BV('Willem Duursma'):.0f} vs Uwland {BV('Zeke Uwland'):.0f}")
cu, wa, we = BV('Paul Curtis'), BV('Josh Ward'), BV('Joshua Weddle')
g('A2', 'PASS' if (cu >= 0.9 * wa and we > wa) else 'FAIL',
  f'Curtis {cu:.0f} vs 0.90xWard {0.9*wa:.0f} (ratio {cu/wa:.3f}); Weddle {we:.0f} vs Ward {wa:.0f} [AMENDED]')
for gid, nm, fr in [('A3', 'Connor Rozee', 0.80), ('A10', 'Charlie Curnow', 0.70)]:
    v26, v25 = BV(nm), BV25(nm); r = v26 / max(v25, 1e-9)
    g(gid, 'PASS' if r >= fr else 'FAIL', f'{nm}: 2026={v26:.0f} 2025={v25:.0f} ratio={r:.2f} (need>={fr})')
board = sorted(((v, k) for k, v in BASE.items() if v is not None), key=lambda t: -t[0])
rank = next(i for i, (_, k) in enumerate(board, 1) if k == byname('Harley Reid')['key'])
g('A4', 'PASS' if rank <= 40 else 'FAIL', f'Harley Reid rank={rank} v={BV("Harley Reid"):.0f}')
a5 = [('Jack Ginnivan', 1600), ('Jake Bowey', 2100), ('Nick Blakey', 2600)]
g('A5', 'PASS' if all(BV(n) > f for n, f in a5) else 'FAIL',
  '; '.join(f'{n}={BV(n):.0f} (floor {f})' for n, f in a5))
def cohort(grp):
    o = []
    for p in players:
        if p.get('_pickless') or BASE.get(p['key']) is None: continue
        if MA.gfut(p) == grp and (2026 - int(p.get('year') or 0)) in (1, 2, 3):
            o.append((math.log(float(MA.effpk(p))), BASE[p['key']]))
    return o
rucs, mids = cohort('RUC'), cohort('MID')
mx_ = np.array([x for x, _ in mids]); mv_ = np.array([v for _, v in mids])
ksm = lambda x, bw=0.6: float(np.dot(np.exp(-0.5 * ((mx_ - x) / bw) ** 2), mv_) / np.exp(-0.5 * ((mx_ - x) / bw) ** 2).sum())
mr, mm = float(np.median([v for _, v in rucs])), float(np.median([ksm(x) for x, _ in rucs]))
g('A6', 'PASS' if mr <= mm else 'FAIL', f'RUC med={mr:.0f} (n={len(rucs)}) vs MID kernel med={mm:.0f} (n={len(mids)})')
g('A7', 'PASS', 'position-field gate — path-independent (same store fields)')
b_, t_ = BV('Sam Berry'), BV('Elijah Tsatas')
g('A8', 'PASS' if b_ > 2 * t_ else 'FAIL', f'Berry={b_:.0f} vs 2xTsatas={2*t_:.0f}')
g('A9', 'PASS' if BV('Jack Ginnivan') > BV('Josh Ward') else 'FAIL',
  f'Ginnivan {BV("Jack Ginnivan"):.0f} vs Ward {BV("Josh Ward"):.0f}')
g('A11', 'PASS' if BV('Jacob Farrow') > BV('Dylan Patterson') and BV('Sam Cumming') > BV('Daniel Annable') else 'FAIL',
  f"Farrow {BV('Jacob Farrow'):.0f}/Patterson {BV('Dylan Patterson'):.0f}; Cumming {BV('Sam Cumming'):.0f}/Annable {BV('Daniel Annable'):.0f}")
g('A12', 'PASS' if BV('Tobie Travaglia') > BV('Christian Moraes') and BV('Josh Smillie') > BV('Patrick Retschko') else 'FAIL',
  f"Travaglia {BV('Tobie Travaglia'):.0f}/Moraes {BV('Christian Moraes'):.0f}; Smillie {BV('Josh Smillie'):.0f}/Retschko {BV('Patrick Retschko'):.0f}")
pk1, pk8 = float(MA.PVC[1]), float(MA.PVC[8])
g('A13', 'PENDING', 'advisory: ' + '; '.join(f'{n}={BV(n):.0f}' for n in ('George Wardlaw', 'Levi Ashcroft')) + f' vs PVC[1]={pk1:.0f}')
g('A14', 'PENDING', 'advisory: ' + '; '.join(f'{n}={BV(n):.0f}' for n in ('Trent Rivers', 'Zach Reid', 'Jase Burgoyne')) + f' vs PVC[8]={pk8:.0f}')
KMAX = cp.KMAX
off = []
for p in players:
    if p.get('_pickless') or int(p.get('year') or 0) not in (2024, 2025): continue
    v = BASE.get(p['key'])
    if v is None: continue
    dv = float(MA.PVC[min(MA.effpk(p), KMAX)])
    if v < 0.25 * dv: off.append((p['player'], round(v), round(dv)))
g('B5', 'PASS' if not off else 'FAIL', f'{len(off)} yr1-2 below 0.25x draftval; worst: ' +
  '; '.join(f'{n}={v}/dv{d}' for n, v, d in sorted(off, key=lambda t: t[1] / t[2])[:3]))
GRPPOS = {}
for r in MA.data:
    gg = MA.GRP.get(r.get('pos'))
    if gg and gg not in GRPPOS: GRPPOS[gg] = r['pos']
def ramp_p(gm):
    return {'player': 'b6-synth', 'key': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025,
            'dob': '2006-03-01', 'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []),
            '_pos_now': None, '_fut': []}
try:
    MA.BASE_REF = MA.AGE_REF = 2026; MA._pe_clear()
    with contextlib.redirect_stdout(io.StringIO()):
        vals6 = [float(TR.production_value(ramp_p(gm), cm)) for gm in range(0, 15)]
    steps = [vals6[i + 1] - vals6[i] for i in range(14)]
    dips = [(i, round(s)) for i, s in enumerate(steps) if s < -1.0]
    T = vals6[6] - vals6[0]
    big = [(i, round(s)) for i, s in enumerate(steps[:6]) if s > 0.5 * max(T, 1.0)]
    ok = (not dips) and T > 0 and not big and (vals6[3] - vals6[0]) >= 0.25 * T
    g('B6', 'PASS' if ok else 'FAIL', f'ramp={[round(v) for v in vals6]}; dips={dips or "none"}; T={T:+.0f}; steps>50%T={big or "none"}')
except Exception as ex:
    g('B6', 'ERROR', f'{type(ex).__name__}: {ex}')
OUT['board_gates'] = {k: {'status': s, 'detail': d} for k, (s, d) in GB.items()}
OUT['population'] = {'board_players': len(players), 'store_rows': len(MA.data)}
OUT['base_values'] = {k: round(v, 2) for k, v in BASE.items() if v is not None}
OUT['legacy_values'] = {k: round(float(v), 2) for k, v in LEGACY.items() if v is not None}
dst = '/home/user/afl-rl-engine/session_2026-07-02/scripts/d3_ask1_board_out.json'
json.dump(OUT, open(dst, 'w'), indent=1, sort_keys=True)
print('wrote', dst, 'md5', hashlib.md5(open(dst, 'rb').read()).hexdigest()[:8])
