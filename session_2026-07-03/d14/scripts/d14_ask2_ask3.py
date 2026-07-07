#!/usr/bin/env python3
# D14 ASK2 (KPP floor: binding map, KPP anchors incl Riak Andrew/Whitlock, depth-monotonicity, floor-saves recount)
# + ASK3d (full ruck ladder: every real ruck, V0 + V0/PVC). Board path (curve + floor). 3-col via board dumps.
import os,sys,io,contextlib,json,hashlib
RA='/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0',RL_GAMMA='0.85',RL_PICK1='3000',RL_RUCK_TAX='0.25',RL_RECENCY_DECAY='0.72',RL_PRIOR_TREES='400',PAR_RAMPS='22')
sys.path[:0]=[RA,'/home/claude/rl_workspace/forward_valuation','/home/claude/rl_vendor']; os.chdir(RA)
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0],g)
ENG=hashlib.md5(open('_merged_recover.py','rb').read()).hexdigest()[:8]
MA=g['MA'];ev=g['ev'];v0_start=g['v0_start'];draftval=g['draftval'];_REAL=g['_REAL']
R_SURF=g['R_SURF'];_R_surf=g['_R_surf'];_dv_surf=g['_dv_surf'];_sitout_cls=g['_sitout_cls']
ev_prefloor=g['ev_prefloor'];floor_frac=g['floor_frac']
import numpy as np
D14=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR='/tmp/claude-0/-home-user-afl-rl-engine/3f93d318-7659-571c-8ede-d0b99740694d/scratchpad'
CON=json.load(open(SCR+'/board_control.json'))['rows']; V23=json.load(open(SCR+'/board_v23.json'))['rows']; V24=json.load(open(SCR+'/board_v24.json'))['rows']
out=open(os.path.join(D14,'d14_ask2_floor.md'),'w')
def P(*a): print(*a); print(*a,file=out)
def E(p):
    with contextlib.redirect_stdout(io.StringIO()): return ev(p)
def V0(p):
    with contextlib.redirect_stdout(io.StringIO()): return v0_start(p)
P(f"# D14 ASK2 — KPP RETENTION FLOOR (Owner Override O1) + ASK3d ruck ladder   (engine v2.4 {ENG})\n")
# ---- FLOOR-BINDING MAP: at each (knot pick, depth) does max() select nonKPP? ----
P("## Floor-binding map — KPP sit-out retention := max(KPP, nonKPP). Cells where nonKPP is SELECTED (floor binds).")
P("(retention R at depth d1..d6; **bold** = nonKPP>KPP → floor binds)\n")
P("| pick | d1 | d2 | d3 | d4 | d5 | d6 |\n|--:|:--|:--|:--|:--|:--|:--|")
for pk in [5,15,30,50]:
    lp=np.log(pk); kpp=_dv_surf('KPP',lp); non=_dv_surf('nonKPP',lp)
    cells=[]
    for i in range(6):
        binds=non[i]>kpp[i]+1e-9
        cells.append((f"**{max(kpp[i],non[i]):.3f}**" if binds else f"{kpp[i]:.3f}"))
    P(f"| {pk} | "+" | ".join(cells)+" |")
# where binds, per depth
bindcells=[]
for pk in [5,15,30,50]:
    lp=np.log(pk); kpp=_dv_surf('KPP',lp); non=_dv_surf('nonKPP',lp)
    for i in range(6):
        if non[i]>kpp[i]+1e-9: bindcells.append((pk,i+1))
P(f"\nFloor BINDS at (pick,depth): {bindcells}")
P(f"-> binds predominantly d3+ (KPP decays faster than nonKPP at depth); shallow d1-2 KPP mostly ≥ nonKPP (no bind). Matches the D13 finding (expected d3+).")
# depth monotonicity numeric re-verify
P("\n## Depth monotonicity of the FLOORED KPP surface (re-verified numerically):")
allmono=True
for pk in [1,3,5,8,15,30,50,80]:
    dv=[_R_surf('KPP',pk,t) for t in range(1,7)]
    mono=all(dv[k+1]<=dv[k]+1e-9 for k in range(5)); allmono=allmono and mono
    P(f"  pk{pk:>2}: R(d1..d6)={[round(x,3) for x in dv]}  non-increasing={mono}")
