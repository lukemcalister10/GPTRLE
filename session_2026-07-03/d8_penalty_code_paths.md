# DIAG-B rev3 ASK 5c — the penalty code paths as they hit 2025 draftees, QUOTED (engine v2 `4a134d05`, cp `5ac8b162`)

_All line numbers = `engine/rl_after/_merged_recover.py` (mr) and `engine/forward_valuation/conditional_prior.py` (cp) on branch `claude/d7-bake-candidate-v2`. Season state at the store cut: **R14 of 24 rounds** (fE = 14/24 = 0.583). Engine untouched — quotes only._

## 1. SIT-OUT / NO-GAMES anchor — the branch that REPLACES the whole valuation

The qualification counter (mr:215) — an **absolute ≥6-games bar, not prorated**:
```python
def nseas(p,Y=2026): return sum(1 for x in p['scoring'] if x['games']>=6 and x['year']<=Y)
```
The branch (mr:225-236):
```python
SITOUT_RETAIN={'RUC':[0.85,0.85,0.74,0.62,0.51,0.40],'KPP':[0.70,0.70,0.60,0.50,0.40,0.30],'nonKPP':[0.50,0.50,0.42,0.35,0.28,0.20]}
def _sitout_cls(pos): return 'RUC' if pos=='RUC' else ('KPP' if pos in ('KEY_FWD','KEY_DEF') else 'nonKPP')
...
    if ns==0:                                                 # SIT-OUT (never played >=6g through Y, still listed)
        N=min(max(el,1),6)
        return round(dv*SITOUT_RETAIN[_sitout_cls(pos)][N-1])
```
**Basis: FULL SEASON.** A 2025 draftee needs 6 games to escape this branch when only 14 rounds have been possible — the bar is the same 6 that applies to a completed 24-round season. Every 2025 draftee with 0–5 games is priced at a flat 0.50×draftval (nonKPP) / 0.70 (KPP) / 0.85 (RUC), **regardless of how well they scored in those games** (the `return` skips the entire raw path). Mid-season this branch catches players who will have cleared 6 games by round 24.

## 2. POLE exposure gate — pedigree-upside recovery scaled by games out of a FULL season

mr:26 and mr:115-118 (inside `raw_ev`):
```python
PROVEN_N=4; POLE_RAMP=22.0
...
    expgate=1.0 if _nqual(p,Y)>=PROVEN_N else min(1.0, cp._exposure(p,Y)/POLE_RAMP)
    w=wage*tfade*expgate
    return pr+w*recover(perf,par)*max(0.0,po-pr)
```
**Basis: FULL SEASON (22).** For a first-year player `cp._exposure` = current-season games (no decay on the in-progress year), so the pedigree-pole recovery term is scaled by g/22 — an **ever-present 14-game player reads expgate = 14/22 = 0.64**, where the same player at the end of a completed Yr1 (20–23 games) reads ~1.0. Not prorated to the 14 rounds elapsed.

## 3. Level reliability ramp — demonstrated level shrunk by games/14

cp:77-81:
```python
LEVEL_RAMP=float(os.environ.get('RL_LEVEL_RAMP','14'))   # recency-wtd games for the level to count FULLY (dial)
def _lvl_eff(p,Y):
    return _lvl_wt(p,Y)*min(1.0, _exposure(p,Y)/LEVEL_RAMP)
```
**Basis: fixed 14 recency-weighted games.** At R14 only a literal ever-present reaches 1.0; a 9-game 2025 draftee's demonstrated level enters the band features at 9/14 = 64% of face value. The same absolute bar applies to completed seasons — it is not scaled by season progress. (This also feeds `_feat` → the GBR band prior, whose raw `exposure` feature likewise reads mid-season games with no proration.)

## 4. Stalled / never-produced decay (the other "no-games" penalty)

mr:237-243:
```python
    keyruc = pos in ('KEY_FWD','KEY_DEF','RUC'); onset = 2 if ns==0 else (4 if keyruc else 3)
    if el>=onset and ns<=1:                                   # stalled: essentially no production after the window
        frac=0.25*max(0.4,1-0.10*(el-onset))*(1.6 if keyruc else 1.0)
        e=min(e, dv*frac)
```
Tenure-gated (`el>=onset`, onset≥2) — **does NOT bind on 2025 draftees** (tenure 1). Quoted for completeness: same unprorated `nseas` bar.

## 5. What IS prorated (and what it covers)

**M2** (cp:54-68) prorates the **decay clock on PRIOR seasons** while 2026 is in progress:
```python
EXPO_F=float(os.environ.get('RL_EXPO_F','0.545'))             # durable-player pace; 1.0 -> lever off
EXPO_DEN=11.0
def _exposure(p,Y):
    rows=_season_rows(p,Y)
    if Y==EXPO_INPROG_Y and EXPO_F<1.0:
        gy=sum(g for yr,g,_ in rows if yr==Y)
        s=min(1.0,max(0.0,1.0-gy/EXPO_DEN))
        if s>0.0:
            ex=1.0-s*(1.0-EXPO_F)
            return float(sum(g*(1.0 if yr==Y else RECENCY_DECAY**(max(0,Y-yr-1)+ex)) for yr,g,_ in rows))
    return float(sum(g*_swt(yr,Y) for yr,g,_ in rows))
```
For a 2025 draftee there ARE no prior seasons — **M2 is a no-op on this cohort.**

**M3** (mr:256-271) prorates the **age/tenure CLOCKS** (value-space blend with a clock-pinned eval, weight `1-s*(1-0.58)`, `s=clip(1-g26/11,0,1)`). It lifts under-exposed young players, but it moves the clocks only — **it does not touch the games-basis gates in §1–§3**. And for the §1 sit-out branch M3 is a structural no-op: the pinned eval hits the same `dv*SITOUT_RETAIN[cls][max(1,N-1)-1]` = the same retain value (tenure floor 1), so blend = identity.

**Floor** (mr:280-291): `max(ev, 0.45*draftval)` at years-since-draft 1 — lifts the worst prices, unrelated to proration.

## PLAIN STATEMENT (the ASK's question)
- The sit-out/no-games qualification (`games>=6`), the proven-season bar (`games>=10`), the level ramp (14) and the pole ramp (22) are ALL computed against **full-season-scale absolute games constants** — none is prorated to the 14-of-24 season position. (The engine's nominal season constant is `SEASON=22` (cp:18); Luke's "out of 24" is rounds — the operative bases are 6/10/14/22 games.)
- The ONLY proration anywhere in the engine is M2 (prior-season decay clock — no-op for Yr1 players) and M3 (age/tenure clocks — no-op for the sit-out branch, partial lift elsewhere).
- Games-played smoothing exists INSIDE the level machinery (`_lvl_wt`/`_exposure` are games-weighted and cliff-free), but the `ev()`-level gates in §1 and §4 are hard thresholds on unprorated bars, and §1 discards the scoring evidence entirely.
