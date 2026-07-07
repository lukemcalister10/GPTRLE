# D5 ASK 2 — M1+v7 PER-TERM DECOMPOSITION (each term toggled OFF individually against the candidate basis)
_Sequential term-off engine builds + same-builder (7147) matrix rebuilds. Terms of the overlay: **M1** = the level up-branch lift (`_inferM1`, S_M1=0.46 partial current-over-recency credit); **v7-cB** = upper-quantile band compression (cB=0.47·clip((effs−1)/3), squeezes bb[3]/bb[4] toward the median); **v7-asc** = age-scaled q97 tail (asc: 1.0@20y → 0.40@27y on bb[5]). M2 (exposure proration) rides in the candidate basis; its own toggle (RL_EXPO_F=1) shown as context. Nothing wired anywhere._

## The term table (state = candidate with ONE term off; effect of a term = candidate row − its off row)
| state | A2 Curtis/Ward | 2020 cohort d4/d5/d6 idx | new-B1 avg row (d1..d7) | new-B1 verdict | A3 (pre-LTI) | B5 count | note |
|---|---|---|---|---|---|---|---|
| CANDIDATE (all on) | 0.875 (1163/1329) | 97/98/95 | 1:100 2:130 3:138 4:148 5:142 6:134 7:119 | PASS pk4 147.6 | 0.658 | 82 | baseline |
| M1 OFF | 0.737 (979/1329) | 94/92/93 | 1:100 2:130 3:138 4:145 5:138 6:130 7:115 | PASS pk4 145.2 | 0.692 | 82 | M1 effect = Curtis +184 lift, A3 −0.034, 2020/B5 ~nil |
| v7-cB OFF | 0.822 (1358/1653) | 105/106/103 | 1:100 2:132 3:143 4:157 5:154 6:145 7:128 | PASS pk4 156.6 | 0.659 | 76 | cB effect = the band squeeze: Curtis −195, Ward −324 |
| v7-asc OFF | 0.858 (1254/1462) | 105/106/102 | 1:100 2:131 3:142 4:154 5:151 6:142 7:126 | PASS pk4 154.3 | 0.666 | 53 | asc effect = the age-tail markdown: 2020 + B5 owner |
| M2 OFF (RL_EXPO_F=1, context) | 0.873 (1156/1324) | — | — | — | 0.642 | 83 | M2 effect = A3 +0.016, else ~nil |
| CONTROL / HEAD (all off) | 0.652 (1162/1782) | 109/110/110 | 1:100 2:132 3:146 4:160 5:158 6:148 7:131 | PASS pk4 160.5 | 0.692 | 51 | head engine, same-builder control matrix |

## (b) WHO owns the 2020 markdown — per-term markdown on the 2020 cohort (d4-6 value, candidate vs each term-off matrix)
| term (turned ON at the margin) | 2020 d4-6 markdown | markdown % on top-quartile | middle | bottom half | Spearman(value, Δ%) |
|---|---|---|---|---|---|
| M1 | +3.9% | +4.6% | +0.1% | -0.0% | +0.466 (p=0.00065) |
| v7-cB | -8.0% | -6.8% | -15.1% | -8.8% | -0.024 (p=0.87) |
| v7-asc | -7.9% | -5.0% | -19.4% | -33.6% | +0.706 (p=1e-08) |
| WHOLE OVERLAY (control → candidate) | -11.6% | -7.2% | -30.4% | -32.5% | +0.527 (p=8.5e-05) |
