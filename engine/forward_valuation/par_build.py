"""PAR estimator (U26-REDESIGN, step 1) — STANDALONE DIAGNOSTIC, nothing wired into the engine.

par(pos, pick, tenure) = level_pos(log-pick)  +  ramp_pos(tenure)     [additive; ramp(yr1)=0]
  - target = median recency-weighted level (_lvl_wt) among players ON THE PARK at that pos x tenure
  - "on the park" = games_at_tenure >= f * base_play_rate(pos,tenure)   (base-rate-relative, NOT flat >=6g)
  - level: local-LINEAR kernel regression over log(pick), tricube, bandwidth H_LOGPICK
  - ramp: fit SEPARATELY per position via additive backfitting (shares strength across both axes),
          then SHRUNK toward the global ramp via n/(n+k) for thin positions (RUC/KPP)
  - cohort: DRAFT 2003-2018 (locked Decision A)

Run: cd /home/claude/rl_after && PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RECENCY_DECAY=0.72 \
     python3 ../forward_valuation/par_build.py
"""
import sys, os, io, contextlib, collections
sys.path.insert(0, '/home/claude/rl_after')
os.environ.setdefault('RL_GAMMA','0.85'); os.environ.setdefault('RL_PICK1','3000')
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import rl_model as MA
import conditional_prior as CP   # reuse _lvl_wt / debutyr / _exposure (same recency machinery)

# ---- dials (surfaced) ----
H_LOGPICK  = float(os.environ.get('PAR_BW',    '0.40'))  # kernel bandwidth in log-pick units
MIN_GAMES  = float(os.environ.get('PAR_MING', '6'))     # par gate = flat >=6g at that tenure
SHRINK_K   = float(os.environ.get('PAR_K',     '30'))    # ramp shrinkage n/(n+k) toward global
TEN_MAX    = 6
DRAFT_LO, DRAFT_HI = 2003, 2018
GROUPS = ['MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC']
EVAL_PICKS = [1,3,5,8,12,20,30,45,60]

def draftyr(p): return CP.debutyr(p) - 1
def season_row(p, Y):
    for x in p['scoring']:
        if x['year'] == Y: return x
    return None

# ---- 1. gather on-park observations: (pos, logpick, tenure, lvl, games) -------------------
def gather():
    pool = [p for p in MA.data if MA.GRP.get(p.get('pos'))
            and (p.get('pick') or p.get('_ft')) and DRAFT_LO <= draftyr(p) <= DRAFT_HI]
    # raw rows first (need base_play_rate before applying the gate)
    raw = []  # (pos, pick, ten, Y, games, p)
    for p in pool:
        pos = MA.gfut(p); pk = min(MA.effpk(p), CP.KMAX); d0 = draftyr(p)
        for T in range(1, TEN_MAX+1):
            Y = d0 + T; r = season_row(p, Y); g = r['games'] if r else 0
            if g > 0:
                raw.append((pos, pk, T, Y, g, p))
    # base play rate = median games among players who PLAYED (g>0) at that pos x tenure
    base = {}
    bycell = collections.defaultdict(list)
    for pos, pk, T, Y, g, p in raw: bycell[(pos,T)].append(g)
    for k,v in bycell.items(): base[k] = float(np.median(v))
    # apply the base-rate-relative gate -> on-park observations, target = _lvl_wt
    obs = []  # (pos, logpick, T, lvl)
    for pos, pk, T, Y, g, p in raw:
        if g >= MIN_GAMES:                       # par gate = flat >=6g at that tenure (Luke)
            obs.append((pos, np.log(pk), T, CP._lvl_wt(p, Y)))
    return obs, base, raw

# ---- 2. local-linear kernel regression over log-pick --------------------------------------
def tricube(u):
    u = np.abs(u); w = (1 - u**3)**3; w[u >= 1] = 0.0; return w
def loclin(x0, xs, ys, h):
    """local-linear fit at x0; returns (yhat, ESS=(sum w)^2/sum w^2)."""
    w = tricube((xs - x0)/h)
    if w.sum() <= 0: return float('nan'), 0.0
    W = np.diag(w); Xd = np.column_stack([np.ones_like(xs), xs - x0])
    try:
        beta = np.linalg.solve(Xd.T@W@Xd, Xd.T@W@ys); yhat = float(beta[0])
    except np.linalg.LinAlgError:
        yhat = float(np.sum(w*ys)/np.sum(w))
    ess = float((w.sum()**2)/np.sum(w**2))
    return yhat, ess

