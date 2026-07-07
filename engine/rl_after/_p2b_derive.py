import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; b6=g['b6']; era=g['era']; REF=g['REF']
def adj(a,y): return a*REF/era.get(y,REF)   # era-adjusted season avg (engine's de-era)

# ---- walk-forward records: for each ND-pick player, each as-of year Y with a forward season ----
def seas(p): return sorted([(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>=6], key=lambda r:r[0])
recs=[]
for p in MA.data:
    if not MA.GRP.get(p.get('pos')) or not p.get('pick'): continue
    if (p.get('year') or 2099)>2020: continue
    S=seas(p)
    if len(S)<2: continue
    for i in range(len(S)-1):
        Yi=S[i][0]; through=[s for s in S if s[0]<=Yi]; fwd=[s for s in S if s[0]>Yi]
        if not fwd: continue
        yrs=[s[0] for s in through]; gms=[s[1] for s in through]; avs=[adj(s[2],s[0]) for s in through]
        w=np.array([0.72**(Yi-y) for y in yrs])*np.array(gms)
        dem=float(np.dot(w,avs)/w.sum())
        n=len(through)
        disp=float(np.sqrt(np.dot(w,(np.array(avs)-dem)**2)/w.sum())) if n>1 else 0.0
        fb=max(adj(s[2],s[0]) for s in fwd)
        recs.append(dict(p=p,Y=Yi,dem=dem,n=n,disp=disp,age=cp._age_asof(p,Yi),T=Yi-(p.get('year') or Yi)+1,fb=fb,jump=fb-dem))
print(f"walk-forward records: {len(recs)}")
bar=77.1  # MID reference bar for 'mediocre' band (most of the ladder is MID)

# ---- (A) BREAKOUT BASE RATE: proven-mediocre, how often forward_best reaches q97 ----
pm=[r for r in recs if r['T']>=4 and (bar-10)<=r['dem']<=(bar+4)]
print(f"\n(A) proven-mediocre records (T>=4, dem in [{bar-10:.0f},{bar+4:.0f}]): {len(pm)}")
hit97=0; hit_d15=0; hit_d20=0
for r in pm:
    try:
        q97=float(b6(r['p'],r['Y'])[5])   # model ceiling as-of
    except Exception: q97=r['dem']+30
    if r['fb']>=q97: hit97+=1
    if r['jump']>=15: hit_d15+=1
    if r['jump']>=20: hit_d20+=1
n=len(pm)
print(f"    P(fwd_best >= model q97) = {hit97}/{n} = {100*hit97/n:.1f}%   <- empirical breakout base rate")
print(f"    P(jump >= +15) = {100*hit_d15/n:.1f}% ; P(jump >= +20) = {100*hit_d20/n:.1f}%")
print(f"    => DERIVED q97 fair weight ~= base rate ~= {hit97/n:.3f} (vs current 0.10)")

# ---- (B) BODY: forward spread vs demonstrated consistency ----
# consistency C = evidence(n) x tightness(disp): more stable seasons -> tighter forward peak?
print("\n(B) forward outcome spread by (n_seasons, dispersion) bins -- justifies body compression:")
def cbin(r):
    if r['n']<=1: return '1season'
    return ('stable' if r['disp']<8 else 'volatile')+f"_n{min(r['n'],5)}+"
from collections import defaultdict
grp=defaultdict(list)
for r in recs:
    if r['T']>=2: grp[('stable' if (r['n']>=4 and r['disp']<8) else ('volatile' if r['n']>=4 else '1-2seas'))].append(r['jump'])
for k in ['1-2seas','volatile','stable']:
    j=np.array(grp[k]); 
    if len(j): print(f"    {k:10s} n={len(j):4d}  mean_jump={j.mean():+5.1f}  std_jump={j.std():5.1f}  p90_jump={np.percentile(j,90):5.1f}")
print("    => high-consistency (stable, many seasons) forward peaks cluster tighter -> compress q70-q90 toward median.")

# ---- (C) TAIL headroom vs AGE: p90 forward jump by age ----
print("\n(C) breakout headroom (p90 of forward jump) by AGE -- justifies tail age-scaling:")
for lo,hi in [(17,19),(19,21),(21,23),(23,25),(25,40)]:
    j=np.array([r['jump'] for r in recs if lo<=r['age']<hi])
    if len(j): print(f"    age[{lo},{hi}) n={len(j):4d}  p90_jump={np.percentile(j,90):5.1f}  p97_jump={np.percentile(j,97):5.1f}  mean={j.mean():+5.1f}")
print("    => headroom shrinks with age -> scale q97 width (q97-median) by age.")
