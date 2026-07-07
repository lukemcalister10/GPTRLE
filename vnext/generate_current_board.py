"""Load persisted annual models, simulate coherent five-year careers and price utility."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.stats import norm
from snapshot import build_snapshot,canonical_position
from model_artifacts import predict

REPL={'MID':80.1,'DEF':78.3,'RUC':78.5,'KPD':68.4,'FWD':70.9,'KPF':66.8,'UNK':76.0}
CAPT_THRESH=107.4; CAPT_GAIN=.35; CAPT_EXP=1.25; CAPT_CAP=18.0
# Validation-selected broad career persistence. The simulator uses a common
# latent quality state plus annual noise, preserving each annual marginal.
RHO_EVENT=.50; RHO_LEVEL=.45

def posval_np(x): return 3*np.logaddexp(0,np.asarray(x)/3)
def captain_np(level):
    over=np.maximum(0,np.asarray(level)-CAPT_THRESH); cb=CAPT_GAIN*over**CAPT_EXP
    return cb*CAPT_CAP/(CAPT_CAP+cb)

def utility(avg,games,pos,lead):
    bar=REPL.get(pos,76.0)-3.0
    return (posval_np(avg-bar)+captain_np(avg))*games/(1.15**(lead-1))

def sample_binary(p,common,idio,rho):
    cut=norm.ppf(np.clip(p,1e-6,1-1e-6)); latent=np.sqrt(rho)*common+np.sqrt(1-rho)*idio
    return latent<cut

def simulate_player(g: pd.DataFrame,pos: str,sims: int,rng: np.random.Generator):
    g=g.sort_values('lead').reset_index(drop=True); n=len(g)
    quality=rng.standard_normal((sims,1)); event_idio=rng.standard_normal((sims,n)); level_idio=rng.standard_normal((sims,n))
    meaningful=np.zeros((sims,n),bool); avgs=np.zeros((sims,n)); games=np.zeros((sims,n))
    # Event persistence plus continuous conditional performance persistence.
    for j,r in g.iterrows():
        meaningful[:,j]=sample_binary(float(r.p_meaningful),quality[:,0],event_idio[:,j],RHO_EVENT)
        z=np.sqrt(RHO_LEVEL)*quality[:,0]+np.sqrt(1-RHO_LEVEL)*level_idio[:,j]
        av=np.clip(float(r.cond_avg)+float(r.avg_resid_sd)*z,0,145)
        gm=np.clip(np.rint(float(r.cond_games)+float(r.games_resid_sd)*(0.35*z+0.936*rng.standard_normal(sims))),0,23)
        avgs[:,j]=np.where(meaningful[:,j],av,0); games[:,j]=np.where(meaningful[:,j],np.maximum(gm,6),0)
    util=np.zeros((sims,n))
    for j in range(n): util[:,j]=utility(avgs[:,j],games[:,j],pos,j+1)
    total=util.sum(axis=1)
    return {
      'five_year_utility_mean':float(total.mean()),'five_year_utility_median':float(np.median(total)),
      'five_year_utility_p10':float(np.quantile(total,.10)),'five_year_utility_p90':float(np.quantile(total,.90)),
      'expected_games_5y_mc':float(games.sum(axis=1).mean()),'expected_points_5y_mc':float((avgs*games).sum(axis=1).mean()),
      'p_zero_meaningful_5y':float((meaningful.sum(axis=1)==0).mean()),
      'p_90_any_5y_mc':float(((avgs>=90)&meaningful).any(axis=1).mean()),
      'p_100_any_5y_mc':float(((avgs>=100)&meaningful).any(axis=1).mean()),
      'p_110_any_5y_mc':float(((avgs>=110)&meaningful).any(axis=1).mean()),
      'exp_90_seasons_5y_mc':float(((avgs>=90)&meaningful).sum(axis=1).mean()),
      'exp_100_seasons_5y_mc':float(((avgs>=100)&meaningful).sum(axis=1).mean()),
      'exp_110_seasons_5y_mc':float(((avgs>=110)&meaningful).sum(axis=1).mean()),
      'future_value_y1_mean':float(util[:,0].mean()),'future_value_y2_mean':float(util[:,1].mean()),
      'future_value_y1_p10':float(np.quantile(util[:,0],.10)),'future_value_y1_p90':float(np.quantile(util[:,0],.90)),
      'future_value_y2_p10':float(np.quantile(util[:,1],.10)),'future_value_y2_p90':float(np.quantile(util[:,1],.90)),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--artifacts',required=True);ap.add_argument('--out',required=True);ap.add_argument('--sims',type=int,default=1500);ap.add_argument('--seed',type=int,default=260707)
    a=ap.parse_args();O=Path(a.out);O.mkdir(parents=True,exist_ok=True);players=json.load(open(a.data));raw={};cur=[]
    for p in players:
        # Mirror the source engine's current-player eligibility as closely as the
        # flattened JSON permits. Historical/retired rows are training evidence,
        # not current board candidates.
        if p.get('_retired'): continue
        if p.get('_last_listed') is not None and int(p.get('_last_listed')) < 2026: continue
        scoring=p.get('scoring') or []
        played=any(int(r.get('games',0) or 0)>=1 for r in scoring)
        recent=bool(p.get('_has26')) or any(int(r.get('year',0) or 0)>=2024 for r in scoring) or int(p.get('year',0) or 0)>=2024
        unplayed=str(p.get('type') or '') in ('ND','RD') and int(p.get('year',0) or 0)>=2024 and sum(int(r.get('games',0) or 0) for r in scoring)==0
        if not ((played and recent) or unplayed): continue
        s=build_snapshot(p,2026)
        if s is not None: cur.append(s.to_dict());raw[s.key]=p
    te=pd.DataFrame(cur); parts=[]
    for lead in range(1,6):
        art=joblib.load(Path(a.artifacts)/f'lead_{lead}.joblib'); pr=predict(art,te)
        z=pd.concat([te[['key','player','position','pick','tenure','age']].reset_index(drop=True),pr.reset_index(drop=True)],axis=1)
        z['lead']=lead;z['forecast_year']=2026+lead;z['games_resid_sd']=art.games_resid_sd;z['avg_resid_sd']=art.avg_resid_sd;parts.append(z)
    A=pd.concat(parts,ignore_index=True);A.to_csv(O/'current_annual_forecast.csv',index=False)
    rng=np.random.default_rng(a.seed);rows=[]
    for key,g in A.groupby('key',sort=False):
        p=raw[key];pos=canonical_position(p.get('future_position') or p.get('present_position') or g.iloc[0].position)
        base={'key':key,'player':g.iloc[0].player,'position_forecast':g.iloc[0].position,'position_utility':pos,'pick':float(g.iloc[0].pick),'tenure':int(g.iloc[0].tenure),'age':float(g.iloc[0].age)}
        rows.append(base|simulate_player(g,pos,a.sims,rng))
    V=pd.DataFrame(rows).sort_values('five_year_utility_mean',ascending=False);V.insert(0,'vnext_rank',np.arange(1,len(V)+1));V.to_csv(O/'current_five_year_simulated_utility.csv',index=False)
    (O/'simulation_manifest.json').write_text(json.dumps({'sims_per_player':a.sims,'seed':a.seed,'rho_event':RHO_EVENT,'rho_level':RHO_LEVEL,'players':len(V)},indent=2))
    print(V.head(30).to_string(index=False))
if __name__=='__main__':main()
