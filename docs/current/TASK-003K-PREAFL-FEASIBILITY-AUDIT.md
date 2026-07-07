# TASK-003K — Pre-AFL information feasibility audit

## Scope

Diagnostic only. No model fitting, cohort or target changes, production forecast, value, keeper utility or UI changes. No external data was scraped or imported. The audit inventories information already committed in the repository and identifies what would require future licensed, reproducible external collection.

GitHub verification note: this checkout had no usable GitHub remote configured. I attempted to add and fetch `https://github.com/lukemcalister10/GPTRLE.git`, but authentication for the private repository was unavailable in the non-interactive environment. The local HEAD already contains TASK-003J and is treated as the provided vNext integration snapshot for this diagnostic branch.

## Inputs inspected

- `AGENTS.md` project rules.
- TASK-003E through TASK-003J current documentation.
- Historical eligibility evidence under `data/historical/`.
- Current 2026 player universe under `data/current/`.
- Repository player database `engine/rl_after/rl_model_data.json` as a read-only source inventory.
- vNext snapshot/cohort code to identify which fields are already used or explicitly neutralised.

## Repository inventory summary

The diagnostic script `scripts/audit_preafl_inventory.py` writes `reports/task-003k-preafl-audit/repository_field_inventory.csv` and `reports/task-003k-preafl-audit/summary.json`.

Key counts from the committed inventory:

- Repository player database: 2,652 players, draft/entry years 2003–2026.
- Entry pick: 2,371/2,652 non-missing; missing is represented by pickless/undrafted style records.
- Entry type code: 2,652/2,652 non-missing, with ND, RD, MSD, UNR, IRE, PDA, SSP, PDN and PSD levels.
- Entry type label: 2,327/2,652 non-missing, including National, Rookie, Mid-Season, Post-Draft and Pre-Season labels.
- Drafted position: 2,652/2,652 non-missing.
- Birth year: 2,350/2,652 non-missing; exact birth date: 846/2,652 non-missing.
- DraftGuru identity map: 1,465 observed people, 1,440 matched repository identities, draft years 2000–2023.
- Historical annual list eligibility: 18,564 player-origin rows, 5,622 positive list-presence rows, origins 2018–2024.
- Current 2026 player list: 804 rows with current AFFL team and position eligibility.

## Candidate source/feature assessment

