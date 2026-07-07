"""Fast annual trajectory benchmark: calibrated hurdle + direct elite thresholds."""
from __future__ import annotations
import argparse,json,warnings
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler,PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.metrics import brier_score_loss,roc_auc_score,mean_absolute_error
from sklearn.isotonic import IsotonicRegression
warnings.filterwarnings('ignore')
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']
CAT=['position','draft_type'];TH=(80,90,100,110,120)
def pre():return ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore'))]),CAT)])
def auc(y,p):return roc_auc_score(y,p) if len(np.unique(y))>1 else np.nan
def calibrate(a,y,z):
 if len(np.unique(y))<2:return np.repeat(np.mean(y),len(z))
 return np.clip(IsotonicRegression(out_of_bounds='clip').fit(a,y).predict(z),.001,.999)
def fit(train,test,l):
 years=sorted(train.origin_year.unique());cut=years[max(1,int(len(years)*.8))-1];fit=train[train.origin_year<cut];cal=train[train.origin_year>=cut]
 if len(cal)<100: cal=train[train.origin_year==years[-1]];fit=train[train.origin_year<years[-1]]
 P=pre();X=P.fit_transform(fit);C=P.transform(cal);Z=P.transform(test)
 y=fit[f'l{l}_meaningful'].astype(int).to_numpy();yc=cal[f'l{l}_meaningful'].astype(int).to_numpy()
 c=LogisticRegression(C=.35,max_iter=500).fit(X,y);p=calibrate(c.predict_proba(C)[:,1],yc,c.predict_proba(Z)[:,1]);active=y==1
 def reg(target,cap,log=False):
  yy=fit.loc[active,target].to_numpy(float);yy=np.log1p(yy) if log else yy;m=Ridge(alpha=12).fit(X[active],yy);v=m.predict(Z);v=np.expm1(v) if log else v;return np.clip(v,0,cap)
 cg=reg(f'l{l}_games',23);ca=reg(f'l{l}_avg',145)
 o=pd.DataFrame({'p_meaningful':p,'cond_games':cg,'cond_avg':ca,'exp_games':p*cg,'exp_avg':p*ca,'exp_points':p*cg*ca},index=test.index)
 for t in TH:
  y=fit[f'l{l}_{t}'].astype(int).to_numpy();yc=cal[f'l{l}_{t}'].astype(int).to_numpy()
  if y.sum()<15:o[f'p{t}']=np.mean(y);continue
  m=LogisticRegression(C=.3,max_iter=500).fit(X,y);o[f'p{t}']=calibrate(m.predict_proba(C)[:,1],yc,m.predict_proba(Z)[:,1])
 arr=o[[f'p{t}' for t in TH]].to_numpy();o[[f'p{t}' for t in TH]]=np.minimum.accumulate(arr,axis=1)
 return o
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();d=pd.read_csv(a.dataset);O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
 rows=[];pred=[]
 for l in range(1,6):
  tr=d[(d.origin_year+l<2019)&(d.origin_year>=2008)].copy();te=d[d.origin_year.isin([2019,2020,2021])].copy();p=fit(tr,te,l);y=te[f'l{l}_meaningful'].astype(int)
  r={'lead':l,'n':len(te),'actual_event':y.mean(),'pred_event':p.p_meaningful.mean(),'brier_event':brier_score_loss(y,p.p_meaningful),'auc_event':auc(y,p.p_meaningful),'mae_games':mean_absolute_error(te[f'l{l}_games'],p.exp_games),'mae_avg':mean_absolute_error(te[f'l{l}_avg'],p.exp_avg),'mae_points':mean_absolute_error(te[f'l{l}_points'],p.exp_points)}
  for t in TH:r[f'brier_{t}']=brier_score_loss(te[f'l{l}_{t}'],p[f'p{t}']);r[f'auc_{t}']=auc(te[f'l{l}_{t}'],p[f'p{t}'])
  rows.append(r);z=te[['key','player','origin_year','position','pick','tenure',f'l{l}_games',f'l{l}_avg',f'l{l}_points',f'l{l}_meaningful']+[f'l{l}_{t}' for t in TH]].copy();z.columns=['key','player','origin_year','position','pick','tenure','actual_games','actual_avg','actual_points','actual_meaningful']+[f'actual_{t}' for t in TH];z=pd.concat([z.reset_index(drop=True),p.reset_index(drop=True)],axis=1);z['lead']=l;pred.append(z)
 M=pd.DataFrame(rows);P=pd.concat(pred,ignore_index=True);M.to_csv(O/'summary_metrics.csv',index=False);P.to_csv(O/'predictions.csv',index=False)
 rel=[]
 for l,g in P.groupby('lead'):
  for target,ac,pc in [('meaningful','actual_meaningful','p_meaningful')]+[(str(t),f'actual_{t}',f'p{t}') for t in TH]:
   g=g.copy();g['bin']=pd.qcut(g[pc],10,duplicates='drop')
   for _,q in g.groupby('bin',observed=True):rel.append({'lead':l,'target':target,'n':len(q),'pred':q[pc].mean(),'actual':q[ac].mean()})
 pd.DataFrame(rel).to_csv(O/'reliability.csv',index=False)
 w=P.pivot_table(index=['key','origin_year'],columns='lead',values=['actual_points','exp_points']);res=pd.DataFrame({l:w[('actual_points',l)]-w[('exp_points',l)] for l in range(1,6)});res.corr().to_csv(O/'point_residual_correlation.csv')
 # Multi-season elite outcomes from annual probabilities and realised results.
 multi=[]
 for (k,o),g in P.groupby(['key','origin_year']):
  if len(g)!=5:continue
  rr={'key':k,'origin_year':o}
  for t in (90,100,110):
   probs=g.sort_values('lead')[f'p{t}'].to_numpy();acts=g.sort_values('lead')[f'actual_{t}'].to_numpy()
   # independence approximation, documented; later replaced by copula simulation.
   rr[f'p_any_{t}']=1-np.prod(1-probs);rr[f'actual_any_{t}']=int(acts.max()>0);rr[f'exp_seasons_{t}']=probs.sum();rr[f'actual_seasons_{t}']=acts.sum()
  multi.append(rr)
 MU=pd.DataFrame(multi);MU.to_csv(O/'multi_season_elite.csv',index=False);ms=[]
 for t in (90,100,110):ms.append({'threshold':t,'n':len(MU),'actual_any':MU[f'actual_any_{t}'].mean(),'pred_any':MU[f'p_any_{t}'].mean(),'brier_any':brier_score_loss(MU[f'actual_any_{t}'],MU[f'p_any_{t}']),'mae_seasons':mean_absolute_error(MU[f'actual_seasons_{t}'],MU[f'exp_seasons_{t}'])})
 pd.DataFrame(ms).to_csv(O/'multi_season_metrics.csv',index=False);(O/'summary.json').write_text(json.dumps({'annual':rows,'multi':ms},indent=2));print(M.to_string(index=False));print(pd.DataFrame(ms).to_string(index=False))
if __name__=='__main__':main()
