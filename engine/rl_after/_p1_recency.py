import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; _lvlcurr=g['_lvlcurr']; ev=g['ev']
LD=g['LDECAY_G']; _ldg=g['_ldg']; REC=0.72; Y=2026
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if ev(p,Y)==exp]
    return hs[0] if len(hs)==1 else (f"AMBIG {[q['player'] for q in hs]}")

def rows(p):  # (year, games, avg), season with games>0 within career window
    d=cp.debutyr(p); return [(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (d-1)<x['year']<=Y]
def wtd_recent(p,n):  # games-weighted avg of the n most-recent seasons (games>0)
    rr=sorted(rows(p),key=lambda r:-r[0])[:n]; tg=sum(r[1] for r in rr)
    return sum(r[1]*r[2] for r in rr)/tg if tg else 0.0
def compose(p):
    rr=rows(p); gg=_ldg(MA.gfut(p)); ld=LD[gg]
    # Lc weights (0.35^k GEN etc) and 0.72^k weights, games-scaled
    wl=[(yr,gm,av, gm*ld**max(0,Y-yr), gm*REC**max(0,Y-yr)) for yr,gm,av in rr]
    Wl=sum(w[3] for w in wl); W72=sum(w[4] for w in wl)
    frac_old_Lc = sum(w[3] for w in wl if Y-w[0]>=2)/Wl if Wl else 0
    frac_old_72 = sum(w[4] for w in wl if Y-w[0]>=2)/W72 if W72 else 0
    return wl,frac_old_Lc,frac_old_72

names=[('Tom Powell',1390,'OV?'),('Jack Ginnivan',None,'improver'),('Tanner Bruhn',913,'improver'),
       ('Will Day',None,'FAIR'),('Caleb Serong',None,'FAIR')]
print("=== 1b RECENCY COMPOSITION ===")
for sub,exp,tag in names:
    p=R(sub,exp)
    if isinstance(p,str): print(f"\n{sub}: {p}"); continue
    wl,foLc,fo72=compose(p)
    bar=MA.REPL[MA.gfut(p)]-3; Lc=_lvlcurr(p,Y); Le=cp._lvl_eff(p,Y); Lo=cp._lvl_eff_orig(p,Y); lw=cp._lvl_wt(p,Y)
    r1=wtd_recent(p,1); r2=wtd_recent(p,2)
    print(f"\n{p['player']} [{tag}] {MA.gfut(p)} bar{bar:.1f}  (ld={LD[_ldg(MA.gfut(p))]}^k for Lc; 0.72^k for lvl_wt/L_old)")
    print(f"   {'yr':>5s}{'g':>4s}{'avg':>6s}{'wLc%':>6s}{'w72%':>6s}")
    Wl=sum(w[3] for w in wl); W72=sum(w[4] for w in wl)
    for yr,gm,av,wa,wb in wl:
        print(f"   {yr:>5d}{gm:>4d}{av:>6.1f}{100*wa/Wl:>6.1f}{100*wb/W72:>6.1f}")
    print(f"   recent-1 avg={r1:.1f}  recent-2 avg={r2:.1f}   Lc={Lc:.1f}  lvl_wt={lw:.1f}  L_old={Lo:.1f}  Leff={Le:.1f}")
    print(f"   frac of Lc from seasons >=2yr old = {100*foLc:.0f}% ; frac of lvl_wt(0.72^k) from >=2yr old = {100*fo72:.0f}%")
    print(f"   Lc - recent1 = {Lc-r1:+.1f} ; Leff - recent1 = {Le-r1:+.1f} ; Leff - recent2 = {Le-r2:+.1f}  (PORc={Lc-bar:+.1f})")

print("\n\n=== 1c PARISH season data (for the 93.4-vs-86 reconcile) ===")
P=R('Darcy Parish')
rr=rows(P); print(f"   Darcy Parish {MA.gfut(P)}  all seasons (yr,g,avg):")
for yr,gm,av in rr: print(f"      {yr}: g{gm:>2d} avg{av:.1f}")
print(f"   raw career-high season avg = {max(a for _,_,a in rr):.1f} ; present Lc={_lvlcurr(P,Y):.1f} ; lvl_wt={cp._lvl_wt(P,Y):.1f}")
print(f"   debutyr={cp.debutyr(P)}  (seasons 1-5 = {cp.debutyr(P)}..{cp.debutyr(P)+4})")
