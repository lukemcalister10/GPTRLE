import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; _lvlcurr=g['_lvlcurr']; b6=g['b6']; price6=g['price6']; raw_ev=g['raw_ev']; ev=g['ev']; PR=g['PR']
P=[p for p in MA.data if p['player']=='Darcy Parish'][0]
d=cp.debutyr(P); bar=MA.REPL['MID']-3

def seas_avg(p,Y):
    r=[x['avg'] for x in p['scoring'] if x['year']==Y and x['games']>0]
    return r[0] if r else None

sav=cp._lvl_eff
print("=== 1c BOOK-PARISH as-of seasons 1-5 (2016-2020, PRE-breakout; hindsight-free) ===")
print("  MID bar=77.1. par=pedigree par(pk5). Leff=engine level. EVdem=EV re-priced forcing level=that-yr season avg.")
print(f"  {'yr':>5s}{'seas':>5s}{'g':>4s}{'savg':>6s}{'lvlwt':>6s}{'par':>6s}{'Leff':>6s}{'bandM':>7s}{'pr':>6s}{'pole':>5s}{'EV':>6s}{'EVdem':>7s}{'levShare':>9s}")
tot_ev=tot_dem=0
for i,Y in enumerate(range(d,d+5)):
    savg=seas_avg(P,Y)
    lw=cp._lvl_wt(P,Y); par=PR.par_at('MID',min(MA.effpk(P),cp.KMAX),min(max(PR.tenure(P,Y),1),6))
    Le=cp._lvl_eff(P,Y); bb=b6(P,Y); bm=float(np.median(bb))
    pr=price6(P,b6(P,Y),Y); raw=raw_ev(P,Y); evf=ev(P,Y)
    # EV with level forced to that year's actual season avg (demonstrated) -> isolates level inflation
    if savg is not None:
        cp._lvl_eff=lambda q,Yy,s=savg: s
        evdem=ev(P,Y); cp._lvl_eff=sav
    else: evdem=evf
    levshare=evf-evdem
    tot_ev+=evf; tot_dem+=evdem
    print(f"  {Y:>5d}{i+1:>5d}{[x['games'] for x in P['scoring'] if x['year']==Y][0]:>4d}{(savg or 0):>6.1f}{lw:>6.1f}{par:>6.1f}{Le:>6.1f}{bm:>7.1f}{pr:>6.0f}{raw-pr:>5.0f}{evf:>6d}{evdem:>7d}{levshare:>+9d}")
print(f"\n  SUM EV(seasons1-5) = {tot_ev}   ; SUM if level=demonstrated = {tot_dem}")
print(f"  LEVEL's share of the inflation = {tot_ev-tot_dem} (EV lost when level pinned to actual season avg)")
print(f"  RESIDUAL (band ceiling + runway, still high at demonstrated level) = {tot_dem} -> dissect in Phase 2")
print(f"\n  Reconcile note: Parish raw career-high = 116.5 (2021 breakout), NOT ~86. His 2016-20 (pre-breakout) high = 86.7.")
print(f"  Present Lc 93.4 is a recency-weighted blend of recent 89-108 seasons (<=116.5 max) -> legal, no level inflation TODAY.")
