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

POS_GROUP = {"MID":"MID","RUC":"RUC","DEF":"GEN_DEF","KPD":"KEY_DEF","FWD":"GEN_FWD","KPF":"KEY_FWD","UNK":"GEN_FWD"}
NUM = ["age","tenure","pick","total_games","qualifying_seasons","weighted_avg","career_best","recent_best","avg_trend","games_last_2","lead5_p","lead5_games","lead5_avg","lead5_points"]
CAT = ["position","draft_type"]


def annual_value(avg, games, group, repl, captain, lead):
    premium = captain_premium(np.asarray(avg, float), **captain)
    raw = soft_positive(np.asarray(avg, float) + premium - np.asarray([repl[g] for g in group], float)) * np.asarray(games, float)
    raw *= np.where(np.isin(group, ["KEY_FWD","KEY_DEF"]), KEY_POSITION_MULTIPLIER, 1.0)
    return raw / ((1.0 + LENS_DISCOUNT) ** (np.asarray(lead, int) - 1))


def build_training(players, predictions, snapshots, repl, captain):
    by_key = {str(p.get("key") or p.get("player")): p for p in players}
    p5 = predictions[predictions.lead == 5].copy()
    s = snapshots.drop_duplicates(["player_key","origin_year"]).copy()
    frame = p5.merge(s, on=["player_key","origin_year"], validate="one_to_one")
    rows=[]
    for r in frame.itertuples(index=False):
        if int(r.origin_year) > 2015 or r.player_key not in by_key: continue
        p=by_key[r.player_key]; snap=build_snapshot(p,int(r.origin_year))
        if snap is None: continue
        group=POS_GROUP.get(snap.position,"GEN_FWD")
        vals=[]
        for lead in range(6,11):
            season=season_at(p,int(r.origin_year)+lead)
            vals.append(float(annual_value([season["avg"]],[season["games"]],[group],repl,captain,[lead])[0]))
        d=snap.to_dict(); d.update({"player_key":r.player_key,"origin_year":int(r.origin_year),"lead5_p":float(r.p_meaningful),"lead5_games":float(r.exp_games),"lead5_avg":float(r.exp_avg),"lead5_points":float(r.exp_points),"terminal_target":float(sum(vals))})
        rows.append(d)
    return pd.DataFrame(rows)


def empirical_decay(frame):
    age5=frame.age.to_numpy(float)+5
    decay=np.where(age5<26,.88,np.where(age5<29,.78,np.where(age5<32,.62,.42)))
    group=np.array([POS_GROUP.get(x,"GEN_FWD") for x in frame.position])
    # lead-5 annual value continued monotonically for years 6-10
    return frame.lead5_raw.to_numpy(float) * sum(decay**k / ((1+LENS_DISCOUNT)**k) for k in range(1,6))


