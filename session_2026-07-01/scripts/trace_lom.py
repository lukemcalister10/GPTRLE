import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA'];cp=g['cp'];PR=g['PR'];ev=g['ev'];raw_ev=g['raw_ev'];iso_corr=g['iso_corr']
nseas=g['nseas'];draftval=g['draftval'];_sitout_cls=g['_sitout_cls'];bestlvl=g['bestlvl']
SITOUT=g['SITOUT_RETAIN']
# find Lombard
cands=[p for p in MA.data if 'lombard' in p['player'].lower()]
for p in cands:
    print('FOUND:',p['player'],'| key=',p.get('key'),'| pos=',p.get('pos'),'gfut=',MA.gfut(p),'| pick=',p.get('pick'),'effpk=',MA.effpk(p),'| draftyr=',p.get('year'),'| type=',p.get('type'))
    print('  scoring:',[(r['year'],r['games'],r['avg']) for r in p['scoring']])
    Y=2026
    ns=nseas(p,Y); el=PR.tenure(p,Y); pos=MA.gfut(p); dv=draftval(p)
    N=min(max(el,1),6); cls=_sitout_cls(pos)
    e=raw_ev(p,Y)*iso_corr(pos,MA.effpk(p))
    print(f'  ns(>=6g seasons)={ns}  tenure el={el}  N={N}  cls={cls}')
    print(f'  --> CLIFF branch fires? ns==0 -> {ns==0}')
    print(f'  sit-out anchor = dv({dv:.0f}) * retain[{cls}][{N-1}]={SITOUT[cls][N-1]} = {dv*SITOUT[cls][N-1]:.0f}')
    print(f'  raw production value e (DISCARDED by cliff) = {e:.0f}')
    print(f'  CURRENT wired ev(Lombard) = {ev(p,Y)}')
