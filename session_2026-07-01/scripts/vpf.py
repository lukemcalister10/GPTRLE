import io,contextlib
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']
for key,exp in [('ryan-maric',1409),('ed-langdon',593)]:
    p=next((x for x in MA.data if x.get('key')==key), None)
    if p is None: print(f"{key}: NOT FOUND"); continue
    v=ev(p,2026); print(f"{key}: {v}  (expect {exp})  {'PASS' if v==exp else 'CHECK'}")
