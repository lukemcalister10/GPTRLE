# DIRECTIVE 2 — raw scratch-evaluation outputs (head 8aed420a store 644d1254, pinned env)

## TASK A run log (verdict)
```
crosscheck max|ev-bandpath| 2025=532.6 2026=461.0

=== FOUR-PLAYER 2026 VERDICT (gate basis, prototype vs at-head) ===
  Josh Ward        at-head26=1782 (band-basis 1719)  proto26=1253  (-27.1%)
  Paul Curtis      at-head26=1162 (band-basis 1093)  proto26=1087  (-0.6%)
  Josh Weddle      at-head26=1628 (band-basis 1642)  proto26=1414  (-13.9%)
  Jack Ginnivan    at-head26=1578 (band-basis 1580)  proto26=1677  (+6.2%)
  Jake Bowey       at-head26=2585 (band-basis 2498)  proto26=2555  (+2.3%)
  Nick Blakey      at-head26=3053 (band-basis 3221)  proto26=3424  (+6.3%)
  A2 flip?  Curtis>Ward: 1087>1253 = False   Weddle>Ward: 1414>1253 = True
  A9 flip?  Ginnivan>Ward: 1677>1253 = True
  A5 Ginnivan vs 1600 floor: proto26=1677 (+77);  Bowey vs 2100: 2555 (+455);  Blakey vs 2600: 3424 (+824)
pack written: /home/user/afl-rl-engine/session_2026-07-02/readpass_pack_M1v7_8aed420a.md
```

## TASK B store-swap regen
```
git-seed identities (f4a4d34):
  rl_model_data.json = 644d1254
  rl_model_data.json.pre_stage0 = 644d1254
  rl_model_data.json.stage0 = 91a3de6b
live store swapped to stage0: 91a3de6b
export exit=0
regenerated-from-stage0 board md5 = c16e1024   (shipped = b8f9e998; reconciled-store regen = 1898ead7)
```

## TASK B follow-up — shipped vs reconciled-regen value diff
```
regen md5 1898ead7 shipped md5 b8f9e998
top-level type: dict keys: ['ALPHA', 'BAND_ANCHOR', 'BASEPK_REG', 'BASE_YEAR', 'BETA_POS', 'BUST_BAND', 'CAPT_CAP', 'CAPT_EXP']
dict diff: only-regen [] only-shipped []
identical top-level values: 40/58; differing keys: ['PVC', 'cohort', 'SCALE', 'CAPT_THRESH', 'PJ', 'MIX', 'CAT_BY_CLUB', 'MECH', 'back', 'PICKEQ']
```

## TASK C offender list
```
player                     pos pick drafted    ev draftval  ratio g25 g26 yrs  status
Jack Watkins               MID    3    2025    18      308   0.06   0   9   1  listed
Flynn Perez            GEN_DEF   35    2025    39      308   0.13   0   5   1  listed
Zac Banch              GEN_FWD    2    2025    45      308   0.15   6   2   1  listed
Flynn Young            GEN_FWD    4    2025    46      308   0.15  12   3   1  listed
Saad El-Hawli          GEN_DEF   13    2024    50      308   0.16   9   7   2  listed
Lachlan Blakiston      KEY_DEF   13    2025    51      308   0.17  16  14   1  listed
Jack Hutchinson            MID    3    2024    56      308   0.18  16   2   2  listed
Mani Liddy                 MID   16    2025    58      308   0.19  13   0   1  listed
Roan Steele                MID    8    2025    70      308   0.23   7  13   1  listed

total offenders (shipped-B5 population): 9; DELISTED among them: 0
```

