"""Rolling-origin multi-horizon trajectory challenger.

Builds honest 1/3/5-year models.  Draft-time rows use a dedicated model and
all rows are evaluated only where the complete target horizon is observable.
"""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import brier_score_loss, roc_auc_score, mean_absolute_error, mean_squared_error
from sklearn.isotonic import IsotonicRegression
warnings.filterwarnings('ignore')

CAT=['position','draft_type']
NUM=['pick','tenure','age','total_games','qualifying_seasons','last_avg','last_games','prev_avg','prev_games','weighted_avg','career_best','recent_best','avg_trend','games_last_2','seasons_observed']
DRAFT_NUM=['pick','age']
POSITIONS=['MID','DEF','FWD','RUC','KPD','KPF','UNK']


def make_matrix(train: pd.DataFrame, test: pd.DataFrame, draft_only=False):
    nums=DRAFT_NUM if draft_only else NUM
    types=sorted(set(train.draft_type.astype(str)) | set(test.draft_type.astype(str)))
    pmap={v:i for i,v in enumerate(POSITIONS)}; tmap={v:i for i,v in enumerate(types)}
    def m(d):
        x=d[nums].copy()
        x['position_code']=d.position.map(pmap).fillna(pmap['UNK'])
        x['draft_type_code']=d.draft_type.astype(str).map(tmap).fillna(-1)
        return x.replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    return m(train),m(test)


def calibrate_prob(y_train, raw_train, raw_test):
    # Isotonic only when enough support; otherwise keep raw probabilities.
    y=np.asarray(y_train,int); rt=np.asarray(raw_train,float); rs=np.asarray(raw_test,float)
    if len(y)<300 or y.sum()<40 or (len(y)-y.sum())<40:
        return np.clip(rs,.001,.999)
    iso=IsotonicRegression(out_of_bounds='clip')
    iso.fit(rt,y)
    return np.clip(iso.predict(rs),.001,.999)


def tcol(horizon, suffix):
    if horizon == 1:
        return {'meaningful_seasons':'next_meaningful','games':'next_games','points':'next_points','best_avg':'next_avg'}[suffix]
    return f'h{horizon}_{suffix}'

def fit_hurdle(train,test,horizon,draft_only=False):
    Xtr,Xte=make_matrix(train,test,draft_only)
    # Event: at least one meaningful season within horizon.
    y=(train[tcol(horizon,'meaningful_seasons')]>0).astype(int).to_numpy()
    clf=ExtraTreesClassifier(n_estimators=60,max_depth=13,min_samples_leaf=14,max_features=.85,class_weight='balanced_subsample',random_state=31+horizon,n_jobs=-1)
    clf.fit(Xtr,y)
    raw_te=clf.predict_proba(Xte)[:,1]
    # OOB is unavailable with balanced bootstrap defaults, so calibrate on a deterministic holdback slice.
    cut=max(200,int(len(train)*.82))
    if cut < len(train)-80 and y[:cut].sum()>20 and y[cut:].sum()>10:
        c2=ExtraTreesClassifier(n_estimators=50,max_depth=13,min_samples_leaf=14,max_features=.85,class_weight='balanced_subsample',random_state=73+horizon,n_jobs=-1)
        c2.fit(Xtr[:cut],y[:cut]); hold=c2.predict_proba(Xtr[cut:])[:,1]
        p=calibrate_prob(y[cut:],hold,raw_te)
    else: p=np.clip(raw_te,.001,.999)

    active=y==1
    # Total games and points conditional on any meaningful future season. Log targets reduce star/outlier leverage.
    rg=ExtraTreesRegressor(n_estimators=60,max_depth=15,min_samples_leaf=10,max_features=.9,random_state=41+horizon,n_jobs=-1)
    rp=ExtraTreesRegressor(n_estimators=60,max_depth=15,min_samples_leaf=10,max_features=.9,random_state=51+horizon,n_jobs=-1)
    rb=ExtraTreesRegressor(n_estimators=60,max_depth=15,min_samples_leaf=10,max_features=.9,random_state=61+horizon,n_jobs=-1)
    rg.fit(Xtr[active],np.log1p(train.loc[active,tcol(horizon,'games')]))
    rp.fit(Xtr[active],np.log1p(train.loc[active,tcol(horizon,'points')]))
    rb.fit(Xtr[active],train.loc[active,tcol(horizon,'best_avg')])
    cg=np.expm1(rg.predict(Xte)).clip(0,23*horizon)
    cp=np.expm1(rp.predict(Xte)).clip(0,145*23*horizon)
    best=rb.predict(Xte).clip(0,145)
    return pd.DataFrame({
        'pred_p_any_meaningful':p,
        'pred_games_if_active':cg,
        'pred_points_if_active':cp,
        'pred_best_if_active':best,
        'pred_uncond_games':p*cg,
        'pred_uncond_points':p*cp,
        'pred_uncond_best':p*best,
    },index=test.index)