# ---- 3. additive backfitting: level_pos(logpick) + ramp_pos(T) ----------------------------
def fit():
    obs, base, raw = gather()
    POS = {g: np.array([(x,T,lv) for (pos,x,T,lv) in obs if pos==g], dtype=float) for g in GROUPS}
    ramp = {g: np.zeros(TEN_MAX+1) for g in GROUPS}     # ramp[g][T], index 0 unused
    # iterate
    for _ in range(4):
        # (a) level fit on tenure-detrended values, per position
        levelfn = {}
        for g in GROUPS:
            A = POS[g]
            if len(A) < 4: levelfn[g] = None; continue
            xs, Ts, lv = A[:,0], A[:,1].astype(int), A[:,2]
            detr = lv - np.array([ramp[g][t] for t in Ts])
            levelfn[g] = (xs.copy(), detr.copy())
        # (b) ramp = median pick-detrended resid by tenure, anchored ramp(1)=0
        for g in GROUPS:
            A = POS[g]
            if levelfn[g] is None: continue
            xs, Ts, lv = A[:,0], A[:,1].astype(int), A[:,2]
            lx, ldetr = levelfn[g]
            lvlhat = np.array([loclin(x, lx, ldetr, H_LOGPICK)[0] for x in xs])
            resid = lv - lvlhat
            r = np.zeros(TEN_MAX+1)
            for T in range(1, TEN_MAX+1):
                m = (Ts==T)
                r[T] = float(np.median(resid[m])) if m.sum()>0 else (r[T-1] if T>1 else 0.0)
            r = r - r[1]                                  # anchor yr1 = 0
            ramp[g] = r
    # global ramp (pooled across positions, sample-weighted by cell counts)
    allresid_byT = collections.defaultdict(list)
    n_by_pos = {}
    for g in GROUPS:
        A = POS[g]; n_by_pos[g] = len(A)
        if levelfn[g] is None: continue
        xs, Ts, lv = A[:,0], A[:,1].astype(int), A[:,2]
        lx, ldetr = levelfn[g]
        lvlhat = np.array([loclin(x, lx, ldetr, H_LOGPICK)[0] for x in xs])
        resid = lv - lvlhat
        for T,rv in zip(Ts, resid): allresid_byT[T].append(rv)
    gramp = np.zeros(TEN_MAX+1)
    for T in range(1, TEN_MAX+1):
        gramp[T] = float(np.median(allresid_byT[T])) if allresid_byT[T] else 0.0
    gramp = gramp - gramp[1]
    # shrink each position's ramp toward global
    ramp_shr = {}; sw = {}
    for g in GROUPS:                              # UN-POOLED per Luke: enough per-position data; level kernel-ESS carries thin cells
        ramp_shr[g] = ramp[g].copy(); sw[g] = 1.0
    # ---- MONOTONICITY PRIOR (Decision-D class), weighted isotonic on BOTH axes ----
    # (a) level NON-INCREASING in pick (better pick -> par >= worse pick); weights = kernel ESS
    PKGRID = list(range(1, int(CP.KMAX)+1))
    level_grid = {}
    for g in GROUPS:
        lf = levelfn[g]
        if lf is None: level_grid[g] = None; continue
        raw = [loclin(np.log(pk), lf[0], lf[1], H_LOGPICK) for pk in PKGRID]
        ys = np.array([r[0] for r in raw]); es = np.array([max(r[1],0.5) for r in raw])
        ok = np.isfinite(ys)                               # nan-fill empty cells (e.g. RUC pk3) before isotonic
        if ok.any() and not ok.all():
            ys = np.interp(np.arange(len(ys)), np.where(ok)[0], ys[ok])
        ys_mono = _pava(ys, es, increasing=False)          # non-increasing in pick
        level_grid[g] = (np.array(PKGRID, float), ys_mono, es)
    # (b) ramp NON-DECREASING in tenure (development monotone); weights = per-tenure obs count
    for g in GROUPS:
        cnt = np.array([1.0]+[float((POS[g][:,1].astype(int)==T).sum()) for T in range(1,TEN_MAX+1)])
        r = ramp_shr[g].copy()
        r[1:] = _pava(r[1:TEN_MAX+1], cnt[1:TEN_MAX+1], increasing=True)
        ramp_shr[g] = r - r[1]                              # re-anchor yr1 = 0
    return dict(obs=obs, base=base, POS=POS, levelfn=levelfn, ramp=ramp, gramp=gramp,
                ramp_shr=ramp_shr, sw=sw, n_by_pos=n_by_pos, level_grid=level_grid)

def _pava(y, w, increasing=True):
    """weighted pool-adjacent-violators. increasing=True -> non-decreasing; False -> non-increasing."""
    blocks=[]                                              # [value, weight, count]
    for yi,wi in zip(y,w):
        blocks.append([float(yi), max(float(wi),1e-6), 1])
        while len(blocks)>1 and ((blocks[-2][0]>blocks[-1][0]) if increasing else (blocks[-2][0]<blocks[-1][0])):
            v2,w2,c2=blocks.pop(); v1,w1,c1=blocks.pop()
            blocks.append([(v1*w1+v2*w2)/(w1+w2), w1+w2, c1+c2])
    out=[]
    for v,wt,c in blocks: out += [v]*c
    return np.array(out)

