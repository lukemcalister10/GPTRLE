# D13 ASK 2 — V0 PICK-ORDER GUARD (Luke's law)

**STATE:** CONTROL = canonical `8aed420a` · PREVIOUS = CANDIDATE v2.2 `af1fc6aa` · CURRENT = CANDIDATE v2.3.

> <<<LUKE 2026-07-03>>> "v0 for the same age and position cannot be higher for a lower pick in the same draft. I understand mature age players rightfully will be calculated differently."

**Wiring.** Within **(position × draft-age × draft-year)** cells, V0 is strictly **non-increasing in recorded pick** (a worse pick cannot start above a better one). Downward-only projection — only violators are pulled to the running min of better picks in-cell; nobody is lifted. Built at load time (like the ISO/POLE tables). Mature-age / differing-age players sit in **separate draft-age cells → exempt by construction**.

**Divergence scan (recorded vs effective pick):** **0 / 1571 ND players diverge** — expected none, confirmed. (All 802 roster divergences are non-ND: RD 693 / MSD 107 / SSP 2 = empirically-derived pick-equivalents, outside the ND-pick guard scope.)

**Roster-wide per-cell inversion scan:**

| | inversions | cells |
|---|---|---|
| BEFORE (v2.2 `af1fc6aa`) | 449 | 106 |
| AFTER (v2.3 guarded) | **0** | — |

**Named fixes:**

| pair (cell) | before | after |
|---|---|---|
| Cumming\|2025\|7 vs Robey\|2025\|9 (MID·age18·2025) | Robey V0=1882 **>** Cumming V0=1864 (inversion) | both 1859 — Robey ≤ Cumming ✓ |
| **largest** Jhye Clark(pk8) vs Cameron Mackenzie(pk7) (MID·age18·2022) | Jhye Clark V0=2401 **>** Cameron Mackenzie V0=1864 (gap 537) | Jhye Clark → 1864 ≤ 1864 ✓ |

**Age-preservation (mature age calculated differently — exempt by cell construction).** MID 2017: **Tim Kelly** (pk24, age 23, mature) V0=71 vs **Patrick Naish** (pk34, age 18) V0=567. If draft-age were pooled, Naish (worse pick) would be wrongly clamped down to Kelly's 71; because they sit in separate draft-age cells, **Naish keeps his 567** — the mature-age player is calculated in his own cell, age differentiation preserved.
