# DISTRIBUTION PRICING (U21-4) — FINISHED MODEL (cont.24).
# Builds on forward_valuation/distribution_pricing_prototype.py, wiring all 6 spec TODOs.
# Full design: ../DISTRIBUTION_PRICING_SPEC.md. NOT wired into value() — this is a standalone repricer.
#
# THE WHOLE THING IN ONE FLOW:
#   1. BAND: freehand quantile models (q10/30/50/70/90) of forward best-3, on the engine's own features.
#   2. v_at_peak(p,L): value the player AS IF forward-peak = L, through the REAL production chain at the
#      player's REAL age (not PEAK_AGE) — so old stars decline (TODO#1) and proven stars hit their real
#      value() to the dollar (TODO#6). This is the convex map E[v(L)] pays the upside tail / discounts a
#      collapsed one — no separate pedestal / cvx / runway needed.
#   3. PRIOR: pedigree-graded forward-peak prior (centre+width) per position×pick, with the top of the
#      draft built by TREND EXTRAPOLATION (loclin / a*k^-b), not truncated neighbour-average (TODO#4).
#   4. SHRINK: blend each player's empirical band toward that prior IN PROPORTION TO LOCAL DATA THINNESS
#      (a function of LOCAL DATA COUNT, not pick) (TODO#3). K_SHRINK strength is SURFACED, not baked.
#   5. dist_value(p) = SCALE_DIST * E[v_at_peak over the shrunk band]. SCALE_DIST harness-calibrated (TODO#5).
#   6. GUARDRAILS: monotone quantiles (sort) + width-by-age sanity vs the empirical table (TODO#2).
import sys; sys.path.insert(0,'/home/claude/rl_after')
import os; os.environ.setdefault('RL_GAMMA','0.85'); os.environ.setdefault('RL_PICK1','3000')
import io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()): import rl_model as MA
from sklearn.ensemble import GradientBoostingRegressor

MA._v4_init()
SEASON=22
Q=[0.1,0.3,0.5,0.7,0.9]                 # quintile midpoints, 20% mass each
WQ=np.array([0.2,0.2,0.2,0.2,0.2])
ZQ=np.array([-1.2816,-0.5244,0.0,0.5244,1.2816])   # standard-normal quantiles for Q (prior band shape)
# Band core = the PROTOTYPE's GBR config (produced the bands Luke reviewed; HistGBR over-regularised elite medians).
HP=dict(n_estimators=300,max_depth=3,learning_rate=0.05,min_samples_leaf=40,random_state=0)

# ======================= SURFACED / CALIBRATED DIALS =======================
K_SHRINK   = 30.0      # #1 SURFACED CHOICE (Luke sets this watching the repriced output). Half-saturation in
                       #    COMPARABLE-DENSITY units: weight on the EMPIRICAL band = kcount/(kcount+K_SHRINK), rest on
                       #    the pedigree prior, where kcount = density of comparable training rows near the player.
                       #    Higher => trust pedigree longer where comparables are thin (lifts confirmed young top picks
                       #    like Willem); lower => trust the player's own form sooner everywhere. Stallers (common
                       #    archetype => high kcount) are weakly affected by K, so the dial mostly moves the rare young.
SCALE_DIST = 1.0       # #5 harness-calibrated global scale (conserve cohort total / >=90% retention).

# ======================= 1. TRAINING DATA (band target = forward best-3) =======================
def fwd_peak(p,Y,cap=None):
    fut=[x for x in p['scoring'] if x['year']>=Y and (cap is None or x['year']<=cap) and x['games']>=6]
    if not fut: return None
    w=np.array([min(x['games'],SEASON)/SEASON for x in fut]); a=np.array([x['avg'] for x in fut])
    idx=np.argsort(-a)[:3]; return float(np.average(a[idx],weights=w[idx]))
def career_best3(p,cap=None):
    a=sorted([x['avg'] for x in p['scoring'] if (cap is None or x['year']<=cap) and x['games']>=6],reverse=True)[:3]
    return float(np.mean(a)) if a else None

