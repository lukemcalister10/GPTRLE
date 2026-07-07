import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']; ev=g['ev']
def adj(a,y): return a*REF/era.get(y,REF)
def R(sub,exp=None,Y=2026):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if ev(p,Y)==exp]
    return hs[0] if len(hs)==1 else [q['player'] for q in hs]

# --- evidence (n, disp) as-of ---
def evidence(p,Y):
    S=[(x['year'],x['games'],adj(x['avg'],x['year'])) for x in p['scoring'] if x['games']>=6 and x['year']<=Y]
    n=len(S)
    if n==0: return 0,0.0
    w=np.array([0.72**(Y-y) for y,_,_ in S])*np.array([g_ for _,g_,_ in S])
    m=np.dot(w,[a for _,_,a in S])/w.sum()
    disp=float(np.sqrt(np.dot(w,(np.array([a for _,_,a in S])-m)**2)/w.sum())) if n>1 else 0.0
    return n,disp

# --- pricing (level fixed) ---
def price_band(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()):
            vals=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)
def cur(p,Y): return price_band(p,Y,b6(p,Y),WQ6)
def v3(p,Y):  # drop q90: [q10,q30,q50,q70,q97], weights current minus q90
    bb=b6(p,Y); return price_band(p,Y,[bb[0],bb[1],bb[2],bb[3],bb[5]],[.18,.18,.18,.18,.10])
def v6(p,Y,k=0.5): # tenure-gated tail weight-decay (as specified)
    bb=b6(p,Y); T=cp._feat(p,Y)[8]; kk=k*float(np.clip((T-1)/4,0,1))
    w=list(WQ6); mv=kk*(w[4]+w[5]); w=[w[0],w[1]+mv/2,w[2]+mv/2,w[3],w[4]*(1-kk),w[5]*(1-kk)]
    return price_band(p,Y,bb,w)
# v7 DERIVED schedules: body compression from evidence(n); tail width from age headroom
def cB_of(n): return 0.47*float(np.clip((n-1)/3,0,1))               # (B): high-evidence spread ~0.53x low -> compress .47
def aSc_of(age): return float(np.interp(age,[20,22,24,27],[1.00,0.76,0.58,0.40]))  # (C): p90 headroom 49.9->20
def v7(p,Y):
    bb=list(b6(p,Y)); m=bb[2]; n,disp=evidence(p,Y); a=cp._age_asof(p,Y)
    cB=cB_of(n); asc=aSc_of(a)
    bb[3]=m+(1-cB)*(bb[3]-m); bb[4]=m+(1-cB)*(bb[4]-m)   # compress body q70,q90 toward median (evidence)
    bb[5]=m+asc*(bb[5]-m)                                # age-scale tail q97 width
    return price_band(p,Y,bb,WQ6), cB, asc               # weights kept (base rate 17% >= 0.10 -> tail preserved)

# --- find a TRUE year-1 flier (young high pick, first qual season) ---
cand=[]
for p in MA.data:
    if not MA.GRP.get(p.get('pos')) or not (p.get('pick') and p['pick']<=15): continue
    qs=[x for x in p['scoring'] if x['games']>=6]
    if not qs: continue
    fy=min(x['year'] for x in qs); a=cp._age_asof(p,fy)
    if a<=19.5 and fy>=2024: cand.append((p['player'],p['pick'],fy,round(a,1)))
print("true yr-1 flier candidates (young, pk<=15, first qual >=2024):", cand[:6])

# --- LADDER + VALIDATION set ---
Preg=R('Darcy Parish')
LAD=[('bookParish-yr3',Preg,2018,'PUREBAND'),('bookParish-yr5',Preg,2020,'PUREBAND'),
     ('Jeffrey',R('Joel Jeffrey',1773),2026,'MIDOV'),('Bruhn',R('Tanner Bruhn',913),2026,'MIDOV(plateau)'),
     ("O'Driscoll",R("Nathan O'Driscoll",896),2026,'MIDOV(plateau)'),('Serong',R('Caleb Serong'),2026,'FAIR/anchor'),
     ('Butters',R('Zak Butters'),2026,'ELITE'),('Bontempelli',R('Marcus Bontempelli'),2026,'ELITE'),
     ('ClaytonOliver',R('Clayton Oliver'),2026,'ELITE-decl'),
     # VALIDATION:
     ('DaviesUniacke@21',R('Luke Davies-Uniacke'),2021,'BREAKOUT(pre)'),
     ('EdRichards@21',R('Ed Richards'),2021,'BREAKOUT(pre,flat)'),
     ('Parish@20',Preg,2020,'BREAKOUT(pre)'),
     ('MatureAge:Watkins',R('Jack Watkins'),2026,'MATURE-AGE(old,1seas)'),
     ('MatureAge:McCarthy',R('Tom McCarthy'),2025,'MATURE-AGE(old,1seas)')]

print(f"\n{'case':22s}{'tier':20s}{'age':>4s}{'n':>3s}{'disp':>5s}{'cur':>7s}{'v3':>7s}{'v6':>7s}{'v7':>7s}{'cB':>5s}{'aSc':>5s}")
rows={}
for nm,p,Y,tier in LAD:
    if isinstance(p,str): print(f"{nm:22s} UNRESOLVED {p}"); continue
    n,disp=evidence(p,Y); a=cp._age_asof(p,Y)
    c=cur(p,Y); a3=v3(p,Y); a6=v6(p,Y); a7,cB,asc=v7(p,Y)
    rows[nm]=(tier,c,a3,a6,a7)
    print(f"{nm:22s}{tier:20s}{a or 0:>4.0f}{n:>3d}{disp:>5.1f}{c:>7.0f}{a3:>7.0f}{a6:>7.0f}{a7:>7.0f}{cB:>5.2f}{asc:>5.2f}")

# Δ% vs current, anchored to Serong
print("\nΔ% vs current, RE-ANCHORED to Serong:")
s=rows.get('Serong')
def anch(v):
    return 100*(s[v]-s[1])/s[1] if s else 0
print(f"{'case':22s}{'tier':20s}{'v3':>8s}{'v6':>8s}{'v7':>8s}")
for nm,(tier,c,a3,a6,a7) in rows.items():
    print(f"{nm:22s}{tier:20s}{100*(a3-c)/c-anch(2):>+8.1f}{100*(a6-c)/c-anch(3):>+8.1f}{100*(a7-c)/c-anch(4):>+8.1f}")
