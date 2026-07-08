from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from snapshot import build_snapshot, season_at
from task004_claude_adapter import captain_premium, soft_positive, LENS_DISCOUNT, KEY_POSITION_MULTIPLIER

POS_GROUP={"MID":"MID","RUC":"RUC","DEF":"GEN_DEF","KPD":"KEY_DEF","FWD":"GEN_FWD","KPF":"KEY_FWD","UNK":"GEN_FWD"}
NUM=["age","tenure","pick","total_games","qualifying_seasons","weighted_avg","career_best","recent_best","avg_trend","games_last_2","boundary_games","boundary_avg","boundary_points"]
CAT=["position","draft_type"]


def annual_value(avg,games,group,repl,captain,lead):
    premium=captain_premium(np.asarray(avg,float),**captain)
    raw=soft_positive(np.asarray(avg,float)+premium-np.asarray([repl[g] for g in group],float))*np.asarray(games,float)
    raw*=np.where(np.isin(group,["KEY_FWD","KEY_DEF"]),KEY_POSITION_MULTIPLIER,1.0)
    return raw/((1.0+LENS_DISCOUNT)**(np.asarray(lead,int)-1))


def build_training(players,repl,captain):
    rows=[]
    for p in players:
        try: draft=int(p.get("year"))
        except (TypeError,ValueError): continue
        for boundary in range(max(2008,draft),2021):
            snap=build_snapshot(p,boundary)
            if snap is None: continue
            observed=season_at(p,boundary); group=POS_GROUP.get(snap.position,"GEN_FWD")
            target=0.0
            for step in range(1,6):
                s=season_at(p,boundary+step)
                target+=float(annual_value([s["avg"]],[s["games"]],[group],repl,captain,[5+step])[0])
            d=snap.to_dict(); d.update({"boundary_year":boundary,"boundary_games":float(observed["games"]),"boundary_avg":float(observed["avg"]),"boundary_points":float(observed["games"]*observed["avg"]),"terminal_target":target})
            rows.append(d)
    return pd.DataFrame(rows)


def empirical_decay(frame):
    age=frame.age.to_numpy(float)
    decay=np.where(age<26,.88,np.where(age<29,.78,np.where(age<32,.62,.42)))
    return frame.boundary_raw.to_numpy(float)*np.sum(np.vstack([decay**k/((1+LENS_DISCOUNT)**k) for k in range(1,6)]),axis=0)


def make_model():
    prep=ColumnTransformer([("num",StandardScaler(),NUM),("cat",OneHotEncoder(handle_unknown="ignore"),CAT)])
    reg=HistGradientBoostingRegressor(loss="absolute_error",max_depth=4,max_iter=250,learning_rate=.05,l2_regularization=2.0,random_state=5)
    return Pipeline([("prep",prep),("reg",reg)])


