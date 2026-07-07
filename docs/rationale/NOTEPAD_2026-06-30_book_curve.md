# Notepad — turn response, 2026-06-30 (book re-render + career-year tenure curve)

Engine 7147b824 (unchanged; no bake). Full book = BOOK_7147b824_2026-06-30.xlsx.

PART 1 BOOK (xlsx Book tab): value + production same row, per player per career year (1864 players). Switchers ◆/yellow
(drafted vs current shown), named ★/blue. Ed Allan RESOLVED = "Edward Allan" (MID pk19, 2022 cohort). 8 NAME COLLISIONS
flagged (Alwyn Davey, Sam Butler, Harrison Jones, Will Hamill, Josh Smith, John McCarthy, Tom Lynch, Mitchell Brown) --
do NOT merge, disambiguate by pick/cohort (Max/Maxwell King rule).

PART 2 TENURE CURVE (AFTER mean value; %d vs BEFORE, same players = survivorship-clean; medians in xlsx):
  POOLED peak cy6 (694); yr5-6 ~1.8-1.9x yr1.
  MID peak cy6 (920, ~1.8x); GEN_DEF peak cy7 (699, ~2.7x, latest outfield); GEN_FWD peak cy6 (450, ~1.4x flattest,
  biggest fade); KEY_DEF peak cy6 (545, ~1.8x); KEY_FWD peak cy6 (738, ~2.2x); RUC(thin) peak cy7-8 (~1070, ~3.2x steepest).
  Upside-fix %d yr3-6: gentle, -0.5 to -3.9%, biggest GEN_FWD; <=0 everywhere. Median<<mean (heavy skew; typical player low,
  stars carry the mean).

FINDING (book-as-instrument): first pass showed KEY_FWD +3..6% -- impossible for a down-only fade. Cause = before/after join
keyed on NAME, the 8 duplicate names collided. Re-joined by INDEX -> KEY_FWD -0.5..-3.3% (correct). Upside fix is clean/gentle,
no inflation. Pole-offset note: pole-lift rises as faded level drops price6 (Koschitzke 246->312) -> level-only fade is partly
self-offset for key-position players; nets ~0 at GENTLER, but a stronger nerf would need eo-fading the pole too. Flagged.

FLAGS: yr1-2 PROVISIONAL (no-games not wired, sat-out old values); yr3+ reliable, peaks in the reliable zone. Switchers 74
book / 77 active = 10.9% of board value -> two-field is the next structural job (curve still prices them on current bar).

PLAIN: value climbs from draft, peaks ~career year 6 (yr7 gen-def, 7-8 ruck), then falls; a yr5-6 player ~1.8-2.2x a yr1
(forwards flatter, rucks steeper). Upside fix nudges yr3-6 down gently (<4%), most on general forwards, never up. Most players
low-value, a few stars carry the average. yr1-2 not trustworthy till no-games wires.
