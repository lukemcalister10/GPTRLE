"""DIAG-B rev3 — matrix-side analysis (ASK 3 / ASK 4 / ASK 5a) from the v2 walk-forward matrix.
READ-ONLY: reads data/s4_matrix_v2_4a134d05.json; writes session_2026-07-03/d8_matrix_analysis.md.
Run from repo root: python3 session_2026-07-03/scripts/d8_matrix_analysis.py
"""
import json, collections, numpy as np
rec = json.load(open('data/s4_matrix_v2_4a134d05.json')); R = list(rec.values())
INCURVE = {'ND', 'RD'}
bycoh = collections.defaultdict(list)
for r in R:
    if r['type'] in INCURVE and r['year']: bycoh[r['year']].append(r)
def num(v): return isinstance(v, (int, float))
def cur_disp(x): return 0 if x.get('retired_now') else (x['cur'] or 0)

GMAX = max(len(x['Vpath']) for C in bycoh for x in bycoh[C])
def m1_row(C):
    ic = bycoh[C]; denom = sum(x['anchor'] for x in ic if num(x['anchor']))
    row = []
    for k in range(1, GMAX + 1):
        vals = [x['Vpath'][k-1] for x in ic if len(x['Vpath']) >= k and num(x['Vpath'][k-1])]
        row.append(100 * sum(vals) / denom if (vals and denom) else None)
    return row, denom

VIEWS = {'FULL HISTORY (2004-2024)': list(range(2004, 2025)),
         '2015-2024 WINDOW': list(range(2015, 2025))}
out = []
out.append('# DIAG-B rev3 — matrix-side analysis (v2 matrix s4_matrix_v2_4a134d05.json)\n')

# ---- ASK 4: overall Measure-1 mean row, slopes, peak — both views ----
out.append('## ASK 4 — cross-cohort Measure-1 mean (Yr-k as % of own end-of-Yr1), slopes, peak\n')
slopes_tbl = ['| view | yr1->2 slope (pp) | yr4->5 slope (pp) | peak yr | peak value | peaks in yrs 4-6? |', '|---|---|---|---|---|---|']
for vname, cohorts in VIEWS.items():
    percoh = {C: m1_row(C)[0] for C in cohorts}
    mean_row = []
    for k in range(GMAX):
        col = [percoh[C][k] for C in cohorts if percoh[C][k] is not None]
        mean_row.append(float(np.mean(col)) if len(col) >= 5 else None)
    # per-cohort slopes (mean of per-cohort deltas, cohorts with both points)
    s12 = [percoh[C][1] - percoh[C][0] for C in cohorts if percoh[C][0] is not None and percoh[C][1] is not None]
    s45 = [percoh[C][4] - percoh[C][3] for C in cohorts if percoh[C][3] is not None and percoh[C][4] is not None]
    valid = [(k, v) for k, v in enumerate(mean_row) if v is not None]
    pk_k, pk_v = max(valid, key=lambda t: t[1])
    out.append(f'### {vname}')
    out.append('| Yr | ' + ' | '.join(str(k+1) for k, _ in valid) + ' |')
    out.append('|---|' + '---|' * len(valid))
    out.append('| mean % of own Yr1 | ' + ' | '.join(f'{v:.0f}%' for _, v in valid) + ' |')
    out.append(f'- mean yr1->2 slope: **{np.mean(s12):+.1f} pp** (n={len(s12)} cohorts) · mean yr4->5 slope: **{np.mean(s45):+.1f} pp** (n={len(s45)})')
    out.append(f'- OVERALL-row peak: **Yr {pk_k+1} at {pk_v:.0f}%** -> peaks in yrs 4-6: **{"YES" if 4 <= pk_k+1 <= 6 else "NO"}**\n')
    slopes_tbl.append(f'| {vname} | {np.mean(s12):+.1f} | {np.mean(s45):+.1f} | Yr {pk_k+1} | {pk_v:.0f}% | {"YES" if 4 <= pk_k+1 <= 6 else "NO"} |')
out.append('### slopes/peak summary')
out.extend(slopes_tbl)

