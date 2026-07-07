import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']
def seasons(p): return [(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (cp.debutyr(p)-1)<x['year']]

# --- games distribution (to set G_full) ---
allg=[x['games'] for p in MA.data for x in p['scoring'] if x['games']>0]
allg=np.array(allg)
print("games/season pctiles:", {q:int(np.percentile(allg,q)) for q in [25,50,60,70,75,80,90]}, " n=",len(allg))

G_FULL=14; G_EVAL=10; DELTA=3.0; WIN=4
def lvl_full(p,Y,ld):   # recency x games weighted level over FULL seasons only (reliability level)
    rows=[(y,gm,a) for (y,gm,a) in seasons(p) if gm>=G_FULL and y<=Y]
    tw=sum(gm*ld**max(0,Y-y) for y,gm,a in rows); return (sum(gm*ld**max(0,Y-y)*a for y,gm,a in rows)/tw if tw>0 else None), tw
def recent_fullgames(p,Y,back): return sum(gm for (y,gm,a) in seasons(p) if Y-back< y<=Y and gm>=G_FULL)
def realized_fwd(p,Y):
    fwd=[(y,gm,a) for (y,gm,a) in seasons(p) if Y< y<=Y+3 and gm>=G_EVAL]
    if not fwd: return None
    return sum(gm*a for y,gm,a in fwd)/sum(gm for y,gm,a in fwd)

# --- assemble established up-side decision points ---
pts=[]
for p in MA.data:
    if not (p.get('pick') or p.get('_ft')): continue
    ys=[y for y,_,_ in seasons(p)]
    if not ys: continue
    for Y in range(min(ys), 2025):                 # need forward seasons -> Y<=2024
        if _nqual(p,Y)<PROVEN_N: continue          # established only
        Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y)
        if Lc<Lo: continue                          # UP-side branch only
        ld=g['LDECAY_G'][_ldg(MA.gfut(p))]; ft=FLAT[_ldg(MA.gfut(p))]
        rfwd=realized_fwd(p,Y)
        if rfwd is None: continue
        Lrel,twrel=lvl_full(p,Y,ld)
        if Lrel is None: continue
        er2=recent_fullgames(p,Y,2)                 # full games in last 2 seasons
        pts.append(dict(nm=p['player'],Y=Y,pos=MA.gfut(p),Lo=Lo,Lc=Lc,gap=Lc-Lo,ft=ft,rfwd=rfwd,
                        Lrel=Lrel,rise=Lrel-Lo,er2=er2))
print(f"\nestablished up-side decision points: {len(pts)}")

held=[q for q in pts if q['gap']<=q['ft']]
print(f"of which CURRENTLY HELD (gap<=ft): {len(held)}")

# --- (1) does holding under-price? ---
import statistics as st
def frac(rs,f): return 100*sum(1 for q in rs if f(q))/len(rs) if rs else 0
print("\n=== (1) among HELD points, is L_old below realised forward? ===")
d_lo=[q['rfwd']-q['Lo'] for q in held]; d_lc=[q['rfwd']-q['Lc'] for q in held]
print(f"  mean(rfwd - L_old) = {np.mean(d_lo):+.2f}   mean(rfwd - Lc) = {np.mean(d_lc):+.2f}")
print(f"  frac rfwd > L_old+{DELTA:.0f} = {frac(held,lambda q:q['rfwd']>q['Lo']+DELTA):.0f}%   frac rfwd < L_old-{DELTA:.0f} = {frac(held,lambda q:q['rfwd']<q['Lo']-DELTA):.0f}%")
print("  -> L_old is closer/further to truth than Lc? |rfwd-Lo| vs |rfwd-Lc|:",
      f"{np.mean(np.abs(d_lo)):.2f} vs {np.mean(np.abs(d_lc)):.2f}")

# --- (2) which signal predicts rfwd>Lo+DELTA among HELD points ---
def auc(rs,sig,lab):
    xs=[(sig(q),lab(q)) for q in rs]; pos=[s for s,l in xs if l]; neg=[s for s,l in xs if not l]
    if not pos or not neg: return float('nan')
    c=sum((a>b)+0.5*(a==b) for a in pos for b in neg); return c/(len(pos)*len(neg))
lab=lambda q: q['rfwd']>q['Lo']+DELTA
print("\n=== (2) predicting under-priced holds (AUC, higher=better separation) ===")
for nm,sig in [('gap = Lc-Lo (current gate signal)',lambda q:q['gap']),
               ('rise = Lrel-Lo (full-season reliability rise)',lambda q:q['rise']),
               ('rise x min(1,er2/14) (recent-exposure shrunk)',lambda q:q['rise']*min(1,q['er2']/14.0)),
               ('er2 (recent full-game volume alone)',lambda q:q['er2'])]:
    print(f"  {nm:48s} AUC={auc(held,sig,lab):.3f}")

# --- (3) blend: fit rfwd ~ Lo + s*(Lc-Lo) on FIRED (reliable-rise) holds ---
fired=[q for q in held if q['rise']*min(1,q['er2']/14.0)>3]
if fired:
    Lo=np.array([q['Lo'] for q in fired]); Lc=np.array([q['Lc'] for q in fired]); rf=np.array([q['rfwd'] for q in fired])
    denom=np.sum((Lc-Lo)**2); s=float(np.sum((Lc-Lo)*(rf-Lo))/denom) if denom>0 else 0
    print(f"\n=== (3) release blend on {len(fired)} fired holds: rfwd ~ Lo + s*(Lc-Lo) -> s = {s:.2f} ===")
    print(f"  (s=1 -> switch fully to Lc; s=0 -> stay at Lo). resid RMSE vs stay-at-Lo:",
          f"{np.sqrt(np.mean((rf-(Lo+s*(Lc-Lo)))**2)):.2f} vs {np.sqrt(np.mean((rf-Lo)**2)):.2f}")
