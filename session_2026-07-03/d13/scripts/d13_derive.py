#!/usr/bin/env python3
# D13 ASK3b — RE-DERIVE the retention surface R(cls, log-pick, depth) at finest supported resolution.
# NO engine load (reads d13_normcells.json). Method:
#   norm(cls,d)   = E[winsor(O/V0,2.0) | class, still-listed, depth d]  (developer-inclusive same-depth norm;
#                   the D10 "0.76 daEV form" denominator — strips the survivor-selection common-mode, rising
#                   0.44->1.11 with depth). R1 outcome: daEV(V0) denominator KEPT (blind-dv widened the gap).
#   r_sit(cell)   = winsor(O/V0, 2.0) for the SIT-OUT subset (no qualifying season through Y).
#   Rraw(cls,p,d) = Gaussian-kernel local mean of r_sit over (log-pick, depth), per class; bw grown until
#                   eff-n>=35 (D5 rule). CONTINUOUS over log-pick (never pick-binned — Luke's instruction).
#   R(cls,p,d)    = Rraw / norm(cls,d), clip [0.05, 1.0].
#   Luke's signed law: ISOTONIC NON-INCREASING IN DEPTH at every pick point (a sitter never gains value).
# R2 test: does R vary over pick beyond a +-0.05 ribbon around the pooled (pick-flat) curve at eff-n>=35?
import json, numpy as np
from collections import Counter
d = json.load(open('session_2026-07-03/d13/d13_normcells.json'))
C = [c for c in d['cells'] if c['wc']]
CLASSES = ('nonKPP', 'KPP', 'RUC')
DEPTHS = list(range(1, 7))
def wins(x, cap=2.0): return min(max(x, 0.0), cap)

# ---- per-class same-depth norm (developer-inclusive) ----
norm = {}
for cls in CLASSES:
    for dd in DEPTHS:
        v = [wins(c['O']/max(1e-9, c['V0'])) for c in C if c['cls'] == cls and c['d'] == dd]
        norm[(cls, dd)] = float(np.mean(v)) if v else float('nan')
# deep-tail norm (d6) carried flat for depth>6 (thin)
print("=== per-class same-depth all-draftee NORM E[O/V0] (winsor 2.0) ===")
for cls in CLASSES:
    print("  %-6s "%cls + " ".join("d%d=%.3f"%(dd, norm[(cls,dd)]) for dd in DEPTHS))

# ---- sit-out subset ----
SIT = {cls: [c for c in C if c['cls'] == cls and c['sitout']] for cls in CLASSES}
print("\n=== sit-out cell counts by class ===", {cls: len(SIT[cls]) for cls in CLASSES})

# ---- adaptive-bandwidth Gaussian kernel local mean over (log-pick, depth) ----
def eff_n(w):
    s = w.sum()
    return (s*s)/np.sum(w*w) if s > 0 else 0.0
def kern_mean(cells, logp, dd, bwp, bwd):
    lp = np.array([np.log(min(max(c['pick'], 1), 90)) for c in cells])
    dpt = np.array([c['d'] for c in cells])
    r = np.array([wins(c['O']/max(1e-9, c['V0'])) for c in cells])
    w = np.exp(-0.5*((lp-logp)/bwp)**2) * np.exp(-0.5*((dpt-dd)/bwd)**2)
    return (np.sum(w*r)/np.sum(w) if w.sum() > 0 else float('nan')), eff_n(w), w.sum()
def Rraw_at(cls, pick, dd, target_n=35):
    cells = SIT[cls]; logp = np.log(min(max(pick, 1), 90))
    bwd = 0.75
    for bwp in [0.35, 0.5, 0.7, 0.9, 1.2, 1.6, 2.2, 3.0, 5.0]:
        m, en, _ = kern_mean(cells, logp, dd, bwp, bwd)
        if en >= target_n:
            return m, bwp, en
    # widen depth bw if still thin
    for bwd2 in [1.1, 1.6, 2.5]:
        m, en, _ = kern_mean(cells, logp, dd, 5.0, bwd2)
        if en >= target_n:
            return m, 5.0, en
    m, en, _ = kern_mean(cells, logp, dd, 5.0, 2.5)
    return m, 5.0, en  # widest; declared thin

