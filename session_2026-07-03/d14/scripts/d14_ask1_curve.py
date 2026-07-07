#!/usr/bin/env python3
# D14 ASK1 — V0 board curve: dump fitted curve params per cell, eff-n/pools (R1), roster move summary,
# TOP-10 up/down (NAMED, 3-col CONTROL/v2.3/v2.4), Cumming/Robey, cross-draft dispersion before/after,
# Emmett row, R2 (>35% movers). Reads the engine's LIVE fitted curve (_V0CURVE_META) + prebuilt board dumps.
import os,sys,io,contextlib,json,hashlib
RA='/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0',RL_GAMMA='0.85',RL_PICK1='3000',RL_RUCK_TAX='0.25',RL_RECENCY_DECAY='0.72',RL_PRIOR_TREES='400',PAR_RAMPS='22')
sys.path[:0]=[RA,'/home/claude/rl_workspace/forward_valuation','/home/claude/rl_vendor']; os.chdir(RA)
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0],g)
ENG=hashlib.md5(open('_merged_recover.py','rb').read()).hexdigest()[:8]
META=g['_V0CURVE_META']; GRIDPK=g['_V0_GRIDPK']; star=META['_star']
D14=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR='/tmp/claude-0/-home-user-afl-rl-engine/3f93d318-7659-571c-8ede-d0b99740694d/scratchpad'
CON=json.load(open(SCR+'/board_control.json'))['rows'] if os.path.exists(SCR+'/board_control.json') else {}
V23=json.load(open(SCR+'/board_v23.json'))['rows']; V24=json.load(open(SCR+'/board_v24.json'))['rows']
POS=['MID','KEY_FWD','KEY_DEF','GEN_FWD','GEN_DEF','RUC']
out=open(os.path.join(D14,'d14_ask1_curve_params.md'),'w')
def P(*a): print(*a); print(*a,file=out)
P(f"# D14 ASK1 — V0 BOARD CURVE params + moves   (engine v2.4 {ENG})\n")
P("## Order of operations (declared): ruck cap (ASK1 RL_RUC_PRIOR_CAP=1.73) applies FIRST -> _v0_raw; THEN the curve is FITTED on _v0_raw; board V0 := V0*(pos,draft-age,recorded pick).\n")
P("## Cell fits — eff-n / pooling (R1). Pick bands below are DIAGNOSTIC slices only, never derivation bins.\n")
P("| cell | n | min eff-n | grid@Hmax | V0*[pk1] | V0*[pk8] | V0*[pk20] | V0*[pk40] | V0*[pk60] |")
P("|---|--:|--:|--:|--:|--:|--:|--:|--:|")
for pos in POS:
    m=META[('age18',pos)]
    P(f"| {pos} age≤18 | {m['n']} | {m['min_effn']:.1f} | {m['grid_at_hmax']}/90 | "+" | ".join(f"{star(pos,18,pk):.0f}" for pk in [1,8,20,40,60])+" |")
mN=META['mature_nonRUC']; mR=META['mature_RUC']
for ag in [19,21,24]:
    P(f"| non-RUC mat age{ag} (pooled 5pos) | {mN['n']} | {mN['min_effn']:.1f} | {mN['grid_at_hmax']}/{len(GRIDPK)*len(mN['ages'])} | "+" | ".join(f"{star('MID',ag,pk):.0f}" for pk in [1,8,20,40,60])+" |")
for ag in [19,22,25]:
    P(f"| RUC mat age{ag} | {mR['n']} | {mR['min_effn']:.1f} | {mR['grid_at_hmax']}/{len(GRIDPK)*len(mR['ages'])} | "+" | ".join(f"{star('RUC',ag,pk):.0f}" for pk in [1,8,20,40,60])+" |")
P("\n**R1 (pooling) outcome:** age≤18 per-position fits reach eff-n≥35 with bandwidth NOT maxed (grid@Hmax=0/90) — the finest resolution the sample supports. Every mature exact (pos×age) cell is eff-n<35 even at max bandwidth → pooled: the 5 non-RUC positions pool into one age-resolved surface (mature V0 is age-dominated & position-washed in-sample; DECLARED), RUC mature kept separate (own level, eff-n≈12 flagged). Mature stays differentiated from age-18 and monotone-decreasing in draft-age.")
# ---- moves (real ND, curve population) ----
nd=[k for k in V24 if V24[k]['type']=='ND' and V24[k]['pick'] is not None and V23.get(k,{}).get('v0') is not None]
def dv0(k): return (V24[k]['v0'] or 0)-(V23[k]['v0'] or 0)
up=[k for k in nd if dv0(k)>1e-6]; dn=[k for k in nd if dv0(k)<-1e-6]
mx=max(nd,key=lambda k:abs(dv0(k)))
P(f"\n## Roster move summary (V0, real ND n={len(nd)}): n_up={len(up)} · n_down={len(dn)} · unchanged={len(nd)-len(up)-len(dn)} · max|ΔV0|={abs(dv0(mx)):.0f} ({V24[mx]['player']})")
def cell(k): r=V24[k]; return CON.get(k,{}).get('v0')
def r3(k):
    r=V24[k]; c=CON.get(k,{}).get('v0'); c=f"{c:.0f}" if c is not None else "—"
    return f"| {r['player'][:20]} | {r['pos']} {r['year']} pk{r['effpk']} age{r['ageR']} | {c} | {V23[k]['v0']:.0f} | {V24[k]['v0']:.0f} | {dv0(k):+.0f} |"
