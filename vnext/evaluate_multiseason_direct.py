"""Direct five-year elite-event calibration, used to correct independence overstatement."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss,roc_auc_score
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed'];CAT=['position','draft_type']
def prep():return ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore'))]),CAT)])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--annual-pred',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();d=pd.read_csv(a.dataset);A=pd.read_csv(a.annual_pred);O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
 tr=d[(d.origin_year+5<2019)&(d.origin_year>=2008)].copy();te=d[d.origin_year.isin([2019,2020,2021])].copy();years=sorted(tr.origin_year.unique());cut=years[max(1,int(len(years)*.8))-1];fit=tr[tr.origin_year<cut];cal=tr[tr.origin_year>=cut];P=prep();X=P.fit_transform(fit);C=P.transform(cal);Z=P.transform(te);rows=[];out=te[['key','origin_year']].copy()
 for t in (90,100,110):
  cols=[f'l{l}_{t}' for l in range(1,6)];y=(fit[cols].max(axis=1)>0).astype(int).to_numpy();yc=(cal[cols].max(axis=1)>0).astype(int).to_numpy();yt=(te[cols].max(axis=1)>0).astype(int).to_numpy();m=LogisticRegression(C=.3,max_iter=500).fit(X,y);rc=m.predict_proba(C)[:,1];rz=m.predict_proba(Z)[:,1];iso=IsotonicRegression(out_of_bounds='clip').fit(rc,yc);p=np.clip(iso.predict(rz),.001,.999);out[f'actual_any_{t}']=yt;out[f'p_direct_any_{t}']=p
  annual=A.pivot_table(index=['key','origin_year'],columns='lead',values=f'p{t}');ind=(1-(1-annual).prod(axis=1)).reindex(pd.MultiIndex.from_frame(te[['key','origin_year']])).to_numpy();
  rows.append({'threshold':t,'n':len(te),'actual_rate':yt.mean(),'direct_pred':p.mean(),'direct_brier':brier_score_loss(yt,p),'direct_auc':roc_auc_score(yt,p),'independence_pred':np.nanmean(ind),'independence_brier':brier_score_loss(yt,np.nan_to_num(ind,nan=np.nanmean(ind)))})
 out.to_csv(O/'direct_predictions.csv',index=False);pd.DataFrame(rows).to_csv(O/'comparison.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
