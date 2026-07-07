#!/usr/bin/env python3
# ship_gates_check.py — scripted PASS/FAIL for the FROZEN acceptance suite (SHIP_GATES.md, frozen ref 764a0d91).
# Run at each candidate head and mandatorily at any bake:  python3 ship_gates_check.py
# Requires the bootstrap layout (/home/claude/...) + pinned env (setup_env.sh). One engine load per process.
# SCRIPTING NOTES honoured: EXACT full-name matching (no substrings; ambiguity -> ERROR, never a silent pick);
# line-ball = +/-20%; A13/A14 staged PENDING until the PVC stage; A6 kernel-smoothed pick-matching with the thin
# RUC slice pooled deliberately (yrs 1-3 together); [DC] tags carried into output for failure triage.
# THRESHOLD REGISTER (updated 2026-07-02, DIRECTIVE 2, Luke's rulings turns 09-10):
#   A6 kernel bw 0.6 on log-pick — RATIFIED (via Luke's delegation to supervisor, 02/07/2026).
#   B1 rule — RE-SCRIPTED per Luke: PASS = pooled cohort value rises from draft to a peak by yr4-5 (yr6
#     acceptable); interim pre-peak dips <5% tolerated (year 2 explicitly named); level need NOT hold in yr6.
#   B6 rule — RE-SCRIPTED per Luke: gate tests the WHOLE 0->6 ramp (<=5g players were dumped into the sit-out
#     stream, so 0g and 5g got identical treatment; flat-then-step IS the violation); value must progress
#     smoothly from the 0-game anchor to the 6-game production value. Monotone-in-evidence clause UNCHANGED.
#     Smoothness thresholds below are DECLARED pending ratification. Prior "seam 10%/3x" shorthand superseded.
#   B5 floor 0.25x draftval — PROVISIONAL this run (year-schedule crater-floor PROPOSAL with Luke to sign:
#     session_2026-07-02/directive2_notes.md). POPULATION CONVENTION (Luke, verbatim intent): ACTIVE/LISTED
#     players only; once inactive, value = 0; in backtests inactive players REMAIN in denominators while
#     contributing 0 to numerators for that year.
#   B2 leakage tol 0.5 %-pts — SET 02/07/2026 (supervisor ruling under Luke's delegation; measured N=5 spread
#     = 0.00 %-pts, so any gap >=0.5 is signal; rationale in CHANGELOG). Supersedes the provisional 5.0.
#   A2 AMENDED 02/07/2026 (Luke, in writing): Curtis leg = Curtis >= 0.90 x Ward (verbatim reason in CHANGELOG).
#   D4 AUDIT 02/07/2026 (full gate-line audit vs frozen 764a0d91 + logged amendments — session_2026-07-02/
#     d4_instrument_audit.md): A8 expression confirmed the literal 2x test (Berry=3473, Tsatas=1083 — both
#     reported passes GENUINE); defect was DISPLAY AMBIGUITY ("vs 2x Tsatas=2166" read as raw Tsatas) —
#     detail string de-ambiguated + comparison > -> >= per frozen "at least 2x". No missing-2x, no tolerance leak.
#   A10 AMENDED 02/07/2026 (Luke, in writing, D4): threshold 0.70 -> 0.50, DATA-CAUSED (Curnow has banked 13
#     games of 2026 — his level is 2026 form, not an engine artifact), PROVISIONAL + review at season-complete.
#   A3 ANNOTATED 02/07/2026 (Luke, D4): evaluated PRE-LTI-layer (the pre-LTI engine ratio is what A3 tests;
#     the future LTI overlay must not be the thing that passes it).
#   B5 YEAR-SCHEDULE SIGNED 02/07/2026 (Luke, in writing, D4): floors by years-in-system replace the 0.25x
#     proxy — see the B5 block for constants, population, and the generating rule.
#   B1 REDEFINED 02/07/2026 (Luke, in writing, confirmed, D5): the gate tests the CROSS-COHORT UNWEIGHTED
#     AVERAGE of indexed cohort value at each year-depth (rise from yr1 to a peak in yrs 4-6; <5% pre-peak
#     dips of the average tolerated). Per-cohort curves UNGATED by design but printed as a pipe table on
#     every gates-board run. The old per-cohort rise backstop is RETIRED — obituary in CHANGELOG (D5).
#   A3 AMENDED 02/07/2026 (Luke, in writing, D7): threshold 0.80 -> 0.75, DATA-CAUSED — Rozee out for the
#     remainder of 2026 (LTI register Section B); Luke verbatim: "Happy to adjust Rozee to 75%". The bar
#     deliberately sits at reality's edge (same design as A10/Curnow).
#   A2 UNCHANGED at 0.90 by ruling (Luke, D7): ships red at the v2 config (Curtis 0.822 measured at
#     candidate-minus-cB); Luke verbatim: "we can look at Curtis down the line".
#   B5 AMENDED 02/07/2026 (Luke-ruled; text prepared D6, committed D7): retired as a pass/fail ALARM;
#     replaced by the floor-as-pricing-feature at the ev() boundary (flat .05 yrs-7+ tail, VARIANT A as
#     signed) + the MANDATORY FLOOR-SAVES table printed on every board run (the new alarm surface) + the
#     pure-lower-bound re-verify (0 lowered, 0 non-ND moved). At heads that do not carry the floor feature
#     (canonical pre-v2), the line reports the legacy offender count INFORMATIONALLY — never FAIL.
import os, sys, io, json, copy, math, time, hashlib, subprocess, contextlib
ROOT = os.path.dirname(os.path.abspath(__file__))
RA = '/home/claude/rl_workspace/rl_after'
# GUARD 5 (boot-store) — PRE-FLIGHT, before the engine loads. The frozen acceptance suite must never run
# against a store the caller has not verified is the checked-out, pinned one. The four data guards validate
# whichever dir they are imported from (RA here, the workspace), so a stale-but-self-consistent workspace
# passes them silently — this closes that hole by asserting RA's store+head == data/expected_boot.json ==
# the repo checkout, and HALTS otherwise. This is a pre-flight ADDITION only: no gate's assertion, threshold,
# or value is touched; on the correct store the board is byte-identical to before. (Stale-boot hardening
# 2026-07-05.) OWNER RULING 2026-07-05 (Luke, in writing): "the Guard 5 pre-flight is a safety addition,
# not a frozen-gate amendment; apply and keep it." — recorded per the A7 precedent; the frozen suite 764a0d91
# is unamended. This pre-flight does not alter gate behaviour on the pinned store; it only refuses to run on
# any other store.
sys.path.insert(0, ROOT)
import boot_guard as _bg
_bg.assert_boot('ship_gates_check', store_path=os.path.join(RA, 'rl_model_data.json'),
                engine_head_path=os.path.join(RA, '_merged_recover.py'))
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', os.path.join(ROOT, 'vendor')]
os.environ['PYTHONPATH'] = ':'.join(sys.path[:3])          # subprocesses (B4 export) need it too
os.chdir(RA)
import numpy as np
SKIP = set(os.environ.get('SGC_SKIP', '').upper().split(',')) - {''}
HEAD = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
STORE = hashlib.md5(open('rl_model_data.json', 'rb').read()).hexdigest()[:8]
# ---- BINDING REPORTING RULES (Luke's word, D10 03/07/2026 — see BAKE_CHECKLIST.md §REPORTING) ----
# 5a: every gates/board output reports THREE COLUMNS — CONTROL / PREVIOUS / CURRENT, deltas explicit.
# 5b: every board/report carries a LOUD state label; no unlabelled player value anywhere Luke-facing.
try:
    _REG = json.load(open(os.path.join(ROOT, 'data', 'report_states.json')))