def naive(train,test,horizon):
    tr=train.copy(); te=test.copy()
    tr['pick_bin']=pd.cut(tr.pick,[0,10,20,30,45,60,101],include_lowest=True)
    te['pick_bin']=pd.cut(te.pick,[0,10,20,30,45,60,101],include_lowest=True)
    tr['tenure_bin']=pd.cut(tr.tenure,[-1,0,1,2,4,8,99]); te['tenure_bin']=pd.cut(te.tenure,[-1,0,1,2,4,8,99])
    cols=['position','pick_bin','tenure_bin']
    tr['_event']=(tr[tcol(horizon,'meaningful_seasons')]>0).astype(int)
    agg=tr.groupby(cols,observed=True).agg(p=('_event','mean'),games=(tcol(horizon,'games'),'mean'),points=(tcol(horizon,'points'),'mean'),best=(tcol(horizon,'best_avg'),'mean')).reset_index()
    te=te.merge(agg,on=cols,how='left',sort=False).set_index(test.index)
    for c,target in [('p','_event'),('games',tcol(horizon,'games')),('points',tcol(horizon,'points')),('best',tcol(horizon,'best_avg'))]:
        fallback=tr.groupby('position')[target].mean()
        te[c]=te[c].fillna(te.position.map(fallback)).fillna(tr[target].mean())
    # demonstrated evidence influences established players; draft rows stay cohort-prior only.
    evidence=np.clip(te.total_games/(20*horizon),0,1)
    persistence_games=np.minimum(23*horizon,te.games_last_2/2*horizon)
    level=np.where(te.weighted_avg>0,te.weighted_avg,te.last_avg)
    demonstrated_points=persistence_games*level
    p_recent=np.clip(te.games_last_2/30,0,1)
    p=np.where(te.tenure==0,te.p,.55*te.p+.45*p_recent)
    games=np.where(te.tenure==0,te.games,evidence*persistence_games+(1-evidence)*te.games)
    points=np.where(te.tenure==0,te.points,evidence*demonstrated_points+(1-evidence)*te.points)
    best=np.where(te.tenure==0,te.best,evidence*np.maximum(level,te.career_best)+(1-evidence)*te.best)
    return pd.DataFrame({'pred_p_any_meaningful':np.clip(p,.001,.999),'pred_uncond_games':np.maximum(0,games),'pred_uncond_points':np.maximum(0,points),'pred_uncond_best':np.maximum(0,best)},index=test.index)


