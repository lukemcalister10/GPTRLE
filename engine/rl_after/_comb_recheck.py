import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; PR=g['PR']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']
DOWN_TOL=g['DOWN_TOL']; _agemult=g['_agemult']; _par_prior=g['_par_prior']; _upS=g['_upS']; _eo=g['_eo']
ORIG_LVL=cp._lvl_eff                               # baked _lvl_eff_infer (hold-band)
def adj(a,y): return a*REF/era.get(y,REF)

# ---- M1 params (derived in _m1_gate.py) ----
TOL_M1=5.0; G_ADQ=12; WIN=2; S_M1=0.46
def _recent_adq_above(p,Y,Lo):
    return any(x['games']>=G_ADQ and x['avg']>Lo for x in p['scoring'] if Y-WIN< x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
def _core_M1(p,Y):                                 # == _lvl_eff_core but sustain-aware UP-side
    L_old=cp._lvl_eff_orig(p,Y); n=_nqual(p,Y)
    if n==0: return L_old
    Lc=_lvlcurr(p,Y)
    if n>=PROVEN_N:
        if Lc>=L_old:
            fire=(Lc-L_old)>=TOL_M1 and _recent_adq_above(p,Y,L_old)
            return (L_old+S_M1*(Lc-L_old)) if fire else L_old
        drop=L_old-Lc
        if drop<=DOWN_TOL: return L_old
        sw=float(np.clip((drop-DOWN_TOL)/5.0,0.0,1.0)); Lsh=Lc*_agemult(cp._age_asof(p,Y))
        return (1.0-sw)*L_old+sw*Lsh
    c=n/PROVEN_N; return c*Lc+(1-c)*_par_prior(p,Y)
def _infer_M1(p,Y):                                # == _lvl_eff_infer but on _core_M1
    L0=_core_M1(p,Y); eo=_eo(p,Y)
    if eo<=0.0: return L0
    avs=[x['avg'] for x in p['scoring'] if x.get('games',0)>=6 and (cp.debutyr(p)-1)<x['year']<=Y]
    if not avs: return L0
    bar=MA.REPL.get(MA.gfut(p),0.0)-3.0; N=Y-cp.debutyr(p)+1
    T=min(L0, max(_upS(max(avs)-bar,N), _lvlcurr(p,Y)))
    return (1.0-eo)*L0+eo*T

# ---- derive Gcap for exposure-weighted cB ----
qg=[x['games'] for p in MA.data for x in p['scoring'] if x['games']>=6]
GCAP=float(np.median(qg))
print(f"Gcap (median games among qual>=6 seasons) = {GCAP:.0f}   [exposure-weighted cB uses this]\n")
def eff_seasons(p,Y):
    return sum(min(x['games']/GCAP,1.0) for x in p['scoring'] if x['games']>=6 and (cp.debutyr(p)-1)<x['year']<=Y)

# ---- band pricing ----
def band_at(p,Y,lvlfn):
    old=cp._lvl_eff; cp._lvl_eff=lvlfn
    try:
        MA._pe_clear(); bb=list(b6(p,Y))
    finally:
        cp._lvl_eff=old; MA._pe_clear()
    return bb
def price_band(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): vals=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)
def v7_compress(bb,p,Y,exposure):                  # exposure=True -> refined cB; False -> original raw-n cB
    bb=list(bb); m=bb[2]; a=cp._age_asof(p,Y)
    if exposure: ev_n=eff_seasons(p,Y)
    else:
        ev_n=len([1 for x in p['scoring'] if x['games']>=6 and x['year']<=Y and (cp.debutyr(p)-1)<x['year']])
    cB=0.47*float(np.clip((ev_n-1)/3,0,1)); asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    bb[3]=m+(1-cB)*(bb[3]-m); bb[4]=m+(1-cB)*(bb[4]-m); bb[5]=m+asc*(bb[5]-m)
    return bb,cB
def R(nm):
    h=[x for x in MA.data if x['player']==nm]; return h[0] if h else None

Y=2026
groups=[('IMPROVERS',['Jack Graham','Neil Erasmus','Elijah Tsatas','Luke Davies-Uniacke']),
        ('INJURY-PRONE',['Alex Davies']),
        ('DECLINERS',['Deven Robertson','James Worpel']),
        ('VALIDATION (5)',['Jack Ginnivan','Tanner Bruhn','Will Day','Tom Powell'])]
print(f"{'player':22s}{'pos':>8s}{'age':>4s}{'Lo':>6s}{'Lc':>6s}{'Leff0':>7s}{'LeffM1':>7s}{'cur':>6s}"
      f"{'v7old%':>8s}{'M1only%':>8s}{'COMB%':>7s}{'cB0':>5s}{'cBx':>5s}")
for gname,names in groups:
    print(f"-- {gname} --")
    for nm in names:
        p=R(nm)
        if not p: print(f"{nm:22s} NOT FOUND"); continue
        pos=MA.gfut(p); a=cp._age_asof(p,Y); Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y)
        L0=ORIG_LVL(p,Y); Lm=_infer_M1(p,Y)
        bb_cur=band_at(p,Y,ORIG_LVL); bb_m1=band_at(p,Y,_infer_M1)
        cur=price_band(p,Y,bb_cur,WQ6)
        v7old_bb,cB0=v7_compress(bb_cur,p,Y,exposure=False); v7old=price_band(p,Y,v7old_bb,WQ6)
        m1only=price_band(p,Y,bb_m1,WQ6)
        comb_bb,cBx=v7_compress(bb_m1,p,Y,exposure=True); comb=price_band(p,Y,comb_bb,WQ6)
        f=lambda x:100*(x-cur)/cur
        print(f"{nm:22s}{pos:>8s}{a:>4.0f}{Lo:>6.1f}{Lc:>6.1f}{L0:>7.1f}{Lm:>7.1f}{cur:>6.0f}"
              f"{f(v7old):>+8.1f}{f(m1only):>+8.1f}{f(comb):>+7.1f}{cB0:>5.2f}{cBx:>5.2f}")