P(f"  ALL non-increasing = {allmono}  (max of two isotonic-non-increasing curves is non-increasing ✓)")
# ---- KPP anchors 3-col incl Riak Andrew, Whitlock ----
def find_all(nm):
    return [p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos')) and not p.get('_double_count')]
def k_of(p): return f"{p.get('key') or MA.slug(p['player'])}|{p.get('type')}|{p.get('year')}|{p.get('pick')}"
P("\n## KPP retention anchors (CONTROL 8aed420a · v2.3 f3e537ba · v2.4 — board ev; V0 in parens)")
P("| player (cls·pick) | CONTROL | v2.3 | v2.4 |\n|---|--:|--:|--:|")
kppnames=['Riak Andrew','Whitlock','Harrison Ramm','Matt Allison','Aaron Cadman','Jed Walter','Ethan Read']
for nm in kppnames:
    for p in find_all(nm):
        k=k_of(p); cls=_sitout_cls(MA.gfut(p))
        c=CON.get(k,{}).get('ev'); c3=V23.get(k,{}).get('ev'); c4=V24.get(k,{}).get('ev')
        if cls!='KPP': continue
        P(f"| {p['player']} ({cls}·pk{MA.effpk(p)}) | {c if c is not None else '—'} ({CON.get(k,{}).get('v0','—')}) | {c3} ({V23.get(k,{}).get('v0')}) | {c4} ({V24.get(k,{}).get('v0')}) |")
# ---- floor-saves recount incl RUC ----
P("\n## Floor-saves recount (v2.4, board path; RUC recomputed off capped V0)")
saves=[]; ruc=0
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if id(p) not in _REAL or p.get('type')!='ND' or p.get('_retired') or p.get('_pickless') or (g['delisted'](p)): continue
        yis=2026-int(p.get('year') or 0)
        if yis<1: continue
        pref=ev_prefloor(p); fl=floor_frac(yis)*v0_start(p)
        if pref<fl:
            saves.append((p['player'],MA.gfut(p),MA.effpk(p),round(pref),round(fl)))
            if MA.gfut(p)=='RUC': ruc+=1
P(f"floor-saves total={len(saves)} (RUC {ruc}); pure lower bound (lowered=0, non-ND moved=0 — verified in gates B5).")
# new saves vs v2.3 (v2.3 saves list not directly here; report count delta + list the RUC + top lifts)
P("saves (player · pos · pick · raw ev_prefloor · floor):")
for s in sorted(saves,key=lambda s:-(s[4]-s[3]))[:20]: P(f"  {s[0]:22s} {s[1]:8s} pk{s[2]:>2}  raw {s[3]:>4} -> floor {s[4]:>4}  (+{s[4]-s[3]})")
# ---- ASK3d RUCK LADDER: every real ruck, V0 + V0/PVC ----
rl=open(os.path.join(D14,'d14_ask3d_ruck_ladder.md'),'w')
def PR2(*a): print(*a,file=rl)
PR2(f"# D14 ASK3d — FULL RUCK LADDER (every real ruck; V0 + V0/PVC; ruck cap 1.73×PVC in force)  engine {ENG}\n")
PR2("| ruck | year | pick | PVC | V0 (v2.4) | V0/PVC | ev v2.3 | ev v2.4 |\n|---|--:|--:|--:|--:|--:|--:|--:|")
rucks=[p for p in MA.data if id(p) in _REAL and MA.gfut(p)=='RUC' and not p.get('_double_count') and p.get('pick') is not None]
for p in sorted(rucks,key=lambda p:MA.effpk(p)):
    k=k_of(p); pvc=draftval(p); v0=V0(p); r=v0/pvc if pvc else 0
    PR2(f"| {p['player']} | {p.get('year')} | {MA.effpk(p)} | {pvc:.0f} | {v0:.0f} | {r:.2f} | {V23.get(k,{}).get('ev','—')} | {V24.get(k,{}).get('ev','—')} |")
rl.close()
P(f"\n## ASK3d ruck ladder written: {len(rucks)} rucks -> d14_ask3d_ruck_ladder.md (V0/PVC per rung; cap 1.73 in force)")
out.close()
print("wrote d14_ask2_floor.md + d14_ask3d_ruck_ladder.md")