except Exception:
    _REG = {'states': {}}
STATE_LABEL = _REG.get('states', {}).get(HEAD, f'PROTOTYPE/UNREGISTERED @ {HEAD} — NOT AN ENDORSED STATE')
def _load_snap(key):
    try:
        return json.load(open(os.path.join(ROOT, _REG[key]['gates'])))
    except Exception:
        return {'head': '????????', 'gates': {}}
SNAP_CTL, SNAP_PREV = _load_snap('control'), _load_snap('previous')
t0 = time.time()
G = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], G)
ev, MA, cp = G['ev'], G['MA'], G['cp']
GRPPOS, draftval, delisted = G['GRPPOS'], G['draftval'], G['delisted']

# SHIP_GATES shorthand -> exact store ID (pinned; EXACT-name discipline, never substring)
ALIAS = {'Josh Weddle': 'Joshua Weddle', 'Dan Annable': 'Daniel Annable'}

def byname(name):
    name = ALIAS.get(name, name)
    hits = [p for p in MA.data if p['player'] == name and not p.get('_retired')]
    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, f'no exact active match for "{name}"'
    return None, f'AMBIGUOUS "{name}": ' + '; '.join(f"pick={h.get('pick')} yr={h.get('year')}" for h in hits)

def E(name, yr=2026):
    p, err = byname(name)
    if err:
        raise LookupError(err)
    with contextlib.redirect_stdout(io.StringIO()):
        return float(ev(p, yr))

RES, NOTES = [], []
def gate(gid, dc, status, detail):
    RES.append((gid, dc, status, detail))

def cmp_gate(gid, dc, pairs, fmt):        # pairs: list of (label, lhs, rhs) requiring lhs > rhs
    try:
        vals = [(lb, E(a), E(b)) for lb, a, b in pairs]
        ok = all(x > y for _, x, y in vals)
        gate(gid, dc, 'PASS' if ok else 'FAIL', '; '.join(fmt.format(lb, x, y) for lb, x, y in vals))
    except LookupError as ex:
        gate(gid, dc, 'ERROR', str(ex))

# ---------- SECTION A ----------
cmp_gate('A1', False, [('Duursma>Uwland', 'Willem Duursma', 'Zeke Uwland')], '{}: {:.0f} vs {:.0f}')
# A2 AMENDED (Luke, in writing, 02/07/2026 — verbatim reason logged in CHANGELOG per the SHIP_GATES amendment
# process): Curtis leg re-scripted from Ward < Curtis to Curtis >= 0.90 x Ward; Weddle leg + A9 unchanged.
# A2 UNCHANGED at 0.90 by ruling (Luke, D7 02/07): ships red at the v2 config (Curtis/Ward 0.822 measured);
# Luke verbatim: "we can look at Curtis down the line".
try:
    _cu, _wa, _we = E('Paul Curtis'), E('Josh Ward'), E('Joshua Weddle')
    _ok = (_cu >= 0.90 * _wa) and (_we > _wa)
    gate('A2', False, 'PASS' if _ok else 'FAIL',
         f'Curtis>=0.90xWard: {_cu:.0f} vs {0.90*_wa:.0f} (Ward={_wa:.0f}, ratio={_cu/max(_wa,1e-9):.3f}) [AMENDED 02/07/2026; UNCHANGED at 0.90 by ruling D7 — Luke: "we can look at Curtis down the line"]; Weddle>Ward: {_we:.0f} vs {_wa:.0f}')
except LookupError as ex:
    gate('A2', False, 'ERROR', str(ex))
