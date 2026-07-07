import io, contextlib
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; PR=g['PR']; rd=g['rd']
price6=g['price6']; b6=g['b6']; raw_ev=g['raw_ev']; par_pole=g['par_pole']; iso_corr=g['iso_corr']
_lvlcurr=g['_lvlcurr']; _nqual=g['_nqual']; nseas=g['nseas']; ev=g['ev']; _eo=g['_eo']
Y=2026

print("REPL_DROP:", dict(rd.REPL_DROP))
print("REPL raw:", {k:round(v,1) for k,v in MA.REPL.items()})
print()

def resolve(sub, exp=None):
    hits=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None:
        hits=[p for p in hits if ev(p,Y)==exp]
    if len(hits)==1: return hits[0]
    return None

TARGETS=[('Joel Jeffrey',1773,'OV'),('Tom Powell',1390,'OV'),('Oliver Hollands',946,'OV'),
         ('Tanner Bruhn',913,'OV'),("O'Driscoll",896,'OV'),('Heath Chapman',734,'OV'),
         ('Davies',632,'OV'),('Ryan Angwin',538,'OV'),('Cox',437,'OV'),
         ('Jack Ginnivan',None,'CTRL'),('Darcy Parish',None,'CTRL')]

rows=[]
for sub,exp,tag in TARGETS:
    p=resolve(sub,exp)
    if p is None:
        # try each hit, report which matches
        cand=[q for q in MA.data if sub.lower() in q['player'].lower() and MA.GRP.get(q.get('pos'))]
        print(f"UNRESOLVED {sub} exp={exp}: candidates ev = {[(q['player'],ev(q,Y)) for q in cand]}")
        continue
    gfut=MA.gfut(p); bnow=MA.bnow(p); pk=MA.effpk(p); ten=PR.tenure(p,Y); ns=nseas(p,Y)
    nq=_nqual(p,Y); age=MA.age(p)
    bar_fut=MA.REPL[gfut]-3.0; bar_now=MA.REPL[bnow]-3.0
    L_old=cp._lvl_eff_orig(p,Y); Lc=_lvlcurr(p,Y); L_eff=cp._lvl_eff(p,Y)
    pr=price6(p,b6(p,Y),Y); raw=raw_ev(p,Y); pole=raw-pr
    po,par=par_pole(gfut,pk,min(max(ten,1),6)); iso=iso_corr(gfut,pk); evf=ev(p,Y)
    e_pre=raw*iso
    stale=(evf < round(e_pre)-1)
    rows.append(dict(name=p['player'],tag=tag,pos=gfut,bnow=bnow,pk=pk,ten=ten,ns=ns,nq=nq,age=age,
                     bar_fut=bar_fut,bar_now=bar_now,Lold=L_old,Lc=Lc,Leff=L_eff,
                     por_eff=L_eff-bar_fut,por_cur=Lc-bar_fut,pr=pr,pole=pole,polepct=100*pole/max(raw,1),
                     po=po,iso=iso,epre=e_pre,ev=evf,stale=stale,eo=_eo(p,Y)))

rows.sort(key=lambda r:-r['ev'])
h=f"{'player':17s}{'t':>3s}{'pos':>8s}{'pk':>3s}{'tn':>3s}{'ns':>3s}{'age':>4s}{'bar':>6s}{'Lc':>6s}{'Leff':>6s}{'POR':>6s}{'pr':>6s}{'pole':>6s}{'pol%':>5s}{'iso':>5s}{'EV':>6s}{'stl':>4s}"
print(h); print('-'*len(h))
for r in rows:
    print(f"{r['name'][:17]:17s}{r['tag'][:2]:>3s}{r['pos']:>8s}{r['pk']:>3d}{r['ten']:>3d}{r['ns']:>3d}{r['age'] or 0:>4.0f}"
          f"{r['bar_fut']:>6.1f}{r['Lc']:>6.1f}{r['Leff']:>6.1f}{r['por_eff']:>+6.1f}{r['pr']:>6.0f}{r['pole']:>6.0f}"
          f"{r['polepct']:>5.0f}{r['iso']:>5.2f}{r['ev']:>6d}{'Y' if r['stale'] else '-':>4s}")
print("\nKEY: bar=REPL[gfut]-3 (settled-pos eff bar). Lc=current recency level. Leff=level engine USES (hold-band).")
print("POR=Leff-bar (margin on the level priced). pr=production/bar-priced base. pole=raw_ev-pr (pedigree lift). pol%=pole/raw.")
print("iso=isotonic pick multiplier. stl=staleness floor bound. EV=final.")
