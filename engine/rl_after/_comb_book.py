import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
g['_BOARD_PATH']=False   # D14: walk-forward book render — board-only laws (V0 curve, KPP floor) OFF (Luke's exemption).
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; PR=g['PR']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']
DOWN_TOL=g['DOWN_TOL']; _agemult=g['_agemult']; _par_prior=g['_par_prior']; _upS=g['_upS']; _eo=g['_eo']
nseas=g['nseas']; delisted=g['delisted']; ORIG_LVL=cp._lvl_eff
def adj(a,y): return a*REF/era.get(y,REF)
TOL_M1=5.0; G_ADQ=12; WIN=2; S_M1=0.46
def _recent_adq_above(p,Y,Lo):
    return any(x['games']>=G_ADQ and x['avg']>Lo for x in p['scoring'] if Y-WIN< x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
def _core_M1(p,Y):
    L_old=cp._lvl_eff_orig(p,Y); n=_nqual(p,Y)
    if n==0: return L_old
    Lc=_lvlcurr(p,Y)
    if n>=PROVEN_N:
        if Lc>=L_old:
            return (L_old+S_M1*(Lc-L_old)) if ((Lc-L_old)>=TOL_M1 and _recent_adq_above(p,Y,L_old)) else L_old
        drop=L_old-Lc
        if drop<=DOWN_TOL: return L_old
        sw=float(np.clip((drop-DOWN_TOL)/5.0,0.0,1.0)); return (1.0-sw)*L_old+sw*Lc*_agemult(cp._age_asof(p,Y))
    c=n/PROVEN_N; return c*Lc+(1-c)*_par_prior(p,Y)
def _infer_M1(p,Y):
    L0=_core_M1(p,Y); eo=_eo(p,Y)
    if eo<=0.0: return L0
    avs=[x['avg'] for x in p['scoring'] if x.get('games',0)>=6 and (cp.debutyr(p)-1)<x['year']<=Y]
    if not avs: return L0
    bar=MA.REPL.get(MA.gfut(p),0.0)-3.0; N=Y-cp.debutyr(p)+1
    return (1.0-eo)*L0+eo*min(L0, max(_upS(max(avs)-bar,N), _lvlcurr(p,Y)))
qg=[x['games'] for p in MA.data for x in p['scoring'] if x['games']>=6]; GCAP=float(np.median(qg))
def eff_seasons(p,Y): return sum(min(x['games']/GCAP,1.0) for x in p['scoring'] if x['games']>=6 and (cp.debutyr(p)-1)<x['year']<=Y)
def band_at(p,Y,lvlfn):
    old=cp._lvl_eff; cp._lvl_eff=lvlfn
    try: MA._pe_clear(); bb=list(b6(p,Y))
    finally: cp._lvl_eff=old; MA._pe_clear()
    return bb
def price_band(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): vals=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)
def v7ref(bb,p,Y):
    bb=list(bb); m=bb[2]; a=cp._age_asof(p,Y); e=eff_seasons(p,Y)
    cB=0.47*float(np.clip((e-1)/3,0,1)); asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    bb[3]=m+(1-cB)*(bb[3]-m); bb[4]=m+(1-cB)*(bb[4]-m); bb[5]=m+asc*(bb[5]-m); return bb
def qseas(p,Y): return sorted([(x['year'],x['games'],adj(x['avg'],x['year'])) for x in p['scoring'] if x['games']>=6 and x['year']<=Y])
def trend(p,Y):
    S=qseas(p,Y); l3=[s[2] for s in S][-3:]; return (l3[-1]-l3[0]) if len(l3)>=2 else 0.0
def meang(p,Y):
    S=qseas(p,Y); return float(np.mean([s[1] for s in S])) if S else 0.0

