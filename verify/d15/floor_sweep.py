#!/usr/bin/env python3
"""
D15 V2 — KPP RETENTION FLOOR: "NEVER LOWERS" FULL SWEEP  (v2.4 / fa6abd0 / 7c199a1f)

Owner Override O1 (D14 ASK2): on the BOARD PATH the KPP sit-out retention surface is
set to pointwise MAX(KPP, nonKPP) at every (log-pick, depth). The load-bearing claim
is that this floor NEVER LOWERS a KPP retention value — it is a pure lower bound that
only raises. This sweeps EVERY cell in the floor's domain and checks it directly by
exercising the live engine code path `_R_surf('KPP', pick, tau)`:

  floored   = _R_surf('KPP', pick, tau)  with _BOARD_PATH = True   (O1 ON)
  unfloored = _R_surf('KPP', pick, tau)  with _BOARD_PATH = False  (O1 OFF, raw KPP)

Domain = pick in 1..90  x  depth tau in 1..6  = 540 cells (printed, not assumed).
Violation = floored < unfloored - eps at any cell (expect 0).
Also isolates the O1 bind map (where nonKPP > KPP) and re-checks D14c depth-monotonicity.

Run:  python verify/d15/floor_sweep.py   (from repo root, pinned venv)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _d15_common as C

EPS = 1e-9

PROBE = r'''
import numpy as np
PICKS = list(range(1,91)); TAUS = [1,2,3,4,5,6]
cells = []
viol = []
# raw class dv vectors for the bind analysis (KPP vs the nonKPP comparator)
def raw_dv(cls, pick):
    lp = np.log(min(max(pick,1),90)); return _dv_surf(cls, lp)   # 6-vector, depths 1..6
for pk in PICKS:
    kpp = raw_dv('KPP', pk); non = raw_dv('nonKPP', pk)
    for ti, tau in enumerate(TAUS):
        _BOARD_PATH_SAVE = _BOARD_PATH
        globals()['_BOARD_PATH'] = True
        floored = float(_R_surf('KPP', pk, tau))
        globals()['_BOARD_PATH'] = False
        unfloored = float(_R_surf('KPP', pk, tau))
        globals()['_BOARD_PATH'] = _BOARD_PATH_SAVE
        binds = non[ti] > kpp[ti] + 1e-12
        cells.append(dict(pick=pk, tau=tau, floored=floored, unfloored=unfloored,
                          kpp=float(kpp[ti]), non=float(non[ti]), binds=bool(binds),
                          lift=floored-unfloored))
        if floored < unfloored - 1e-9:
            viol.append(dict(pick=pk, tau=tau, floored=floored, unfloored=unfloored))
# D14c: floored KPP retention non-increasing in depth (max of two isotonic-non-increasing curves)
mono_bad = []
for pk in PICKS:
    _S=_BOARD_PATH; globals()['_BOARD_PATH']=True
    seq=[float(_R_surf('KPP',pk,t)) for t in TAUS]
    globals()['_BOARD_PATH']=_S
    for i in range(1,len(seq)):
        if seq[i] > seq[i-1] + 1e-9: mono_bad.append(dict(pick=pk, depth=i+1, prev=seq[i-1], cur=seq[i]))
RESULT = dict(md5=_ENG_MD5, cells=cells, viol=viol, mono_bad=mono_bad,
              npick=len(PICKS), ntau=len(TAUS))
'''


def main():
    root = C.repo_root()
    out_path = os.path.join(root, 'verify', 'd15', 'floor_sweep_output.txt')
    L = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); L.append(s)

    res, md5, sha = C.run_tree('v2.4', PROBE)
    cells = res['cells']; viol = res['viol']; mono = res['mono_bad']
    ncells = len(cells); nbind = sum(1 for c in cells if c['binds'])

    P(f"# D15 V2 — KPP FLOOR NEVER-LOWERS FULL SWEEP   (git {sha} / engine md5 {md5})")
    P(f"# floored=_R_surf('KPP',pick,tau) O1 ON  vs  unfloored O1 OFF; violation = floored < unfloored")
    P("")
    P(f"## SWEEP DOMAIN: pick 1..{res['npick']}  x  depth 1..{res['ntau']}  =  {ncells} cells")
    if ncells == 540:
        P(f"   cell count = {ncells}  (== the audit's claimed 540)")
    else:
        P(f"   cell count = {ncells}  (!= the audit's claimed 540 — DISCREPANCY, see above)")
    P("")
    P(f"## VIOLATIONS (floored < unfloored): {len(viol)}   (expect 0)")
    if viol:
        for v in viol[:50]:
            P(f"   VIOLATION pick{v['pick']} depth{v['tau']}: floored={v['floored']:.6f} < unfloored={v['unfloored']:.6f}")
    else:
        P("   none — the floor is a pure lower bound on every cell (never lowers).")
    P("")
    P(f"## D14c depth-monotonicity of the floored KPP surface: {'OK' if not mono else str(len(mono))+' BAD'}")
    if mono:
        for m in mono[:20]:
            P(f"   NON-MONOTONE pick{m['pick']} depth{m['depth']}: {m['prev']:.4f} -> {m['cur']:.4f}")
    P("")

    # ---- O1 override effect isolated on its named cells ----
    P(f"## O1 OVERRIDE EFFECT — binds (nonKPP>KPP) on {nbind}/{ncells} cells; "
      f"max lift = {max(c['lift'] for c in cells):.4f} retention")
    by_depth = {}
    for c in cells:
        by_depth.setdefault(c['tau'], []).append(c)
    P("   binds per depth (cells where nonKPP>KPP, i.e. floor raises):")
    for t in [1, 2, 3, 4, 5, 6]:
        b = [c for c in by_depth[t] if c['binds']]
        picks = [c['pick'] for c in b]
        rng = f"picks {min(picks)}-{max(picks)}" if picks else "none"
        P(f"     depth {t}: {len(b):>3} / {res['npick']} cells bind   ({rng})")
    P("")
    P("   named-cell spot checks (verification-doc claims):")
    def cell(pk, t):
        return next(c for c in cells if c['pick'] == pk and c['tau'] == t)
    for pk in [20, 25, 30]:
        c = cell(pk, 1)
        P(f"     pick{pk} depth1 (mid-pick band): KPP={c['kpp']:.3f} nonKPP={c['non']:.3f} "
          f"-> floored={c['floored']:.3f} {'BINDS(+%.3f)'%c['lift'] if c['binds'] else 'no bind'}")
    for t in [3, 5]:
        c = cell(5, t)
        P(f"     pick5  depth{t}: KPP={c['kpp']:.3f} nonKPP={c['non']:.3f} "
          f"-> floored={c['floored']:.3f} {'BINDS(+%.3f)'%c['lift'] if c['binds'] else 'no bind'}")
    c50 = [cell(50, t) for t in [1, 2, 3, 4, 5, 6]]
    any50 = any(c['binds'] for c in c50)
    P(f"     pick50 all depths: {'binds somewhere' if any50 else 'NO bind at any depth (KPP>=nonKPP everywhere)'}")
    P("")
    verdict = 'PASS' if (not viol and not mono) else 'FAIL'
    P(f"## VERDICT: {verdict}   — {ncells} cells swept, {len(viol)} floor violations, "
      f"{len(mono)} monotonicity breaks")

    open(out_path, 'w').write("\n".join(L) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == '__main__':
    main()
