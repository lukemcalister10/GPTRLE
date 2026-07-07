# D13 ASK 3 — RETENTION SURFACE RE-DERIVATION

**STATE:** CONTROL = canonical `8aed420a` · PREVIOUS = CANDIDATE v2.2 `af1fc6aa` · CURRENT = CANDIDATE v2.3.

> <<<LUKE 2026-07-03>>> "I'm still not happy with the sit out penalty and think it is excessive especially for KPP players." + "A player should never gain value by sitting out and doing nothing."

## 3a — DIAGNOSTICS

**(i) Selection.** The sit-out pool collapses with depth — the survivor-selection Luke flagged. Complete-window sit-out cell counts by class × depth:

| class | d1 | d2 | d3 | d4 | d5 | d6 |
|---|---|---|---|---|---|---|
| nonKPP | 971 | 363 | 143 | 53 | 22 | 7 |
| KPP | 343 | 161 | 73 | 30 | 14 | 7 |
| RUC | 129 | 61 | 40 | 17 | 12 | 4 |

The **same-depth all-draftee daEV norm E[O/V0] RISES with depth** (nonKPP 0.46→1.08, KPP 0.42→1.22, RUC 0.30→1.13) — deep survivors are increasingly the developers. Dividing sit-out realization by this rising norm **strips the survivor-selection common-mode**. Exit-by-pick-band (Luke's mechanism): at depth 2 the high picks (1-20) exit at 8-14% vs deep picks (21+) 18-28% — deep picks exit faster, biasing deep-cell survivors toward high picks; supports pick-conditioning.

**(ii) KPP severity — denominator vs numerator.** KPP mean forward outcome O=201 vs nonKPP 283; KPP V0/dv=**0.90** (BELOW pick value — *not* pole-inflated). Recomputing retention with a position-blind (dv) denominator does not close the KPP-vs-nonKPP gap — it **widens** it (0.065→0.079). KPP severity is **numerator-driven** (KPP sit-outs realize less forward output), not denominator-driven. Thin deep cells: KPP d4/d5/d6 raw n=30/14/7.

## 3c — PRE-SPECIFIED DECISION RULES (outcomes)

- **R1 (denominator):** blind-dv did NOT close ≥half the gap (widened it; KPP V0/dv=0.90). → **KEEP the daEV (V0) form.**
- **R2 (pedigree/pick):** evaluation slices vary over pick well outside the ±0.05 ribbon (maxdev 0.13–0.21, all classes). → **wire the PICK-CONDITIONED surface** — the flat-across-pick curve was the artifact.

## 3b/3d — OLD vs NEW curves (pooled over eval picks; isotonic non-increasing in depth) per class

| class | old d1..d6 (v2.2, VIOLATED law) | new d1..d6 (v2.3, non-increasing) |
|---|---|---|
| nonKPP | 0.429 0.404 0.410 0.432 0.437 0.424 | 0.613 0.437 0.423 0.395 0.376 0.272 |
| KPP | 0.468 0.380 0.325 0.278 0.253 0.266 | 0.657 0.426 0.324 0.211 0.206 0.205 |
| RUC | 0.674 0.547 0.503 0.472 0.435 0.435 | 0.865 0.630 0.619 0.571 0.534 0.468 |

(The surface is pick-conditioned; these pooled rows are for OLD/NEW comparison only. Full knotted surface in the engine `R_SURF`.)

## 3d — ANCHOR SET (three-column board: CONTROL · v2.2 · v2.3)

| player (cls·pick) | CONTROL | v2.2 | v2.3 | Δ v2.2→v2.3 |
|---|---|---|---|---|
| Annable nonKPP·6 | 936 | 1414 | **1485** | +71 |
| Patterson nonKPP·5 | 982 | 849 | **908** | +59 |
| Taylor nonKPP·11 | 690 | 693 | **733** | +40 |
| Ison nonKPP·47 (ns1, played) | 212 | 538 | **538** | +0 |
| Smillie nonKPP·7 | 896 | 779 | **993** | +214 |
| Riak Andrew (KPP sitter) | — | 263 | **330** | +67 |
| Matt Whitlock (KPP sitter) | — | 264 | **327** | +63 |
| **sit-out family agg (n137)** | 41139* | 43903 | **46764** | +2861 |
| **2025 cohort total (n102)** | 47416 | 55836 | **57009** | +1173 |

_*CONTROL sit-out set n=150 (canonical unprorated nseas); v2.x set n=137 (prorated qualifier). Δ column is the clean v2.2→v2.3 over the fixed 137._

**Smillie (Luke's eyeball, non-increasing):** board 779→993; projected end-Yr1-at-zero-games=1108, end-Yr2-at-zero-games=848 → **non-increasing** (a sit-out year cannot raise his value). Every named anchor's yr1→yr2-at-zero is non-increasing (Luke's signed law holds).

## 3e — HONESTY CLAUSE

After all corrections, KPP retention is **comparable to (even above) nonKPP at depths 1–2** (KPP 0.66/0.43 vs nonKPP 0.61/0.44 — the early-career harshness Luke flagged is substantially relieved, KPP d1 0.468→0.657) but remains **materially harsher at depths 3+** (KPP 0.32/0.21/0.21 vs nonKPP 0.42/0.39/0.38). This residual is **data-derived** (numerator-driven per R1: KPP sit-outs realize less forward output) and rests on **thin, declared-pooled deep cells** (n=30/14/7). This is the corrected curve; any further KPP softening is Luke's signed owner override, not a quiet re-tune. In practice every current KPP sit-out (mostly d1–2) moves **up** v2.2→v2.3.
