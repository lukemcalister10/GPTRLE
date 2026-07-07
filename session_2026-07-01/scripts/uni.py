import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; nseas=g['nseas']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)

print("=== TEST 2: leaguewide SuperCoach per-game mean by year (avg-weighted by games) ===")
for lbl,flt in [('all g>=1',1),('g>=6',6),('established nseas>=6, g>=6',None)]:
    for Y in [2022,2023,2024,2025,2026]:
        recs=[]
        for p in MA.data:
            r=g_y(p,Y)
            if not r or r.get('avg') is None: continue
            if flt is not None and r['games']<flt: continue
            if flt is None:
                if r['games']<6 or nseas(p,2026)<6: continue
            recs.append(r)
        gm=sum(r['games'] for r in recs); tot=sum(r['avg']*r['games'] for r in recs)
        pg=tot/gm if gm else 0
        print(f"  [{lbl:28s}] {Y}: per-game={pg:6.2f}  players={len(recs):4d} games={gm}")
    print()

print("=== TEST 1: mean ev %-delta per transition (players with g>=6 in BOTH years) ===")
trans=[(2022,2023),(2023,2024),(2024,2025),(2025,2026)]
print(f"{'transition':12s} {'n':>4s} {'mean_dV%':>8s} {'median%':>8s} {'%down':>6s}")
for (a,b) in trans:
    ds=[]
    for p in MA.data:
        ra,rb=g_y(p,a),g_y(p,b)
        if not ra or not rb or ra['games']<6 or rb['games']<6: continue
        try: va,vb=ev(p,a),ev(p,b)
        except: continue
        if va>0: ds.append((vb-va)/va)
    ds=np.array(ds)
    print(f"{a}->{b}   {len(ds):>4d} {100*ds.mean():>7.1f}% {100*np.median(ds):>7.1f}% {100*(ds<0).mean():>5.0f}%")

print("\n=== TEST 1b: same, split by recent cohort (rose before? turn down in 25->26?) ===")
print(f"{'cohort':>6s} {'n25-26':>6s} " + " ".join(f"{a%100}->{b%100:>2d}" for a,b in trans))
for C in range(2016,2024):
    row=[]
    n2526=0
    for (a,b) in trans:
        ds=[]
        for p in MA.data:
            if p.get('year')!=C: continue
            ra,rb=g_y(p,a),g_y(p,b)
            if not ra or not rb or ra['games']<6 or rb['games']<6: continue
            try: va,vb=ev(p,a),ev(p,b)
            except: continue
            if va>0: ds.append((vb-va)/va)
        row.append(f"{100*np.mean(ds):>5.0f}%" if ds else "   - ")
        if (a,b)==(2025,2026): n2526=len(ds)
    print(f"{C:>6d} {n2526:>6d} " + " ".join(row))
