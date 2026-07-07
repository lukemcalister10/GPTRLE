# DPP STRIP — FINAL CONSOLIDATION — RETURN
_Candidate branch `claude/dpp-strip-final-consolidation-cxvk2o`, off PR #34 head `14472db`. **DO NOT merge to canonical.** The owner sees the new board + book before any bake; re-bake from the owner's codespace. Everything below is re-runnable under `run_panel.sh` env; full tables in `evidence/dpp_strip/`._

## STEP 0 — GROUND
- Reached PR #34 branch `claude/f1-f2-one-source-rewire-8xynuh` @ **`14472db`**; branched off its head.
- Single source `engine/rl_after/rl_model_data.json` going in = **`73d23a8e`** (post-rewire, as PR #34 reported). Read PR #34 `evidence/f1f2_rewire/REPORT.md` + `the_34_ifapplied.txt` first.
- After this build the store is **`e1b4d8bf`** (three single-valued position columns; no `raw_multipos`; Kako + off-by-one folded).

## BOARD (805 active, membership key-for-key identical across every state)
| state | board sum | vs prior |
|---|---|---|
| PREVIOUS (held, PR #34 head) | **673,310** | — (matches PR #34 REPORT exactly) |
| CONTROL (blend stripped, no 34) | 664,612 | blend strip **−8,698** |
| S34 (blend stripped + the 34) | 660,728 | the 34 **−3,884** |
| **FINAL** (+ Kako + off-by-one) | **660,325** | Phase 2+3 **−403** |

**Sum-to-total checks exactly:** blend(−8,698) + the-34(−3,884) = −12,582 = PREVIOUS→S34. PREVIOUS→FINAL = **−12,985**.

---

## PHASE 1 — STRIP DPP (deliberate re-pricing)
The `_fut` weighted blend is **deleted**: no `raw_multipos` list, no `futblend` weights, no `gfut` multi-leg — no probabilistic legs anywhere. The store now carries **three clean single-valued columns**: `drafted_position` (cohort curves), `present_position` (year-0 leg), `future_position` (years-1+ leg + peak/curve). In this build **`future_position = present_position`** for every player, so each resolves as a single position now — **but the seam is live**: a later transition model can populate `future_position` where it should differ, with no schema or code change. Each dual is collapsed to its **primary (present/dominant) leg** (Petracca → MID, drops the 0.3 GEN_FWD leg).

### (a) Blend strip — the "forward-eligibility ≈ $0" answer  (`blend_strip_distribution.txt`)
94 active former-duals, PREVIOUS → CONTROL (collapse to dominant leg, drop the minority legs):
- **median drop $1**, mean $97, **max Rowan Marshall $984** (1417→433 — a 50/50 RUC/KFWD swingman losing the KFWD leg + the ruck cap now binding). **13/94 (14%) lose ≤ $5.**
- **Verdict:** forward-eligibility ≈ $0 is **true for the median dual** (half the "duals" carried a near-worthless second leg), but **false for the ~20 genuine swingmen** — Marshall $984, Bailey J. Williams $687, Touk Miller / Jy Simpkin $642, **Petracca $619**, Sam Draper $594 all lost real value. Marshall (not Petracca) is the max — this matches PR #34's `the_34_ifapplied.txt` top line (−986) exactly.

### (b) The 34 — present-position reassignments APPLIED  (`the_34_applied.txt`)
All 34 of the owner's calls applied; present is now authoritative, future set to match. CONTROL→S34 isolates the 34 effect; largest: Justin McInerney −797, Ryley Sanders −971 (isolated), totals up to −986 (Marshall). Petracca 3033 → **2414** and Marshall 1417 → **431** reproduce PR #34's if-applied numbers **exactly**.

### Invariant — "nothing outside {former-dual} ∪ {the 34} may move" (flagged)  (`ripple_analysis.txt`)
- **Only 2 non-dual/non-34 players change POSITION** — `harvey-thomas` (+162) and `luke-lloyd` (inactive): single-leg records whose `present_position` disagrees with their sole future leg (34-like cases the owner didn't list). **Held at their stored `present_position`; their divergent future leg stripped; FLAGGED for owner review** (candidates for a future 35th call, not silently reassigned).
- **582 players move with position UNCHANGED** — a pure **shared-surface ripple**: the V0 board curve (D14 law) is fit per-position on real ND players' zero-evidence start values, so when the 94 duals' start values shifted the pooled curve re-fits and reprices players who share it. SCALE and PVC are ~unchanged (not a global rescale); established anchors barely move (Daicos 7002→7002, Cripps 1326→1326, Gawn −8), young V0-anchored players move more. **Median 0.13%**; this is the National-Draft ripple the directive anticipated ("sanity on the earlier scrub ripple").

---

## PHASE 2 — KAKO FORENSIC + VERIFY  (`kako_forensic.txt`)
**How it was lost:** his 2025 season was **never in the store** — from the seed `f4a4d34` the store had Kako as 2026-only (6@55.0); his real 2025 (23@55.1) lived **only** as a hard-coded patch in the book generator `s4_matrix_M1v7.py` (lines 14-21), injected at book-build time. So the board (no patch) and book (patched) disagreed and the store was silently wrong. **`14472db`** (PR #34) folded it into the store and deleted the book-local patch.
**Verify + correct:** store now reads **2025: 23 g @ 55.2 · 2026: 6 g @ 55.0**. The folded patch had 55.**1**; corrected to **55.2** (owner ground truth). Board impact: 0 (0.1 SC below the rounding threshold). Self-test check (4) asserts it.

## PHASE 3 — OFF-BY-ONE GAMES  (`offbyone_before_after.txt`)
25 players had a season exceeding their career-total field. **24** are the Sellwood pattern (2026 in-progress season = career+1) — fixed by reducing that season to the career total (e.g. Sellwood 14→13). **1** distinct sub-case: `liam-mackie` (career field 0 vs a real 2019 2-game season, inactive) — career raised 0→2 to preserve the real season. **After: career ≥ season for all players (0 violations).**

## PHASE 4 — pvc_snapshot.json  (`pvc_snapshot_disposition.txt`)
**Reader found (live):** `rl_model.py:_v4_init` → the peak-model logPVC feature (`peak_est`). It is the peak model's **train-time PVC**, frozen to break the SCALE↔PVC↔peak_est bootstrap cycle (NOT the live PVC — feeding live would be train/serve skew + a board re-price). **Disposition (live reader → regenerate as derived/stamped/read-only):** generator `build_peak_model_v4.py` now **co-emits** it read-only next to the pickle; `single_source.lock_tier2()` stamps it (`tier=2, frozen`) and sets it `0o444`; the false "== live PVC" comment is corrected. Content unchanged (`735d2dec`) → value-neutral. Not deleted, not regenerated-from-live.

## PHASE 5 — THE FOUR SINGLE-SOURCE GUARDS (permanent; each FAILS the build, never warns)
`engine/rl_after/single_source.py` + generator integration + `guard_correction_canary.py`. `SINGLE_SOURCE_INVARIANT.md` is committed and referenced as the **top block of the kickoff doc** (`docs/KICKOFF_PROMPT.md`).
1. **One writable source; derived read-only + source-md5-stamped** — `rl_export`/`s4_matrix` are the only writers; each stamps `<file>.srcmd5` with the source md5 and chmods the output `0o444`. ✔ board + book are `mode 444`, stamped `e1b4d8bf`.
2. **Source-hash assertion (HALT on mismatch)** — the book asserts the board's stamp == current source md5 before consuming it; the self-test asserts both. ✔
3. **Lookalike tripwire** — self-test FAILS if >1 `rl_model_data*.json` (or any `.pre_stage0`/`.stage0`/`.bak`) exists, or if `rl_model.py` opens outside the classified set. ✔ (it even caught the canary's own backup file — see below.)
4. **Correction-sticks canary** — edits the source, full-rebuilds, asserts the edit survives to board **and** book; restores everything. Proves the Kako class is dead. ✔ (`guard_correction_canary.py`).

## PHASE 6 — SELF-TEST (fresh bootstrap)
`rm -rf` workspace → `bootstrap.sh` → `rl_export` → `s4_matrix` → `one_source_selftest` — **all PASS**:
guards 1-3 · active == **805** key-for-key · F1 export↔engine parity (0 mismatch) · F2 book↔board parity (0 mismatch) · Kako 23@55.2 / 6@55.0 · Bontempelli 13 seasons (2014→2026) regenerate from source · position model (3 single-valued columns, `raw_multipos` gone, future==present). Guard 4 canary run separately — see below.

---

## RETURN — one-liners
- **Largest National-Draft mover (incidental/ripple):** Joe Berry 1424 → 1269 (**−155, −10.9%**, pure V0-curve ripple, GEN_FWD). (Largest ND mover overall is a deliberate reassignment: Tim Kelly −677 via the 34.)
- **Name-collision guard, keyed by ID** (`name_collision_guard.txt`) — all distinct: two Emmetts (`louis-emmett` RUC pk27/25 · `tom-emmett` GFWD pk41/22); two Bailey Williamses (`bailey-williams-wb` pk48/15 · `bailey-williams-wc` "Bailey J." pk35/18); two Max Kings (`max-king-stk` pk4/18 · `max-king-syd` Maxwell pk49/25); Berry (`sam-berry` · `jarrod-berry`); Pickett (`kysaiah-pickett` ND · `marlion-pickett` MSD). Store keys: 2652 records, all unique + non-null; board and both parity gates match on key, never name/id.

## IN PLAIN TERMS
We deleted the old "he could play two positions" pricing and gave every player one position now plus a slot for where he's heading (identical for now, but the wiring's there for later). Collapsing the two-position guys to their main role is what moved the board: for **most** of them that second position was worth basically nothing (median a dollar), but for the genuine swingmen it was real money — Rowan Marshall drops the most ($984) once he's priced as a pure ruck. We then applied your 34 position re-calls, corrected Isaac Kako's missing 2025 season to 23 games @ 55.2 (and traced why it went missing — it only ever lived in a hidden patch, never in the real data file), and fixed 25 players whose game counts were off by one. A modest, mostly-tiny ripple runs through the young forwards because they share a starting-value curve with the swingmen we re-priced — nothing dramatic, and your established stars barely moved. Finally we bolted four permanent alarms onto the build so this can never rot again: there's exactly one real data file, everything else is locked read-only and stamped, and a self-test literally edits the data and checks the change reaches the board and book — proving the Kako problem can't come back. **Nothing is baked. The board + book are ready for your eyes; the re-bake happens from your codespace on your word.**
