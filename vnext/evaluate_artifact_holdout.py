"""Untouched-origin validation of the persisted-artifact estimator family."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from sklearn.metrics import brier_score_loss, mean_absolute_error, roc_auc_score
from model_artifacts import train_lead,predict

def auc(y,p): return roc_auc_score(y,p) if y.nunique()>1 else float('nan')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True);ap.add_argument('--out',required=True);ap.add_argument('--origin',type=int,default=2021);a=ap.parse_args()
 d=pd.read_csv(a.dataset);rows=[]
 for lead in range(1,6):
  tr=d[(d.origin_year+lead<a.origin)&(d.origin_year>=2008)].copy();te=d[d.origin_year==a.origin].copy();art=train_lead(tr,lead);p=predict(art,te);y=te[f'l{lead}_meaningful'].astype(int)
  r={'lead':lead,'n':len(te),'actual_event':y.mean(),'pred_event':p.p_meaningful.mean(),'brier_event':brier_score_loss(y,p.p_meaningful),'auc_event':auc(y,p.p_meaningful),'mae_games':mean_absolute_error(te[f'l{lead}_games'],p.exp_games),'mae_points':mean_absolute_error(te[f'l{lead}_points'],p.exp_points)}
  for t in (90,100,110):r[f'brier_{t}']=brier_score_loss(te[f'l{lead}_{t}'],p[f'p{t}']);r[f'auc_{t}']=auc(te[f'l{lead}_{t}'],p[f'p{t}'])
  rows.append(r)
 O=Path(a.out);O.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(O,index=False);print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
