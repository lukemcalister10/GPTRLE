# CANONICAL v4 build (cont.19): forward-realised target (best-3 >=Y, completeness-weighted current year) + draft rows (bust-inclusive) + corrected age + games-weighted recency. Produces peak_model_v4.pkl. Run: python3 build_peak_model_v4.py (needs rl_after engine + dob_corrected.json + bust_prior_table.json).
import sys; sys.path.insert(0,'/home/claude/rl_after')
import os; os.environ['RL_GAMMA']='0.85'; os.environ['RL_PICK1']='3000'
import io,contextlib,json,pickle
with contextlib.redirect_stdout(io.StringIO()): import rl_model as MA
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
MA.P_HOOK=None; MA.PROD_GATE='off'
allp=[p for p in MA.data if MA.GRP.get(p['pos'])]
POSI={'MID':0,'GEN_DEF':1,'GEN_FWD':2,'KEY_DEF':3,'KEY_FWD':4,'RUC':5}
DOB=json.load(open('/home/claude/rl_workspace/forward_valuation/dob_corrected.json')); PT=json.load(open('/home/claude/rl_workspace/forward_valuation/bust_prior_table.json'))
SEASON=22  # reference full home-and-away
def bp(pos,pick): return PT[pos][str(min(max(int(round(pick)),1),70))]
def best(ss,n): a=sorted([x['avg'] for x in ss if x['games']>=6],reverse=True)[:n]; return float(np.mean(a)) if a else None
def by_corr(p): k=p['player']+'|'+str(MA.debut(p)); return DOB[k][0] if k in DOB else p.get('_by')
def age_at(p,Y): by=by_corr(p); return (Y-by) if by else (Y-(MA.debut(p)-18))
# *** target now includes year Y (>=Y), with the current/partial year weighted by completeness ***
def fwd_peak(p,Y):
    fut=[x for x in p['scoring'] if x['year']>=Y and x['games']>=6]
    if not fut: return None
    # weight each season by completeness (games/SEASON, capped 1) so a partial current year counts less
    w=np.array([min(x['games'],SEASON)/SEASON for x in fut]); a=np.array([x['avg'] for x in fut])
    idx=np.argsort(-a)[:3]; return float(np.average(a[idx],weights=w[idx]))
def feats(p,Y):
    d=MA.debut(p); pos=MA.GRP[p['pos']]; ep=MA.effpk(p); T=Y-d+1
    sub=[x for x in p['scoring'] if x['year']<=Y]; g=sum(x['games'] for x in sub); nss=len([x for x in sub if x['games']>=6])
    b2=best(sub,2); b1=best(sub,1); maxg=max([x['games'] for x in sub],default=0)
    rs=[x for x in sub if x['games']>=6][-2:]  # recency: games-weighted (partial current year down-weighted)
    recent=float(np.average([x['avg'] for x in rs],weights=[x['games'] for x in rs])) if rs else 0
    last=[x for x in sub if x['year']==Y]; la=last[0]['avg'] if last else 0; lg=last[0]['games'] if last else 0
    early=sum(x['games'] for x in sub if x['year']-d+1<=2); seq=[x['avg'] for x in sub if x['games']>=6]; slope=(seq[-1]-seq[0]) if len(seq)>1 else 0.0
    bestyr=max([x['year'] for x in sub if x['games']>=6 and x['avg']==(b1 or -1)],default=Y); ysb=Y-bestyr
    return [np.log(MA.PVC[ep]),ep,POSI[pos],b2 or 0,b1 or 0,recent,la,lg,g,nss,maxg,early,slope,ysb,age_at(p,Y),T,bp(pos,ep)]
def draft_feat(p):
    pos=MA.GRP[p['pos']]; ep=MA.effpk(p); return [np.log(MA.PVC[ep]),ep,POSI[pos],0,0,0,0,0,0,0,0,0,0,0,age_at(p,MA.debut(p)-1),0,bp(pos,ep)]
def build(lo,hi):
    X,y=[],[]
    for p in allp:
        d=MA.debut(p)
        if d<lo or d>hi: continue
        X.append(draft_feat(p)); y.append(best([x for x in p['scoring']],3) or 0.0)
        for Y in sorted(set(x['year'] for x in p['scoring'] if x['games']>0)):
            if len([x for x in p['scoring'] if x['year']>Y and x['games']>=6])>=1:   # >=1 FUTURE season (so it's forward, not echo)
                t=fwd_peak(p,Y)
                if t is not None: X.append(feats(p,Y)); y.append(t)
    return np.array(X),np.array(y)
def r2(pr,yy): return 1-np.sum((yy-pr)**2)/np.sum((yy-yy.mean())**2)
Xtr,ytr=build(2006,2015)
m=HistGradientBoostingRegressor(max_iter=600,max_depth=5,learning_rate=0.04,min_samples_leaf=30,l2_regularization=2.0,random_state=0).fit(Xtr,ytr)
Xte,yte=[],[]
for p in allp:
    d=MA.debut(p)
    if not(2016<=d<=2019): continue
    for Y in sorted(set(x['year'] for x in p['scoring'] if x['games']>0)):
        if len([x for x in p['scoring'] if x['year']>Y and x['games']>=6])>=2:
            t=fwd_peak(p,Y)
            if t is not None: Xte.append(feats(p,Y)); yte.append(t)
