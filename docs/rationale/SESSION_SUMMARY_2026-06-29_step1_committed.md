# SESSION SUMMARY 2026-06-29 — STEP 1 COMMITTED (#1-family thin-evidence fix)
Engine md5 **7f7d7f76 -> 38de7a01716d**. Band pickle UNCHANGED (34faa8659). Stage-0, nothing baked.

## What shipped
A-vs-B inversion (one-season-70 outpriced a proven five-season climber ~2.85x) confirmed a BUG = third face of
"not-enough-penalty-for-thin-evidence" (with Cook=zero-evidence and the yr2 cohort peak). Built + supervisor-approved +
COMMITTED a both-ends fix, inference-only so the band pickle/q97m/ISO/pole keep their ORIGINAL-feature training and
proven-flat players stay byte-identical:
 1. career-evidence shrinkage (thin -> shrink _lvlcurr toward pedigree par, c=n/PROVEN_N)  [A down]
 2. grower current-level read _lvlcurr (proven & not-flat -> current level, not career avg)  [B up]
 3. developmental tenure eff_ten=max(base,age-18), thin-career only, parametrized per call site  [flips A<B; = mature-age fix]
 4. pole exposure-gate (thin-only) + staleness onset=2 for never-produced  [Cook decays]

## Verification (committed engine vs extracted pre-commit /tmp/orig_engine 7f7d7f76, via _verify_panel.py)
(a) A 2941->1096, B 1038->1403  B>A   (b) proven-flat 8/8 byte-identical MAX|Delta|=0   (c) growers rise; Cook 879/456/411/365/319.
Full falsifier block sane. Boekhorst = delisted washout (16, unchanged). Trajectory lift = current-level read, parked feature still parked.

## Delta=0 leak hunt (resolved)
Three layers: ISO rebuild (deferred rebind past ISO), eff_ten tenure base (parametrized by call site), and the real one —
par_pole computes the pole LIVE through the band on a 2-season synth, so the fix dragged the pole -327 and bled -8 into
proven players' T5 lift. FIX: froze _POLE on original features before the rebind. Pole = pick-side, rebuilt step 2-4.

## NEXT — STEP 2 (the pick-valuation spine begins)
Monotone pole smoothing over log-pick for ALL positions (KEY_FWD pk1=2217<pk2=2221 violation; GEN_FWD pk10>pk5; RUC pk20>pk10),
RUC thin-pooling (say which positions needed it), par level untouched, fix the PRICE; #5 pk60 rides along. Open step-2 design
question: smooth frozen-original pole, or recompute through the fixed band first? Report post-smoothing pole table all positions.
Then step 3 par-player calibration (also calibrates the provisional dials).
