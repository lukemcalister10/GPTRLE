"""Fit annual models on all fully observed history and project 2027-2031 player trajectories."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from evaluate_v3_trajectory import fit_lead,THRESH
REPL={'MID':80.1,'DEF':78.3,'FWD':70.9,'RUC':78.5,'KPD':68.4,'KPF':66.8,'UNK':75.0}
CAPT_THRESH=107.4;CAPT_GAIN=.35;CAPT_EXP=1.25;CAPT_CAP=18.0

def season_utility(avg,games,pos,lead):
 b=np.array([REPL.get(str(x),75.0)-3 for x in pos]);x=np.asarray(avg)-b;sur=3*np.logaddexp(0,x/3);over=np.maximum(0,np.asarray(avg)-CAPT_THRESH);cb=CAPT_GAIN*over**CAPT_EXP;capt=cb*CAPT_CAP/(CAPT_CAP+cb);return (sur+capt)*np.asarray(games)/(1.15**(lead-1))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();d=pd.read_csv(a.dataset);test=d[d.origin_year==2026].copy();parts=[]
 for lead in range(1,6):
  train=d[(d.origin_year+lead<=2026)&(d.origin_year>=2008)].copy();p=fit_lead(train,test,lead,'linear');z=test[['key','player','position','pick','tenure','age','weighted_avg','career_best']].copy();z['forecast_year']=2026+lead;z['lead']=lead
  for c in p.columns:z[c]=p[c].to_numpy()
  z['expected_utility']=season_utility(z.cond_avg,z.exp_games,z.position,lead);parts.append(z)
 out=pd.concat(parts,ignore_index=True);agg=out.groupby(['key','player','position','pick','tenure','age'],as_index=False).agg(expected_utility_5y=('expected_utility','sum'),expected_games_5y=('exp_games','sum'),expected_points_5y=('exp_points','sum'),max_elite_probability=('p110','max'))
 out.to_csv(Path(a.out)/'current_annual_forecasts.csv',index=False);agg.sort_values('expected_utility_5y',ascending=False).to_csv(Path(a.out)/'current_5y_summary.csv',index=False)
 print(agg.sort_values('expected_utility_5y',ascending=False).head(20).to_string(index=False))
if __name__=='__main__':main()