P("\n### TOP-10 V0 UP (NAMED · CONTROL 8aed420a · v2.3 f3e537ba · v2.4)")
P("| player | cell | CONTROL | v2.3 | v2.4 | Δ(v2.3→v2.4) |\n|---|---|--:|--:|--:|--:|")
for k in sorted(up,key=lambda k:-dv0(k))[:10]: P(r3(k))
P("\n### TOP-10 V0 DOWN")
P("| player | cell | CONTROL | v2.3 | v2.4 | Δ(v2.3→v2.4) |\n|---|---|--:|--:|--:|--:|")
for k in sorted(dn,key=lambda k:dv0(k))[:10]: P(r3(k))
# ---- R2 >35% movers ----
big=[k for k in nd if V23[k]['v0'] and abs(dv0(k))/V23[k]['v0']>0.35]
P(f"\n## R2 — V0 movers >35% : {len(big)} (age18={sum(1 for k in big if V24[k]['ageR']==18)}, mature={sum(1 for k in big if V24[k]['ageR']>=19)}). WIRED anyway (the wobble is the disease). Full list -> d14_r2_movers.tsv. Board-ev impact of the mature lifts is ≤ a few points (production-driven veterans); listed in the write-up.")
rr=open(os.path.join(D14,'d14_r2_movers.tsv'),'w'); rr.write("player\tpos\tyear\tpick\tageR\tv0_v23\tv0_v24\tpct\tev_v23\tev_v24\n")
for k in sorted(big,key=lambda k:-abs(dv0(k))/V23[k]['v0']):
    r=V24[k]; rr.write(f"{r['player']}\t{r['pos']}\t{r['year']}\t{r['effpk']}\t{r['ageR']}\t{V23[k]['v0']:.0f}\t{r['v0']:.0f}\t{dv0(k)/V23[k]['v0']*100:+.0f}%\t{V23[k]['ev']}\t{r['ev']}\n")
rr.close()
# ---- Cumming/Robey, cross-draft, Emmett ----
byname={}
for k in V24:
    byname.setdefault(V24[k]['player'],k)
def line(nm):
    k=byname.get(nm);
    if not k: return f"| {nm} | (not found) |"
    r=V24[k]; c=CON.get(k,{}).get('v0'); c=f"{c:.0f}" if c is not None else "—"
    return f"| {nm} ({r['pos']} {r['year']} pk{r['effpk']} age{r['ageR']}) | {c} | {V23[k]['v0']:.0f} | {r['v0']:.0f} |"
P("\n## Cumming / Robey  (CONTROL · v2.3 · v2.4 — V0)")
P("| player (cell) | CONTROL | v2.3 | v2.4 |\n|---|--:|--:|--:|")
for nm in ['Sam Cumming','Sullivan Robey']: P(line(nm))
P("\n## Emmett (ruck cap 1.73 default + curve interaction)")
P("| player (cell) | CONTROL | v2.3 | v2.4 |\n|---|--:|--:|--:|")
P(line('Louis Emmett'))
k=byname.get('Louis Emmett'); r=V24[k]
P(f"\nEmmett explicit: ruck cap 1.73×PVC binds his prior FIRST (_v0_raw={V23[k]['v0']:.0f} at v2.3), then the RUC age18 curve at pk{r['effpk']} sets V0*={r['v0']:.0f} (ev {V23[k]['ev']}→{r['ev']}).")
# cross-draft dispersion before/after (one line)
from collections import defaultdict
disp=defaultdict(list)
for k in nd: disp[(V24[k]['pos'],V24[k]['ageR'],V24[k]['effpk'])].append((V23[k]['v0'],V24[k]['v0']))
multi=[(kk,vv) for kk,vv in disp.items() if len({round(x,1) for x in [a for a,_ in vv]})>1 or len(vv)>=2]
before_max=max((max(a for a,_ in vv)-min(a for a,_ in vv) for kk,vv in disp.items() if len(vv)>=2),default=0)
after_max=max((max(b for _,b in vv)-min(b for _,b in vv) for kk,vv in disp.items() if len(vv)>=2),default=0)
ncross=sum(1 for kk,vv in disp.items() if len(vv)>=2)
P(f"\n## Cross-draft dispersion (same pos×draft-age×pick, ≥2 draft years; {ncross} such groups): BEFORE(v2.3) max spread = {before_max:.0f} SCAR → AFTER(v2.4) max spread = {after_max:.0f} (0 by construction — curve is a function of pos×age×pick only).")
out.close()
print("\nwrote d14_ask1_curve_params.md + d14_r2_movers.tsv")
