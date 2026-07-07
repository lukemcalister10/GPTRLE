#!/usr/bin/env python3
# D8 ASK 2 — verification sweep at head+GRADEDFIX (ONE engine load against the ALREADY-DEPLOYED patched
# workspace engine): full-population evs + per-fire-population detail (gap, q, grade, cap, uncapped,
# graded price). Usage: d8_ask2_verify.py <sweep_out.json> <detail_out.json>
import os, sys, io, json, hashlib, contextlib
# RA overridable: D8 runs against a scratch deployment (engine copy + its own rl_model/store, patched in
# place) — the shared workspace and candidate branch are never touched. PAIRING NOTE (honest): the cp/PR
# chain still resolves through wire_redesign.py's HARDCODED _FV='/home/claude/rl_workspace/forward_valuation'
# (the ASK-3iii root cause), so these runs read scratch-engine x WORKSPACE-forward_valuation — harmless here
# because forward_valuation is canonical and byte-identical in both trees (pair-guard added to
# verify_restore.sh this directive), but not structurally immune.
RA = os.environ.get('RL_D8_RA', '/home/claude/rl_workspace/rl_after')
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, os.path.join(os.path.dirname(RA), 'forward_valuation'), '/home/claude/rl_vendor']
outp, outd = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(RA)
import numpy as np
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, PR = G['ev'], G['MA'], G['PR']
raw_ev, iso_corr = G['raw_ev'], G['iso_corr']
draftval, delisted, nseas = G['draftval'], G['delisted'], G['nseas']
era, REF = G['era'], G['REF']
D8Q, D8G1, D8G2 = G['_D8Q'], G['_D8G1'], G['_D8G2']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]

EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired'):
            continue
        try:
            EV[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = float(ev(p, 2026))
        except Exception:
            EV[f"{p['player']}|{p.get('year')}|{p.get('pick')}"] = None
json.dump(dict(label='head+gradedfix', engine=ENG, evs=EV), open(outp, 'w'), indent=0)

rows = []
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired') or delisted(p):
            continue
        try:
            if nseas(p, 2026) != 1:
                continue
            pos = MA.gfut(p)
            el = PR.tenure(p, 2026)
            keyruc = pos in ('KEY_FWD', 'KEY_DEF', 'RUC')
            onset = 4 if keyruc else 3
            if el < onset:
                continue
            e_pre = float(raw_ev(p, 2026)) * float(iso_corr(pos, MA.effpk(p)))
            dv = draftval(p)
            frac = 0.25 * max(0.4, 1 - 0.10 * (el - onset)) * (1.6 if keyruc else 1.0)
            cap = dv * frac
            quals = [x for x in p['scoring'] if x['games'] >= 6 and x['year'] <= 2026]
            gap = 2026 - quals[-1]['year']
            yrow = [x for x in p['scoring'] if x['year'] == 2026 and x['games'] > 0]
            qv = (yrow[0]['avg'] * REF / era.get(2026, REF)) / MA.REPL[pos] if yrow else 0.0
            if gap == 0:
                grade = 1.0
            elif not yrow:
                grade = 0.0
            else:
                grade = float(np.interp(qv, D8Q, D8G1 if gap == 1 else D8G2))
            v = float(ev(p, 2026))
            rows.append(dict(player=p['player'], club=p.get('_club'), type=p.get('type'), pos=pos,
                             pick=p.get('pick'), year=p.get('year'), gap=gap,
                             g26=(yrow[0]['games'] if yrow else 0),
                             avg26=(yrow[0]['avg'] if yrow else None), q26=round(qv, 3),
                             qual=f"{quals[-1]['year']}:{quals[-1]['games']}g@{quals[-1]['avg']}",
                             grade=round(grade, 4), cap_value=round(cap, 1),
                             uncapped=round(e_pre, 1), graded_ev=round(v, 1)))
        except Exception as ex:
            rows.append(dict(player=p.get('player'), error=str(ex)))
rows.sort(key=lambda r: (r.get('gap', 99), -(r.get('uncapped') or 0)))
json.dump(dict(engine=ENG, n_fire=len(rows), rows=rows), open(outd, 'w'), indent=1)
print(f'engine={ENG} | sweep n={sum(1 for v in EV.values() if v is not None)} | fire population n={len(rows)}')
for r in rows:
    if 'error' in r: print('ERR', r); continue
    print(f"  {r['player']:26s} gap={r['gap']} g26={r['g26']} q26={r['q26']:5.2f} grade={r['grade']:6.3f} "
          f"cap={r['cap_value']:6.1f} uncap={r['uncapped']:7.1f} -> {r['graded_ev']:6.0f}")
print('wrote', outp, hashlib.md5(open(outp, 'rb').read()).hexdigest()[:8],
      '|', outd, hashlib.md5(open(outd, 'rb').read()).hexdigest()[:8])
