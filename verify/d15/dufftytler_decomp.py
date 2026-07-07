#!/usr/bin/env python3
"""
D15 V4 — COOPER DUFF-TYTLER MATERIALITY DECOMPOSITION
Real player, ACTIVE board. Top-5 pick (pick 4) from the most recent completed draft
(2025 ND), drafted KFWD, _fut=[[KFWD,85],[RUC,15]] -> gfut=KEY_FWD, born 2007 ->
draft-age 18, thin production (2026: 11g @ 49.5).

Answers the owner's bake-input question: did D14's V0 curve + KPP floor move a price
he actually trades? Three real engine columns are run in ISOLATED subprocesses:
  [CONTROL 8aed420a / git f4a4d34]  [v2.3 f3e537ba / git def39f5]  [v2.4 7c199a1f / git fa6abd0]

  a. His actual line each column: board price (ev) · V0 start value (under KEY_FWD) ·
     which pricing leg dominates (anchor vs production) with the blend weight.
  b. Which POSITION FIELD the V0 curve keys on — read from the call site (file:line).
  c. TOGGLE [HYPOTHETICAL-v2.4]: his V0 and board price if designated RUC (1220 plateau).
  d. NEXT-DRAFT PURE-RUCK entrant [HYPOTHETICAL-v2.4]: age-18 pick-3 start value under
     RUC and KEY_FWD (picks 1 and 5 for shape).

Run:  python verify/d15/dufftytler_decomp.py   (from repo root, pinned venv; ~3 min)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _d15_common as C

PLAYER = 'duff-tytler'

# ---- probe: full decomposition for one player; v2.4 also runs toggle + entrant ----
PROBE = r'''
import numpy as np
Y = 2026
def find(nm):
    c = [p for p in MA.data if nm.lower() in p.get('player','').lower() and MA.GRP.get(p.get('pos'))]
    return c[0] if c else None
p = find("__PLAYER__")
G = globals()
def has(n): return n in G
draftage = int(round(cp._age_asof(p, p.get('year') or (cp.debutyr(p)-1))))
gf = MA.gfut(p); pk = MA.effpk(p)
star = _V0CURVE_META['_star'] if has('_V0CURVE_META') else None

# --- start / V0 anchor ---
if has('v0_start'):
    v0 = float(v0_start(p)); v0_src = 'D14CURVE'   # v0_start on the board path = the fitted V0* curve
else:
    v0 = float(raw_ev(p, cp.debutyr(p)-1) * iso_corr(gf, pk)); v0_src = 'PRECURVE'  # raw_ev*iso zero-evidence anchor
v0_uncapped = float(_v0_uncapped(p)) if has('_v0_uncapped') else None
v0_raw = float(_v0_raw(p)) if has('_v0_raw') else None
star_here = float(star(gf, draftage, pk)) if star else None

# --- production leg ---
if has('_prod_path'):
    e = float(_prod_path(p, Y))
else:
    e = float(raw_ev(p, Y) * iso_corr(gf, pk))

# --- routing / dominance ---
ns = int(nseas_pro(p, Y)) if has('nseas_pro') else None
gy = sum(x['games'] for x in p['scoring'] if x['year'] == Y)
board_price = int(ev(p, Y))
prefloor = int(ev_prefloor(p, Y)) if has('ev_prefloor') else None
yis = Y - int(p.get('year') or 0)
floor_val = float(floor_frac(yis) * v0) if has('floor_frac') else None
floor_frac_v = float(floor_frac(yis)) if has('floor_frac') else None

sit = {}
if has('sitout_ev') and has('LAM_SIT') and has('_R_surf') and has('_sitout_cls'):
    fe = _fEy(Y) if has('_fEy') else 0.58
    tau = max(0.0, Y - cp.debutyr(p)) + ((fe**1.5) if Y >= cp.debutyr(p) else 0.0)
    R = float(_R_surf(_sitout_cls(gf), pk, tau))
    lam = float(np.interp(min(gy/fe, 6.0), [0,1,2,3,4,5,6], LAM_SIT))
    sit = dict(is_sitout=(ns == 0), lam=lam, R=R, anchor_leg=(1-lam)*R*v0, prod_leg=lam*e,
               blended=(1-lam)*R*v0 + lam*e)

RESULT = dict(md5=_ENG_MD5, player=p['player'], gfut=gf, effpk=pk, pick=p.get('pick'),
              draftage=draftage, year=p.get('year'), gy=gy, ns=ns,
              v0=v0, v0_src=v0_src, v0_uncapped=v0_uncapped, v0_raw=v0_raw, star_here=star_here,
              prod_e=e, board_price=board_price, prefloor=prefloor,
              yis=yis, floor_val=floor_val, floor_frac=floor_frac_v, sit=sit)

# --- v2.4 only: toggle to RUC + next-draft entrant (curve reads) ---
if star is not None and _ENG_MD5 == '7c199a1f':
    RESULT['star_grid'] = {
        'RUC':     {pk_: float(star('RUC', 18, pk_)) for pk_ in [1, 3, 5]},
        'KEY_FWD': {pk_: float(star('KEY_FWD', 18, pk_)) for pk_ in [1, 3, 5]},
    }
    RESULT['toggle'] = {'v0_KEY_FWD': float(star('KEY_FWD', draftage, pk)),
                        'v0_RUC': float(star('RUC', draftage, pk))}
    # full-price toggle: mutate designation to RUC-dominant, inject his RUC curve value, re-price
    base_price = int(ev(p, Y))
    p['_fut'] = [['RUC', 85.0], ['KFWD', 15.0]]        # gfut -> RUC (probe-only, in-memory)
    for cache in ('_V0C', '_V0U'):
        if cache in G:
            G[cache].clear()
    MA._pe_clear()
    G['_V0CURVE'][_v0key(p)] = float(star('RUC', draftage, pk))   # his V0 under the RUC population curve
    ruc_v0 = float(v0_start(p)); ruc_price = int(ev(p, Y))
    RESULT['toggle'].update(base_price_KEY_FWD=base_price, price_RUC=ruc_price,
                            v0_start_RUC=ruc_v0, prod_e_RUC=float(_prod_path(p, Y)))
'''.replace('__PLAYER__', PLAYER)


def dominant_leg(r):
    """Return (leg, weight-string) for the actual line."""
    sit = r.get('sit') or {}
    if sit.get('is_sitout'):
        return ('SIT-OUT blend', f"production λ={sit['lam']:.3f} · anchor (1-λ)·R={ (1-sit['lam'])*sit['R']:.3f} "
                                 f"(R={sit['R']:.3f}); blend={sit['blended']:.0f}")
    # main path: production leg is the price unless the V0-anchored floor binds
    fv = r.get('floor_val')
    price = r['board_price']
    if fv is not None and abs(price - round(fv)) <= 1 and fv > r['prod_e']:
        return ('ANCHOR (V0 floor)', f"floor={r['floor_frac']:.2f}×V0={fv:.0f} binds over production {r['prod_e']:.0f}")
    slack = f"floor {r['floor_frac']:.2f}×V0={fv:.0f} slack (<price)" if fv is not None else "no floor"
    return ('PRODUCTION', f"production leg {r['prod_e']:.0f} ≈ price; {slack}; anchor V0={r['v0']:.0f} not traded")


def main():
    root = C.repo_root()
    out_path = os.path.join(root, 'verify', 'd15', 'dufftytler_decomp_output.txt')
    L = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); L.append(s)

    cols = {}
    for lbl in ['CONTROL', 'v2.3', 'v2.4']:
        res, md5, sha = C.run_tree(lbl, PROBE, timeout=600)
        cols[lbl] = (res, md5, sha)

    r4 = cols['v2.4'][0]
    P("# D15 V4 — COOPER DUFF-TYTLER MATERIALITY DECOMPOSITION")
    P(f"# {r4['player']}  ·  drafted pick {r4['pick']} ({r4['year']} ND)  ·  gfut(current designation)={r4['gfut']}"
      f"  ·  draft-age {r4['draftage']}  ·  2026: {r4['gy']}g")
    P("# columns:  [CONTROL 8aed420a/f4a4d34]  [v2.3 f3e537ba/def39f5]  [v2.4 7c199a1f/fa6abd0]")
    P("")

    # ---- (a) three-column line ----
    P("## (a) HIS ACTUAL LINE — three columns (all numbers state-labelled)")
    P(f"{'':22}{'[CONTROL]':>14}{'[v2.3]':>14}{'[v2.4]':>14}")
    def row(label, fn):
        vals = []
        for lbl in ['CONTROL', 'v2.3', 'v2.4']:
            vals.append(fn(cols[lbl][0]))
        P(f"{label:22}{vals[0]:>14}{vals[1]:>14}{vals[2]:>14}")
    row("board price (ev)", lambda r: f"{r['board_price']}")
    row("V0 start value", lambda r: f"{r['v0']:.0f}")
    row("  (V0 source)", lambda r: 'D14-curve' if r['v0_src'] == 'D14CURVE' else 'pre-curve raw')
    row("prod leg e", lambda r: f"{r['prod_e']:.0f}")
    row("prefloor ev", lambda r: f"{r['prefloor']}" if r['prefloor'] is not None else '—')
    row("floor frac·V0", lambda r: f"{r['floor_val']:.0f}" if r.get('floor_val') is not None else '—')
    row("nseas_pro / sit?", lambda r: f"{r['ns']}/{'SIT' if (r.get('sit') or {}).get('is_sitout') else 'played'}")
    P("")
    P("### dominant pricing leg (per column):")
    for lbl in ['CONTROL', 'v2.3', 'v2.4']:
        leg, why = dominant_leg(cols[lbl][0])
        P(f"   [{lbl}] {leg}  —  {why}")
    dp = r4['board_price'] - cols['CONTROL'][0]['board_price']
    P("")
    P(f"### PRICE MOVEMENT (the number the owner trades): CONTROL {cols['CONTROL'][0]['board_price']} "
      f"→ v2.3 {cols['v2.3'][0]['board_price']} → v2.4 {r4['board_price']}  "
      f"(net Δ CONTROL→v2.4 = {dp:+d})")
    P(f"### V0 ANCHOR MOVEMENT: CONTROL {cols['CONTROL'][0]['v0']:.0f} → v2.3 {cols['v2.3'][0]['v0']:.0f} "
      f"→ v2.4 {r4['v0']:.0f}  (the D14 curve reshaped the START anchor)")
    P("")

    # ---- (b) position field ----
    P("## (b) WHICH POSITION FIELD THE V0 CURVE KEYS ON  (read from the code, not docs)")
    P("   The board V0 curve is looked up by MA.gfut(p) — the SETTLED/CURRENT designation, NOT the")
    P("   frozen drafted position p['pos'].")
    P("     • engine/rl_after/_merged_recover.py:428  _V0CURVE[_v0key(p)] = star(MA.gfut(p), _ageR(p), p.get('pick'))")
    P("     • engine/rl_after/_merged_recover.py:324  _v0key(p) = (... , MA.gfut(p), MA.effpk(p))   # key includes gfut")
    P("     • engine/rl_after/_merged_recover.py:433  v0_start: return _V0CURVE.get(_v0key(p))       # board path")
    P("     • engine/rl_after/rl_model.py:36-40        gfut(p): settled FUTURE position = max-weight of p['_fut'],")
    P("                                                 else bnow(p) (= _pos_now or drafted pos). TOGGLEABLE.")
    P("   => A KEY_FWD→RUC toggle (flip _fut so gfut returns RUC) moves him off the KEY_FWD age-18 curve")
    P("      onto the RUC age-18 curve — i.e. onto the 1220 top-pick plateau. (sized in (c)).")
    P("")

    # ---- (c) toggle ----
    tg = r4.get('toggle', {})
    P("## (c) TOGGLE SCENARIO [HYPOTHETICAL-v2.4] — if designated RUC on fa6abd0 (probe-only, no board write)")
    P(f"   [v2.4]           V0 (KEY_FWD, as designated) = {tg.get('v0_KEY_FWD',0):.0f}")
    P(f"   [HYPOTHETICAL-v2.4] V0 (RUC, pk{r4['effpk']} age18) = {tg.get('v0_RUC',0):.0f}   "
      f"(RUC age-18 curve at pick {r4['effpk']} — just below the 1220 pick-1..3 plateau; "
      f"ΔV0 = {tg.get('v0_RUC',0)-tg.get('v0_KEY_FWD',0):+.0f})")
    P(f"   [v2.4]           board price as KEY_FWD = {tg.get('base_price_KEY_FWD','?')}")
    P(f"   [HYPOTHETICAL-v2.4] board price as RUC  = {tg.get('price_RUC','?')}   "
      f"(v0_start now {tg.get('v0_start_RUC',0):.0f}; prod leg under RUC machinery = {tg.get('prod_e_RUC',0):.0f})")
    if tg:
        P(f"   => sized toggle exposure on the traded price: {tg.get('price_RUC',0)-tg.get('base_price_KEY_FWD',0):+d} "
          f"SCAR (V0 anchor lift {tg.get('v0_RUC',0)-tg.get('v0_KEY_FWD',0):+.0f}).")
    P("")

    # ---- (d) next-draft entrant ----
    sg = r4.get('star_grid', {})
    P("## (d) NEXT-DRAFT PURE-RUCK ENTRANT [HYPOTHETICAL-v2.4] — new age-18 entrant start value (V0*), by pick")
    P(f"{'pick':>6}{'[RUC]':>12}{'[KEY_FWD]':>12}")
    for pk in [1, 3, 5]:
        P(f"{pk:>6}{sg.get('RUC',{}).get(str(pk), sg.get('RUC',{}).get(pk,0)):>12.0f}"
          f"{sg.get('KEY_FWD',{}).get(str(pk), sg.get('KEY_FWD',{}).get(pk,0)):>12.0f}")
    P("   (pick-3 is the sizing target: a day-one pure ruck starts at the RUC-curve V0* above under the")
    P("    stopgap curve; the KEY_FWD column is the same entrant if mis-designated a key forward.)")
    P("")
    P("## engine md5 assertions:  CONTROL=%s  v2.3=%s  v2.4=%s" %
      (cols['CONTROL'][1], cols['v2.3'][1], cols['v2.4'][1]))

    open(out_path, 'w').write("\n".join(L) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == '__main__':
    main()
