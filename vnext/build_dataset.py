"""Build strict as-of player-season rows and fully observable future targets."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from snapshot import build_snapshot, season_at


def build_rows(players, min_origin=2008, max_origin=2025):
    rows=[]
    for p in players:
        try: dy=int(p.get('year'))
        except (TypeError, ValueError): continue
        for y in range(max(min_origin, dy), max_origin+1):
            s=build_snapshot(p,y)
            if s is None: continue
            d=s.to_dict()
            n1=season_at(p,y+1)
            d.update({
                'target_year': y+1,
                'next_games': n1['games'],
                'next_avg': n1['avg'],
                'next_meaningful': int(n1['games']>=6),
                'next_points': n1['avg']*n1['games'],
                'next_90': int(n1['games']>=6 and n1['avg']>=90),
                'next_100': int(n1['games']>=6 and n1['avg']>=100),
                'next_110': int(n1['games']>=6 and n1['avg']>=110),
            })
            # Fully observed fixed-horizon targets. Zero seasons remain zero.
            for h in (3,5):
                fut=[season_at(p,yy) for yy in range(y+1,y+h+1)]
                d[f'h{h}_games']=sum(r['games'] for r in fut)
                d[f'h{h}_points']=sum(r['avg']*r['games'] for r in fut)
                d[f'h{h}_best_avg']=max((r['avg'] for r in fut if r['games']>=6), default=0.0)
                d[f'h{h}_meaningful_seasons']=sum(r['games']>=6 for r in fut)
            rows.append(d)
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--min-origin', type=int, default=2008)
    ap.add_argument('--max-origin', type=int, default=2025)
    a=ap.parse_args()
    players=json.load(open(a.data))
    df=build_rows(players,a.min_origin,a.max_origin)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(a.out,index=False)
    print(json.dumps({'rows':len(df),'players':df.key.nunique(),'origins':[int(df.origin_year.min()),int(df.origin_year.max())]},indent=2))
if __name__=='__main__': main()