# A3 ANNOTATED (Luke 02/07, D4): evaluated PRE-LTI-layer. A10 AMENDED (Luke, in writing, 02/07, D4):
# 0.70 -> 0.50, DATA-CAUSED (13g of 2026 banked), PROVISIONAL — review at season-complete; CHANGELOG logged.
# A3 AMENDED (Luke, in writing, D7 02/07): 0.80 -> 0.75, DATA-CAUSED (Rozee out for the remainder of 2026,
# register-confirmed); "Happy to adjust Rozee to 75%". Knife-edge by design (same as A10/Curnow).
for gid, nm, frac, note in [('A3', 'Connor Rozee', 0.75, ' [evaluated PRE-LTI-layer — Luke 02/07; AMENDED 0.80->0.75 Luke D7 data-caused (out for 2026), knife-edge by design]'),
                            ('A10', 'Charlie Curnow', 0.50, ' [AMENDED 0.70->0.50 Luke 02/07 data-caused, PROVISIONAL — review at season-complete]')]:
    try:
        v26, v25 = E(nm, 2026), E(nm, 2025)
        r = v26 / max(v25, 1e-9)
        gate(gid, True, 'PASS' if r >= frac else 'FAIL', f'{nm}: 2026={v26:.0f} 2025={v25:.0f} ratio={r:.2f} (need >={frac:.2f}){note}')
    except LookupError as ex:
        gate(gid, True, 'ERROR', str(ex))
# EV sweep (non-retired) for A4/A6/B5 + board context
EV = {}
with contextlib.redirect_stdout(io.StringIO()):
    for p in MA.data:
        if p.get('_retired'):
            continue
        try:
            EV[id(p)] = float(ev(p, 2026))
        except Exception:
            EV[id(p)] = None
board = sorted(((v, p) for p in MA.data if not p.get('_retired') and (v := EV.get(id(p))) is not None),
               key=lambda t: -t[0])
try:
    hr, err = byname('Harley Reid')
    if err: raise LookupError(err)
    rank = next(i for i, (_, p) in enumerate(board, 1) if p is hr)
    gate('A4', False, 'PASS' if rank <= 40 else 'FAIL', f'Harley Reid board rank={rank} ev={EV[id(hr)]:.0f} (need TOP 40)')
except LookupError as ex:
    gate('A4', False, 'ERROR', str(ex))
try:
    a5 = [('Jack Ginnivan', 1600), ('Jake Bowey', 2100), ('Nick Blakey', 2600)]
    vals = [(nm, E(nm), fl) for nm, fl in a5]
    gate('A5', False, 'PASS' if all(v > fl for _, v, fl in vals) else 'FAIL',
         '; '.join(f'{nm}={v:.0f} (floor {fl})' for nm, v, fl in vals) + ' [SCAR floors — RE-BASE if PVC re-levels]')
except LookupError as ex:
    gate('A5', False, 'ERROR', str(ex))
# A6 — yrs 1-3 (drafted 2023-2025, pooled deliberately: thin RUC slice), kernel-smoothed pick-matched MID medians
def cohort(grp):
    out = []
    for p in MA.data:
        if p.get('_retired') or p.get('_pickless') or EV.get(id(p)) is None:
            continue
        if MA.gfut(p) == grp and (2026 - int(p.get('year') or 0)) in (1, 2, 3):
            out.append((math.log(float(MA.effpk(p))), EV[id(p)]))
    return out
rucs, mids = cohort('RUC'), cohort('MID')
if len(rucs) >= 3 and len(mids) >= 10:
    mx = np.array([x for x, _ in mids]); mv = np.array([v for _, v in mids])
    def ksm(x, bw=0.6):
        w = np.exp(-0.5 * ((mx - x) / bw) ** 2)
        return float(np.dot(w, mv) / w.sum())
    med_ruc = float(np.median([v for _, v in rucs]))
    med_mid = float(np.median([ksm(x) for x, _ in rucs]))
    gate('A6', False, 'PASS' if med_ruc <= med_mid else 'FAIL',
         f'yr1-3 RUC median={med_ruc:.0f} (n={len(rucs)}, pooled — thin slice) vs pick-matched MID kernel median={med_mid:.0f} (n={len(mids)}, bw=0.6 log-pick, RATIFIED 02/07)')
else:
    gate('A6', False, 'ERROR', f'thin cohorts: RUC n={len(rucs)} MID n={len(mids)}')
# A7 — position poles hold. AMENDED 2026-07-05 (Luke, owner-authorised in writing): the 2026-07-05 DPP strip
# (final consolidation) DELETED the multi-position _fut weighted-blend from engine + store (0/2652 records carry
# _fut). A7's protected-pole read is re-pointed from the stripped p.get('_fut')-dominant label to the live single
# settled-future position p.get('future_position') (the source gfut() prices the years-1+ leg from). CHANNEL SWAP
# ONLY — same protected players, same pass condition (fine future_position == dom AND gfut(p) == grp), tolerance
# UNCHANGED; A7 still tests "did a protected position pole silently revert?" against the CURRENT data model.
# See CHANGELOG 2026-07-05 (frozen-suite amendment) + SHIP_GATES.md A7.
try:
    ok, det = True, []
    for nm, dom, grp in [('Ryan Maric', 'MID', 'MID'), ('Ed Langdon', 'GDEF', 'GEN_DEF')]:
        p, err = byname(nm)
        if err: raise LookupError(err)
        lab = p.get('future_position')            # AMENDED 2026-07-05: was sorted(p['_fut'])-dominant; _fut blend stripped by the DPP consolidation
        g_ = MA.gfut(p)
        ok &= (lab == dom and g_ == grp)
        det.append(f'{nm}: future_position={lab} gfut={g_} (need {dom}/{grp}) [AMENDED 2026-07-05: _fut blend stripped -> single future_position, owner-authorised]')
    gate('A7', False, 'PASS' if ok else 'FAIL', '; '.join(det))
