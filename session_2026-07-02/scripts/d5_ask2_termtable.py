#!/usr/bin/env python3
# D5 ASK 2 — assemble the per-term decomposition table from the sequential term-off runs.
# Inputs: meas_{head,candidate,m1off,cboff,ascoff,m2off}.json + s4_matrix_{m1off,cboff,ascoff}.json
#         + candidate/control matrices. All engine work already done sequentially; this is arithmetic.
import json, sys, hashlib
import numpy as np
from scipy.stats import spearmanr

S = sys.argv[1]
M = {k: json.load(open(f'{S}/meas_{k}.json')) for k in ['head', 'candidate', 'm1off', 'cboff', 'ascoff', 'm2off']}

MATS = dict(candidate=f'{S}/s4_matrix_candidate_fb39d88a.json',
            control='/home/user/afl-rl-engine/data/s4_matrix_control_8aed420a.json',
            m1off=f'{S}/s4_matrix_m1off.json', cboff=f'{S}/s4_matrix_cboff.json', ascoff=f'{S}/s4_matrix_ascoff.json')

def b1(mp):
    mat = json.load(open(mp))
    Ssum = {}
    for v in mat.values():
        C = int(v['year'])
        if not v['incurve'] or not (2004 <= C <= 2020):
            continue
        for i, _ in enumerate(v['yrs']):
            N = i + 1
            if N > 7:
                break
            Ssum[(C, N)] = Ssum.get((C, N), 0.0) + float(v['Vpath'][i] or 0.0)
    cs = sorted({c for c, _ in Ssum})
    R = {C: {N: 100.0 * Ssum[(C, N)] / max(Ssum[(C, 1)], 1e-9) for N in range(1, 8) if (C, N) in Ssum} for C in cs}
    AVG = {N: float(np.mean([R[C][N] for C in cs if N in R[C]])) for N in range(1, 8) if any(N in R[C] for C in cs)}
    ppk = max(AVG, key=AVG.get)
    path_ok = all(AVG[N + 1] >= 0.95 * AVG[N] for N in range(1, ppk) if N + 1 in AVG)
    ok = ppk in (4, 5, 6) and AVG[ppk] > 100.0 and path_ok
    return dict(AVG=AVG, ppk=ppk, ok=ok, R2020=R.get(2020, {}))

def coh2020(mp):
    mat = json.load(open(mp))
    out = {}
    for v in mat.values():
        if not v['incurve'] or int(v['year']) != 2020:
            continue
        k = (v['player'], round(float(v['pick']), 1))
        vp = v['Vpath']
        out[k] = sum(float(vp[i] or 0.0) for i in (3, 4, 5) if i < len(vp))
    return out

B1S = {k: b1(mp) for k, mp in MATS.items()}
C20 = {k: coh2020(mp) for k, mp in MATS.items()}

