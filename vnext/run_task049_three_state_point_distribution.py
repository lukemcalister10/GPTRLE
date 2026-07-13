from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import pandas as pd
from task049_three_state_distribution import build_short_support, compare_unchanged_outputs, generate_three_state_predictions, short_support_training_summary, SAMPLE_COUNT, GENERATOR_ID
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCE=ROOT/'build/task047-pooled-ridge-conditional-average'
DEFAULT_OUT=ROOT/'build/task049-three-state-point-distribution'

def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

def run(source:Path=DEFAULT_SOURCE,out:Path=DEFAULT_OUT):
    out.mkdir(parents=True,exist_ok=True)
    required = [source/'vnext_predictions.csv', source/'training_dataset.csv', source/'fold_artifact_manifest.csv', source/'prediction_manifest.json', source/'fold_failures.csv', ROOT/'build/task-003-cohorts/target_failures.csv']
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing mandatory TASK-049 source artifact(s): {missing}")
    source_manifest = json.loads((source/'prediction_manifest.json').read_text())
    fold_failures = pd.read_csv(source/'fold_failures.csv')
    target_failures = pd.read_csv(ROOT/'build/task-003-cohorts/target_failures.csv')
    if len(fold_failures) != 0 or len(target_failures) != 0:
        raise ValueError(f"source failure artifacts must be empty; fold_failures={len(fold_failures)} target_failures={len(target_failures)}")
    preds=pd.read_csv(source/'vnext_predictions.csv')
    ds=pd.read_csv(source/'training_dataset.csv')
    rows=[]
    for lead in range(1,6):
        rows.append(pd.DataFrame({'origin_year':ds.origin_year,'lead':lead,'games':ds[f'l{lead}_games'],'points':ds[f'l{lead}_points']}))
    training=pd.concat(rows, ignore_index=True).dropna(subset=['games','points'])
    folds=pd.read_csv(source/'fold_artifact_manifest.csv')
    supports=build_short_support(training, folds)
    cand,diag=generate_three_state_predictions(preds, supports)
    comp=compare_unchanged_outputs(preds,cand)
    cand.to_csv(out/'vnext_predictions.csv',index=False,lineterminator='\n')
    diag.to_csv(out/'branch_diagnostics.csv',index=False,lineterminator='\n')
    comp.to_csv(out/'non_uncertainty_output_comparison.csv',index=False,lineterminator='\n')
    by=diag.groupby(['origin_year','lead']).agg(rows=('player_key','size'),p_zero_mean=('p_zero','mean'),p_short_mean=('p_short','mean'),p_meaningful_mean=('p_meaningful','mean'),short_draw_count_sum=('short_draw_count','sum'),meaningful_draw_count_sum=('meaningful_draw_count','sum'),pred_short_games_mean=('pred_short_games_mean','mean'),pred_short_rate_mean=('pred_short_rate_mean','mean'),moment_delta_mean=('moment_delta','mean'),moment_error_after_max_abs=('moment_error_after',lambda s: float(s.abs().max()))).reset_index()
    by.to_csv(out/'branch_diagnostics_by_fold_lead.csv',index=False,lineterminator='\n')
    support_summary = short_support_training_summary(supports)
    support_summary.to_csv(out/'short_season_training_summary_by_fold_lead.csv',index=False,lineterminator='\n')
    manifest={
      'task':'TASK-049-three-state-point-distribution','state':'candidate-rejected-evidence','source_task047_dir':str(source),'sample_count':SAMPLE_COUNT,'seed_contract':'sha256(TASK-049|player_key|origin_year|lead)','source_manifest_task':source_manifest.get('task'),
      'source_prediction_manifest':{'path':str(source/'prediction_manifest.json'),'sha256':sha(source/'prediction_manifest.json') if (source/'prediction_manifest.json').exists() else None},
      'source_fold_failures':{'path':str(source/'fold_failures.csv'),'rows':int(len(pd.read_csv(source/'fold_failures.csv'))) if (source/'fold_failures.csv').exists() else None,'sha256':sha(source/'fold_failures.csv') if (source/'fold_failures.csv').exists() else None},
      'source_target_failures':{'path':str(ROOT/'build/task-003-cohorts/target_failures.csv'),'rows':int(len(pd.read_csv(ROOT/'build/task-003-cohorts/target_failures.csv'))) if (ROOT/'build/task-003-cohorts/target_failures.csv').exists() else None,'sha256':sha(ROOT/'build/task-003-cohorts/target_failures.csv') if (ROOT/'build/task-003-cohorts/target_failures.csv').exists() else None},
      'candidate_key_inheritance':'candidate rows are deterministic transformations of TASK-047 vnext_predictions.csv keys; non-quantile comparison is exact',
      'task049_transformation_failure_rows':0,
      'prediction_rows':int(len(cand)),'diagnostic_rows':int(len(diag)),
      'artifacts':{n:{'path':str(out/n),'rows':int(len(pd.read_csv(out/n))),'sha256':sha(out/n),'bytes':(out/n).stat().st_size} for n in ['vnext_predictions.csv','branch_diagnostics.csv','branch_diagnostics_by_fold_lead.csv','short_season_training_summary_by_fold_lead.csv','non_uncertainty_output_comparison.csv']}
    }
    (out/'prediction_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(manifest,indent=2,sort_keys=True))
    return manifest

def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',type=Path,default=DEFAULT_SOURCE); p.add_argument('--out',type=Path,default=DEFAULT_OUT)
    a=p.parse_args(); run(a.source,a.out)
if __name__=='__main__': main()