# CENSORING FIX (cont.24, Luke): a still-RISING young active has a TRUNCATED forward-best-3 (a lower bound, not the
# real peak) — feeding it in at full weight teaches "players like this top out low", dragging young projections down.
# EXCLUSION was tried and FAILED (hard gate -> survivorship, Clark 588->946; riser-only -> Clark 704, Mannagh<Clark,
# anchors +4%): dropping rows lurches the prior + breaks the validated calibration. DOWNWEIGHTING (Luke's suggestion)
# works instead — keep every row, but SOFTEN a censored riser's label in proportion to how far below peak age they
# are (youngest risers = least-observed peak = least weight). Soft => lifts young projections (Zane 358->444) WITHOUT
# moving the anchors or flipping Mannagh<Clark. is_censored_riser flags them; ref = cap year in the walk-forward.
CENSOR_DOWNWEIGHT=True
RISE_YEARS=4.0          # a censored riser RISE_YEARS below peak age -> weight floor; AT peak age -> weight 1.0.
RB_TAPER   = 0.55       # #SURFACED (Luke): recency taper on recent_best2. A best season STALE years ago is credited
                        #    RB_TAPER**stale, the rest reverting to current form (level_now). 1.0 = no taper (old);
                        #    lower = harsher on stale/un-backed-up peaks. Tames the board's recent_best2 inflation
                        #    (Sholl, rucks) while protecting fresh demonstrators (Mannagh). Set it watching the board.