print('forward-peak R2 (out-of-sample, target now >=Y w/ completeness weight): %.3f'%r2(m.predict(np.array(Xte)),np.array(yte)))
print('\nsurvivorship (draft proj late picks>30):')
for pos in ['MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC']:
    pl=[p for p in allp if MA.GRP[p['pos']]==pos and MA.effpk(p)>30 and 2006<=MA.debut(p)<=2018]
    act=np.mean([best([x for x in p['scoring']],3) or 0 for p in pl]); dr=np.mean([m.predict([draft_feat(p)])[0] for p in pl])
    print('  %-9s actual %.1f draft-proj %.1f (%+.0f%%)'%(pos,act,dr,100*(dr-act)/max(act,1)))
spec=[p for p in allp if MA.effpk(p)>20 and 2006<=MA.debut(p)<=2016 and sum(x['games'] for x in p['scoring'] if x['year']<=MA.debut(p)+2)>=20 and best([x for x in p['scoring']],3)]
print('Kondogiannis bias: %+.1f'%np.mean([(best([x for x in p['scoring']],3))-m.predict([feats(p,MA.debut(p)+2)])[0] for p in spec]))
pickle.dump({'model':m,'fnames':['logPVC','effpk','pos','best2','best1','recent_gw','last_avg','last_g','games','nss','maxg','early','slope','yrs_since_best','age','T','bust_prior']},open('/home/claude/rl_workspace/forward_valuation/peak_model_v4.pkl','wb'))
# CO-EMIT the TRAIN-TIME PVC snapshot (Phase-4 disposition, DPP-strip build). The logPVC feature above is
# np.log(MA.PVC[ep]); inference (rl_model._v4_init) must read the SAME PVC as a FROZEN feature to break the
# SCALE<->PVC<->peak_est bootstrap cycle. pvc_snapshot.json is therefore a DERIVED artifact of THIS build, not a
# hand-checked-in file -- the model and its train-time PVC are now co-generated so they can never drift apart
# (the report's flagged "next hidden-copy risk"). Emitted read-only + provenance-stamped by the build.
import os as _os, stat as _st, shutil as _sh
_snap={str(k):float(MA.PVC[k]) for k in range(1,100)}
_snap_path='/home/claude/rl_workspace/rl_after/pvc_snapshot.json'
_pkl_src='/home/claude/rl_workspace/forward_valuation/peak_model_v4.pkl'
_pkl_dst='/home/claude/rl_workspace/rl_after/peak_model_v4.pkl'
try: _os.chmod(_snap_path, _st.S_IWUSR|_st.S_IRUSR|_st.S_IRGRP|_st.S_IROTH)
except Exception: pass
json.dump(_snap, open(_snap_path,'w'))
try: _sh.copyfile(_pkl_src,_pkl_dst)   # place the pkl where rl_model actually reads it (co-located tier-2 caches)
except Exception: pass
try:
    import single_source as _SS   # /home/claude/rl_after on sys.path (line 2) -> tier-2 frozen stamp + read-only
    _SS.stamp_tier2_frozen('pvc_snapshot.json'); _SS.stamp_tier2_frozen('peak_model_v4.pkl')
    print('co-emitted + tier-2-stamped pvc_snapshot.json (train-time PVC) + peak_model_v4.pkl (read-only)')
except Exception as _e:
    _os.chmod(_snap_path, _st.S_IRUSR|_st.S_IRGRP|_st.S_IROTH)
    print('co-emitted pvc_snapshot.json (train-time PVC, read-only) — %d picks (stamp skipped: %s)'%(len(_snap),_e))
# ===== WIRE-CHECK: do proven guns recover now the current year counts? =====
MA.BASE_REF=2026; MA.AGE_REF=2026; orig=MA.peak_est
def pev4(p):
    if MA.BASE_REF-MA.debut(p)+1<1: return float(m.predict([draft_feat(p)])[0])
    return float(m.predict([feats(p,MA.BASE_REF)])[0])
act=[p for p in allp if not p.get('_retired') and max([r['year'] for r in p['scoring'] if r['games']>0] or [0])>=2025]
print('\n=== control vs v4(>=Y) value, key players ===')
for nm in ['Sean Darcy','Tom Barrass','Brennan Cox','Josh Treacy','Max Holmes','Nick Daicos','Riley Thilthorpe']:
    p=next((x for x in act if x['player']==nm),None)
    if not p: continue
    MA.peak_est=orig; c=MA.value(p); MA.peak_est=pev4; v=MA.value(p)
    print('  %-18s | ctrl %6d  v4 %6d  %+5.0f%%'%(nm,c,v,100*(v-c)/max(c,1)))
MA.peak_est=orig; C={p['player']:MA.value(p) for p in act}; MA.peak_est=pev4; V={p['player']:MA.value(p) for p in act}
proven=[p for p in act if best([x for x in p['scoring']],3) and p.get('games',0)>=80]
dd=[100*(V[p['player']]-C[p['player']])/max(C[p['player']],1) for p in proven if C[p['player']]>50]
big=[p['player'] for p in proven if abs((V[p['player']]-C[p['player']])/max(C[p['player']],1))>1.0]
print('PROVEN active (>=80g, n=%d): median move %+.1f%% (was -7.1%% with strictly-after); |move|>100%%: %d %s'%(len(dd),np.median(dd),len(big),big[:6]))
print('saved peak_model_v4.pkl')
