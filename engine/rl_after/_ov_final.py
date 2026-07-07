import io, contextlib, numpy as np, copy
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
price6=g['price6']; b6=g['b6']; raw_ev=g['raw_ev']; ev=g['ev']; _lvlcurr=g['_lvlcurr']; nseas=g['nseas']
frac=MA.frac; PEAK_AGE=MA.PEAK_AGE; DELTAS=MA.DELTAS; posval=MA.posval; REPL=MA.REPL
Y=2026
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if ev(p,Y)==exp]
    return hs[0]
J=R('Joel Jeffrey',1773); P=R('Darcy Parish'); Pw=R('Tom Powell',1390); B=R('Tanner Bruhn',913); Ch=R('Heath Chapman',734); H=R('Hollands',946)

def traj(nm,p):
    d=cp.debutyr(p); print(f"\n{nm} (debut {d}, {MA.gfut(p)} pk{MA.effpk(p)}):  yr/seas/age/ns/Lc/Leff/pr/pole/EV")
    for yy in range(d,2027):
        try:
            Lc=_lvlcurr(p,yy);Le=cp._lvl_eff(p,yy);pr=price6(p,b6(p,yy),yy);raw=raw_ev(p,yy);a=cp._age_asof(p,yy)
            print(f"    {yy} s{yy-d+1} a{a or 0:.0f} ns{nseas(p,yy)}  Lc{Lc:5.1f} Le{Le:5.1f} pr{pr:5.0f} po{raw-pr:4.0f} EV{ev(p,yy):5d}")
        except Exception as e: print(f"    {yy}: {type(e).__name__} {e}")

print("="*70,"\n(b1) REAL trajectories (improvers -> rise partly legit):")
for nm,p in [('Jeffrey',J),('Powell',Pw),('Bruhn',B)]: traj(nm,p)
print("\n"+"="*70,"\n(b1b) FLAT mediocre players (no improvement confound -> cleaner):")
for nm,p in [('Chapman',Ch),('Elijah Hollands',H)]: traj(nm,p)

print("\n"+"="*70,"\n(b2) CONSTANT-LEVEL age isolation: fix Jeffrey level at his final Lc, vary age via dob; does value rise/hold late?")
Lcj=_lvlcurr(J,Y); MA._LEVEL_OVR=None
for tgt_age in [20,23,26,29,32]:
    J2=copy.deepcopy(J); yr,mo,da=J2['dob'].split('-'); J2['dob']=f"{2026-tgt_age}-{mo}-{da}"
    # override current level to fixed Lcj by monkeypatching _lvlcurr's source is hard; instead read proj shape via age curve
    a=MA.age(J2); pa=PEAK_AGE[MA.gfut(J2)]
    fwd=[frac(a+k,pa) for k in range(12)]; ey=sum(f for f in fwd if f>=0.42)
    # value of a FLAT player at margin (Lcj-bar) integrated over runway (approx proj core, level=Lcj held)
    bar=REPL[MA.gfut(J2)]; d=0.15
    approx=sum(posval(Lcj*max(f,1.0 if a+k<=pa else f)-bar)*21/((1+d)**k) for k,f in enumerate(fwd) if f>=0.42)
    print(f"   age{tgt_age}: eff_fwd_yrs={ey:5.2f}  approx_fwd_value(level fixed {Lcj:.1f}, margin +{Lcj-bar:.1f})={approx:6.0f}")

print("\n"+"="*70,"\n(b3) RUNWAY toggle: age Jeffrey 24->29 (Parish's age), re-price (caveat: tenure shifts):")
J2=copy.deepcopy(J); yr,mo,da=J2['dob'].split('-'); J2['dob']=f"{int(yr)-5}-{mo}-{da}"
print(f"   Jeffrey age{MA.age(J):.0f}: EV={ev(J,Y)} pr={price6(J,b6(J,Y),Y):.0f}  ->  aged {MA.age(J2):.0f}: EV={ev(J2,Y)} pr={price6(J2,b6(J2,Y),Y):.0f}")
print(f"   (Parish age29 EV=1484 for reference)")

print("\n"+"="*70,"\n(b4) BAND pedigree sensitivity: Jeffrey b6 at pk30 vs pk60 (prior vs ceiling):")
for pk in [30,60]:
    old=J.get('_eff'); J['_eff']=pk; bb=b6(J,Y)
    if old is None: J.pop('_eff',None)
    else: J['_eff']=old
    print(f"   pk{pk}: cpb={[f'{x:.1f}' for x in bb[:5]]} q97={bb[5]:.1f}")
print(f"   Jeffrey Lc={_lvlcurr(J,Y):.1f} (upper band/ceiling projects ABOVE produced level)")

print("\n"+"="*70,"\n(fade) MATURE-FADE curve (DELTAS: frac of peak by yrs past peak-age):")
xs=sorted(DELTAS); print("   yrs_past_peak: "+" ".join(f"{k:+d}" for k in xs if -2<=k<=12))
print("   frac_of_peak:  "+" ".join(f"{DELTAS[k]:.2f}" for k in xs if -2<=k<=12))
print(f"   '84%' = DELTAS[+7]={DELTAS[7]:.2f}; good-mature band ~+5..+9 = {DELTAS[5]:.2f}..{DELTAS[9]:.2f}")
for nm,p in [('Parish GENUINE',P)]:
    a=MA.age(p);pa=PEAK_AGE[MA.gfut(p)];Lc=_lvlcurr(p,Y);bar=REPL[MA.gfut(p)]-3
    print(f"   {nm}: age{a:.0f} peak_age{pa} => +{a-pa:.0f}yr, frac={frac(a,pa):.2f}; current {Lc:.1f} (+{Lc-bar:.1f}), fades {frac(a,pa):.2f}->slowly")
print("   NOTE: DELTAS is position-uniform -> identical % for genuine vs propped; a propped peak retains the same 84%.")
