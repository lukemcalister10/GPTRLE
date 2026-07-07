import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']
price6=g['price6']; b6=g['b6']; raw_ev=g['raw_ev']; ev=g['ev']; _lvlcurr=g['_lvlcurr']
Y=2026
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if ev(p,Y)==exp]
    return hs[0]
J=R('Joel Jeffrey',1773); G=R('Jack Ginnivan'); P=R('Darcy Parish')

sav_lvl=cp._lvl_eff
def price_variant(p, level_cur=False, pk=None):
    # optionally force current level, optionally override pedigree pick (effpk via _eff)
    old_eff=p.get('_eff'); 
    if pk is not None: p['_eff']=pk
    if level_cur: cp._lvl_eff=lambda q,Y: _lvlcurr(q,Y)
    try:
        v=ev(p,Y)
    finally:
        cp._lvl_eff=sav_lvl
        if pk is not None:
            if old_eff is None: p.pop('_eff',None)
            else: p['_eff']=old_eff
    return v

print("Toggle grid — EV under level x pedigree counterfactuals (isolates the two mechanisms):\n")
print(f"{'player':14s}{'base':>7s}{'lvl=cur':>9s}{'pk=60':>7s}{'both':>7s}   (base pk / age / current margin)")
for nm,p in [('Jeffrey',J),('Ginnivan',G),('Parish',P)]:
    b=price_variant(p)
    lc=price_variant(p,level_cur=True)
    pk60=price_variant(p,pk=60)
    both=price_variant(p,level_cur=True,pk=60)
    bar=MA.REPL[MA.gfut(p)]-3.0; Lc=_lvlcurr(p,Y)
    print(f"{nm:14s}{b:>7d}{lc:>9d}{pk60:>7d}{both:>7d}   (pk{MA.effpk(p)} age{MA.age(p):.0f} +{Lc-bar:.1f})")

print("\n--- gap decompositions ---")
def g_ev(p,**k): return price_variant(p,**k)
# Jeffrey vs Ginnivan
Jb,Gb=g_ev(J),g_ev(G)
Jl,Gl=g_ev(J,level_cur=True),g_ev(G,level_cur=True)
print(f"JEFFREY - GINNIVAN gap:")
print(f"  baseline:            {Jb} - {Gb} = {Jb-Gb:+d}  (Jeffrey over -> INVERSION)")
print(f"  un-hold both (lvl=cur): {Jl} - {Gl} = {Jl-Gl:+d}  ({'reversed' if Jl-Gl<0 else 'still inverted'})")
print(f"  => hold-band suppression of the improver moves the gap by {(Jl-Gl)-(Jb-Gb):+d}")
# Jeffrey vs Parish
Pb=g_ev(P); Pl=g_ev(P,level_cur=True); Jpk=g_ev(J,pk=60)
print(f"\nJEFFREY - PARISH gap:")
print(f"  baseline:            {Jb} - {Pb} = {Jb-Pb:+d}  (Jeffrey over despite +5 vs +16 margin)")
print(f"  un-hold both:        {Jl} - {Pl} = {Jl-Pl:+d}  (hold-band doesn't fix it; both ~at current)")
print(f"  Jeffrey pedigree pk30->60: {Jb} -> {Jpk} ({Jpk-Jb:+d})  = pedigree-band contribution to Jeffrey")
print(f"  Jeffrey@pk60 - Parish:  {Jpk} - {Pb} = {Jpk-Pb:+d}  ({'reversed' if Jpk-Pb<0 else 'still inverted'})")
