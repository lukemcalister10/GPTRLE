#!/usr/bin/env python3
# D5 ASK 1 — measure NEW-B1 (Luke's redefinition, 02/07/2026) at three states, side by side.
# Matrix-only computation (B1 never loads the engine); the math REPLICATES ship_gates_check.py's
# rebuilt B1 block verbatim (cross-cohort UNWEIGHTED AVERAGE of indexed cohort value, cohorts
# 2004-2020 incurve, depth 1-7; PASS = avg peak in yrs 4-6, >100, pre-peak dips of the avg <5%).
import json, os, sys, hashlib
import numpy as np

SCRATCH = sys.argv[1] if len(sys.argv) > 1 else '.'
STATES = [
    ('canonical head 8aed420a (gate-default matrix)', '/home/user/afl-rl-engine/data/s4_matrix_nogames.json'),
    ('candidate fb39d88a (M2+M1v7, same-builder)', os.path.join(SCRATCH, 's4_matrix_candidate_fb39d88a.json')),
    ('fix-off control (canonical engine, same-builder — D4 ASK-4 control)', '/home/user/afl-rl-engine/data/s4_matrix_control_8aed420a.json'),
]

def newB1(mpath):
    mat = json.load(open(mpath))
    S = {}
    for v in mat.values():
        C = int(v['year'])
        if not v['incurve'] or not (2004 <= C <= 2020):
            continue
        for i, _yy in enumerate(v['yrs']):
            N = i + 1
            if N > 7:
                break
            S[(C, N)] = S.get((C, N), 0.0) + float(v['Vpath'][i] or 0.0)
    cohorts = sorted({c for c, _ in S})
    R = {C: {N: 100.0 * S[(C, N)] / max(S[(C, 1)], 1e-9) for N in range(1, 8) if (C, N) in S} for C in cohorts}
    AVG = {N: float(np.mean([R[C][N] for C in cohorts if N in R[C]]))
           for N in range(1, 8) if any(N in R[C] for C in cohorts)}
    ppk = max(AVG, key=AVG.get)
    path_ok = all(AVG[N + 1] >= 0.95 * AVG[N] for N in range(1, ppk) if N + 1 in AVG)
    ok = ppk in (4, 5, 6) and AVG[ppk] > 100.0 and path_ok
    return dict(R=R, AVG=AVG, ppk=ppk, path_ok=path_ok, ok=ok, cohorts=cohorts,
                md5=hashlib.md5(open(mpath, 'rb').read()).hexdigest()[:8], base=os.path.basename(mpath))

res = [(label, newB1(mp)) for label, mp in STATES]
L = []
L.append('# D5 ASK 1 — NEW-B1 (cross-cohort AVERAGE law, Luke redefinition 02/07/2026) at three states')
L.append('_Gate: at each year-depth d, unweighted mean of indexed cohort value (yr1=100) across cohorts observed at d '
         'must rise from yr1 to a peak in yrs 4-6; pre-peak dips of the AVERAGE <5% tolerated. Per-cohort UNGATED._')
L.append('')
L.append('## Year-depth AVERAGE table — side by side (the gated row per state)')
L.append('| state | matrix md5 | d1 | d2 | d3 | d4 | d5 | d6 | d7 | peakN | path_ok | NEW-B1 |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
for label, r in res:
    row = ' | '.join((f"{r['AVG'][N]:.1f}" if N in r['AVG'] else '—') for N in range(1, 8))
    L.append(f"| {label} | `{r['md5']}` | {row} | {r['ppk']} | {r['path_ok']} | "
             f"{'**PASS**' if r['ok'] else '**FAIL**'} |")
L.append('')
L.append('## The 2020 cohort row, explicitly (UNGATED under the new law — Luke eyeball channel)')
L.append('| state | d1 | d2 | d3 | d4 | d5 | d6 | d7 | peakN | rises above yr1 in yrs4-6? |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
for label, r in res:
    c = r['R'].get(2020, {})
    row = ' | '.join((f'{c[N]:.0f}' if N in c else '—') for N in range(1, 8))
    pk = max(c, key=c.get) if c else '—'
    rise = 'YES' if c and max(c.get(N, 0) for N in (4, 5, 6)) > 100.0 else 'NO'
    L.append(f'| {label} | {row} | {pk} | {rise} |')
L.append('')
L.append('## Full per-cohort index tables (UNGATED)')
for label, r in res:
    L.append(f'\n### {label} — matrix `{r["base"]}` md5 `{r["md5"]}`')
    L.append('| cohort | peakN | d1 | d2 | d3 | d4 | d5 | d6 | d7 |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for C in r['cohorts']:
        c = r['R'][C]
        pk = max(c, key=c.get)
        L.append(f'| {C} | {pk} | ' + ' | '.join((f'{c[N]:.0f}' if N in c else '—') for N in range(1, 8)) + ' |')
    a = r['AVG']
    L.append(f"| **AVG (gated)** | **{r['ppk']}** | " +
             ' | '.join((f'**{a[N]:.1f}**' if N in a else '—') for N in range(1, 8)) + ' |')

out = '/home/user/afl-rl-engine/session_2026-07-02/d5_ask1_newB1_three_states.md'
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:22]))
print('...')
for label, r in res:
    print(f"VERDICT {label}: {'PASS' if r['ok'] else 'FAIL'} (peak N={r['ppk']} AVG={r['AVG'][r['ppk']]:.1f} path_ok={r['path_ok']})")
print('wrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
