#!/usr/bin/env python3
# DIAGNOSTIC A — READ-ONLY. One engine load; all evals sequential in this one process.
# Usage: diag_v2.py <label> <out.json>   (engine state = whatever sits in /home/claude/rl_workspace)
import os, sys, io, json, copy, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
label, outp = sys.argv[1], sys.argv[2]
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, cp, PR = G['ev'], G['MA'], G['cp'], G['PR']
draftval, delisted, nseas, bestlvl = G['draftval'], G['delisted'], G['nseas'], G['bestlvl']
raw_ev, iso_corr = G['raw_ev'], G['iso_corr']
SITOUT_RETAIN, _sitout_cls = G['SITOUT_RETAIN'], G['_sitout_cls']
ev_pre = G.get('ev_prefloor')            # v2 only; None at canonical
floor_frac = G.get('floor_frac')
ENG = hashlib.md5(open('_merged_recover.py','rb').read()).hexdigest()[:8]
CP = hashlib.md5(open('/home/claude/rl_workspace/forward_valuation/conditional_prior.py','rb').read()).hexdigest()[:8]
OUT = {'label': label, 'engine_md5': ENG, 'cp_md5': CP,
       'env_overrides': {k: os.environ.get(k) for k in ('RL_EXPO_F','RL_M3_FE') if os.environ.get(k)}}

def Q(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)

def g26(p): return sum(r['games'] for r in p['scoring'] if r['year'] == 2026)
def act(p): return not p.get('_retired')

# ---- resolve the seven players by surname, report every hit (name guard) ----
SURNAMES = ['Lord', 'Berry', 'Ginnivan', 'Annable', 'Cumming', 'Travaglia', 'Moraes']
matches = {}
for s in SURNAMES:
    hits = [p for p in MA.data if s.lower() in p['player'].lower() and act(p)]
    matches[s] = [{'player': p['player'], 'pick': p.get('pick'), 'cohort': p.get('year'),
                   'pos': MA.gfut(p), 'g26': g26(p)} for p in hits]
OUT['name_resolution'] = matches

def decomp(p, Y=2026):
    pos = MA.gfut(p); el = PR.tenure(p, Y); ns = nseas(p, Y); dv = draftval(p)
    par = PR.par_at(pos, min(MA.effpk(p), cp.KMAX), min(max(el, 1), 6))
    pr = bestlvl(p, Y) / max(1, par)
    base = Q(raw_ev, p, Y) * iso_corr(pos, MA.effpk(p))       # production-path value (pre-overlay)
    keyruc = pos in ('KEY_FWD', 'KEY_DEF', 'RUC')
    onset = 2 if ns == 0 else (4 if keyruc else 3)
    sit = ns == 0
    N = min(max(el, 1), 6)
    retain = SITOUT_RETAIN[_sitout_cls(pos)][N - 1] if sit else None
    stalled = (not sit) and el >= onset and ns <= 1
    medio = (not sit) and (not stalled) and el >= onset + 2 and pr < 0.55
    pre = Q(ev_pre, p, Y) if ev_pre else None
    fin = Q(ev, p, Y)
    yis = 2026 - int(p.get('year') or 0)
    ffrac = floor_frac(yis) if floor_frac else None
    return {'player': p['player'], 'pos': pos, 'pick': p.get('pick'), 'cohort': p.get('year'),
            'g26': g26(p), 'career_games': sum(r['games'] for r in p['scoring']),
            'el_tenure': el, 'nseas_ge6': ns, 'draftval': round(dv, 1),
            'base_prod_path': round(base, 1), 'sitout_fires': sit,
            'sitout_retain': retain, 'sitout_value': round(dv * retain) if sit else None,
            'stalled_fires': stalled, 'mediocre_fires': medio,
            'prefloor': pre, 'final': fin,
            'floor_frac': ffrac, 'floor_amount': (round(fin - pre, 1) if pre is not None else None)}

NAMED = ['Cooper Lord', 'Sam Berry', 'Jack Ginnivan', 'Sam Annable', 'Hugh Cumming',
         'Travaglia', 'Moraes']
rows = []
for want in NAMED:
    sur = want.split()[-1]
    hits = [p for p in MA.data if sur.lower() in p['player'].lower() and act(p)]
    for p in hits:
        rows.append(decomp(p))
OUT['decomp'] = rows

# ---- B6 ramp (identical construction to ship_gates_check) ----
GRPPOS = G['GRPPOS']
def ramp_p(gm):
    return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025,
            'dob': '2006-03-01', 'type': 'ND',
            'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []),
            'games': gm, '_pos_now': None, '_fut': []}
OUT['b6_ramp'] = {gm: round(Q(ev, ramp_p(gm), 2026)) for gm in range(0, 15)}

