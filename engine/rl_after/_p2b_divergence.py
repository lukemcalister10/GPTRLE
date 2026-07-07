import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']; ev=g['ev']
def adj(a,y): return a*REF/era.get(y,REF)
def qseas(p,Y): return sorted([(x['year'],x['games'],adj(x['avg'],x['year'])) for x in p['scoring'] if x['games']>=6 and x['year']<=Y])
def evidence(p,Y):
    S=qseas(p,Y); n=len(S)
    if n==0: return 0,0.0,0.0,0.0,0.0
    yrs=[s[0] for s in S]; gms=[s[1] for s in S]; avs=[s[2] for s in S]
    w=np.array([0.72**(Y-y) for y in yrs])*np.array(gms); m=np.dot(w,avs)/w.sum()
    disp=float(np.sqrt(np.dot(w,(np.array(avs)-m)**2)/w.sum())) if n>1 else 0.0
    mg=float(np.mean(gms)); l3=avs[-3:]; trend=(l3[-1]-l3[0]) if len(l3)>=2 else 0.0
    return n,disp,mg,trend,m
def price_band(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): vals=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)
def cur(p,Y): return price_band(p,Y,b6(p,Y),WQ6)
def v6(p,Y,k=0.5):
    bb=b6(p,Y); T=cp._feat(p,Y)[8]; kk=k*float(np.clip((T-1)/4,0,1))
    w=list(WQ6); mv=kk*(w[4]+w[5]); w=[w[0],w[1]+mv/2,w[2]+mv/2,w[3],w[4]*(1-kk),w[5]*(1-kk)]
    return price_band(p,Y,bb,w),T
def v7(p,Y):
    bb=list(b6(p,Y)); m=bb[2]; n,_,_,_,_=evidence(p,Y); a=cp._age_asof(p,Y)
    cB=0.47*float(np.clip((n-1)/3,0,1)); asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    bb[3]=m+(1-cB)*(bb[3]-m); bb[4]=m+(1-cB)*(bb[4]-m); bb[5]=m+asc*(bb[5]-m)
    return price_band(p,Y,bb,WQ6),cB,asc

# broad sample: outfield players with >=2 qual seasons and a non-trivial current value
Y=2026; rows=[]
for p in MA.data:
    if MA.gfut(p) not in ('MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD'): continue
    if g['nseas'](p,Y)<2 or g['delisted'](p): continue
    c=cur(p,Y)
    if c<300: continue
    n,disp,mg,trend,m=evidence(p,Y); a=cp._age_asof(p,Y)
    a6,T=v6(p,Y); a7,cB,asc=v7(p,Y)
    d6=100*(a6-c)/c; d7=100*(a7-c)/c
    rows.append(dict(nm=p['player'],pos=MA.gfut(p),age=a,n=n,mg=mg,disp=disp,trend=trend,cur=c,d6=d6,d7=d7,div=d7-d6,cB=cB,asc=asc,T=T))
print(f"scanned {len(rows)} players\n")

def show(rs,title):
    print(title)
    print(f"  {'player':20s}{'pos':>8s}{'age':>4s}{'n':>3s}{'mg':>4s}{'trend':>6s}{'cur':>6s}{'v6Δ%':>6s}{'v7Δ%':>6s}{'v7-v6':>6s}")
    for r in rs:
        print(f"  {r['nm'][:20]:20s}{r['pos']:>8s}{r['age'] or 0:>4.0f}{r['n']:>3d}{r['mg']:>4.0f}{r['trend']:>+6.1f}{r['cur']:>6.0f}{r['d6']:>+6.1f}{r['d7']:>+6.1f}{r['div']:>+6.1f}")

show(sorted(rows,key=lambda r:r['div'])[:10], "=== v7 HARSHER than v6 (most negative v7-v6) ===")
print()
show(sorted(rows,key=lambda r:-r['div'])[:10], "=== v6 HARSHER than v7 (most positive v7-v6) ===")

# aggregate: does one systematically hit a profile harder?
imp=[r for r in rows if r['trend']>=8]; dec=[r for r in rows if r['trend']<=-8]; inj=[r for r in rows if r['mg']<12 and r['n']>=4]
print("\n=== profile aggregates (mean Δ%) ===")
for lbl,rs in [('IMPROVERS (trend>=+8)',imp),('DECLINERS (trend<=-8)',dec),('INJURY-PRONE (mg<12,n>=4)',inj),('ALL',rows)]:
    if rs: print(f"  {lbl:26s} n={len(rs):4d}  v6 {np.mean([r['d6'] for r in rs]):+5.1f}  v7 {np.mean([r['d7'] for r in rs]):+5.1f}  (v7-v6 {np.mean([r['div'] for r in rs]):+5.1f})")