| Candidate source or feature | Repository source | Already exists? | Years covered | Player coverage and missingness | Identity-match quality | Known by historical origin? | Leakage risk | Available for current 2026 players? | Estimated effort | Classification |
|---|---|---:|---|---|---|---|---|---|---|---|
| Entry/draft year | `engine/rl_after/rl_model_data.json` field `year`; DraftGuru map `draft_year` | Yes | repo 2003–2026; DraftGuru 2000–2023 | 2,652/2,652 repo non-missing | Repo key native; DraftGuru map 1,440/1,465 matched | Yes if entry year is first list/entry known at origin; TASK-003 cohorts already correct later-entry conflicts to verified first list year with `UNK` facts | Low after existing historical correction; raw current-era source can encode later backfill if not corrected | Yes in repo for 2026 universe after identity join, not in supplied `Players_2026.csv` alone | Low | Safe for historical model training if sourced through existing cohort entry-correction path |
| Draft pick / pick bucket / pickless flag | `pick`, `_pickless`; DraftGuru map `draft_pick` | Yes | repo 2003–2026; DraftGuru 2000–2023 | `pick` 2,371/2,652 non-missing; `_pickless` complete | Repo key native; DraftGuru matched identities good but not complete for all repo players | Usually known at entry; existing code sets pick 80 when verified list presence predates repository entry | Low to medium: must not use a pick discovered only after an earlier list origin; use corrected `pick=80/type=UNK` for affected historical rows | Yes in repo for many 2026 players; current CSV alone lacks it | Low | Safe for historical model training with correction; high-ranked next experiment input |
| Draft type/pathway | `type`, `_draft`; DraftGuru map source URL/player page | Yes | repo 2003–2026; DraftGuru 2000–2023 | `type` 2,652/2,652; `_draft` 2,327/2,652 | Repo key native; DraftGuru matched good but not complete | Known by entry/listing origin when not backfilled | Low to medium: newer categories (MSD, SSP, PDN) may be unseen in earlier folds; use unknown handling | Yes in repo for many current players; current CSV lacks it | Low | Safe for historical model training; high-ranked next experiment input |
| Age at entry / age at origin | `_by`, `_bd`, `year` | Partly | repo 2003–2026 | `_by` 2,350/2,652; `_bd` 846/2,652; age currently falls back to `18 + tenure` | Repo key native | Birth year/date is public/static and known before origin when present | Low; exact DOB missingness is not leakage, but filling missing DOB from future-only source would need provenance | Yes in repo for most current players; current CSV lacks it | Low for birth-year features, medium for better DOB provenance | Safe for historical model training using committed `_by` plus missing indicator |
| List tenure without AFL games | Derived from verified eligibility matrix and AFL scoring rows | Yes, derivable | historical origins 2018–2024; repo scoring 2005–2026 | Positive list eligibility 5,622 rows; derived first AFL game year missing for 743 never-played records | Eligibility identities reviewed; repository scoring key native | Yes at each origin if computed only from seasons `<= origin_year` and verified list presence | Low if computed as of origin; high if using future first-game year directly | Current list tenure needs current list membership plus entry year; current CSV gives membership, repo gives entry year | Medium | Safe for historical model training; highest-ranked next experiment input |
| Historical annual list status / club-listed flag | `data/historical/historical_eligibility_2018_2024.csv.gz.b64`; `DraftGuruEligibilityResolver` | Yes | 2018–2024 origins | 18,564 rows, 5,622 eligible positives | Strong: 1,440 matched, 25 reviewed exclusions; duplicate-name cases manually checked | Yes: annual list pages represent list status for that season | Low for eligibility/cohort; using club identity as a model feature could add policy/list-management signal and must be justified | Current 2026 list is available from `Players_2026.csv`; historical 2025 is not in this matrix | Medium | Safe for training for list tenure/status indicators, not as current-club strength proxy without separate audit |
| Position at entry | `drafted_position`; snapshot currently canonicalises this | Yes | repo 2003–2026 | 2,652/2,652 non-missing | Repo key native | Usually known by entry; conservative compared with current/future position fields | Low | Yes in repo for many current players; current CSV has current AFFL positional eligibility separately | Already used | Safe; already in model |
| Current/present/future position | `present_position`, `future_position`; `data/current/Players_2026.csv` `Position/s` | Yes | repo current/backfilled; current list 2026 | 2,652/2,652 repo; 804/804 current | Repo key native; current list needs name matching to repo key | Not necessarily known at historical origins; these may reflect current/future positional classification | High for historical training unless reconstructed by origin | Yes | Low technically, but not valid historically | Current-only information that cannot be benchmarked fairly |
| National, rookie, preseason, mid-season, supplementary pathways | `type`, `_draft`; examples include ND, RD, PSD, MSD, SSP, PDN, PDA, UNR, IRE | Yes | repo 2003–2026 | Complete code; label 12.25% missing | Repo key native | Yes if entry pathway is the actual origin pathway; verified-first-list corrections neutralise conflicts | Low/medium due unseen categories in early folds; TASK-003J observed categorical gaps for newer pathways | Yes in repo for many 2026 players | Low | Safe with robust rare/unknown category design |
| Category: father-son, academy, next generation | `_cat` | Sparse | repo 2003–2026 | 173/2,652 non-missing; 93.5% missing | Repo key native but provenance unclear | Likely known at draft time when present | Medium: missingness/provenance unclear; category may be selectively collected for recent/high-profile players | Yes for some current players | Low technically, high evidence burden | Too sparse/unreliable until provenance is documented |
| Junior/state-league/VFL/SANFL/WAFL/NAB League scoring | None found in committed data | No | Not covered | No committed rows/fields | Not applicable | Would be known if collected from dated public/stat providers before origin | Medium/high: source coverage, licence, retrospective availability and identity matching must be documented | Potentially available externally for some 2026 players | High | Requires external collection |
| Combine/draft-camp testing | None found in committed data | No | Not covered | No committed rows/fields | Not applicable | Would be known if collected before origin | Medium/high: publication bias, missingness and licensing likely material | Potentially available externally for some 2026 players | High | Requires external collection; likely sparse |
| Current AFFL team / owner data | `data/current/Players_2026.csv` `AFFL Team` | Yes, current only | 2026 only | 804/804 | Supplied current list, no historical benchmark matrix | No for historical origins | Very high if used in forecast training; owner/league information is not a player outcome cause | Yes | Low | Current-only / do not use for forecast model |
| Current active/retired flags | `_has26`, `_retired`, `_force_active`, `_last_listed` | Yes | Current/backfilled status | `_has26` and `_retired` complete; sparse overrides | Repo key native | No for historical origins unless reconstructed from origin-specific lists | High: directly encodes future/current survival for old origins | Yes | Low | Current-only; not safe for historical model training |
| Current/source club | `_club`; historical eligibility `club` | Yes | repo current/backfilled; historical 2018–2024 list club | `_club` 2,317/2,652; historical club present for positive eligibility | Historical list identity reviewed | Historical club is known at origin, but using it could import club environment/list strategy; `_club` likely current/source not origin-specific | Medium for historical club; high for `_club` backfilled current club | Current club in supplied current CSV/AFFL team is not AFL club in all cases | Medium | Safe only as annual list status/tenure; club feature should be deferred |
| Repository scoring rows before first AFL game | `scoring` | Yes but AFL-only | repo 2005–2026 | 743 players have zero scoring seasons; pre-debut rows generally absent | Repo key native | AFL scoring observed by origin is safe; there is no junior/state scoring here | Low for existing AFL history; none for zero-history prospects | Yes for already played current players, not zero-history | Already used | Safe but does not solve zero-history separation |

