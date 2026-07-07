# REWIRE TO ONE SOURCE — F1/F2 fix · phantom scrub · position collapse — RETURN

**Candidate branch. DO NOT merge to canonical.** Luke sees the board + book before any bake; the re-bake happens
later from his codespace. Everything below is re-runnable under `run_panel.sh` env.

## GROUND TRUTH (STEP 0)
- Canonical HEAD `389ac397` (tag `baked-v2.4-2026-07-04`), reachable. Read: PR #30 (F1/F2), #31 (dataflow), #33 (lookalike diff).
- Source-of-truth store `engine/rl_after/rl_model_data.json` **md5 `644d1254`** going in == `.pre_stage0` (byte-identical) ✓.
- After the rewire the store is **md5 `73d23a8e`** (single source; the two lookalikes are deleted).

---

## PHASE 1 — 5-SUPPORT-FILE CLASSIFICATION (+ hidden-copy FLAG)

| file | md5[:8] | class | origin / generator | hand-editable |
|---|---|---|---|---|
| `params.json` | `07655a5f` | **AUTHORED INPUT** | model constants (PEAK, PEAK_AGE, AGE_CURVE); no generator writes it | yes |
| `rl_passmark.json` | `4332c655` | **AUTHORED INPUT** | passmark calibration (pm_pos, pm_band, bands, BUST_BAND); no generator | yes |
| `peak_model_v4.pkl` | `b763f59e` | **DERIVED CACHE** | generator = `engine/forward_valuation/build_peak_model_v4.py` (GBR pickle); inputs = engine + `dob_corrected.json` + `bust_prior_table.json` | no (binary model) |
| `bust_prior_table.json` | `ffb54267` | **AUTHORED INPUT** | bust-prior table by pos×pick; no in-repo generator; also feeds the peak-model build | yes |
| `pvc_snapshot.json` | `735d2dec` | **DERIVED SNAPSHOT — hand-checked-in — ⚠ DRIFTED** | snapshot of the *train-time* PVC used to break the SCALE↔PVC bootstrap cycle at inference (`rl_model.py:362`) | edited by hand |

**⚠ FLAG — `pvc_snapshot.json` is the next hidden-copy risk (exactly as the directive predicted).** Its comment
claims it is "deterministic so == live PVC at standard env." It is **not**: **94 of 99 picks differ** from the live
engine PVC (e.g. pick 2 snap `2496` vs live `2501`; pick 30 snap `618` vs live `603`). The v2.4 bake dials (KEY_FWD
REPL 67.8→66.8) moved the live PVC without anyone regenerating the snapshot, so it has silently gone stale. It is a
hand-checked-in "snapshot" that *ought to be derived* — either regenerate it from the engine at bake time or pin it
as an explicit train-time artifact and rename it so it stops masquerading as the live PVC. (Left untouched here — it
is the peak-model's *train-time* input and changing it re-trains the model; out of scope for this rewire, flagged for
Luke.)

---

## RE-PRICING, SEPARATED BY CAUSE (three-column; every number labelled)

