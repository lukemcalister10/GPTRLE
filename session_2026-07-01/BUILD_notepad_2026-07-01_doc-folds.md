# BUILD notepad — 2026-07-01 — doc items folded (Langdon causal correction + md5-axes line)

STATUS: Two approved doc edits FOLDED into the tarball source dir /home/claude/rl/rl_complete_8aed420a/ (the re-cut origin).
NOT re-cut (per supervisor: do not re-cut just for these; next real re-cut carries them). Engine head 8aed420a and store
pre_stage0 644d1254 UNCHANGED — these are pure doc corrections, nothing baked, no code/data/store touched. Scratch .py files
are in the workspace only, not in the source dir, so a re-cut from the source dir won't pick them up.

This notepad carries the FULL verbatim text of both edits so they are recoverable even if this chat ends before the next re-cut.

================================================================================
EDIT 1 of 2 — PROVENANCE_2026-07-01.md section (d), Ed Langdon bullet  +  docs/CHANGELOG.md item (2)
Langdon causal story corrected (fix DECISION untouched; 593 stays; 70/30 stays).
================================================================================

--- PROVENANCE (d), Ed Langdon bullet — NEW TEXT ---
- Ed Langdon  drafted MID -> GFWD(last yr) -> GDEF(now): _pos_now GFWD -> GDEF; _fut [GDEF 50, MID 50] ->
  [GDEF 70, MID 30]. ev 1122 -> 593. FIX DECISION CORRECT (593 = veteran defender; both field corrections AND the
  70/30 pole stand). CAUSAL STORY CORRECTED 2026-07-01 (pole-vs-bar decomposition; 2x2 + Shapley, round-trip
  validated): the drop is ~100% the present-position BAR (bnow GEN_FWD ~68 -> GEN_DEF ~75, +7.4 pts/gm on the
  dominant year-0 term), NOT the _fut pole. The pole contributed ~0 (Shapley +1): gfut = max(_fut) is GDEF in BOTH
  50/50 (tie -> first-listed) and 70/30, so the curve/peak/runway channel never moved; only futblend shifted
  (MID 0.5 -> 0.3), immaterial for a 215-game short-runway veteran. And MID pole weight is DEFLATIONARY not
  inflationary (adding MID LOWERS him: 1122 -> 1103, 591 -> 574) -> the earlier "removing 50% MID pole inflation"
  story was wrong on BOTH the driver and the sign. 70/30 is +-2 pts on price (immaterial); left as-is.
  RESIDUAL WATCH: a veteran whose _fut spans DISSIMILAR buckets (KEY/RUC vs GEN) would still carry a large pole term.

(REPLACED the old text: "...[GDEF 70, MID 30] (was landing GDEF only by tiebreak). ev 1122 -> 593 (driven by
 removing the 50% MID pole inflation; now priced as the veteran defender). The 70/30 weight is a 'mostly-defender,
 residual mid' choice — tunable if Luke's read differs.")

--- docs/CHANGELOG.md item (2) — NEW TEXT ---
#   (2) _pos_now double-switcher fixes (store data, pre_stage0 cf8b3c5e->644d1254): Maric _pos_now GDEF->MID
#       (ev 1427->1409); Langdon _pos_now GFWD->GDEF + _fut [GDEF50,MID50]->[GDEF70,MID30] (ev 1122->593; CAUSAL
#       STORY CORRECTED 2026-07-01 by pole-vs-bar decomp: drop is ~100% the present-position BAR GFWD->GDEF, _fut
#       pole ~0 [Shapley +1], MID DEFLATIONARY not inflationary; fix decision + 70/30 stand - see PROVENANCE (d)).
#       Panel 10/10; full 2654-diff = ONLY these 2 moved.

(REPLACED the old causal clause: "...(ev 1122->593, removes tiebreak-MID pole inflation).")

================================================================================
EDIT 2 of 2 — START_HERE.md, md5-axes clarity block (inserted adjacent to the engine/store md5 line)
================================================================================

--- INSERTED after the "Engine CODE md5 8aed420a ... Store pre_stage0 = 644d1254." line ---
> **IDs are on DIFFERENT axes — a mismatch here is NOT automatically drift.** The bundle CHECKSUM changes on every
> re-cut (any file — data, harness, doc). The engine-code head (`8aed420a`) changes only on a code edit. The store
> `pre_stage0` (`644d1254`) changes on data edits. The tarball FILENAME follows the engine head
> (`rl_complete_<engine-head>.tar[.gz]`), NOT the bundle checksum. A fresh bundle checksum over an unchanged engine
> head is the normal signature of a data/harness/doc-only re-cut — not drift. Verify the internal heads listed here;
> the filename and bundle checksum are packaging, not the identity to check against.
> (Concrete example this snapshot: bundle checksum 89459a9b sits over engine head 8aed420a and store 644d1254 — all correct.)

================================================================================
NEXT
================================================================================
- HOLDING for the MEDIOCRE-OVERVALUATION decomposition (Luke #1: mediocre proven players hold too much value, curve not
  convex enough; flagship Joel Jeffrey valued above Jack Ginnivan). Diagnosis-first prompt is the next relay; NO fix design ahead of it.
- Population pole-value-share-by-career-stage analysis: PARKED (called for later).
- Discipline locked: exact id / pick / cohort keying everywhere; never substring-match (several same-name / father-son pairs in the store).
- On the next real re-cut: originate from /home/claude/rl/rl_complete_8aed420a/ (holds both folded edits); do NOT re-extract.