def conc(base, other):
    ks = sorted(base, key=lambda k: -base[k])
    rows = [(base[k], other.get(k, 0.0) - base[k]) for k in ks]
    sub = [(c, 100.0 * d / c) for c, d in rows if c > 0]
    rho, p = spearmanr([c for c, _ in sub], [d for _, d in sub])
    n = len(ks)
    q = max(1, n // 4)
    def blk(sl):
        c = sum(base[k] for k in sl); d = sum(other.get(k, 0.0) - base[k] for k in sl)
        return 100.0 * d / c if c else 0.0
    return dict(total=100.0 * sum(d for _, d in rows) / max(sum(c for c, _ in rows), 1e-9),
                top=blk(ks[:q]), mid=blk(ks[q:n - n // 2]), bot=blk(ks[n - n // 2:]), rho=float(rho), p=float(p))

# each term's OWN 2020 markdown = termoff-matrix -> candidate-matrix delta (turning the term back ON at the margin)
term_conc = {t: conc(C20[t], C20['candidate']) for t in ['m1off', 'cboff', 'ascoff']}
cand_conc = conc(C20['control'], C20['candidate'])

def row(label, key, note):
    m = M[key]
    b = B1S.get({'HEAD': None}.get(key, key))
    r20 = b['R2020'] if b else {}
    r20s = '/'.join(f"{r20[N]:.0f}" for N in (4, 5, 6) if N in r20) if r20 else '—'
    avg = b['AVG'] if b else {}
    avgs = ' '.join(f"{N}:{avg[N]:.0f}" for N in sorted(avg)) if avg else '—'
    nb1 = ('PASS' if b['ok'] else 'FAIL') + f" pk{b['ppk']} {avg[b['ppk']]:.1f}" if b else '—'
    return (f"| {label} | {m['a2_ratio']:.3f} ({m['named']['Paul Curtis']:.0f}/{m['named']['Josh Ward']:.0f}) "
            f"| {r20s} | {avgs} | {nb1} | {m['a3_ratio']:.3f} | {m['b5_count']} | {note} |")

L = []
L.append('# D5 ASK 2 — M1+v7 PER-TERM DECOMPOSITION (each term toggled OFF individually against the candidate basis)')
L.append('_Sequential term-off engine builds + same-builder (7147) matrix rebuilds. Terms of the overlay: '
         '**M1** = the level up-branch lift (`_inferM1`, S_M1=0.46 partial current-over-recency credit); '
         '**v7-cB** = upper-quantile band compression (cB=0.47·clip((effs−1)/3), squeezes bb[3]/bb[4] toward the median); '
         '**v7-asc** = age-scaled q97 tail (asc: 1.0@20y → 0.40@27y on bb[5]). M2 (exposure proration) rides in the '
         'candidate basis; its own toggle (RL_EXPO_F=1) shown as context. Nothing wired anywhere._')
L.append('')
L.append('## The term table (state = candidate with ONE term off; effect of a term = candidate row − its off row)')
L.append('| state | A2 Curtis/Ward | 2020 cohort d4/d5/d6 idx | new-B1 avg row (d1..d7) | new-B1 verdict | A3 (pre-LTI) | B5 count | note |')
L.append('|---|---|---|---|---|---|---|---|')
L.append(row('CANDIDATE (all on)', 'candidate', 'baseline'))
L.append(row('M1 OFF', 'm1off', 'M1 effect = Curtis +184 lift, A3 −0.034, 2020/B5 ~nil'))
L.append(row('v7-cB OFF', 'cboff', 'cB effect = the band squeeze: Curtis −195, Ward −324'))
L.append(row('v7-asc OFF', 'ascoff', 'asc effect = the age-tail markdown: 2020 + B5 owner'))
L.append(row('M2 OFF (RL_EXPO_F=1, context)', 'm2off', 'M2 effect = A3 +0.016, else ~nil'))
mh = M['head']
bh = B1S['control']
r20h = '/'.join(f"{bh['R2020'][N]:.0f}" for N in (4, 5, 6) if N in bh['R2020'])
avgh = ' '.join(f"{N}:{bh['AVG'][N]:.0f}" for N in sorted(bh['AVG']))
L.append(f"| CONTROL / HEAD (all off) | {mh['a2_ratio']:.3f} ({mh['named']['Paul Curtis']:.0f}/{mh['named']['Josh Ward']:.0f}) "
         f"| {r20h} | {avgh} | {('PASS' if bh['ok'] else 'FAIL')} pk{bh['ppk']} {bh['AVG'][bh['ppk']]:.1f} "
         f"| {mh['a3_ratio']:.3f} | {mh['b5_count']} | head engine, same-builder control matrix |")
L.append('')
L.append('## (b) WHO owns the 2020 markdown — per-term markdown on the 2020 cohort (d4-6 value, candidate vs each term-off matrix)')
L.append('| term (turned ON at the margin) | 2020 d4-6 markdown | markdown % on top-quartile | middle | bottom half | Spearman(value, Δ%) |')
L.append('|---|---|---|---|---|---|')
NAMES = dict(m1off='M1', cboff='v7-cB', ascoff='v7-asc')
for t in ['m1off', 'cboff', 'ascoff']:
    c = term_conc[t]
    L.append(f"| {NAMES[t]} | {c['total']:+.1f}% | {c['top']:+.1f}% | {c['mid']:+.1f}% | {c['bot']:+.1f}% | {c['rho']:+.3f} (p={c['p']:.2g}) |")
c = cand_conc
L.append(f"| WHOLE OVERLAY (control → candidate) | {c['total']:+.1f}% | {c['top']:+.1f}% | {c['mid']:+.1f}% | {c['bot']:+.1f}% | {c['rho']:+.3f} (p={c['p']:.2g}) |")
out = '/home/user/afl-rl-engine/session_2026-07-02/d5_ask2_term_table.md'
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
print('\nwrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