Columns: **PREVIOUS** = shipped board (F1-broken, `eb5d6716`) · **CONTROL** = F1-fixed but pre-scrub engine (the
board's *true* gated value) · **CURRENT** = F1 + phantom-scrub + Kako fix + position-collapse.

### (a) F1 FIX — how many move, by how much, which direction
The shipped board priced players through a **second `rl_model` instance**, so the `id(p)`-based `_REAL` gate matched
**0/805** and the ruck cap / v7 age-taper / B5 floor were silently dropped. Fixing it (match by stable **key**, build
from **one** instance) makes those layers fire on the board.

- **531 / 805 players move** (shipped vs gated engine); **501 corrected DOWN** (were over-priced), **30 UP**.
- Median board change **−10.8 %**; worst on young rucks (the stripped ruck cap).
- **Louis Emmett (RUC pk27/2025): 1361 → 853** (F1 alone) → **855** (CURRENT). The single most decisive number.
- Board **sum 706,324 → 672,078 = −34,246 SCAR (−4.85 %)** of pure over-pricing removed.

### (b) PHANTOM SCRUB — which MSD/Ireland players move, by how much
Deleting the 4 phantom rows + the MSD/IRE credit machinery + the MSD 1.5×/2.0× game boosts. Effect on the engine:

- **PICKEQ: MSD 59 → 60, IRE 94 → 94** (barely moves — the pick-equiv is discretized).
- **MSD: 54 move, median 3.7 %** (max 73.5 %: `jai-culley` 437→116, a real MSD who loses the 1.5× debut-game boost).
  `massimo-d-ambrosio` +18 % (1560→1844), `hugo-hall-kahan` −22 %. Real McAndrew 984→**1002**, real Keane 1539→**1560**.
- **IRE: 13 move, median 3.0 %** (max 8.3 %).
- **⚠ NOT confined to MSD/IRE** — a broad, small **ND ripple (477 move, median 0.83 %)** appears because the phantoms
  were *live members of shared surfaces*: the two credit phantoms double-counted real seasons in the era-normalisation
  baseline (REF shifts **+0.039 %**), and the pick-35 bust phantom sat in the ND PVC cohort (PVC picks ~30-40 rise
  **+0.5–0.7 %** once the bust is gone). This is the phantoms' hidden coupling being *corrected*, not a re-model —
  but "nothing else should move" is not literally achievable, and it is quantified here for your ruling.

### (extra) Kako single-source data reconciliation (labelled separately, NOT F1/scrub)
The book carried a Luke-confirmed missing-data patch for **Isaac Kako** (his 2025 season, 23 g @ 55.1) that the store
lacked — a single-source violation. Folded into the store: **board Kako 1187 → 1708** (+521). Book & board now agree.

### SUM-TO-TOTAL (805 common active)
`PREVIOUS 706,324 → CONTROL 672,078 → CURRENT 673,310.`
`F1 (−34,246) + [scrub + Kako + collapse] (+1,232) = −33,014 = PREVIOUS→CURRENT.` **Checks exactly.**

### Named three-column panel
| key | PREVIOUS | CONTROL (F1) | CURRENT | note |
|---|---|---|---|---|
| louis-emmett | 1361 | 853 | **855** | ruck cap now fires (F1) |
| josh-ward | 1772 | 1640 | **1634** | F2 book == 1634 too (was 1233) |
| christian-petracca | 3033 | 3033 | **3033** | **unchanged — DPP retained** |
| nick-daicos | 7063 | 7013 | 7002 | v7 taper fires (F1) + era ripple |
| marcus-bontempelli | 3110 | 3085 | 3080 | " |
| max-gawn | 2120 | 2120 | 2120 | no gated layer binds |
| harley-reid | 3561 | 3537 | 3553 | |
| isaac-kako | 1187 | 1187 | **1708** | single-source data fix |
| lachlan-mcandrew (real) | 1064 | 984 | 1002 | scrub |
| mark-keane (real) | 1627 | 1539 | 1560 | scrub |

## Petracca PREVIOUS vs CURRENT — **3033 → 3033 (UNCHANGED)**
`ev()` prices on `gfut` (settled future = `raw_multipos`), which is **retained**. Petracca stays dual-priced
(`raw_multipos = [[MID,0.7],[GFWD,0.3]]`, gfut = MID). DPP behaves exactly as now.

---

## THE 34 LIST (present-position reassignments — Luke's stage0 calls) — **HELD, not applied**
Diff of `.stage0._pos_now` vs `.pre_stage0._pos_now` = **exactly 34** players (the established de-DPP calls; the other
10 stage0 changes were players with no prior present-position). Full table: `evidence/f1f2_rewire/the_34_list.txt`.

**DECISION-NEEDED (yours).** The directive says "apply the 34," but the RETURN also says "Petracca unchanged /
nothing else should move." These conflict: **`present_position` is NOT display-only** — it feeds the DPP present-leg
via `distribution_pricing.v_at_peak`'s `g0=bnow`. Applying the 34 (with `raw_multipos` retained) re-prices them, all
**downward**, up to −70 %: **rowan-marshall 1417→431, tim-kelly 1598→943, petracca 3033→2414, touk-miller 1908→1325,
adam-treloar 1194→616**. Full if-applied table: `evidence/f1f2_rewire/the_34_ifapplied.txt`.

So Phase 3 was done **value-neutral**: the store now carries clean `drafted_position` / `present_position` /
`raw_multipos` columns (the ~8 old fields collapsed; `_fut` **retained**, unlike stage0 which wiped it), and
`present_position` = the *current-engine* present, reproducing every value byte-for-byte. **The 34 are captured for
your confirmation; say the word and I apply them** (they systematically lower the young-MID board — your call, not a
silent bake).

---

## NAME-COLLISION GUARD — keyed by ID, all distinct
| pair | keys (distinct) |
|---|---|
| two Emmetts | `louis-emmett` (RUC pk27/25) · `tom-emmett` (GFWD pk41/22) |
| two Bailey Williamses | `bailey-williams-wb` (MID pk48/15) · `bailey-williams-wc` ("Bailey J.", RUC pk35/18) |
| two Max Kings | `max-king-stk` (Max, KFWD pk4/18) · `max-king-syd` (Maxwell, GFWD pk49/25) |
| Berry | `sam-berry` (MID pk29/20) · `jarrod-berry` (MID pk17/16) |
| Pickett | `kysaiah-pickett` (GFWD pk12/19 ND) · `marlion-pickett` (GFWD pk11/19 **MSD**) |

Store keys verified **non-null and unique** across all 2,652 records; the F1 fix and both parity gates match on these
keys, never on object id.

---

## SELF-TEST (must pass or the build FAILS) — `engine/rl_after/one_source_selftest.py`
```
(0) .pre_stage0 / .stage0 lookalikes ABSENT ................................. PASS
    rl_model.py opens ONLY the store + the 5 classified inputs ............. PASS
(1) engine active == 805, keys unique ...................................... PASS
(2) EXPORT PARITY (F1): board v == independently recomputed gated ev(), 0 mismatch  PASS
(3) BOOK PARITY (F2): book cur == board v, 0 mismatch (2 pvc-excluded noted)  PASS
(4) Bontempelli 13-season track regenerated from source == source .......... PASS
SELF-TEST PASSED.
```
Plus two **permanent** in-build gates that FAIL the build on any regression:
`rl_export.py` → "PARITY GATE PASS: all 805 board values == engine gated ev()"; `s4_matrix_M1v7.py` →
"BOOK PARITY GATE PASS: all 803 shared board players' present value == book cur".

Bontempelli, straight from `rl_model_data.json`: 13 seasons **2014→2026**, first `(2014, 78.6, 16)`, last `(2026, 119.0, 14)`.

---

## IN PLAIN TERMS (league-manager language)
Two separate leaks were making our numbers wrong in opposite directions, and the engine itself was fine both times —
the bugs were entirely in the two scripts that *publish* the board and the book. (1) The **player-value board** was
built through a second, private copy of the model, so it quietly ignored three safeguards we baked in last week —
most visibly the ruck cap — and **over-priced about two-thirds of the list, worst on young rucks** (Emmett showed 1361
when the engine says 855). (2) The **walk-forward book** was built by an old recipe that double-counted a fade we only
meant to apply once, so it **under-priced the same players the other way** (Josh Ward 1233 when the truth is 1634).
Both are now plumbed to the one engine, and each publisher has a permanent tripwire that halts the build if the board
or book ever drifts from the engine again. Separately, I removed four "phantom" bookkeeping rows (they were quietly
nudging the mid-season and Irish-recruit prices and, it turns out, leaking into the league-average baseline), folded
Isaac Kako's missing 2025 season into the one store so the board and book agree on him, and cleaned up the messy
position columns to three clear ones (present / drafted / dual-position) without moving a single price. The only thing
waiting on your word: your 34 position re-calls (mostly "value this kid as a midfielder now"). They're captured and
ready — but applying them **lowers** those players a lot, so I've held them for you to green-light, not baked them in.
