import io, contextlib, json
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA = g['MA']; ev = g['ev']; nseas = g['nseas']

def find(nm):
    c = [p for p in MA.data
         if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    return c[0] if c else None

FIELDS = ['player', 'pos', '_pos_now', '_pos_draft', '_pos_drafted',
          '_fut', 'ns', 'games', 'gp', 'age']

for nm, exp in [('Maric', 1409), ('Langdon', 593)]:
    p = find(nm)
    if not p:
        print(f"{nm}: NOT FOUND"); continue
    v = ev(p)
    tag = 'OK' if v == exp else f'  <-- MISMATCH (expect {exp}; OLD store would give {"1427" if nm=="Maric" else "1122"})'
    print(f"\n=== {p['player']}  EV={v}  (expect {exp}) {tag}")
    shown = {k: p[k] for k in FIELDS if k in p}
    print("  fields:", json.dumps(shown, default=str))
