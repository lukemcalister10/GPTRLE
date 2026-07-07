# BUILD notepad — 2026-07-01 — current-season drop: uniformity tests (2026-specific vs every-year)

Head 8aed420a unchanged, bake HELD.

HEADLINE: the uniform + 2026-specific drop is REAL but confined to the THIN-GAMES population — players
with <6 games in 2026 drop -18% to -35% UNIFORMLY across every cohort. On-field/on-pace players (g>=6)
follow the natural career arc (younger rise, older decline) — which is why the earlier Phase-1
counterfactual (on-pace only) missed it. Leaguewide scoring is NOT down. Mechanism = recency/reliability
machinery + mid-season decay asymmetry, NOT a games penalty and NOT lower scoring.

TEST 2 (leaguewide scoring): NOT below 2025 — marginally higher (established 79.33->79.83). Falsified. No
scoring-level cause.

TEST 1 (per-transition, g>=6 both): median trend 0/0/-8.6/-12.3% — 2024->25 (complete season) already
negative, so 2025->26 is a continuation not a discontinuity. By cohort, younger cohorts still RISE in
25->26 on-field (2020 +30, 2021 +44, 2023 +20); older decline. Career arc, not uniform.

BOOK RECONCILIATION (the key): cohort-mean ev 25->26, split by 2026 games. OFF-field (g<6) column negative
EVERY cohort (-18 to -35%), dead uniform. On-field follows the arc. Averaging both drags each cohort down
(2023: on-field +21% but all-members -2% via off-field -32%). This is the uniform 2026 signal; survives the
earlier counterfactual (on-pace only, rate frozen).

TEST 3 (mechanism): conditional_prior cont.25 rebuild weights by GAMES x recency (not by season);
_swt=0.72^(Y-yr); reliability-shrunk level; LEVEL_RAMP=14 recency-wtd games to count fully. Mid-season
asymmetry: as-of round 14, 2025 fully one-year-decayed (x0.72) while 2026 only ~60% elapsed + thin -> thin
players sit in an evidence trough -> shrunk level -> depressed value. Uniform + current-season-specific;
unwinds as 2026 completes. By-games weighting means it's the DECAY ASYMMETRY, not full-weight-per-season.

TEST 4 (M1+v7): ed-richards (rising MID) M1v7 3134->2552 (19% drop) vs baseline 4188->2487 (41%) — HALVES
the drop by compressing the inflated 2025 peak. charlie-curnow (flat KFWD) 1596->877 (45%) vs 1849->944
(49%) — unchanged. So M1+v7 softens on-field RISER drops but does NOT touch the uniform thin-2026 drop.
Bake is largely separable — neither causes nor fixes it.

FIX DIRECTION (Phase 2, not designing; read call first): prorate prior-season recency decay by elapsed
fraction f (don't fully decay 2025 when 2026 ~60% done) or gate reliability-shrink by f; inert at f=1
(history + M1+v7 curve untouched); lifts thin-2026 members only. BUT: a player genuinely <6g by round 14
(injured/dropped) arguably SHOULD price lower mid-season -> is the depression an artifact or correct? Luke
decides whether Phase 2 runs.

BAKE: held per directive; M1+v7 separable from the 2026 issue, can proceed on its own read-merits.
