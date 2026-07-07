import io, contextlib, copy, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; WQ6=g['WQ6']; ev=g['ev']
orig_price6=g['price6']

def draft_year(p): return p.get('year')
cohort=[p for p in MA.data if p.get('type')=='ND' and p.get('pick') and 2014<=(draft_year(p) or 0)<=2019]
def cum_games(p,Y): return sum(x.get('games',0) for x in p['scoring'] if x['year']<=Y)
def value_asof(p,t):
    D=draft_year(p); Yt=D+t; q=copy.deepcopy(p)
    q['scoring']=[x for x in q['scoring'] if x['year']<=Yt]; q['_pos_now']=None; q['_fut']=[]
    MA.BASE_REF=MA.AGE_REF=Yt; MA._pe_clear()
    if cum_games(p,Yt)==0 and t>=3: return 0.0
    with contextlib.redirect_stdout(io.StringIO()): return float(ev(q,Yt))
def curve():
    out={}
    for t in range(0,9):
        vals=[value_asof(p,t) for p in cohort if (draft_year(p)+t)<=2026]
        out[t]=np.mean(vals)
    return out

# v6 tenure-gated tail weight-decay price6 (re-weights the SAME band; LEVEL untouched)
def make_v6(kmax):
    def v6(p,bb,Y=2026):
        T=cp._feat(p,Y)[8]; k=kmax*float(np.clip((T-1)/4,0,1))
        w=list(WQ6); moved=k*(w[4]+w[5]); w=[w[0],w[1]+moved/2,w[2]+moved/2,w[3],w[4]*(1-k),w[5]*(1-k)]
        w=np.array(w)/sum(w); sav=dict(MA.REPL)
        try:
            for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
            MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
            with contextlib.redirect_stdout(io.StringIO()):
                vals=[dp.v_at_peak(p,float(L),'bal') for L in bb]
            return float(dp.SCALE_DIST*np.dot(w,vals))
        finally: MA.REPL.update(sav)
    return v6

print("=== BASELINE de-survivored cohort curve (current, verify) ===")
base=curve(); print("  "+"  ".join(f"t{t}:{base[t]:.0f}" for t in base)); pk=max(base,key=base.get); print(f"  peak t={pk}")

print("\n=== UNDER V6 (tenure-gated tail weight-decay, kmax=0.5) ===")
g['price6']=make_v6(0.5); g['_POLE'].clear()   # repoint price6 for raw_ev + par_pole; clear pole cache to rebuild
v6c=curve()
g['price6']=orig_price6; g['_POLE'].clear()
print("  "+"  ".join(f"t{t}:{v6c[t]:.0f}" for t in v6c)); pk6=max(v6c,key=v6c.get); print(f"  peak t={pk6}")

print("\n=== COMPARISON (mean SCAR by career-year) ===")
print(f"  {'t':>3s}{'base':>8s}{'v6':>8s}{'Δ%':>7s}")
for t in base: print(f"  {t:>3d}{base[t]:>8.0f}{v6c[t]:>8.0f}{100*(v6c[t]-base[t])/base[t]:>+7.1f}")
print(f"\n  baseline peak t={pk} ; v6 peak t={pk6}")
print(f"  late-year (t6) shaved {100*(v6c[6]-base[6])/base[6]:+.1f}% ; early (t1) {100*(v6c[1]-base[1])/base[1]:+.1f}% ; t0 {100*(v6c[0]-base[0])/base[0]:+.1f}%")
print("  => if peak moves toward t4-5 and late shaved > early, the band lever ties BOTH symptoms to ONE fix.")
