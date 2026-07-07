"""Calibrate cross-season persistence and simulate coherent five-year careers.

Uses a one-factor Gaussian copula to preserve each annual model's calibrated
marginal probabilities while allowing strong outcomes to persist across years.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import brier_score_loss, mean_absolute_error

THRESH=(90,100,110)

def any_prob_copula(prob: np.ndarray, rho: float, z_common: np.ndarray, z_idio: np.ndarray) -> np.ndarray:
    """Monte Carlo P(any event) for rows x 5 annual marginal probabilities."""
    p=np.clip(prob,1e-6,1-1e-6)
    cuts=norm.ppf(p)[:,None,:]  # rows,1,years
    latent=np.sqrt(rho)*z_common[None,:,None]+np.sqrt(1-rho)*z_idio[None,:,:]
    return (latent < cuts).any(axis=2).mean(axis=1)

def choose_rho(g: pd.DataFrame, threshold: int, sims: int=400, seed: int=2607):
    piv=g.pivot(index=['key','origin_year'],columns='lead',values=f'p{threshold}').dropna()
    act=g.pivot(index=['key','origin_year'],columns='lead',values=f'actual_{threshold}').reindex(piv.index).fillna(0)
    actual=(act.max(axis=1)>0).astype(int).to_numpy()
    probs=piv[[1,2,3,4,5]].to_numpy()
    origins=np.array([x[1] for x in piv.index])
    rng=np.random.default_rng(seed+threshold)
    zc=rng.standard_normal(sims); zi=rng.standard_normal((sims,5))
    rows=[]
    for rho in np.linspace(0,.9,10):
        pred=any_prob_copula(probs,float(rho),zc,zi)
        val=origins<=2020; test=origins==2021
        rows.append({'threshold':threshold,'rho':rho,
                     'val_brier':brier_score_loss(actual[val],pred[val]),
                     'val_mean_pred':pred[val].mean(),'val_actual':actual[val].mean(),
                     'test_brier':brier_score_loss(actual[test],pred[test]),
                     'test_mean_pred':pred[test].mean(),'test_actual':actual[test].mean()})
    R=pd.DataFrame(rows); best=R.loc[R.val_brier.idxmin()]
    return R,best,piv,act

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predictions',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    O=Path(a.out);O.mkdir(parents=True,exist_ok=True);g=pd.read_csv(a.predictions)
    allgr=[];summary=[];corr=[]
    # Observed persistence among annual outcomes.
    for t in THRESH:
        A=g.pivot_table(index=['key','origin_year'],columns='lead',values=f'actual_{t}').dropna()
        c=A.corr();c.to_csv(O/f'observed_event_correlation_{t}.csv')
        off=c.to_numpy()[np.triu_indices(5,1)]
        corr.append({'threshold':t,'mean_pairwise_event_corr':float(np.nanmean(off)),'adjacent_event_corr':float(np.nanmean([c.loc[i,i+1] for i in range(1,5)]))})
        R,b,piv,act=choose_rho(g,t);allgr.append(R)
        # Compare independence and selected copula on the untouched 2021 origin.
        probs=piv[[1,2,3,4,5]].to_numpy(); actual=(act.max(axis=1)>0).astype(int).to_numpy(); origins=np.array([x[1] for x in piv.index]);test=origins==2021
        independent=1-np.prod(1-probs,axis=1)
        rng=np.random.default_rng(9000+t);zc=rng.standard_normal(1200);zi=rng.standard_normal((1200,5));cop=any_prob_copula(probs,float(b.rho),zc,zi)
        summary.append({'threshold':t,'selected_rho':float(b.rho),
                        'test_n':int(test.sum()),'test_actual':float(actual[test].mean()),
                        'independence_pred':float(independent[test].mean()),'independence_brier':float(brier_score_loss(actual[test],independent[test])),
                        'copula_pred':float(cop[test].mean()),'copula_brier':float(brier_score_loss(actual[test],cop[test])),
                        'independence_mae_probability':float(mean_absolute_error(actual[test],independent[test])),
                        'copula_mae_probability':float(mean_absolute_error(actual[test],cop[test]))})
    pd.concat(allgr,ignore_index=True).to_csv(O/'rho_grid.csv',index=False)
    pd.DataFrame(corr).to_csv(O/'observed_persistence.csv',index=False)
    S=pd.DataFrame(summary);S.to_csv(O/'copula_vs_independence.csv',index=False)
    (O/'summary.json').write_text(json.dumps({'persistence':corr,'comparison':summary},indent=2))
    print(pd.DataFrame(corr).to_string(index=False));print('\n',S.to_string(index=False))
if __name__=='__main__':main()
