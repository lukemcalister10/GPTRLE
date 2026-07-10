from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from analyse_task048_ridge_uncertainty import KEY,QCOLS,QUANTILES,prior_history,realised_cohort,pinball,calibration,interval_coverage,summarise_pinball,bootstrap_ci,validate_quantiles,EXPECTED_ROWS,EXPECTED_SNAPSHOTS,EXPECTED_FOLDS
BOOTSTRAP_SEED=49049; BOOTSTRAP_REPLICATIONS=2000
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,model):
 df=pd.read_csv(p); need=KEY+['p_meaningful','exp_games','cond_games','cond_avg','exp_points',*QCOLS]
 return df[need].assign(model=model)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--baseline',type=Path,required=True); ap.add_argument('--candidate',type=Path,required=True); ap.add_argument('--targets',type=Path,required=True); ap.add_argument('--features',type=Path,required=True); ap.add_argument('--moment-reconciliation',type=Path,required=True); ap.add_argument('--short-evidence',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
 base=load(args.baseline,'task047'); cand=load(args.candidate,'task049'); targets=pd.read_csv(args.targets)[KEY+['games','points']]; features=pd.read_csv(args.features)
 for name,df in [('baseline',base),('candidate',cand),('targets',targets)]:
  if df.duplicated(KEY).any(): raise ValueError(f'{name} duplicate keys')
 if not base[KEY].sort_values(KEY).reset_index(drop=True).equals(cand[KEY].sort_values(KEY).reset_index(drop=True)) or not base[KEY].sort_values(KEY).reset_index(drop=True).equals(targets[KEY].sort_values(KEY).reset_index(drop=True)): raise ValueError('keys differ')
 nonq=[c for c in base.columns if c not in QCOLS+['model']]
 
 b_nonq=base[nonq].sort_values(KEY).reset_index(drop=True); c_nonq=cand[nonq].sort_values(KEY).reset_index(drop=True)
 unchanged=True
 for _col in nonq:
  if pd.api.types.is_numeric_dtype(b_nonq[_col]):
   unchanged = unchanged and bool(np.nanmax(np.abs(b_nonq[_col].to_numpy(float)-c_nonq[_col].to_numpy(float))) <= 1e-12)
  else:
   unchanged = unchanged and b_nonq[_col].equals(c_nonq[_col])
 feat=features[[c for c in ['key','origin_year','position','total_games'] if c in features.columns]].rename(columns={'key':'player_key'})
 allp=pd.concat([base,cand]).merge(targets,on=KEY).merge(feat,on=['player_key','origin_year'],how='left')
 allp['broad_position']=allp.get('position',pd.Series('unknown',index=allp.index)).fillna('unknown').astype(str); allp['prior_history_cohort']=prior_history(allp.get('total_games',pd.Series(0,index=allp.index))); allp['realised_cohort']=realised_cohort(allp.games,allp.points)
 primary=summarise_pinball(allp,[]).groupby('model').pinball_loss.mean().reset_index(name='primary_mean_pinball_loss')
 def diff(summary, groups=[]):
  piv=summary.pivot_table(index=groups+['quantile','tau'],columns='model',values='pinball_loss').reset_index(); piv['abs_diff_task049_minus_task047']=piv.task049-piv.task047; piv['pct_diff_task049_minus_task047']=piv['abs_diff_task049_minus_task047']/piv.task047; return piv
 tables={}
 tables['primary_pinball.csv']=primary; tables['pinball_overall.csv']=diff(summarise_pinball(allp,[])); tables['pinball_by_lead.csv']=diff(summarise_pinball(allp,['lead']),['lead']); tables['fold_level_differences.csv']=diff(summarise_pinball(allp,['origin_year','lead']),['origin_year','lead'])
 for nm,groups in [('overall',[]),('by_lead',['lead']),('by_position',['broad_position']),('by_prior_history',['prior_history_cohort'])]: tables[f'quantile_calibration_{nm}.csv']=calibration(allp,groups); tables[f'interval_coverage_{nm}.csv']=interval_coverage(allp,groups)
 structural=[]
 for (model,lead),g in allp.groupby(['model','lead']):
  r={'model':model,'lead':lead,'n':len(g),'actual_zero_game_zero_point_rows':int((g.realised_cohort=='zero_game_zero_point').sum()),'actual_one_to_five_positive_points_rows':int((g.realised_cohort=='one_to_five_positive_points').sum()),'meaningful_six_plus_rows':int((g.realised_cohort=='meaningful_six_plus').sum())}
  for c,_ in QUANTILES: r[f'{c}_zero_proportion']=float((g[c].abs()<=1e-12).mean())
  structural.append(r)
 tables['realised_state_cohorts_by_lead.csv']=pd.DataFrame(structural); tables['state_probability_reconciliation.csv']=pd.read_csv(args.moment_reconciliation); tables['short_season_evidence.csv']=pd.read_csv(args.short_evidence)
 wide=base.merge(cand,on=KEY,suffixes=('_task012','_task047')).merge(targets,on=KEY) # names for imported bootstrap: observed is candidate-baseline
 tables['bootstrap_confidence_intervals.csv']=bootstrap_ci(wide,reps=BOOTSTRAP_REPLICATIONS,seed=BOOTSTRAP_SEED).rename(columns={'observed_diff_task047_minus_task012':'observed_diff_task049_minus_task047'})
 qv=[validate_quantiles(base,'task047'),validate_quantiles(cand,'task049')]; mr=tables['state_probability_reconciliation.csv']
 integrity=pd.DataFrame([{'check':'row_count_per_model','passed':allp.groupby('model').size().eq(EXPECTED_ROWS).all(),'detail':json.dumps({str(k):int(v) for k,v in allp.groupby('model').size().items()})},{'check':'player_origin_snapshots','passed':targets[KEY[:2]].drop_duplicates().shape[0]==EXPECTED_SNAPSHOTS,'detail':str(targets[KEY[:2]].drop_duplicates().shape[0])},{'check':'legal_folds','passed':targets[['origin_year','lead']].drop_duplicates().shape[0]==EXPECTED_FOLDS,'detail':str(targets[['origin_year','lead']].drop_duplicates().shape[0])},{'check':'non_uncertainty_outputs_unchanged','passed':unchanged,'detail':'all non-quantile prediction fields exact'},{'check':'moment_reconciliation_max_abs_delta_le_1e-8','passed':float(mr.abs_delta.max())<=1e-8,'detail':str(float(mr.abs_delta.max()))},*[{'check':f"{r['model']}_quantiles_non_negative",'passed':r['negative_quantile_values']==0,'detail':str(r['negative_quantile_values'])} for r in qv],*[{'check':f"{r['model']}_quantiles_non_crossing",'passed':r['crossing_rows']==0,'detail':str(r['crossing_rows'])} for r in qv]])
 tables['integrity_checks.csv']=integrity
 p=primary.set_index('model').primary_mean_pinball_loss; diffpct=(p.task049-p.task047)/p.task047; pin_over=tables['pinball_overall.csv']; max_worse=float(pin_over.pct_diff_task049_minus_task047.max()); cal=tables['quantile_calibration_overall.csv']; cal_base=float(cal[cal.model=='task047'].absolute_calibration_error.mean()); cal_c=float(cal[cal.model=='task049'].absolute_calibration_error.mean()); cov=tables['interval_coverage_overall.csv']; ccov=cov[cov.model=='task049'].set_index('interval'); leadcov=tables['interval_coverage_by_lead.csv']; leadc=leadcov[(leadcov.model=='task049') & (leadcov.interval.isin(['q25_q75','q10_q90']))]; sub=pd.concat([tables['interval_coverage_by_position.csv'],tables['interval_coverage_by_prior_history.csv']]); sub=sub[(sub.model=='task049')&(sub.n>=200)&(sub.interval.isin(['q25_q75','q10_q90']))]
 cohort=diff(summarise_pinball(allp[allp.realised_cohort=='one_to_five_positive_points'],[])); imp=int((cohort.abs_diff_task049_minus_task047<0).sum()); bad=bool((cohort.pct_diff_task049_minus_task047>.05).any())
 boot=tables['bootstrap_confidence_intervals.csv']; bp=boot[boot.metric=='primary_mean_pinball'].iloc[0]
 gates=pd.DataFrame([{'gate':1,'passed':diffpct<=-.01 and bp.ci_high <= p.task047*.01 and bp.ci_low<0,'detail':f'primary pct diff={diffpct:.6f}; bootstrap median not stored; CI=({bp.ci_low:.6f},{bp.ci_high:.6f})'},{'gate':2,'passed':max_worse<=.02,'detail':f'max quantile worsening={max_worse:.6f}'},{'gate':3,'passed':cal_c<=.05 and cal_c<=cal_base*.75,'detail':f'candidate={cal_c:.6f}; baseline={cal_base:.6f}'},{'gate':4,'passed':0.46<=ccov.loc['q25_q75'].coverage<=0.54 and 0.76<=ccov.loc['q10_q90'].coverage<=0.84,'detail':f"q25-q75={ccov.loc['q25_q75'].coverage:.6f}; q10-q90={ccov.loc['q10_q90'].coverage:.6f}"},{'gate':5,'passed':not (leadc.absolute_coverage_error>.08).any(),'detail':f'max={float(leadc.absolute_coverage_error.max()):.6f}'},{'gate':6,'passed':not (sub.absolute_coverage_error>.12).any(),'detail':f'max={float(sub.absolute_coverage_error.max()):.6f}'},{'gate':7,'passed':imp>=4 and not bad,'detail':f'improved_quantiles={imp}; any_worse_gt_5pct={bad}'},{'gate':8,'passed':unchanged and float(mr.abs_delta.max())<=1e-8,'detail':f"unchanged={unchanged}; max_mean_delta={float(mr.abs_delta.max()):.12g}"},{'gate':9,'passed':bool(integrity.passed.all()),'detail':'see integrity_checks.csv'}])
 tables['acceptance_gates.csv']=gates
 artifacts={}
 for n,df in tables.items(): df.to_csv(args.out/n,index=False,lineterminator='\n'); artifacts[n]={'rows':len(df),'sha256':sha(args.out/n),'bytes':(args.out/n).stat().st_size}
 summary={'task':'TASK-049-three-state-point-distribution','accepted_uncertainty_outputs':bool(gates.passed.all()),'uncertainty_status':'accepted' if gates.passed.all() else 'blocked','failed_gates':gates.loc[~gates.passed,'gate'].astype(int).tolist(),'bootstrap_seed':BOOTSTRAP_SEED,'bootstrap_replications':BOOTSTRAP_REPLICATIONS,'rows_per_model':{str(k):int(v) for k,v in allp.groupby('model').size().items()},'player_origin_snapshots':int(targets[KEY[:2]].drop_duplicates().shape[0]),'folds':int(targets[['origin_year','lead']].drop_duplicates().shape[0]),'primary_mean_pinball':primary.to_dict('records'),'input_hashes':{'baseline':sha(args.baseline),'candidate':sha(args.candidate),'targets':sha(args.targets),'features':sha(args.features)},'artifacts':artifacts,'recommended_next_hypothesis':None if gates.passed.all() else 'Audit whether the moment-preserving short-season mixture needs a predeclared distribution-shape repair; do not tune TASK-049.'}
 (args.out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); (args.out/'README.md').write_text('# TASK-049 three-state point distribution\n\nConcise locked evidence in CSV files and summary.json.\n'); print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
