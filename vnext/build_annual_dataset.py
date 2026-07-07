"""Build leakage-safe annual lead targets (1-5 seasons) for trajectory modelling."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
from snapshot import build_snapshot, season_at


def build_rows(players,min_origin=2008,max_origin=2026,max_lead=5):
    rows=[]
    for p in players:
        try: dy=int(p.get('year'))
        except (TypeError,ValueError): continue
        for y in range(max(min_origin,dy),max_origin+1):
            s=build_snapshot(p,y)
            if s is None: continue
            d=s.to_dict()
            for lead in range(1,max_lead+1):
                r=season_at(p,y+lead)
                meaningful=int(r['games']>=6)
                d[f'l{lead}_games']=r['games']
                d[f'l{lead}_avg']=r['avg'] if meaningful else 0.0
                d[f'l{lead}_points']=r['avg']*r['games']
                d[f'l{lead}_meaningful']=meaningful
                for t in (80,90,100,110,120):
                    d[f'l{lead}_{t}']=int(meaningful and r['avg']>=t)
            rows.append(d)
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--min-origin',type=int,default=2008);ap.add_argument('--max-origin',type=int,default=2026)
    a=ap.parse_args();players=json.load(open(a.data));df=build_rows(players,a.min_origin,a.max_origin)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);df.to_csv(a.out,index=False)
    print(json.dumps({'rows':len(df),'players':int(df.key.nunique()),'origins':[int(df.origin_year.min()),int(df.origin_year.max())]},indent=2))
if __name__=='__main__':main()
