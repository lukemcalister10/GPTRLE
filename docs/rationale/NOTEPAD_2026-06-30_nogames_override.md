# Notepad — turn response, 2026-06-30 (no-games override wiring)

Wired a candidate (price6 fix + position-aware no-games override together) and verified on relativities.
Three of the four targets land right; the fourth is a real judgment call I need to put back to you. Bake still held.

WHAT THE OVERRIDE DOES: for still-listed sat-out players it replaces the position-blind staleness floor with a
position-aware retention (RUC/KPP gentle, nonKPP steep), declining with years sat. Delisted busts still fall
through the delist gate untouched, so this only governs kept projects.

TOP-50 ND RUCK TABLE — before, then override on two baselines (draftval vs the normal price6-fixed value):
  Player    Yr   Pk  sat  Before  dvOVR  normOVR
  Conway    2021 24   5    175    295    554
  Barnett   2022 23   4    201    372    509
  Knobel    2022 42   4    161    298    445
  Green     2023 16   3    364    707    622
  Goad      2023 20   3    269    523    664
  Edwards   2023 32   3   1057   1057   1057
  Smith     2023 47   3    153    296    540
  Emmett    2025 27   1   1051   1051   1051

HOLDS:
1) Case 2 fixed — sat-out project rucks lift off the over-crush (Green 364->707, Goad 269->523, Conway 175->295).
2) Years-sat works — Conway (sat5) below Green/Goad (sat3) under both baselines, and above his old 175.
3) Sat-out mids stay crushed (C.Edwards 157->141, DeMattia 141->126, Hustwaite 111->95) — lifts rucks WITHOUT
   rescuing mids, as predicted. Position ordering is data-backed: sat-out RUC/KPP ~0.40x draftval vs nonKPP ~0.22x.

DOESN'T HOLD (judgment call, not a bug): Green/Goad do NOT clear Emmett (707/523 or 622/664 vs 1051). Reason is
the through-line itself — Emmett played a game (a demonstrated signal, however thin); Green/Goad are pure pedigree
who've sat three years. Pushing sat pure-pedigree rucks ABOVE a player who's shown something contradicts "value
requires a demonstrated signal; pedigree alone isn't one." The engine currently says signal beats pedigree.
WHICH DO YOU WANT?

EDWARDS FLAG (next thread): not docked (good) but not credited either — full season @50.8 (1057) sits level with
Emmett's one game @32.8 (1051). Production not rewarded over Emmett. That's the production-credit/decliner axis.

BASELINE TRADEOFF (live dial): draftval respects pick order (Green pk16 707 > Goad pk20 523 > deep) but Conway
barely clears the crush; normal-value lifts Conway more (554) but compresses/inverts picks (Green 622 < Goad 664).
Retention LEVEL (median 0.40x vs survivor 0.76x) is measure-dependent — defer to the PVC.

HELD FOR YOUR CALLS: (A) baseline draftval vs normal-value; (C) should sat pure-pedigree rucks sit above or below
a played-thin-signal ruck. Levels (B) deferred; Edwards (D) next. Once A and C resolve, bake price6 fix + override
together. Engine e0ac9c377d1e, nothing baked.
