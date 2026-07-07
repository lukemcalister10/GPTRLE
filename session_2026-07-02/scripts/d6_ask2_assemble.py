#!/usr/bin/env python3
# D6 ASK 2b/2c — assemble the floor-saves tables (both variants) + the new-B1 re-print under the
# clamp. Pure post-processing: inputs are the verified clamp run + head meas + the LTI register +
# the head gate-default matrix. No engine load.
import json, re, sys, hashlib
import numpy as np

SCR = sys.argv[1]
REPO = '/home/user/afl-rl-engine'
VER = json.load(open(f'{SCR}/verify_clamp.json'))
MEAS = json.load(open(f'{SCR}/meas_head_d6.json'))
ROWS = {r['player']: r for r in MEAS['clean_rows']}

# ---- register: Section A (LTI) + Section B (OUT-2026) ----
reg = {}
txt = open(f'{REPO}/LTI_REGISTER_2026-07-02.md').read()
secA = txt.split('## SECTION A')[1].split('## SECTION B')[0]
for m in re.finditer(r'^\| ([^|]+) \| ([^|]+) \|', secA, re.M):
    nm = m.group(1).strip()
    if nm != 'player':
        reg[nm] = f'LTI ({m.group(2).strip()})'
secB = txt.split('## SECTION B')[1].split('---')[0]
for nm in re.findall(r'[A-Z][\w\'\-\.]+(?: [A-Z][\w\'\-\.]+)+', secB.replace('**', '')):
    reg.setdefault(nm, 'OUT-2026')
def regstat(nm):
    return reg.get(nm, 'clear')

# ---- floor schedule (mirror of the prototype) ----
DEV = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}
def floor_yrs(yis, variant):
    if yis in DEV: return DEV[yis]
    if variant == 'A': return 0.05
    return {7: .05, 8: .011, 9: .012, 10: .021}.get(yis, .012)

L = []
L.append('# D6 ASK 2 — FLOOR-AS-PRICING-FEATURE PROTOTYPE (Luke\'s ruling; BOTH tail variants)')
L.append(f"_Head `8aed420a` store `644d1254` · prototype `engine/prototypes/floor_pricing_clamp.py` md5 `{VER['proto_md5']}` · "
         "ev_final(p) = max(ev(p), floor_yrs(p)·draftval(p)) · ND entrants only (MSD/SSP + delisted/retired/pickless excluded) · "
         "variant A tail = flat .05 yrs 7+ (as signed) · variant B tail = yr7 .05 then D5 ASK-3c kernel floors d8 .011 / d9 .012 / d10 .021 / d11+ .012._")
L.append('')
for variant in ('A', 'B'):
    V = VER['variants'][variant]
    saves = sorted(V['saves'], key=lambda s: -s['lift'])
    L.append(f"## 2b — FLOOR-SAVES TABLE, variant {variant} ({'flat .05 tail' if variant=='A' else 'derived kernel tail'}) — "
             f"saves = {V['n_saves']} · aggregate value added = {V['agg_lift']:.0f}")
    L.append('| player | club | yrs-in-system | raw ev | floor value | saved-to value | lift | register status |')
    L.append('|---|---|---|---|---|---|---|---|')
    for s in saves:
        r = ROWS.get(s['player'], {})
        L.append(f"| {s['player']} | {r.get('club','—')} | {s['yis']} | {s['raw']:.0f} | {s['floor']:.1f} | "
                 f"{s['saved_to']} | +{s['lift']:.0f} | {regstat(s['player'])} |")
    saved_names = {s['player'] for s in saves}
    for nm in ('Nick Haynes', 'Jacob Hopper'):
        if nm not in saved_names:
            r = ROWS[nm]
            fl = floor_yrs(r['yis'], variant) * r['draftval']
            L.append(f"| {nm} (NOT saved under {variant}) | {r['club']} | {r['yis']} | {r['ev']:.0f} | {fl:.1f} | "
                     f"— (ev ≥ floor) | 0 | {regstat(nm)} |")
    top5 = ', '.join(f"{s['player']} +{s['lift']:.0f}" for s in saves[:5])
    L.append(f"- 5 largest lifts: {top5}")
    L.append(f"- verified pure lower bound (wired-run, full population n={V['n_all']}): byte-identical={V['n_same']}, "
             f"lifted={V['n_up']}, lowered={V['n_down']} (bar 0), non-ND moved={V['n_nonnd_moved']} (bar 0). "
             f"saves-collector {V['n_saves']} vs integer lifts {V['n_up']}: the difference is rounding "
             f"(sub-1pt margins land on the same integer).")
    L.append('')

# ---- 2c: new-B1 average curve under the clamp ----
mat = json.load(open(f'{REPO}/data/s4_matrix_nogames.json'))
def b1(clamp=None, skip_delist=True):
    Ssum = {}
    for v in mat.values():
        if not v['incurve'] or not (2004 <= int(v['year']) <= 2020):
            continue
        dv = float(v.get('draftval') or 0.0)
        nd = (v.get('type') == 'ND') and not v.get('pickless')
        for i, _ in enumerate(v['yrs']):
            N = i + 1
            if N > 7:
                break
            val = float(v['Vpath'][i] or 0.0)
            if clamp and nd and dv > 0:
                delist_cell = val <= 0.02 * dv + 0.5
                if not (skip_delist and delist_cell):
                    val = max(val, floor_yrs(N, clamp) * dv)
            Ssum[(int(v['year']), N)] = Ssum.get((int(v['year']), N), 0.0) + val
    cs = sorted({c for c, _ in Ssum})
    R = {C: {N: 100.0 * Ssum[(C, N)] / max(Ssum[(C, 1)], 1e-9) for N in range(1, 8) if (C, N) in Ssum} for C in cs}
    AVG = {N: float(np.mean([R[C][N] for C in cs if N in R[C]])) for N in range(1, 8)}
    ppk = max(AVG, key=AVG.get)
    path_ok = all(AVG[N + 1] >= 0.95 * AVG[N] for N in range(1, ppk) if N + 1 in AVG)
    ok = ppk in (4, 5, 6) and AVG[ppk] > 100.0 and path_ok
    return AVG, ppk, ok, path_ok

L.append('## 2c — new-B1 AVERAGE curve re-printed under the clamp (gate-default head matrix `s4_matrix_nogames.json`)')
L.append('_B1 evaluates depths 1-7 only and variants A/B share the schedule through yr7 — the clamped B1 curve is '
         'IDENTICAL for both variants by construction (they diverge at d8+, outside B1\'s window). Delist-fingerprint '
         'cells (v ≤ 0.02·draftval — the delist gate) are NOT clamped, per the floor\'s own delisted-exclusion; '
         'the no-skip variant shown as sensitivity._')
L.append('| state | d1 | d2 | d3 | d4 | d5 | d6 | d7 | peakN | path_ok | NEW-B1 |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|')
for lab, kw in [('head unclamped (reference)', dict(clamp=None)),
                ('head + floor clamp (A ≡ B), delisted cells excluded', dict(clamp='A', skip_delist=True)),
                ('sensitivity: clamp incl. delisted cells (not the rule)', dict(clamp='A', skip_delist=False))]:
    AVG, ppk, ok, path_ok = b1(**kw)
    row = ' | '.join(f"{AVG[N]:.1f}" for N in range(1, 8))
    L.append(f"| {lab} | {row} | {ppk} | {path_ok} | {'**PASS**' if ok else '**FAIL**'} |")
out = f'{REPO}/session_2026-07-02/d6_ask2_floor_saves.md'
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[-8:]))
print('\nwrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
