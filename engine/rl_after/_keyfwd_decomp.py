import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; b6=g['b6']; WQ6=g['WQ6']; era=g['era']; REF=g['REF']
_nqual=g['_nqual']; delisted=g['delisted']
GCAP=17.0
def eff_s(p,Y): return sum(min(x['games']/GCAP,1.0) for x in p['scoring'] if x['games']>=6 and (cp.debutyr(p)-1)<x['year']<=Y)
def price(p,Y,bb,w):
    w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): v=[dp.v_at_peak(p,float(L),'bal') for L in bb]
        return float(dp.SCALE_DIST*np.dot(w,v)), v
    finally: MA.REPL.update(sav)
def R(nm):
    h=[x for x in MA.data if x['player']==nm]; return h[0] if h else None
Y=2026
for nm in ['Nikolas Cox','Joel Amartey','Max King','Liam McMahon']:
    p=R(nm)
    if not p: print(nm,"NF"); continue
    MA._pe_clear(); bb=list(b6(p,Y))
    a=cp._age_asof(p,Y); n=_nqual(p,Y); e=eff_s(p,Y)
    cB=0.47*float(np.clip((e-1)/3,0,1)); asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    m=bb[2]
    def comp(cb,ac):
        z=list(bb); z[3]=m+(1-cb)*(z[3]-m); z[4]=m+(1-cb)*(z[4]-m); z[5]=m+ac*(z[5]-m); return price(p,Y,z,WQ6)[0]
    cur,vals=price(p,Y,bb,WQ6)
    body=comp(cB,1.0); tail=comp(0.0,asc); full=comp(cB,asc)
    f=lambda x:100*(x-cur)/cur
    print(f"{nm:16s} age{a:.0f} n{n} eff_s{e:.1f} cB{cB:.2f} asc{asc:.2f}  band[q10..q97]={[round(x) for x in bb]}")
    print(f"    cur{cur:5.0f}  body-only {f(body):+6.1f}%  tail-only(asc) {f(tail):+6.1f}%  FULL {f(full):+6.1f}%   v_at_peak={[round(x) for x in vals]}")
