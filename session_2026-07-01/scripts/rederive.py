import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA'];cp=g['cp'];raw_ev=g['raw_ev'];iso_corr=g['iso_corr'];draftval=g['draftval'];delisted=g['delisted']
def cls(p):
    pos=MA.gfut(p); return 'RUC' if pos=='RUC' else ('KPP' if pos in ('KEY_FWD','KEY_DEF') else 'nonKPP')
def gyr(p,yr): return next((r['games'] for r in p['scoring'] if r['year']==yr),0)
def played6ever(p): return any(r['games']>=6 for r in p['scoring'])
def maxyr(p): return max((r['year'] for r in p['scoring']), default=None)
# population: drafted players with a pick (draftval defined), draftyr known
pool=[p for p in MA.data if p.get('year') and p.get('pick') and not p.get('_pickless') and MA.GRP.get(p.get('pos'))]
print(f"pool drafted players: {len(pool)}")
print("REALIZED sit-out retention: players with <6 games in ALL of career-yrs 1..N, still listed at yr N;")
print("  realized = production-value(raw_ev, NO anchor)/draftval if they EVER played >=6g, else 0 (washed out).")
print(f"{'cls':7s} {'N':>2s} {'n(sit-thru-N)':>13s} {'washout%':>8s} {'median_ret':>10s} {'mean_ret':>9s}   wired")
WIRED={'RUC':[0.85,0.85,0.74,0.62,0.51,0.40],'KPP':[0.70,0.70,0.60,0.50,0.40,0.30],'nonKPP':[0.50,0.50,0.42,0.35,0.28,0.20]}
for c in ['RUC','KPP','nonKPP']:
    for N in range(1,7):
        pop=[]
        for p in pool:
            dy=p['year']
            if dy+N>2026: continue                      # not observable to year N
            if cls(p)!=c: continue
            if any(gyr(p,dy+k)>=6 for k in range(1,N+1)): continue   # played >=6 in some yr 1..N -> not sit-out-through-N
            my=maxyr(p)
            listed_at_N = (my is not None and my>=dy+N) or (not delisted(p) and p.get('_has26'))  # evidence still around at/after yr N
            if not listed_at_N: continue
            pop.append(p)
        n=len(pop)
        if n==0:
            print(f"{c:7s} {N:>2d} {n:>13d} {'-':>8s} {'-':>10s} {'-':>9s}   {WIRED[c][N-1]}"); continue
        rets=[]
        wash=0
        for p in pop:
            if played6ever(p):
                try: v=raw_ev(p,2026)*iso_corr(MA.gfut(p),MA.effpk(p)); rets.append(max(0.0,v)/max(1,draftval(p)))
                except Exception: rets.append(0.0)
            else:
                rets.append(0.0); wash+=1
        rets=np.array(rets)
        print(f"{c:7s} {N:>2d} {n:>13d} {100*wash/n:>7.0f}% {np.median(rets):>10.2f} {np.mean(rets):>9.2f}   {WIRED[c][N-1]}")