def is_censored_riser(p,ref=None):
    ref=MA.BASE_REF if ref is None else ref
    g=MA.GRP[p['pos']]
    if MA._age_at(p,ref) > MA.PEAK_AGE[g]+1: return False          # past peak -> peak observed
    sea=[(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6 and x['year']<=ref]
    if not sea: return False
    last_yr=max(y for y,_ in sea)
    if last_yr <= ref-2: return False                              # inactive/delisted -> outcome observed (incl. busts)
    best=max(a for _,a in sea); latest=max(a for y,a in sea if y==last_yr)
    return latest >= best-1.0                                      # latest season is their best => still climbing => censored
def row_weight(p,ref=None):
    if not (CENSOR_DOWNWEIGHT and is_censored_riser(p,ref)): return 1.0
    g=MA.GRP[p['pos']]; a=MA._age_at(p,MA.BASE_REF if ref is None else ref)
    return float(np.clip((a-(MA.PEAK_AGE[g]-RISE_YEARS))/RISE_YEARS,0.2,1.0))

def build_training(pool,cap=None,exclude=None):
    """Returns X,y,META,W. META=[(ep,la,T)] per PER-YEAR row (for the local-count kernel). W = per-row sample weight
    (censoring downweight). cap/exclude support the walk-forward harness (target window cap, hold-out cohort)."""
    X,y,META,W=[],[],[],[]
    for p in pool:
        if exclude is not None and p.get('year')==exclude: continue
        w=row_weight(p,cap)
        d=career_best3(p,cap)
        if d is not None: X.append(MA._v4_draft_feat(p)); y.append(d); W.append(w)   # draft row (pedigree anchor), no META
        for Y in sorted(set(x['year'] for x in p['scoring'] if x['games']>0 and (cap is None or x['year']<=cap))):
            if any(x['year']>Y and (cap is None or x['year']<=cap) and x['games']>=6 for x in p['scoring']):
                t=fwd_peak(p,Y,cap)
                if t is not None:
                    f=MA._v4_feats(p,Y); X.append(f); y.append(t); W.append(w)
                    META.append((f[1],f[6],f[15]))   # ep, la(latest avg), T(tenure) — for the local-count kernel
    return np.array(X),np.array(y),np.array(META),np.array(W)

def fit_models(X,y,W=None):
    return {q:GradientBoostingRegressor(loss='quantile',alpha=q,**HP).fit(X,y,sample_weight=W) for q in Q}

# ======================= 3+4. PEDIGREE PRIOR (centre + width), TOP-OF-DRAFT TREND-EXTRAPOLATED =======================
def _loclin(xs,ys,k,W):
    pts=[(x,yv,(W+1-abs(x-k))) for x,yv in zip(xs,ys) if abs(x-k)<=W and yv==yv]
    if not pts: return float('nan')
    Wt=sum(w for *_,w in pts); xb=sum(w*x for x,_,w in pts)/Wt; yb=sum(w*yv for _,yv,w in pts)/Wt
    sxx=sum(w*(x-xb)**2 for x,_,w in pts)
    if sxx<1e-9: return yb
    b=sum(w*(x-xb)*(yv-yb) for x,yv,w in pts)/sxx
    return (yb-b*xb)+b*k

KMAX=70
def build_prior(pool,cap=None):
    """Per position: forward-peak CENTRE(pick) + WIDTH(pick) from career-best-3 over the historical pool.
    Top of the draft (picks 1-6) built by parametric a*k^-b extrapolation blended to local-linear by ~pick 12,
    so picks 1-4 anchor to where the trend HEADS, not where neighbour-averaging FLATTENS them (TODO#4)."""
    prior={}
    for g in set(MA.GRP.values()):
        pts=[(min(MA.effpk(p),KMAX),career_best3(p,cap)) for p in pool
             if MA.GRP.get(p['pos'])==g and (p.get('_ft') or p.get('pick')) and career_best3(p,cap) is not None]
        if len(pts)<25: prior[g]=None; continue
        ks=np.array([k for k,_ in pts]); vs=np.array([v for _,v in pts])
        # per-pick band stats (+-4 window) -> centre & width
        ctr_raw,wid_raw=[],[]
        for k in range(1,KMAX+1):
            m=np.abs(ks-k)<=4
            ctr_raw.append(float(np.mean(vs[m])) if m.sum()>=3 else float('nan'))
            wid_raw.append(float(np.std(vs[m]))  if m.sum()>=5 else float('nan'))
        kk=list(range(1,KMAX+1))
        ll_ctr=[_loclin(kk,ctr_raw,k,5) for k in kk]
        ll_wid=[_loclin(kk,wid_raw,k,7) for k in kk]
        # parametric power-decay top on the CENTRE: y=a*k^-b fit to picks 1-8 (log-log)
        kfit=np.arange(1,9); yfit=np.array([ctr_raw[i] for i in range(8)])
        ok=~np.isnan(yfit)
        if ok.sum()>=4:
            B,logA=np.polyfit(np.log(kfit[ok]),np.log(yfit[ok]),1); A=np.exp(logA); b=-B
            ctr=[]
            for i,k in enumerate(kk):
                par=A*k**(-b)
                if k<=6: ctr.append(par)
                elif k>=12: ctr.append(ll_ctr[i])
                else: w=(12-k)/6.0; ctr.append(w*par+(1-w)*ll_ctr[i])
        else:
            ctr=ll_ctr
        # enforce non-increasing centre (a deeper pick can't expect MORE)
        for i in range(1,len(ctr)):
            if ctr[i]>ctr[i-1]: ctr[i]=ctr[i-1]
        prior[g]=(np.array(ctr),np.array(ll_wid))
    return prior

def prior_band(p,prior):
    g=MA.gfut(p); pr=prior.get(g)
    if pr is None: return None
    ck=int(np.clip(MA.effpk(p),1,KMAX))-1
    c=pr[0][ck]; w=pr[1][ck]
    if not (w==w): w=np.nanmean(pr[1])
    return c+ZQ*w           # symmetric normal prior band at the Q quantiles

# ======================= 4(local-count) + SHRINKAGE =======================
# SHRINK each player's band toward the pedigree prior IN PROPORTION TO HOW THIN THE PLAYER'S OWN LOCAL DATA IS
# (spec#3). "Local data count" = COMPARABLE DENSITY: how many training rows sit near this player in feature space
# (pick, demonstrated level, tenure). This is the RIGHT thinness measure — it separates RARE archetypes (elite-young
# pick-1 = few comparables => lean prior => lift Willem) from COMMON ones (stalled high pick = MANY comparables =>
# trust the player's own collapsed data => discount Clark). own_games would conflate "few games" with "few
# comparables" and PROP a staller (the spec's "not-playing protects pedigree" failure). Pick enters ONLY through
# the prior's LEVEL, never the weight => a pick-1 and a pick-13 with equally-thin LOCAL data shrink equally (spec#3).
_SIG=np.array([6.0,8.0,1.0])    # kernel bandwidths on (ep, demonstrated level, tenure T). level is the key discriminator.
def comparable_density(p,META):
    if len(META)==0: return 0.0
    f=MA._v4_feats(p,MA.BASE_REF); v=np.array([f[1],f[6],f[15]])
    d=(META-v)/_SIG
    return float(np.sum(np.exp(-0.5*np.sum(d*d,axis=1))))
def own_games(p):
    return sum(x['games'] for x in p['scoring'] if x['year']<=MA.BASE_REF and x['games']>0)
def evidence(p,META):
    # total "sample support" = the player's OWN accumulated games (direct evidence => narrows + de-priors a PROVEN
    # player regardless of how rare his archetype is, e.g. Sheezel/Bont) PLUS comparable density (indirect evidence
    # => de-priors a COMMON archetype like a stalled high pick, e.g. Clark). The prior dominates only when BOTH are
    # thin — a RARE archetype the player himself hasn't yet evidenced (Willem: T=1, elite-young). That is exactly the
    # cell the spec wants pedigree to carry (lift Willem) and no other.
    return own_games(p)+comparable_density(p,META)

def raw_band(p,models):
    f=MA._v4_feats(p,MA.BASE_REF)
    return np.sort(np.array([float(models[q].predict([f])[0]) for q in Q]))   # sort = monotone guardrail (TODO#2)

def shrunk_band(p,models,prior,META,k_shrink):
    rb=raw_band(p,models); pb=prior_band(p,prior)
    if pb is None: return rb,1.0
    n=evidence(p,META); w=n/(n+k_shrink)           # weight on EMPIRICAL band; (1-w) on pedigree prior. thin support => prior.
    return np.sort(w*rb+(1-w)*pb),w

# Empirical forward-MOVE by age (spec width table) — young players IMPROVE on their current level, old DECLINE.
_AGEMOVE=[(19,22.6),(22,10.7),(25,-0.7),(28,-10.6),(31,-21.1)]
def age_move(a):
    if a<=_AGEMOVE[0][0]: return _AGEMOVE[0][1]
    if a>=_AGEMOVE[-1][0]: return _AGEMOVE[-1][1]
    for i in range(len(_AGEMOVE)-1):
        a0,m0=_AGEMOVE[i]; a1,m1=_AGEMOVE[i+1]
        if a0<=a<=a1: return m0+(m1-m0)*(a-a0)/(a1-a0)
    return 0.0
def recent_best2(p,yrs=4):
    # RECENCY-TAPERED demonstrated ceiling (cont.24, Luke): best-2 qualifying seasons in the window, each credited
    # RB_TAPER**(years-since-it) with the remainder falling back to the player's CURRENT form (level_now). A peak this
    # year keeps full credit; a stale/un-backed-up one decays toward what he's doing NOW. Fixes the board's
    # recent_best2 inflation (Sholl's 2yr-stale 85 -> ~69; De Koning credited at his ~85 level not his peak 100),
    # while protecting fresh demonstrators (Mannagh's 84 was last year). RB_TAPER=1.0 recovers the old un-tapered behaviour.
    ln=MA.level_now(p)
    if ln is None: return 0.0
    cand=sorted([(x['year'],x['avg']) for x in p['scoring'] if x['games']>=7 and MA.BASE_REF-yrs<x['year']<=MA.BASE_REF],
                key=lambda t:-t[1])[:2]
    if not cand: return 0.0
    vals=[(RB_TAPER**(MA.BASE_REF-yr))*av+(1-RB_TAPER**(MA.BASE_REF-yr))*ln for yr,av in cand]
    return float(np.mean(vals))
def band_anchor(p):
    # The band CENTRE = the best forward-peak estimate, = MAX of three real signals each catching what the others miss:
    #  (1) peak_est  — v4's learned forward projection (dominates for stallers & proven players => they're untouched);
    #  (2) recent_best2 — RECENT demonstrated ceiling (best-2 of the last 3 full seasons), un-recency-weighted: credits
    #                  Mannagh's 84@23 in 2025 that level_now/peak_est discard. RECENT (not career) so it does NOT credit
    #                  an old player's distant peak (Bont's forward peak is his current level declining, not his best-ever);
    #  (3) level_now + age_move(age)*room — YOUTH improvement toward the ceiling, ATTENUATED by how much room remains
    #                  (room->0 near the position ceiling): lifts a confirmed young top pick well below the ceiling
    #                  (Willem 86 @ pick-1) onto the star track, but barely moves a young player already AT the ceiling
    #                  (Sheezel 114) — matching the empirical 'young-star (105+) moves only +5' fact.
    g=MA.gfut(p); a=MA.age(p); ln=MA.level_now(p)
    room=MA.clamp((MA.PEAK[g]+30-ln)/40.0,0.0,1.0)
    youth=ln+age_move(a)*room
    rb=recent_best2(p)         # recent demonstrated ceiling (un-discounted). NOTE: for a still-elite 30+ player whose
                               # recent best exceeds v4's regressed forward (e.g. Bont 127 vs peak_est 118) this prices
                               # ~+7% over value(); that is a SURFACED judgment call (credit recent level vs regressed
                               # decline). Discounting it by age tames Bont but also softens recent demonstrators a
                               # down-year removed (Mannagh 84@2025), whom Luke wants clearly above Bice/Clark — so it
                               # is left un-discounted. Toggle: subtract k*max(0,a-(PEAK_AGE+3)) here to pin 30+ to peak_est.
    return max(MA.peak_est(p),rb,youth)

def final_band(p,models,prior,META,k_shrink):
    """Shrunk band, then RELOCATED UP by max(0, band_anchor - median): the freehand quantile median regresses
    demonstrated-ceiling/young players below their real forward level; this lifts the whole band (centre + tails) to
    the anchor, reducing the over-pessimistic lower tail. Stallers/proven (anchor==peak_est==median) untouched.
    Valuing over the band's ACTUAL levels stays (gives stallers their upside-tail floor; ages old players down)."""
    band,w=shrunk_band(p,models,prior,META,k_shrink)
    delta=max(0.0,band_anchor(p)-float(np.median(band)))
    return band+delta,w

# ======================= 2(width sanity). EMPIRICAL WIDTH-BY-AGE TABLE (from spec) =======================
# forward-move SD by age bucket (the 'band should look like this' guardrail). young-star narrow, old-star wide.
WIDTH_REF={(18,20):16.8,(21,23):14.8,(24,26):12.2,(27,29):11.4,(30,99):13.8}
def ref_width(age):
    for (lo,hi),sd in WIDTH_REF.items():
        if lo<=age<=hi: return sd
    return 13.0

# ======================= v_at_peak (TODO#1 + #6) =======================
def v_at_peak(p,L,lens='bal'):
    """Value p AS IF forward-peak = L, through the production chain at the player's REAL age.
    Proven players: == value() at L=peak_est (production-dominated). Old players: declines (real age past peak)."""
    g=MA.gfut(p); g0=MA.bnow(p); cur=MA.level_now(p)
    prod=MA.val(MA.proj_from_peak(g,L,MA.age(p),cur,lens,g0=g0,fut=MA.futblend(p),pre_hc=p.get('_b2hc',0.0)))
    return max(prod,MA.prod_floor(p,lens))

# ======================= dist_value =======================
def dist_value(p,models,prior,META,k_shrink=None,scale=None,lens='bal'):
    if k_shrink is None: k_shrink=K_SHRINK
    if scale is None: scale=SCALE_DIST
    if MA.level_now(p) is None: return MA.value(p,lens)     # pre-debut / pedigree-only: keep existing pedigree path
    band,_=final_band(p,models,prior,META,k_shrink)
    ev=scale*float(np.dot(WQ,[v_at_peak(p,L,lens) for L in band]))
    if MA.brodie_sig(p): ev*=0.5
    return round(ev*MA.lens_tilt(p,lens))

# ======================= build (the live 2026 model) =======================
def build():
    pool=[p for p in MA.data if MA.GRP.get(p['pos'])]
    X,y,META,W=build_training(pool)
    models=fit_models(X,y,W); prior=build_prior(pool)
    return models,prior,META

def get(nm,pool=None):
    return (next((x for x in MA.players if x['player']==nm),None)
            or next((x for x in MA.data if x['player']==nm),None))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--k',type=float,default=K_SHRINK); ap.add_argument('--scale',type=float,default=SCALE_DIST)
    a=ap.parse_args()
    models,prior,META=build()
    AUDIT=['Willem Duursma','Jhye Clark','Zane Duursma','Shaun Mannagh','Riley Bice']
    ANCH=['Harry Sheezel','Nick Daicos','Marcus Bontempelli']
    print(f'K_SHRINK={a.k}  SCALE_DIST={a.scale}\n')
    print('%-19s %-7s %5s %5s  %-34s %5s %5s %5s'%('player','pos','age','cur','shrunk band (q10/30/50/70/90)','wEmp','val()','DIST'))
    for grp,names in [('AUDIT NAMES',AUDIT),('PROVEN ANCHORS',ANCH)]:
        print(f'--- {grp} ---')
        for nm in names:
            p=get(nm)
            if p is None: print(f'{nm:19s} (not found)'); continue
            if MA.level_now(p) is None: print(f'{nm:19s} (pre-debut / pedigree-only)  val()={MA.value(p)}'); continue
            band,w=final_band(p,models,prior,META,a.k); rb=raw_band(p,models)
            wid=band[-1]-band[0]; exp_w=2.56*ref_width(MA.age(p))   # q10->q90 span ~= 2.56*SD for a normal cohort
            dv=dist_value(p,models,prior,META,a.k,a.scale)
            # proven players LEGITIMATELY tighten below cohort width (we know what they are), so only flag gross outliers
            flag='' if 0.40*exp_w<=wid<=1.85*exp_w else ' [WIDTH?]'
            bstr='['+' '.join('%5.1f'%b for b in band)+']'
            print('%-19s %-7s %4d %4.0f  %-36s %4.2f %5d %5d%s'%(
                nm,MA.GRP[p['pos']],MA.age(p),MA.level_now(p),bstr,w,MA.value(p),dv,flag))
