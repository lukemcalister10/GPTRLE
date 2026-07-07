import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; dp=g['dp']; rd=g['rd']; b6=g['b6']; price6=g['price6']; WQ6=g['WQ6']
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if g['ev'](p,2026)==exp]
    return hs[0] if len(hs)==1 else [q['player'] for q in hs]

P6=[0.10,0.30,0.50,0.70,0.90,0.97]
def qfunc(bb,tau):  # monotone quantile function from the 6 band points; linear extrap below .10
    if tau< P6[0]:
        sl=(bb[1]-bb[0])/(P6[1]-P6[0]); return bb[0]-sl*(P6[0]-tau)
    return float(np.interp(tau,P6,bb))
def price_scheme(p,Y,taus,w):  # replicate price6 pricing (REPL_DROP ctx) with a custom percentile scheme; LEVEL fixed via b6
    bb=b6(p,Y); w=np.array(w)/sum(w)
    sav=dict(MA.REPL)
    try:
        for gg in MA.REPL: MA.REPL[gg]=sav[gg]-rd.REPL_DROP.get(gg,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()):
            vals=[dp.v_at_peak(p,float(qfunc(bb,t)),'bal') for t in taus]
        return float(dp.SCALE_DIST*np.dot(w,vals))
    finally: MA.REPL.update(sav)

# ladder (recent/current seasons; book-Parish as-of yr3 pre-breakout)
Preg=R('Darcy Parish')
LAD=[('bookParish-yr3',Preg,2018,'PUREBAND'),('Jeffrey',R('Joel Jeffrey',1773),2026,'MIDOV'),
     ('Bruhn',R('Tanner Bruhn',913),2026,'MIDOV'),("O'Driscoll",R("Nathan O'Driscoll",896),2026,'MIDOV'),
     ('WillDay',R('Will Day'),2026,'FAIR'),('Serong',R('Caleb Serong'),2026,'FAIR'),
     ('Butters',R('Zak Butters'),2026,'ELITE'),('Bontempelli',R('Marcus Bontempelli'),2026,'ELITE'),
     ('ClaytonOliver',R('Clayton Oliver'),2026,'ELITE-decl'),('Reid-yr1',R('Harley Reid'),2026,'YOUNG')]

print("WQ6 weights on [q10,q30,q50,q70,q90,q97] =",list(np.round(WQ6,3)),"-> top2(q90,q97)=",round(WQ6[4]+WQ6[5],2))
print("\n=== VALIDATION: my re-priced current scheme vs engine price6 ===")
for nm,p,Y,tier in LAD[:3]:
    mine=price_scheme(p,Y,P6,WQ6); eng=price6(p,b6(p,Y),Y)
    print(f"  {nm:16s} mine={mine:.0f}  price6={eng:.0f}  diff={mine-eng:+.1f}")

VARIANTS={
 '1_current':      (P6, list(WQ6)),
 '2_no_q97(5b)':   ([.10,.30,.50,.70,.90], [.2]*5),
 '3_no_q90(keepq97)':([.10,.30,.50,.70,.97], [.18,.18,.18,.18,.10]),
 '4_slidup(15-95)':([.15,.35,.55,.75,.95], [.2]*5),
}
print("\n=== PART 2 SWEEP (level fixed): pr per variant, and Δ% vs current (anchored to Serong) ===")
rows={}
for nm,p,Y,tier in LAD:
    rows[nm]=(tier,{v:price_scheme(p,Y,t,w) for v,(t,w) in VARIANTS.items()})
hdr=f"{'player':16s}{'tier':11s}"+''.join(f"{v.split('_')[0]+v.split('_')[1][:7]:>12s}" for v in VARIANTS)
print(hdr)
for nm,(tier,pv) in rows.items():
    print(f"{nm:16s}{tier:11s}"+''.join(f"{pv[v]:>12.0f}" for v in VARIANTS))
# relative to current, anchored to Serong's shift
print("\nΔ% vs current, RE-ANCHORED to Serong (so a reference stays ~0):")
serong=rows['Serong'][1]
print(f"{'player':16s}{'tier':11s}"+''.join(f"{v.split('_')[1][:9]:>11s}" for v in list(VARIANTS)[1:]))
for nm,(tier,pv) in rows.items():
    cur=pv['1_current']
    cells=[]
    for v in list(VARIANTS)[1:]:
        raw=100*(pv[v]-cur)/cur
        anch=100*(serong[v]-serong['1_current'])/serong['1_current']
        cells.append(raw-anch)
    print(f"{nm:16s}{tier:11s}"+''.join(f"{c:>+11.1f}" for c in cells))
print("\n(negative = shaved MORE than Serong. Watch: PUREBAND/MIDOV should shave > ELITE; YOUNG(Reid) must NOT crater.)")
