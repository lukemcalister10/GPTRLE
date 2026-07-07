import os
import io,contextlib,json,collections,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA'];ev=g['ev'];REF=g.get('REF',100);era=g['era'];delisted=g['delisted']
INCURVE={'ND','RD'}; POOLED={'MSD','SSP','UNR','IRE','PDA','PDN','PDS'}
def eligible(p): return MA.GRP.get(p.get('pos')) and not p.get('_pvc_exclude')
players=[p for p in MA.data if eligible(p)]
best={}
for p in players:
    k=(p.get('key') or MA.slug(p['player']), p.get('type'), p.get('year'))  # +year: keep same-name-different-cohort pairs distinct
    if k not in best or len(p['scoring'])>len(best[k]['scoring']): best[k]=p
players=list(best.values())
# ISOLATED DATA FIX (Isaac Kako, ND pk13 2024): his real 2025 debut (23g, 55.1 — 2024 Rising Star) is missing
# from the source DB, leaving him mis-read as sat-out 2025. Fold it in so his calendar Yr1 anchors on a PLAYED
# debut, not the no-games pole. Luke confirmed this is isolated to Kako (known missing-data case), not systemic.
for _p in players:
    if 'kako' in _p['player'].lower() and _p.get('year')==2024:
        if not any(r['year']==2025 for r in _p['scoring']):
            _p['scoring']=sorted(_p['scoring']+[{'year':2025,'avg':55.1,'games':23}], key=lambda r:r['year'])
        print(f"[Kako patch] scoring now {[(r['year'],r['games'],r['avg']) for r in _p['scoring']]}",flush=True)
print(f"eligible players: {len(players)}",flush=True)
# WALK-FORWARD as-of value matrix (UNCHANGED — values are correct; only the indexing was wrong)
ASOF={}
for Y in range(2003,2027):
    saved={}
    for p in players:
        if (p.get('year') or 9999)>Y: continue
        LL=p.get('_last_listed'); RET=p.get('_retired'); lastscore=max((r['year'] for r in p['scoring']), default=0)
        saved[id(p)]=(p['scoring'],RET,LL); p['scoring']=[r for r in p['scoring'] if r['year']<=Y]
        eff_last = LL if LL is not None else (lastscore if RET else None)
        p['_retired']=False; p['_last_listed']= eff_last if (eff_last is not None and eff_last < Y) else None
    MA.BASE_REF=Y; MA.AGE_REF=Y; MA._pe_clear()
    for p in players:
        if (p.get('year') or 9999)>Y: continue
        try:
            with contextlib.redirect_stdout(io.StringIO()): ASOF[(id(p),Y)]=ev(p,Y)
        except Exception: ASOF[(id(p),Y)]=None
    for p in players:
        if id(p) in saved: p['scoring'],p['_retired'],p['_last_listed']=saved[id(p)]
    MA._pe_clear()
MA.BASE_REF=MA.AGE_REF=2026; MA._pe_clear()
def adjavg(y,a): return round(a*REF/era.get(y,REF),1)
def retired_now(p):
    if delisted(p): return True
    lg=max((r['year'] for r in p['scoring'] if r.get('games',0)>=1), default=None); dy=p.get('year')
    return bool(lg is not None and dy is not None and dy<=2021 and lg<=2024)
