# D14 ASK2 — KPP RETENTION FLOOR (Owner Override O1) + ASK3d ruck ladder   (engine v2.4 7c199a1f)

## Floor-binding map — KPP sit-out retention := max(KPP, nonKPP). Cells where nonKPP is SELECTED (floor binds).
(retention R at depth d1..d6; **bold** = nonKPP>KPP → floor binds)

| pick | d1 | d2 | d3 | d4 | d5 | d6 |
|--:|:--|:--|:--|:--|:--|:--|
| 5 | 0.660 | 0.487 | **0.446** | **0.446** | **0.446** | **0.314** |
| 15 | **0.707** | **0.479** | **0.479** | **0.479** | **0.479** | **0.307** |
| 30 | **0.649** | **0.436** | **0.422** | **0.414** | **0.414** | **0.303** |
| 50 | 0.642 | 0.407 | 0.351 | 0.334 | 0.334 | 0.329 |

Floor BINDS at (pick,depth): [(5, 3), (5, 4), (5, 5), (5, 6), (15, 1), (15, 2), (15, 3), (15, 4), (15, 5), (15, 6), (30, 1), (30, 2), (30, 3), (30, 4), (30, 5), (30, 6)]
-> binds predominantly d3+ (KPP decays faster than nonKPP at depth); shallow d1-2 KPP mostly ≥ nonKPP (no bind). Matches the D13 finding (expected d3+).

## Depth monotonicity of the FLOORED KPP surface (re-verified numerically):
  pk 1: R(d1..d6)=[0.66, 0.487, 0.446, 0.446, 0.446, 0.314]  non-increasing=True
  pk 3: R(d1..d6)=[0.66, 0.487, 0.446, 0.446, 0.446, 0.314]  non-increasing=True
  pk 5: R(d1..d6)=[0.66, 0.487, 0.446, 0.446, 0.446, 0.314]  non-increasing=True
  pk 8: R(d1..d6)=[0.675, 0.461, 0.46, 0.46, 0.46, 0.311]  non-increasing=True
  pk15: R(d1..d6)=[0.707, 0.479, 0.479, 0.479, 0.479, 0.307]  non-increasing=True
  pk30: R(d1..d6)=[0.649, 0.436, 0.422, 0.414, 0.414, 0.303]  non-increasing=True
  pk50: R(d1..d6)=[0.642, 0.407, 0.351, 0.334, 0.334, 0.329]  non-increasing=True
  pk80: R(d1..d6)=[0.642, 0.407, 0.351, 0.334, 0.334, 0.329]  non-increasing=True
  ALL non-increasing = True  (max of two isotonic-non-increasing curves is non-increasing ✓)

## KPP retention anchors (CONTROL 8aed420a · v2.3 f3e537ba · v2.4 — board ev; V0 in parens)
| player (cls·pick) | CONTROL | v2.3 | v2.4 |
|---|--:|--:|--:|
| Riak Andrew (KPP·pk55) | 235 (-1.0) | 330 (613.9) | 257 (477.1) |
| Matt Whitlock (KPP·pk27) | 426 (-1.0) | 327 (615.8) | 351 (624.3) |
| Jack Whitlock (KPP·pk33) | 1022 (-1.0) | 1031 (615.8) | 1031 (578.6) |
| Harrison Ramm (KPP·pk59) | 216 (-1.0) | 318 (394.1) | 318 (394.1) |
| Matt Allison (KPP·pk27) | 12 (-1.0) | 12 (615.8) | 12 (624.3) |
| Aaron Cadman (KPP·pk1) | 2813 (-1.0) | 2818 (1016.0) | 2818 (970.1) |
| Jed Walter (KPP·pk3) | 1410 (-1.0) | 1403 (987.3) | 1403 (970.1) |
| Ethan Read (KPP·pk9) | 1261 (-1.0) | 1283 (871.8) | 1283 (844.0) |

## Floor-saves recount (v2.4, board path; RUC recomputed off capped V0)
floor-saves total=54 (RUC 1); pure lower bound (lowered=0, non-ND moved=0 — verified in gates B5).
saves (player · pos · pick · raw ev_prefloor · floor):
  Paddy Dow              MID      pk 3  raw   13 -> floor  111  (+98)
  Chayce Jones           MID      pk 9  raw    9 -> floor   84  (+75)
  Steele Sidebottom      MID      pk11  raw    3 -> floor   74  (+71)
  Oliver Wiltshire       GEN_FWD  pk61  raw   13 -> floor   80  (+67)
  Jaeger O'Meara         MID      pk 1  raw   62 -> floor  128  (+66)
  Luke Pedlar            GEN_FWD  pk11  raw   66 -> floor  121  (+55)
  Billy Cootee           MID      pk42  raw   30 -> floor   82  (+52)
  Jacob Hopper           MID      pk 7  raw   42 -> floor   94  (+52)
  Conor Stone            GEN_DEF  pk15  raw   25 -> floor   72  (+47)
  Phoenix Gothard        GEN_FWD  pk12  raw  330 -> floor  369  (+39)
  Bailey Laurie          GEN_FWD  pk23  raw   21 -> floor   60  (+39)
  Jack Martin            GEN_FWD  pk 3  raw   44 -> floor   82  (+38)
  Jade Gresham           GEN_FWD  pk18  raw   13 -> floor   47  (+34)
  Liam Stocker           GEN_DEF  pk19  raw    2 -> floor   34  (+32)
  Callum Ah Chee         GEN_FWD  pk 8  raw   38 -> floor   70  (+32)
  Brandon Starcevich     GEN_DEF  pk18  raw    6 -> floor   36  (+30)
  Jake Melksham          KEY_FWD  pk10  raw   11 -> floor   41  (+30)
  Nicholas Coffield      GEN_DEF  pk 8  raw   16 -> floor   44  (+28)
  Sam Butler             GEN_FWD  pk23  raw   60 -> floor   87  (+27)
  Charlie Spargo         GEN_FWD  pk29  raw    1 -> floor   28  (+27)

## ASK3d ruck ladder written: 172 rucks -> d14_ask3d_ruck_ladder.md (V0/PVC per rung; cap 1.73 in force)
