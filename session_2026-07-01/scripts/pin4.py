import io,contextlib
src=open('s4_matrix_M1v7.py').read()
marker="cp._lvl_eff=_inferM1; g['b6']=_b6fix"
ns={}
with contextlib.redirect_stdout(io.StringIO()): exec(src.split(marker)[0]+marker+"\n", ns)
g=ns['g']; MA=g['MA']; ev=g['ev']
p=next(x for x in MA.data if x['key']=='connor-rozee')
print(f"TEST 4 M1+v7 x Rozee: 2025={ev(p,2025)} 2026={ev(p,2026)}  | baseline 2025=3874 2026=2679")
