# D12 ASK 4 — READ-ONLY DIAGNOSTICS (facts for Luke's rulings; NOTHING WIRES)

**STATE: read at CURRENT v2.2 `af1fc6aa` (engine unchanged by these; zero writes to the engine).** Per the statistics rule: finest resolution the sample supports, thin pools declared.

## 4a — V0 MONOTONICITY PROBE

**Cumming|2025|7 (MID, V0 1864) vs Robey|2025|9 (MID, V0 1882) — feature-by-feature:**

| player | pk | effpk | draft age | draft yr | pr = price6 (band base) | iso_corr | V0 = pr×iso |
|---|---|---|---|---|---|---|---|
| Sam Cumming | 7 | 7 | 19 | 2025 | 1845.7 | 1.0100 | 1864.2 |
| Sullivan Robey | 9 | 9 | 18 | 2025 | 1906.4 | 0.9870 | 1881.6 |

**NAMED CHANNEL: the band base price `price6` (the GBR pole/quantile surface), NOT pick, age, or iso.** The inversion is *born* in `pr`: Robey's pick-9 band base (1906.4) exceeds Cumming's pick-7 base (1845.7) — a ~3.3% local band wobble. It is **not** effpk≠nominal (both effpk = nominal, 7 and 9), **not** draft-age (both wage = 1.0), and iso actually *favors* Cumming (1.010 > 0.987). The isotonic guard `iso_corr` is a per-position, par-synth, multiplicative correction **isotonic over EFFECTIVE pick** (±1.3% here) — too gentle to overcome the ~3.3% raw band inversion between two real players. This is exactly the "wobble the iso guard misses because it is isotonic over effective pick" hypothesis, confirmed.

**Nominal-pick V0 inversions, all positions × current-roster cohorts (ND, non-delisted, real pick, yr≥2015):** **1,853 inverted pairs** (earlier nominal pick, lower V0). Two mechanisms:
- **band wobble** (Cumming/Robey type, ~1–3%): small, local, within-cohort;
- **draft-age / mature-age re-draftees** (dominant in magnitude): e.g. MID pk24 Tim Kelly V0 71 (mature-age; `wage=clip(1−(age−20)/6)` crushes the pole term) sits below pk25 kids at ~940 — the guard is over pick, not age.

Top later-pick-higher-V0 per position (illustrative): RUC Emmett pk27 (1536) > Green pk16 (1045); KEY_FWD Oscar Allen pk21 (696) > Coleman-Jones pk20 (486); KEY_DEF Sam Taylor pk28 (649) > Trainor pk21 (504).
**FACT for Luke:** a nominal-pick monotonicity guard would bind on 1,853 pairs; most are the age channel (legitimate — a 24-yo pick-24 is worth less than an 18-yo pick-25) plus a thin band-wobble tail. Luke rules whether a nominal-pick guard becomes law.

## 4b — NEVER-PLAYER DEPTH PATH (under the WIRED R_SIT table; a never-player is λ=0 at every depth → value = R_SIT[cls][d−1] × V0)

| class | R_SIT d1..d6 | RISES between depths? |
|---|---|---|
| nonKPP | .429 / .404 / .410 / .432 / .437 / .424 | **YES** — d2→d3→d4→d5 |
| KPP | .468 / .380 / .325 / .278 / .253 / .266 | **YES** — d5→d6 |
| RUC | .674 / .547 / .503 / .472 / .435 / .435 | no (monotone down, flat tail) |

**ANSWER: YES — a never-player's price can RISE between depths** (nonKPP d2→d5; KPP d5→d6). The wired retention curve is **non-monotone in depth**, so a player who never plays can be priced higher in year 4 than year 2. Fact for Luke's monotone-in-depth shape-constraint ruling.

**Josh Smillie (key `josh-smillie`, pk7 MID/nonKPP, drafted 2024 → debut 2025, 0 games 2026, V0 1864.2):**
- end-Yr1 (depth 1, 0 games): 0.429 × 1864 = **800**
- projected end-Yr2 (depth 2, 0 games): 0.404 × 1864 = **753**
- actual v2.2 EV (mid-2026, depth-2 in progress, τ=1+0.58^1.5): **779** (interp between the depth-1/2 knots × V0)
- **Yr1→Yr2 at zero games: 800 → 753 (falls −47)** — nonKPP declines depth 1→2 even though the same curve rises depth 2→5. (Smillie shares V0 with Cumming — both pk7 MID.)

## 4d — RUC V0 CONTEXT (feeds Luke's nerf number, next directive — MEASUREMENT ONLY, no cap wired)

**Full RUC roster V0/PVC ratio distribution (n=31 ND, non-delisted):** min 0.92 · p25 1.55 · median **1.73** · p75 2.02 · max **2.52** · mean 1.77. Ruck start values run ~1.7–1.8× the old PVC — the `h-ruc-startvalue-hot` flag, quantified.

**Five hottest (V0/PVC):** Emmett **2.52×** (V0 1536 / PVC 609) · Witts 2.36× (727/308) · Meek 2.34× (719/308) · Briggs 2.11× (1229/583) · Gawn 2.07× (1231/596).

**Emmett V0 decomposition:** V0 1536 = raw_ev(draft-yr) × iso_corr(RUC, effpk 27) = 1767 × 0.869. PVC(draftval) = 609.

**Emmett at V0/PVC caps (arithmetic, no cap wired):** cap = min(V0, k × PVC) with PVC = 609:
| cap k | capped V0 | vs current V0 1536 |
|---|---|---|
| 1.3× | 792 | −744 |
| 1.5× | 914 | −622 |
| 2.0× | 1218 | −318 |

**MEASUREMENT CAVEAT (Luke-facing):** Emmett's *current* v2.2 value **1338** is **production-driven, not V0-gated** — he has 5 games (nseas_pro=1), tenure 1 < ruck-onset 4, so neither the stalled nor mediocre V0 cap fires; his ev is the production price `e_full`. A pure **V0-floor** cap therefore would **not move his 1338 today** — it would only bind when he sits out or on the floor. To move played young rucks, the ruck nerf must target the ruck **raw_ev/band** itself (the source of both V0 and the production price), not just the V0 floor. This is the key fact for designing the nerf.

## 4c — RETENTION REVIEW — ROLLED TO FOLLOW-UP (announced, NOT degraded)

Per the session split-point and the binding statistics rule, 4c re-runs the **locked retention harvest** under three new conditionings **at the finest resolution the sample supports** (kernel over log-pick × depth). Doing it at coarse pick bins would be the exact wide-bin artifact the rule bans, so it is **rolled to a scoped follow-up directive (D13)** rather than degraded. Scope carried forward verbatim:
- **(i) selection/survivor:** cohort sizes entering/exiting each depth cell, who exits (delist gate), direction of bias; busts-at-zero are IN the sample — state what that does to the classic survivor story.
- **(ii) KPP severity:** denominator (pedigree-pole-inflated V0) vs numerator (lower realized outcomes); KPP retention recomputed with a **position-blind band price** as alternative denominator, side-by-side with the wired form; d4–6 thin cells 10/4/3.
- **(iii) pedigree conditioning:** retention harvest **split by pick band**, kernel over log-pick × depth, every pooled slice declared — does sit-out retention vary by draft pedigree? (Tests whether the current flat-across-pick retention is itself a wide-bin artifact.)

This needs a fresh harvest load at finest resolution — the XHIGH driver — and is delivered whole in D13 rather than coarsened here.