except LookupError as ex:
    gate('A7', False, 'ERROR', str(ex))
# A8 AUDITED D4 02/07 (Luke's arithmetic catch): expression was and is the literal 2x test; the old detail
# string "Berry=N vs 2x Tsatas=M" invited reading M as raw Tsatas (M was 2xTsatas). De-ambiguated to raw
# values + explicit ratio; comparison > -> >= per the frozen wording "by at least 2x".
try:
    b, t = E('Sam Berry'), E('Elijah Tsatas')
    gate('A8', True, 'PASS' if b >= 2 * t else 'FAIL',
         f'Berry={b:.0f} Tsatas={t:.0f} ratio={b/max(t,1e-9):.2f}x (need >=2.00x) [display de-ambiguated D4 02/07]')
except LookupError as ex:
    gate('A8', True, 'ERROR', str(ex))
cmp_gate('A9', False, [('Ginnivan>Ward', 'Jack Ginnivan', 'Josh Ward')], '{}: {:.0f} vs {:.0f}')
cmp_gate('A11', True, [('Farrow>Patterson', 'Jacob Farrow', 'Dylan Patterson'), ('Cumming>Annable', 'Sam Cumming', 'Dan Annable')], '{}: {:.0f} vs {:.0f}')
cmp_gate('A12', True, [('Travaglia>Moraes', 'Tobie Travaglia', 'Christian Moraes'), ('Smillie>Retschko', 'Josh Smillie', 'Patrick Retschko')], '{}: {:.0f} vs {:.0f}')
# A13/A14 — PVC-coupled: staged PENDING (advisory numbers vs the CURRENT stand-in PVC, not the future curve)
def lineball(v, ref):
    return abs(v - ref) <= 0.20 * ref
try:
    pk1, pk8 = float(MA.PVC[1]), float(MA.PVC[8])
    a13 = [(nm, E(nm)) for nm in ('George Wardlaw', 'Levi Ashcroft')]
    a14 = [(nm, E(nm)) for nm in ('Trent Rivers', 'Zach Reid', 'Jase Burgoyne')]
    gate('A13', False, 'PENDING', f'PVC stage not run; advisory vs stand-in PVC[1]={pk1:.0f}: ' + '; '.join(f'{nm}={v:.0f} lineball={lineball(v,pk1)}' for nm, v in a13))
    gate('A14', False, 'PENDING', f'PVC stage not run; advisory vs stand-in PVC[8]={pk8:.0f}: ' + '; '.join(f'{nm}={v:.0f} lineball={lineball(v,pk8)}' for nm, v in a14))
except LookupError as ex:
    gate('A13', False, 'ERROR', str(ex)); gate('A14', False, 'ERROR', str(ex))
gate('A15', False, 'STRUCK', 'Luke 02/07/2026 — convexity dimension seeded as V_NEXT #1')
# ---------- SECTION B ----------
# B1 — cohort growth law from the walk-forward matrix (per-cohort SUM indexed yr1=100, busts=0; cohorts
# 2004-2020, incurve only). REBUILT (Luke's REDEFINITION, in writing, confirmed 02/07/2026, D5 — supersedes
# BOTH the pooled-rise re-script AND the per-cohort backstop): at each years-in-system depth d the SIMPLE
# (UNWEIGHTED) MEAN of indexed cohort value across all cohorts OBSERVED at depth d must rise from year 1 to
# a peak occurring in years 4-6; pre-peak dips of the AVERAGE tolerated under 5% (tolerance carried from old
# B1 — now applies to the average ONLY). Individual cohorts are UNGATED by design (Luke: "not all draft
# cohorts are equal; 2020 is a shocking draft — it should lose value") but the per-cohort table IS PRINTED
# as a pipe table on every gates-board run (Luke's eyeball channel — visibility without a gate). The retired
# per-cohort backstop's obituary lives in CHANGELOG (D5).
B1_TABLE = None
try:
    mpath = os.environ.get('S4_MATRIX', os.path.join(ROOT, 'data', 's4_matrix_baked_efea88e5.json'))  # BAKED walk-forward matrix (v2.5 DPP-strip, store e1b4d8bf)
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
    gate('B1', False, 'PASS' if ok else 'FAIL',
         f'cross-cohort AVERAGE peak N={ppk} AVG(peak)={AVG[ppk]:.0f} (need peak in yrs 4-6, >100; pre-peak dips '
         f'of the AVERAGE <5% tolerated, path_ok={path_ok}; per-cohort UNGATED, table printed every run — Luke '
         'redefinition 02/07 D5); avg row: ' + ' '.join(f'{N}:{AVG[N]:.0f}' for N in sorted(AVG)) +
         f'; cohorts n={len(cohorts)}; matrix={os.path.basename(mpath)}')
    _t = ['| cohort | peakN | ' + ' | '.join(f'd{N}' for N in range(1, 8)) + ' |',
          '|---|---|' + '---|' * 7]
    for C in cohorts:
        pk = max(R[C], key=R[C].get)
        _t.append(f'| {C} | {pk} | ' + ' | '.join((f'{R[C][N]:.0f}' if N in R[C] else '—') for N in range(1, 8)) + ' |')
    _t.append(f'| **AVG (the gated row)** | **{ppk}** | ' +
              ' | '.join((f'**{AVG[N]:.0f}**' if N in AVG else '—') for N in range(1, 8)) + ' |')
    B1_TABLE = '\n'.join(_t)
    NOTES.append('B1 per-cohort curves (UNGATED — printed every gates-board run, Luke eyeball channel):\n' + B1_TABLE)
