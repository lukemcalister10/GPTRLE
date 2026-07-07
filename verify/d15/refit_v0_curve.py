#!/usr/bin/env python3
"""
D15 V1 — INDEPENDENT V0 BOARD CURVE RE-FIT  (v2.4 / fa6abd0 / engine md5 7c199a1f)

Re-derives the D14 V0 board curve FROM SOURCE, without reading the engine's stored
fitted grid (_V0CURVE / _V0CURVE_META['_c18','_surfN','_surfR','_star']).

  * The engine subprocess dumps ONLY the SOURCE points the curve is fit on — the
    per-player capped start value _v0_raw at (position, draft-age, log recorded pick).
    Those are the raw inputs, not the fitted curve.
  * This parent process re-implements the D14 fitting algorithm from scratch
    (adaptive-bandwidth Nadaraya-Watson over log pick to local eff-n >= 35, then
    isotonic non-increasing; TIER-2 mature = 2-D age x log-pick kernel, isotonic in
    pick then non-increasing in draft-age) and evaluates its own curve.
  * It then compares the independently-fitted values against the engine's live
    star(pos, age, pick) at a fixed probe grid and across the FULL 1..90 pick grid
    for every cell, and reports the maximum absolute deviation.

PASS = independent re-fit reproduces the engine curve within TOL_ABS.
Run:  python verify/d15/refit_v0_curve.py    (from repo root, pinned venv)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sklearn.isotonic import IsotonicRegression
import _d15_common as C

TOL_ABS = 1e-6          # stated tolerance: identical algorithm on identical source -> float-noise only
POS6 = ['MID', 'KEY_FWD', 'KEY_DEF', 'GEN_FWD', 'GEN_DEF', 'RUC']
GRIDPK = list(range(1, 91))
LGRID = np.log(GRIDPK)

# ---- D14 fitting spec (hyperparameters are the DECLARED algorithm, not the fitted coefficients) ----
EFFN_MIN = 35.0
H0, HMAX, HGROW = 0.18, 2.2, 1.15                       # age<=18 NW bandwidth schedule
HA0, HAMAX, HAGROW = 1.2, 8.0, 1.2                      # mature age-bandwidth schedule
HP0, HPMAX, HPGROW = 0.18, 2.2, 1.15                    # mature pick-bandwidth schedule
MAT_AGES = list(range(19, 31))


def _iso_dec(y):
    return list(map(float, IsotonicRegression(increasing=False, out_of_bounds='clip').fit(LGRID, y).predict(LGRID)))


def refit_pick(pts):
    """adaptive-bandwidth NW over log-pick, grown to local eff-n>=EFFN_MIN, then isotonic non-increasing."""
    lx = np.array([a for a, _ in pts]); vy = np.array([b for _, b in pts]); grid = []
    for lg in LGRID:
        h = H0
        while True:
            w = np.exp(-0.5 * ((lx - lg) / h) ** 2); sw = w.sum()
            effn = (sw * sw) / float(np.sum(w * w)) if sw > 0 else 0.0
            if effn >= EFFN_MIN or h >= HMAX:
                break
            h *= HGROW
        grid.append(float(np.dot(w, vy) / sw) if sw > 0 else float(vy.mean()))
    return _iso_dec(grid)


def refit_mature(pts):
    """2-D (draft-age, log-pick) kernel; isotonic in pick per age, then non-increasing in draft-age."""
    aa = np.array([a for a, _, _ in pts]); lx = np.array([l for _, l, _ in pts]); vy = np.array([v for _, _, v in pts])
    surf = {}
    for ag in MAT_AGES:
        row = []
        for lg in LGRID:
            ha, hp = HA0, HP0
            while True:
                w = np.exp(-0.5 * ((aa - ag) / ha) ** 2) * np.exp(-0.5 * ((lx - lg) / hp) ** 2); sw = w.sum()
                effn = (sw * sw) / float(np.sum(w * w)) if sw > 0 else 0.0
                if effn >= EFFN_MIN or (ha >= HAMAX and hp >= HPMAX):
                    break
                if ha < HAMAX:
                    ha *= HAGROW
                else:
                    hp *= HPGROW
            row.append(float(np.dot(w, vy) / sw) if sw > 0 else float(vy.mean()))
        surf[ag] = _iso_dec(row)
    for i in range(len(GRIDPK)):                          # non-increasing in draft-age at each pick
        run = 1e18
        for ag in MAT_AGES:
            run = min(run, surf[ag][i]); surf[ag][i] = run
    return surf


def my_star(c18, surfN, surfR, pos, ag, pick):
    lp = np.log(min(max(pick, 1), 90))
    if ag <= 18:
        return float(np.interp(lp, LGRID, c18[pos]))
    surf = surfR if pos == 'RUC' else surfN
    return float(np.interp(lp, LGRID, surf[min(max(ag, 19), 30)]))


# ---- Probe: dump SOURCE points (_v0_raw) + engine star grid (comparison target only) ----
PROBE = r'''
import numpy as np
star = _V0CURVE_META['_star']
real = [p for p in MA.data if id(p) in _REAL and p.get('type')=='ND' and p.get('pick') is not None]
def ageR(p): return int(round(cp._age_asof(p, p.get('year') or (cp.debutyr(p)-1))))
POS6 = ['MID','KEY_FWD','KEY_DEF','GEN_FWD','GEN_DEF','RUC']
age18 = {pos: [[float(np.log(p.get('pick'))), float(_v0_raw(p))]
               for p in real if MA.gfut(p)==pos and ageR(p)<=18] for pos in POS6}
matN = [[ageR(p), float(np.log(p.get('pick'))), float(_v0_raw(p))]
        for p in real if MA.gfut(p)!='RUC' and ageR(p)>=19]
matR = [[ageR(p), float(np.log(p.get('pick'))), float(_v0_raw(p))]
        for p in real if MA.gfut(p)=='RUC' and ageR(p)>=19]
GRIDPK = list(range(1,91))
star_age18 = {pos: [float(star(pos,18,pk)) for pk in GRIDPK] for pos in POS6}
star_matN  = {ag: [float(star('MID',ag,pk)) for pk in GRIDPK] for ag in range(19,31)}
star_matR  = {ag: [float(star('RUC',ag,pk)) for pk in GRIDPK] for ag in range(19,31)}
# engine's own fit meta (n/eff-n only; NOT the fitted grid) for cross-display
meta = {str(k): {kk: v[kk] for kk in ('n','min_effn','grid_at_hmax') if kk in v}
        for k,v in _V0CURVE_META.items() if isinstance(v,dict) and 'n' in v}
RESULT = dict(md5=_ENG_MD5, age18=age18, matN=matN, matR=matR,
              star_age18=star_age18, star_matN=star_matN, star_matR=star_matR, meta=meta)
'''


def main():
    root = C.repo_root()
    out_path = os.path.join(root, 'verify', 'd15', 'refit_output.txt')
    L = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); L.append(s)

    res, md5, sha = C.run_tree('v2.4', PROBE)
    P(f"# D15 V1 — INDEPENDENT V0 CURVE RE-FIT   (git {sha} / engine md5 {md5})")
    P(f"# Source = per-player _v0_raw (capped start value); re-fit implemented in this script; ")
    P(f"# comparison target = engine star(pos,age,pick). TOL_ABS = {TOL_ABS:g}")
    P("")

    # --- independent re-fit ---
    c18 = {pos: refit_pick([tuple(x) for x in res['age18'][pos]]) for pos in POS6}
    surfN = refit_mature([tuple(x) for x in res['matN']])
    surfR = refit_mature([tuple(x) for x in res['matR']])
    P(f"Source counts:  age18 " + " ".join(f"{p}={len(res['age18'][p])}" for p in POS6)
      + f"  | mature nonRUC={len(res['matN'])} RUC={len(res['matR'])}")
    P("")

    # --- required probe grid ---
    P("## PROBE GRID — independent re-fit vs engine star  (fitted / engine / |dev|)")
    P("### RUC age<=18  (expect 1220/1220/1220 plateau, 1139 @pk5, 1087 @pk7-8)")
    for pk in [1, 2, 3, 5, 7, 8]:
        mv = my_star(c18, surfN, surfR, 'RUC', 18, pk); ev = res['star_age18']['RUC'][pk - 1]
        P(f"  pk{pk:>2}   refit={mv:9.3f}   engine={ev:9.3f}   |dev|={abs(mv-ev):.2e}")
    P("### KEY_FWD (KPP) age<=18, picks 1-8")
    for pk in range(1, 9):
        mv = my_star(c18, surfN, surfR, 'KEY_FWD', 18, pk); ev = res['star_age18']['KEY_FWD'][pk - 1]
        P(f"  pk{pk:>2}   refit={mv:9.3f}   engine={ev:9.3f}   |dev|={abs(mv-ev):.2e}")
    P("")

    # --- FULL grid max deviation (every cell, every pick) ---
    worst = (-1.0, None)
    ncells = 0
    for pos in POS6:                                       # 6 age<=18 cells x 90 picks
        ncells += 1
        for i, pk in enumerate(GRIDPK):
            mv = my_star(c18, surfN, surfR, pos, 18, pk); ev = res['star_age18'][pos][i]
            d = abs(mv - ev)
            if d > worst[0]:
                worst = (d, f"age18 {pos} pk{pk}: refit={mv:.4f} engine={ev:.4f}")
    for ag in MAT_AGES:                                    # mature nonRUC + RUC surfaces x 90 picks
        ncells += 2
        for i, pk in enumerate(GRIDPK):
            mv = my_star(c18, surfN, surfR, 'MID', ag, pk); ev = res['star_matN'][str(ag)][i]
            d = abs(mv - ev)
            if d > worst[0]:
                worst = (d, f"matNonRUC age{ag} pk{pk}: refit={mv:.4f} engine={ev:.4f}")
            mv = my_star(c18, surfN, surfR, 'RUC', ag, pk); ev = res['star_matR'][str(ag)][i]
            d = abs(mv - ev)
            if d > worst[0]:
                worst = (d, f"matRUC age{ag} pk{pk}: refit={mv:.4f} engine={ev:.4f}")
    P(f"## FULL GRID SWEEP — {ncells} cells x {len(GRIDPK)} picks "
      f"= {ncells*len(GRIDPK)} probe points (age<=18: 6 pos; mature: nonRUC+RUC over ages 19-30)")
    P(f"   max abs deviation = {worst[0]:.3e}   at [{worst[1]}]")
    verdict = 'PASS' if worst[0] <= TOL_ABS else 'FAIL'
    P("")
    P(f"## VERDICT: {verdict}   (max|dev| {worst[0]:.3e} {'<=' if verdict=='PASS' else '>'} TOL {TOL_ABS:g})")
    if verdict == 'FAIL':
        P(f"   STOP-FLAG: non-trivial deviation at [{worst[1]}]")
    # engine fit meta cross-display (eff-n reached; not used in the re-fit)
    P("")
    P("## engine fit meta (n / min_effn / grid@Hmax) — reported, NOT used as re-fit input")
    for k in ["('age18', 'MID')", "('age18', 'KEY_FWD')", "('age18', 'RUC')", 'mature_nonRUC', 'mature_RUC']:
        m = res['meta'].get(k)
        if m:
            P(f"   {k:24} n={m['n']:<5} min_effn={m['min_effn']:.1f} grid@Hmax={m['grid_at_hmax']}")

    open(out_path, 'w').write("\n".join(L) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == '__main__':
    main()
