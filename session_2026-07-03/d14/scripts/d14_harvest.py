#!/usr/bin/env python3
# D14 harvest: current-roster REAL ND players — pos(gfut) x draft-age x recorded pick x CAPPED V0 (_v0_raw, post ruck-cap pre-guard).
import os,sys,io,contextlib,json,hashlib
RA='/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0',RL_GAMMA='0.85',RL_PICK1='3000',RL_RUCK_TAX='0.25',RL_RECENCY_DECAY='0.72',RL_PRIOR_TREES='400',PAR_RAMPS='22')
sys.path[:0]=[RA,'/home/claude/rl_workspace/forward_valuation','/home/claude/rl_vendor']; os.chdir(RA)
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0],g)
MA=g['MA'];cp=g['cp'];_REAL=g['_REAL'];_v0_raw=g['_v0_raw'];_v0_uncapped=g['_v0_uncapped'];v0_start=g['v0_start']
draftval=g['draftval'];_v0key=g['_v0key']
ENG=hashlib.md5(open('_merged_recover.py','rb').read()).hexdigest()[:8]
def age_at(p,Y):
    with contextlib.redirect_stdout(io.StringIO()): return cp._age_asof(p,Y)
rows=[]
for p in MA.data:
    if id(p) not in _REAL or p.get('type')!='ND' or p.get('pick') is None: continue
    yr=p.get('year')
    a=age_at(p, yr or (cp.debutyr(p)-1))
    with contextlib.redirect_stdout(io.StringIO()):
        capped=_v0_raw(p); unc=_v0_uncapped(p); guarded=v0_start(p); pvc=draftval(p)
    rows.append(dict(player=p['player'],key=p.get('key'),year=yr,pos=MA.gfut(p),age=a,ageR=int(round(a)),
                     pick=p.get('pick'),effpk=MA.effpk(p),capped=capped,unc=unc,guarded=guarded,pvc=pvc))
out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'d14_harvest.json')
json.dump(dict(engine=ENG,n=len(rows),rows=rows),open(out,'w'))
print(f'engine={ENG} harvested {len(rows)} real ND players -> {out}')
# quick cell census
from collections import Counter,defaultdict
byposage=defaultdict(list)
for r in rows: byposage[(r['pos'],r['ageR'])].append(r)
print("\n(pos, ageR): n  [pick range]  capped-V0 range")
for pos in ['MID','KEY_FWD','KEY_DEF','GEN_FWD','GEN_DEF','RUC']:
    for a in sorted({k[1] for k in byposage if k[0]==pos}):
        rs=byposage[(pos,a)]; pk=[r['pick'] for r in rs]; v=[r['capped'] for r in rs]
        print(f"  {pos:8s} age{a:2d}: n={len(rs):3d}  pick[{min(pk):.0f}-{max(pk):.0f}]  V0[{min(v):.0f}-{max(v):.0f}]")
print("\nAge census (all pos):", dict(sorted(Counter(r['ageR'] for r in rows).items())))
print("Pos census:", dict(Counter(r['pos'] for r in rows)))