## Safe historical-training feature set

These can be benchmarked fairly without importing new data if implemented through the locked cohort build and origin-date rules:

1. **Zero-AFL list tenure as of origin**: number of verified annual list seasons with zero AFL games, plus indicators for first-listed year and no-AFL-games-on-list.
2. **Entry pathway and pick interactions**: draft type/pathway, pick bucket, pickless/undrafted flag, rare/new pathway bucket, and interactions restricted to general pathway classes.
3. **Age-at-entry and age-at-origin refinements**: use committed birth year where present, missing indicator where absent, and avoid future DOB backfill unless provenance is added.
4. **Historical list status indicators**: verified listed at origin and possibly years-listed counts; do not use current active/retired status.
5. **Entry position**: already safe and already used; may interact with pathway/tenure in a future model experiment if that is the single hypothesis.

## Current-only information that cannot be benchmarked fairly

- `Players_2026.csv` `AFFL Team` and current `Position/s` for historical training.
- `present_position`, `future_position`, `_has26`, `_retired`, `_force_active`, `_last_listed`, `_pvc_exclude` unless reconstructed historically.
- Current/source `_club` as a static field for historical origins.

## Information requiring external collection

- Junior, state-league, VFL, SANFL, WAFL, NAB League or equivalent scoring.
- Combine/draft-camp testing.
- Detailed pre-draft bio data beyond committed birth year/category fields.

Any future PR collecting these must document source, licence, reproducibility, historical availability at each origin, identity matching, missingness and whether current 2026 coverage is comparable to historical coverage.

## Too sparse or unreliable for immediate use

- `_cat` father-son/academy/Next Gen category: only 173/2,652 non-missing and provenance is not documented in current task evidence.
- Exact birth date `_bd`: useful if provenance is established, but currently 68.1% missing; birth year `_by` is more immediately usable.
- Static present/future position and active/retired flags: not sparse, but unreliable for historical modelling because they encode current/backfilled state.

## Ranked recommendation for the next zero-history model experiment

1. **Test an origin-safe zero-AFL list-tenure/pathway representation for zero-history players.** Mechanism: TASK-003J found many zero-history players collapse into similar low-information vectors. A feature block that separates newly drafted players from players retained on AFL lists for one or more seasons without AFL games, crossed only with broad entry pathway and pick bucket, directly targets state separation without broad magnitude inflation. This is safe because annual list presence is already reviewed for 2018–2024 and AFL games are observable by origin.
2. **Add robust rare/new pathway handling for draft type.** Mechanism: TASK-003J observed categorical gaps concentrated in MSD, PDN, SSP and unknown pathways. Grouping or encoding pathways by broad legal entry route may reduce unseen-category brittleness while preserving historical fairness.
3. **Refine age-at-entry with committed birth-year missingness indicators.** Mechanism: separates mature-age entrants from 18-year-old draftees where birth year is available, without requiring external data.
4. **Defer junior/state-league and combine data.** They may be highly relevant, but they are absent from the repository and would require a separate data-governance PR before modelling.
5. **Do not use current-only active, owner/team, present/future position or current club fields in training.** They cannot be fairly benchmarked against locked historical origins.

The recommended next experiment should be a single model hypothesis: add leakage-safe zero-history state-separation features derived from historical list tenure, entry pathway and pick bucket, then evaluate under the unchanged locked validation protocol. This audit does not implement or fit that model.

## Reproduction

```bash
python scripts/audit_preafl_inventory.py
```
