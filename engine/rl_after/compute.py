import io,contextlib,json
with contextlib.redirect_stdout(io.StringIO()):
    import rl_model as MA
from collections import defaultdict
import numpy as np
data=MA.data; GRP=MA.GRP
def cg(p): return sum(r['games'] for r in p['scoring'])
# SINGLE SOURCE = rl_model.py: establishment-P (pgrid + P_estab + P_HOOK), the Brodie role-reliability cut, and the
# present-identity overrides were all ported INTO rl_model.py on 2026-06-21 and apply at import -> compute INHERITS
# them via MA.value. These aliases are for the analysis panel only; do NOT re-apply the cut/override here (double-count).
est=MA.established; grp3=MA.grp3; P_estab=MA.P_estab; brodie_sig=MA.brodie_sig
# ---- compute after (gating + Brodie cut + overrides all baked into MA.value now) ----
after={}; brod=[]
for p in MA.players:
    pt=MA.value(p,'bal'); pres=MA.proj_value(p,0)
    if brodie_sig(p): brod.append(p.get('player'))
    after[p['key'] or MA.slug(p['player'])]={'name':p.get('player'),'pos':GRP.get(p.get('_pos_now') or p['pos']),
        'pick':MA.effpk(p),'type':p['type'],'g':cg(p),'P':round(P_estab(p),3) if not est(p) else 1.0,'v':pres,'pt':pt}
# ---- before = current live shipped board ----
before={}
ba=json.load(open('/home/claude/rl_build/rl_app_data.json'))['active']
for r in ba: before[r.get('key') or MA.slug(r['name'])]={'name':r['name'],'v':r['v']}
json.dump({'before':before,'after':after,'brodie':brod},open('/tmp/cmp.json','w'))
# ---- VALIDATION vs documented anchors ----
def show(nm):
    ka=[k for k,a in after.items() if a['name']==nm]; kb=[k for k,b in before.items() if b['name']==nm]
    a=after[ka[0]] if ka else None; b=before[kb[0]] if kb else None
    print("  %-20s before=%-6s after=%-6s P=%-5s g=%-3s"%(nm,(b['v'] if b else '—'),(a['v'] if a else '—'),(a['P'] if a else '—'),(a['g'] if a else '—')))
print("VALIDATION (before=live shipped convex; after=v3.4+P convex):")
for nm in ['Tristan Xerri','Will Brodie','Lachlan McAndrew','Ned Moyle','Nick Madden','Harry Sheezel','Jai Newcombe',"Reilly O'Brien"]:
    show(nm)
print("\nBrodie-signal caught:",brod)
print("active before=%d after=%d"%(len(before),len(after)))
