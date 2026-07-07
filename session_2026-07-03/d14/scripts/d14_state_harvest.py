#!/usr/bin/env python3
# D13 three-column harvest — run against a given engine state (arg: state label). Harvests the board
# quantities the D13 report needs: panel, named anchors (board/V0/cls/pick/ns), the 54-set sit-out aggregate,
# the 2025 cohort aggregate, floor-saves, Tsatas/Berry, and (v2.3 only) the projected zero-game yr1/yr2
# retention values (Luke's non-increasing law on named players). Writes d13_state_<label>.json.
import os, sys, io, json, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
LABEL = sys.argv[1] if len(sys.argv) > 1 else 'v23'
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
MA, cp = G['MA'], G['cp']
ev, delisted = G['ev'], G['delisted']
_REAL = G.get('_REAL') or set(id(p) for p in MA.data)  # canonical: all store players are real (no synths in MA.data)
nseas_pro = G.get('nseas_pro') or G['nseas']  # canonical predates the prorated qualifier -> unprorated nseas
_sitout_cls = G.get('_sitout_cls') or (lambda pos: 'RUC' if pos == 'RUC' else ('KPP' if pos in ('KEY_FWD', 'KEY_DEF') else 'nonKPP'))
v0_start = G.get('v0_start')                  # canonical 8aed420a predates v0_start (old flat sit-out anchor)
ev_prefloor = G.get('ev_prefloor'); floor_frac = G.get('floor_frac')
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def gY(p, Y): return sum(x['games'] for x in p['scoring'] if x['year'] == Y)
def E(p):
    with contextlib.redirect_stdout(io.StringIO()): return ev(p)
def V0(p):
    if v0_start is None: return -1.0
    with contextlib.redirect_stdout(io.StringIO()): return v0_start(p)

# panel
PANEL = [('Nick Daicos', 7059), ('Marcus Bontempelli', 3101), ('Harry Sheezel', 7287), ('Max Gawn', 2126),
         ('Harley Reid', 3523), ('Josh Ward', 1782), ('Darcy Moore', 177), ('Taylor Goad', 545),
         ('Josh Smillie', 896), ('Will Green', 741)]
def find(nm):
    c = [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos')) and not p.get('_double_count')]
    return c[0] if c else None
panel = {nm: E(find(nm)) for nm, _ in PANEL if find(nm)}

# named anchors (exact where possible)
def anchor(nm, yr=None, pos=None):
    cs = [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos')) and not p.get('_double_count')]
    if yr: cs = [p for p in cs if p.get('year') == yr]
    if pos: cs = [p for p in cs if MA.gfut(p) == pos]
    out = {}
    for p in cs:
        out[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = dict(
            player=p['player'], year=p.get('year'), pick=p.get('pick'), effpk=MA.effpk(p),
            cls=_sitout_cls(MA.gfut(p)), pos=MA.gfut(p), ns=nseas_pro(p, 2026), g26=gY(p, 2026),
            V0=round(V0(p), 1), board=E(p))
    return out
anchors = {}
for nm in ['Annable', 'Dylan Patterson', 'Ison', 'Josh Smillie', 'Tsatas', 'Berry', 'Louis Emmett']:
    anchors.update(anchor(nm))
# Taylor (KPP/anchor) — the 2025 anchor Taylor
anchors.update(anchor('Taylor', yr=2025))

# 54-set: real sit-outs (ns==0), and 2025 cohort
sitouts = [p for p in MA.data if id(p) in _REAL and not p.get('_double_count') and MA.GRP.get(p.get('pos'))
           and not delisted(p) and nseas_pro(p, 2026) == 0 and (p.get('pick') or p.get('_ft'))]
coh2025 = [p for p in MA.data if id(p) in _REAL and not p.get('_double_count') and MA.GRP.get(p.get('pos'))
           and p.get('year') == 2025 and not delisted(p)]
sitout_rows = [dict(key=f"{p['player']}|{p.get('year')}|{p.get('pick')}", player=p['player'],
                    cls=_sitout_cls(MA.gfut(p)), effpk=MA.effpk(p), board=E(p)) for p in sitouts]
sit_agg = sum(r['board'] for r in sitout_rows)
coh_agg = sum(E(p) for p in coh2025)

# floor-saves (only where the floor + v0_start exist, i.e. v2.x)
fsaves = -1; fsaves_ruc = -1
if ev_prefloor is not None and floor_frac is not None and v0_start is not None:
    fsaves = 0; fsaves_ruc = 0
    with contextlib.redirect_stdout(io.StringIO()):
        for p in MA.data:
            if id(p) not in _REAL or p.get('type') != 'ND' or p.get('_retired') or p.get('_pickless') or delisted(p): continue
            yis = 2026 - int(p.get('year') or 0)
            if yis < 1: continue
            if ev_prefloor(p) < floor_frac(yis)*v0_start(p):
                fsaves += 1
                if MA.gfut(p) == 'RUC': fsaves_ruc += 1

out = dict(label=LABEL, engine=ENG, panel=panel, anchors=anchors,
           n_sitout=len(sitouts), sitout_agg=sit_agg, sitout_rows=sitout_rows,
           n_coh2025=len(coh2025), coh2025_agg=coh_agg, floor_saves=fsaves, floor_saves_ruc=fsaves_ruc)

# v2.3-only: projected zero-game yr1/yr2 (Luke's non-increasing law) using the wired surface
if '_R_surf' in G:
    _R_surf = G['_R_surf']
    proj = {}
    for nm in ['Annable', 'Dylan Patterson', 'Taylor', 'Ison', 'Josh Smillie']:
        cs = [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos')) and not p.get('_double_count')]
        if nm == 'Taylor': cs = [p for p in cs if p.get('year') == 2025]
        for p in cs:
            cls = _sitout_cls(MA.gfut(p)); v0 = V0(p); pk = MA.effpk(p)
            yr1 = _R_surf(cls, pk, 1)*v0; yr2 = _R_surf(cls, pk, 2)*v0
            proj[f"{p['player']}|{p.get('year')}"] = dict(cls=cls, pick=pk, V0=round(v0),
                yr1_zero=round(yr1), yr2_zero=round(yr2), noninc=bool(yr2 <= yr1+1e-6))
    out['projected'] = proj

json.dump(out, open(os.path.join(OUT, f'd13_state_{LABEL}.json'), 'w'), indent=0)
print(f'[{LABEL}] engine={ENG}  panel Daicos={panel.get("Nick Daicos")}  '
      f'54-set n={len(sitouts)} agg={sit_agg}  2025-cohort n={len(coh2025)} agg={coh_agg}  '
      f'floor-saves={fsaves} (RUC {fsaves_ruc})')
