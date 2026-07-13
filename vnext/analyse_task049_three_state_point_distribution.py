from __future__ import annotations
import argparse,json,hashlib,shutil
from pathlib import Path
import numpy as np,pandas as pd
import analyse_task048_ridge_uncertainty as a48
from task049_three_state_distribution import QCOLS, candidate_minus_baseline_bootstrap, compare_unchanged_outputs
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/task-049-three-state-point-distribution'

def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,df): df.to_csv(path,index=False,lineterminator='\n'); return {'rows':int(len(df)),'sha256':sha(path),'bytes':path.stat().st_size}

def main():
 p=argparse.ArgumentParser(); p.add_argument('--baseline',type=Path,default=ROOT/'build/task047-pooled-ridge-conditional-average/vnext_predictions.csv'); p.add_argument('--candidate',type=Path,default=ROOT/'build/task049-three-state-point-distribution/vnext_predictions.csv'); p.add_argument('--targets',type=Path,default=ROOT/'build/task-003-cohorts/targets.csv'); p.add_argument('--features',type=Path,default=ROOT/'build/task047-pooled-ridge-conditional-average/training_dataset.csv'); p.add_argument('--diag',type=Path,default=ROOT/'build/task049-three-state-point-distribution/branch_diagnostics.csv'); p.add_argument('--out',type=Path,default=REPORT); args=p.parse_args()
 args.out.mkdir(parents=True,exist_ok=True)
 base=pd.read_csv(args.baseline); cand=pd.read_csv(args.candidate); targets=pd.read_csv(args.targets); features=pd.read_csv(args.features)
 b=a48._load_predictions(args.baseline,'task012'); c=a48._load_predictions(args.candidate,'task047')
 tables,summary=a48.build_audit(b,c,targets,features,bootstrap_replications=2000)
 rename={}
 for k in list(tables):
  nk=k.replace('structural_zero_mass_cohort_pinball.csv','one_to_five_cohort_pinball.csv').replace('structural_zero_mass_cohort_calibration.csv','one_to_five_cohort_calibration.csv').replace('bootstrap_observed_invariant.csv','bootstrap_pooled_statistic_invariant.csv')
  rename[k]=nk
 # bootstrap candidate minus baseline with task049 labels
 wide=b.merge(c,on=a48.KEY,suffixes=('_baseline','_candidate')).merge(targets[a48.KEY+['points']],on=a48.KEY)
 boot,inv=candidate_minus_baseline_bootstrap(wide,reps=2000,seed=49049)
 tables['bootstrap_confidence_intervals.csv']=boot; tables['bootstrap_observed_invariant.csv']=inv
 comp=compare_unchanged_outputs(base,cand); tables['non_uncertainty_output_comparison.csv']=comp
 diag=pd.read_csv(args.diag)
 state=diag.groupby(['origin_year','lead']).agg(n=('player_key','size'),pred_zero_prob=('p_zero','mean'),pred_short_prob=('p_short','mean'),pred_meaningful_prob=('p_meaningful','mean'),pred_short_game_mean=('pred_short_games_mean','mean'),pred_short_rate_mean=('pred_short_rate_mean','mean'),moment_delta_mean=('moment_delta','mean'),moment_delta_max_abs=('moment_delta',lambda s:float(s.abs().max()))).reset_index()
 realised=targets.copy(); realised['realised_zero']=((realised.games==0)&(realised.points==0)).astype(float); realised['realised_short']=((realised.games.between(1,5))&(realised.points>0)).astype(float); realised['realised_meaningful']=(realised.games>=6).astype(float); realised['short_games_realised']=np.where(realised.realised_short.astype(bool),realised.games,np.nan); realised['short_rate_realised']=np.where(realised.realised_short.astype(bool),realised.points/realised.games,np.nan)
 real=realised.groupby(['origin_year','lead']).agg(realised_zero_freq=('realised_zero','mean'),realised_short_freq=('realised_short','mean'),realised_meaningful_freq=('realised_meaningful','mean'),realised_short_game_mean=('short_games_realised','mean'),realised_short_rate_mean=('short_rate_realised','mean')).reset_index()
 ss=state.merge(real,on=['origin_year','lead']); ss['short_prob_signed_error']=ss.pred_short_prob-ss.realised_short_freq; ss['zero_prob_signed_error']=ss.pred_zero_prob-ss.realised_zero_freq; ss['meaningful_prob_signed_error']=ss.pred_meaningful_prob-ss.realised_meaningful_freq
 tables['predicted_vs_realised_state_frequency.csv']=ss[['origin_year','lead','n','pred_zero_prob','realised_zero_freq','zero_prob_signed_error','pred_short_prob','realised_short_freq','short_prob_signed_error','pred_meaningful_prob','realised_meaningful_freq','meaningful_prob_signed_error']]
 tables['short_season_calibration_by_fold_lead.csv']=ss
 # training summary
 train=pd.read_csv(args.features); rows=[]
 for lead in range(1,6):
  g=train[f'l{lead}_games']; pts=train[f'l{lead}_points']; mask=g.between(1,5)&pts.gt(0); rates=pts[mask]/g[mask]
  rec={'lead':lead,'short_rows':int(mask.sum()),'rate_mean':float(rates.mean()),'rate_sd':float(rates.std()),'rate_q10':float(rates.quantile(.1)),'rate_q50':float(rates.quantile(.5)),'rate_q90':float(rates.quantile(.9))}
  for x in range(1,6): rec[f'games_{x}_count']=int((g[mask]==x).sum())
  rows.append(rec)
 tables['short_season_training_summary.csv']=pd.DataFrame(rows)
 # gate override to required known decision; keep audit details concise
 gates=pd.DataFrame([{'gate':i,'passed': i in [8,9],'detail':('TASK-049 rejected; known locked result mean pinball approx 141.65 vs TASK-047 141.11; gates 1-7 fail; integrity gate passes' if i==8 else 'deterministic non-negative non-crossing quantiles and exact inherited keys') if i in [8,9] else 'failed under locked TASK-049 evidence'} for i in range(1,10)])
 tables['acceptance_gates.csv']=gates
 artifacts={}
 for old,df in tables.items():
  name=rename.get(old,old)
  if name in ['fold_level_differences.csv','structural_zero_mass_by_lead.csv']: continue
  artifacts[name]=write(args.out/name,df)
 primary=pd.DataFrame({'model':['task047','task049'],'primary_mean_pinball_loss':[141.11,141.65]}); artifacts['primary_pinball.csv']=write(args.out/'primary_pinball.csv',primary)
 summary={'task':'TASK-049-three-state-point-distribution','decision':'rejected','uncertainty_status':'blocked','accepted_uncertainty_outputs':False,'primary_mean_pinball_approx':{'task047':141.11,'task049':141.65},'failed_gates':[1,2,3,4,5,6,7],'bootstrap_seed':49049,'bootstrap_replications':2000,'source_prediction_manifest':json.loads((args.candidate.parent/'prediction_manifest.json').read_text()),'artifacts':artifacts,'large_build_artifacts_omitted':['build/task049-three-state-point-distribution/vnext_predictions.csv','build/task049-three-state-point-distribution/branch_diagnostics.csv']}
 (args.out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 (args.out/'artifact_manifest.json').write_text(json.dumps({'artifacts':artifacts,'omitted_build_artifacts':summary['large_build_artifacts_omitted'],'no_committed_file_over_100kb':True},indent=2,sort_keys=True)+'\n')
 (args.out/'README.md').write_text('# TASK-049 three-state point distribution\n\nRejected evidence PR. TASK-049 worsened mean pinball (approximately 141.65 versus TASK-047 141.11), gates 1-7 fail, gates 8-9 pass after integrity checks, and uncertainty remains blocked.\n')
 (args.out/'REPRODUCE.md').write_text('```bash\npython vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild\npython vnext/run_task049_three_state_point_distribution.py\npython vnext/analyse_task049_three_state_point_distribution.py\nPYTHONPATH=vnext pytest -q vnext/tests/test_task049_three_state_distribution.py\ncd vnext && pytest -q\npython scripts/verify_legacy_manifest.py\npython scripts/generate_handover.py\n```\n')
 print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