def make_model():
    prep=ColumnTransformer([("num",StandardScaler(),NUM),("cat",OneHotEncoder(handle_unknown="ignore"),CAT)])
    reg=HistGradientBoostingRegressor(loss="absolute_error",max_depth=4,max_iter=250,learning_rate=.05,l2_regularization=2.0,random_state=5)
    return Pipeline([("prep",prep),("reg",reg)])


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--players",type=Path,required=True); ap.add_argument("--predictions",type=Path,required=True); ap.add_argument("--snapshots",type=Path,required=True); ap.add_argument("--claude-board",type=Path,required=True); ap.add_argument("--current-forecast",type=Path,required=True); ap.add_argument("--task004-board",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    players=json.loads(a.players.read_text()); payload=json.loads(a.claude_board.read_text()); pred=pd.read_csv(a.predictions); snaps=pd.read_csv(a.snapshots)
    repl={str(k):float(v) for k,v in payload["REPL"].items()}; captain={"threshold":float(payload["CAPT_THRESH"]),"gain":float(payload["CAPT_GAIN"]),"exponent":float(payload["CAPT_EXP"]),"cap":float(payload["CAPT_CAP"])}
    train=build_training(players,pred,snaps,repl,captain)
    groups=np.array([POS_GROUP.get(x,"GEN_FWD") for x in train.position]); train["lead5_raw"]=annual_value(train.lead5_avg,train.lead5_games,groups,repl,captain,np.full(len(train),5))
    folds=[]; scored=[]
    for year in sorted(train.origin_year.unique()):
        tr=train[train.origin_year<year]; te=train[train.origin_year==year]
        if len(tr)<500 or len(te)<50: continue
        model=make_model(); model.fit(tr[NUM+CAT],tr.terminal_target); mp=np.maximum(0,model.predict(te[NUM+CAT])); bp=empirical_decay(te); zp=np.zeros(len(te))
        folds.append({"origin_year":int(year),"n":len(te),"model_mae":mean_absolute_error(te.terminal_target,mp),"decay_mae":mean_absolute_error(te.terminal_target,bp),"zero_mae":mean_absolute_error(te.terminal_target,zp)})
        scored.append(te.assign(model_pred=mp,decay_pred=bp))
    fold=pd.DataFrame(folds); fold.to_csv(a.out/"rolling_origin_metrics.csv",index=False); score=pd.concat(scored,ignore_index=True)
    overall={"n":int(len(score)),"model_mae":float(mean_absolute_error(score.terminal_target,score.model_pred)),"decay_mae":float(mean_absolute_error(score.terminal_target,score.decay_pred)),"zero_mae":float(mean_absolute_error(score.terminal_target,np.zeros(len(score))))}
    overall["model_vs_decay_pct"]=100*(overall["model_mae"]-overall["decay_mae"])/overall["decay_mae"]
    old=score[score.age>=25] # age 30+ at terminal boundary
    overall["terminal_age30_model_mae"]=float(mean_absolute_error(old.terminal_target,old.model_pred)) if len(old) else None
    overall["terminal_age30_decay_mae"]=float(mean_absolute_error(old.terminal_target,old.decay_pred)) if len(old) else None

    final=make_model(); final.fit(train[NUM+CAT],train.terminal_target)
    current=pd.read_csv(a.current_forecast); p5=current[current.lead==5].copy(); currows=[]
    by_key={str(p.get("key") or p.get("player")):p for p in players}
    for r in p5.itertuples(index=False):
        p=by_key.get(str(r.key)); snap=build_snapshot(p,2026) if p else None
        if snap is None: continue
        d=snap.to_dict(); d.update({"stable_player_id":r.stable_player_id,"lead5_p":r.p_meaningful,"lead5_games":r.exp_games,"lead5_avg":r.exp_avg,"lead5_points":r.exp_points}); currows.append(d)
    cur=pd.DataFrame(currows); cg=np.array([POS_GROUP.get(x,"GEN_FWD") for x in cur.position]); cur["lead5_raw"]=annual_value(cur.lead5_avg,cur.lead5_games,cg,repl,captain,np.full(len(cur),5)); cur["terminal_model_raw"]=np.maximum(0,final.predict(cur[NUM+CAT])); cur["terminal_decay_raw"]=empirical_decay(cur)
    b=pd.read_csv(a.task004_board); board=b.merge(cur[["stable_player_id","terminal_model_raw","terminal_decay_raw"]],on="stable_player_id",validate="one_to_one")
    board["model_total_raw"]=board.task003q_raw_value+board.terminal_model_raw; board["decay_total_raw"]=board.task003q_raw_value+board.terminal_decay_raw
    total=board.claude_value.sum()
    for stem in ["model","decay"]:
        board[f"{stem}_value"]=board[f"{stem}_total_raw"]*total/board[f"{stem}_total_raw"].sum(); board[f"{stem}_rank"]=board[f"{stem}_value"].rank(method="min",ascending=False).astype(int)
    board.to_csv(a.out/"current_board_terminal_comparison.csv",index=False)
    concentration={}
    for stem in ["claude","task003q","model","decay"]:
        v=board[f"{stem}_value"] if stem!="claude" else board.claude_value; rk=v.rank(method="min",ascending=False); concentration[stem]={"top100_share":float(v[rk<=100].sum()/v.sum()),"bottom_half_share":float(v[rk>len(v)/2].sum()/v.sum())}
    overall["concentration"]=concentration
    gate=overall["model_vs_decay_pct"]<=-2 and concentration["model"]["top100_share"]<.75 and concentration["model"]["bottom_half_share"]>.02
    overall["status"]="pass" if gate else "fail"; overall["decision_rule"]="model MAE at least 2% better than empirical monotone decay; top-100 share below 75%; bottom-half share above 2%"
    (a.out/"final_report.json").write_text(json.dumps(overall,indent=2,sort_keys=True)+"\n"); print(json.dumps(overall,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
