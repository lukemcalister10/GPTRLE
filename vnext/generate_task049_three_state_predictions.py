from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import pandas as pd
from task049_three_state_point_distribution import generate_three_state_predictions, KEY, QCOLS
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--task047-dir',type=Path,default=ROOT/'build/task047-pooled-ridge-conditional-average'); p.add_argument('--out',type=Path,required=True); args=p.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
 pred_path=args.task047_dir/'vnext_predictions.csv'; train_path=args.task047_dir/'training_dataset.csv'; fold_path=args.task047_dir/'fold_artifact_manifest.csv'
 pred=pd.read_csv(pred_path); train=pd.read_csv(train_path); fold=pd.read_csv(fold_path)
 cand,evidence,recon=generate_three_state_predictions(pred,train,fold)
 if cand[KEY].duplicated().any(): raise ValueError('duplicate prediction keys')
 if (cand[QCOLS].to_numpy(float)<-1e-12).any(): raise ValueError('negative quantile')
 if (pd.DataFrame(cand[QCOLS]).diff(axis=1).iloc[:,1:].to_numpy(float)<-1e-12).any(): raise ValueError('crossing quantile')
 max_delta=float(recon.abs_delta.max())
 if max_delta>1e-8: raise ValueError(f'moment reconciliation failed: {max_delta}')
 cand.to_csv(args.out/'vnext_predictions.csv',index=False,lineterminator='\n'); evidence.to_csv(args.out/'short_season_evidence.csv',index=False,lineterminator='\n'); recon.to_csv(args.out/'moment_reconciliation.csv',index=False,lineterminator='\n')
 manifest={'task':'TASK-049-three-state-point-distribution','model_id':'vnext_task049_three_state_point_distribution','prediction_rows':len(cand),'input_hashes':{'task047_predictions_sha256':sha(pred_path),'training_dataset_sha256':sha(train_path),'fold_artifact_manifest_sha256':sha(fold_path)},'output_hashes':{n:sha(args.out/n) for n in ['vnext_predictions.csv','short_season_evidence.csv','moment_reconciliation.csv']},'quantile_method':{'method':'three_state_empirical_short_season_mixture','sample_count':2048,'seed':'sha256(TASK-049|player_key|origin_year|lead)','moment_adjustment':'multiply all simulated positive and meaningful points by exp_points/raw_simulated_mean per row'},'target_failure_rows':0,'fold_failure_rows':0}
 (args.out/'prediction_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps(manifest,indent=2,sort_keys=True))
if __name__=='__main__': main()
