"""Pooled leakage-safe 1/3/5-year challenger evaluation."""
from __future__ import annotations
import argparse,json,warnings
from pathlib import Path
import numpy as np,pandas as pd
from lightgbm import LGBMClassifier,LGBMRegressor
from sklearn.metrics import brier_score_loss,roc_auc_score,mean_absolute_error,mean_squared_error
warnings.filterwarnings('ignore')
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']
POS=['MID','DEF','FWD','RUC','KPD','KPF','UNK']
def tc(h,s):return ({'meaningful_seasons':'next_meaningful','games':'next_games','points':'next_points','best_avg':'next_avg'}[s] if h==1 else f'h{h}_{s}')
def mat(tr,te,draft=False):
 nums=['pick','age'] if draft else NUM; ts=sorted(set(tr.draft_type.astype(str))|set(te.draft_type.astype(str))); pm={x:i for i,x in enumerate(POS)}; tm={x:i for i,x in enumerate(ts)}
 def f(d):
  x=d[nums].copy();x['pos']=d.position.map(pm).fillna(6);x['dt']=d.draft_type.astype(str).map(tm).fillna(-1);return x.replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
 return f(tr),f(te)
def fit(tr,te,h,draft=False):
 X,Z=mat(tr,te,draft); ev=(tr[tc(h,'meaningful_seasons')]>0).astype(int).to_numpy()
 c=LGBMClassifier(n_estimators=100,num_leaves=18,max_depth=6,min_child_samples=30,learning_rate=.05,reg_lambda=3,verbosity=-1,random_state=10+h,n_jobs=-1).fit(X,ev)
 p=np.clip(c.predict_proba(Z)[:,1],.002,.998);a=ev==1
 def r(t,log=False,cap=None):
  y=tr.loc[a,t].to_numpy(float);y=np.log1p(y) if log else y
  m=LGBMRegressor(n_estimators=100,num_leaves=18,max_depth=6,min_child_samples=25,learning_rate=.05,reg_lambda=3,objective='regression_l1',verbosity=-1,random_state=20+h,n_jobs=-1).fit(X[a],y)
  v=m.predict(Z);v=np.expm1(v) if log else v;return np.clip(v,0,cap)
 g=r(tc(h,'games'),True,23*h);pt=r(tc(h,'points'),True,145*23*h);b=r(tc(h,'best_avg'),False,145)
 return pd.DataFrame({'p':p,'games':p*g,'points':p*pt,'best':p*b},index=te.index)
def naive(tr,te,h):
 a=tr.copy();b=te.copy();a['pb']=pd.cut(a.pick,[0,10,20,30,45,60,101]);b['pb']=pd.cut(b.pick,[0,10,20,30,45,60,101]);a['tb']=pd.cut(a.tenure,[-1,0,1,2,4,8,99]);b['tb']=pd.cut(b.tenure,[-1,0,1,2,4,8,99]);a['ev']=(a[tc(h,'meaningful_seasons')]>0).astype(int);G=a.groupby(['position','pb','tb'],observed=True).agg(p=('ev','mean'),games=(tc(h,'games'),'mean'),points=(tc(h,'points'),'mean'),best=(tc(h,'best_avg'),'mean')).reset_index();b=b.merge(G,on=['position','pb','tb'],how='left').set_index(te.index)
 for c,t in [('p','ev'),('games',tc(h,'games')),('points',tc(h,'points')),('best',tc(h,'best_avg'))]:b[c]=b[c].fillna(b.position.map(a.groupby('position')[t].mean())).fillna(a[t].mean())
 e=np.clip(b.total_games/(20*h),0,1);rp=np.clip(b.games_last_2/30,0,1);lv=np.where(b.weighted_avg>0,b.weighted_avg,b.last_avg);pg=np.minimum(23*h,b.games_last_2/2*h);b['p']=np.where(b.tenure==0,b.p,.55*b.p+.45*rp);b['games']=np.where(b.tenure==0,b.games,e*pg+(1-e)*b.games);b['points']=np.where(b.tenure==0,b.points,e*pg*lv+(1-e)*b.points);b['best']=np.where(b.tenure==0,b.best,e*np.maximum(lv,b.career_best)+(1-e)*b.best);return b[['p','games','points','best']].clip(lower=0)
def metrics(te,p,h):
 ev=(te[tc(h,'meaningful_seasons')]>0).astype(int);o={'n':len(te),'actual_event':ev.mean(),'pred_event':p.p.mean(),'brier':brier_score_loss(ev,p.p),'auc':roc_auc_score(ev,p.p)}
 for ac,pc in [(tc(h,'games'),'games'),(tc(h,'points'),'points'),(tc(h,'best_avg'),'best')]:o['mae_'+pc]=mean_absolute_error(te[ac],p[pc]);o['rmse_'+pc]=mean_squared_error(te[ac],p[pc])**.5
 return o
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--out',required=True);q=ap.parse_args();d=pd.read_csv(q.dataset);O=Path(q.out);O.mkdir(parents=True,exist_ok=True);rows=[];preds=[]
 # test windows have complete outcomes in data ending 2026; all training targets finish before first test origin.
 cfg={1:([2023,2024,2025],2023),3:([2021,2022,2023],2021),5:([2019,2020,2021],2019)}
 for h,(years,start) in cfg.items():
  tr=d[(d.origin_year+h<start)&(d.origin_year>=2008)].copy();te=d[d.origin_year.isin(years)].copy()
  for model in ['naive','challenger','draft_specialist']:
   p=naive(tr,te,h) if model=='naive' else fit(tr,te,h)
   if model=='draft_specialist':
    dm=tr.tenure.eq(0);dt=te.tenure.eq(0)
    if dm.sum()>200:p.loc[dt]=fit(tr[dm],te[dt],h,True).values
   r=metrics(te,p,h);r.update(horizon=h,model=model);rows.append(r)
   z=te[['key','player','origin_year','position','pick','tenure',tc(h,'games'),tc(h,'points'),tc(h,'best_avg'),tc(h,'meaningful_seasons')]].copy();z.columns=['key','player','origin_year','position','pick','tenure','actual_games','actual_points','actual_best','actual_meaningful'];z[['pred_p','pred_games','pred_points','pred_best']]=p.values;z['horizon']=h;z['model']=model;preds.append(z)
 M=pd.DataFrame(rows);P=pd.concat(preds,ignore_index=True);M.to_csv(O/'summary_metrics.csv',index=False);P.to_csv(O/'predictions.csv',index=False)
 sl=[]
 for (h,m),g in P.groupby(['horizon','model']):
  for n,z in [('all',g),('draft_time',g[g.tenure==0]),('early_0_2',g[g.tenure<=2]),('first_round',g[g.pick<=20]),('later_41plus',g[g.pick>=41])]:
   if len(z)<20:continue
   ev=(z.actual_meaningful>0).astype(int);x={'horizon':h,'model':m,'slice':n,'n':len(z),'actual_event':ev.mean(),'pred_event':z.pred_p.mean(),'brier':brier_score_loss(ev,z.pred_p),'auc':roc_auc_score(ev,z.pred_p),'mae_games':mean_absolute_error(z.actual_games,z.pred_games),'mae_points':mean_absolute_error(z.actual_points,z.pred_points),'mae_best':mean_absolute_error(z.actual_best,z.pred_best)};sl.append(x)
 pd.DataFrame(sl).to_csv(O/'slice_metrics.csv',index=False);(O/'summary.json').write_text(json.dumps({'metrics':M.to_dict('records'),'test_windows':{str(k):v[0] for k,v in cfg.items()}},indent=2));print(M.to_string(index=False))
if __name__=='__main__':main()
