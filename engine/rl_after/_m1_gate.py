import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']; LD=g['LDECAY_G']
def seasons(p): return [(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (cp.debutyr(p)-1)<x['year']]
G_EVAL=10; DELTA=3.0
def realized(p,Y):
    fwd=[(y,gm,a) for (y,gm,a) in seasons(p) if Y< y<=Y+3 and gm>=G_EVAL]
    if not fwd: return None,None
    return sum(gm*a for y,gm,a in fwd)/sum(gm for y,gm,a in fwd), np.mean(sorted([a for y,gm,a in fwd],reverse=True)[:2])
def recent_adq_above(p,Y,Lo,G,back):   # exists recent (last `back` yrs) season w/ games>=G and avg>Lo
    return any(gm>=G and a>Lo for (y,gm,a) in seasons(p) if Y-back< y<=Y)
# assemble held up-side points
pts=[]
for p in MA.data:
    if not (p.get('pick') or p.get('_ft')): continue
    ys=[y for y,_,_ in seasons(p)]
    if not ys: continue
    for Y in range(min(ys),2025):
        if _nqual(p,Y)<PROVEN_N: continue
        Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y)
        if Lc<Lo or Lc-Lo>FLAT[_ldg(MA.gfut(p))]: continue   # currently HELD up-side
        ra,rb=realized(p,Y)
        if ra is None: continue
        pts.append(dict(p=p,Y=Y,Lo=Lo,Lc=Lc,gap=Lc-Lo,ra=ra,rb=rb))
print(f"held up-side points w/ forward: {len(pts)}\n")
def stats(rs):
    if not rs: return "n=0"
    da=np.array([q['ra']-q['Lo'] for q in rs])
    return f"n={len(rs):4d}  mean(rfwd-Lo)={da.mean():+5.2f}  frac>Lo+3={100*np.mean(da>DELTA):3.0f}%"
# sweep TOL x G_ADQ (window=2yrs); fired = gap>=TOL AND recent adequate above
print("=== fired vs not-fired forward under composite gate (window=2y) ===")
for G in [10,12,14]:
    for TOL in [4,5,6,7]:
        fired=[q for q in pts if q['gap']>=TOL and recent_adq_above(q['p'],q['Y'],q['Lo'],G,2)]
        rest =[q for q in pts if not (q['gap']>=TOL and recent_adq_above(q['p'],q['Y'],q['Lo'],G,2))]
        print(f"  G_ADQ={G} TOL={TOL}:  FIRED {stats(fired):48s} | held {stats(rest)}")
# pick G=12,TOL=5: blend + AUC
G,TOL=12,5
fired=[q for q in pts if q['gap']>=TOL and recent_adq_above(q['p'],q['Y'],q['Lo'],G,2)]
Lo=np.array([q['Lo'] for q in fired]);Lc=np.array([q['Lc'] for q in fired]);rf=np.array([q['ra'] for q in fired])
s=float(np.sum((Lc-Lo)*(rf-Lo))/np.sum((Lc-Lo)**2))
print(f"\n=== chosen G_ADQ=12,TOL=5: fired n={len(fired)} ===")
print(f"  blend rfwd~Lo+s(Lc-Lo): s={s:.2f}  RMSE stay-Lo={np.sqrt(np.mean((rf-Lo)**2)):.2f} vs blend={np.sqrt(np.mean((rf-(Lo+s*(Lc-Lo)))**2)):.2f} vs switch-Lc={np.sqrt(np.mean((rf-Lc)**2)):.2f}")
def auc(rs,sig,lab):
    xs=[(sig(q),lab(q)) for q in rs];pos=[x for x,l in xs if l];neg=[x for x,l in xs if not l]
    return sum((a>b)+0.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg)) if pos and neg else float('nan')
gate=lambda q: 1.0 if (q['gap']>=TOL and recent_adq_above(q['p'],q['Y'],q['Lo'],G,2)) else 0.0
print(f"  composite gate AUC (predict rfwd>Lo+3) = {auc(pts,gate,lambda q:q['ra']>q['Lo']+DELTA):.3f}   (vs raw gap {auc(pts,lambda q:q['gap'],lambda q:q['ra']>q['Lo']+DELTA):.3f})")

# --- validation 5 under chosen gate ---
print("\n=== validation 5 under G_ADQ=12,TOL=5,window=2,s (Leff before->after) ===")
def R(nm):
    h=[x for x in MA.data if x['player']==nm]; return h[0] if h else None
Y=2026
for nm in ['Jack Ginnivan','Tanner Bruhn','Luke Davies-Uniacke','Will Day','Tom Powell']:
    p=R(nm); Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); gap=Lc-Lo
    fire = gap>=TOL and recent_adq_above(p,Y,Lo,G,2)
    Leff_now=cp._lvl_eff(p,Y)
    Leff_new = (Lo+s*(Lc-Lo)) if fire else Leff_now
    print(f"  {nm:22s} Lo={Lo:5.1f} Lc={Lc:5.1f} gap={gap:+4.1f}  {'FIRE' if fire else 'hold':4s}  Leff {Leff_now:5.1f} -> {Leff_new:5.1f}  (Δ{Leff_new-Leff_now:+.1f})")