# ---- seam population sweep: active ND players with a partial 2026 season and ns==0 ----
seam, over = [], []
for p in MA.data:
    if not act(p) or delisted(p):
        continue
    try:
        g = g26(p); ns = nseas(p, 2026)
    except Exception:
        continue
    if ns == 0 and 1 <= g <= 5:
        try:
            q = copy.deepcopy(p)
            for r in q['scoring']:
                if r['year'] == 2026:
                    r['games'] = 6
            if isinstance(q.get('games'), (int, float)):
                q['games'] = q['games'] + (6 - g)
            v6 = Q(ev, q, 2026)
            vnow = Q(ev, p, 2026)
            vsm = vnow + (g / 6.0) * (v6 - vnow)
            seam.append({'player': p['player'], 'pos': MA.gfut(p), 'pick': p.get('pick'),
                         'cohort': p.get('year'), 'g26': g, 'el': PR.tenure(p, 2026),
                         'now': vnow, 'at6g': v6, 'smooth_est': round(vsm),
                         'distortion': round(vsm - vnow)})
        except Exception as ex:
            seam.append({'player': p['player'], 'err': str(ex)})
    elif ns == 1 and 6 <= g <= 8:
        # sole qualifying season is the in-progress one: just OVER the seam
        only26 = all(r['games'] < 6 for r in p['scoring'] if r['year'] < 2026)
        if only26:
            over.append({'player': p['player'], 'pos': MA.gfut(p), 'pick': p.get('pick'),
                         'cohort': p.get('year'), 'g26': g, 'el': PR.tenure(p, 2026),
                         'now': Q(ev, p, 2026)})
OUT['seam_under'] = sorted([s for s in seam if 'distortion' in s],
                           key=lambda r: -abs(r['distortion']))
OUT['seam_err'] = [s for s in seam if 'err' in s]
OUT['seam_over'] = sorted(over, key=lambda r: r['g26'])

# ---- what-if for haircut-firers among the seven (scratch, illustrative) ----
FE = 14.0 / 24.0
wi = []
for r in rows:
    if not r['sitout_fires']:
        continue
    p = [q for q in MA.data if q['player'] == r['player'] and act(q)][0]
    dv = draftval(p); pos = MA.gfut(p); el = PR.tenure(p, 2026); g = g26(p)
    curve = SITOUT_RETAIN[_sitout_cls(pos)]
    N = min(max(el, 1), 6)
    # (a) games-smoothed: linear from the sit-out anchor to the 6-game production value
    va = None
    if g > 0:
        q = copy.deepcopy(p)
        for rr in q['scoring']:
            if rr['year'] == 2026:
                rr['games'] = 6
        if isinstance(q.get('games'), (int, float)):
            q['games'] = q['games'] + (6 - g)
        v6 = Q(ev, q, 2026)
        va = round(r['final'] + (g / 6.0) * (v6 - r['final']))
    # (b) R14/24-prorated tenure: retention read at fractional elapsed tenure N-1+fE
    nf = min(max(el - 1 + FE, 1.0), 6.0)
    i0 = int(nf) - 1
    fr = nf - int(nf)
    ret_b = curve[i0] if i0 >= 5 else curve[i0] * (1 - fr) + curve[i0 + 1] * fr
    wi.append({'player': r['player'], 'g26': g, 'current': r['final'],
               'whatif_a_games_smoothed': va,
               'whatif_b_R14_prorated': round(dv * ret_b), 'retain_b': round(ret_b, 3)})
OUT['whatif'] = wi

# ---- Berry / Lord comparables: similar career MIDs (base-valuation check) ----
def prof(p):
    return dict(pos=MA.gfut(p), pick=p.get('pick'), cohort=p.get('year'),
                ten=PR.tenure(p, 2026), best=bestlvl(p, 2026), g=sum(r['games'] for r in p['scoring']))
comps = {}
for nm in ['Sam Berry', 'Cooper Lord']:
    hits = [p for p in MA.data if p['player'] == nm and act(p)]
    if not hits:
        comps[nm] = 'NOT FOUND'
        continue
    t = prof(hits[0])
    cands = []
    for p in MA.data:
        if not act(p) or p['player'] == nm or delisted(p):
            continue
        c = prof(p)
        if c['pos'] != t['pos'] or c['cohort'] is None or t['cohort'] is None:
            continue
        if abs((c['cohort'] or 0) - (t['cohort'] or 0)) <= 1 and t['best'] > 0 and c['best'] > 0 \
           and abs(c['best'] - t['best']) / t['best'] <= 0.12 and abs(c['g'] - t['g']) <= 25:
            cands.append({'player': p['player'], 'pick': c['pick'], 'cohort': c['cohort'],
                          'games': c['g'], 'best_lvl': round(c['best'], 1),
                          'final': Q(ev, p, 2026)})
    comps[nm] = {'target': {k: (round(v, 1) if isinstance(v, float) else v) for k, v in t.items()},
                 'comparables': sorted(cands, key=lambda r: -r['final'])[:8]}
OUT['comparables'] = comps

json.dump(OUT, open(outp, 'w'), indent=1,
          default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print('WROTE', outp, ENG, CP)
