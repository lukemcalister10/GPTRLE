from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from task003q_hybrid import blend_weight

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(); p.add_argument('--review-dir',type=Path,required=True); p.add_argument('--out',type=Path,required=True); a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
 cur=pd.read_csv(a.review_dir/'current_board_annual.csv'); hy=pd.read_csv(a.review_dir/'candidate_board_annual.csv'); checks=pd.read_csv(a.review_dir/'validation_checks.csv')
 m=cur.merge(hy,on=['stable_player_id','lead'],suffixes=('_current','_hybrid'),validate='one_to_one')
 expected=blend_weight(m.age_current.to_numpy(float),m.lead.to_numpy(int)); actual=m.task003q_weight.to_numpy(float)
 names=hy[hy.player_name.str.fullmatch('Max King|Maxwell King',case=False,na=False)]
 report={'players':int(hy.stable_player_id.nunique()),'rows':int(len(hy)),'five_leads_each':bool(hy.groupby('stable_player_id').lead.nunique().eq(5).all()),'duplicate_keys':int(hy.duplicated(['stable_player_id','lead']).sum()),'max_identity_separation':bool(names.stable_player_id.nunique()==2 and names.key.nunique()==2),'weight_mismatches':int((np.abs(expected-actual)>1e-12).sum()),'cond_games_mismatches':int((np.abs(m.cond_games_current-m.cond_games_hybrid)>1e-10).sum()),'cond_avg_mismatches':int((np.abs(m.cond_avg_current-m.cond_avg_hybrid)>1e-10).sum()),'exp_avg_mismatches':int((np.abs(m.exp_avg_current-m.exp_avg_hybrid)>1e-10).sum()),'validation_green':bool((checks.drop(columns=['model_id','players','rows','expected_rows'])==0).all().all() and (checks.players==804).all() and (checks.rows==4020).all())}
 report['status']='pass' if all([report['players']==804,report['rows']==4020,report['five_leads_each'],report['duplicate_keys']==0,report['max_identity_separation'],report['weight_mismatches']==0,report['cond_games_mismatches']==0,report['cond_avg_mismatches']==0,report['exp_avg_mismatches']==0,report['validation_green']]) else 'fail'
 cols=['stable_player_id','key','player_name','affl_team','eligibilities','position','age','lead','forecast_year','p_meaningful','exp_games','exp_avg','exp_points','cond_games','cond_avg','task003q_weight','p80','p90','p100','p110','p120']+[c for c in hy.columns if c.startswith('points_q')]
 hy[cols].sort_values(['stable_player_id','lead']).to_csv(a.out/'task003q_annual_forecast.csv',index=False)
 for name in ['player_rollup_rank_changes.csv','largest_changes.csv','slice_summary.csv','zero_history_players.csv','age30_plus_lead5.csv']:
  pd.read_csv(a.review_dir/name).to_csv(a.out/name,index=False)
 (a.out/'validation_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 dictionary={'stable_player_id':'authoritative join key; never join by name alone','p_meaningful':'meaningful-season probability','exp_games':'unconditional expected games; do not apply another survival factor','exp_points':'unconditional expected points; do not apply another survival factor','task003q_weight':'frozen TASK-003K blend weight'}
 (a.out/'data_dictionary.json').write_text(json.dumps(dictionary,indent=2,sort_keys=True)+'\n')
 files=[x for x in a.out.iterdir() if x.is_file()]
 manifest={'model':'TASK-003Q','origin_year':2026,'players':804,'rows':4020,'join_rule':'stable_player_id only','double_fade_warning':'Claude must not apply a second retirement or survival fade','identity_warning':'Max King and Maxwell King are distinct records','validation_status':report['status'],'files':{x.name:sha(x) for x in files}}
 (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,indent=2)); return 0 if report['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
