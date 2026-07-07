# D14 ASK1 — V0 BOARD CURVE params + moves   (engine v2.4 7c199a1f)

## Order of operations (declared): ruck cap (ASK1 RL_RUC_PRIOR_CAP=1.73) applies FIRST -> _v0_raw; THEN the curve is FITTED on _v0_raw; board V0 := V0*(pos,draft-age,recorded pick).

## Cell fits — eff-n / pooling (R1). Pick bands below are DIAGNOSTIC slices only, never derivation bins.

| cell | n | min eff-n | grid@Hmax | V0*[pk1] | V0*[pk8] | V0*[pk20] | V0*[pk40] | V0*[pk60] |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| MID age≤18 | 427 | 35.3 | 0/90 | 2554 | 1792 | 991 | 571 | 445 |
| KEY_FWD age≤18 | 178 | 35.0 | 0/90 | 970 | 856 | 668 | 486 | 342 |
| KEY_DEF age≤18 | 152 | 35.1 | 0/90 | 895 | 856 | 678 | 550 | 430 |
| GEN_FWD age≤18 | 284 | 35.6 | 0/90 | 1631 | 1401 | 808 | 485 | 390 |
| GEN_DEF age≤18 | 295 | 35.5 | 0/90 | 1163 | 874 | 657 | 500 | 423 |
| RUC age≤18 | 72 | 35.0 | 0/90 | 1220 | 1087 | 986 | 803 | 604 |
| non-RUC mat age19 (pooled 5pos) | 149 | 35.0 | 0/1080 | 558 | 550 | 530 | 530 | 465 |
| non-RUC mat age21 (pooled 5pos) | 149 | 35.0 | 0/1080 | 550 | 545 | 521 | 337 | 287 |
| non-RUC mat age24 (pooled 5pos) | 149 | 35.0 | 0/1080 | 537 | 537 | 508 | 167 | 128 |
| RUC mat age19 | 14 | 11.9 | 1080/1080 | 757 | 698 | 675 | 659 | 649 |
| RUC mat age22 | 14 | 11.9 | 1080/1080 | 731 | 673 | 650 | 633 | 624 |
| RUC mat age25 | 14 | 11.9 | 1080/1080 | 702 | 644 | 622 | 606 | 597 |

**R1 (pooling) outcome:** age≤18 per-position fits reach eff-n≥35 with bandwidth NOT maxed (grid@Hmax=0/90) — the finest resolution the sample supports. Every mature exact (pos×age) cell is eff-n<35 even at max bandwidth → pooled: the 5 non-RUC positions pool into one age-resolved surface (mature V0 is age-dominated & position-washed in-sample; DECLARED), RUC mature kept separate (own level, eff-n≈12 flagged). Mature stays differentiated from age-18 and monotone-decreasing in draft-age.

## Roster move summary (V0, real ND n=1571): n_up=831 · n_down=740 · unchanged=0 · max|ΔV0|=1354 (Nicholas Naitanui)

### TOP-10 V0 UP (NAMED · CONTROL 8aed420a · v2.3 f3e537ba · v2.4)
| player | cell | CONTROL | v2.3 | v2.4 | Δ(v2.3→v2.4) |
|---|---|--:|--:|--:|--:|
| Orren Stephenson | RUC 2011 pk83 age29 | -1 | 57 | 549 | +492 |
| Tim Kelly | MID 2017 pk24 age23 | -1 | 71 | 488 | +417 |
| Dean Towers | GEN_FWD 2012 pk26 age22 | -1 | 99 | 485 | +386 |
| Jordan De Goey | GEN_FWD 2014 pk6 age18 | -1 | 1071 | 1454 | +383 |
| Nakia Cockatoo | GEN_FWD 2014 pk11 age18 | -1 | 1071 | 1346 | +275 |
| Ben Hudson | RUC 2003 pk52 age24 | -1 | 342 | 609 | +268 |
| Darcy Fort | RUC 2018 pk65 age25 | -1 | 336 | 595 | +259 |
| Shaun Mannagh | GEN_FWD 2023 pk36 age26 | -1 | 5 | 239 | +234 |
| Chris Bryan | RUC 2004 pk62 age22 | -1 | 395 | 624 | +229 |
| Liam Ryan | GEN_FWD 2017 pk26 age21 | -1 | 264 | 489 | +225 |

### TOP-10 V0 DOWN
| player | cell | CONTROL | v2.3 | v2.4 | Δ(v2.3→v2.4) |
|---|---|--:|--:|--:|--:|
| Nicholas Naitanui | RUC 2008 pk2 age18 | -1 | 2574 | 1220 | -1354 |
| Matthew Kreuzer | RUC 2007 pk1 age18 | -1 | 2381 | 1220 | -1161 |
| Andrew Walker | GEN_DEF 2003 pk2 age18 | -1 | 2166 | 1163 | -1003 |
| Callum Mills | GEN_DEF 2015 pk3 age18 | -1 | 2094 | 1103 | -990 |
| Harley Bennell | GEN_FWD 2010 pk2 age18 | -1 | 2581 | 1631 | -950 |
| Izak Rankine | GEN_FWD 2018 pk3 age18 | -1 | 2573 | 1631 | -941 |
| Jack Billings | GEN_FWD 2013 pk3 age18 | -1 | 2573 | 1631 | -941 |
| Jack Martin | GEN_FWD 2012 pk3 age18 | -1 | 2573 | 1631 | -941 |
| Colin Sylvia | GEN_FWD 2003 pk3 age18 | -1 | 2573 | 1631 | -941 |
| Lachie Whitfield | GEN_DEF 2012 pk1 age18 | -1 | 2084 | 1163 | -921 |

## R2 — V0 movers >35% : 91 (age18=28, mature=63). WIRED anyway (the wobble is the disease). Full list -> d14_r2_movers.tsv. Board-ev impact of the mature lifts is ≤ a few points (production-driven veterans); listed in the write-up.

## Cumming / Robey  (CONTROL · v2.3 · v2.4 — V0)
| player (cell) | CONTROL | v2.3 | v2.4 |
|---|--:|--:|--:|
| Sam Cumming (MID 2025 pk7 age18) | -1 | 1859 | 1876 |
| Sullivan Robey (MID 2025 pk9 age18) | -1 | 1859 | 1686 |

## Emmett (ruck cap 1.73 default + curve interaction)
| player (cell) | CONTROL | v2.3 | v2.4 |
|---|--:|--:|--:|
| Louis Emmett (RUC 2025 pk27 age18) | -1 | 1054 | 955 |

Emmett explicit: ruck cap 1.73×PVC binds his prior FIRST (_v0_raw=1054 at v2.3), then the RUC age18 curve at pk27 sets V0*=955 (ev 1054→1054).

## Cross-draft dispersion (same pos×draft-age×pick, ≥2 draft years; 318 such groups): BEFORE(v2.3) max spread = 507 SCAR → AFTER(v2.4) max spread = 0 (0 by construction — curve is a function of pos×age×pick only).
