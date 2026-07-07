import io,contextlib,copy,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; nseas=g['nseas']; cp=g['cp']; LR=cp.LEVEL_RAMP
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def gm(p,y):
    r=g_y(p,y); return r['games'] if r else 0
def w2026frac(p):  # weight fraction the 2026 season gets in _lvl_wt (games x recency)
    rows=cp._season_rows(p,2026); tw=sum(gg*cp._swt(yr,2026) for yr,gg,_ in rows)
    r26=[gg*cp._swt(yr,2026) for yr,gg,a in rows if yr==2026]
    return (r26[0]/tw if r26 and tw>0 else 0.0)
def decomp(p):
    ev25=ev(p,2025); ev26=ev(p,2026)
    q=copy.deepcopy(p); q['scoring']=[r for r in q['scoring'] if r['year']<=2025]
    ev_age=ev(q,2026)                       # aged 1yr + prior-decay, NO 2026 season
    return ev25,ev_age,ev26,(ev_age-ev25),(ev26-ev_age)

print("=== PART 1: ROZEE decomposition ===")
p=next(x for x in MA.data if x['key']=='connor-rozee')
ev25,ev_age,ev26,d_age,d_lvl=decomp(p)
print(f"trajectory: {[(r['year'],r['games'],r.get('avg')) for r in p['scoring'] if r['year']>=2021]}")
print(f"ev25={ev25} -> ev26={ev26}  total drop {ev26-ev25} ({100*(ev26-ev25)/ev25:.0f}%)")
print(f"  (a) age/tenure+prior-decay: {d_age:+.0f} ({100*d_age/ev25:+.0f}%)   [ev25 {ev25} -> ev_age {ev_age:.0f}]")
print(f"  (b) LEVEL pull of the 2g/80 2026: {d_lvl:+.0f} ({100*d_lvl/ev25:+.0f}%)   [ev_age {ev_age:.0f} -> ev26 {ev26}]")
print(f"  _lvl_wt 2025={cp._lvl_wt(p,2025):.1f} 2026={cp._lvl_wt(p,2026):.1f} | _lvl_eff 2025={cp._lvl_eff(p,2025):.1f} 2026={cp._lvl_eff(p,2026):.1f}")
print(f"  exposure 2025={cp._exposure(p,2025):.0f} 2026={cp._exposure(p,2026):.0f} (LR={LR}; shrink {min(1,cp._exposure(p,2025)/LR):.2f}->{min(1,cp._exposure(p,2026)/LR):.2f})")
print(f"  2026 weight-fraction in _lvl_wt: {100*w2026frac(p):.0f}%  (games-weighted -> 2g gets small weight)")
print(f"  COUNTERFACTUAL (discount 2g level pull = ev_age): {ev_age:.0f}  -> candidate artifact = {ev_age-ev26:+.0f}")

print("\n=== PART 2: channel decomposition ACROSS cohorts (g<6 pop: 25>=10g, 26 in 1-5g) — uniform or cohort-varying? ===")
pop=[p for p in MA.data if gm(p,2025)>=10 and 1<=gm(p,2026)<=5]
def yrs(p): return 2026-(cp.debutyr(p)-1)
buck={'young(2-4)':[],'mid(5-7)':[],'old(8+)':[]}
for p in pop:
    y=yrs(p); b='young(2-4)' if y<=4 else ('mid(5-7)' if y<=7 else 'old(8+)')
    try: ev25,ev_age,ev26,da,dl=decomp(p)
    except: continue
    if ev25>0: buck[b].append((100*da/ev25,100*dl/ev25,100*(ev26-ev25)/ev25))
print(f"{'bucket':12s} {'n':>3s} {'d_age%':>7s} {'d_level%':>8s} {'total%':>7s}")
for b,rows in buck.items():
    if not rows: continue
    a=np.array(rows); print(f"{b:12s} {len(rows):>3d} {a[:,0].mean():>7.0f} {a[:,1].mean():>8.0f} {a[:,2].mean():>7.0f}")

print("\n=== PART 3: hypothesis test ===")
gaps=[g_y(p,2026)['avg']-g_y(p,2025)['avg'] for p in pop]
print(f"(a) avg26-avg25 for g<6 pop: mean={np.mean(gaps):+.1f} median={np.median(gaps):+.1f} %below-2025={100*np.mean([x<0 for x in gaps]):.0f}% (n={len(pop)})")
w26=[w2026frac(p) for p in pop]
print(f"(b) 2026 weight-fraction in _lvl_wt: mean={100*np.mean(w26):.0f}% median={100*np.median(w26):.0f}% (if small, thin 2026 is ALREADY size-discounted -> level NOT over-weighted)")
