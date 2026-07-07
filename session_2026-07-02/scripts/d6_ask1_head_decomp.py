#!/usr/bin/env python3
# D6 ASK 1 — Phoenix Gothard decomposition at HEAD (one engine load; sequential).
# 1a: store record print (data check before mechanism).
# 1b: channel-by-channel decomposition of ev=317: band/replacement-netting -> pole recovery
#     (tenure fade x exposure gate) -> isotonic position guard -> STALENESS CAP (the min()).
#     Channel toggles via the D3/D5 monkeypatch machinery (tenure-click pin = M3 axes).
# 1c (part): head+M3-prototype value (D4 ASK-5 blend, s=clip(1-g26/11,0,1) -> s=0 for g26=13).
# Also emits meas_head_d6.json (gate-exact B5 offenders + clean rows + games/club/pos) for ASKs 2-3.
import os, sys, io, json, contextlib, hashlib
RA = '/home/claude/rl_workspace/rl_after'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor']
os.chdir(RA)
import numpy as np
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
ev, MA, cp, PR = g['ev'], g['MA'], g['cp'], g['PR']
raw_ev, iso_corr, draftval, delisted = g['raw_ev'], g['iso_corr'], g['draftval'], g['delisted']
b6, price6, par_pole, recover = g['b6'], g['price6'], g['par_pole'], g['recover']
nseas, _nqual, _lvlcurr, _eo, eff_ten = g['nseas'], g['_nqual'], g['_lvlcurr'], g['_eo'], g['eff_ten']
bestlvl = g['bestlvl']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
STORE = hashlib.md5(open('rl_model_data.json', 'rb').read()).hexdigest()[:8]
print(f'[d6-ask1] engine={ENG} store={STORE}')

P = [p for p in MA.data if p['player'] == 'Phoenix Gothard' and not p.get('_retired')]
assert len(P) == 1
p = P[0]
Y = 2026

# ---- 1a: store record ----
g26 = sum(x['games'] for x in p['scoring'] if x['year'] == 2026)
avg26 = next((x['avg'] for x in p['scoring'] if x['year'] == 2026), None)
print('\n== 1a STORE RECORD ==')
print(f"  player={p['player']} club={p.get('_club')} pick={p.get('pick')} year={p.get('year')} type={p.get('type')}")
print(f"  drafted pos={p.get('pos')} current pos (_pos_now)={p.get('_pos_now')} gfut={MA.gfut(p)} _fut={p.get('_fut')} switcher={'YES' if p.get('_pos_now') and p.get('_pos_now')!=p.get('pos') else 'NO'}")
print(f"  2026: games={g26} avg={avg26} | all scoring rows={p['scoring']}")
print(f"  years-in-system={2026-int(p['year'])} draft={p.get('_draft')} dob={p.get('_bd')} age_asof2026={cp._age_asof(p,Y)}")

# ---- 1b: pipeline decomposition ----
with contextlib.redirect_stdout(io.StringIO()):
    E0 = ev(p, Y)
    bb = b6(p, Y)
    pr = price6(p, bb, Y)
    rv = raw_ev(p, Y)
pos = MA.gfut(p); pk = MA.effpk(p)
T = min(max(PR.tenure(p, Y), 1), 6)
et = min(max(eff_ten(p, Y, PR.tenure(p, Y)), 1), 6)
with contextlib.redirect_stdout(io.StringIO()):
    po, par = par_pole(pos, pk, T)
a = MA.age(p)
wage = 0.0 if pos == 'RUC' else float(np.clip(1 - ((a or 21) - 20) / 6, 0, 1))
tfade = float(np.interp(et, [1, 2, 3, 4, 5, 6], [1.00, 0.76, 0.40, 0.16, 0.05, 0.05]))
nq = _nqual(p, Y)
expo = cp._exposure(p, Y)
expgate = 1.0 if nq >= 4 else min(1.0, expo / 22.0)
w = wage * tfade * expgate
perf = cp._lvl_wt(p, Y)
rec = recover(perf, par)
ic = iso_corr(pos, pk)
e_pre = rv * ic
dv = draftval(p)
el = PR.tenure(p, Y); ns = nseas(p, Y)
keyruc = pos in ('KEY_FWD', 'KEY_DEF', 'RUC')
onset = 2 if ns == 0 else (4 if keyruc else 3)
cap = dv * 0.25 * max(0.4, 1 - 0.10 * (el - onset)) * (1.6 if keyruc else 1.0)
REPL = MA.REPL.get(pos)
print('\n== 1b PIPELINE (band -> pole recovery -> iso guard -> staleness cap) ==')
print(f'  band b6 [q10,q30,q50,q70,q90,q97] = {[round(float(x),1) for x in bb]}')
print(f'  REPL[{pos}] = {REPL:.1f} (replacement netting inside price6/v_at_peak; his 2026 avg {avg26} sits {avg26-REPL:+.1f} vs REPL)')
print(f'  pr (band price, replacement-netted)          = {pr:.1f}')
print(f'  pole po={po:.1f} par={par:.1f} | age={a} wage={wage:.3f} | eff_ten={et} tfade={tfade:.3f} | nqual={nq} exposure={expo:.2f} expgate={expgate:.3f} -> w={w:.4f}')
print(f'  perf (_lvl_wt)={perf:.1f} recover(perf/par={perf/max(par,1e-9):.2f})={rec:.3f}')
print(f'  raw_ev = pr + w*rec*(po-pr) = {pr:.1f} + {w*rec*max(0.0,po-pr):.1f} = {rv:.1f}')
print(f'  iso_corr({pos},{pk}) = {ic:.4f} -> e_pre (uncapped engine price) = {e_pre:.1f}')
print(f'  STALENESS: el={el} ns={ns} onset={onset} -> stalled-branch cap = 0.25*{max(0.4,1-0.10*(el-onset)):.2f}*dv({dv:.0f}) = {cap:.1f}')
print(f'  ev = min(e_pre, cap) rounded = {E0}   [confirm 317: {"YES" if E0==317 else "NO"}]')
print(f'  channel deltas: staleness cap {min(e_pre,cap)-e_pre:+.1f} | signed floor 0.28*dv = {0.28*dv:.1f} (cap sits {cap-0.28*dv:+.1f} below it)')