## TASK D 9->10g dip
```
=== (1) channel trace — canonical synth (MID pk10 avg85, 2025 draft), games 1..14 ===
  g     ev   step     Lc     Lo   Leff  expos shrink  band(b6 nodes)
  1    745          85.0   64.1   64.1    1.0   0.07  [np.float64(47.2), np.float64(70.9), np.float64(84.5), np.float64(97.2), np.float64(107.0), np.float64(117.9)]
  2    745     +0   85.0   65.1   65.1    2.0   0.14  [np.float64(48.7), np.float64(74.2), np.float64(87.1), np.float64(98.6), np.float64(110.6), np.float64(121.8)]
  3    745     +0   85.0   66.1   66.1    3.0   0.21  [np.float64(54.0), np.float64(77.0), np.float64(93.4), np.float64(103.5), np.float64(110.7), np.float64(121.5)]
  4    745     +0   85.0   67.1   67.1    4.0   0.29  [np.float64(57.1), np.float64(78.4), np.float64(94.5), np.float64(105.1), np.float64(110.4), np.float64(121.5)]
  5    745     +0   85.0   68.1   68.1    5.0   0.36  [np.float64(58.9), np.float64(78.4), np.float64(96.2), np.float64(105.8), np.float64(113.6), np.float64(121.5)]
  6   3263  +2518   85.0   69.1   69.1    6.0   0.43  [np.float64(61.3), np.float64(76.5), np.float64(97.6), np.float64(108.9), np.float64(114.9), np.float64(121.6)]
  7   3352    +89   85.0   70.1   70.1    7.0   0.50  [np.float64(62.7), np.float64(82.5), np.float64(99.6), np.float64(108.2), np.float64(116.1), np.float64(121.7)]
  8   3357     +5   85.0   71.1   71.1    8.0   0.57  [np.float64(63.7), np.float64(78.2), np.float64(99.2), np.float64(109.3), np.float64(116.1), np.float64(121.7)]
  9   3538   +181   85.0   72.1   72.1    9.0   0.64  [np.float64(68.2), np.float64(87.9), np.float64(99.5), np.float64(111.9), np.float64(117.1), np.float64(121.7)]
 10   3318   -220   85.0   73.1   68.6   10.0   0.71  [np.float64(64.3), np.float64(85.1), np.float64(98.3), np.float64(108.6), np.float64(115.3), np.float64(121.8)]
 11   3464   +146   85.0   74.0   68.6   11.0   0.79  [np.float64(69.4), np.float64(88.9), np.float64(100.0), np.float64(109.6), np.float64(116.0), np.float64(122.5)]
 12   3531    +67   85.0   75.0   68.6   12.0   0.86  [np.float64(69.5), np.float64(91.5), np.float64(100.2), np.float64(109.8), np.float64(116.5), np.float64(122.5)]
 13   3583    +52   85.0   76.0   68.6   13.0   0.93  [np.float64(70.1), np.float64(92.0), np.float64(100.2), np.float64(109.8), np.float64(117.2), np.float64(123.5)]
 14   3578     -5   85.0   77.0   68.6   14.0   1.00  [np.float64(70.1), np.float64(92.6), np.float64(100.2), np.float64(109.8), np.float64(117.2), np.float64(122.7)]

=== (2) variant grid — dip at 9->10g (and worst dip anywhere in 6..14) per cohort variant ===
     grp  pick  avg     v9    v10  d9->10  worst dip 6..14 (at)
     MID     2   65   3046   3301    +255  -39 at 7->8
     MID     2   85   4342   4137    -205  -205 at 9->10
     MID     2  105   6041   6067     +26  -59 at 7->8
     MID    10   65   2140   2176     +36  -17 at 13->14
     MID    10   85   3538   3318    -220  -220 at 9->10
     MID    10  105   5885   5475    -410  -410 at 9->10
     MID    40   65   1070    950    -120  -120 at 9->10
     MID    40   85   2577   2144    -433  -433 at 9->10
     MID    40  105   5205   4757    -448  -448 at 9->10
 GEN_DEF     2   65   2433   2517     +84  -24 at 7->8
 GEN_DEF     2   85   3977   3814    -163  -163 at 9->10
 GEN_DEF     2  105   6270   6288     +18  -43 at 8->9
 GEN_DEF    10   65   1401   1342     -59  -59 at 9->10
 GEN_DEF    10   85   2939   2813    -126  -126 at 9->10
 GEN_DEF    10  105   5678   5317    -361  -361 at 9->10
 GEN_DEF    40   65    907    802    -105  -105 at 9->10
 GEN_DEF    40   85   2682   2323    -359  -359 at 9->10
 GEN_DEF    40  105   5650   5215    -435  -435 at 9->10
 KEY_FWD     2   65   2109   1971    -138  -138 at 9->10
 KEY_FWD     2   85   5047   4603    -444  -444 at 9->10
 KEY_FWD     2  105   7960   7551    -409  -409 at 9->10
 KEY_FWD    10   65   1879   1622    -257  -257 at 9->10
 KEY_FWD    10   85   4953   4505    -448  -448 at 9->10
 KEY_FWD    10  105   7890   7642    -248  -248 at 9->10
 KEY_FWD    40   65   1483   1320    -163  -163 at 9->10
 KEY_FWD    40   85   4639   4216    -423  -423 at 9->10
 KEY_FWD    40  105   7865   7264    -601  -601 at 9->10
     RUC     2   65   3058   3078     +20  none
     RUC     2   85   4370   4160    -210  -210 at 9->10
     RUC     2  105   6421   6439     +18  -19 at 7->8
     RUC    10   65   1900   1718    -182  -182 at 9->10
     RUC    10   85   4031   3696    -335  -335 at 9->10
     RUC    10  105   7750   7365    -385  -385 at 9->10
     RUC    40   65   1463   1340    -123  -123 at 9->10
     RUC    40   85   3150   2883    -267  -267 at 9->10
     RUC    40  105   6069   5628    -441  -441 at 9->10

=== (3) monotonicity clause check, canonical synth: any gm where value(gm+1)<value(gm) at same avg ===
violations: [(9, -220.0), (13, -5.0)]
```

