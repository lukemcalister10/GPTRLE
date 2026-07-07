#!/usr/bin/env python3
# D7 ASK 4a — enumerate the staleness-cap population at CANONICAL HEAD (one engine load; scratch, wires nothing).
# The stalled branch (ev(): el>=onset AND ns<=1 -> e=min(e, dv*frac)) fires only for ns==1 players (ns==0
# routes to the sit-out branch first). For every firing player: CAPPED = ev(p,2026); UNCAPPED = e_pre =
# raw_ev*iso_corr (the value the cap overwrites). Derivation features: the qualifying season's year/games/avg,
# gap = 2026 - qual_year, current-season (2026) games/avg, REPL[gfut], era-adjusted level fraction.
import os, sys, io, json, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
outp = sys.argv[1]
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, cp, PR = G['ev'], G['MA'], G['cp'], G['PR']
raw_ev, iso_corr = G['raw_ev'], G['iso_corr']
draftval, delisted, nseas = G['draftval'], G['delisted'], G['nseas']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]

rows = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired') or delisted(p):
            continue
        try:
            ns = nseas(p, 2026)
            if ns != 1:
                continue
            pos = MA.gfut(p)
            el = PR.tenure(p, 2026)
            keyruc = pos in ('KEY_FWD', 'KEY_DEF', 'RUC')
            onset = 4 if keyruc else 3
            if el < onset:
                continue
            # the branch FIRES for this player
            e_pre = float(raw_ev(p, 2026)) * float(iso_corr(pos, MA.effpk(p)))
            dv = draftval(p)
            frac = 0.25 * max(0.4, 1 - 0.10 * (el - onset)) * (1.6 if keyruc else 1.0)
            cap = dv * frac
            v = float(ev(p, 2026))
            quals = [x for x in p['scoring'] if x['games'] >= 6 and x['year'] <= 2026]
            q = quals[-1] if quals else None
            g26 = sum(x['games'] for x in p['scoring'] if x['year'] == 2026)
            a26rows = [x for x in p['scoring'] if x['year'] == 2026 and x['games'] > 0]
            a26 = a26rows[0]['avg'] if a26rows else None
            repl = float(MA.REPL.get(pos, 0.0))
            rows.append(dict(player=p['player'], club=p.get('_club'), type=p.get('type'),
                             pos=pos, keyruc=keyruc, yis=2026 - int(p.get('year') or 0),
                             year=p.get('year'), pick=p.get('pick'), effpk=MA.effpk(p),
                             el=int(el), onset=onset, draftval=round(dv, 1),
                             seasons=[(x['year'], x['games'], x['avg']) for x in p['scoring']],
                             qual_year=(q['year'] if q else None), qual_g=(q['games'] if q else None),
                             qual_avg=(q['avg'] if q else None),
                             gap=(2026 - q['year']) if q else None,
                             g26=g26, avg26=a26, repl=round(repl, 1),
                             qual_repl_frac=round((q['avg'] / repl), 3) if q and repl > 0 else None,
                             capped_ev=round(v, 1), uncapped=round(e_pre, 1),
                             cap_value=round(cap, 1), binds=bool(e_pre > cap + 1e-9)))
        except Exception as ex:
            rows.append(dict(player=p.get('player'), error=str(ex)))
rows.sort(key=lambda r: -(r.get('uncapped') or 0))
json.dump(dict(engine=ENG, n_fire=len(rows), rows=rows), open(outp, 'w'), indent=1)
print(f'engine={ENG} | stalled-branch FIRES for n={len(rows)} (binds for '
      f'{sum(1 for r in rows if r.get("binds"))})')
for r in rows:
    if 'error' in r:
        print('ERR', r); continue
    print(f"  {r['player']:24s} {r['club'] or '—':18s} yis={r['yis']:2d} el={r['el']} type={r['type']:>3s} "
          f"pos={r['pos']:7s} qual={r['qual_year']}({r['qual_g']}g@{r['qual_avg']}) gap={r['gap']} "
          f"g26={r['g26']:2d} avg26={r['avg26'] or '—'} q/repl={r['qual_repl_frac']} "
          f"capped={r['capped_ev']:.0f} uncapped={r['uncapped']:.0f} binds={r['binds']}")
print('wrote', outp, 'md5', hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8])