rec={}; nsat=0
for p in players:
    C=p.get('year')
    if C is None: continue
    played={x['year']:(x['games'],x['avg']) for x in p['scoring'] if x['games']>=1}
    last_active=max(played) if played else None
    rn=retired_now(p)
    # CALENDAR-YEAR-SINCE-DRAFT indexing: Yr_k = C+k whether or not played; missed year = real (pole/staleness) value.
    # ACTIVE players run through 2026 (current value); RETIRED players stop at last played year (blank after, no post-career floor).
    yend = (last_active if last_active else C+1) if rn else 2026
    yend = min(yend,2026)
    yrs=list(range(C+1, yend+1)) if yend>=C+1 else [C+1]
    Vpath=[ASOF.get((id(p),y)) for y in yrs]
    Ppath=[(adjavg(y,played[y][1]) if y in played else 0.0) for y in yrs]
    anchor=ASOF.get((id(p),C+1))                          # END OF CALENDAR YEAR 1 (regardless of games) = the curve anchor
    fp=min(played) if played else None
    old_anchor=ASOF.get((id(p),fp)) if fp else None       # buggy first-PLAYED anchor (for bias comparison)
    sat=(C+1 not in played) and bool(played)
    if sat and p.get('type') in INCURVE and 2004<=C<=2024: nsat+=1
    rec[id(p)]=dict(player=p['player'],pos=(MA.GRP.get(p.get('pos')) or MA.gfut(p)),cpos=MA.gfut(p),sw=bool(MA.GRP.get(p.get('pos')) and MA.GRP.get(p.get('pos'))!=MA.gfut(p)),type=p.get('type'),pick=MA.effpk(p),pickless=bool(p.get('_pickless')),
                    year=C,cat=p.get('_cat'),draftval=round(MA.PVC[min(MA.effpk(p),70)]) if not p.get('_pickless') else None,
                    yrs=yrs,Vpath=Vpath,Ppath=Ppath,cur=ASOF.get((id(p),2026)),anchor=anchor,old_anchor=old_anchor,
                    sat_out_yr1=sat,retired_now=rn,incurve=(p.get('type') in INCURVE))
json.dump({str(k):v for k,v in rec.items()}, open(os.environ.get('S4_MATRIX','s4_matrix.json'),'w'))
print(f"matrix saved (CALENDAR-indexed): {len(rec)} players",flush=True)
# ---- mapping-only proof: a played value is identical old vs new (just a different slot) ----
camp=[v for v in rec.values() if 'seth campbell' in v['player'].lower()][0]
print(f"\nMAPPING-ONLY PROOF — Seth Campbell: yrs={camp['yrs']} Vpath={[round(x) if x else None for x in camp['Vpath']]}")
print(f"  new anchor (calendar Yr1 {camp['year']+1}, no games)={round(camp['anchor'])}; the 465 first-played value now sits at its correct slot {camp['yrs'].index(2024)+1 if 2024 in camp['yrs'] else '?'} (Yr2)")
# ---- CURVE-ANCHOR BIAS (2004-2024 ND+RD) ----
elig=[v for v in rec.values() if v['incurve'] and 2004<=v['year']<=2024]
sat=[v for v in elig if v['sat_out_yr1'] and v['anchor'] and v['old_anchor']]
deltas=[v['old_anchor']-v['anchor'] for v in sat]
print(f"\nCURVE-ANCHOR BIAS (2004-2024 ND+RD, n={len(elig)}):")
print(f"  sat out draft Yr1: {nsat} players ({round(100*nsat/len(elig))}% of curve pool)")
print(f"  over-valuation when anchored at first-played vs real Yr1: total={round(sum(deltas))} SCAR, mean=+{round(np.mean(deltas))}, median=+{round(np.median(deltas))}")
old_sum=sum(v['old_anchor'] for v in elig if v['old_anchor']); new_sum=sum(v['anchor'] for v in elig if v['anchor'])
print(f"  whole-pool anchor sum: buggy={round(old_sum)} -> fixed={round(new_sum)}  ({round(100*(old_sum-new_sum)/old_sum,1)}% lower overall)")
for lo,hi in [(1,20),(21,40),(41,80)]:
    s=[v for v in sat if lo<=v['pick']<=hi]
    if s: print(f"  picks {lo}-{hi}: {len(s)} sat-out, mean over-val +{round(np.mean([v['old_anchor']-v['anchor'] for v in s]))} ({round(100*np.mean([(v['old_anchor']-v['anchor'])/v['anchor'] for v in s]))}% of real Yr1)")
