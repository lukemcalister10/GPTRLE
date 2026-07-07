# D4 INSTRUMENT AUDIT — ship_gates_check.py vs frozen SHIP_GATES.md (764a0d91 + logged amendments)
_2026-07-02 · head `8aed420a` store `644d1254` · audited BEFORE any verdict this session; fixes wired same pass._

## A8 FIRST — Luke's arithmetic catch, resolved on the printout
Scripted expression as found (verbatim, `ship_gates_check.py` pre-fix):
```
b, t = E('Sam Berry'), E('Elijah Tsatas')
gate('A8', True, 'PASS' if b > 2 * t else 'FAIL', f'Berry={b:.0f} vs 2x Tsatas={2*t:.0f} (Tsatas={t:.0f})')
```
Raw values at head: **Berry = 3473.0, Tsatas = 1083.0**, 2×Tsatas = 2166.0.

| candidate | test on the printout | verdict |
|---|---|---|
| missing 2× (expression tests b > t) | expression contains `2 * t` literally | **NOT IT** |
| ±20% tolerance leak (b > 1.6t) | no tolerance term anywhere in A8 | **NOT IT** |
| display ambiguity | report string "Berry=3473 **vs 2x Tsatas=2166**" — the 2166 IS 2×Tsatas, but reads as raw Tsatas; Luke's 2×2166=4332>3473 arithmetic is the natural reading | **THE DEFECT** |

Both reported passes are **GENUINE literal-2× passes**: engine 3473 ≥ 2×1083 (ratio 3.21×); board-path 2199 ≥ 2×568 (ratio 3.87× — D3 ruler used the same 2×-in-display convention). **Fix wired:** detail string now prints raw values + explicit ratio (`Berry=3473 Tsatas=1083 ratio=3.21x (need >=2.00x)`), and `>` → `>=` per the frozen wording "by at least 2x". Printout artifact: `session_2026-07-02/d4_a8_audit.txt`.

## FULL GATE-LINE AUDIT — one row per gate
| gate | frozen wording (764a0d91 + logged amendments) | scripted expression | verdict |
|---|---|---|---|
| A1 | Willem Duursma > Zeke Uwland | `E(Duursma) > E(Uwland)` | MATCH |
| A2 | Ward < Curtis AND Ward < Weddle; Curtis leg AMENDED 02/07 (Luke, in writing): Curtis ≥ 0.90×Ward | `(cu >= 0.90*wa) and (we > wa)` | MATCH (amended form, already wired D3) |
| A3 | [DC] Rozee 2026 ≥ 80% of 2025; ANNOTATED 02/07 (Luke): evaluated PRE-LTI-layer | `ev26/ev25 >= 0.80` + pre-LTI annotation | MATCH — annotation **WIRED D4** |
| A4 | Harley Reid remains TOP 40 on the board by value | rank ≤ 40 on non-retired engine-EV board | MATCH |
| A5 | Ginnivan > 1600, Bowey > 2100, Blakey > 2600 (SCAR floors, re-base at PVC) | `v > floor` each, re-base note carried | MATCH |
| A6 | yr1-3 RUC cohort median ≤ pick-matched MID median (pool thin RUC, smooth) | pooled RUC yrs1-3 vs kernel-smoothed MID (bw 0.6 log-pick, RATIFIED 02/07) | MATCH |
| A7 | Maric prices off a MID pole; Langdon off GDEF-dominant future | fut-dominant label + gfut group equality | MATCH |
| A8 | [DC] Berry > Tsatas by at least 2× | WAS `b > 2*t` + ambiguous display; NOW `b >= 2*t` + ratio printout | **MISMATCH → FIXED D4** (display ambiguity + strict `>` vs frozen "at least") |
| A9 | Jack Ginnivan > Josh Ward | `E(Ginnivan) > E(Ward)` | MATCH |
| A10 | [DC] Curnow 2026 ≥ 70% of 2025; AMENDED 02/07 (Luke, in writing, D4): 0.70 → 0.50, data-caused, provisional | WAS `>= 0.70`; NOW `>= 0.50` + provisional/review note | **MISMATCH vs amended spec → WIRED D4** |
| A11 | [DC] Farrow > Patterson; Cumming > Annable | both pairs `>` | MATCH |
| A12 | [DC] Travaglia > Moraes; Smillie > Retschko | both pairs `>` | MATCH |
| A13 | Pick-1 line-ball ±20% Wardlaw + Ashcroft; staged PENDING until PVC | PENDING + advisory lineball vs stand-in PVC[1] | MATCH (staged) |
| A14 | Pick ~8 line-ball ±20% Rivers/Z.Reid/Burgoyne; staged PENDING | PENDING + advisory vs stand-in PVC[8] | MATCH (staged) |
| A15 | STRUCK (Luke 02/07) — convexity → V_NEXT #1 | STRUCK | MATCH |
| B1 | Cohort growth law rise to yr4-6 peak; RE-SCRIPTED (Luke 02/07): pooled peak by yr4-5 (yr6 acceptable), pre-peak dips <5%, no yr6-hold | pooled peak ∈ {4,5,6} > 100, path_ok (≥0.95 steps), per-cohort backstop | MATCH (amended form) |
| B2 | GATE-1 leakage ~0 + good/bust separation; tol 0.5 SET 02/07 | median \|IS−WF\| ≤ 0.5 AND GOOD>BUST per position | MATCH (amended form) |
| B3 | Walk-forward book gates pass at ship head | PENDING (set not yet enumerated; proposal stands) | MATCH (staged) |
| B4 | Python and board JS byte-agree on the shipped board | regenerate export, md5 vs shipped bundle | MATCH — NOTE: shipped bundle proven orphaned (D3); gate re-anchors at the ONE-price board re-cut |
| B5 | No-crater guard (founding rule); YEAR-SCHEDULE SIGNED 02/07 (Luke, in writing, D4) | WAS 0.25× yr1-2 proxy; NOW yrs1-7+ .45/.35/.28/.21/.13/.09/.05 × draftval, ND-entrants only, generating rule + re-base note recorded | **MISMATCH vs signed spec → WIRED D4** |
| B6 | Value continuous across games ramp + monotone in evidence; RE-SCRIPTED (Luke 02/07): whole 0→6 ramp | whole-ramp steps + dips + DECLARED thresholds (pending ratification) | MATCH (amended form) |
| C1 | Beats NAIVE BASELINE on book metrics | PENDING (book not built; proposal stands) | MATCH (staged) |
| C2 | Beats ORIGINAL V1 pick model | PENDING (book not built) | MATCH (staged) |

**AUDIT VERDICT: 23 gate lines audited · 20 MATCH (6 in Luke-amended form) · 3 MISMATCH (A8, A10, B5) — all fixed/wired this session · A3 annotation added.** No other divergence between the frozen text and the instrument found.
