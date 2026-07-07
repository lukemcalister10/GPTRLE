import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']; era=g['era']; REF=g['REF']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; _ldg=g['_ldg']; FLAT=g['FLAT_TOL_G']; PROVEN_N=g['PROVEN_N']
def adj(a,y): return a*REF/era.get(y,REF)
def R(nm):
    h=[p for p in MA.data if p['player']==nm]; return h[0] if h else None
names=['Jack Ginnivan','Tanner Bruhn','Luke Davies-Uniacke','Will Day','Tom Powell']
Y=2026
print(f"{'player':22s}{'pos':>8s}{'nq':>3s}{'ft':>5s}{'L_old':>7s}{'Lc':>7s}{'gap':>6s}{'Leff':>7s}{'held?':>7s}")
for nm in names:
    p=R(nm)
    if not p: print(f"{nm}: NOT FOUND"); continue
    pos=MA.gfut(p); n=_nqual(p,Y); ft=FLAT[_ldg(pos)]
    Lo=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); Leff=cp._lvl_eff(p,Y)
    gap=Lc-Lo; held = (n>=PROVEN_N and Lc>=Lo and gap<=ft)
    print(f"{nm:22s}{pos:>8s}{n:>3d}{ft:>5.1f}{Lo:>7.1f}{Lc:>7.1f}{gap:>+6.1f}{Leff:>7.1f}{('HELD' if held else '-'):>7s}")
print("\n=== season history (era-adj avg; * = games>=14) ===")
for nm in names:
    p=R(nm)
    if not p: continue
    Lo=cp._lvl_eff_orig(p,Y)
    rows=[(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (cp.debutyr(p)-1)<x['year']<=Y]
    s=" ".join(f"{yr}:{gm:2d}g@{adj(a,yr):4.1f}{'*' if gm>=14 else ' '}{'^' if adj(a,yr)>Lo else ' '}" for yr,gm,a in rows)
    print(f"{nm:22s} L_old={Lo:4.1f} | {s}")
