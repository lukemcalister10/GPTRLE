#!/usr/bin/env python3
# D4 — one engine load: (a) B5 offender decomposition by years-in-system, (b) ASK 3e as-of-year spot tests.
import os, sys, io, json, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', os.path.join(ROOT, 'vendor')]
os.chdir(RA)

G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, draftval, delisted = G['ev'], G['MA'], G['draftval'], G['delisted']

FLOORS = {1: 0.45, 2: 0.35, 3: 0.28, 4: 0.21, 5: 0.13, 6: 0.09}
TAIL = 0.05
out = []
from collections import Counter
offs = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired') or p.get('_pickless') or delisted(p) or p.get('type') != 'ND':
            continue
        yis = 2026 - int(p.get('year') or 0)
        if yis < 1:
            continue
        try:
            v = float(ev(p, 2026))
        except Exception:
            continue
        fl = FLOORS.get(yis, TAIL)
        if v < fl * draftval(p):
            offs.append((p['player'], yis, v, fl * draftval(p)))
cnt = Counter(y for _, y, _, _ in offs)
out.append('B5 offender decomposition by years-in-system (n=%d):' % len(offs))
out.append('  ' + '  '.join(f'yr{y}:{cnt[y]}' for y in sorted(cnt)))
dev = [o for o in offs if o[1] <= 8]
out.append(f'  development-window (yrs1-8) offenders: {len(dev)}: ' + '; '.join(f'{n}(yr{y})={v:.0f}<{f:.0f}' for n, y, v, f in dev))
out.append(f'  deep-veteran (yr9+) offenders: {len(offs)-len(dev)}')

out.append('')
out.append('ASK 3e — as-of-year spot tests ev(p, Y) [engine answers the view question]:')
def by(name):
    hits = [p for p in MA.data if p['player'] == name]
    return hits[0] if len(hits) == 1 else None
with contextlib.redirect_stdout(io.StringIO()):
    for nm in ['Nick Daicos', 'Connor Rozee', 'Harry Sheezel', 'Josh Smillie', 'Sam Berry']:
        p = by(nm)
        if p is None:
            out.append(f'  {nm}: ambiguous/missing'); continue
        row = []
        for Y in (2024, 2025, 2026, 2027, 2028):
            try:
                row.append(f'{Y}={float(ev(p, Y)):.0f}')
            except Exception as ex:
                row.append(f'{Y}=ERR({type(ex).__name__})')
        out.append(f'  {nm:18s} ' + '  '.join(row))
    # back_extra (retired, -1/-2 views) — the delisted() hardcoded-2026 caveat
    bx = [p for p in MA.data if p.get('_retired')][:2]
    for p in bx:
        row = []
        for Y in (2024, 2025, 2026):
            try:
                row.append(f'{Y}={float(ev(p, Y)):.0f}')
            except Exception as ex:
                row.append(f'{Y}=ERR({type(ex).__name__})')
        out.append(f'  [retired] {p["player"]:18s} ' + '  '.join(row) + '   (delisted() hardcodes 2026 -> flat near-zero all views)')

txt = '\n'.join(out)
open(os.path.join(ROOT, 'session_2026-07-02', 'd4_b5_decomp_3e_spot.txt'), 'w').write(txt + '\n')
print(txt)
