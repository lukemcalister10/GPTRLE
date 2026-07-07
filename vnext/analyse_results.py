from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, mean_absolute_error, roc_auc_score

ROOT=Path(__file__).parent
pred=pd.read_csv(ROOT/'output/eval_v1/predictions.csv')
# Handle earlier run label if present.
pred['model']=pred.model.replace({'vnext_linear_hurdle':'vnext_tree_hurdle'})

def slice_metrics(d):
    actual=d.next_meaningful.to_numpy()
    out={'n':len(d),'actual_meaningful_rate':actual.mean(),'predicted_meaningful_rate':d.pred_p_meaningful.mean(),
         'brier':brier_score_loss(actual,d.pred_p_meaningful),
         'mae_unconditional_avg':mean_absolute_error(np.where(actual==1,d.next_avg,0),d.pred_unconditional_avg)}
    try: out['auc']=roc_auc_score(actual,d.pred_p_meaningful)
    except: out['auc']=None
    m=actual==1
    out['mae_avg_if_meaningful']=mean_absolute_error(d.next_avg[m],d.pred_avg_if_meaningful[m]) if m.any() else None
    return out

slices=[]
for model,g in pred.groupby('model'):
    for name,mask in {
        'all':np.ones(len(g),dtype=bool),
        'draft_time_t0':g.tenure.eq(0),
        'young_age_le22':g.origin_year.sub(0).notna() & (g.tenure<=4), # tenure is available; age absent in predictions export
        'early_tenure_0_2':g.tenure.le(2),
        'established_tenure_3plus':g.tenure.ge(3),
        'first_round_pick_1_20':g.pick.le(20),
        'later_pick_41plus':g.pick.ge(41),
    }.items():
        d=g[mask]
        if len(d):
            row={'model':model,'slice':name}; row.update(slice_metrics(d)); slices.append(row)
s=pd.DataFrame(slices)
s.to_csv(ROOT/'output/eval_v1/slice_metrics.csv',index=False)

# Reliability bins for the challenger, especially draft-time rows.
rels=[]
for model,g in pred.groupby('model'):
  for cohort_name,sub in [('all',g),('draft_time_t0',g[g.tenure==0]),('early_tenure_0_2',g[g.tenure<=2])]:
    if sub.empty: continue
    sub=sub.copy(); sub['bin']=pd.cut(sub.pred_p_meaningful,np.linspace(0,1,11),include_lowest=True)
    r=sub.groupby('bin',observed=True).agg(n=('next_meaningful','size'),predicted=('pred_p_meaningful','mean'),observed=('next_meaningful','mean')).reset_index()
    r['model']=model;r['cohort']=cohort_name;rels.append(r)
rel=pd.concat(rels,ignore_index=True)
rel.to_csv(ROOT/'output/eval_v1/reliability.csv',index=False)

payload={'slice_metrics':s.to_dict(orient='records')}
(ROOT/'output/eval_v1/diagnostics.json').write_text(json.dumps(payload,indent=2))
print(s.to_string(index=False))