def metrics(test,pred,h):
    event=(test[tcol(h,'meaningful_seasons')]>0).astype(int).to_numpy(); p=pred.pred_p_any_meaningful.to_numpy()
    out={'n':len(test),'event_rate':float(event.mean()),'pred_event_rate':float(p.mean()),'brier_any_meaningful':float(brier_score_loss(event,p))}
    try: out['auc_any_meaningful']=float(roc_auc_score(event,p))
    except ValueError: out['auc_any_meaningful']=None
    for target,pc in [(tcol(h,'games'),'pred_uncond_games'),(tcol(h,'points'),'pred_uncond_points'),(tcol(h,'best_avg'),'pred_uncond_best')]:
        a=test[target].to_numpy(float); z=pred[pc].to_numpy(float)
        out['mae_'+target]=float(mean_absolute_error(a,z)); out['rmse_'+target]=float(mean_squared_error(a,z)**.5)
    # Keeper-relevant event calibration.
    for threshold in (90,100,110):
        actual=((test[tcol(h,'best_avg')]>=threshold)&(test[tcol(h,'meaningful_seasons')]>0)).astype(int).to_numpy()
        # Approximate from predicted best and event prob; dedicated threshold models come next.
        z=(pred.pred_uncond_best.to_numpy()-threshold)/10
        prob=np.clip(p/(1+np.exp(-z)),.001,.999)
        out[f'brier_peak_{threshold}']=float(brier_score_loss(actual,prob))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    df=pd.read_csv(a.dataset); outdir=Path(a.out); outdir.mkdir(parents=True,exist_ok=True)
    all_metrics=[]; all_preds=[]
    for h,last_origin in [(1,2025),(3,2023),(5,2021)]:
        first=2018
        for origin in range(first,last_origin+1):
            # A training row is legal only when its entire target horizon finishes before the test origin.
            train=df[(df.origin_year+h < origin)&(df.origin_year>=2008)].copy()
            test=df[df.origin_year==origin].copy()
            if len(train)<700 or len(test)<30: continue
            for model in ('naive','vnext_hurdle','vnext_draft_specialist'):
                if model=='naive': pred=naive(train,test,h)
                elif model=='vnext_hurdle': pred=fit_hurdle(train,test,h,False)
                else:
                    pred=fit_hurdle(train,test,h,False)
                    dtest=test.tenure.eq(0)
                    dtrain=train.tenure.eq(0)
                    if dtest.any() and dtrain.sum()>=300:
                        dp=fit_hurdle(train[dtrain],test[dtest],h,True)
                        pred.loc[dtest,dp.columns]=dp.values
                m=metrics(test,pred,h); m.update({'horizon':h,'origin':origin,'model':model}); all_metrics.append(m)
                cols=['key','player','origin_year','position','pick','tenure',tcol(h,'games'),tcol(h,'points'),tcol(h,'best_avg'),tcol(h,'meaningful_seasons')]; keep=test[cols].copy(); keep=keep.rename(columns={tcol(h,'games'):f'h{h}_games',tcol(h,'points'):f'h{h}_points',tcol(h,'best_avg'):f'h{h}_best_avg',tcol(h,'meaningful_seasons'):f'h{h}_meaningful_seasons'})
                keep['horizon']=h; keep['model']=model
                for c in pred.columns: keep[c]=pred[c].to_numpy()
                all_preds.append(keep)
    met=pd.DataFrame(all_metrics); preds=pd.concat(all_preds,ignore_index=True)
    met.to_csv(outdir/'rolling_metrics.csv',index=False); preds.to_csv(outdir/'predictions.csv',index=False)
    metric_cols=[c for c in met.columns if c not in ('model','origin','horizon','n')]
    summary=met.groupby(['horizon','model'])[metric_cols].mean().reset_index()
    summary.to_csv(outdir/'summary_metrics.csv',index=False)
    # Slice diagnostics.
    slices=[]
    for (h,model),g in preds.groupby(['horizon','model']):
        for name,mask in [('all',np.ones(len(g),bool)),('draft_time',g.tenure.eq(0)),('early_tenure_0_2',g.tenure.le(2)),('first_round',g.pick.le(20)),('later_pick_41plus',g.pick.ge(41))]:
            z=g[mask]
            if len(z)<20: continue
            event=(z[f'h{h}_meaningful_seasons']>0).astype(int)
            row={'horizon':h,'model':model,'slice':name,'n':len(z),'actual_event':event.mean(),'pred_event':z.pred_p_any_meaningful.mean(),'brier':brier_score_loss(event,z.pred_p_any_meaningful),'mae_games':mean_absolute_error(z[f'h{h}_games'],z.pred_uncond_games),'mae_points':mean_absolute_error(z[f'h{h}_points'],z.pred_uncond_points),'mae_best':mean_absolute_error(z[f'h{h}_best_avg'],z.pred_uncond_best)}
            try: row['auc']=roc_auc_score(event,z.pred_p_any_meaningful)
            except ValueError: row['auc']=None
            slices.append(row)
    pd.DataFrame(slices).to_csv(outdir/'slice_metrics.csv',index=False)
    payload={'rows':int(len(preds)/3),'origins_by_horizon':{str(h):sorted(met[met.horizon==h].origin.unique().tolist()) for h in (1,3,5)},'summary':summary.to_dict(orient='records')}
    (outdir/'summary.json').write_text(json.dumps(payload,indent=2)); print(json.dumps(payload,indent=2))
if __name__=='__main__': main()
