"""CONDITIONAL OUTCOME-SHAPE PRIOR (component 1 of the band redesign).
Replaces build_prior's symmetric-normal-from-incomplete-careers. Predicts the DISTRIBUTION (quantiles) of forward best-3
given (position, pick, games-played-so-far, tenure), calibrated to RESOLVED careers (censoring-corrected), busts included
so the lower tail is honest. Smooth (quantile GBR on continuous features). This is the PRIOR only — the player's own
demonstrated band + reliability blend come in components 2-3.
  Validate: cd rl_after && PYTHONHASHSEED=0 python3 ../forward_valuation/conditional_prior.py
"""
import sys; sys.path.insert(0,'/home/claude/rl_after')
import os; os.environ.setdefault('RL_GAMMA','0.85'); os.environ.setdefault('RL_PICK1','3000')
import io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()): import rl_model as MA
from sklearn.ensemble import GradientBoostingRegressor

Q=[0.10,0.30,0.50,0.70,0.90]
GROUPS=['MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC']
GIDX={g:i for i,g in enumerate(GROUPS)}
KMAX=70
SEASON=22

def debutyr(p): return p['year'] if p['type']=='MSD' else p['year']+1
def games_through(p,Y): return sum(x['games'] for x in p['scoring'] if x['games']>0 and debutyr(p)-1< x['year']<=Y)
def level_through(p,Y):  # best single-season avg through Y (just for the bust/served split target, not a feature here)
    a=[x['avg'] for x in p['scoring'] if x['games']>=6 and x['year']<=Y]
    return max(a) if a else 0.0
def fwd_best3_from(p,Y,cap):
    """resolved forward best-3 from year Y onward (>=max(Y,debut)). busts: best single season if <3 qual, else 0."""
    lo=max(Y, debutyr(p))
    qual=sorted([x['avg'] for x in p['scoring'] if x['games']>=6 and lo<=x['year']<=cap],reverse=True)
    if len(qual)>=3: return float(np.mean(qual[:3]))
    if len(qual)>=1: return float(np.mean(qual))          # partial: average what qualifies
    any_season=[x['avg'] for x in p['scoring'] if lo<=x['year']<=cap and x['games']>0]
    return float(max(any_season)) if any_season else 0.0  # played sub-6-game seasons -> low; never played -> 0 (bust)

