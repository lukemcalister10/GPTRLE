"""GATE 1 confirm: does the POLE price future-good HIGH-PICKS near par EARLY (pedigree before proven), while future-good
LATE-PICKS read low early and rise as they produce? Leakage-guarded (cohort held out), pooled across positions."""
import io,contextlib,copy,os,numpy as np,time
os.environ['RL_PRIOR_TREES']='150'
ns={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], ns)
MA=ns['MA']; cp=ns['cp']; PR=ns['PR']; REF=ns['REF']; era=ns['era']
def build_q97(pool):
    from sklearn.ensemble import GradientBoostingRegressor
    X,yy=[],[]
    for p in pool:
        if cp.debutyr(p)>2021 or not (p.get('pick') or p.get('_ft')): continue
        d0=cp.debutyr(p)-1; last=max([x['year'] for x in p['scoring']]+[d0])
        for Y in range(d0,min(last,2026)+1): X.append(cp._feat(p,Y)); yy.append(cp.fwd_best3_from(p,Y,2026))
    return GradientBoostingRegressor(loss='quantile',alpha=0.97,n_estimators=150,max_depth=4,learning_rate=0.05,min_samples_leaf=25,random_state=0).fit(np.array(X),np.array(yy))
def trunc(p,T):
    d0=cp.debutyr(p)-1; q=copy.deepcopy(p); q['scoring']=[x for x in p['scoring'] if x['year']<=d0+T]; q['_pos_now']=None; q['_fut']=[]; return q,d0+T
def real_mat(p):
    s=sorted([a*REF/era.get(y,REF) for y,a in [(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6]],reverse=True)[:3]; return float(np.mean(s)) if s else 0.0
full=[p for p in MA.data if MA.GRP.get(p['pos'])]
TEN=[0,1,2,3,4,5]; agg={}
for D in range(2014,2019):
    coh=[p for p in full if p.get('type')=='ND' and p.get('pick') and p['year']==D and p.get('scoring')]
    cohset=set(id(p) for p in coh); pool=[p for p in full if id(p) not in cohset]
    with contextlib.redirect_stdout(io.StringIO()): wf_cm,_=cp.build_cond_prior(cap=2026,resolved_cut=2021,pool=pool); wf_q97=build_q97([p for p in pool if cp.debutyr(p)<=2021 and (p.get('pick') or p.get('_ft'))])
    ns['cm']=wf_cm; ns['q97m']=wf_q97
    for p in coh:
        pos=MA.gfut(p); pk=min(MA.effpk(p),cp.KMAX); par=PR.par_at(pos,pk,5)
        with contextlib.redirect_stdout(io.StringIO()): parval=ns['par_pole'](pos,pk,5)[0]
        if parval<=0 or real_mat(p)<0.85*par: continue        # future-GOOD only
        band='HIGH pk<=12' if pk<=12 else ('LATE pk>=25' if pk>=25 else None)
        if not band: continue
        for T in TEN:
            tp,Y=trunc(p,T)
            try:
                with contextlib.redirect_stdout(io.StringIO()): e=ns['ev'](tp,Y)
            except Exception: continue
            agg.setdefault(band,{}).setdefault(T,[]).append(100.0*e/parval)
print("=== future-GOOD players, value % of par-value, by PICK band (leakage-guarded WF) ===")
print("  pole works -> HIGH-pick good reads high EARLY (pedigree priced before proven); LATE-pick good reads low early & climbs")
for band in ['HIGH pk<=12','LATE pk>=25']:
    n=len(agg.get(band,{}).get(1,[])); 
    if not n: continue
    line=" ".join(f"T{T}:{np.median(agg[band][T]):4.0f}" for T in TEN if T in agg[band])
    print(f"  {band:12s} n={n:2d}  [{line}]")