# ---- evaluation slices (DIAGNOSTIC pick points; NOT derivation bins) ----
PICK_EVAL = [5, 15, 30, 50]     # representative picks for reporting/wiring knots
def isotonic_noninc(vals):      # project onto non-increasing (downward-only running cap = Luke's law, minimal)
    out = list(vals);
    for i in range(1, len(out)):
        if out[i] > out[i-1]: out[i] = out[i-1]
    return out

print("\n=== ASK3b: R(cls, pick, depth) = kernel r_sit / norm, clip[.05,1], then ISOTONIC non-increasing in depth ===")
SURF = {}; BW = {}
for cls in CLASSES:
    SURF[cls] = {}; BW[cls] = {}
    print("\n  --- %s ---" % cls)
    print("   pick |  d1    d2    d3    d4    d5    d6   | bw(logpick)@each depth  eff-n@each")
    for pk in PICK_EVAL:
        raw = []; bws = []; ens = []
        for dd in DEPTHS:
            m, bwp, en = Rraw_at(cls, pk, dd)
            R = wins(m/norm[(cls, dd)] if norm[(cls, dd)] == norm[(cls, dd)] else m, 1.0)
            R = max(R, 0.05)
            raw.append(R); bws.append(bwp); ens.append(en)
        iso = isotonic_noninc(raw)
        SURF[cls][pk] = iso; BW[cls][pk] = (bws, ens)
        print("   %4d | " % pk + " ".join("%.3f" % x for x in iso) + " | " +
              " ".join("%.1f" % b for b in bws) + "  " + " ".join("%d" % e for e in ens))

# ---- R2 TEST: pick variation vs pooled (pick-flat) curve ----
print("\n=== R2 TEST: does R vary materially over pick? (pooled curve = pick-averaged; ribbon +-0.05) ===")
r2_fire = {}
for cls in CLASSES:
    pooled = [np.mean([SURF[cls][pk][i] for pk in PICK_EVAL]) for i in range(6)]
    maxdev = 0.0; where = ''
    for pk in PICK_EVAL:
        for i in range(6):
            dev = abs(SURF[cls][pk][i] - pooled[i])
            if dev > maxdev: maxdev = dev; where = "pk%d d%d" % (pk, i+1)
    r2_fire[cls] = bool(maxdev > 0.05)
    print("  %-6s pooled=[%s] maxdev=%.3f @%s -> %s" % (
        cls, " ".join("%.2f" % x for x in pooled), maxdev, where,
        "PICK-CONDITIONED (R2 fires)" if r2_fire[cls] else "flat-over-pick (wire pooled+depth-constraint)"))

# ---- OLD vs NEW per class (pooled comparison to wired R_SIT) ----
OLD = {'nonKPP': [0.429, 0.404, 0.410, 0.432, 0.437, 0.424],
       'KPP':    [0.468, 0.380, 0.325, 0.278, 0.253, 0.266],
       'RUC':    [0.674, 0.547, 0.503, 0.472, 0.435, 0.435]}
print("\n=== OLD (wired v2.2) vs NEW (pooled over eval picks, iso) per class ===")
for cls in CLASSES:
    new_pooled = isotonic_noninc([np.mean([SURF[cls][pk][i] for pk in PICK_EVAL]) for i in range(6)])
    print("  %-6s OLD=[%s]" % (cls, " ".join("%.3f" % x for x in OLD[cls])))
    print("         NEW=[%s]" % (" ".join("%.3f" % x for x in new_pooled)))

def _f(x): return round(float(x), 4)
json.dump(dict(norm={f"{k[0]}|{k[1]}": _f(v) for k, v in norm.items()},
               SURF={cls: {str(pk): [_f(x) for x in SURF[cls][pk]] for pk in SURF[cls]} for cls in CLASSES},
               r2_fire={k: bool(v) for k, v in r2_fire.items()}, PICK_EVAL=[int(x) for x in PICK_EVAL], OLD=OLD),
          open('session_2026-07-03/d13/d13_surface.json', 'w'), indent=1)
print("\nwrote session_2026-07-03/d13/d13_surface.json")
