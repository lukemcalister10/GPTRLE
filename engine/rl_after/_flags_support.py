import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; PR=g['PR']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; PROVEN_N=g['PROVEN_N']; DOWN_TOL=g['DOWN_TOL']
_agemult=g['_agemult']; _par_prior=g['_par_prior']; _upS=g['_upS']; _eo=g['_eo']; delisted=g['delisted']
def adj(a,y): return a*REF/era.get(y,REF)
TOL_M1=5.0; G_ADQ=12; WIN=2; S_M1=0.46; GCAP=17.0
def _radq(p,Y,Lo): return any(x['games']>=G_ADQ and x['avg']>Lo for x in p['scoring'] if Y-WIN<x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
def _core(p,Y):
    Lo=cp._lvl_eff_orig(p,Y); n=_nqual(p,Y)
    if n==0: return Lo
    Lc=_lvlcurr(p,Y)
    if n>=PROVEN_N:
        if Lc>=Lo: return (Lo+S_M1*(Lc-Lo)) if ((Lc-Lo)>=TOL_M1 and _radq(p,Y,Lo)) else Lo
        drop=Lo-Lc
        if drop<=DOWN_TOL: return Lo
        sw=float(np.clip((drop-DOWN_TOL)/5,0,1)); return (1-sw)*Lo+sw*Lc*_agemult(cp._age_asof(p,Y))
    c=n/PROVEN_N; return c*Lc+(1-c)*_par_prior(p,Y)
def _infer(p,Y):
    L0=_core(p,Y); eo=_eo(p,Y)
    if eo<=0: return L0
    avs=[x['avg'] for x in p['scoring'] if x.get('games',0)>=6 and (cp.debutyr(p)-1)<x['year']<=Y]
    if not avs: return L0
    bar=MA.REPL.get(MA.gfut(p),0.0)-3.0; N=Y-cp.debutyr(p)+1
    return (1-eo)*L0+eo*min(L0,max(_upS(max(avs)-bar,N),_lvlcurr(p,Y)))
ORIG=cp._lvl_eff
def eff_s(p,Y): return sum(min(x['games']/GCAP,1.0) for x in p['scoring'] if x['games']>=6 and (cp.debutyr(p)-1)<x['year']<=Y)
def band_at(p,Y,fn):
    o=cp._lvl_eff; cp._lvl_eff=fn
    try: MA._pe_clear(); bb=list(b6(p,Y))
    finally: cp._lvl_eff=o; MA._pe_clear()
    return bb
def price(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): v=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,v))
    finally: MA.REPL.update(sav)
def v7c(bb,p,Y,cap=None):
    bb=list(bb); m=bb[2]; a=cp._age_asof(p,Y); cB=0.47*float(np.clip((eff_s(p,Y)-1)/3,0,1))
    if cap is not None: cB=min(cB,cap)
    asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    bb[3]=m+(1-cB)*(bb[3]-m); bb[4]=m+(1-cB)*(bb[4]-m); bb[5]=m+asc*(bb[5]-m); return bb
def qs(p,Y): return sorted([(x['year'],x['games'],adj(x['avg'],x['year'])) for x in p['scoring'] if x['games']>=6 and x['year']<=Y])
def tr(p,Y):
    l3=[s[2] for s in qs(p,Y)][-3:]; return (l3[-1]-l3[0]) if len(l3)>=2 else 0.0
Y=2026

# ---------- FLAG A: trend-up (>=+8) but level-flat (gap<5) established cohort ----------
print("=== FLAG A cohort: established (n>=4), trend>=+8, level gap<5  (M1 holds, v7 crushes) ===")
A=[]
for p in MA.data:
    if MA.gfut(p) not in ('MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC') or delisted(p): continue
    Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); n=_nqual(p,Y); t=tr(p,Y)
    if not (n>=PROVEN_N and t>=8 and (Lc-Lo)<5): continue
    cur=price(p,Y,band_at(p,Y,ORIG),WQ6)
    if cur<200: continue
    comb=price(p,Y,v7c(band_at(p,Y,_infer),p,Y),WQ6)
    A.append((100*(comb-cur)/cur,p['player'],MA.gfut(p),cp._age_asof(p,Y),n,Lc-Lo,t,cur))
for d,nm,pos,a,n,gp,t,cur in sorted(A):
    print(f"  {nm:22s}{pos:>8s} age{a:.0f} n{n} gap{gp:+4.1f} trend{t:+5.1f} cur{cur:5.0f}   COMB {d:+6.1f}%")
print(f"  ({len(A)} players) -- apply your reads: which of these are genuinely improving vs a plateau with a noisy up-tick?")

# ---------- FLAG B: KEY_FWD + KEY_DEF crush cohort + cB-cap lever ----------
print("\n=== FLAG B: KEY_FWD + KEY_DEF -- current vs cB capped at 0.35 / 0.30 ===")
K=[]
for p in MA.data:
    if MA.gfut(p) not in ('KEY_FWD','KEY_DEF') or delisted(p): continue
    cur=price(p,Y,band_at(p,Y,ORIG),WQ6)
    if cur<200: continue
    bm=band_at(p,Y,_infer)
    comb=price(p,Y,v7c(bm,p,Y),WQ6); c35=price(p,Y,v7c(bm,p,Y,cap=0.35),WQ6); c30=price(p,Y,v7c(bm,p,Y,cap=0.30),WQ6)
    K.append((100*(comb-cur)/cur,100*(c35-cur)/cur,100*(c30-cur)/cur,p['player'],MA.gfut(p),cur))
for pos in ('KEY_FWD','KEY_DEF'):
    sub=[k for k in K if k[4]==pos]
    print(f"  {pos}: n={len(sub)}  mean COMB {np.mean([k[0] for k in sub]):+.1f}  | cap0.35 {np.mean([k[1] for k in sub]):+.1f}  | cap0.30 {np.mean([k[2] for k in sub]):+.1f}")
print("  worst KEY crushes (COMB / cap0.35 / cap0.30):")
for d,d35,d30,nm,pos,cur in sorted(K)[:10]:
    print(f"    {nm:22s}{pos:>8s} cur{cur:5.0f}   {d:+6.1f}  ->  {d35:+6.1f}  /  {d30:+6.1f}")
