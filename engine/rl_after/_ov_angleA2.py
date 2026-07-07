import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
price6=g['price6']; b6=g['b6']; raw_ev=g['raw_ev']; par_pole=g['par_pole']; iso_corr=g['iso_corr']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; nseas=g['nseas']; ev=g['ev']
Y=2026

def resolve(sub, exp=None):
    hits=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hits=[p for p in hits if ev(p,Y)==exp]
    return hits[0] if len(hits)==1 else None

TARGETS=[('Joel Jeffrey',1773),('Tom Powell',1390),('Hollands',946),('Tanner Bruhn',913),
         ("O'Driscoll",896),('Heath Chapman',734),('Davies',632),('Ryan Angwin',538),('Cox',437),
         ('Jack Ginnivan',None),('Darcy Parish',None)]
CTRL={'Jack Ginnivan','Darcy Parish'}

# baseline (held) prices
base={}
for sub,exp in TARGETS:
    p=resolve(sub,exp)
    if p is None:
        print(f"UNRESOLVED {sub} exp={exp}"); continue
    base[p['player']]=(p,exp)

# level-override toggle: force engine to use CURRENT level (Lc) instead of held Leff, re-price
sav=cp._lvl_eff
def _at_current(p,Y): return _lvlcurr(p,Y)
rows=[]
for nm,(p,exp) in base.items():
    gfut=MA.gfut(p); bnow=MA.bnow(p); pk=MA.effpk(p); age=MA.age(p); ns=nseas(p,Y)
    bar=MA.REPL[gfut]-3.0
    Lold=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); Leff=cp._lvl_eff(p,Y)
    pr=price6(p,b6(p,Y),Y); raw=raw_ev(p,Y); pole=raw-pr; evf=ev(p,Y)
    cls='IMPR' if Lc>Lold+1 else ('DECL' if Lc<Lold-1 else 'flat')
    rows.append([nm,gfut,pk,age,ns,bar,Lold,Lc,Leff,Lc-bar,Leff-bar,pr,pole,evf,cls,('CTRL' if nm in CTRL else 'OV')])

# now override to current level and re-price EV
cp._lvl_eff=_at_current
evcur={}
try:
    for nm,(p,exp) in base.items(): evcur[nm]=ev(p,Y)
finally:
    cp._lvl_eff=sav

rows.sort(key=lambda r:-r[13])
h=f"{'player':17s}{'pos':>8s}{'pk':>3s}{'ag':>3s}{'ns':>3s}{'bar':>6s}{'Lold':>6s}{'Lc':>6s}{'Leff':>6s}{'PORc':>6s}{'PORe':>6s}{'pr':>6s}{'pole':>5s}{'EV':>6s}{'EV@cur':>7s}{'cls':>5s}"
print(h); print('-'*len(h))
for r in rows:
    nm,gfut,pk,age,ns,bar,Lold,Lc,Leff,porc,pore,pr,pole,evf,cls,tag=r
    print(f"{nm[:17]:17s}{gfut:>8s}{pk:>3d}{age or 0:>3.0f}{ns:>3d}{bar:>6.1f}{Lold:>6.1f}{Lc:>6.1f}{Leff:>6.1f}"
          f"{porc:>+6.1f}{pore:>+6.1f}{pr:>6.0f}{pole:>5.0f}{evf:>6d}{evcur[nm]:>7d}{('*'+cls if tag=='CTRL' else cls):>5s}")
print("\nPORc=Lc-bar (current-production margin, ~Luke's ground truth). PORe=Leff-bar (engine-used margin).")
print("EV@cur = EV re-priced forcing level=Lc (un-holds the hold-band). cls: IMPR/DECL/flat vs career L_old. *=control.")
print("\n--- b6 PEAK BAND (pedigree/ceiling prior) vs current level, key players ---")
for nm in ['Joel Jeffrey','Jack Ginnivan','Darcy Parish']:
    p=base[nm][0]; bb=b6(p,Y); Lc=_lvlcurr(p,Y); bar=MA.REPL[MA.gfut(p)]-3.0
    print(f"  {nm:14s} Lc={Lc:5.1f} bar={bar:4.1f}  band=[{','.join(f'{x:.1f}' for x in bb)}]  band_mid={np.median(bb):.1f}  peak_over_Lc={np.median(bb)-Lc:+.1f}")
