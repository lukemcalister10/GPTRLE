# Notepad — turn response, 2026-06-30 (no-games override: 3 issues resolved)

All three resolved empirically. Engine e0ac9c377d1e, nothing baked.

(1) TWO-MECHANISM — it's ALL-POSITIONS, not rucks-only. The corrected override applies
dv*retain(pos,yrs_sat) for EVERY position in the sat-out branch; the old position-blind staleness floor is
DEAD for still-listed sat-out players. The mids at ~140 were the override's nonKPP factor, not the old floor.
The separate "mediocre-PLAYED" branch (played multiple seasons but poorly) is a different axis (decliner
thread) and is correctly left alone — sat-out players never reach it. No half-fix.

(2) EARLY-YEAR STEEPNESS — it was the LEVEL, not the shape; fixed with plateau-then-decline.
Washout by years-sat: sat1 56%, but sat2 1%, sat3+ 0% -> a still-listed yr2+ sitter SURVIVED THE CULL.
So the 0.22x crush was the terminal washout applied flat from yr2. Re-parameterized to plateau (yr1-2,
survived cull) then decline to terminal by ~yr6:
  RUC     yr1-6: 0.85 0.85 0.74 0.62 0.51 0.40
  KPP     yr1-6: 0.70 0.70 0.60 0.50 0.40 0.30
  nonKPP  yr1-6: 0.50 0.50 0.42 0.35 0.28 0.20   (levels DEFERRED to PVC; the SHAPE is the fix)
Results: Smillie (MID pk7 sat2) 446 -> 892 (crater fixed, docked ~50% not terminal). Sat-out mids
157->297, 141->266 (docked, not cratered). Rucks lifted: Green 364->746, Goad 269->552, Conway 175->321
(years-sat decline preserved; pick order preserved -> confirms draftval baseline over normal-value).

(3) EMMETT vs GREEN/GOAD — NOT locked. With the override Green/Goad rise to 746/552, much closer to Emmett.
The residual is a ruck SIGNAL-THRESHOLD question: full credit -> Emmett 1051; his ~5 injury-cover games @32.8
treated as NOISE -> Emmett = pk27 pedigree = 224 (BELOW Green/Goad). So Emmett in [224..1051], Green/Goad
between. The principle (weak circumstantial ruck signal must not dominate kept pedigree) -> discount Emmett ->
Green/Goad at/above him. Exact discount = a ruck-specific signal-threshold lever, deferred to PVC.

NEXT: baseline=draftval confirmed (normal-value inverts pick order). Levels (B) deferred to PVC, incl. the
kept-but-unproven credit tension (Smillie 892 — club faith vs no-signal). Ruck signal-threshold (Emmett) +
Edwards production-credit are the decliner-adjacent threads. BAKE held: price6 fix + shape-corrected no-games
override bake together once levels + Emmett threshold are set against the PVC and signed off.
