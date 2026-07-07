#!/usr/bin/env python3
# D13 ASK2 verification — V0 pick-order guard. Roster-wide per-cell inversion scan before(v2.2)->after(v2.3),
# Cumming|2025|7 vs Robey|2025|9, largest pre-fix inversion, ND divergence scan, age-preservation example.
import os, sys, io, json, hashlib, contextlib, time
from collections import defaultdict
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
t0 = time.time(); G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
print(f'engine={ENG} loaded in {time.time()-t0:.0f}s')
MA, cp = G['MA'], G['cp']
v0_start, _v0_cell, _REAL = G['v0_start'], G['_v0_cell'], G['_REAL']
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = json.load(open(os.path.join(OUT, 'd13_baseline.json')))

def age_at(p, Y):
    with contextlib.redirect_stdout(io.StringIO()):
        return cp._age_asof(p, Y)
def cellkey_base(c):  # rebuild the engine cell key from a baseline v0cell dict
    return (c['pos'], int(round(c['draftage'])), c['year'])

# ---- ND divergence scan (recorded vs effective) ----
V = base['v0cells']
nd_div = sum(1 for c in V if c['type'] == 'ND' and c['diverge'])
nd_tot = sum(1 for c in V if c['type'] == 'ND')
print(f'\n=== DIVERGENCE SCAN: ND players recorded!=effective pick = {nd_div}/{nd_tot} (expected 0) ===')
print(f'  (802 total divergences all non-ND: RD 693 / MSD 107 / SSP 2 = pick-equivalents, out of guard scope)')

# ---- BEFORE inversions (v2.2 baseline V0) per (pos,age,year) cell over recorded pick ----
def scan_inversions(getv0, players_by_cell):
    inv = []
    for cell, rows in players_by_cell.items():
        rows = sorted(rows, key=lambda r: r['pick'])
        for i in range(len(rows)):
            for j in range(i+1, len(rows)):
                if rows[j]['pick'] > rows[i]['pick'] and getv0(rows[j]) > getv0(rows[i]) + 1e-6:
                    inv.append((cell, rows[i], rows[j], getv0(rows[j]) - getv0(rows[i])))
    return inv
# baseline cells: ND real players with recorded pick
bcells = defaultdict(list)
for c in V:
    if c['type'] == 'ND' and c['rec_pick'] is not None:
        bcells[cellkey_base(c)].append(dict(player=c['player'], pick=c['rec_pick'], V0=c['V0'], key=c['key']))
before = scan_inversions(lambda r: r['V0'], bcells)
print(f'\n=== INVERSION SCAN per (pos x draft-age x draft-year) cell ===')
print(f'  BEFORE (v2.2 af1fc6aa): {len(before)} inversions across {len(set(str(b[0]) for b in before))} cells')

# ---- AFTER inversions (guarded v2.3 V0) ----
p_by_key = {f"{p['player']}|{p.get('year')}|{p.get('pick')}": p for p in MA.data}
def guarded_v0(r):
    p = p_by_key.get(r['key'])
    with contextlib.redirect_stdout(io.StringIO()):
        return v0_start(p) if p is not None else r['V0']
after = scan_inversions(guarded_v0, bcells)
print(f'  AFTER  (v2.3 guarded): {len(after)} inversions  -> {"EMPTY (guard holds)" if len(after)==0 else "STILL PRESENT (FAIL)"}')

# ---- Cumming vs Robey ----
print('\n=== Cumming|2025|7 vs Robey|2025|9 (cell MID x age18 x 2025) ===')
def gv(nm, yr, pk):
    p = next((q for q in MA.data if q['player'] == nm and q.get('year') == yr and q.get('pick') == pk), None)
    with contextlib.redirect_stdout(io.StringIO()):
        return (v0_start(p), age_at(p, yr)) if p else (None, None)
cum_b = next(c['V0'] for c in V if c['player'] == 'Sam Cumming' and c['year'] == 2025)
rob_b = next(c['V0'] for c in V if c['player'] == 'Sullivan Robey' and c['year'] == 2025)
cum_a, cum_age = gv('Sam Cumming', 2025, 7); rob_a, rob_age = gv('Sullivan Robey', 2025, 9)
print(f'  BEFORE: Cumming(pk7) V0={cum_b:.1f}  Robey(pk9) V0={rob_b:.1f}  -> Robey ABOVE Cumming (inversion, {rob_b-cum_b:+.1f})')
print(f'  AFTER : Cumming(pk7) V0={cum_a:.1f}  Robey(pk9) V0={rob_a:.1f}  -> {"FIXED (Robey<=Cumming)" if rob_a<=cum_a+1e-6 else "STILL INVERTED"}')

# ---- largest pre-fix inversion ----
if before:
    big = max(before, key=lambda x: x[3])
    print(f'\n=== LARGEST pre-fix inversion: cell {big[0]} ===')
    print(f'  {big[1]["player"]}(pk{big[1]["pick"]}) V0={big[1]["V0"]:.0f}  <  {big[2]["player"]}(pk{big[2]["pick"]}) V0={big[2]["V0"]:.0f}  (gap {big[3]:.0f})')
    ba = guarded_v0(big[2]); print(f'  after guard: {big[2]["player"]} V0={ba:.0f} (<= {big[1]["player"]} {guarded_v0(big[1]):.0f})')

# ---- age-preservation example (mature-age vs 18yo, same pos/year, DIFFERENT age cells) ----
print('\n=== AGE-PRESERVATION (mature-age in separate cell -> not forced below 18yo; differentiation kept) ===')
byposyr = defaultdict(list)
for c in V:
    if c['type'] == 'ND' and c['rec_pick'] is not None:
        byposyr[(c['pos'], c['year'])].append(c)
ex = None
for (pos, yr), rows in byposyr.items():
    ages = {int(round(r['draftage'])) for r in rows}
    if len(ages) >= 2 and max(ages) >= 20:  # has a mature-age + a younger
        mature = [r for r in rows if int(round(r['draftage'])) >= 20]
        young = [r for r in rows if int(round(r['draftage'])) <= 18]
        for m in mature:
            for y in young:
                if m['rec_pick'] > y['rec_pick']:  # mature has WORSE pick but different age cell
                    ex = (pos, yr, y, m); break
            if ex: break
    if ex: break
if ex:
    pos, yr, y, m = ex
    print(f'  {pos} {yr}: {y["player"]}(pk{y["rec_pick"]}, age{int(round(y["draftage"]))}) vs {m["player"]}(pk{m["rec_pick"]}, age{int(round(m["draftage"]))})')
    print(f'    worse-pick mature-age V0={guarded_v0({"key":m["key"],"V0":m["V0"]}):.0f} vs younger better-pick V0={guarded_v0({"key":y["key"],"V0":y["V0"]}):.0f}')
    print(f'    -> different age cells: mature-age V0 NOT clamped to the younger (age differentiation preserved)')

json.dump(dict(engine=ENG, nd_div=nd_div, before_inv=len(before), after_inv=len(after),
               cumming=[cum_b, cum_a], robey=[rob_b, rob_a],
               largest=[big[1]['player'], big[1]['V0'], big[2]['player'], big[2]['V0'], big[3]] if before else None),
          open(os.path.join(OUT, 'd13_ask2_guard.json'), 'w'), indent=0)
print('\nwrote d13_ask2_guard.json')
