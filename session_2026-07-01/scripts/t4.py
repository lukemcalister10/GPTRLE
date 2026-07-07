import io,contextlib
src=open('s4_matrix_M1v7.py').read()
marker="cp._lvl_eff=_inferM1; g['b6']=_b6fix"
preamble=src.split(marker)[0]+marker+"\n"
ns={}
with contextlib.redirect_stdout(io.StringIO()): exec(preamble, ns)
g=ns['g']; MA=g['MA']; ev=g['ev']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
print("TEST 4: M1+v7 re-price of the two traced players (baseline in parens)")
for key,b25,b26 in [('ed-richards',4188,2487),('charlie-curnow',1849,944)]:
    p=next(x for x in MA.data if x['key']==key)
    v25,v26=ev(p,2025),ev(p,2026)
    print(f"  {key:16s} M1v7: {v25}->{v26} ({100*(v25-v26)/v25:.0f}% drop)  |  baseline: {b25}->{b26} ({100*(b25-b26)/b25:.0f}% drop)")
