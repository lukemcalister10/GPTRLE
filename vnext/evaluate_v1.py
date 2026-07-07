"""Rolling-origin baseline and vNext hurdle challenger evaluation."""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, brier_score_loss, roc_auc_score
warnings.filterwarnings('ignore')

CAT=['position','draft_type']
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']

def make_preprocess(scale=False):
    num_steps=[('impute',SimpleImputer(strategy='median'))]
    if scale:num_steps.append(('scale',StandardScaler()))
    return ColumnTransformer([
        ('num',Pipeline(num_steps),NUM),
        ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),CAT),
    ])

def naive_predictions(train,test):
    # Honest low-complexity baseline: recent demonstrated level if available;
    # otherwise historical draft-pick/position/tenure means from training only.
    tr=train.copy(); te=test.copy()
    bins=[0,10,20,30,45,60,101]
    tr['pick_bin']=pd.cut(tr.pick,bins,right=True,include_lowest=True)
    te['pick_bin']=pd.cut(te.pick,bins,right=True,include_lowest=True)
    tr['tenure_bin']=pd.cut(tr.tenure,[-1,0,1,2,4,8,99])
    te['tenure_bin']=pd.cut(te.tenure,[-1,0,1,2,4,8,99])
    grp=tr.groupby(['position','pick_bin','tenure_bin'],observed=True).agg(p=('next_meaningful','mean'),avg=('next_avg','mean')).reset_index()
    te=te.merge(grp,on=['position','pick_bin','tenure_bin'],how='left')
    gp=tr.groupby('position').next_meaningful.mean(); ga=tr.groupby('position').next_avg.mean()
    te['p']=te.p.fillna(te.position.map(gp)).fillna(tr.next_meaningful.mean()).clip(.001,.999)
    te['avg']=te.avg.fillna(te.position.map(ga)).fillna(tr.next_avg.mean())
    evidence=np.clip(te.last_games/18,0,1)
    demonstrated=np.where(te.last_games>=6,te.last_avg,te.weighted_avg)
    te['pred_avg']=evidence*demonstrated+(1-evidence)*te['avg']
    # Persistence probability informed by recent games without future status fields.
    recent_p=np.clip(te.games_last_2/30,0,1)
    te['pred_p']=np.clip(.55*te.p+.45*recent_p,.001,.999)
    te['pred_uncond']=te.pred_p*te.pred_avg
    return te[['pred_p','pred_avg','pred_uncond']].to_numpy()

def fit_challenger(train,test):
    all_pos=['MID','DEF','FWD','RUC','KPD','KPF','UNK']
    all_type=sorted(set(train.draft_type.astype(str)) | set(test.draft_type.astype(str)))
    pos_map={v:i for i,v in enumerate(all_pos)}; type_map={v:i for i,v in enumerate(all_type)}
    def matrix(d):
        x=d[NUM].copy()
        x['position_code']=d.position.map(pos_map).fillna(pos_map['UNK'])
        x['draft_type_code']=d.draft_type.astype(str).map(type_map).fillna(-1)
        return x.replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    Xtr=matrix(train); Xte=matrix(test)
    clf=ExtraTreesClassifier(n_estimators=80,max_depth=12,min_samples_leaf=12,max_features=.8,class_weight=None,random_state=7,n_jobs=1)
    clf.fit(Xtr,train.next_meaningful.to_numpy())
    p=np.clip(clf.predict_proba(Xte)[:,1],.001,.999)
    cond=train.next_meaningful.to_numpy()==1
    reg=ExtraTreesRegressor(n_estimators=80,max_depth=14,min_samples_leaf=8,max_features=.8,random_state=7,n_jobs=1)
    reg.fit(Xtr[cond],train.next_avg.to_numpy()[cond])
    avg=np.clip(reg.predict(Xte),20,145)
    return np.c_[p,avg,p*avg]

def metrics(y,p,avg,uncond):
    meaningful=y.next_meaningful.to_numpy()
    actual_uncond=np.where(meaningful==1,y.next_avg.to_numpy(),0.0)
    out={
        'n':len(y),
        'meaningful_rate':float(meaningful.mean()),
        'brier_meaningful':float(brier_score_loss(meaningful,p)),
        'mae_unconditional_avg':float(mean_absolute_error(actual_uncond,uncond)),
        'rmse_unconditional_avg':float(mean_squared_error(actual_uncond,uncond)**.5),
    }
    try: out['auc_meaningful']=float(roc_auc_score(meaningful,p))
    except ValueError: out['auc_meaningful']=None
    mask=meaningful==1
    out['mae_avg_if_meaningful']=float(mean_absolute_error(y.next_avg.to_numpy()[mask],avg[mask])) if mask.any() else None
    for t in (90,100,110):
        actual=y[f'next_{t}'].to_numpy()
        # Approximate threshold probability from conditional mean with a fixed residual scale.
        z=(avg-t)/12.0
        condprob=1/(1+np.exp(-1.7*z))
        prob=p*condprob
        out[f'brier_{t}']=float(brier_score_loss(actual,prob))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    df=pd.read_csv(a.dataset)
    results=[]; preds=[]
    # Evaluation years chosen for adequate prior data and full observed next year.
    for origin in range(2018,2026):
        train=df[(df.target_year < origin) & (df.origin_year>=2008)].copy()
        test=df[df.origin_year==origin].copy()
        if len(train)<500 or len(test)<20: continue
        for name,arr in [('naive',naive_predictions(train,test)),('vnext_tree_hurdle',fit_challenger(train,test))]:
            m=metrics(test,arr[:,0],arr[:,1],arr[:,2]); m.update({'origin':origin,'model':name}); results.append(m)
            pp=test[['key','player','origin_year','position','pick','tenure','next_meaningful','next_avg','next_games']].copy()
            pp['model']=name; pp['pred_p_meaningful']=arr[:,0]; pp['pred_avg_if_meaningful']=arr[:,1]; pp['pred_unconditional_avg']=arr[:,2]; preds.append(pp)
    r=pd.DataFrame(results); pr=pd.concat(preds,ignore_index=True)
    summary=r.groupby('model').agg({c:'mean' for c in ['brier_meaningful','auc_meaningful','mae_unconditional_avg','rmse_unconditional_avg','mae_avg_if_meaningful','brier_90','brier_100','brier_110']}).reset_index()
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    r.to_csv(out/'rolling_metrics.csv',index=False); summary.to_csv(out/'summary_metrics.csv',index=False); pr.to_csv(out/'predictions.csv',index=False)
    payload={'summary':summary.to_dict(orient='records'),'origins':sorted(r.origin.unique().tolist()),'rows_evaluated':int(pr[pr.model=='naive'].shape[0])}
    (out/'summary.json').write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))
if __name__=='__main__': main()
