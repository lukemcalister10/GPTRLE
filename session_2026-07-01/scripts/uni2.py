import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def gm(p,y):
    r=g_y(p,y); return r['games'] if r else 0
# BOOK-STYLE reconciliation: cohort-mean ev over ALL debuted members (not just g>=6 both)
print("=== BOOK-STYLE cohort-mean ev 2025 vs 2026 (all debuted members), split by 2026 games ===")
print(f"{'coh':>5s} {'nAll':>4s} {'ev25':>6s} {'ev26':>6s} {'d%ALL':>6s} | {'n_on':>4s} {'d%on(g>=6)':>9s} | {'n_off':>5s} {'d%off(g<6)':>10s}")
for C in range(2016,2024):
    mem=[p for p in MA.data if p.get('year')==C and any(r['games']>=1 for r in p['scoring'] if r['year'] in (2025,2026))]
    if not mem: continue
    def md(sub):
        ds=[]
        for p in sub:
            try: va,vb=ev(p,2025),ev(p,2026)
            except: continue
            if va>0: ds.append((vb-va)/va)
        return (np.mean(ds)*100 if ds else None), len(ds)
    dall,nall=md(mem)
    on=[p for p in mem if gm(p,2026)>=6]; off=[p for p in mem if gm(p,2026)<6]
    don,non=md(on); doff,noff=md(off)
    e25=np.mean([ev(p,2025) for p in mem]); e26=np.mean([ev(p,2026) for p in mem])
    f=lambda x: f"{x:>5.0f}%" if x is not None else "   - "
    print(f"{C:>5d} {nall:>4d} {e25:>6.0f} {e26:>6.0f} {f(dall):>6s} | {non:>4d} {f(don):>9s} | {noff:>5d} {f(doff):>10s}")