# escape counterfactuals
print('\n== 1b CHANNEL COUNTERFACTUALS ==')
# (i) tenure click -1 (M3 pin axes): el 3->2 escapes onset
_ten0 = PR.tenure
PR.tenure = lambda q, YY, __f=_ten0: max(1, __f(q, YY) - 1) if (q is p and YY == Y) else __f(q, YY)
with contextlib.redirect_stdout(io.StringIO()):
    E_ten = ev(p, Y)
PR.tenure = _ten0
print(f'  (i) tenure-click -1yr (el 3->2, cap onset not reached): ev = {E_ten}')
# (ii) a second qualifying season (ns=2 escape): inject a synthetic 2025 6-game season at his own level
import copy
p2 = copy.deepcopy(p)
p2['scoring'] = [{'year': 2025, 'games': 6, 'avg': avg26}] + p2['scoring']
with contextlib.redirect_stdout(io.StringIO()):
    E_ns2 = ev(p2, Y)
print(f'  (ii) same player + a 6g@{avg26} 2025 season (ns=2, cap branch off; nq/exposure also move): ev = {E_ns2}')
# (iii) cap off only (the pure uncapped price, all else head): e_pre
print(f'  (iii) staleness-cap OFF, all else head: ev = {round(e_pre)}')
# (iv) iso/position guard off
print(f'  (iv) iso_corr=1 (position guard off), cap still on: ev = {round(min(rv, cap))} (cap binds regardless)')
# (v) exposure gate at proven treatment
rv_eg1 = pr + wage * tfade * 1.0 * rec * max(0.0, po - pr)
print(f'  (v) expgate=1 (proven treatment) raw_ev would be {rv_eg1:.1f}; capped ev still {round(min(rv_eg1*ic, cap))}')

# ---- 1c: head+M3 (blend is identity at s=0) ----
s = float(np.clip(1.0 - g26 / 11.0, 0.0, 1.0))
print(f'\n== 1c head+M3-prototype: g26={g26} -> s={s:.2f} -> w=1 -> M3 ev = {E0} (byte-identical by construction; M3 scopes to g26<11) ==')

# ---- the yr-3 cap cohort: is 0.250 the cap fingerprint across the offender list? ----
print('\n== the 0.25-cap fingerprint across yr-3 ND offenders (ratio ~0.250 = the stalled-branch cap, not priced value) ==')
for q in MA.data:
    if q.get('_retired') or q.get('_pickless') or delisted(q) or q.get('type') != 'ND':
        continue
    if 2026 - int(q.get('year') or 0) != 3:
        continue
    with contextlib.redirect_stdout(io.StringIO()):
        vq = ev(q, Y)
    dvq = draftval(q)
    if vq < 0.28 * dvq:
        nsq = nseas(q, Y)
        g26q = sum(x['games'] for x in q['scoring'] if x['year'] == 2026)
        a26q = next((x['avg'] for x in q['scoring'] if x['year'] == 2026), None)
        print(f"  {q['player']:22s} ev={vq:5.0f} dv={dvq:6.0f} ratio={vq/dvq:.3f} ns={nsq} g26={g26q} avg26={a26q}")

# ---- meas sweep for ASKs 2-3 (gate-exact, same as D5 machinery + games/club/pos fields) ----
EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for q in MA.data:
        if q.get('_retired'):
            continue
        try:
            EV[id(q)] = float(ev(q, Y))
        except Exception:
            EV[id(q)] = None
B5F = {1: .45, 2: .35, 3: .28, 4: .21, 5: .13, 6: .09}
off, clean = [], []
for q in MA.data:
    if q.get('_retired') or q.get('_pickless') or delisted(q) or q.get('type') != 'ND':
        continue
    yis = 2026 - int(q.get('year') or 0)
    if yis < 1:
        continue
    v = EV.get(id(q))
    if v is None:
        continue
    dvq = draftval(q)
    row = dict(player=q['player'], club=q.get('_club'), yis=yis, type=q.get('type'),
               ev=round(v, 1), draftval=round(dvq, 1), ratio=round(v / max(dvq, 1e-9), 4),
               pick=q.get('pick'), year=q.get('year'), key=q.get('key'), pos=q.get('pos'),
               g26=sum(x['games'] for x in q['scoring'] if x['year'] == 2026),
               ns=nseas(q, Y))
    clean.append(row)
    fl = B5F.get(yis, 0.05)
    if v < fl * dvq:
        off.append(dict(row, floor_frac=fl, floor=round(fl * dvq, 1), margin=round(v - fl * dvq, 1)))
off.sort(key=lambda r: (r['yis'], r['margin']))
out = dict(label='head_d6', engine_md5=ENG, store_md5=STORE, b5_count=len(off), b5_offenders=off, clean_rows=clean)
dst = sys.argv[1]
json.dump(out, open(dst, 'w'), indent=1)
print(f'\nB5 offenders at head (confirm 51): {len(off)} | clean ND rows: {len(clean)} | wrote {dst}')