except Exception as ex:
    gate('B1', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# B2 — GATE-1 leakage + separation, parsed from the harness output (_gate1_wf.py run this session)
try:
    g1p = '/home/claude/gate1_out.txt'
    if 'B2' in SKIP or not os.path.exists(g1p):
        gate('B2', False, 'NOT-RUN', 'run _gate1_wf.py first (writes /home/claude/gate1_out.txt)')
    else:
        import re
        rows, cur = {}, None
        for ln in open(g1p):
            ls = ln.strip()
            if ls.startswith(('MID', 'GEN_', 'KEY_')) and 'WF[' in ls:
                pos, tag = ls.split()[0], ls.split()[1]
                cur = (pos, tag)
                rows[cur] = {'WF': [float(x) for x in re.findall(r'T\d+:\s*(-?\d+)', ls.split('WF[')[1])]}
            elif ls.startswith('IS[') and cur:
                rows[cur]['IS'] = [float(x) for x in ls[3:ls.index(']')].split()]
        gaps = [abs(i - w) for r in rows.values() if 'IS' in r for w, i in zip(r['WF'], r['IS'])]
        leak = float(np.median(gaps)) if gaps else float('nan')
        seps = {pos: (np.median(rows[(pos, 'GOOD')]['WF']), np.median(rows[(pos, 'BUST')]['WF']))
                for pos in {p for p, _ in rows} if (pos, 'GOOD') in rows and (pos, 'BUST') in rows}
        sep_ok = all(g_ > b_ for g_, b_ in seps.values()) and bool(seps)
        ok = sep_ok and leak <= 0.5
        gate('B2', False, 'PASS' if ok else 'FAIL',
             f'median |IS-WF| leakage={leak:.1f} %-pts (tol 0.5, SET 02/07/2026 — N=5 spread 0.00); GOOD>BUST separation: ' +
             ', '.join(f'{p} {g_:.0f}/{b_:.0f}' for p, (g_, b_) in sorted(seps.items())))
except Exception as ex:
    gate('B2', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# B3 — walk-forward book FREEZE-STAMP (wired at the v2.4 bake 2026-07-04). The book (s4 matrix) is
# id(p)-keyed (str(id(p)) memory addresses -> raw bytes non-deterministic), so the seal hashes the
# STABLE-keyed content (player,type,year,pick), NOT raw bytes. Compares the current matrix's stable-key
# sha256 to the baked baseline data/book_stable_seal.json. Raw-file sha will differ every regen BY DESIGN.
try:
    _seal_path = os.path.join(ROOT, 'data', 'book_stable_seal.json')
    _mpath_b3 = os.environ.get('S4_MATRIX', os.path.join(ROOT, 'data', 's4_matrix_baked_efea88e5.json'))  # BAKED walk-forward matrix (v2.5 DPP-strip, store e1b4d8bf)
    if 'B3' in SKIP:
        gate('B3', False, 'NOT-RUN', 'SGC_SKIP=B3')
    elif not os.path.exists(_seal_path):
        gate('B3', False, 'NOT-RUN', f'no book seal baseline at {os.path.relpath(_seal_path, ROOT)} — run the freeze-stamp to seal the baked book')
    else:
        def _b3_stable_sha(path):
            _d = json.load(open(path)); _by = {}
            for _idk, _rec in _d.items():
                _by[(_rec.get('player'), _rec.get('type'), _rec.get('year'), _rec.get('pick'))] = _rec
            _h = hashlib.sha256()
            for _k in sorted(_by.keys(), key=lambda t: json.dumps(t, sort_keys=True)):
                _h.update(json.dumps(_k, sort_keys=True).encode())
                _h.update(json.dumps(_by[_k], sort_keys=True, separators=(',', ':')).encode())
            return _h.hexdigest(), len(_by)
        _seal = json.load(open(_seal_path))
        _cur_sha, _cur_n = _b3_stable_sha(_mpath_b3)
        _ok3 = (_cur_sha == _seal.get('stable_sha256'))
        gate('B3', False, 'PASS' if _ok3 else 'FAIL',
             f"book stable-key seal {'MATCHES' if _ok3 else 'DIFFERS FROM'} baseline: current={_cur_sha[:16]}.. ({_cur_n} players) "
             f"vs baseline={str(_seal.get('stable_sha256'))[:16]}.. ({_seal.get('n_players')} players, sealed head {_seal.get('head_md5')}); "
             f"matrix={os.path.basename(_mpath_b3)} [raw-file sha is id(p)-keyed / non-deterministic by design]")
except Exception as ex:
    gate('B3', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# B4 — board parity: regenerate rl_app_data.json (subprocess: one-engine-load rule) and byte-compare to shipped
try:
    if 'B4' in SKIP:
        gate('B4', False, 'NOT-RUN', 'SGC_SKIP=B4')
    else:
        shipped = '/home/claude/rl_build/rl_app_data.json'
        prev = os.path.join(RA, 'rl_app_data.json')
        bak = prev + '.sgc_bak'
        if os.path.exists(prev):
            os.replace(prev, bak)
        r = subprocess.run([sys.executable, 'rl_export.py'], cwd=RA, capture_output=True, text=True, timeout=1800)
        m_new = hashlib.md5(open(prev, 'rb').read()).hexdigest()[:8] if os.path.exists(prev) else 'MISSING'
        m_ship = hashlib.md5(open(shipped, 'rb').read()).hexdigest()[:8]
        if os.path.exists(prev):
            os.remove(prev)
        if os.path.exists(bak):
            os.replace(bak, prev)
        gate('B4', False, 'PASS' if m_new == m_ship else 'FAIL',
             f'regenerated rl_app_data.json md5={m_new} vs shipped {m_ship} (byte-agree gate; export exit={r.returncode})')
except Exception as ex:
    gate('B4', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# B5 — AMENDED 02/07/2026 (Luke-ruled, in writing; text prepared D6, committed D7; verbatim in CHANGELOG):
# retired as a pass/fail ALARM. The signed year-schedule floor is now a PRICING FEATURE at the ev() boundary
# (wired in the v2 candidate engine: ev = max(ev_prefloor, floor_yrs x draftval), ND entrants only, FLAT .05
# yrs-7+ tail — VARIANT A as signed). This block does, on every board run:
#   (1) FLOOR-SAVES TABLE (player · club · yrs-in-system · raw ev · floor · saved-to · lift · register
#       status) — the new alarm surface: a list that grows unexpectedly is the old gate's signal; mispricings
#       stay VISIBLE, never silently clamped.
#   (2) PURE-LOWER-BOUND RE-VERIFY: 0 lowered, 0 non-ND moved (full non-retired population).
# At a head WITHOUT the floor feature (canonical pre-v2), the legacy offender count prints INFORMATIONALLY.
# Status is FEATURE / FEATURE-ABSENT — never FAIL (the alarm is retired). GENERATING RULE + RE-BASE-AT-PVC
# reminder unchanged in SHIP_GATES.md (floor ~= 0.9 x smoothed clean p5 ND-only; re-derive at the PVC stage).
B5_FLOORS = {1: 0.45, 2: 0.35, 3: 0.28, 4: 0.21, 5: 0.13, 6: 0.09}   # yrs 7+ -> tail (VARIANT A, as signed)
B5_TAIL = 0.05
B5_TABLE = None
def _b5_scope(p):
    return not (p.get('_retired') or p.get('_pickless') or delisted(p) or p.get('type') != 'ND') \
        and (2026 - int(p.get('year') or 0)) >= 1
try:
    ev_pre = G.get('ev_prefloor')
    if ev_pre is not None:
        # register status column (LTI register — same parse as the D6 annotated table)
        import re as _re
        _reg = {}
        try:
            _rtxt = open(os.path.join(ROOT, 'LTI_REGISTER_2026-07-02.md')).read()
            _secA = _rtxt.split('## SECTION A')[1].split('## SECTION B')[0]
            for _m in _re.finditer(r'^\| ([^|]+) \| ([^|]+) \|', _secA, _re.M):
                if _m.group(1).strip() != 'player':
                    _reg[_m.group(1).strip()] = f'LTI ({_m.group(2).strip()})'
            _secB = _rtxt.split('## SECTION B')[1].split('---')[0]
            for _nm in _re.findall(r"[A-Z][\w'\-\.]+(?: [A-Z][\w'\-\.]+)+", _secB.replace('**', '')):
                _reg.setdefault(_nm, 'OUT-2026')
        except Exception:
            pass
        PRE = {}
        with contextlib.redirect_stdout(io.StringIO()):
            for p in MA.data:
                if p.get('_retired'):
                    continue
                try:
                    PRE[id(p)] = float(ev_pre(p, 2026))
                except Exception:
                    PRE[id(p)] = None
        lowered = [p['player'] for p in MA.data if not p.get('_retired')
                   and PRE.get(id(p)) is not None and EV.get(id(p)) is not None
                   and EV[id(p)] < PRE[id(p)] - 1e-9]
        nonnd_moved = [p['player'] for p in MA.data if not p.get('_retired') and not _b5_scope(p)
                       and PRE.get(id(p)) is not None and EV.get(id(p)) is not None
                       and abs(EV[id(p)] - PRE[id(p)]) > 1e-9]
        saves = []
        for p in MA.data:
            if p.get('_retired') or not _b5_scope(p):
                continue
            v0, v1 = PRE.get(id(p)), EV.get(id(p))
            if v0 is None or v1 is None or v1 <= v0 + 1e-9:
                continue
            yis = 2026 - int(p.get('year') or 0)
            fl = B5_FLOORS.get(yis, B5_TAIL) * draftval(p)
            saves.append((p['player'], p.get('_club') or '—', yis, v0, fl, v1, v1 - v0,
                          _reg.get(p['player'], 'clear')))
        saves.sort(key=lambda r: -r[6])
        _t = ['| player | club | yrs-in-system | raw ev | floor | saved-to | lift | register status |',
              '|---|---|---|---|---|---|---|---|']
        for nm, cl, yis, v0, fl, v1, lift, rg in saves:
            _t.append(f'| {nm} | {cl} | {yis} | {v0:.0f} | {fl:.1f} | {v1:.0f} | +{lift:.0f} | {rg} |')
        B5_TABLE = '\n'.join(_t)
        NOTES.append(f'B5 FLOOR-SAVES table (n={len(saves)}, aggregate lift={sum(r[6] for r in saves):+.0f} — '
                     'printed every gates-board run, the new alarm surface):\n' + B5_TABLE)
        ok_bound = not lowered and not nonnd_moved
        gate('B5', False, 'FEATURE' if ok_bound else 'FAIL',
             f'floor-as-pricing-feature (Luke-ruled 02/07; VARIANT A flat .05 tail): {len(saves)} saves, '
             f'aggregate lift {sum(r[6] for r in saves):+.0f}; pure lower bound: lowered={len(lowered)} (bar 0), '
             f'non-ND moved={len(nonnd_moved)} (bar 0); saves table printed below (the new alarm surface)')
    else:
        off = []
        for p in MA.data:
            if not _b5_scope(p):
                continue
            v = EV.get(id(p))
            if v is None:
                continue
            fl = B5_FLOORS.get(2026 - int(p.get('year') or 0), B5_TAIL)
            if v < fl * draftval(p):
                off.append(p['player'])
        gate('B5', False, 'FEATURE-ABSENT',
             f'floor feature not wired at this head (v2 candidate carries it); legacy offender count = '
             f'{len(off)} (INFORMATIONAL — the alarm is retired, Luke-ruled 02/07 D7)')
except Exception as ex:
    gate('B5', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# B6 — games-ramp continuity, RE-SCRIPTED (Luke 02/07, turns 09-10): the gate tests the WHOLE 0->6 ramp.
# <=5g players were dumped into the sit-out stream, so 0g and 5g got identical treatment; flat-then-step IS the
# violation. Value must progress smoothly from the 0-game anchor (empty scoring -> sit-out dv*retain path) to the
# 6-game production value. Monotone-in-evidence clause UNCHANGED (covers the 9->10g dip separately).
# DECLARED smoothness thresholds pending ratification: no single 0->6 step > 50% of the total 0->6 rise T,
# AND cumulative rise by 3g >= 25% of T (anti-flat-start). Prior "seam 10%/3x" shorthand superseded.
try:
    def ramp_p(gm):
        # top-level 'games' carried per the M3 wiring-time note (D4 backtest, m3_design §1): the age pin
        # activates _dev_advance's roll, which reads p['games'] — real store rows all carry it; the synth
        # must too. Byte-inert at heads without the M3 pin (the roll never activates there).
        return {'player': 'b6-synth', 'pos': GRPPOS.get('MID'), 'pick': 10.0, 'year': 2025, 'dob': '2006-03-01',
                'type': 'ND', 'scoring': ([{'year': 2026, 'games': gm, 'avg': 85.0}] if gm > 0 else []),
                'games': gm, '_pos_now': None, '_fut': []}
    with contextlib.redirect_stdout(io.StringIO()):
        vals = [float(ev(ramp_p(gm), 2026)) for gm in range(0, 15)]
    steps = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    dips = [(i, s) for i, s in enumerate(steps) if s < -1.0]          # label = start game of the step
    T = vals[6] - vals[0]
    big = [(i, round(s)) for i, s in enumerate(steps[:6]) if s > 0.50 * max(T, 1.0)]
    rise3 = vals[3] - vals[0]
    smooth_bad = (T <= 0) or big or (rise3 < 0.25 * T)
    gate('B6', False, 'PASS' if not dips and not smooth_bad else 'FAIL',
         f'ramp(0..14g)={[round(v) for v in vals]}; dips(more games worth less)={dips or "none"}; '
         f'0->6 rise T={T:+.0f}; 0->6 steps>50%T={big or "none"}; rise by 3g={rise3:+.0f} (need >={0.25*T:.0f}) '
         f'[whole-ramp re-spec, DECLARED thresholds]')
except Exception as ex:
    gate('B6', False, 'ERROR', f'{type(ex).__name__}: {ex}')
# ---------- SECTION C ----------
# ---------- D14 BY-CONSTRUCTION LAWS (Luke's amended V0 board law + owner override O1) ----------
# Wired PERMANENT gates (D14 1c/2a), board path: (D14a) same pos×draft-age×recorded-pick ⇒ IDENTICAL V0*
# across draft years (Luke's amended law); (D14b) within-cell V0 inversions = 0 roster-wide (the D13 pick-
# order guard TRANSFORM converted to this ASSERTION — obituary E5); (D14c) KPP retention floor O1 preserves
# depth monotonicity (max of two isotonic-non-increasing curves). Only present on a D14+ engine (board path).
try:
    _a = G['_v0_curve_assert']()
    gate('D14a', False, 'PASS' if _a['cross_draft_maxdisp'] < 1e-6 else 'FAIL',
         f"same pos×draft-age×recorded-pick ⇒ identical V0* across draft years: max cross-draft dispersion={_a['cross_draft_maxdisp']:.4f} SCAR (Luke's amended law; board path)")
    gate('D14b', False, 'PASS' if _a['within_cell_inversions'] == 0 else 'FAIL',
         f"within (pos×draft-age×draft-year) V0 inversions under V0* = {_a['within_cell_inversions']} roster-wide (D13 guard-transform → assertion; obituary E5)")
    gate('D14c', False, 'PASS' if _a['kpp_depth_monotone'] else 'FAIL',
         f"KPP retention floor O1 depth-monotone = {_a['kpp_depth_monotone']} (max of isotonic-non-increasing KPP/nonKPP; comparator nonKPP-only)")
except Exception as ex:
    gate('D14a', False, 'PENDING', f'D14 laws absent (pre-D14 engine): {type(ex).__name__}')

gate('C1', False, 'PENDING', 'naive-baseline book not yet built — definition proposal in report (needs its own directive)')
gate('C2', False, 'PENDING', 'V1-pick-model book not yet built — definition proposal in report (needs its own directive)')

# ---------- BOARD + REPORT ----------
order = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15',
         'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'D14a', 'D14b', 'D14c', 'C1', 'C2']
RES.sort(key=lambda r: order.index(r[0]))
cnt = {}
lines = [f'=== STATE: {STATE_LABEL} ===',
         f'=== SHIP GATES BOARD — head {HEAD} store {STORE} — suite 764a0d91 — {time.strftime("%Y-%m-%d")} ===',
         f'=== THREE-COLUMN RULE (Luke, binding D10): CONTROL={SNAP_CTL.get("head")} · PREVIOUS={SNAP_PREV.get("head")} · CURRENT={HEAD} ===']
for gid, dc, st, det in RES:
    cnt[st] = cnt.get(st, 0) + 1
    tag = ' [DC]' if dc else ''
    c_st = SNAP_CTL['gates'].get(gid, {}).get('status', '—')
    p_st = SNAP_PREV['gates'].get(gid, {}).get('status', '—')
    delta = '' if (c_st == p_st == st) else '  <- MOVED'
    lines.append(f'{gid:4s}{tag:5s} {c_st:8s}| {p_st:8s}| {st:8s} {det}{delta}')
    if dc and st == 'FAIL':
        lines.append(f'{"":9s} triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)')
lines.append(f'{"":9s} columns: CONTROL | PREVIOUS | CURRENT (three-column rule; snapshots data/gates_snapshots/)')
summary = 'VERDICT: ' + '  '.join(f'{k}={v}' for k, v in sorted(cnt.items())) + f'  ({time.time()-t0:.0f}s)'
lines.append(summary)
print('\n'.join(lines))
# persist this run as a snapshot (future runs' PREVIOUS/CONTROL columns read these)
try:
    os.makedirs(os.path.join(ROOT, 'data', 'gates_snapshots'), exist_ok=True)
    json.dump({'head': HEAD, 'store': STORE,
               'gates': {gid: {'dc': dc, 'status': st, 'detail': det[:200]} for gid, dc, st, det in RES}},
              open(os.path.join(ROOT, 'data', 'gates_snapshots', f'gates_{HEAD}.json'), 'w'), indent=1)
except Exception:
    pass
if B1_TABLE:      # Luke's ruling (02/07/2026 D5): the per-cohort table prints on EVERY gates-board run
    print('\nB1 per-cohort curves (UNGATED — Luke eyeball channel):\n' + B1_TABLE)
if B5_TABLE:      # Luke's ruling (02/07/2026, committed D7): the FLOOR-SAVES table prints on EVERY board run
    print('\nB5 FLOOR-SAVES (the new alarm surface — mispricings stay visible, never silently clamped):\n' + B5_TABLE)
rep = os.path.join(ROOT, os.environ.get('SGC_REPORT_DIR', 'session_2026-07-02'), f'ship_gates_report_{HEAD}.md')
os.makedirs(os.path.dirname(rep), exist_ok=True)
def _matcur(key):
    out = {}
    try:
        for r in json.load(open(os.path.join(ROOT, _REG[key]['matrix']))).values():
            out[f"{r['player']}|{r['year']}|{r['pick']}"] = r.get('cur')
    except Exception:
        pass
    return out
_MC, _MP = _matcur('control'), _matcur('previous')
with open(rep, 'w') as f:
    f.write(f'# ship_gates_check report — STATE: {STATE_LABEL} — head {HEAD} store {STORE}\n')
    f.write('_Three-column rule (Luke, binding D10): every board output reports CONTROL / PREVIOUS / CURRENT with explicit deltas._\n')
    f.write('```\n' + '\n'.join(lines) + '\n```\n')
    f.write('\n## Supporting detail\n')
    for n in NOTES:
        f.write('\n' + n + '\n')
    f.write(f'\n## Board top-50 (A4 context) — CONTROL {SNAP_CTL.get("head")} · PREVIOUS {SNAP_PREV.get("head")} · CURRENT {HEAD}\n')
    f.write('| # | player | pos | CONTROL | PREVIOUS | CURRENT | D vs ctl | D vs prev |\n|---|---|---|---|---|---|---|---|\n')
    for i, (v, p) in enumerate(board[:50], 1):
        k = f"{p['player']}|{p.get('year')}|{p.get('pick')}"
        c, q = _MC.get(k), _MP.get(k)
        dc_ = f'{v-c:+.0f}' if isinstance(c, (int, float)) else '—'
        dq = f'{v-q:+.0f}' if isinstance(q, (int, float)) else '—'
        f.write(f'| {i} | {p["player"]} | {MA.gfut(p)} | {c if c is not None else "—"} | {q if q is not None else "—"} | {v:.0f} | {dc_} | {dq} |\n')
    f.write('\n## C1/C2 DEFINITION PROPOSAL (for supervisor ruling)\n'
            'Rebuild the walk-forward book (s4 matrix protocol, as-of values, only <=T data) twice more:\n'
            '(a) NAIVE BASELINE: last-2-season era-adjusted avg -> value via simple age curve + position multipliers;\n'
            '(b) ORIGINAL V1 PICK MODEL: value = PVC(effective pick) with the V1 age/tenure profile.\n'
            'Headline metrics, engine must beat both on: (1) within-player GATE-1 protocol (WF good/bust separation,\n'
            'leakage-matched); (2) rank correlation of as-of value vs realized fwd best-3 production (real_mat);\n'
            '(3) cohort growth-law shape error vs the realized production curve. Each becomes C1x/C2x scripted lines.\n')
print(f'report: {rep}  md5={hashlib.md5(open(rep,"rb").read()).hexdigest()[:8]}')
# LOUD anti-leakage guard (folded at the v2.4 bake 2026-07-04): B2 (GATE-1 leakage) is MANDATORY. A
# NOT-RUN B2 (missing /home/claude/gate1_out.txt or SGC_SKIP=B2) must NOT pass silently — it counts as a
# FAILURE for the exit code. SCOPED to B2 only: other NOT-RUN/PENDING gates (A13/A14 PVC-staged, B4 skip)
# keep their semantics. This is the silent-anti-leakage-failure the bake calls out — now it fails loud.
_b2st = [st for gid, _, st, _ in RES if gid == 'B2']
_b2_notrun = bool(_b2st) and _b2st[0] == 'NOT-RUN'
if _b2_notrun:
    print('\n!! LOUD FAIL: B2 anti-leakage gate NOT EVALUATED (NOT-RUN) — the MANDATORY leakage gate cannot be '
          'skipped silently; run _gate1_wf.py first (writes /home/claude/gate1_out.txt). Treated as FAILURE.')
_hard_fail = any(st in ('FAIL', 'ERROR') for _, _, st, _ in RES) or _b2_notrun
sys.exit(1 if _hard_fail else 0)