## TASK E N=5 leakage parse
```
te_gate1_run1.txt: median|IS-WF|=0.00 max|IS-WF|=3 mean=0.47 sep_ok=True seps={GEN_DEF:52/1, GEN_FWD:44/1, KEY_DEF:60/1, KEY_FWD:64/1, MID:52/0}
te_gate1_run2.txt: median|IS-WF|=0.00 max|IS-WF|=3 mean=0.47 sep_ok=True seps={GEN_DEF:52/1, GEN_FWD:44/1, KEY_DEF:60/1, KEY_FWD:64/1, MID:52/0}
te_gate1_run3.txt: median|IS-WF|=0.00 max|IS-WF|=3 mean=0.47 sep_ok=True seps={GEN_DEF:52/1, GEN_FWD:44/1, KEY_DEF:60/1, KEY_FWD:64/1, MID:52/0}
te_gate1_run4.txt: median|IS-WF|=0.00 max|IS-WF|=3 mean=0.47 sep_ok=True seps={GEN_DEF:52/1, GEN_FWD:44/1, KEY_DEF:60/1, KEY_FWD:64/1, MID:52/0}
te_gate1_run5.txt: median|IS-WF|=0.00 max|IS-WF|=3 mean=0.47 sep_ok=True seps={GEN_DEF:52/1, GEN_FWD:44/1, KEY_DEF:60/1, KEY_FWD:64/1, MID:52/0}
```

## TASK F pin.py reissue
```
=== PART 1: ROZEE decomposition ===
trajectory: [(2021, 21, 72.9), (2022, 22, 93.3), (2023, 25, 106.2), (2024, 23, 96.6), (2025, 21, 105.0), (2026, 2, 80.0)]
ev25=3874 -> ev26=2679  total drop -1195 (-31%)
  (a) age/tenure+prior-decay: -827 (-21%)   [ev25 3874 -> ev_age 3047]
  (b) LEVEL pull of the 2g/80 2026: -368 (-9%)   [ev_age 3047 -> ev26 2679]
  _lvl_wt 2025=96.6 2026=96.0 | _lvl_eff 2025=96.6 2026=96.0
  exposure 2025=71 2026=53 (LR=14.0; shrink 1.00->1.00)
  2026 weight-fraction in _lvl_wt: 4%  (games-weighted -> 2g gets small weight)
  COUNTERFACTUAL (discount 2g level pull = ev_age): 3047  -> candidate artifact = +368

=== PART 2: channel decomposition ACROSS cohorts (g<6 pop: 25>=10g, 26 in 1-5g) — uniform or cohort-varying? ===
bucket         n  d_age% d_level%  total%
young(2-4)    14     -48        5     -43
mid(5-7)      12     -31        1     -30
old(8+)       36     -26        5     -21

=== PART 3: hypothesis test ===
(a) avg26-avg25 for g<6 pop: mean=-4.7 median=-1.4 %below-2025=56% (n=62)
(b) 2026 weight-fraction in _lvl_wt: mean=12% median=9% (if small, thin 2026 is ALREADY size-discounted -> level NOT over-weighted)
```

## TASK G3 year-distribution
```
listed+picked players priced: 696

 yrs    n    min     p5    p10    p25    p50   mean
   1   80   0.06   0.16   0.48   0.50   0.50   0.72
   2   91   0.16   0.27   0.50   0.50   0.70   1.06
   3   68   0.14   0.25   0.25   0.42   0.73   1.52
   4   50   0.18   0.23   0.23   0.40   0.62   0.98
   5   64   0.04   0.19   0.20   0.39   1.10   2.01
   6   43   0.02   0.07   0.07   0.14   0.53   1.66
   7   41   0.04   0.08   0.10   0.21   0.99   1.45
   8   41   0.01   0.01   0.05   0.25   0.73   1.68
   9   44   0.01   0.01   0.03   0.13   0.69   1.63
  10   48   0.02   0.09   0.11   0.33   0.77   1.43
  11   33   0.01   0.02   0.04   0.13   0.75   1.13
 12+   93   0.00   0.02   0.04   0.10   0.65   1.26

smoothed (3yr centred MA on the percentile tracks; thin years n<15 rely on the pooling this MA provides):
  p5: y1=0.22  y2=0.23  y3=0.25  y4=0.22  y5=0.16  y6=0.11  y7=0.05  y8=0.04  y9=0.04  y10=0.04  y11=0.05  y12=0.02
  p10: y1=0.49  y2=0.41  y3=0.33  y4=0.23  y5=0.17  y6=0.12  y7=0.07  y8=0.06  y9=0.06  y10=0.06  y11=0.06  y12=0.04
  p25: y1=0.50  y2=0.47  y3=0.44  y4=0.40  y5=0.31  y6=0.25  y7=0.20  y8=0.20  y9=0.24  y10=0.20  y11=0.19  y12=0.12
```