def current_boundary_rows(players,forecast):
    by_key={str(p.get("key") or p.get("player")):p for p in players}; rows=[]
    for r in forecast[forecast.lead==5].itertuples(index=False):
        p=by_key.get(str(r.key)); snap=build_snapshot(p,2026) if p else None
        if snap is None: continue
        d=snap.to_dict(); d["age"]=float(d["age"]+5); d["tenure"]=int(d["tenure"]+5); d.update({"stable_player_id":r.stable_player_id,"boundary_games":float(r.exp_games),"boundary_avg":float(r.exp_avg),"boundary_points":float(r.exp_points)})
        # Re-anchor stateful level fields to the predicted year-five endpoint without inventing a rebound.
        d["last_avg"]=d["weighted_avg"]=d["recent_best"]=float(r.exp_avg); d["last_games"]=float(r.exp_games); d["games_last_2"]=float(2*r.exp_games); d["avg_trend"]=min(0.0,float(r.exp_avg)-float(d.get("prev_avg",r.exp_avg)))
        rows.append(d)
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--players",type=Path,required=True); ap.add_argument("--claude-board",type=Path,required=True); ap.add_argument("--current-forecast",type=Path,required=True); ap.add_argument("--task004-board",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    players=json.loads(a.players.read_text()); payload=json.loads(a.claude_board.read_text()); current=pd.read_csv(a.current_forecast)
    repl={str(k):float(v) for k,v in payload["REPL"].items()}; captain={"threshold":float(payload["CAPT_THRESH"]),"gain":float(payload["CAPT_GAIN"]),"exponent":float(payload["CAPT_EXP"]),"cap":float(payload["CAPT_CAP"])}
    train=build_training(players,repl,captain); groups=np.array([POS_GROUP.get(x,"GEN_FWD") for x in train.position]); train["boundary_raw"]=annual_value(train.boundary_avg,train.boundary_games,groups,repl,captain,np.full(len(train),5))
    folds=[]; scored=[]
    for year in sorted(train.boundary_year.unique()):
        tr=train[train.boundary_year<year]; te=train[train.boundary_year==year]
        if year<2014 or len(tr)<1000 or len(te)<100: continue
        model=make_model(); model.fit(tr[NUM+CAT],tr.terminal_target); mp=np.maximum(0,model.predict(te[NUM+CAT])); bp=empirical_decay(te)
        folds.append({"boundary_year":int(year),"n":len(te),"model_mae":mean_absolute_error(te.terminal_target,mp),"decay_mae":mean_absolute_error(te.terminal_target,bp),"zero_mae":mean_absolute_error(te.terminal_target,np.zeros(len(te)))})
        scored.append(te.assign(model_pred=mp,decay_pred=bp))
    fold=pd.DataFrame(folds); fold.to_csv(a.out/"rolling_origin_metrics.csv",index=False); score=pd.concat(scored,ignore_index=True)
    overall={"n":int(len(score)),"model_mae":float(mean_absolute_error(score.terminal_target,score.model_pred)),"decay_mae":float(mean_absolute_error(score.terminal_target,score.decay_pred)),"zero_mae":float(mean_absolute_error(score.terminal_target,np.zeros(len(score))))}
    overall["model_vs_decay_pct"]=100*(overall["model_mae"]-overall["decay_mae"])/overall["decay_mae"]
    old=score[score.age>=30]; overall["age30_model_mae"]=float(mean_absolute_error(old.terminal_target,old.model_pred)); overall["age30_decay_mae"]=float(mean_absolute_error(old.terminal_target,old.decay_pred))
    final=make_model(); final.fit(train[NUM+CAT],train.terminal_target)
    cur=current_boundary_rows(players,current); cg=np.array([POS_GROUP.get(x,"GEN_FWD") for x in cur.position]); cur["boundary_raw"]=annual_value(cur.boundary_avg,cur.boundary_games,cg,repl,captain,np.full(len(cur),5)); cur["terminal_model_raw"]=np.maximum(0,final.predict(cur[NUM+CAT])); cur["terminal_decay_raw"]=empirical_decay(cur)
    board=pd.read_csv(a.task004_board).merge(cur[["stable_player_id","terminal_model_raw","terminal_decay_raw"]],on="stable_player_id",validate="one_to_one")
    board["model_total_raw"]=board.task003q_raw_value+board.terminal_model_raw; board["decay_total_raw"]=board.task003q_raw_value+board.terminal_decay_raw; total=board.claude_value.sum()
    for stem in ["model","decay"]:
        board[f"{stem}_value"]=board[f"{stem}_total_raw"]*total/board[f"{stem}_total_raw"].sum(); board[f"{stem}_rank"]=board[f"{stem}_value"].rank(method="min",ascending=False).astype(int)
    board.to_csv(a.out/"current_board_terminal_comparison.csv",index=False)
    concentration={}
    for stem in ["claude","task003q","model","decay"]:
        v=board[f"{stem}_value"] if stem!="claude" else board.claude_value; rk=v.rank(method="min",ascending=False); concentration[stem]={"top100_share":float(v[rk<=100].sum()/v.sum()),"bottom_half_share":float(v[rk>len(v)/2].sum()/v.sum())}
    overall["concentration"]=concentration; old_change=(overall["age30_model_mae"]-overall["age30_decay_mae"])/overall["age30_decay_mae"]*100
    gate=overall["model_vs_decay_pct"]<=-2 and old_change<=3 and concentration["model"]["top100_share"]<.75 and concentration["model"]["bottom_half_share"]>.02
    overall["age30_model_vs_decay_pct"]=old_change; overall["status"]="pass" if gate else "fail"; overall["decision_rule"]="rolling MAE >=2% better than monotone decay, age30 not >3% worse, top100 <75%, bottom half >2%"
    (a.out/"final_report.json").write_text(json.dumps(overall,indent=2,sort_keys=True)+"\n"); print(json.dumps(overall,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
