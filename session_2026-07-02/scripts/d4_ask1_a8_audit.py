#!/usr/bin/env python3
# D4 ASK1 — A8 audit: print the ACTUAL scripted expression + threshold, evaluate both paths,
# and give Luke's literal-2x arithmetic against the raw values. Label comes from this printout only.
import os, sys, io, json, contextlib, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', os.path.join(ROOT, 'vendor')]
os.chdir(RA)

out = []
out.append('=== A8 AUDIT — scripted expression as committed (ship_gates_check.py) ===')
src = open(os.path.join(ROOT, 'ship_gates_check.py')).read().splitlines()
for i, ln in enumerate(src, 1):
    if 'A8' in ln or ("Sam Berry" in ln and 'Tsatas' in ln):
        out.append(f'  L{i}: {ln.strip()}')

G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA = G['ev'], G['MA']

def E(name, yr=2026):
    hits = [p for p in MA.data if p['player'] == name and not p.get('_retired')]
    assert len(hits) == 1, f'{name}: {len(hits)} hits'
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(hits[0], yr))

b, t = E('Sam Berry'), E('Elijah Tsatas')
out.append('')
out.append('=== ENGINE PATH (head) — raw values ===')
out.append(f'  ev(Sam Berry, 2026)      = {b:.1f}')
out.append(f'  ev(Elijah Tsatas, 2026)  = {t:.1f}')
out.append(f'  2 x Tsatas               = {2*t:.1f}')
out.append(f'  literal 2x test  (b >= 2t)        : {b:.0f} >= {2*t:.0f} -> {"PASS" if b >= 2*t else "FAIL"}')
out.append(f'  scripted test    (b >  2t)        : {b:.0f} >  {2*t:.0f} -> {"PASS" if b >  2*t else "FAIL"}')
out.append(f'  20%-tolerance variant (b > 1.6t)  : {b:.0f} >  {1.6*t:.0f} -> {"PASS" if b > 1.6*t else "FAIL"}')
out.append(f'  Luke arithmetic (reads report pair "3473 vs 2166" as Berry vs RAW Tsatas): 2x2166={2*2166} > 3473 -> that reading fails')
out.append(f'  report display check: last board printed "Berry=3473 vs 2x Tsatas=2166 (Tsatas=1083)" — 2166 IS 2xTsatas in that string')

# BOARD PATH — from the D3 board dump (TR.production_value), no re-export needed
bp = os.path.join(ROOT, 'session_2026-07-02', 'scripts', 'd3_ask1_board_out.json')
out.append('')
out.append('=== BOARD PATH (D3 dump, TR.production_value) ===')
try:
    d = json.load(open(bp))
    vals = None
    # search structure for per-player board values
    def find_players(o, depth=0):
        if depth > 4: return None
        if isinstance(o, dict):
            if 'Sam Berry' in o: return o
            for v in o.values():
                r = find_players(v, depth+1)
                if r is not None: return r
        return None
    m = find_players(d)
    if m:
        bb, bt = float(m['Sam Berry']), float(m['Elijah Tsatas'])
        out.append(f'  board Berry={bb:.1f}  board Tsatas={bt:.1f}  2x Tsatas={2*bt:.1f}')
        out.append(f'  literal 2x on board: {"PASS" if bb >= 2*bt else "FAIL"}')
    else:
        out.append(f'  (no per-player map found in {os.path.basename(bp)} — keys: {list(d)[:8] if isinstance(d, dict) else type(d)})')
except Exception as ex:
    out.append(f'  board dump unreadable: {ex}')

txt = '\n'.join(out)
rep = os.path.join(ROOT, 'session_2026-07-02', 'd4_a8_audit.txt')
open(rep, 'w').write(txt + '\n')
print(txt)
print(f'\nwritten: {rep}')
