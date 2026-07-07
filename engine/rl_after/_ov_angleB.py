import io, contextlib, numpy as np, copy
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
price6=g['price6']; b6=g['b6']; raw_ev=g['raw_ev']; ev=g['ev']; _lvlcurr=g['_lvlcurr']; nseas=g['nseas']
frac=MA.frac; PEAK_AGE=MA.PEAK_AGE; DELTAS=MA.DELTAS
Y=2026
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if ev(p,Y)==exp]
    return hs[0]
J=R('Joel Jeffrey',1773); P=R('Darcy Parish'); Pw=R('Tom Powell',1390); B=R('Tanner Bruhn',913)

print("=== (b1) EV TRAJECTORY across seasons (ev at as-of year) — does it rise? ===")
for nm,p in [('Jeffrey',J),('Powell',Pw),('Bruhn',B)]:
    d=cp.debutyr(p)
    print(f"\n{nm} (debut {d}, pos {MA.gfut(p)}, pk{MA.effpk(p)}):")
    print(f"    {'yr':>4s}{'seas#':>6s}{'age':>4s}{'ns':>3s}{'Lc':>6s}{'Leff':>6s}{'pr':>6s}{'pole':>5s}{'EV':>6s}")
    for yy in range(d, 2027):
        seas=yy-d+1
        try:
            Lc=_lvlcurr(p,yy); Leff=cp._lvl_eff(p,yy); pr=price6(p,b6(p,yy),yy); raw=raw_ev(p,yy)
            age=MA._age_asof(p,yy)
            print(f"    {yy:>4d}{seas:>6d}{age or 0:>4.0f}{nseas(p,yy):>3d}{Lc:>6.1f}{Leff:>6.1f}{pr:>6.0f}{raw-pr:>5.0f}{ev(p,yy):>6d}")
        except Exception as e:
            print(f"    {yy}: {type(e).__name__}")

print("\n\n=== (b2) RUNWAY: forward age-curve fraction (frac of peak by future year) ===")
for nm,p in [('Jeffrey(GEN_DEF,24)',J),('Parish(MID,29)',P)]:
    g0=MA.gfut(p); a=MA.age(p); pa=PEAK_AGE[g0]
    fs=[frac(a+k,pa) for k in range(11)]
    eff_years=sum(f for f in fs if f>=0.42)
    print(f"  {nm:22s} peak_age={pa}  frac[a..a+10]=[{','.join(f'{x:.2f}' for x in fs)}]  eff_fwd_years(>=.42)={eff_years:.2f}")

print("\n=== (b3) RUNWAY isolation: age Jeffrey 24->29 (dob shift +5y), re-price ===")
J2=copy.deepcopy(J)
yr,mo,da=J2['dob'].split('-'); J2['dob']=f"{int(yr)-5}-{mo}-{da}"
print(f"  Jeffrey base (age {MA.age(J):.0f}): EV={ev(J,Y)}, pr={price6(J,b6(J,Y),Y):.0f}")
print(f"  Jeffrey aged to {MA.age(J2):.0f}:  EV={ev(J2,Y)}, pr={price6(J2,b6(J2,Y),Y):.0f}   (caveat: tenure/debut also shift)")

print("\n=== (b4) BAND pedigree sensitivity: Jeffrey b6 at pk30 vs pk60 (isolate prior vs ceiling) ===")
for pk in [30,60]:
    old=J.get('_eff'); J['_eff']=pk; bb=b6(J,Y)
    if old is None: J.pop('_eff',None)
    else: J['_eff']=old
    print(f"  pk{pk}: cond_prior_band={[f'{x:.1f}' for x in bb[:5]]}  q97_ceiling={bb[5]:.1f}")
Lc=_lvlcurr(J,Y); print(f"  Jeffrey current level Lc={Lc:.1f}  (band upper/ceiling >> Lc => projected, not produced)")
