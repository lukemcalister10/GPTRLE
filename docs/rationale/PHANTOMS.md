# 🎭 PHANTOM & DOUBLE-COUNT INVENTORY — CANONICAL
**Read this BEFORE: re-ranking any draft, recomputing pathway pools / PICKEQ, auditing distinct players, or "cleaning" odd-looking records. These are DELIBERATE inserts, not data errors.**
Last updated: 2026-06-20 (session 2j cont.6). Working rows: **2690**.

**⚙️ v3.3.1 NOTE — MSD year-1 doubling EXCLUDES phantoms.** The `MSD_Y1_MULT=1.5` load-time transform in `rl_model.py` (scales each MSD player's draft-year games ×1.5, floored) explicitly skips `_phantom` records, so the credit phantom `lachlan-mcandrew-msd-credit` keeps its calibrated 13-game season and the bust phantom `phantom-2022msd11` (empty scoring) is untouched. Do NOT remove that `_phantom` guard — without it the double-count credit gets distorted.

---

## 0. Background — the model's AUTO-RECALL CONSOLIDATION (the thing that makes all this necessary)
`rl_model.py` automatically moves any **returning** player (career pattern: *played → gap → returned*, i.e. delisted-then-recalled) onto their **re-entry pathway**, **in place, during load**. The file may say `2019 ND #35` but the model counts that player at e.g. `2025 SSP` (effpk 86). It triggers on the **career pattern**, NOT on any field/flag, and it was verified empirically (a full-value duplicate placed in the original pool is ALSO dragged to SSP — both copies landed in SSP).

Players currently auto-consolidated (file entry → model entry):
- **Flynn Perez** 2019 ND #35 → 2025 SSP
- **Mark Keane** 2018 IRE → 2022 SSP
- **Lachlan McAndrew** 2021 MSD #12 → 2024 SSP
- **Hugo Hall-Kahan** was 2022 MSD #11 → 2026 MSD (now **solidified in-file to 2026 MSD**, so no longer relies on the inference)

**Consequence:** a returning player's ORIGINAL draft slot is vacated in the model view, and their original pathway pool loses them. The phantoms below fill / credit those slots.

**⚙️ cont.14 NOTE — these 4 are now ALSO set explicitly via `PRESENT_ID_OVERRIDES` in rl_model.py** (relocated from compute.py so the BOARD applies them): Perez→SSP 2025, Hall-Kahan→MSD 2026, McAndrew→SSP 2024, Keane→SSP 2022. This formalises the auto-recall re-entry (no longer relies only on the pattern inference) and drives the VALUE anchor (type/year/_grp/_eff). **Display convention (unchanged, not a bug):** the board's `_draft` label still shows each player's FILE pathway (Keane=Ireland, McAndrew=Mid-Season, Perez=National, Hall-Kahan=Mid-Season) while the value is computed at the SSP/MSD re-entry. With establishment-P now live, McAndrew is valued at SSP-2024 × P=0.28 → 1755 but labelled "Mid-Season", exactly as Keane is labelled "Ireland". Showing re-entry pathways instead would be a 1-line global change (reset `_draft` in the override loop).

---

## 1. BUST PHANTOMS (`_phantom=True`, `scoring=[]`, best2=0)
| key | record | why |
|---|---|---|
| `phantom-2019nd35` | "Phantom (2019 ND #35 bust)" — 2019 ND #35, GDEF | Perez (real) is consolidated to 2025 SSP, vacating ND #35. This makes pick **2019 #35 count as a bust** in the ND curve. ⚠️ The FILE has an intentional **PAIR** at 2019 ND #35 (Perez's real record + this phantom). **Any ND re-rank MUST skip `_phantom` records AND recall-consolidated players, or it will corrupt 2019's numbering** (push picks down by one). |
| `phantom-2022msd11` | "Phantom (2022 MSD #11 bust)" — 2022 MSD #11, GDEF | Hall-Kahan's 2022 MSD pick produced no games until 2026; his record was solidified to 2026 MSD, so 2022 MSD #11 holds **only** this phantom (no pair, no landmine). Makes that pick a **bust in the MSD pool**. |

## 2. DOUBLE-COUNT CREDIT PHANTOMS (`_phantom=True` AND `_double_count=True`) — ⚠️ DELIBERATELY DISHONEST
| key | record | best2 |
|---|---|---|
| `mark-keane-ire-credit` | "Mark Keane (IRE credit)" — 2024 IRE, KDEF, scoring=[{2024,77.9,21},{2025,77.7,25}] | ~77.8 |
| `lachlan-mcandrew-msd-credit` | "Lachlan McAndrew (MSD credit)" — 2026 MSD, RUC, scoring=[{2026,87.1,13}] | ~87.1 |

**Why (Luke's explicit call, "as dishonest as that sounds"):** Keane and McAndrew came through their ORIGINAL pathway (IRE / MSD) and THEN re-entered via SSP. The auto-recall counts them ONLY at SSP. Luke wants **both** mechanisms credited. A plain duplicate does NOT work (the consolidation drags both copies to SSP — tested). So these credit phantoms use **no-gap scoring mirroring each player's real peak**, which the consolidation ignores → they stay in the IRE / MSD pool, while the **real** records (`mark-keane`, `lachlan-mcandrew`) stay in SSP.

**RESULT = an intentional DOUBLE-COUNT:** each player's value is counted in BOTH the original pool (IRE/MSD) AND SSP. Verified: Keane appears in IRE pool (credit phantom) + SSP pool (real); McAndrew in MSD pool (credit) + SSP (real). This **inflates the IRE & MSD pooled value / hit-rate / n that feed PICKEQ** — by design.

---

## 3. WATCH-ITEMS (do not get caught out)
- These are **fabricated** records. The real players live elsewhere (Perez/Keane/McAndrew → SSP; Hall-Kahan → 2026 MSD).
- **Identify:** bust phantoms = `_phantom=True` with `scoring=[]`; double-count credits = `_phantom=True` AND `_double_count=True`.
- **Distinct-player audits:** exclude `_phantom` records, and note **Keane & McAndrew each appear TWICE** (real SSP + credit phantom).
- **The credit phantoms' scoring is HAND-SET** to mirror real peak (Keane 77.8, McAndrew 87.1). If the real players' output changes in a future data refresh, **update these phantoms** or they drift.
- **The credit phantoms' year/scoring is chosen to have NO GAP** so the recall consolidation ignores them. **Do NOT "correct" them to the real original draft year if that re-introduces a gap** — it would re-consolidate them to SSP and silently kill the double-count.
- **Benjamin Johnson** (`benjamin-johnson-2019`, 2019 ND #58, GDEF, scoring=[]) is **NOT a phantom** — he's a REAL never-played player re-added after an earlier slug-dedup wrongly dropped him (clashed with 2009 `ben-johnson`). Genuine bust entry; leave as a normal record.
- **Phantom count: 4** (`_phantom=True`). Quick check: `python3 -c "import json;d=json.load(open('rl_after/rl_model_data.json'));print([p['key'] for p in d if p.get('_phantom')])"`

## cont.19 — SAME-NAME DOB collision (2026-06-22)
dob_corrected.json keyed by composite name|debut, NOT name. Two Sam Fishers (2004/2017), two Alwyn Daveys (2007/2023, the son), two Callum Browns share names. Name-keying ages the young player wrong. Use composite key + era-disambiguation when loading DOBs into rl_model_data.json.
