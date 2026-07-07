"""Train annual vNext models once, persist them, and run deterministic inference.

Artifacts contain preprocessing, estimators, temporal isotonic calibrators and
conditional residual scales. No model fitting occurs during board generation.
"""
from __future__ import annotations
import argparse, json
from dataclasses import dataclass
from pathlib import Path
import joblib
import sys
if __name__ == '__main__':
    sys.modules['model_artifacts'] = sys.modules[__name__]
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.isotonic import IsotonicRegression
from evaluate_v3_fast import pre, TH

@dataclass
class ConstantCalibrator:
    value: float
    def predict(self, x):
        return np.full(len(x), self.value, dtype=float)

@dataclass
class LeadArtifact:
    lead: int
    preprocessor: object
    event_model: object
    event_calibrator: object
    games_model: object
    avg_model: object
    threshold_models: dict
    threshold_calibrators: dict
    games_resid_sd: float
    avg_resid_sd: float
    train_max_origin: int
    n_fit: int
    n_cal: int


ConstantCalibrator.__module__='model_artifacts'
LeadArtifact.__module__='model_artifacts'

def make_calibrator(raw, y):
    y=np.asarray(y,dtype=int)
    if len(np.unique(y))<2:
        return ConstantCalibrator(float(y.mean()) if len(y) else 0.0)
    return IsotonicRegression(out_of_bounds='clip').fit(np.asarray(raw),y)


def split_temporal(train: pd.DataFrame, lead: int):
    years=sorted(train.origin_year.unique())
    cut=years[max(1,int(len(years)*.8))-1]
    fit=train[train.origin_year<cut].copy(); cal=train[train.origin_year>=cut].copy()
    if len(cal)<100:
        cal=train[train.origin_year==years[-1]].copy(); fit=train[train.origin_year<years[-1]].copy()
    return fit,cal


def train_lead(train: pd.DataFrame, lead: int) -> LeadArtifact:
    fit,cal=split_temporal(train,lead)
    P=pre(); X=P.fit_transform(fit); C=P.transform(cal)
    y=fit[f'l{lead}_meaningful'].astype(int).to_numpy(); yc=cal[f'l{lead}_meaningful'].astype(int).to_numpy()
    event=SGDClassifier(loss='log_loss',alpha=0.0008,max_iter=800,tol=1e-3,random_state=lead).fit(X,y)
    event_cal=make_calibrator(event.predict_proba(C)[:,1],yc)
    active=y==1
    games=SGDRegressor(loss='huber',alpha=0.002,max_iter=800,tol=1e-3,random_state=lead+10).fit(X[active],fit.loc[active,f'l{lead}_games'].to_numpy(float))
    avg=SGDRegressor(loss='huber',alpha=0.002,max_iter=800,tol=1e-3,random_state=lead+20).fit(X[active],fit.loc[active,f'l{lead}_avg'].to_numpy(float))
    # Residual scales from temporally later calibration rows, conditional on meaningful.
    ca=cal[f'l{lead}_meaningful'].astype(bool).to_numpy()
    if ca.any():
        gp=np.clip(games.predict(C[ca]),0,23); ap=np.clip(avg.predict(C[ca]),0,145)
        gsd=float(np.std(cal.loc[ca,f'l{lead}_games'].to_numpy(float)-gp,ddof=1)) if ca.sum()>2 else 3.0
        asd=float(np.std(cal.loc[ca,f'l{lead}_avg'].to_numpy(float)-ap,ddof=1)) if ca.sum()>2 else 12.0
    else: gsd,asd=3.0,12.0
    tm={}; tc={}
    for t in TH:
        yt=fit[f'l{lead}_{t}'].astype(int).to_numpy(); yct=cal[f'l{lead}_{t}'].astype(int).to_numpy()
        if yt.sum()<15 or len(np.unique(yt))<2:
            tm[t]=None; tc[t]=ConstantCalibrator(float(yt.mean()))
        else:
            m=SGDClassifier(loss='log_loss',alpha=0.001,max_iter=800,tol=1e-3,random_state=lead+t).fit(X,yt); tm[t]=m; tc[t]=make_calibrator(m.predict_proba(C)[:,1],yct)
    return LeadArtifact(lead=lead,preprocessor=P,event_model=event,event_calibrator=event_cal,games_model=games,avg_model=avg,threshold_models=tm,threshold_calibrators=tc,games_resid_sd=max(gsd,1.0),avg_resid_sd=max(asd,3.0),train_max_origin=int(max(train.origin_year)),n_fit=len(fit),n_cal=len(cal))


def predict(artifact: LeadArtifact, rows: pd.DataFrame) -> pd.DataFrame:
    Z=artifact.preprocessor.transform(rows)
    p=np.clip(artifact.event_calibrator.predict(artifact.event_model.predict_proba(Z)[:,1]),.001,.999)
    cg=np.clip(artifact.games_model.predict(Z),0,23); ca=np.clip(artifact.avg_model.predict(Z),0,145)
    out=pd.DataFrame({'p_meaningful':p,'cond_games':cg,'cond_avg':ca,'exp_games':p*cg,'exp_avg':p*ca,'exp_points':p*cg*ca},index=rows.index)
    for t in TH:
        m=artifact.threshold_models[t]
        raw=np.full(len(rows),artifact.threshold_calibrators[t].value) if m is None else m.predict_proba(Z)[:,1]
        out[f'p{t}']=np.clip(artifact.threshold_calibrators[t].predict(raw),.001,.999)
    arr=out[[f'p{t}' for t in TH]].to_numpy(); out[[f'p{t}' for t in TH]]=np.minimum.accumulate(arr,axis=1)
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--out',required=True); ap.add_argument('--target-cutoff',type=int,default=2025)
    a=ap.parse_args(); d=pd.read_csv(a.dataset); O=Path(a.out); O.mkdir(parents=True,exist_ok=True)
    manifest={'target_cutoff':a.target_cutoff,'leads':{}}
    for lead in range(1,6):
        tr=d[(d.origin_year+lead<=a.target_cutoff)&(d.origin_year>=2008)].copy()
        art=train_lead(tr,lead); joblib.dump(art,O/f'lead_{lead}.joblib',compress=3)
        manifest['leads'][str(lead)]={'rows':len(tr),'max_origin':int(tr.origin_year.max()),'n_fit':art.n_fit,'n_cal':art.n_cal,'games_resid_sd':art.games_resid_sd,'avg_resid_sd':art.avg_resid_sd}
    (O/'manifest.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
