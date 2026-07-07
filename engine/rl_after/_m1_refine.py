import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']; LD=g['LDECAY_G']
def seasons(p): return [(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (cp.debutyr(p)-1)<x['year']]
G_FULL=14; G_EVAL=10; DELTA=3.0; WIN=4
def lvl_full(p,Y,ld):
    rows=[(y,gm,a) for (y,gm,a) in seasons(p) if gm>=G_FULL and y<=Y]
    tw=sum(gm*ld**max(0,Y-y) for y,gm,a in rows); return (sum(gm*ld**max(0,Y-y)*a for y,gm,a in rows)/tw if tw>0 else None)
def rfg(p,Y,back): return sum(gm for (y,gm,a) in seasons(p) if Y-back< y<=Y and gm>=G_FULL)
def consist(p,Y,Lo,ld):   # recency x games weighted FRACTION of recent full seasons above L_old
    rows=[(y,gm,a) for (y,gm,a) in seasons(p) if gm>=G_FULL and Y-WIN< y<=Y]
    tw=sum(gm*ld**max(0,Y-y) for y,gm,a in rows)
    return (sum(gm*ld**max(0,Y-y)*(a>Lo) for y,gm,a in rows)/tw if tw>0 else 0.0), tw
def realized(p,Y):
    fwd=[(y,gm,a) for (y,gm,a) in seasons(p) if Y< y<=Y+3 and gm>=G_EVAL]
    if not fwd: return None,None
    avg=sum(gm*a for y,gm,a in fwd)/sum(gm for y,gm,a in fwd)
    best2=np.mean(sorted([a for y,gm,a in fwd],reverse=True)[:2])
    return avg,best2
pts=[]
for p in MA.data:
    if not (p.get('pick') or p.get('_ft')): continue
    ys=[y for y,_,_ in seasons(p)]
    if not ys: continue
    for Y in range(min(ys),2025):
        if _nqual(p,Y)<PROVEN_N: continue
        Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y)
        if Lc<Lo: continue
        ld=LD[_ldg(MA.gfut(p))]; ft=FLAT[_ldg(MA.gfut(p))]
        if Lc-Lo>ft: continue                       # HELD only
        ra,rb=realized(p,Y)
        if ra is None: continue
        Lrel=lvl_full(p,Y,ld)
        if Lrel is None: continue
        cons,tw=consist(p,Y,Lo,ld)
        pts.append(dict(nm=p['player'],Y=Y,rise=Lrel-Lo,Lo=Lo,Lc=Lc,er2=rfg(p,Y,2),er3=rfg(p,Y,3),cons=cons,ra=ra,rb=rb))
print(f"held established up-side points with forward: {len(pts)}\n")

def summ(rs,lab):
    if not rs: print(f"  {lab:34s} n=0"); return
    da=np.array([q['ra']-q['Lo'] for q in rs]); db=np.array([q['rb']-q['Lo'] for q in rs])
    fr=100*np.mean(da>DELTA)
    print(f"  {lab:34s} n={len(rs):4d}  mean(rfwd_avg-Lo)={da.mean():+5.2f}  mean(best2-Lo)={db.mean():+5.2f}  frac avg>Lo+3={fr:3.0f}%")

print("=== by rise bucket (does a real rise sustain forward?) ===")
for lo,hi in [(-99,2),(2,5),(5,8),(8,12),(12,99)]:
    summ([q for q in pts if lo<=q['rise']<hi], f"rise in [{lo},{hi})")

RS=[q for q in pts if q['rise']>=5]
print(f"\n=== within REAL-RISE (rise>=5, n={len(RS)}): does consistency separate sustain from regress? ===")
def auc(rs,sig,lab):
    xs=[(sig(q),lab(q)) for q in rs]; pos=[s for s,l in xs if l]; neg=[s for s,l in xs if not l]
    if not pos or not neg: return float('nan')
    return sum((a>b)+0.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg))
lab=lambda q:q['ra']>q['Lo']+DELTA
for nm,sig in [('rise',lambda q:q['rise']),('consistency (frac fulls above Lo)',lambda q:q['cons']),
               ('er2 recent full games',lambda q:q['er2']),('rise*cons',lambda q:q['rise']*q['cons']),
               ('rise*cons*min(1,er2/20)',lambda q:q['rise']*q['cons']*min(1,q['er2']/20.0))]:
    print(f"  {nm:34s} AUC={auc(RS,sig,lab):.3f}")
# blend on real-rise + consistent + exposed
fired=[q for q in RS if q['cons']>=0.6 and q['er2']>=14]
if fired:
    Lo=np.array([q['Lo'] for q in fired]);Lc=np.array([q['Lc'] for q in fired]);rf=np.array([q['ra'] for q in fired])
    s=float(np.sum((Lc-Lo)*(rf-Lo))/np.sum((Lc-Lo)**2))
    print(f"\n  FIRED (rise>=5 & cons>=0.6 & er2>=14): n={len(fired)}  mean(rfwd-Lo)={np.mean(rf-Lo):+.2f}  blend s={s:.2f}"
          f"  RMSE stay={np.sqrt(np.mean((rf-Lo)**2)):.2f} vs blend={np.sqrt(np.mean((rf-(Lo+s*(Lc-Lo)))**2)):.2f}")

# --- place the 5 validation players ---
print("\n=== validation players: rise / consistency / recent-exposure ===")
def R(nm):
    h=[x for x in MA.data if x['player']==nm]; return h[0] if h else None
Y=2026
print(f"  {'player':22s}{'rise':>6s}{'cons':>6s}{'er2':>5s}{'er3':>5s}  fire(rise>=5&cons>=.6&er2>=14)?")
for nm in ['Jack Ginnivan','Tanner Bruhn','Luke Davies-Uniacke','Will Day','Tom Powell']:
    p=R(nm); ld=LD[_ldg(MA.gfut(p))]; Lo=cp._lvl_eff_orig(p,Y)
    Lrel=lvl_full(p,Y,ld); rise=(Lrel-Lo) if Lrel is not None else float('nan')
    cons,_=consist(p,Y,Lo,ld); e2=rfg(p,Y,2); e3=rfg(p,Y,3)
    fire = (rise>=5 and cons>=0.6 and e2>=14)
    print(f"  {nm:22s}{rise:>+6.1f}{cons:>6.2f}{e2:>5d}{e3:>5d}  {'FIRE' if fire else 'hold'}")
