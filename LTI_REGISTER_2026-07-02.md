# LTI & AVAILABILITY REGISTER — Luke's ground-truth data — captured 2026-07-02 (turn 43)
### Source: Luke, verbatim intent. This file is the curated register the engine should consume — human-maintained ground truth beats inference for injury detection. Committed via D5. Luke updates it as injuries occur.
### TIMING DESIGNATIONS (Luke's definitions):
### · "2025" = injured in his last game of the 2025 season; hasn't played since; MAY return during 2026.
### · "2026 pre-season" = injured before the 2026 season started; will not play until 2027.
### · "2026" = injured in his most recently recorded 2026 game; will not play until 2027.
### NAME GUARD: "Maxwell King" is the disambiguated name per the standing collision rule (two real players named Max King; never merge on name — key by ID/pick/cohort).

## SECTION A — LONG-TERM INJURED (deserve the LTI return-season haircut; those out for 2026 also have nil 2026 production)
| player | injury timing | notes |
|---|---|---|
| Jack Payne | 2025 | may return 2026 |
| Matt Carroll | 2026 | out until 2027 |
| Jesse Motlop | 2026 pre-season | out until 2027 |
| Harry O'Farrell | 2025 | may return 2026 |
| Jamie Elliott | 2026 | out until 2027 |
| Reef McInnes | 2025 AND again 2026 | repeat LTI — two windows |
| Oscar Steene | 2026 | out until 2027 |
| Brayden Fiorini | 2026 | out until 2027 |
| Lewis Hayes | 2025 AND again 2026 | repeat LTI — two windows |
| Nic Martin | 2025 | Luke's exemplar obvious case (established → zero games) |
| Toby Conway | 2025 | may return 2026 |
| Tom Green | 2026 | Luke's exemplar obvious case |
| Josh Kelly | 2026 pre-season | out until 2027 |
| Darcy Jones | 2025 | may return 2026 |
| Nathan Wardius | 2026 pre-season | out until 2027 |
| Jai Culley | 2026 | out until 2027 |
| Jack Viney | 2026 pre-season | out until 2027 |
| Andy Moniz-Wakefield | 2026 | out until 2027 |
| Jackson Archer | 2026 pre-season | out until 2027 |
| Blake Thredgold | 2026 pre-season | out until 2027 |
| Ollie Lord | 2026 | out until 2027 |
| Esava Ratugolea | 2026 | out until 2027 |
| Josh Sinn | 2026 pre-season | out until 2027 |
| Josh Gibcus | 2026 | out until 2027 |
| Judson Clarke | 2025 | may return 2026 |
| Sam Flanders | 2026 | out until 2027 |
| Liam Hetherton | 2026 pre-season | out until 2027 |
| Maxwell King | 2026 pre-season | out until 2027 · name-collision guard applies |
| Noah Long | 2026 pre-season | out until 2027 |
| Jacob Newton | 2026 | out until 2027 |
| Deven Robertson | 2026 | out until 2027 |
| Sam Darcy | 2026 | out until 2027 |

## SECTION B — NOT LTI, but out for the remainder of 2026 (no haircut; nil 2026-relevant production)
Archie May · Harley Barker · Brody Mihocek · Toby Pink · Mani Liddy · Ewan Mackinlay · **Connor Rozee** · Jonty Faull · Joel Amartey · Noah Chamberlain · Harry Edwards

---
## Guards carried over from the D4 skeleton (compatible — retained; the verbatim register above is the content of record)
- **EXACT-name discipline** — the store's rename guard applies: the player commonly called "Max King" is
  **"Maxwell King"** in the store (Max King → Maxwell King rename guard, START_HERE §5); two Uwlands; 8 known
  name collisions — any consumer keys rows by store key (`p['key']`) / ID / pick / cohort, never by display name alone.
- Entries are Luke's ground truth: the engine may HAIRCUT for absence (cf. the existing `_b2hc` present-
  unavailability machinery) but never re-diagnoses an entry.
- A3 is evaluated PRE-LTI-layer (Luke, 02/07/2026, logged): any LTI overlay built from this register must not
  be the thing that passes A3.