def _lvl_asof(p,Y):
    """LEGACY (pre cont.25 rebuild): mean of last up-to-2 qualifying-season (>=6g) avgs. Kept for reference only."""
    qs=sorted([(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6 and x['year']<=Y],reverse=True)[:2]
    return float(np.mean([a for _,a in qs])) if qs else 0.0

# ---- cont.25 rebuild: SMOOTH games+recency-weighted evidence (no >=6g cliff; MSD/partial-season & long-gap aware) ----
RECENCY_DECAY=float(os.environ.get('RL_RECENCY_DECAY','0.72'))   # per-year decay on game-evidence (dial)
def _season_rows(p,Y):
    return [(x['year'],x['games'],x['avg']) for x in p['scoring']
            if x['games']>0 and (debutyr(p)-1) < x['year'] <= Y]
def _swt(yr,Y): return RECENCY_DECAY ** max(0, Y-yr)
# ---- M2-EXPOSURE (BAKE CANDIDATE, D4 02/07/2026 — Luke's written go; NOT baked until Luke's bake word) ----
# While season EXPO_INPROG_Y is IN PROGRESS, the prior-season decay clock advances at the durable-player pace
# f instead of a full click, scoped by evidence replacement s = clip(1 - g_Y/EXPO_DEN, 0, 1): players with
# >= EXPO_DEN current-season games are untouched BY CONSTRUCTION (s=0). Byte-exact at f=1 and on all completed
# seasons: the in-progress exponent max(0,Y-yr-1) + 1 - s*(1-f) collapses to max(0,Y-yr) when s=0 or f=1.
# f is DERIVED PER EVALUATION DATE (durable-player elapsed pace): median on-pace g26 = 12.0 / 22 -> 0.545 at
# the 2026-07-02 store cut (band 0.52-0.68; A3 flat across the band). EXPO_DEN = 11 (the on-pace floor) is the
# zero-collateral denominator (0/288 on-pace movers >2%, max 0.00% — D3 ASK3, session_2026-07-02/scripts/
# d3_ask3_final.py). Derivation: session_2026-07-02/dropfix_design_M2exposure.md. RL_EXPO_F=1 = kill-switch.
EXPO_INPROG_Y=int(os.environ.get('RL_EXPO_INPROG_Y','2026'))  # the season in progress at the store cut
EXPO_F=float(os.environ.get('RL_EXPO_F','0.545'))             # durable-player pace; 1.0 -> lever off (byte-exact)
EXPO_DEN=11.0                                                 # evidence-replacement denominator (on-pace floor)
def _exposure(p,Y):
    """Recency-weighted reliable game-count = the UNCERTAINTY signal (replaces raw cumulative games). Smooth: phases in
    from game 1; old games decay, so a long gap (e.g. Conway) reads as ~no recent exposure rather than '6 career games'.
    M2: in-progress season -> prorated decay clock (block comment above); completed seasons byte-exact."""
    rows=_season_rows(p,Y)
    if Y==EXPO_INPROG_Y and EXPO_F<1.0:
        gy=sum(g for yr,g,_ in rows if yr==Y)
        s=min(1.0,max(0.0,1.0-gy/EXPO_DEN))
        if s>0.0:
            ex=1.0-s*(1.0-EXPO_F)
            return float(sum(g*(1.0 if yr==Y else RECENCY_DECAY**(max(0,Y-yr-1)+ex)) for yr,g,_ in rows))
    return float(sum(g*_swt(yr,Y) for yr,g,_ in rows))
def _lvl_wt(p,Y):
    """Demonstrated level weighted by games-in-season x recency. Smooth (no >=6g threshold -> kills the game-6 value cliff);
    a partial first season (MSD) contributes PARTIALLY not at face value; recent form dominates older seasons."""
    rows=_season_rows(p,Y); tw=sum(g*_swt(yr,Y) for yr,g,_ in rows)
    return float(sum(g*_swt(yr,Y)*a for yr,g,a in rows)/tw) if tw>0 else 0.0
def _age_asof(p,Y):
    a=MA.age(p)
    return float(a-(MA.AGE_REF-Y)) if a is not None else 18.0+max(0,Y-(debutyr(p)-1))
LEVEL_RAMP=float(os.environ.get('RL_LEVEL_RAMP','14'))   # recency-wtd games for the level to count FULLY (dial)
_SFE=float(os.environ.get('RL_M3_FE','0.58'))            # D10 03/07/2026: season-progress proration (R14/24 convention, same dial as M3)
def _playable_fse(p,Y):                                  # full-season-equivalent games playable since debut
    return SEASON*(max(0,Y-debutyr(p))+((_SFE if Y==EXPO_INPROG_Y else 1.0) if Y>=debutyr(p) else 0.0))
def _lvl_eff(p,Y):
    """Reliability-shrunk level: the weighted level scaled by how much recent evidence backs it. A 5-game stint reads as a
    fraction of its face value (kills tiny-sample over-read e.g. Conway's 5g@80); phases in smoothly to full by ~a season.
    D10: the trust bar cannot exceed the games actually PLAYABLE (yr-1 mid-season 14 -> 14*fE=8.2); completed seasons and
    every training row are byte-identical (playable >= SEASON there)."""
    ramp=LEVEL_RAMP*min(1.0, _playable_fse(p,Y)/SEASON)
    return _lvl_wt(p,Y)*min(1.0, _exposure(p,Y)/max(ramp,1e-9))

def _feat(p,Y):
    oh=[0.0]*len(GROUPS); oh[GIDX[MA.gfut(p)]]=1.0
    ep=min(MA.effpk(p),KMAX); ten=max(0,Y-(debutyr(p)-1))
    return oh+[np.log(ep), _exposure(p,Y), ten, _lvl_eff(p,Y), _age_asof(p,Y)]

def build_cond_prior(cap=2026, resolved_cut=2021, pool=None):
    """Train quantile models on RESOLVED careers (debut<=resolved_cut). One row per (player, as-of-year Y) from draft year
    (games 0) through their last season; target = resolved forward best-3 from Y."""
    if pool is None: pool=[p for p in MA.data if MA.GRP.get(p['pos'])]
    X,y=[],[]
    for p in pool:
        if debutyr(p)>resolved_cut: continue                # resolved only
        if not (p.get('pick') or p.get('_ft')): continue
        d0=debutyr(p)-1                                      # draft year (0 games)
        last=max([x['year'] for x in p['scoring']]+[d0])
        for Y in range(d0, min(last,cap)+1):
            t=fwd_best3_from(p,Y,cap)
            X.append(_feat(p,Y)); y.append(t)
    X=np.array(X); y=np.array(y)
    _NTREES=int(os.environ.get('RL_PRIOR_TREES','400'))   # default 400 (no change); lower only for fast mock sweeps
    models={q:GradientBoostingRegressor(loss='quantile',alpha=q,n_estimators=_NTREES,max_depth=4,
            learning_rate=0.05,min_samples_leaf=25,random_state=0).fit(X,y) for q in Q}
    return models, len(y)

def cond_prior_band(p, models, Y=None):
    if Y is None: Y=MA.BASE_REF
    f=np.array([_feat(p,Y)])
    return np.sort(np.array([float(models[q].predict(f)[0]) for q in Q]))

# ----------------------- validation -----------------------
if __name__=='__main__':
    models,n=build_cond_prior()
    print(f'trained conditional prior on {n} resolved (player,year) rows')
    allp=[p for p in MA.data if MA.GRP.get(p['pos'])]
    def debut(p): return debutyr(p)
    def cb3(p):
        a=sorted([x['avg'] for x in p['scoring'] if x['games']>=6],reverse=True)[:3]
        return float(np.mean(a)) if a else None
    # check 1: at DRAFT (games=0, tenure=0), does the prior reproduce realized best-3 quantiles by position x pick?
    print()
    print('VALIDATION 1 — prior AT DRAFT (0 games) vs realized best-3 (resolved), by position x pick:')
    print('  pos        pk | prior p10/p50/p90 | realized p10/p50/p90 (n)')
    import types
    class _Stub:  # build a feature at draft for an arbitrary (pos,pick)
        pass
    def realized_q(g,pk):
        v=[cb3(p) if cb3(p) is not None else fwd_best3_from(p,debutyr(p)-1,2026)
           for p in allp if MA.gfut(p)==g and (p.get('pick') or p.get('_ft')) and abs(min(MA.effpk(p),70)-pk)<=3 and debutyr(p)<=2020]
        if len(v)<6: return None
        a=np.array(v); return np.percentile(a,10),np.percentile(a,50),np.percentile(a,90),len(a)
    def prior_q_at(g,pk):
        oh=[0.0]*len(GROUPS); oh[GIDX[g]]=1.0
        f=np.array([oh+[np.log(pk),0.0,0.0,0.0,18.5]])   # at draft: exposure=0, tenure=0, level=0, age~18.5
        return np.sort([float(models[q].predict(f)[0]) for q in Q])
    for g in GROUPS:
        for pk in [3,8,15,30]:
            rq=realized_q(g,pk)
            if rq is None: continue
            pq=prior_q_at(g,pk)
            print(f'{g:8s} {pk:3d} | {pq[0]:5.0f}/{pq[2]:.0f}/{pq[4]:<5.0f} | {rq[0]:5.0f}/{rq[1]:.0f}/{rq[2]:<5.0f} (n={rq[3]})')
        print()
    # check 2: the LEVEL+tenure mechanism — at tenure 1, does a higher Y1 level lift the projected peak (and lower tail)?
    print('VALIDATION 2 — Y1-vs-expectation (MID pick 7, tenure 1, games 22): does a higher Y1 level lift the peak band?')
    for lv in [50,65,80,95]:
        oh=[0.0]*len(GROUPS); oh[GIDX['MID']]=1.0
        f=np.array([oh+[np.log(7),22.0,1.0,float(lv)]])
        pq=np.sort([float(models[q].predict(f)[0]) for q in Q])
        print(f'  Y1 level={lv:2d}: p10/p50/p90 = {pq[0]:.0f}/{pq[2]:.0f}/{pq[4]:.0f}')
