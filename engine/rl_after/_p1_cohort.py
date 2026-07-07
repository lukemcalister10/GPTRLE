import io, contextlib, copy, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; ev=g['ev']

# identify draft-year field
s=[p for p in MA.data if p['player']=='Darcy Parish'][0]
print("sample fields:", {k:s.get(k) for k in ['year','_draft','type','pick']})

def draft_year(p): return p.get('year')
cohort=[p for p in MA.data if p.get('type')=='ND' and (p.get('pick')) and 2014<=(draft_year(p) or 0)<=2019]
print(f"cohort ND-with-pick 2014-2019: n={len(cohort)}")

def cum_games(p,Y): return sum(x.get('games',0) for x in p['scoring'] if x['year']<=Y)
def value_asof(p,t):
    D=draft_year(p); Yt=D+t
    q=copy.deepcopy(p)
    q['scoring']=[x for x in q['scoring'] if x['year']<=Yt]
    q['_pos_now']=None; q['_fut']=[]                      # leak-free: value on drafted position
    MA.BASE_REF=MA.AGE_REF=Yt; MA._pe_clear()
    if cum_games(p,Yt)==0 and t>=3: return 0.0            # realized-bust floor (never-debuted 3+ yrs)
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(q,Yt))

print("\n=== DE-SURVIVORED full-cohort mean value (SCAR) by career-year t (current head 8aed420a) ===")
print(f"  {'t':>3s}{'n':>5s}{'mean':>7s}{'median':>8s}")
means={}
for t in range(0,9):
    vals=[value_asof(p,t) for p in cohort if (draft_year(p)+t)<=2026]
    if not vals: continue
    means[t]=np.mean(vals)
    print(f"  {t:>3d}{len(vals):>5d}{np.mean(vals):>7.0f}{np.median(vals):>8.0f}")
pk=max(means,key=means.get)
print(f"\n  PEAK at t={pk} (mean {means[pk]:.0f}).  yr0={means.get(0,0):.0f}  ratio peak/yr0 = {means[pk]/max(means.get(0,1),1):.2f}x")
print(f"  Shape: {'monotone ramp (peak at window end)' if pk>=max(means) and pk==max(means.keys()) else 'peaks then declines'}")
print("  Interpretation: peak yr6-8 => runway+variance concern LIVE (Phase-2 ceiling decay shared fix);")
print("                  peak yr4-5 => survivorship fix already handled it, thread closes.")
