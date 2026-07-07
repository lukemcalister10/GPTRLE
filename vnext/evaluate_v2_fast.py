"""Fast rolling-origin multi-horizon challenger (1/3/5 years)."""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import brier_score_loss, roc_auc_score, mean_absolute_error, mean_squared_error
warnings.filterwarnings('ignore')
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']
POS=['MID','DEF','FWD','RUC','KPD','KPF','UNK']

def tc(h,s):
    return ({'meaningful_seasons':'next_meaningful','games':'next_games','points':'next_points','best_avg':'next_avg'}[s] if h==1 else f'h{h}_{s}')

def matrix(train,test,draft=False):
    nums=['pick','age'] if draft else NUM
    types=sorted(set(train.draft_type.astype(str))|set(test.draft_type.astype(str))); pm={x:i for i,x in enumerate(POS)}; tm={x:i for i,x in enumerate(types)}
    def f(d):
        x=d[nums].copy(); x['pos']=d.position.map(pm).fillna(6); x['dtype']=d.draft_type.astype(str).map(tm).fillna(-1)
        return x.replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    return f(train),f(test)

def fit(train,test,h,draft=False):
    X,Y=matrix(train,test,draft); event=(train[tc(h,'meaningful_seasons')]>0).astype(int).to_numpy()
    clf=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=20,min_samples_leaf=25,l2_regularization=2,learning_rate=.08,random_state=100+h)
    clf.fit(X,event); p=np.clip(clf.predict_proba(Y)[:,1],.002,.998)
    active=event==1
    def reg(target,log=False,cap=None):
        y=train.loc[active,target].to_numpy(float); y=np.log1p(y) if log else y
        m=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=20,min_samples_leaf=20,l2_regularization=3,learning_rate=.07,loss='absolute_error',random_state=200+h)
        m.fit(X[active],y); z=m.predict(Y); z=np.expm1(z) if log else z
        return np.clip(z,0,cap) if cap else np.maximum(z,0)
    games=reg(tc(h,'games'),True,23*h); points=reg(tc(h,'points'),True,145*23*h); best=reg(tc(h,'best_avg'),False,145)
    return pd.DataFrame({'p':p,'games':p*games,'points':p*points,'best':p*best},index=test.index)

def naive(train,test,h):
    tr=train.copy(); te=test.copy(); tr['pb']=pd.cut(tr.pick,[0,10,20,30,45,60,101]); te['pb']=pd.cut(te.pick,[0,10,20,30,45,60,101]); tr['tb']=pd.cut(tr.tenure,[-1,0,1,2,4,8,99]); te['tb']=pd.cut(te.tenure,[-1,0,1,2,4,8,99]); tr['ev']=(tr[tc(h,'meaningful_seasons')]>0).astype(int)
    agg=tr.groupby(['position','pb','tb'],observed=True).agg(p=('ev','mean'),games=(tc(h,'games'),'mean'),points=(tc(h,'points'),'mean'),best=(tc(h,'best_avg'),'mean')).reset_index(); te=te.merge(agg,on=['position','pb','tb'],how='left').set_index(test.index)
    for c,t in [('p','ev'),('games',tc(h,'games')),('points',tc(h,'points')),('best',tc(h,'best_avg'))]: te[c]=te[c].fillna(te.position.map(tr.groupby('position')[t].mean())).fillna(tr[t].mean())
    evidence=np.clip(te.total_games/(20*h),0,1); recent_p=np.clip(te.games_last_2/30,0,1); level=np.where(te.weighted_avg>0,te.weighted_avg,te.last_avg); persist=np.minimum(23*h,te.games_last_2/2*h)
    te['p']=np.where(te.tenure==0,te.p,.55*te.p+.45*recent_p); te['games']=np.where(te.tenure==0,te.games,evidence*persist+(1-evidence)*te.games); te['points']=np.where(te.tenure==0,te.points,evidence*persist*level+(1-evidence)*te.points); te['best']=np.where(te.tenure==0,te.best,evidence*np.maximum(level,te.career_best)+(1-evidence)*te.best)
    return te[['p','games','points','best']].clip(lower=0)

