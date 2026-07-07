# D5 ASK 3c — yr8+ tail floors from the generating rule (0.9 x smoothed clean p5, ND-only)
_Basis: head `8aed420a` store `644d1254`, ND-only LISTED picked (n=590; B5 population). Smoothing: Gaussian kernel over years-in-system, weighted 5th percentile; bandwidth widened per depth until effective n >= 35 (rule stated up front, not tuned). The 11+ slice is POOLED DELIBERATELY (single-depth n runs 30 at d=11 down to 1 at d=21). NUMBERS ONLY — no schedule change without Luke's word._

| depth d | n at d | raw clean p5 | smoothed clean p5 (bw / eff-n) | derived floor 0.9xp5 | current floor |
|---|---|---|---|---|---|
| 1 | 58 | 0.499 | 0.499 (bw 0.75 / eff 89) | **0.449** | 0.45 |
| 2 | 71 | 0.499 | 0.366 (bw 0.75 / eff 120) | **0.329** | 0.35 |
| 3 | 59 | 0.250 | 0.249 (bw 0.75 / eff 109) | **0.224** | 0.28 |
| 4 | 42 | 0.226 | 0.201 (bw 0.75 / eff 90) | **0.181** | 0.21 |
| 5 | 49 | 0.194 | 0.143 (bw 0.75 / eff 85) | **0.129** | 0.13 |
| 6 | 40 | 0.066 | 0.067 (bw 0.75 / eff 78) | **0.060** | 0.09 |
| 7 | 37 | 0.074 | 0.044 (bw 0.75 / eff 70) | **0.040** | 0.05 |
| 8 | 35 | 0.012 | 0.012 (bw 0.75 / eff 69) | **0.011** | 0.05 |
| 9 | 40 | 0.013 | 0.013 (bw 0.75 / eff 72) | **0.012** | 0.05 |
| 10 | 39 | 0.090 | 0.023 (bw 0.75 / eff 69) | **0.021** | 0.05 |
| 11+ (POOLED deliberately) | 120 | 0.014 | 0.014 (pooled, no kernel) | **0.012** | 0.05 |

Notes: (i) depths 1-6 shown for continuity with the signed dev-window schedule (derived from the same generating rule at D3/D4); (ii) the signed schedule's 7+ flat .05 vs the derived tail: the generating rule gives materially LOWER floors from d=8 on — the .05-forever tail binds beyond its generating data; (iii) 11+ pooled composition is dominated by d=11-13 (75/120 rows) — the pooled p5 leans on the younger end of the bucket; (iv) raw vs smoothed at thin depths (d>=9) differ exactly where smoothing is doing its declared job.
