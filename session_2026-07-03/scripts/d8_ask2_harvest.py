#!/usr/bin/env python3
# D8 ASK 2a — HISTORICAL HARVEST for the GRADED staleness-cap derivation (one engine load; scratch,
# wires nothing). For every historical (player, Y) cell where the stalled branch WOULD fire
# (ns(Y)==1, el>=onset, listed at Y), record the live-output evidence at Y and the REALIZED forward
# outcome after Y. The graded rule's grade(E) is fit on these cells offline.
#
# CONVENTIONS (all standing, none invented here):
#  - qualifying season = >=6 games (the store's own bar, as in nseas()).
#  - era adjustment = avg * REF/era[year] (the engine's own bestlvl() convention).
#  - position group + REPL = MA.gfut / MA.REPL (the engine's own pricing convention).
#  - listed-at-Y (historical listing windows are NOT in the store) = the LISTED-WINDOW rule
#    (CHANGELOG 2026-06-29 book-bust-timing entry): off_board = max(min-listed-window, last game
#    year); min window ND pick<=20 -> 4 list-years, ND 21-40 -> 3, everything else (incl MSD
#    "draft+1", RD/PSD/PDx/SSP/IRE) -> 2. Concrete beats inferred: _last_listed used where present;
#    still-listed (non-retired, no _last_listed) -> 2026. DECLARED BIAS: for g_Y=0 ghost cells the
#    inferred window is a floor on true listing — cells beyond the window with no later games are
#    invisible; direction = the E=0 bin leans on min-window survivors (see analysis notes).
#  - evidence E = g_Y * (era-adjusted avg_Y / REPL[pos]) — games of replacement-equivalent output in
#    season Y ("current output vs replacement x games of evidence", the directive's axis). g_Y=0 -> 0.
#  - outcome window = the 3 seasons after Y (Y+1..Y+3), the same horizon family as prior realised-
#    forward derivations (E[fwdPeak] N=3/4/5/6, decliner shed). P_fwd = max era-adjusted avg over
#    QUALIFYING (>=6g) seasons in the window, 0 if none. rr = P_fwd / era-adjusted qual level.
#    Primary per-cell outcome v = min(rr, 1) — re-realization fraction of the stale level, capped at
#    full (beyond-full realization cannot earn more than full release; structural, not tuned).
#    Alternates recorded for robustness: surv (any qualifying season in window), raw rr.
#  - cells harvested Y=2008..2025; PRIMARY FIT Y<=2022 (complete 3yr window on complete seasons);
#    later cells carried with window_complete=False for robustness only.
import os, sys, io, json, hashlib, contextlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
outp = os.path.abspath(sys.argv[1])
os.chdir(RA)
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
MA, PR, era, REF = G['MA'], G['PR'], G['era'], G['REF']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]

def min_window(p):
    t, pk = p.get('type'), p.get('pick')
    if t == 'ND' and pk and pk <= 20: return 4
    if t == 'ND' and pk and pk <= 40: return 3
    return 2

def listed_through(p):
    if p.get('_last_listed') is not None:
        return int(p['_last_listed'])
    if not p.get('_retired'):
        return 2026
    lg = max((x['year'] for x in p['scoring']), default=0)
    dy = p.get('year') or lg
    return max(dy + min_window(p) - 1, lg)

cells = []
skipped = dict(no_pos=0, no_year=0)
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_double_count'):
            continue
        dy = p.get('year')
        if not dy:
            skipped['no_year'] += 1; continue
        try:
            pos = MA.gfut(p)
        except Exception:
            skipped['no_pos'] += 1; continue
        repl = float(MA.REPL.get(pos, 0.0))
        if repl <= 0:
            skipped['no_pos'] += 1; continue
        keyruc = pos in ('KEY_FWD', 'KEY_DEF', 'RUC')
        onset = 4 if keyruc else 3
        lt = listed_through(p)
        rows = sorted(p['scoring'], key=lambda x: x['year'])
        for Y in range(2008, 2026):
            if Y > lt or Y < dy:
                continue
            quals = [x for x in rows if x['games'] >= 6 and x['year'] <= Y]
            if len(quals) != 1:
                continue
            el = PR.tenure(p, Y)
            if el < onset:
                continue
            q = quals[0]
            adjq = REF / era.get(q['year'], REF)
            qual_lvl = q['avg'] * adjq
            yrow = [x for x in rows if x['year'] == Y]
            gY = yrow[0]['games'] if yrow else 0
            avgY = yrow[0]['avg'] if yrow else 0.0
            adjY = REF / era.get(Y, REF)
            qq = (avgY * adjY / repl) if gY > 0 else 0.0
            E = gY * qq
            fwd = [x for x in rows if x['games'] >= 6 and Y < x['year'] <= Y + 3]
            P_fwd = max((x['avg'] * REF / era.get(x['year'], REF) for x in fwd), default=0.0)
            rr = P_fwd / qual_lvl if qual_lvl > 0 else 0.0
            cells.append(dict(
                player=p['player'], key=f"{p['player']}|{dy}|{p.get('pick')}", Y=Y,
                pos=pos, type=p.get('type'), pick=p.get('pick'), keyruc=keyruc,
                el=int(el), onset=onset, gap=Y - q['year'],
                qual_year=q['year'], qual_g=q['games'], qual_lvl=round(qual_lvl, 2),
                qual_q=round(qual_lvl / repl, 4),
                gY=gY, avgY=round(avgY * adjY, 2), q=round(qq, 4), E=round(E, 4),
                nfwd=len(fwd), P_fwd=round(P_fwd, 2), rr=round(rr, 4),
                v=round(min(rr, 1.0), 4), surv=int(bool(fwd)),
                window_complete=bool(Y <= 2022)))
json.dump(dict(engine=ENG, n_cells=len(cells), skipped=skipped,
               meta=dict(era={str(k): v for k, v in era.items()}, REF=REF,
                         REPL=dict(MA.REPL)),
               cells=cells), open(outp, 'w'), indent=0)
n22 = sum(1 for c in cells if c['window_complete'])
np_ = len({c['key'] for c in cells})
print(f'engine={ENG} cells={len(cells)} (primary Y<=2022: {n22}) unique players={np_} skipped={skipped}')
from collections import Counter
print('by gap:', dict(sorted(Counter(c['gap'] for c in cells if c['window_complete']).items())))
print('gap>=1 by gY:', dict(sorted(Counter(c['gY'] for c in cells if c['window_complete'] and c['gap'] >= 1).items())))
print('wrote', outp, 'md5', hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8])