def score(test,p,h):
    ev=(test[tc(h,'meaningful_seasons')]>0).astype(int).to_numpy(); out={'n':len(test),'actual_event':ev.mean(),'pred_event':p.p.mean(),'brier':brier_score_loss(ev,p.p)}
    try: out['auc']=roc_auc_score(ev,p.p)
    except: out['auc']=None
    for a,b in [(tc(h,'games'),'games'),(tc(h,'points'),'points'),(tc(h,'best_avg'),'best')]: out['mae_'+b]=mean_absolute_error(test[a],p[b]); out['rmse_'+b]=mean_squared_error(test[a],p[b])**.5
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--out',required=True); a=ap.parse_args(); df=pd.read_csv(a.dataset); O=Path(a.out); O.mkdir(parents=True,exist_ok=True); ms=[]; ps=[]
    origins={1:[2023,2024,2025],3:[2021,2022,2023],5:[2019,2020,2021]}
    for h,years in origins.items():
      for origin in years:
        train=df[(df.origin_year+h<origin)&(df.origin_year>=2008)].copy(); test=df[df.origin_year==origin].copy()
        for model in ['naive','challenger','draft_specialist']:
          if model=='naive': pred=naive(train,test,h)
          else:
            pred=fit(train,test,h,False)
            if model=='draft_specialist':
              dm=train.tenure.eq(0); dt=test.tenure.eq(0)
              if dm.sum()>250 and dt.any(): pred.loc[dt]=fit(train[dm],test[dt],h,True).values
          m=score(test,pred,h); m.update(model=model,horizon=h,origin=origin); ms.append(m)
          z=test[['key','player','origin_year','position','pick','tenure',tc(h,'games'),tc(h,'points'),tc(h,'best_avg'),tc(h,'meaningful_seasons')]].copy(); z.columns=['key','player','origin_year','position','pick','tenure','actual_games','actual_points','actual_best','actual_meaningful']; z[['pred_p','pred_games','pred_points','pred_best']]=pred[['p','games','points','best']].to_numpy(); z['model']=model; z['horizon']=h; ps.append(z)
    M=pd.DataFrame(ms); P=pd.concat(ps,ignore_index=True); M.to_csv(O/'rolling_metrics.csv',index=False); P.to_csv(O/'predictions.csv',index=False)
    S=M.groupby(['horizon','model'])[[c for c in M if c not in ['model','horizon','origin','n']]].mean().reset_index(); S.to_csv(O/'summary_metrics.csv',index=False)
    slices=[]
    for (h,m),g in P.groupby(['horizon','model']):
      for name,z in [('all',g),('draft_time',g[g.tenure==0]),('early_0_2',g[g.tenure<=2]),('first_round',g[g.pick<=20]),('later_41plus',g[g.pick>=41])]:
        if len(z)<20: continue
        ev=(z.actual_meaningful>0).astype(int); r={'horizon':h,'model':m,'slice':name,'n':len(z),'actual_event':ev.mean(),'pred_event':z.pred_p.mean(),'brier':brier_score_loss(ev,z.pred_p),'mae_games':mean_absolute_error(z.actual_games,z.pred_games),'mae_points':mean_absolute_error(z.actual_points,z.pred_points),'mae_best':mean_absolute_error(z.actual_best,z.pred_best)}
        try:r['auc']=roc_auc_score(ev,z.pred_p)
        except:r['auc']=None
        slices.append(r)
    pd.DataFrame(slices).to_csv(O/'slice_metrics.csv',index=False); payload={'summary':S.to_dict('records'),'origins':origins}; (O/'summary.json').write_text(json.dumps(payload,indent=2)); print(S.to_string(index=False))
if __name__=='__main__':main()
