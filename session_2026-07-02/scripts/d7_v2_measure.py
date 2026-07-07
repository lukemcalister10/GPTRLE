#!/usr/bin/env python3
# D7 — BAKE CANDIDATE v2 measurement (ONE engine load; run sequentially).
# Usage: python3 d7_v2_measure.py <label> <out.json> [RL_M3_FE via env]
# Reports: named rows (Rozee A3 exact ratio · Tsatas · Curtis/Ward A2 · Curnow A10 · Ward M1-TOL gap ·
# Gothard prefloor/final · A8 Berry/Tsatas · panel names) · full EV + PREFLOOR sweeps at 2026 ·
# pure-lower-bound verify (0 lowered / 0 non-ND moved) · FLOOR-SAVES rows · population reconciliation
# (sweep-population vs export-active 805) · legacy B5 offender count at final ev (expect 0 by construction).
import os, sys, io, json, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)

label, outp = sys.argv[1], sys.argv[2]
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, cp = G['ev'], G['MA'], G['cp']
draftval, delisted, nseas = G['draftval'], G['delisted'], G['nseas']
ev_pre = G.get('ev_prefloor')
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
CP = hashlib.md5(open('/home/claude/rl_workspace/forward_valuation/conditional_prior.py', 'rb').read()).hexdigest()[:8]
STORE = hashlib.md5(open('rl_model_data.json', 'rb').read()).hexdigest()[:8]
FE = G.get('M3_FE')

ALIAS = {'Josh Weddle': 'Joshua Weddle'}
def by(nm):
    nm = ALIAS.get(nm, nm)
    hits = [p for p in MA.data if p['player'] == nm and not p.get('_retired')]
    assert len(hits) == 1, f'match {nm}: {len(hits)}'
    return hits[0]
def E(nm, yr=2026):
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(by(nm), yr))
def gyr(p, y): return sum(r['games'] for r in p['scoring'] if r['year'] == y)

named = {}
for nm in ['Paul Curtis', 'Josh Ward', 'Josh Weddle', 'Sam Berry', 'Elijah Tsatas',
           'Jack Ginnivan', 'Jake Bowey', 'Nick Blakey', 'Willem Duursma', 'Zeke Uwland',
           'Harley Reid', 'Phoenix Gothard',
           'Nick Daicos', 'Marcus Bontempelli', 'Harry Sheezel', 'Max Gawn', 'Darcy Moore',
           'Taylor Goad', 'Josh Smillie', 'Will Green', 'Ryan Maric', 'Ed Langdon']:
    named[nm] = round(E(nm), 1)
for nm in ['Connor Rozee', 'Charlie Curnow']:
    named[nm + ' 2026'] = round(E(nm), 1)
    named[nm + ' 2025'] = round(E(nm, 2025), 1)
# Gothard prefloor (the staleness cap should still bind: cap fix is ASK 4, NOT in v2)
with contextlib.redirect_stdout(io.StringIO()):
    named['Phoenix Gothard PREFLOOR'] = round(float(ev_pre(by('Phoenix Gothard'), 2026)), 1)
# Ward M1-TOL knife-edge: gap = Lc - Lo vs TOL_M1
w = by('Josh Ward')
with contextlib.redirect_stdout(io.StringIO()):
    Lo = float(cp._lvl_eff_orig(w, 2026)); Lc = float(G['_lvlcurr'](w, 2026))
ward_tol = dict(Lo=round(Lo, 1), Lc=round(Lc, 1), gap=round(Lc - Lo, 1), TOL_M1=G['TOL_M1'],
                m1_lift_fires=bool((Lc - Lo) >= G['TOL_M1']))

# full sweeps at 2026: final ev + prefloor
EV, PRE = {}, {}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired'):
            continue
        try:
            EV[id(p)] = float(ev(p, 2026)); PRE[id(p)] = float(ev_pre(p, 2026))
        except Exception:
            EV[id(p)] = None; PRE[id(p)] = None

def in_floor_scope(p):
    return (p.get('type') == 'ND' and not p.get('_retired') and not p.get('_pickless')
            and not delisted(p) and (2026 - int(p.get('year') or 0)) >= 1)
lowered = [p['player'] for p in MA.data if not p.get('_retired')
           and PRE.get(id(p)) is not None and EV.get(id(p)) is not None and EV[id(p)] < PRE[id(p)] - 1e-9]
nonnd_moved = [p['player'] for p in MA.data if not p.get('_retired') and not in_floor_scope(p)
               and PRE.get(id(p)) is not None and EV.get(id(p)) is not None
               and abs(EV[id(p)] - PRE[id(p)]) > 1e-9]
saves = []
FLOORF = G['floor_frac']
for p in MA.data:
    if p.get('_retired') or not in_floor_scope(p):
        continue
    v0, v1 = PRE.get(id(p)), EV.get(id(p))
    if v0 is None or v1 is None or v1 <= v0 + 1e-9:
        continue
    yis = 2026 - int(p.get('year') or 0)
    saves.append(dict(player=p['player'], club=p.get('_club'), yis=yis, raw=round(v0, 1),
                      floor=round(FLOORF(yis) * draftval(p), 1), saved_to=round(v1),
                      lift=round(v1 - v0, 1), g26=gyr(p, 2026)))
