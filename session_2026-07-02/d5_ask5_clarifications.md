# D5 ASK 5 — D4 clarification prints
_Candidate numbers from this session's re-measurement (engine `fb39d88a` / cp `5ac8b162` / store `644d1254`, sequential loads; scratch JSON `meas_candidate.json`)._

**(i) Tsatas NET candidate ev():** **979** (raw ev at the candidate = the net of the +9.0 M1 level-lift and the v7 compression; head value was 1083). The supervisor's implied ~982 was arithmetic off the rounded 2.24×; the exact printed number is 979. Context: Luke's logged read "1083 OK, preferred lower" — the candidate lands 104 LOWER. The "+9.0 M1-lift" was LEVEL-space (Lo 66.7 → Lc 75.7); its net value-space sibling is **−104** (1083 → 979): v7's compression more than eats the M1 level credit.

**(ii) A8 at candidate:** Berry net = **2197** · Tsatas net = **979** · ratio = **2.24×** (2197/979 = 2.244, ≥ 2.00 → A8 holds at the candidate).

**(iii) The 6 gate lines audited (23) but not scored (17), and why each is inactive:**
| line | status | why inactive |
|---|---|---|
| A13 (pick-1 line-ball) | PENDING | PVC-coupled by the frozen suite — staged until the pick-value curve exists; advisory line-ball vs the stand-in PVC printed every run (currently True/True) |
| A14 (pick-~8 line-ball) | PENDING | same PVC coupling; advisory currently True/True/False (Burgoyne — goes True at the candidate) |
| A15 (Robey package anchor) | STRUCK | struck by Luke 02/07/2026 ("not all firsts are equal"); convexity dimension seeded as V_NEXT #1 — audited that it STAYS struck |
| B3 (walk-forward book gates) | PENDING | the book-gate set was never enumerated as scripted checks — definition proposal stands in the gates report; book headline shape is covered by B1 meanwhile |
| C1 (naive-baseline book) | PENDING | the baseline book does not exist yet — building it needs its own directive; definition proposal in the gates report |
| C2 (V1 pick-model book) | PENDING | same — the V1 comparison book is unbuilt; proposal in the gates report |

**(iv) Obituary completeness:** **layer count = 9, not the expected 8** — the table carries the 8 deleted layers (router included) PLUS row 9, the JS legacy pricing chain, which is DEAD (fires only in a never-run fallback, `_engine_block_v23.js:97`) but NOT yet excised — its excision is bake-gated to the ONE-board re-cut. Name + magnitude column verbatim:
| # | layer | measured magnitude (D3 1b) |
|---|---|---|
| 1 | the WIRE overwrite | 800/805 players, 31.6% of board value |
| 2 | REPL −3 (board application) | 802/805 players, 19.6% |
| 3 | tail restoration | 29 players, 1.4% |
| 4 | RUC draft pool | 19 players, 1.1% |
| 5 | RUCK TAX 0.25 | 16 players, 0.3% |
| 6 | pedigree soft floor | 35 players, 0.1% |
| 7 | Brodie ×0.5 | exactly 1 player (508 vs 1015 off), 0.1% |
| 8 | lens tilt | 0 players moved (inert at 'bal') |
| 9 | JS legacy pricing chain | 0% (DEAD fallback; not yet excised — bake-gated) |
