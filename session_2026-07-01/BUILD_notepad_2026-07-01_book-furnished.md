# BUILD notepad — 2026-07-01 — backtest book FURNISHED (xlsx) + two corrections

You were right — I had summarised the book but never furnished the per-player ledger. Now delivered as
combined_backtest_book_8aed420a.xlsx (3 sheets: Book / Summary / Flags). NOTHING baked. head 8aed420a / store 644d1254.

TWO CORRECTIONS made while building it:
1. SCOPE FIX. My first cut priced ALL players incl. pre-debut rookies, which mis-applied v7 to them (v7 compresses the
   cond_prior band; pre-debut players are priced via the PEDIGREE path, and shaving their unproven pedigree ceiling would
   violate the Harley-Reid guardrail). The book is now restricted to EXPERIENCED players (>=2 seasons) = the population v7
   is for. Pre-debut/rookies are out of scope (protected).
2. MISLABEL FIX. I earlier called Coe/Puncher/Knevitt/Tunstill "_fut data errors, same class as Maric/Langdon". WRONG.
   Verified: Coe (pick8) & Puncher (pick15) are unplayed 2026 draftees (empty scoring); the big negative gap is just high
   pedigree minus zero games — not a data error. They simply shouldn't have had v7 applied (correction #1).

UPDATED NUMBERS (correct experienced-only population, n=372): mean -15.3% / median -10.3%. down>2%:280 flat:80 up>2%:12.
  (The earlier -13.3/-7.5 was diluted by the out-of-scope rookies sitting at ~0%.)
  Worst (all in-scope): Sholl -84 (Flag A), Ladhams -71 (inj+decline RUC), Knevitt -69 (thin fringe), Robertson -64,
    Amartey/King -62/-60 (KEY_FWD ceiling). Best: Ash +12.9, Peatling +7.2, Callaghan +6.5, Blakey +6.3, Ginnivan +6.2 (risers).

BOOK sheet: 372 rows sorted by Delta% asc (crushes first), autofilter + freeze header + red/white/green colour scale on
  Delta%; columns Player/Pos/Age/QualSeas/YrsSince/MeanG/Trend/LvlGap/Current/Combined/Delta%/Tier/Archetype/M1fired/Note.
SUMMARY sheet: overall distribution + by-archetype/tier/position tables + scope note.
FLAGS sheet: Flag-A 34-name cohort (trust-the-level rec), Flag-B resolution (ceiling-shave, not a bug), the scope note.

STATE unchanged, nothing baked. Still HOLDING for your reads on the Flag-A names + confirm Flag-B, then the bake decision.
