#!/usr/bin/env python3
# D6 ASK 3 — register-annotated offender table: head-51 + candidate-31-joiners re-emitted with
# (i) REGISTER status (LTI register 1b24df4e), (ii) LUKE'S READ (seeded verbatim from the D6
# directive), (iii) 2026 games from the store. Inputs: this session's fresh head/candidate sweeps
# (d6 meas) + the committed D5 3b attribution column. No engine load.
import json, re, sys, hashlib

SCR = sys.argv[1]
REPO = '/home/user/afl-rl-engine'
H = json.load(open(f'{SCR}/meas_head_d6.json'))
C = json.load(open(f'{SCR}/meas_candidate_d6.json'))

def keyed(m):
    return {(r['player'], r['year'], r['pick']): r for r in m['b5_offenders']}
HK, CK = keyed(H), keyed(C)
join = sorted((CK[k] for k in CK if k not in HK), key=lambda r: (r['yis'], r['margin']))
leave = [HK[k] for k in HK if k not in CK]
assert len(HK) == 51 and len(CK) == 82 and len(join) == 31 and not leave, (len(HK), len(CK), len(join), len(leave))

# D5 attribution column (committed d5_ask3_b5_offenders.md, 3b table)
attr = {}
d5 = open(f'{REPO}/session_2026-07-02/d5_ask3_b5_offenders.md').read().split('## 3b')[1]
for ln in d5.splitlines():
    cells = [c.strip() for c in ln.split('|')]
    if len(cells) >= 12 and cells[1] and cells[1] not in ('player', '---') and not cells[1].startswith('-'):
        attr[cells[1]] = cells[10]

# register
reg = {}
txt = open(f'{REPO}/LTI_REGISTER_2026-07-02.md').read()
secA = txt.split('## SECTION A')[1].split('## SECTION B')[0]
for m in re.finditer(r'^\| ([^|]+) \| ([^|]+) \|', secA, re.M):
    nm = m.group(1).strip()
    if nm != 'player':
        reg[nm] = f"LTI ({m.group(2).strip()})"
secB = txt.split('## SECTION B')[1].split('---')[0]
for nm in re.findall(r"[A-Z][\w'\-\.]+(?: [A-Z][\w'\-\.]+)+", secB.replace('**', '')):
    reg.setdefault(nm, 'OUT-2026')

# Luke's reads, seeded verbatim from the D6 directive
LREAD = {}
for nm in ['Josh Goater', 'Braeden Campbell', 'Jack Bowes', 'Oliver Henry', 'Josh Gibcus',
           'Luke Pedlar', 'Jamarra Ugle-Hagan']:
    LREAD[nm] = 'floor-save endorsed'
for nm in ['Caiden Cleary', 'Riley Hardeman']:
    LREAD[nm] = 'tolerable-but-noted'
for nm in ['Nick Haynes', 'Jacob Hopper']:
    LREAD[nm] = 'utility-value vet'
LREAD['Phoenix Gothard'] = '**HEADLINE WORRY**'

L = []
L.append('# D6 ASK 3 — REGISTER-ANNOTATED OFFENDER TABLE (the evidence for Luke\'s held rulings)')
L.append("**STORE DATA AS-OF:** store `644d1254` (reconciled pre_stage0, the authoritative store) carries **no explicit "
         "as-of timestamp field** — flagged as a REQUIRED_INPUTS gap for Luke. Provenance-derived cut: 2026 season IN "
         "PROGRESS at SEASON_PROG=0.58 ≈ **round 14 of 24** (the M2/M3 calendar constant), workspace captured 2026-07-01, "
         "reconciled 2026-07-02.")
L.append(f"_Head `8aed420a` 51 offenders / candidate `fb39d88a` 82 (31 joiners, 0 leavers — re-verified from THIS session's "
         f"fresh sweeps, matching D5 exactly). REGISTER from `LTI_REGISTER_2026-07-02.md` (`1b24df4e`); LUKE'S READ seeded "
         f"verbatim from the D6 directive; g26 = 2026 games from the store._")
L.append('')
hd = '| player | club | yrs | ev | draftval | ratio | floor | margin | REGISTER | LUKE\'S READ | 2026 games |'
sep = '|---|---|---|---|---|---|---|---|---|---|---|'
def fmt(r):
    return (f"| {r['player']} | {r['club'] or '—'} | {r['yis']} | {r['ev']:.0f} | {r['draftval']:.0f} | "
            f"{r['ratio']:.3f} | {r['floor_frac']:.2f}x = {r['floor']:.0f} | {r['margin']:.0f} | "
            f"{reg.get(r['player'], 'clear')} | {LREAD.get(r['player'], '—')} | {r['g26']} |")
dev = sorted((r for r in HK.values() if r['yis'] <= 8), key=lambda r: (r['yis'], r['margin']))
tail = sorted((r for r in HK.values() if r['yis'] >= 9), key=lambda r: (r['yis'], r['margin']))
L.append(f'## HEAD-51: dev-window bucket (yrs 1-8, n={len(dev)})')
L.append(hd); L.append(sep)
for r in dev:
    L.append(fmt(r))
L.append('')
L.append(f'## HEAD-51: deep-veteran tail (yrs 9+, n={len(tail)})')
L.append(hd); L.append(sep)
for r in tail:
    L.append(fmt(r))
L.append('')
L.append(f'## CANDIDATE 31 JOINERS (82−51; 0 leavers) — with the D5 per-term attribution carried over')
L.append(hd + ' pushed under by (D5) |')
L.append(sep + '---|')
for r in join:
    L.append(fmt(r) + f" {attr.get(r['player'], '—')} |")
L.append('')
lti_j = [r['player'] for r in join if reg.get(r['player'], '').startswith('LTI')]
lti_h = [r['player'] for r in HK.values() if reg.get(r['player'], '').startswith('LTI')]
L.append(f"### Register cross-read: LTI names among the head-51: {', '.join(lti_h) if lti_h else 'NONE'} · "
         f"among the 31 joiners: {', '.join(lti_j) if lti_j else 'NONE'} — joiners marked LTI are candidates for the "
         f"register haircut path, NOT floor saves; their floor-save rows should be read with that flag.")
out = f'{REPO}/session_2026-07-02/d6_ask3_annotated_offenders.md'
open(out, 'w').write('\n'.join(L) + '\n')
print(f'head {len(HK)} / cand {len(CK)} / joiners {len(join)} / leavers {len(leave)}')
print('LTI in head-51:', lti_h, '| LTI in joiners:', lti_j)
print('wrote', out, 'md5', hashlib.md5(open(out, 'rb').read()).hexdigest()[:8])
