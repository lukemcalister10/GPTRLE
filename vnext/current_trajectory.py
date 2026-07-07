"""Fit annual lead models on fully observed history and forecast 2027-31 current trajectories.
Produces a five-year outcome/utility prototype; it does not replace live RL values.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np,pandas as pd
from build_annual_dataset import build_rows
from snapshot import build_snapshot,canonical_position
from evaluate_v3_fast import fit
REPL={'MID':80.1,'DEF':78.3,'RUC':78.5,'KPD':68.4,'FWD':70.9,'KPF':66.8,'UNK':76.0}
CAPT_THRESH=107.4;CAPT_GAIN=.35;CAPT_EXP=1.25;CAPT_CAP=18.0

def posval(x):return 3.0*math.log1p(math.exp(min(x/3.0,40.0)))
def capt(lev):
 over=max(0.,lev-CAPT_THRESH)
 if over<=0:return 0.
 cb=CAPT_GAIN*over**CAPT_EXP
 return cb*CAPT_CAP/(CAPT_CAP+cb)
def scenario_probs(r):
 # Coherent discrete approximation from calibrated exceedance probabilities.
 p0=max(0.,1-r.p_meaningful);p80=max(0.,r.p_meaningful-r.p80);p90=max(0.,r.p80-r.p90);p100=max(0.,r.p90-r.p100);p110=max(0.,r.p100-r.p110);p120=max(0.,r.p110-r.p120);pt=max(0.,r.p120)
 ps=np.array([p0,p80,p90,p100,p110,p120,pt]);ps=ps/ps.sum() if ps.sum() else np.array([1,0,0,0,0,0,0]);return ps,np.array([0,72,85,95,105,115,125],float)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--annual',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
 players=json.load(open(a.data));d=pd.read_csv(a.annual);cur=[];raw={}
 for p in players:
  s=build_snapshot(p,2026)
  if s is not None:cur.append(s.to_dict());raw[s.key]=p
 te=pd.DataFrame(cur);outs=[]
 for l in range(1,6):
  # 2026 is partial, so only targets ending by 2025 are used for training.
  tr=d[(d.origin_year+l<=2025)&(d.origin_year>=2008)].copy();pr=fit(tr,te,l);z=pd.concat([te[['key','player','position','pick','tenure','age']].reset_index(drop=True),pr.reset_index(drop=True)],axis=1);z['lead']=l;z['forecast_year']=2026+l;outs.append(z)
 A=pd.concat(outs,ignore_index=True);A.to_csv(O/'current_annual_forecast.csv',index=False)
 vals=[]
 for key,g in A.groupby('key'):
  g=g.sort_values('lead');rr=raw.get(key,{});livepos=canonical_position(rr.get('future_position') or rr.get('present_position') or g.iloc[0].position);bar=REPL.get(livepos,76.)-3.;total=0.;annual=[]
  for _,r in g.iterrows():
   ps,levels=scenario_probs(r);ug=sum(float(p)*posval(float(l)+capt(float(l))-bar) for p,l in zip(ps,levels));avail=min(23.,max(0.,float(r.cond_games)))
   rawu=ug*avail/(1.15**(int(r.lead)-1));total+=rawu;annual.append(rawu)
  vals.append({'key':key,'player':g.iloc[0].player,'position_forecast':g.iloc[0].position,'position_utility':livepos,'five_year_raw_utility':total,'utility_y1':annual[0],'utility_y2':annual[1],'utility_y3':annual[2],'utility_y4':annual[3],'utility_y5':annual[4],'p_90_any_5y':1-np.prod(1-g.p90.to_numpy()),'p_100_any_5y':1-np.prod(1-g.p100.to_numpy()),'p_110_any_5y':1-np.prod(1-g.p110.to_numpy()),'expected_meaningful_seasons_5y':g.p_meaningful.sum(),'expected_games_5y':g.exp_games.sum(),'expected_points_5y':g.exp_points.sum()})
 V=pd.DataFrame(vals).sort_values('five_year_raw_utility',ascending=False);V.to_csv(O/'current_five_year_utility.csv',index=False)
 (O/'README.txt').write_text('Prototype five-year outcome and utility outputs. Utility uses calibrated threshold scenarios, live positional replacement less 3, captaincy premium, availability and 15% discounting. It is raw utility, not live RL currency, and excludes years 6+ and policy floors/caps.\n')
 print(V.head(25).to_string(index=False))
if __name__=='__main__':main()