def level_at(F, g, pick):
    grid = F.get('level_grid',{}).get(g) if isinstance(F.get('level_grid',{}),dict) else None
    if grid is not None:
        xs,ys,es = grid; pk=min(max(pick,1),70)
        return float(np.interp(pk, xs, ys)), float(np.interp(pk, xs, es))
    lf = F['levelfn'][g]
    if lf is None: return float('nan'), 0.0
    return loclin(np.log(pick), lf[0], lf[1], H_LOGPICK)

def par_at(F, g, pick, T):
    lv,_ = level_at(F, g, pick); return lv + F['ramp_shr'][g][T]

# ============================ REPORT ============================
if __name__ == '__main__':
    F = fit()
    print(f"PAR estimator — cohort DRAFT {DRAFT_LO}-{DRAFT_HI} | additive (par=level+ramp, ramp[yr1]=0)")
    print(f"dials: bandwidth(log-pick)={H_LOGPICK}  par gate>={MIN_GAMES:.0f}g  ramps UN-POOLED (thin-cell protection in level kernel-ESS)")

    print("\n=== A. base play rate (median games among players who played) — pos x tenure ===")
    print("  pos        " + "".join(f"  yr{T}" for T in range(1,TEN_MAX+1)))
    for g in GROUPS:
        print(f"  {g:9s} " + "".join(f"  {F['base'].get((g,T),0):4.0f}" for T in range(1,TEN_MAX+1)))

    print("\n=== B. on-park sample (resolution map) — #players per pos x tenure ===")
    cnt = collections.defaultdict(int)
    for pos,x,T,lv in F['obs']: cnt[(pos,int(T))]+=1
    print("  pos        " + "".join(f"  yr{T}" for T in range(1,TEN_MAX+1)) + "   TOTAL")
    for g in GROUPS:
        tot = F['n_by_pos'][g]
        print(f"  {g:9s} " + "".join(f"  {cnt[(g,T)]:4d}" for T in range(1,TEN_MAX+1)) + f"   {tot:5d}")

    print("\n=== C. level_pos(log-pick) curve + kernel ESS at each eval point ===")
    print("  pos        " + "".join(f"  pk{p:<2d}" for p in EVAL_PICKS))
    for g in GROUPS:
        row=[]; 
        for pk in EVAL_PICKS:
            lv,ess = level_at(F,g,pk); row.append((lv,ess))
        print(f"  {g:9s} " + "".join(f" {lv:5.1f}" for lv,_ in row))
        print(f"   (ESS)    " + "".join(f" {ess:5.1f}" for _,ess in row))

    print(f"\n=== D. tenure ramp per position — RAW vs GLOBAL vs SHRUNK (n/(n+{SHRINK_K:.0f})) ===")
    print("  global ramp:        " + "".join(f"  yr{T}:{F['gramp'][T]:+5.1f}" for T in range(1,TEN_MAX+1)))
    for g in GROUPS:
        n=F['n_by_pos'][g]; w=F['sw'][g]
        raw_s  = "".join(f" {F['ramp'][g][T]:+5.1f}" for T in range(1,TEN_MAX+1))
        shr_s  = "".join(f" {F['ramp_shr'][g][T]:+5.1f}" for T in range(1,TEN_MAX+1))
        flag = "  <-- POOLED (thin)" if w < 0.8 else ""
        print(f"  {g:9s} n={n:4d} w={w:.2f}")
        print(f"     raw   {raw_s}")
        print(f"     shrunk{shr_s}   (yr1->yr5 delta = {F['ramp_shr'][g][5]-F['ramp_shr'][g][1]:+.1f}){flag}")

    print("\n=== E. assembled par(pos,pick,tenure) — sample cells ===")
    print("  pos        pk |  yr1   yr2   yr3   yr4   yr5")
    for g,pk in [('MID',7),('MID',1),('GEN_DEF',14),('KEY_DEF',8),('KEY_FWD',4),('RUC',20),('GEN_FWD',12)]:
        print(f"  {g:9s} {pk:2d} | " + " ".join(f"{par_at(F,g,pk,T):5.1f}" for T in range(1,6)))

    print("\n=== F. ANCHOR RECONCILIATION — MID yr1, picks 1-8 should ~= 66 (cont.26 §2) ===")
    lv18 = np.mean([level_at(F,'MID',pk)[0] for pk in range(1,9)])
    print(f"  mean level_MID(yr1) over picks 1-8 = {lv18:.1f}   (cont.26 empirical par = 66.0)")
    print(f"  level_MID(yr1) @pk7 = {level_at(F,'MID',7)[0]:.1f}   (Cumming's pick; cont.26 break-even@20g = 66)")
