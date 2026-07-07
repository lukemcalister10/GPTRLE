import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; b6=g['b6']; WQ6=g['WQ6']
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if g['ev'](p,2026)==exp]
    return hs[0] if len(hs)==1 else [q['player'] for q in hs]
P6=[0.10,0.30,0.50,0.70,0.90,0.97]
def qfunc(bb,tau):
    if tau<P6[0]:
        sl=(bb[1]-bb[0])/(P6[1]-P6[0]); return bb[0]-sl*(P6[0]-tau)
    return float(np.interp(tau,P6,bb))
def price_scheme(p,Y,taus,w):
    bb=b6(p,Y); w=np.array(w)/sum(w); sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()):
            vals=[dp.v_at_peak(p,float(qfunc(bb,t)),'bal') for t in taus]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)
def bmid(p,Y): return float(np.median(b6(p,Y)))
def tenure_of(p,Y): return cp._feat(p,Y)[8]

Preg=R('Darcy Parish')
LAD=[('bookParish-yr3',Preg,2018,'PUREBAND'),('bookParish-yr5',Preg,2020,'PUREBAND'),
     ('Jeffrey',R('Joel Jeffrey',1773),2026,'MIDOV'),('Bruhn',R('Tanner Bruhn',913),2026,'MIDOV'),
     ("O'Driscoll",R("Nathan O'Driscoll",896),2026,'MIDOV'),('Serong',R('Caleb Serong'),2026,'FAIR'),
     ('Butters',R('Zak Butters'),2026,'ELITE'),('Bontempelli',R('Marcus Bontempelli'),2026,'ELITE'),
     ('Reid-yr1',R('Harley Reid'),2026,'YOUNG')]
print("tenure (dev) per ladder player:")
for nm,p,Y,t in LAD: print(f"   {nm:16s} ten={tenure_of(p,Y):.1f} Leff={cp._feat(p,Y)[9]:.1f} band_mid={bmid(p,Y):.1f} off={bmid(p,Y)-cp._feat(p,Y)[9]:+.1f}")

# V5 tenure-slide: slide 5 base percentiles DOWN by d(T)=dmax*clip((T-1)/4,0,1); first-yr(T<=1)->0. uniform weights.
def v5_price(p,Y,dmax):
    T=tenure_of(p,Y); d=dmax*float(np.clip((T-1)/4,0,1))
    taus=[max(0.02,b-d) for b in [.10,.30,.50,.70,.90]]
    return price_scheme(p,Y,taus,[.2]*5), d
# V6 tail weight-decay: keep P6 set; move q90/q97 weight to q30/q50 by factor k(T)=kmax*clip((T-1)/4,0,1)
def v6_price(p,Y,kmax):
    T=tenure_of(p,Y); k=kmax*float(np.clip((T-1)/4,0,1))
    w=list(WQ6); moved=k*(w[4]+w[5]); w[4]*= (1-k); w[5]*=(1-k); w[1]+=moved*0.5; w[2]+=moved*0.5
    return price_scheme(p,Y,P6,w), k

print("\n=== DERIVE V5 dmax: collapse proven-mediocre offset toward 0, spare first-yr/elite ===")
print(f"{'dmax':>6s} | "+" ".join(f"{nm[:9]:>9s}" for nm,_,_,_ in LAD))
for dmax in [0.08,0.12,0.16,0.20,0.24]:
    cells=[]
    for nm,p,Y,t in LAD:
        cur=price_scheme(p,Y,P6,WQ6); v,d=v5_price(p,Y,dmax); cells.append(100*(v-cur)/cur)
    print(f"{dmax:>6.2f} | "+" ".join(f"{c:>+9.1f}" for c in cells))
print("(Δ% vs current. Want PUREBAND/MIDOV strongly negative, Reid≈0, elite small.)")

print("\n=== DERIVE V6 kmax (tail weight-decay) ===")
print(f"{'kmax':>6s} | "+" ".join(f"{nm[:9]:>9s}" for nm,_,_,_ in LAD))
for kmax in [0.3,0.5,0.7,0.9]:
    cells=[]
    for nm,p,Y,t in LAD:
        cur=price_scheme(p,Y,P6,WQ6); v,k=v6_price(p,Y,kmax); cells.append(100*(v-cur)/cur)
    print(f"{kmax:>6.2f} | "+" ".join(f"{c:>+9.1f}" for c in cells))

# pick a representative dmax and show offset collapse
print("\n=== V5 @ dmax=0.16: offset (band-priced level proxy) before/after, + schedule ===")
dmax=0.16
for nm,p,Y,t in LAD:
    T=tenure_of(p,Y); d=dmax*float(np.clip((T-1)/4,0,1))
    cur=price_scheme(p,Y,P6,WQ6); v,_=v5_price(p,Y,dmax)
    print(f"   {nm:16s} T={T:.1f} slide d={d:.2f}  pr {cur:.0f}->{v:.0f} ({100*(v-cur)/cur:+.1f}%)")
print(f"   schedule: d(T)=0.16*clip((T-1)/4,0,1) -> T1:0.00 T2:0.04 T3:0.08 T4:0.12 T5+:0.16")