# ---- ASK 3: the 2020 test ----
out.append('\n## ASK 3 — 2020 cohort: current total vs draft-day pick sum (engine PVC, as stored per-player in the matrix)\n')
ic20 = bycoh[2020]
cur20 = sum(cur_disp(x) for x in ic20)
dv20 = sum(x['draftval'] or 0 for x in ic20)
a20 = sum(x['anchor'] or 0 for x in ic20)
r20, _ = m1_row(2020)
out.append(f'- 2020 ND+RD n={len(ic20)} · current SUM (retired=0) = **{round(cur20)}** · draft-day pick-value SUM = **{round(dv20)}**')
out.append(f'- **ratio current/pick-sum = {100*cur20/dv20:.1f}%** -> verdict: **{"ABOVE" if cur20 > dv20 else "NOT above"} 100%**')
out.append(f'- for contrast, Measure-1 Current (vs its OWN end-of-Yr1 total {round(a20)}) = **{100*cur20/a20:.0f}%** — this is the number that reads >100% in TABLE 1')
out.append('- 2020 per-cohort Measure-1 curve (% of own Yr1):')
vals = [(k+1, v) for k, v in enumerate(r20) if v is not None]
out.append('| Yr | ' + ' | '.join(str(k) for k, _ in vals) + ' | Current |')
out.append('|---|' + '---|' * (len(vals) + 1))
out.append('| 2020 | ' + ' | '.join(f'{v:.0f}%' for _, v in vals) + f' | {100*cur20/a20:.0f}% |')

# ---- ASK 5a: the 2025 shortfall ----
out.append('\n## ASK 5a — 2025 cohort Yr1 vs prior cohorts END-of-Yr1\n')
anchors = {C: m1_row(C)[1] for C in bycoh}
dvs = {C: sum(x['draftval'] or 0 for x in bycoh[C]) for C in bycoh}
a25 = anchors[2025]; dv25 = dvs[2025]
prior = list(range(2004, 2025)); rec5 = list(range(2020, 2025))
mean_all = np.mean([anchors[C] for C in prior]); mean_r5 = np.mean([anchors[C] for C in rec5])
out.append('| measure | value |', )
out.append('|---|---|')
out.append(f'| 2025 Yr1 SUM (n=64 ND+RD, at store R14/24) | **{round(a25)}** |')
out.append(f'| prior end-of-Yr1 mean (2004-2024, n=21) | {mean_all:.0f} |')
out.append(f'| prior end-of-Yr1 recent-5 mean (2020-2024) | {mean_r5:.0f} |')
out.append(f'| prior end-of-Yr1 range | {min(anchors[C] for C in prior):.0f} - {max(anchors[C] for C in prior):.0f} |')
out.append(f'| shortfall vs 2004-2024 mean | **{100*(a25-mean_all)/mean_all:+.1f}%** |')
out.append(f'| shortfall vs recent-5 mean | **{100*(a25-mean_r5)/mean_r5:+.1f}%** |')
out.append(f'| shortfall vs 2023 ({anchors[2023]:.0f}) / 2024 ({anchors[2024]:.0f}) | {100*(a25-anchors[2023])/anchors[2023]:+.1f}% / {100*(a25-anchors[2024])/anchors[2024]:+.1f}% |')
out.append('\n**Pick-mix control** (anchor SUM / draft-day pick-value SUM — removes cohort size/pick-sum differences):\n')
out.append('| cohort | anchor/pick-sum |')
out.append('|---|---|')
for C in [2018, 2019, 2020, 2021, 2022, 2023, 2024]:
    out.append(f'| {C} | {100*anchors[C]/dvs[C]:.1f}% |')
out.append(f'| **2025** | **{100*a25/dv25:.1f}%** |')
nm_all = np.mean([anchors[C]/dvs[C] for C in prior]); nm_r5 = np.mean([anchors[C]/dvs[C] for C in rec5])
out.append(f'\n- normalized shortfall: vs 2004-2024 mean ratio {100*nm_all:.1f}% -> **{100*(a25/dv25-nm_all)/nm_all:+.1f}%**; vs recent-5 mean ratio {100*nm_r5:.1f}% -> **{100*(a25/dv25-nm_r5)/nm_r5:+.1f}%**')
out.append(f'- i.e. of the raw shortfall vs the recent-5 mean, cohort size/pick-mix (64 players, pick sum {round(dv25)} vs recent-5 mean {np.mean([dvs[C] for C in rec5]):.0f}) explains the difference between the raw and normalized numbers.')

# anchor == cur for the 2025 cohort (both are the ASOF-2026 value) — book-vs-board check part 1
ic25 = bycoh[2025]
mism = [x['player'] for x in ic25 if (x['anchor'] or 0) != (x['cur'] or 0)]
out.append(f'- book Yr1 slot == matrix current (ASOF 2026) for the 2025 cohort: {"IDENTICAL all 64" if not mism else f"MISMATCH {mism}"} (live-board equality vs a fresh engine eval is checked in the decomposition script)')

open('session_2026-07-03/d8_matrix_analysis.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
