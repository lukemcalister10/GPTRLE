# GATE-1 formal re-run at head 8aed420a (2026-07-01)
Harnesses: engine/rl_after/_gate1_wf.py (leakage-guarded IS-vs-WF held-out) + _gate1_picksplit.py (pole pedigree by pick).
Run at head md5 8aed420a, RL_PRIOR_TREES matched at 150 IS/WF (gap=pure leakage, tree-robust). PASS.

## _gate1_wf.py — leakage-guarded within-player, % of PAR-value (WF held-out vs in-sample IS)
5 cohorts held out (2014-2018), ~12,650 WF rows each. IS and WF medians within <=3 pts everywhere => leakage ~0.
  MID     GOOD n=53  WF[T0:13 T1:24 T2:49 T3:61 T4:60 T5:55]  IS[13 24 48 60 59 58]
  MID     BUST n=15  WF[ 0  0  0  0  0  0]
  GEN_FWD GOOD n=41  WF[22 29 46 61 55 43]  IS[22 28 49 61 56 41]
  GEN_FWD BUST n=11  WF[ 1  1  1  1  1  1]
  KEY_FWD GOOD n=22  WF[31 31 60 78 82 69]  IS[31 31 60 77 81 67]
  KEY_FWD BUST n= 5  WF[ 1  1  1  1  1  1]
  GEN_DEF GOOD n=50  WF[20 27 50 53 65 60]  IS[20 28 51 53 66 62]
  GEN_DEF BUST n= 8  WF[ 1  1  1  1  1  1]
  KEY_DEF GOOD n=30  WF[18 27 58 65 60 63]  IS[18 27 58 65 59 61]
  KEY_DEF BUST n= 4  WF[ 1  1  1  1  1  1]
VERDICT: leakage-free (IS~=WF, tree-matched); clean good/bust separation (GOOD -> 43-82% of par by T3-5, BUST 0-1%);
no violent yr0/1 moves; upside-fix T5 zone shows no break. Same shape as the 7f7d7f76 pass.

## _gate1_picksplit.py — future-GOOD value % of par, by pick band (leakage-guarded WF)
  HIGH pk<=12  n= 51  [T0:28 T1:57 T2:68 T3:76 T4:80 T5:74]   (pedigree priced EARLY)
  LATE pk>=25  n=116  [T0:13 T1:15 T2:20 T3:17 T4:36 T5:44]   (low early, climbs with production)
VERDICT: pole prices pedigree before proven (high-pick reads high early vs late-pick near-floor). Early level more
conservative than 7f7d7f76 (28% vs 53% @draft), consistent with the gentler-upside + no-games changes; shape/separation intact.

## Disposition
GATE-1 PASSES at head 8aed420a on both sub-tests. Known residual (unchanged, for Luke's eye, NOT a fail):
good players top out ~43-82% of par-value = the MATURITY-EASING / "84% question".
