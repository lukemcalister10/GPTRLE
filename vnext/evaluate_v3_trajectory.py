"""Leakage-safe annual trajectory challenger with calibrated event/threshold probabilities."""
from __future__ import annotations
import argparse,json,warnings
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.metrics import brier_score_loss,roc_auc_score,mean_absolute_error
from sklearn.isotonic import IsotonicRegression
warnings.filterwarnings('ignore')
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']
CAT=['position','draft_type']
THRESH=(80,90,100,110,120)

def prep():
 return ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)],sparse_threshold=0)

def safe_auc(y,p):
 return roc_auc_score(y,p) if len(np.unique(y))>1 else np.nan

def temporal_calibrate(raw,y,raw_test):
 if len(np.unique(y))<2:return np.repeat(float(np.mean(y)),len(raw_test))
 iso=IsotonicRegression(out_of_bounds='clip').fit(raw,y)
 return np.clip(iso.predict(raw_test),.001,.999)

def fit_lead(train,test,lead,kind='nonlinear'):
 # Internal temporal split for honest post-hoc calibration.
 cut=int(train.origin_year.quantile(.8));fit=train[train.origin_year<cut];cal=train[train.origin_year>=cut]
 if len(fit)<500 or len(cal)<150:fit=train;cal=train.sample(min(1000,len(train)),random_state=lead)
 P=prep();X=P.fit_transform(fit);C=P.transform(cal);Z=P.transform(test)
 y=fit[f'l{lead}_meaningful'].astype(int).to_numpy();yc=cal[f'l{lead}_meaningful'].astype(int).to_numpy()
 if kind=='linear': clf=LogisticRegression(C=.35,max_iter=600)
 else: clf=HistGradientBoostingClassifier(max_iter=120,learning_rate=.055,max_leaf_nodes=15,l2_regularization=2.5,min_samples_leaf=35,random_state=lead)
 clf.fit(X,y);p=temporal_calibrate(clf.predict_proba(C)[:,1],yc,clf.predict_proba(Z)[:,1])
 active=y==1
 def reg(target,cap,log=False):
  yy=fit.loc[active,target].to_numpy(float);yy=np.log1p(yy) if log else yy
  if kind=='linear':m=Ridge(alpha=14)
  else:m=HistGradientBoostingRegressor(loss='absolute_error',max_iter=120,learning_rate=.055,max_leaf_nodes=15,l2_regularization=3,min_samples_leaf=30,random_state=lead+7)
  m.fit(X[active],yy);v=m.predict(Z);v=np.expm1(v) if log else v;return np.clip(v,0,cap)
 cg=reg(f'l{lead}_games',23,False);ca=reg(f'l{lead}_avg',145,False)
 out=pd.DataFrame({'p_meaningful':p,'cond_games':cg,'cond_avg':ca,'exp_games':p*cg,'exp_avg':p*ca,'exp_points':p*cg*ca},index=test.index)
 # Direct unconditional calibrated threshold probabilities.
 for t in THRESH:
  yt=fit[f'l{lead}_{t}'].astype(int).to_numpy();yct=cal[f'l{lead}_{t}'].astype(int).to_numpy()
  if yt.sum()<20:
   out[f'p{t}']=float(np.mean(yt));continue
  if kind=='linear':m=LogisticRegression(C=.3,max_iter=600,class_weight=None)
  else:m=HistGradientBoostingClassifier(max_iter=120,learning_rate=.05,max_leaf_nodes=12,l2_regularization=3,min_samples_leaf=40,random_state=lead+t)
  m.fit(X,yt);out[f'p{t}']=temporal_calibrate(m.predict_proba(C)[:,1],yct,m.predict_proba(Z)[:,1])
 # Enforce nested thresholds defensively.
 arr=out[[f'p{t}' for t in THRESH]].to_numpy();arr=np.minimum.accumulate(arr,axis=1)
 out[[f'p{t}' for t in THRESH]]=arr
 return out

def score(test,p,lead,model):
 y=test[f'l{lead}_meaningful'].astype(int);r={'lead':lead,'model':model,'n':len(test),'event_rate':y.mean(),'pred_event':p.p_meaningful.mean(),'brier_event':brier_score_loss(y,p.p_meaningful),'auc_event':safe_auc(y,p.p_meaningful),'mae_games':mean_absolute_error(test[f'l{lead}_games'],p.exp_games),'mae_avg_uncond':mean_absolute_error(test[f'l{lead}_avg'],p.exp_avg),'mae_points':mean_absolute_error(test[f'l{lead}_points'],p.exp_points)}
 for t in THRESH:
  yy=test[f'l{lead}_{t}'].astype(int);r[f'brier_{t}']=brier_score_loss(yy,p[f'p{t}']);r[f'auc_{t}']=safe_auc(yy,p[f'p{t}'])
 return r

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 d=pd.read_csv(a.dataset);O=Path(a.out);O.mkdir(parents=True,exist_ok=True);metrics=[];preds=[]
 # Rolling origins; every training target predates its test origin.
 for lead in range(1,6):
  for origin in (2020,2021):
   tr=d[(d.origin_year+lead<origin)&(d.origin_year>=2008)].copy();te=d[d.origin_year==origin].copy()
   for model in ('linear',):
    p=fit_lead(tr,te,lead,model);metrics.append(score(te,p,lead,model)|{'test_origin':origin})
    z=te[['key','player','origin_year','position','pick','tenure',f'l{lead}_games',f'l{lead}_avg',f'l{lead}_points',f'l{lead}_meaningful']+[f'l{lead}_{t}' for t in THRESH]].copy()
    z.columns=['key','player','origin_year','position','pick','tenure','actual_games','actual_avg','actual_points','actual_meaningful']+[f'actual_{t}' for t in THRESH]
    z=pd.concat([z.reset_index(drop=True),p.reset_index(drop=True)],axis=1);z['lead']=lead;z['model']=model;preds.append(z)
 M=pd.DataFrame(metrics);PRED=pd.concat(preds,ignore_index=True);M.to_csv(O/'rolling_metrics.csv',index=False);PRED.to_csv(O/'predictions.csv',index=False)
 S=M.groupby(['lead','model'],as_index=False).agg({c:'mean' for c in M.columns if c not in ['lead','model','test_origin']});S.to_csv(O/'summary_metrics.csv',index=False)
 # Calibration tables and residual correlation for annual trajectory simulation.
 rel=[]
 for (lead,model),g in PRED.groupby(['lead','model']):
  for name,actual,pcol in [('meaningful','actual_meaningful','p_meaningful')]+[(str(t),f'actual_{t}',f'p{t}') for t in THRESH]:
   try:g['bin']=pd.qcut(g[pcol],10,duplicates='drop')
   except ValueError:continue
   for _,q in g.groupby('bin',observed=True):rel.append({'lead':lead,'model':model,'target':name,'n':len(q),'pred':q[pcol].mean(),'actual':q[actual].mean()})
 pd.DataFrame(rel).to_csv(O/'reliability.csv',index=False)
 # Compare lead-year point residuals by player/origin where all leads exist.
 n=PRED[PRED.model=='linear'];wide=n.pivot_table(index=['key','origin_year'],columns='lead',values=['actual_points','exp_points'])
 R=pd.DataFrame({l:wide[('actual_points',l)]-wide[('exp_points',l)] for l in range(1,6)}).corr();R.to_csv(O/'point_residual_correlation.csv')
 (O/'summary.json').write_text(json.dumps({'rows':len(PRED),'metrics':S.to_dict('records')},indent=2));print(S.to_string(index=False))
if __name__=='__main__':main()