Y=2026; rows=[]
POS6=('MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC')
for p in MA.data:
    if MA.gfut(p) not in POS6 or delisted(p): continue
    try:
        bb_cur=band_at(p,Y,ORIG_LVL); cur=price_band(p,Y,bb_cur,WQ6)
    except Exception: continue
    if cur<200: continue
    bb_m1=band_at(p,Y,_infer_M1); comb=price_band(p,Y,v7ref(bb_m1,p,Y),WQ6)
    Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); N=Y-cp.debutyr(p)+1
    rows.append(dict(nm=p['player'],pos=MA.gfut(p),cur=cur,comb=comb,d=100*(comb-cur)/cur,
        gap=Lc-Lo,n=_nqual(p,Y),N=N,mg=meang(p,Y),tr=trend(p,Y),age=cp._age_asof(p,Y),fired=(_infer_M1(p,Y)>Lo+0.05 and _nqual(p,Y)>=PROVEN_N and Lc>=Lo)))
print(f"priced {len(rows)} players (outfield+RUC, cur>=200)\n")
D=np.array([r['d'] for r in rows])
print(f"=== OVERALL COMB% distribution ===  mean {D.mean():+.1f}  median {np.median(D):+.1f}")
for q in [5,10,25,50,75,90,95]: print(f"  p{q:2d}: {np.percentile(D,q):+6.1f}", end="")
print(f"\n  moved down >2%: {sum(D<-2)}   ~flat [-2,2]: {sum((D>=-2)&(D<=2))}   up >2%: {sum(D>2)}")

def cls(r):
    if r['N']<=1: return 'first-year'
    if r['mg']<12 and r['n']>=3: return 'injury-prone'
    if r['gap']<=-5 or r['tr']<=-8: return 'decliner'
    if r['gap']>=5: return 'rising'
    return 'plateau'
print("\n=== by ARCHETYPE ===")
for c in ['first-year','rising','plateau','injury-prone','decliner']:
    rs=[r for r in rows if cls(r)==c]; d=np.array([r['d'] for r in rs]) if rs else np.array([0])
    print(f"  {c:13s} n={len(rs):3d}  mean {d.mean():+6.1f}  median {np.median(d):+6.1f}  min {d.min():+6.1f}  max {d.max():+6.1f}")
print("\n=== by VALUE TIER (cur) ===")
for lab,lo,hi in [('elite >=2500',2500,9e9),('upper 1500-2500',1500,2500),('mid 700-1500',700,1500),('low 200-700',200,700)]:
    rs=[r for r in rows if lo<=r['cur']<hi]; d=np.array([r['d'] for r in rs]) if rs else np.array([0])
    print(f"  {lab:16s} n={len(rs):3d}  mean {d.mean():+6.1f}  median {np.median(d):+6.1f}")
print("\n=== by POSITION ===")
for pos in POS6:
    rs=[r for r in rows if r['pos']==pos]; d=np.array([r['d'] for r in rs]) if rs else np.array([0])
    print(f"  {pos:8s} n={len(rs):3d}  mean {d.mean():+6.1f}  median {np.median(d):+6.1f}  min {d.min():+6.1f}")
print("\n=== biggest MOVERS DOWN ===")
for r in sorted(rows,key=lambda r:r['d'])[:15]:
    print(f"  {r['nm']:22s}{r['pos']:>8s} age{r['age']:.0f} n{r['n']} gap{r['gap']:+4.1f} tr{r['tr']:+5.1f} cur{r['cur']:5.0f}  {r['d']:+6.1f}%  {cls(r)}")
print("=== biggest MOVERS UP ===")
for r in sorted(rows,key=lambda r:-r['d'])[:15]:
    print(f"  {r['nm']:22s}{r['pos']:>8s} age{r['age']:.0f} n{r['n']} gap{r['gap']:+4.1f} tr{r['tr']:+5.1f} cur{r['cur']:5.0f}  {r['d']:+6.1f}%  {cls(r)} {'M1-fired' if r['fired'] else ''}")
print(f"\n=== M1 fired count: {sum(r['fired'] for r in rows)}  | trend-up(>=+8) but level-flat(gap<5) established (Graham-type, unrelieved): "
      f"{sum(1 for r in rows if r['tr']>=8 and r['gap']<5 and r['n']>=PROVEN_N)}")
