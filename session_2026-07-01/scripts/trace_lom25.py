import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA'];cp=g['cp'];PR=g['PR'];ev=g['ev'];raw_ev=g['raw_ev'];iso_corr=g['iso_corr']
nseas=g['nseas'];draftval=g['draftval'];_sitout_cls=g['_sitout_cls']
SITOUT=g['SITOUT_RETAIN']
RAISED={'RUC':[0.95,0.95,0.84,0.72,0.61,0.50],'KPP':[0.80,0.80,0.70,0.60,0.50,0.40],'nonKPP':[0.60,0.60,0.52,0.45,0.38,0.30]}
p=[x for x in MA.data if 'lombard' in x['player'].lower()][0]
# --- replicate ASOF Y=2025 truncation (as the walk-forward book does) ---
Y=2025
full=p['scoring']
p['scoring']=[r for r in full if r['year']<=Y]
p['_retired']=False; p['_last_listed']=None
MA.BASE_REF=Y; MA.AGE_REF=Y; MA._pe_clear()
pos=MA.gfut(p); dv=draftval(p); ns=nseas(p,Y); el=PR.tenure(p,Y); N=min(max(el,1),6); cls=_sitout_cls(pos)
e=raw_ev(p,Y)*iso_corr(pos,MA.effpk(p))
print('Lombard @ ASOF Y=2025 (his YEAR-1, book view):')
print('  truncated scoring:',[(r['year'],r['games'],r['avg']) for r in p['scoring']])
print(f'  ns(>=6g)={ns}  el={el}  N={N}  cls={cls}  effpk={MA.effpk(p)}  dv={dv:.0f}')
print(f'  ns==0 CLIFF fires -> {ns==0}')
anc_cur=dv*SITOUT[cls][N-1]; anc_rai=dv*RAISED[cls][N-1]
print(f'  CURRENT sit-out anchor  = dv*{SITOUT[cls][N-1]} = {anc_cur:.0f}   (== current year-1 book value; his 4 games count for NOTHING)')
print(f'  RAISED  sit-out anchor  = dv*{RAISED[cls][N-1]} = {anc_rai:.0f}   (+0.1 placeholder)')
print(f'  production e from 4 games (currently DISCARDED) = {e:.0f}')
# post-blend
G=sum(x['games'] for x in p['scoring'] if x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
for GF,SH in [(44.0,1.3)]:
    w=float(np.clip(G/GF,0,1))**SH
    print(f'  BLEND: G(career games)={G}  w=clip({G}/{GF})^{SH}={w:.3f}')
    print(f'    post-blend value (raised anchor) = (1-{w:.3f})*{anc_rai:.0f} + {w:.3f}*{e:.0f} = {(1-w)*anc_rai+w*e:.0f}')
    print(f'    post-blend value (current anchor)= (1-{w:.3f})*{anc_cur:.0f} + {w:.3f}*{e:.0f} = {(1-w)*anc_cur+w*e:.0f}')
p['scoring']=full; MA.BASE_REF=MA.AGE_REF=2026; MA._pe_clear()
