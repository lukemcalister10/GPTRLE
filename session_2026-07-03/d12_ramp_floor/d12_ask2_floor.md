# D12 ASK 2 — B5 FLOOR RE-ANCHOR draftval → V0 (Luke ruling R8) — CANDIDATE v2.2

**STATE: CONTROL = canonical `8aed420a` (no B5 floor feature — E2-era flat anchor) · PREVIOUS = v2.1 `c8051893` (floor = schedule × draftval) · CURRENT = v2.2 `af1fc6aa` (floor = schedule × V0, concave ramp).**

## Ruling executed (verbatim)
Luke 2026-07-03: _"DV floor should be now aligned with v0. Yes, some issues with rucks, but we can refine them before baking or wiring."_

## The change (one line, schedule unchanged)
```
-  fl = floor_frac(yis) * draftval(p)     # D7 old-PVC basis
+  fl = floor_frac(yis) * v0_start(p)     # D12 live V0 basis (schedule UNCHANGED)
```
`FLOOR_YRS = .45/.35/.28/.21/.13/.09` (yrs 1–6) + flat `.05` tail — **byte-unchanged**. National-draft-entrant scoping unchanged (MSD/SSP/delisted/retired/pickless never floored; pure lower bound). Diff vs ASK 1 = this one line + comment.

## FLOOR-SAVES — three-column, split by position class
(save = floor binds, i.e. prefloor < schedule × basis; lift = floor − prefloor)

| class | CONTROL `8aed420a` | v2.1 `c8051893` (dv) | v2.2 `af1fc6aa` (V0) |
|---|---|---|---|
| nonKPP | n/a | 47 saves, +1779 | **42 saves, +1207** |
| KPP | n/a | 10 saves, +329 | **9 saves, +102** |
| RUC ⚠PROVISIONAL | n/a | 1 save, +9 | **1 save, +21** ⚠ |
| **TOTAL** | **no B5 floor** | **58 saves, +2117** | **52 saves, +1330** |

CONTROL (canonical) predates the B5 pricing floor (added at v2 4a134d05) — it carries the retired flat `SITOUT_RETAIN×draftval` anchor (obituary E2), so "floor-saves" is n/a there. **⚠ RUC floors are PROVISIONAL**: the ruck V0 is Luke-ruled hot (`h-ruc-startvalue-hot`, ~2.5× PVC); its nerf lands NEXT directive before any bake — every RUC floor-save carries ⚠.

## Attribution (isolation): the re-anchor drives the save-set change, the ramp shifts the values
- Concave ramp alone (v2.2 engine, **still dv basis**): 58 saves, +2004 — **0 players leave** the set (prefloors rose but stayed under the higher dv floors; lift shrinks +2117→+2004).
- Re-anchor dv→V0 (holding the concave prefloors): 58 → **52 saves** (13 leave, 7 join, net −6), +2004 → +1330.

The V0 floor is lower than the dv floor for players the old PVC over-priced (freeing them), and higher for players the old PVC under-priced (newly catching a few).

## Save-set delta — players who LEFT (dv-floored → V0 floor non-binding), material moves

| player | class | v2.1 floored (lift) | v2.2 EV | v2.2 V0 floor (non-binding) |
|---|---|---|---|---|
| Dylan Patterson | nonKPP | 884 (+124) | **849** | 511 |
| Billy Cootee | nonKPP | 225 (+195) | 30 | 14 |
| Jamarra Ugle-Hagan | KPP | 270 (+113) | 157 | 91 |
| Aidan Johnson | KPP | 108 (+78) | 31 | 25 |
| Angus Anderson | nonKPP | 139 (+48) | 91 | 43 |
| Cody Angove | nonKPP | 216 (+42) | 176 | 147 |
| Sam Davidson | nonKPP | 133 (+41) | 92 | 18 |
| Hunter Clark | nonKPP | 90 (+40) | 50 | 42 |
| Tai Hayes | nonKPP | 211 (+35) | 197 | 118 |
| Luke McDonald | nonKPP | 85 (+30) | 55 | 43 |
| (+3 small: Broad, Ryan, J.Clarke) | | | | |

**Players who JOINED (V0 > dv → newly floored):** Phoenix Gothard nonKPP +44, Answerth +8, Schoenberg +5, K.Smith/Scott/Kolodjashnij/B.Macdonald +1 each. Material lift moves (both sides): Coffield +69→+27, Wiltshire +73→+41, Melksham +63→+33.

## EXPECTED CONSEQUENCE — PATTERSON (printed loud, Luke-facing)
> **Dylan Patterson's floor drops 884 → 511 (0.45 × V0 1136) and no longer binds.** His v2.2 value becomes his prorated-decayed number under the NEW concave ramp: 1136 × (1 − 0.571×0.442) = **849** (directive predicted ~847; the 2-point gap is the engine's fE=0.58 vs the directive's 14/24=0.5833). He is no longer branded a full-year no-show floored to half the old draft chart; he is priced at what a quiet, not-yet-playing pick-5 defender is worth on the live ruler.

## Anchor check set
| anchor | note | v2.1 | v2.2 |
|---|---|---|---|
| Patterson | dv-floored → V0 floor freed | 884 (floor) | **849** (prefloor) |
| X.Taylor | floor non-binding both sides (prefloor > floor) | 662 | **693** (concave ramp only) |
| Lord (floor line) | floor NEVER binds (414 ≫ floor 108/147) | 414 | **414** (unmoved) |
| 58-save-set aggregate | | 58 saves, +2117 | **52 saves, +1330** |
