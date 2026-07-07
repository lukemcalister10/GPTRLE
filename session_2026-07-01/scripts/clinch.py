import io,contextlib,copy,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; cp=g['cp']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def gm(p,y):
    r=g_y(p,y); return r['games'] if r else 0
def fullpar(p):
    """price as-of-2026 with 2026 = full 22-game season at the player's 2025 level -> isolates missing-games(exposure) from aging"""
    a25=(g_y(p,2025) or {}).get('avg')
    q=copy.deepcopy(p); r=g_y(q,2026)
    if r is None: q['scoring'].append({'year':2026,'games':22,'avg':a25}); r=g_y(q,2026)
    else: r['games']=22; r['avg']=a25
    return ev(q,2026)
# Rozee clincher
p=next(x for x in MA.data if x['key']=='connor-rozee')
b25,b26,fp=ev(p,2025),ev(p,2026),fullpar(p)
print("=== CLINCHER: full-par 2026 counterfactual (22g at 2025 level) isolates EXPOSURE(missing games) vs AGING ===")
print(f"ROZEE: ev25={b25} ev26={b26} fullpar26={fp}")
print(f"  EXPOSURE/missing-games channel (fullpar - ev26) = {fp-b26:+.0f} ({100*(fp-b26)/b25:+.0f}%)")
print(f"  genuine AGING channel (ev25 - fullpar) = {b25-fp:+.0f} ({100*(b25-fp)/b25:+.0f}%)")
print(f"  -> if fullpar ~= ev25, the drop is missing-games(exposure) NOT aging\n")
# cross-cohort: exposure vs aging split
print(f"{'band':14s} {'n':>3s} {'meanDrop%':>9s} {'EXPOSURE%':>9s} {'AGING%':>7s}   (aging should be old>>young if real)")
for lbl,yrs in [('young 2022-23',range(2022,2024)),('mid 2018-20',range(2018,2021)),('old 2014-17',range(2014,2018))]:
    EX=[];AG=[];DR=[]
    for q in MA.data:
        if q.get('year') not in yrs or not (1<=gm(q,2026)<=5) or gm(q,2025)<8: continue
        try:
            b25,b26,fp=ev(q,2025),ev(q,2026),fullpar(q)
        except: continue
        if b25>0: EX.append(100*(fp-b26)/b25); AG.append(100*(b25-fp)/b25); DR.append(100*(b26-b25)/b25)
    if DR: print(f"{lbl:14s} {len(DR):>3d} {np.mean(DR):>8.0f}% {np.mean(EX):>8.0f}% {np.mean(AG):>6.0f}%")
