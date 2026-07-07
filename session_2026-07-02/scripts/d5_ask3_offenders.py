#!/usr/bin/env python3
# D5 ASK 3a/3b — B5 offender evidence package (derive + show, wire NOTHING).
# 3a: FULL offender table at head (51), split dev-window vs deep tail.
# 3b: the candidate joiners (82-51) with per-term attribution from the ASK-2 term-off offender sets.
import json, sys, hashlib

S = sys.argv[1]
M = {k: json.load(open(f'{S}/meas_{k}.json')) for k in ['head', 'candidate', 'm1off', 'cboff', 'ascoff', 'm2off']}
def keyed(m):
    return {(r['player'], r['year'], r['pick']): r for r in m['b5_offenders']}
H, C = keyed(M['head']), keyed(M['candidate'])
OFFSETS = {t: set(keyed(M[t])) for t in ['m1off', 'cboff', 'ascoff', 'm2off']}
TN = dict(m1off='M1', cboff='v7-cB', ascoff='v7-asc', m2off='M2')

def fmt(r, extra=''):
    return (f"| {r['player']} | {r['club'] or '—'} | {r['yis']} | {r['type']} | {r['ev']:.0f} | "
            f"{r['draftval']:.0f} | {r['ratio']:.3f} | {r['floor_frac']:.2f}x = {r['floor']:.0f} | "
            f"{r['margin']:.0f} |{extra}")

L = []
L.append('# D5 ASK 3 — B5 EVIDENCE PACKAGE (offender tables; derive + show, NOTHING WIRED)')
L.append(f"_Head `8aed420a` store `644d1254` — {M['head']['b5_count']} offenders under the signed year-schedule "
         f"(yrs1-7+ .45/.35/.28/.21/.13/.09/.05 × draftval, ND-only listed). Candidate `fb39d88a` — "
         f"{M['candidate']['b5_count']} offenders. Columns per the directive; margin = value − floor (negative = breach depth)._")
L.append('')

hd = '| player | club | yrs-in-system | entrant type | current value | draft-day value | ratio | floor breached | margin |'
sep = '|---|---|---|---|---|---|---|---|---|'
dev = sorted((r for r in H.values() if r['yis'] <= 8), key=lambda r: (r['yis'], r['margin']))
tail = sorted((r for r in H.values() if r['yis'] >= 9), key=lambda r: (r['yis'], r['margin']))
L.append(f'## 3a — FULL offender table at head: DEV-WINDOW bucket (yrs 1-8, n={len(dev)}) — the signal Luke eyeballs')
L.append(hd); L.append(sep)
for r in dev:
    L.append(fmt(r))
L.append('')
L.append(f'## 3a — FULL offender table at head: DEEP-VETERAN TAIL bucket (yrs 9+, n={len(tail)}) — the .05-forever artifact zone')
L.append(hd); L.append(sep)
for r in tail:
    L.append(fmt(r))
L.append('')

join = sorted((C[k] for k in C if k not in H), key=lambda r: (r['yis'], r['margin']))
leave = [H[k] for k in H if k not in C]
L.append(f'## 3b — CANDIDATE DELTA: the {len(join)} players who JOIN at the candidate '
         f'({M["candidate"]["b5_count"]}−{M["head"]["b5_count"]}; leavers: {len(leave)})')
L.append('_Attribution: a joiner is attributed to the term(s) whose individual OFF-toggle rescues them '
         '(they leave the offender set when that one term is turned off). "joint" = no single term rescues._')
L.append(hd + ' pushed under by |')
L.append(sep + '---|')
attr_count = {}
for r in join:
    k = (r['player'], r['year'], r['pick'])
    rescuers = [TN[t] for t in ['m1off', 'cboff', 'ascoff', 'm2off'] if k not in OFFSETS[t]]
    lab = ' + '.join(rescuers) if rescuers else 'joint (no single term rescues)'
    attr_count[lab] = attr_count.get(lab, 0) + 1
    L.append(fmt(r, f' {lab} |'))
L.append('')
L.append('### Joiner attribution summary')
L.append('| pushed under by | n |')
L.append('|---|---|')
for lab, n in sorted(attr_count.items(), key=lambda t: -t[1]):
    L.append(f'| {lab} | {n} |')
if leave:
    L.append('')
    L.append(f'### Leavers at the candidate (offenders at head, cleared by the overlay): ' +
             ', '.join(f"{r['player']} (yr{r['yis']})" for r in sorted(leave, key=lambda r: r['yis'])))

out = '/home/user/afl-rl-engine/session_2026-07-02/d5_ask3_b5_offenders.md'
open(out, 'w').write('\n'.join(L) + '\n')
print(f"3a: dev-window n={len(dev)} / deep tail n={len(tail)} (total {len(H)})")
print(f"3b: joiners n={len(join)} leavers n={len(leave)}")
print('attribution:', json.dumps(attr_count))
print('wrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