saves.sort(key=lambda r: -r['lift'])

# legacy B5 offender count at FINAL ev (expect 0 by construction at v2)
B5F = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}
legacy_off = sum(1 for p in MA.data if not p.get('_retired') and in_floor_scope(p)
                 and EV.get(id(p)) is not None
                 and EV[id(p)] < B5F.get(2026 - int(p.get('year') or 0), .05) * draftval(p) - 1e-9)

# population reconciliation (ASK 5(i)): sweep population vs export-active
n_sweep = sum(1 for v in EV.values() if v is not None)
act = [p for p in MA.data if MA.active(p)] if hasattr(MA, 'active') else []
def dkey(p): return (p.get('key') or MA.slug(p['player'])) + ('|u' if p.get('_unplayed') and not p.get('key') else '')
best, order = {}, []
for p in act:
    k = dkey(p)
    if k not in best:
        order.append(k); best[k] = p
    else:
        rich = lambda q: (-(q['year'] or 9999), len(q['scoring']), 1 if q.get('pick') else 0)
        if rich(p) > rich(best[k]): best[k] = p
export_active = [best[k] for k in order]
exp_ids = set(id(p) for p in export_active)
sweep_ps = [p for p in MA.data if not p.get('_retired') and EV.get(id(p)) is not None]
extras = [p for p in sweep_ps if id(p) not in exp_ids]
missing = [p for p in export_active if id(p) not in set(id(q) for q in sweep_ps)]
recon = dict(n_sweep=n_sweep, n_export_active=len(export_active),
             extras_in_sweep=[dict(player=p['player'], type=p.get('type'), year=p.get('year'),
                                   pick=p.get('pick'), key=p.get('key'), club=p.get('_club'),
                                   double_count=bool(p.get('_double_count')),
                                   unplayed=bool(p.get('_unplayed')),
                                   last_listed=p.get('_last_listed'),
                                   has26=bool(p.get('_has26')),
                                   recent=bool(any(r['year'] >= 2024 for r in p['scoring'])) if p.get('scoring') else False)
                              for p in extras],
             missing_from_sweep=[p['player'] for p in missing])

out = dict(label=label, engine_md5=ENG, cp_md5=CP, store_md5=STORE, M3_FE=FE,
           named=named, ward_tol=ward_tol,
           a2_ratio=round(named['Paul Curtis'] / max(named['Josh Ward'], 1e-9), 4),
           a3_ratio=round(named['Connor Rozee 2026'] / max(named['Connor Rozee 2025'], 1e-9), 4),
           a8_ratio=round(named['Sam Berry'] / max(named['Elijah Tsatas'], 1e-9), 4),
           a10_ratio=round(named['Charlie Curnow 2026'] / max(named['Charlie Curnow 2025'], 1e-9), 4),
           floor=dict(lowered=lowered, nonnd_moved=nonnd_moved, n_saves=len(saves),
                      agg_lift=round(sum(r['lift'] for r in saves), 1), saves=saves),
           legacy_b5_offenders_at_final=legacy_off, recon=recon,
           evs={p['player'] + '|' + str(p.get('year')) + '|' + str(p.get('pick')): EV[id(p)]
                for p in MA.data if not p.get('_retired') and EV.get(id(p)) is not None},
           pres={p['player'] + '|' + str(p.get('year')) + '|' + str(p.get('pick')): PRE[id(p)]
                 for p in MA.data if not p.get('_retired') and PRE.get(id(p)) is not None})
json.dump(out, open(outp, 'w'), indent=1)
print(f"[{label}] engine={ENG} cp={CP} store={STORE} fE={FE}")
print(f"  A2 Curtis/Ward={out['a2_ratio']:.3f} ({named['Paul Curtis']:.0f}/{named['Josh Ward']:.0f}) | "
      f"A3 Rozee={out['a3_ratio']:.4f} ({named['Connor Rozee 2026']:.0f}/{named['Connor Rozee 2025']:.0f}) | "
      f"A8 Berry/Tsatas={out['a8_ratio']:.2f}x ({named['Sam Berry']:.0f}/{named['Elijah Tsatas']:.0f}) | "
      f"A10 Curnow={out['a10_ratio']:.3f} ({named['Charlie Curnow 2026']:.0f}/{named['Charlie Curnow 2025']:.0f})")
print(f"  Gothard prefloor={named['Phoenix Gothard PREFLOOR']:.0f} final={named['Phoenix Gothard']:.0f} | "
      f"Ward M1-TOL gap={ward_tol['gap']} vs {ward_tol['TOL_M1']} fires={ward_tol['m1_lift_fires']}")
print(f"  FLOOR: saves={len(saves)} agg_lift={out['floor']['agg_lift']:+.0f} lowered={len(lowered)} "
      f"nonND_moved={len(nonnd_moved)} | legacy-B5-offenders at final ev = {legacy_off}")
print(f"  RECON: sweep n={n_sweep} vs export-active n={len(export_active)} extras={len(recon['extras_in_sweep'])} "
      f"missing={len(recon['missing_from_sweep'])}")
print('wrote', outp, 'md5', hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8])
