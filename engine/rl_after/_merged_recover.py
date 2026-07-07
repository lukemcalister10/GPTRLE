"""WIRE (1) delist->~0 (2) staleness floor all-stalled (3) isotonic pick guard INTO the engine. Prove on named players."""
import os,io,contextlib,copy,numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
with contextlib.redirect_stdout(io.StringIO()):
    import rl_model as MA, wire_redesign as W; cm=W.build()
TR=W.TR; rd=TR.rd; cp=TR.cp; dp=TR.dp; PR=W.PR
era={}
for Y in range(2009,2026):
    a=[s['avg'] for p in MA.data for s in p.get('scoring') or [] if s['year']==Y and s['games']>=6]
    if a: era[Y]=float(np.mean(a))
REF=float(np.mean(list(era.values())))
pool=[p for p in MA.data if MA.GRP.get(p['pos'])]
X,yy=[],[]
for p in pool:
    if cp.debutyr(p)>2021 or not (p.get('pick') or p.get('_ft')): continue
    d0=cp.debutyr(p)-1; last=max([x['year'] for x in p['scoring']]+[d0])
    for Y in range(d0,min(last,2026)+1): X.append(cp._feat(p,Y)); yy.append(cp.fwd_best3_from(p,Y,2026))
q97m=GradientBoostingRegressor(loss='quantile',alpha=0.97,n_estimators=200,max_depth=4,learning_rate=0.05,min_samples_leaf=25,random_state=0).fit(np.array(X),np.array(yy))
WQ6=np.array([0.18]*5+[0.10]); WQ6/=WQ6.sum(); RECX=[0.30,0.52,0.67,0.82,0.97,1.30]; RECY=[0.54,0.64,0.84,1.00,1.00,1.00]
midpos=next(r['pos'] for r in MA.data if MA.GRP.get(r.get('pos'))=='MID'); GRPPOS={}
for r in MA.data:
    g=MA.GRP.get(r.get('pos'))
    if g and g not in GRPPOS: GRPPOS[g]=r['pos']
# ===== STEP1 #1-FAMILY FIX (inference-only; band pickle + q97m above trained on ORIGINAL features -> Delta=0 for proven-flat) =====
PROVEN_N=4; POLE_RAMP=22.0    # PROVEN_N surface NOT wired (no committed exec spec) -> scalar 4 + c=n/4 retained; see CHANGELOG 2026-06-30
# ==== GAMES-RAMP PRORATION (D10 03/07/2026 — Luke's design statement, verbatim in the directive):
# every games bar (6/10/14/22) prorates to season progress for the IN-PROGRESS season — a player is
# judged only against games that were playable (R14/24 -> fE=0.58 at this cut; RL_M3_FE = the M2/M3
# season-progress convention, one dial). Completed seasons are byte-identical (fE=1). G_ADQ (12, M1
# proven-player recent-adequacy window) deliberately NOT prorated — outside the 6/10/14/22 enumeration.
SEASON_FE=float(os.environ.get('RL_M3_FE','0.58'))
INPROG_Y=int(os.environ.get('RL_M3_INPROG_Y','2026'))
def _fEy(Y): return SEASON_FE if Y==INPROG_Y else 1.0
def _playable(p,Y):                                           # full-season-equivalent games playable since debut
    return cp.SEASON*(max(0,Y-cp.debutyr(p))+(_fEy(Y) if Y>=cp.debutyr(p) else 0.0))
# STEP-3 CALIBRATION WIRED 2026-06-30 (candidate): per-group LDECAY + FLAT_TOL (KEY / GEN / MID+RUC)
def _ldg(pos): return 'KEY' if pos in ('KEY_FWD','KEY_DEF') else ('GEN' if pos in ('GEN_FWD','GEN_DEF') else 'MR')
LDECAY_G={'KEY':0.40,'GEN':0.35,'MR':0.225}; FLAT_TOL_G={'KEY':10.3,'GEN':12.0,'MR':14.0}
# DECLINER SHED 2026-06-30 (candidate): DERIVED from realised forward output of established decliners (drop>3).
#   recovery~0 beyond ~3 SC drop (forward stays at declined current); age accelerates forward BELOW current.
#   _AGEMULT = measured smoothed forward/current by age (washout-incl); DOWN_TOL = wobble band (recovery noisy <3).
_AGEMULT_X=[20,22,25,28,30,32,34,37]; _AGEMULT_Y=[0.92,0.89,0.85,0.79,0.73,0.68,0.62,0.55]
def _agemult(a): return float(np.clip(np.interp(a,_AGEMULT_X,_AGEMULT_Y),0.53,0.95)) if a is not None else 0.85
DOWN_TOL=3.0   # down-side hold band (data: recovery~0 beyond ~3); ASYMMETRIC vs up-side FLAT_TOL (10-14)
cp._lvl_eff_orig=cp._lvl_eff
def _nqual(p,Y): return sum(1 for x in p['scoring'] if x['games']>=10 and x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
# D10 SCOPE NOTE (declared): the 10-bar prorates for the FIRST qualifying season only (delivered
# fractionally + smoothly via the f1 credit in _coreM1 below — the games-ramp/rookie family, the
# directive's evidence base, DIAG-B CF4). A board-wide prorated 10-bar was measured this session and
# REJECTED: it discontinuously re-prices Luke-ruled anchors outside the games-ramp channel (Tsatas
# accept-and-track 1140 -> 2080 breaking A8; O'Driscoll -525, Cadman -253 via mid-season proven flips).
# Extending the proration to multi-season nqual increments needs a Luke ruling; the pre-existing
# full-10-bar step for those players stands (known seam class, h-M3-blend-seam-noise register).
def _lvlcurr(p,Y):                                            # steeper-recency CURRENT level (trend-aware; ==career avg for a flat player)
    ld=LDECAY_G[_ldg(MA.gfut(p))]                             # STEP-3 per-group recency decay
    rows=[(x['year'],x['games'],x['avg']) for x in p['scoring'] if x['games']>0 and (cp.debutyr(p)-1)<x['year']<=Y]
    tw=sum(gm*ld**max(0,Y-yr) for yr,gm,_ in rows)
    return float(sum(gm*ld**max(0,Y-yr)*a for yr,gm,a in rows)/tw) if tw>0 else 0.0
def _par_prior(p,Y): return PR.par_at(MA.gfut(p),min(MA.effpk(p),cp.KMAX),min(max(PR.tenure(p,Y),1),6))
def eff_ten(p,Y,base):                                        # developmental tenure off a CONTEXT base; proven keeps base exactly
    if _nqual(p,Y)>=PROVEN_N: return base                     # proven: original tenure (each call site passes its own base)
    return max(base, cp._age_asof(p,Y)-18)                    # thin career: max(base, age-18); 18-19yo debut -> ==base (Delta=0)
def _lvl_eff_core(p,Y):
    L_old=cp._lvl_eff_orig(p,Y); n=_nqual(p,Y)
    if n==0: return L_old                                     # cameo/never-played: original (pole gate handles never-played)
    Lc=_lvlcurr(p,Y)
    if n>=PROVEN_N:                                           # ESTABLISHED -> asymmetric: hold UP, SHED DOWN to realised forward
        ft=FLAT_TOL_G[_ldg(MA.gfut(p))]
        if Lc>=L_old: return L_old if (Lc-L_old)<=ft else Lc  # UP-side: hold (don't over-credit a wobble/one strong yr)
        drop=L_old-Lc
        if drop<=DOWN_TOL: return L_old                        # down-wobble (<=3): hold steady
        sw=float(np.clip((drop-DOWN_TOL)/5.0,0.0,1.0))        # smooth shed onset over drop 3->8 (no hard boundary)
        Lsh=Lc*_agemult(cp._age_asof(p,Y))                    # DECLINER SHED: realised forward level (current, age-accelerated below)
        return (1.0-sw)*L_old+sw*Lsh
    c=n/PROVEN_N; return c*Lc+(1-c)*_par_prior(p,Y)           # career-thin (1..3 seasons) -> shrink current toward pedigree par
# UPSIDE FADE 2026-06-30 (GENTLER, candidate): elapsed-opportunity-gated fade of the pedigree/upside credit toward the
#   floor at demonstrated production. Credit target = realised forward ceiling surface E[fwdPeak](dL=ceiling-bar, year N),
#   kernel-smoothed from data. Keys on years-since-draft x exposure (NOT nq); young yr1-2 + first-yrs untouched (eo=0);
#   rising/at-production players unaffected (T=L0). Only ever pulls DOWN. See UNEARNED_UPSIDE_SCOPE_2026-06-30.md.
_UP_DLX=[-30.0,-20.0,-10.0,0.0,10.0]; _UP_NY=[3.0,4.0,5.0,6.0]
_UP_S=[[34.,45.,56.,67.,76.],[22.,33.,46.,59.,71.],[12.,22.,36.,51.,65.],[6.,14.,28.,44.,59.]]
def _upS(dL,N):
    dL=float(np.clip(dL,-30,10)); N=float(np.clip(N,3,6))
    col=[float(np.interp(dL,_UP_DLX,row)) for row in _UP_S]
    return float(np.interp(N,_UP_NY,col))
def _eo(p,Y):                                                 # elapsed-opportunity weight = years-since-draft x exposure (NOT nq)
    d=cp.debutyr(p); N=Y-d+1
    yrw=float(np.clip((N-2)/4.0,0.0,1.0))                     # 0 at yr<=2 (young/first-yrs untouched) -> 1 by yr6
    gm=sum(x.get('games',0) for x in p['scoring'] if (d-1)<x['year']<=Y)
    exp=float(np.clip(gm/(14.0*max(N-1,1)),0.0,1.0))         # fraction of ~14-game/yr opportunity actually taken
    return yrw*exp
def _lvl_eff_infer(p,Y):
    L0=_lvl_eff_core(p,Y); eo=_eo(p,Y)
    if eo<=0.0: return L0
    avs=[x['avg'] for x in p['scoring'] if x.get('games',0)>=6 and (cp.debutyr(p)-1)<x['year']<=Y]
    if not avs: return L0
    bar=MA.REPL.get(MA.gfut(p),0.0)-3.0; N=Y-cp.debutyr(p)+1
    T=min(L0, max(_upS(max(avs)-bar,N), _lvlcurr(p,Y)))       # GENTLER: floor at demonstrated production; keep realised upside
    return (1.0-eo)*L0+eo*T
def _feat_infer(p,Y):
    oh=[0.0]*len(cp.GROUPS); oh[cp.GIDX[MA.gfut(p)]]=1.0
    ep=min(MA.effpk(p),cp.KMAX); age=cp._age_asof(p,Y)
    ten=eff_ten(p,Y, max(0,Y-(cp.debutyr(p)-1)))             # base = original _feat tenure
    return oh+[np.log(ep), cp._exposure(p,Y), ten, cp._lvl_eff(p,Y), age]
# (inference rebind deferred to AFTER the isotonic guard builds on ORIGINAL features -> proven-flat stays Delta=0)
def b6(p,Y=2026):
    MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
    with contextlib.redirect_stdout(io.StringIO()): b=np.asarray(cp.cond_prior_band(p,cm,Y))
    return np.append(b,max(float(q97m.predict(np.array([cp._feat(p,Y)]))[0]),b[4]))
def price6(p,bb,Y=2026):
    sav=dict(MA.REPL)
    try:
        for g in MA.REPL: MA.REPL[g]=sav[g]-rd.REPL_DROP.get(g,0)
        MA.BASE_REF=MA.AGE_REF=Y; MA._pe_clear()
        with contextlib.redirect_stdout(io.StringIO()): return float(dp.SCALE_DIST*np.dot(WQ6,[dp.v_at_peak(p,float(L),'bal') for L in bb]))
    finally: MA.REPL.update(sav)
def recover(perf,par): return float(np.clip(np.interp(perf/max(1.0,par),RECX,RECY),0,1))
def synth(pk,avg,pos,nyr=2): return {'player':'s','pos':GRPPOS.get(pos,midpos),'pick':float(pk),'year':2023,'dob':'2005-03-01','type':'ND','scoring':[{'year':2024+i,'games':18,'avg':float(avg)} for i in range(nyr)],'_pos_now':None,'_futpos':None}   # DPP STRIP: single-position synth (gfut falls back to bnow=pos)
_POLE={}
def par_pole(pos,pk,T):
    k=(pos,int(min(pk,cp.KMAX)),int(min(max(T,1),6)))
    if k not in _POLE: sp=synth(k[1],PR.par_at(*k),pos); _POLE[k]=price6(sp,b6(sp))
    _SCALE={'MID':1.19,'GEN_FWD':0.93,'KEY_FWD':0.95,'GEN_DEF':1.08,'KEY_DEF':1.05,'RUC':1.13}  # STEP3-B: principled re-level (trajectory-integrated pole / 2yr synth); piece-2 SHAPE kept, LEVEL rescaled
    return _POLE[k]*_SCALE.get(pos,1.0),PR.par_at(*k)
def raw_ev(p,Y=2026):
    pr=price6(p,b6(p,Y),Y); pos=MA.gfut(p); pk=MA.effpk(p); T=min(max(PR.tenure(p,Y),1),6)
    et=min(max(eff_ten(p,Y, PR.tenure(p,Y)),1),6)                                     # STEP1: developmental tenure off original PR.tenure base
    po,par=par_pole(pos,pk,T); a=MA.age(p)
    wage=0.0 if pos=='RUC' else float(np.clip(1-((a or 21)-20)/6,0,1))
    tfade=float(np.interp(et,[1,2,3,4,5,6],[1.00,0.76,0.40,0.16,0.05,0.05]))          # pole-fade by DEVELOPMENTAL tenure
    expgate=1.0 if _nqual(p,Y)>=PROVEN_N else min(1.0, cp._exposure(p,Y)/max(1e-9,POLE_RAMP*min(1.0,_playable(p,Y)/cp.SEASON)))   # STEP1 gate, D10: 22-bar can't exceed playable games (yr-1 mid-season 22->12.8)
    w=wage*tfade*expgate
    perf=cp._lvl_wt(p,Y)                                  # WEIGHTED games x recency level (RL_RECENCY_DECAY), not flat best-3
    return pr+w*recover(perf,par)*max(0.0,po-pr)
# ===== (3) ISOTONIC PICK GUARD: per pos, monotone non-increasing in pick at par; correction factor =====
PICKS=list(range(1,71)); ISO={}
for pos in ['MID','GEN_FWD','KEY_FWD','GEN_DEF','KEY_DEF','RUC']:
    raw=np.array([raw_ev(synth(pk,PR.par_at(pos,min(pk,cp.KMAX),4),pos)) for pk in PICKS])
    iso=IsotonicRegression(increasing=False).fit_transform(PICKS,raw)        # monotone non-increasing in pick#
    ISO[pos]=(np.array(PICKS),np.maximum(iso,raw*0)+ (iso-raw>=0)*(iso-raw))  # iso is the guarded floor; correction additive where iso>raw
    ISO[pos]=(np.array(PICKS), iso/np.maximum(raw,1e-6))                       # multiplicative correction (>=1 where shallow under-priced)
def iso_corr(pos,pk): xs,fs=ISO[pos]; return float(np.interp(min(pk,70),xs,fs))
for _pp in ['MID','GEN_FWD','KEY_FWD','GEN_DEF','KEY_DEF','RUC']:   # STEP1: FREEZE pole table on ORIGINAL features
    for _pk in range(1,int(cp.KMAX)+1):                            #   (pole = pick-side; untouched until step 2-4)
        for _T in range(1,7): par_pole(_pp,_pk,_T)
# ==== M1 + v7-asc (BAKE CANDIDATE v2, D7 02/07/2026 — Luke-ruled config; NOT baked until Luke's bake word) ====
# M1 transplanted VERBATIM from the verified matrix-builder prototype (s4_matrix_M1v7.py; read-pass pack
# session_2026-07-02/readpass_pack_M1v7_8aed420a.md). M1 refines ONLY the up-branch of the level core:
# a proven player earns S_M1 of a current-over-recency gap when the gap >= TOL_M1 AND a recent season
# (within WIN yrs, >= G_ADQ games) sits above the recency level; the down-branch (DOWN_TOL shed) and the
# thin-career par-prior blend are byte-identical to _lvl_eff_core. v7 age-scales the q97 tail (asc) —
# REAL store players only: the ISO/pole tables above are frozen on ORIGINAL features/bands, and gate
# synths (B6 ramp) keep the original band.
# v7-cB DELETED 02/07/2026 (Luke-ruled, D7 — deleted, not disabled): the upper-quantile band compression
# cB = 0.47*clip((effs-1)/3,0,1) on bb[3]/bb[4] is GONE, with its _effs feed (no other consumer).
# Rationale: indiscriminate markdown (2020-cohort Spearman(value,delta) = -0.024, p=0.87 — no quality
# signal), the Curtis squeezer (Curtis -195/-14.4%, Ward -324/-19.6% — D5 term table). Obituary:
# BOARD_LAYERS_OBITUARY.md (ENGINE-TERM DELETIONS). Resurrection ref:
#   git show 0806d90:engine/rl_after/_merged_recover.py   (the D4 candidate, the last commit carrying cB)
TOL_M1=5.0; G_ADQ=12; WIN=2; S_M1=0.46
def _radq(p,Y,Lo): return any(x['games']>=G_ADQ and x['avg']>Lo for x in p['scoring'] if Y-WIN<x['year']<=Y and (cp.debutyr(p)-1)<x['year'])
def _coreM1(p,Y):
    Lo=cp._lvl_eff_orig(p,Y); n=_nqual(p,Y)
    if n==0:
        # D10: the first qualifying season FORMING in progress earns fractional credit (kills the hard
        # n 0->1 level flip). SCOPE (declared): FIRST-EVIDENCE players only — all evidence is the
        # in-progress season. Multi-year n==0 careers (e.g. Tsatas: 4 list-years, no 10-game season)
        # keep the exposure-shrunk Lo path: injecting the 75%-par-prior n=1 asymptote mid-career was
        # measured this session at +940 on the Luke-ruled Tsatas anchor (A8 break) and REJECTED.
        if Y!=INPROG_Y or any(x['games']>0 and x['year']<Y and (cp.debutyr(p)-1)<x['year'] for x in p['scoring']): return Lo
        gy=sum(x['games'] for x in p['scoring'] if x['year']==Y and (cp.debutyr(p)-1)<x['year'])
        f1=min(1.0, gy/max(1e-9,10.0*SEASON_FE))
        if f1<=0.0: return Lo
        return (1.0-f1)*Lo + f1*((1.0/PROVEN_N)*_lvlcurr(p,Y)+(1.0-1.0/PROVEN_N)*_par_prior(p,Y))
    Lc=_lvlcurr(p,Y)
    if n>=PROVEN_N:
        if Lc>=Lo: return (Lo+S_M1*(Lc-Lo)) if ((Lc-Lo)>=TOL_M1 and _radq(p,Y,Lo)) else Lo
        drop=Lo-Lc
        if drop<=DOWN_TOL: return Lo
        sw=float(np.clip((drop-DOWN_TOL)/5,0,1)); return (1-sw)*Lo+sw*Lc*_agemult(cp._age_asof(p,Y))
    c=n/PROVEN_N; return c*Lc+(1-c)*_par_prior(p,Y)
def _inferM1(p,Y):
    L0=_coreM1(p,Y); eo=_eo(p,Y)
    if eo<=0: return L0
    avs=[x['avg'] for x in p['scoring'] if x.get('games',0)>=6 and (cp.debutyr(p)-1)<x['year']<=Y]
    if not avs: return L0
    bar=MA.REPL.get(MA.gfut(p),0.0)-3.0; N=Y-cp.debutyr(p)+1
    return (1-eo)*L0+eo*min(L0,max(_upS(max(avs)-bar,N),_lvlcurr(p,Y)))
def _v7(bb,p,Y):
    bb=list(bb); m=bb[2]; a=cp._age_asof(p,Y)
    asc=float(np.interp(a,[20,22,24,27],[1.0,0.76,0.58,0.40]))
    bb[5]=m+asc*(bb[5]-m); return bb
# STABLE-KEY REAL-membership (F1 fix 2026-07-05, Luke one-source rewire). The _REAL gate decides which players
# receive the engine's real-store layers (RUC prior cap :317/:492, v7 age-taper :198, B5 floor :552). It is now
# keyed on the STABLE player key, NOT id(p) -- so the layers fire regardless of which module instance or object
# copy is priced. (The shipped-board bug: rl_export exec'd a 2nd rl_model instance, so id(p) matched 0/805 and
# every real-store layer was silently dropped, over-pricing ~2/3 of the board.) Synths (no 'key') never match;
# copies carrying the same key resolve as real by construction. Keys verified non-null + unique across MA.data.
_REAL=set(p['key'] for p in MA.data)
def _isreal(p): return p.get('key') in _REAL
_b6_pre_v7=b6
def b6(p,Y=2026):
    bb=_b6_pre_v7(p,Y)
    if _isreal(p):
        try: return _v7(bb,p,Y)
        except Exception: return bb
    return bb
cp._lvl_eff=_inferM1; cp._feat=_feat_infer   # M1 level bind (was _lvl_eff_infer) + STEP1 inference feature path (q97m + ISO + POLE above used ORIGINAL features)
# ==== M3 CLOCK-PIN PLUMBING (BAKE CANDIDATE v2, D7 02/07/2026 — design: session_2026-07-02/
# m3_design_proportional_tenure.md; the D4 backtest's monkeypatch hook inventory made first-class).
# While _M3PIN is on (ONLY inside _ev_m3's pinned evaluation of the in-progress season), the age/tenure
# CLOCK surfaces read as Y-1: cp._age_asof -1yr · MA.age -1yr · PR.tenure -1yr (floor 1) · _eo's
# years-since-draft N-1 (data window untouched) · _feat's explicit ten term re-based to Y-1. Evidence
# windows, era adjust, nseas/nqual and the M2-prorated exposure clock ALL stay at Y — the pin moves the
# CLOCKS only (using plain ev(p,Y-1) would re-prorate the decay channel M2 already prorates). With the
# pin OFF every wrapper is an identity passthrough — byte-exact by construction (verified in the D7 cut).
_M3PIN={'on':False}
M3_INPROG_Y=int(os.environ.get('RL_M3_INPROG_Y','2026'))      # the season in progress at the store cut
_m3_age_asof0=cp._age_asof; _m3_age0=MA.age; _m3_ten0=PR.tenure; _m3_eo0=_eo; _m3_feat0=cp._feat
def _m3_age_asof(p,Y):
    a=_m3_age_asof0(p,Y)
    return (a-1) if (_M3PIN['on'] and Y==M3_INPROG_Y) else a
def _m3_age(p):
    a=_m3_age0(p)
    return (a-1) if (_M3PIN['on'] and a is not None) else a
def _m3_ten(p,Y):
    t=_m3_ten0(p,Y)
    return max(1,t-1) if (_M3PIN['on'] and Y==M3_INPROG_Y) else t
def _eo(p,Y):                                                 # pin-aware rebind; _inferM1/_lvl_eff_infer read this global
    if not (_M3PIN['on'] and Y==M3_INPROG_Y): return _m3_eo0(p,Y)
    d=cp.debutyr(p); N=Y-d+1-1                                # N-1: the clock; data window stays at Y
    yrw=float(np.clip((N-2)/4.0,0.0,1.0))
    gm=sum(x.get('games',0) for x in p['scoring'] if (d-1)<x['year']<=Y)
    exp=float(np.clip(gm/(14.0*max(N-1,1)),0.0,1.0))
    return yrw*exp
def _m3_feat(p,Y):                                            # _feat's ten term uses raw Y-arithmetic, pin it explicitly
    f=list(_m3_feat0(p,Y))
    if _M3PIN['on'] and Y==M3_INPROG_Y:
        f[8]=eff_ten(p,Y, max(0,(Y-1)-(cp.debutyr(p)-1)))     # index 8 = ten (6 one-hots + logep, exposure, ten, lvl, age)
    return f
cp._age_asof=_m3_age_asof; MA.age=_m3_age; PR.tenure=_m3_ten; cp._feat=_m3_feat
# ===== helpers for delist + staleness =====
def delisted(p): return bool(p.get('_retired')) or (p.get('_last_listed') is not None and p['_last_listed']<2026)
def draftval(p): return float(MA.PVC[min(MA.effpk(p),cp.KMAX)])
def bestlvl(p,Y=2026):
    s=[a*REF/era.get(y,REF) for y,a in [(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6.0*(_fEy(Y) if x['year']==Y else 1.0) and x['year']<=Y]]   # D10: 6-bar prorated in-progress
    return max(s) if s else 0.0
def nseas(p,Y=2026): return sum(1 for x in p['scoring'] if x['games']>=6 and x['year']<=Y)   # unprorated career counter (harness/diagnostic callers)
def nseas_pro(p,Y=2026):                                      # D10: qualification judged against PLAYABLE games (6-bar -> 6*fE for the in-progress season)
    return sum(1 for x in p['scoring'] if x['year']<=Y and x['games']>=6.0*(_fEy(Y) if x['year']==Y else 1.0))
# ===== GAMES-RAMP SIT-OUT TREATMENT (D10 03/07/2026) — the retired-PVC anchor is PURGED =====
# Replaces the flat SITOUT_RETAIN x draftval anchor (obituary: BOARD_LAYERS_OBITUARY.md; derivation:
# session_2026-07-03/d10_ask2_derivation.md — harvest 2,465 complete-window still-listed cells 2004-2021,
# kernel eff-n>=35, busts=0).
#   V0(p) = raw_ev(p, draft year) x iso — the engine's LIVE zero-evidence pick+position start value
#     (Dean-below / Robey-above property). HELD through pre-season: tau=0 -> R=1, no penalty before a
#     season starts (Luke 2a).
#   R_SIT = retention of V0 for still-listed non-playing draftees, measured RELATIVE to the same-depth
#     all-draftee norm (the locked daEV-convention "0.76 form"), knots at end-of-season depths 1..6,
#     CONCAVE within-season accrual (the penalty prorates to season progress via tau'=(R/24)^1.5 —
#     Luke-signed OPTION A, D12 03/07/2026; SUPERSEDES the D10 linear form — Luke 2c-revised: a penalty
#     "should be slightly more generous as the sample is smaller"; 100% at R24/24, ~35% at halfway),
#     flat tail 6+.
#   LAM_SIT = measured evidence-credit blend toward the LIVE production path e_full (isotonic in games;
#     STRUCTURAL endpoints lam(0)=0, lam(prorated bar)=1 -> value CONTINUOUS at graduation: no cliff,
#     no game-6 jackpot — Luke 2b). Games read AT PACE (g/fE) against the prorated bar.
#   SCORING-AWARE through e_full: the production path prices actual output (Annable's 1g@40 is
#     information — Luke 2d). A lambda-side quality term was tested and NOT supported at finest
#     resolution (partial tau +0.04, non-monotone across q bins, n=364) — DECLARED, not wired.
#   POSITION BASIS preserved end-to-end: V0 and e_full both carry the band's position adjustment;
#     classes RUC/KPP/nonKPP for R_SIT only, with the RUC retention SHAPE pooled with KPP (thin bimodal
#     slice, n=270 cells) scaled to RUC's own measured d1-2 level x1.065 — DECLARED pooling.
# D13 ASK3 03/07/2026 — R_SIT (depth-only, per class, RUC-shape-pooled-with-KPP) is SUPERSEDED by the
# continuous log-pick x depth surface R_SURF below (obituary E4: BOARD_LAYERS_OBITUARY.md). The old table
# VIOLATED Luke's signed law (nonKPP rose d3->d5 .410->.437; KPP rose d5->d6 .253->.266 — a sitter gained
# value by sitting). Resurrection ref: git show af1fc6aa's _merged_recover.py. Old table (for the record):
#   R_SIT={'nonKPP':[.429,.404,.410,.432,.437,.424],'KPP':[.468,.380,.325,.278,.253,.266],'RUC':[.674,.547,.503,.472,.435,.435]}
# ===== RETENTION SURFACE (D13 ASK3) — re-derived at finest supported resolution =====
# R(cls, log-pick, depth) = kernel-smoothed sit-out realization r=O/V0 (winsor 2.0, Gaussian bw grown until
# eff-n>=35) / same-depth all-draftee daEV norm (per class; strips survivor selection, rises 0.44->1.11 w/
# depth), clip[.05,1], then ISOTONIC NON-INCREASING IN DEPTH at every pick (Luke's signed law: a sitter never
# gains value). R1: daEV(V0) denominator KEPT (position-blind dv WIDENED the KPP gap 0.065->0.079 -> numerator-
# driven, not pole-inflated: KPP V0/dv=0.90). R2: FIRES all classes (pick maxdev 0.13-0.21 > 0.05 ribbon) ->
# PICK-CONDITIONED. Derivation: session_2026-07-03/d13/d13_ask3_retention.md; scripts d13_derive.py.
# Knots = DIAGNOSTIC evaluation picks of the smooth surface (never derivation bins). Interp over log-pick + tau
# preserves depth-monotonicity (convex comb of non-increasing vectors). Deep KPP d4-6 pooled (thin, DECLARED).
R_SURF={'nonKPP':{5:[0.547,0.446,0.446,0.446,0.446,0.314], 15:[0.707,0.479,0.479,0.479,0.479,0.307], 30:[0.649,0.436,0.422,0.414,0.414,0.303], 50:[0.549,0.388,0.345,0.239,0.164,0.164]},
        'KPP':{5:[0.660,0.487,0.387,0.194,0.183,0.183], 15:[0.694,0.427,0.273,0.136,0.136,0.136], 30:[0.632,0.383,0.286,0.180,0.172,0.172], 50:[0.642,0.407,0.351,0.334,0.334,0.329]},
        'RUC':{5:[1.000,0.715,0.670,0.562,0.535,0.467], 15:[0.851,0.597,0.597,0.520,0.520,0.468], 30:[0.830,0.616,0.616,0.607,0.540,0.469], 50:[0.781,0.594,0.594,0.594,0.541,0.470]}}
_RS_KNOTS=[5,15,30,50]; _RS_LOGK=[np.log(k) for k in _RS_KNOTS]
# _BOARD_PATH: True on the live board render (present/forward valuation). The BACKTEST/WALK-FORWARD harnesses
# set g['_BOARD_PATH']=False after exec so Luke's D14 board-only laws (KPP retention floor O1 below; V0 curve
# further down) DO NOT touch the historical book (Luke's backtest exemption -> the walk-forward book reproduces).
_BOARD_PATH=True
def _dv_surf(cls,lp):                                        # depth vector (6) for a class at a given log-pick
    kn=R_SURF[cls]; return [float(np.interp(lp,_RS_LOGK,[kn[k][i] for k in _RS_KNOTS])) for i in range(6)]
def _R_surf(cls,pick,tau):                                   # interp over log-pick (knots) then over tau (0->1, depths 1..6, flat 6+)
    lp=np.log(min(max(pick,1),90)); dv=_dv_surf(cls,lp)
    # ==== D14 ASK2 (03/07/2026) — KPP RETENTION FLOOR (SIGNED OWNER OVERRIDE O1, Luke verbatim: "if it's lower,
    # it's carried so it can never be the lowest ... I can't see KPPs losing value for sitting at a faster rate
    # than non KPPs"). Wired KPP sit-out retention surface := pointwise MAX(KPP, nonKPP) at every (log-pick,depth).
    # Comparator = nonKPP ONLY (RUC EXCLUDED — own capped machinery; supervisor spec, stated to Luke pre-fire).
    # BOARD PATH ONLY (O1 scope). max() of two isotonic-non-increasing-in-depth vectors is non-increasing (re-
    # verified numerically in _v0_curve_assert). OWNER-SET where the floor binds, data-derived elsewhere. Governance:
    # docs/process/OWNER_OVERRIDES.md O1; obituary/registration BOARD_LAYERS_OBITUARY.md.
    if _BOARD_PATH and cls=='KPP':
        dvn=_dv_surf('nonKPP',lp); dv=[max(a,b) for a,b in zip(dv,dvn)]
    return float(np.interp(tau,[0,1,2,3,4,5,6],[1.0]+dv))
LAM_SIT=[0.0,0.160,0.493,0.547,0.547,0.816,1.0]
def _sitout_cls(pos): return 'RUC' if pos=='RUC' else ('KPP' if pos in ('KEY_FWD','KEY_DEF') else 'nonKPP')
# ==== ASK1 (D13 03/07/2026): RUC PRIOR CAP — cap the hot ruck band prior as a max V0/PVC ratio. Parameterised
# dial RL_RUC_PRIOR_CAP; DEFAULT 1.73 = the class's own ND-ruck median V0/PVC (Luke's inclination, D13 ASK1:
# "I'd be inclined to just cap ruck prior at the 1.73 median"). Sits at the raw_ev/band level (for RUC wage=0
# so raw_ev==the band price) so it flows into V0, the sit-out blend, the floor and the prior-dominated
# production path — NOT a display-stage V0 clamp (D12: Emmett's board value is blend-fed by the prior). Scope:
# REAL rucks only (synth ISO/POLE tables untouched). The pure prior V0 is capped unconditionally (min binds
# only when hot, V0/PVC>cap). The PRODUCTION leg is capped only in the PRIOR-DOMINATED regime — C*PVC < e_full
# <= V0_uncapped: hot prior AND production has NOT grown beyond the start value; any ruck who has demonstrated
# production above his (uncapped) start value (Sweet 2011, McAndrew 992, Xerri 5755, Grundy, Gawn, Marshall)
# is byte-exact. Derivation/ladder: session_2026-07-03/d13/d13_ask1_ruck_cap.md.
RUC_PRIOR_CAP=float(os.environ.get('RL_RUC_PRIOR_CAP','1.4'))   # BAKED default 1.73->1.4 (owner ruck-cap dial, v2.4 bake 2026-07-04; env override preserved)
def _ruc_prior_cap(p,v):                                      # cap a RUC band-fed value at RUC_PRIOR_CAP x PVC (real rucks)
    return min(v, RUC_PRIOR_CAP*draftval(p)) if (_isreal(p) and MA.gfut(p)=='RUC') else v
_V0C={}; _V0U={}
_V0_CM, _V0_Q97 = cm, q97m    # V0 is a STRUCTURAL prior: pin the import-time models (the pole/ISO convention —
                              # gate1's own rule: "pole(_POLE) + ISO stay in-sample structural priors"). In the
                              # live engine this is an identity (same objects); in fold-swapping harnesses the
                              # zero-evidence start value stays fold-stable instead of reading prior-training
                              # variance as phantom leakage at T0/T1 cells.
def _v0key(p): return (p.get('player'),p.get('year'),p.get('pick'),p.get('type'),p.get('dob'),MA.gfut(p),MA.effpk(p))
def _v0_uncapped(p):                                          # zero-evidence band start value — NO ruc cap, NO guard (RUC gate + guard-build use this)
    # cache key = STABLE CONTENT, not id(p): harnesses that deepcopy players (gate1 truncations) recycle
    # memory addresses; V0's inputs are all draft-time content -> same content, same V0.
    k=_v0key(p)
    if k not in _V0U:
        global cm,q97m
        _c,_q=cm,q97m; cm,q97m=_V0_CM,_V0_Q97
        try: _V0U[k]=raw_ev(p,cp.debutyr(p)-1)*iso_corr(MA.gfut(p),MA.effpk(p))
        finally: cm,q97m=_c,_q
    return _V0U[k]
def _v0_raw(p):                                              # ASK1: uncapped V0 -> RUC prior cap (still pre-ASK2-guard)
    k=_v0key(p)
    if k not in _V0C: _V0C[k]=_ruc_prior_cap(p,_v0_uncapped(p))
    return _V0C[k]
# ==== D13 ASK2 V0 PICK-ORDER GUARD — now RETAINED FOR THE BACKTEST/WALK-FORWARD PATH ONLY. On the BOARD PATH it
# is SUPERSEDED by the D14 V0 curve below (obituary E5; Luke's amended law). Luke's backtest exemption (D14,
# verbatim: "For the backtesting this is not a rule and doesn't make sense to be") means the historical book must
# be UNCHANGED; the v2.3 walk-forward book was built on these guard values, so keeping the guard on the backtest
# path reproduces that book byte-for-byte (maxΔ=0). [D13 spec, for the record:] WITHIN (position x draft-age x
# draft-year) cells V0 is NON-INCREASING in RECORDED pick; downward-only projection to the in-cell running min;
# mature-age/differing-age pairs sit in SEPARATE cells (exempt by construction); scope REAL ND (recorded==effective).
_V0GUARD={}
def _v0_cell(p): return (MA.gfut(p), int(round(cp._age_asof(p, p.get('year') or (cp.debutyr(p)-1)))), p.get('year'))
def _build_v0_guard():
    cells={}
    for p in MA.data:
        if not _isreal(p) or p.get('type')!='ND' or p.get('pick') is None: continue
        cells.setdefault(_v0_cell(p),[]).append(p)
    for _cell,ps in cells.items():
        run=float('inf')
        for q in sorted(ps,key=lambda z:z.get('pick')):            # ascending pick (best -> worst)
            run=min(run,_v0_raw(q)); _V0GUARD[_v0key(q)]=run        # non-increasing downward cap over pick
_build_v0_guard()
# ==== D14 ASK1 (03/07/2026): V0 BOARD CURVE — Luke's AMENDED LAW (verbatim): "for the current values that end up
# in the engine/on the board, we can't have a situation where one player who was a mid at pick 8 has a higher
# starting v0 than another in the same boat. It's illogical." => same POSITION x DRAFT-AGE x RECORDED-PICK gives
# the SAME starting V0 across draft years, on the board. Derivation (fitted on the CURRENT roster's CAPPED V0s —
# the ASK1 ruck cap applies FIRST, i.e. we fit _v0_raw = cap(_v0_uncapped); then the curve): a CONTINUOUS
# kernel/local regression of capped V0 over log RECORDED pick, POOLED ACROSS DRAFT YEARS, projected ISOTONIC
# NON-INCREASING in pick. Pick bands are diagnostic slices only, never derivation bins (binding statistics rule).
# CELLS at the finest resolution the sample supports (census in session_2026-07-03/d14):
#   TIER 1 — age<=18 per position (6 cells; 1408/1571 players): adaptive Gaussian bandwidth grown until local
#     eff-n>=35 at every pick, then isotonic. RUC is its OWN age18 curve (fitted on capped V0s).
#   TIER 2 — mature (draft-age>=19; 163 players): every exact (pos x age) cell is eff-n<35 even at max bandwidth
#     -> R1 pooling. Mature V0 is age-dominated and position-washed in-sample (position spread << age spread), so
#     the 5 non-RUC positions POOL into one age-resolved surface V0*(age,log-pick) [DECLARED]; RUC mature keeps
#     its own (thin) cell. Fit is 2D-kernel over (draft-age, log-pick), then isotonic-non-increasing in pick AND
#     non-increasing in draft-age (older draftee never starts above a younger one, same pick) — so mature entrants
#     stay LAWFULLY DIFFERENTIATED from age-18 and by age. eff-n growth/shortfalls recorded in _V0CURVE_META (R1).
# APPLY on the BOARD PATH: every current-roster real-ND start anchor V0 := V0*(pos, draft-age, recorded pick),
# feeding every present/forward consumer (sit-out retention, staleness/stalled/mediocre caps, the B5 floor, the
# delist scrap). The BACKTEST path is untouched (guard, above). By-construction gates in _v0_curve_assert().
_BOARD_PATH  # (declared above, before _R_surf)
_V0CURVE={}; _V0CURVE_META={}; _V0_GRIDPK=list(range(1,91)); _V0_LGRID=np.log(_V0_GRIDPK)
def _ageR(p): return int(round(cp._age_asof(p, p.get('year') or (cp.debutyr(p)-1))))
def _iso_dec(y): return list(map(float,IsotonicRegression(increasing=False,out_of_bounds='clip').fit(_V0_LGRID,y).predict(_V0_LGRID)))
def _fit_pick_curve(pts,effn_min=35.0,h0=0.18,hmax=2.2):     # adaptive-bandwidth NW over log-pick -> isotonic non-increasing
    lx=np.array([a for a,_ in pts]); vy=np.array([b for _,b in pts]); grid=[]; meta_e=[]; meta_hmax=0
    for lg in _V0_LGRID:
        h=h0
        while True:
            w=np.exp(-0.5*((lx-lg)/h)**2); sw=w.sum(); effn=(sw*sw)/float(np.sum(w*w)) if sw>0 else 0.0
            if effn>=effn_min or h>=hmax: break
            h*=1.15
        if h>=hmax: meta_hmax+=1
        grid.append(float(np.dot(w,vy)/sw) if sw>0 else float(vy.mean())); meta_e.append(effn)
    return _iso_dec(grid), dict(n=len(pts),min_effn=float(min(meta_e)),grid_at_hmax=meta_hmax)
def _fit_mature(pts,label,effn_min=35.0,ha0=1.2,hamax=8.0,hp0=0.18,hpmax=2.2):  # 2D (draft-age,log-pick) kernel; age-resolved surface
    aa=np.array([a for a,_,_ in pts]); lx=np.array([l for _,l,_ in pts]); vy=np.array([v for _,_,v in pts])
    ages=list(range(19,31)); surf={}; mine=1e9; hmaxhit=0
    for ag in ages:
        row=[]
        for lg in _V0_LGRID:
            ha,hp=ha0,hp0
            while True:
                w=np.exp(-0.5*((aa-ag)/ha)**2)*np.exp(-0.5*((lx-lg)/hp)**2); sw=w.sum()
                effn=(sw*sw)/float(np.sum(w*w)) if sw>0 else 0.0
                if effn>=effn_min or (ha>=hamax and hp>=hpmax): break
                if ha<hamax: ha*=1.2
                else: hp*=1.15
            if ha>=hamax and hp>=hpmax: hmaxhit+=1
            row.append(float(np.dot(w,vy)/sw) if sw>0 else float(vy.mean())); mine=min(mine,effn)
        surf[ag]=_iso_dec(row)                                # pick-isotonic per age
    for i in range(len(_V0_GRIDPK)):                          # then non-increasing in draft-age at each pick
        run=1e18
        for ag in ages: run=min(run,surf[ag][i]); surf[ag][i]=run
    _V0CURVE_META[label]=dict(n=len(pts),min_effn=float(mine),grid_at_hmax=hmaxhit,ages=ages)
    return surf
def _build_v0_curve():
    POS=['MID','KEY_FWD','KEY_DEF','GEN_FWD','GEN_DEF','RUC']; c18={}
    real=[p for p in MA.data if _isreal(p) and p.get('type')=='ND' and p.get('pick') is not None]
    for pos in POS:
        pts=[(np.log(p.get('pick')),_v0_raw(p)) for p in real if MA.gfut(p)==pos and _ageR(p)<=18]
        grid,meta=_fit_pick_curve(pts); c18[pos]=grid; _V0CURVE_META[('age18',pos)]=meta
    matN=[(_ageR(p),np.log(p.get('pick')),_v0_raw(p)) for p in real if MA.gfut(p)!='RUC' and _ageR(p)>=19]
    matR=[(_ageR(p),np.log(p.get('pick')),_v0_raw(p)) for p in real if MA.gfut(p)=='RUC'      and _ageR(p)>=19]
    surfN=_fit_mature(matN,'mature_nonRUC'); surfR=_fit_mature(matR,'mature_RUC')
    _V0CURVE_META['_c18']=c18; _V0CURVE_META['_surfN']=surfN; _V0CURVE_META['_surfR']=surfR
    def star(pos,ag,pick):
        lp=np.log(min(max(pick,1),90))
        if ag<=18: return float(np.interp(lp,_V0_LGRID,c18[pos]))
        surf=surfR if pos=='RUC' else surfN; return float(np.interp(lp,_V0_LGRID,surf[min(max(ag,19),30)]))
    _V0CURVE_META['_star']=star
    for p in real: _V0CURVE[_v0key(p)]=star(MA.gfut(p),_ageR(p),p.get('pick'))
_build_v0_curve()
def v0_start(p):                                             # BOARD -> D14 V0 curve (Luke's amended law); BACKTEST -> D13 guard (Luke's exemption)
    v=_v0_raw(p)                                             # ASK1 ruck cap applied FIRST (cap -> curve/guard order)
    if _BOARD_PATH:
        c=_V0CURVE.get(_v0key(p)); return c if c is not None else v
    g=_V0GUARD.get(_v0key(p)); return v if g is None else min(v,g)
def _v0_curve_assert():                                      # BY-CONSTRUCTION GATES (D14 1c): wired, return dict of results
    star=_V0CURVE_META['_star']; ages=_V0CURVE_META['mature_nonRUC']['ages']
    # (i) same (pos,ageR,pick) -> identical V0* across draft years (function of pos,ageR,pick only) — check dispersion
    from collections import defaultdict
    grp=defaultdict(list)
    for p in MA.data:
        if _isreal(p) and p.get('type')=='ND' and p.get('pick') is not None:
            grp[(MA.gfut(p),_ageR(p),p.get('pick'))].append(v0_start(p))
    maxdisp=max((max(v)-min(v) for v in grp.values()),default=0.0)
    # (ii) within (pos,ageR,year) cell inversions under V0*
    byc=defaultdict(list); inv=0
    for p in MA.data:
        if _isreal(p) and p.get('type')=='ND' and p.get('pick') is not None:
            byc[(MA.gfut(p),_ageR(p),p.get('year'))].append(p)
    for _c,ps in byc.items():
        ps=sorted(ps,key=lambda z:z.get('pick'))
        for i in range(len(ps)):
            for j in range(i+1,len(ps)):
                if ps[j].get('pick')>ps[i].get('pick') and v0_start(ps[j])>v0_start(ps[i])+1e-6: inv+=1
    # (iii) depth-monotonicity of the KPP-floored retention surface (max of non-increasing curves)
    dmono=True
    for pk in [3,8,15,30,50,80]:
        dv=[ _R_surf('KPP',pk,t) for t in range(1,7) ]
        if any(dv[k+1]>dv[k]+1e-9 for k in range(5)): dmono=False
    return dict(cross_draft_maxdisp=maxdisp, within_cell_inversions=inv, kpp_depth_monotone=dmono)
def sitout_ev(p,Y,e_full):
    fe=_fEy(Y); tau=max(0.0,Y-cp.debutyr(p))+((fe**1.5) if Y>=cp.debutyr(p) else 0.0)   # D12: CONCAVE penalty proration tau'=(R/24)^1.5 (Luke OPTION A); completed seasons full (integer knots), in-progress season accrues concavely. PENALTY path only — the lam reward blend below is UNTOUCHED.
    R=_R_surf(_sitout_cls(MA.gfut(p)), MA.effpk(p), tau)     # D13 ASK3: pick-conditioned, isotonic-in-depth surface (was depth-only R_SIT)
    gy=sum(x['games'] for x in p['scoring'] if x['year']==Y)
    lam=float(np.interp(min(gy/fe,6.0),[0,1,2,3,4,5,6],LAM_SIT))                 # games AT PACE vs the prorated bar
    return (1.0-lam)*R*v0_start(p)+lam*e_full
def _first_evidence(p,Y):                                     # the games-ramp family: ALL evidence is season Y
    return not any(x['games']>0 and x['year']<Y for x in p['scoring'])
def _prod_path(p,Y):
    """Production price e_full = raw_ev x iso. For the FIRST-EVIDENCE family, a 3-point moving average
    on the GAMES axis (+/-1 game at the player's own scoring rate) — DECLARED smoothing: the band prior
    is a stepwise (GBR) surface whose exposure-axis steps (measured +957 in one game on the B6 synth)
    and the designed M3 pin-fade otherwise leave the evidence ramp non-monotone (B6 law: more games at
    the same rate never worth less). Centered, unit-mass, level-preserving; nobody outside the family
    is touched."""
    e=raw_ev(p,Y)*iso_corr(MA.gfut(p),MA.effpk(p))
    if not _first_evidence(p,Y): return e
    row=[x for x in p['scoring'] if x['year']==Y and x['games']>0]
    if not row: return e
    r=row[0]; g0=r['games']; out=[]
    try:
        for gg in (max(g0-1,1),g0,g0+1):
            if gg==g0: out.append(e); continue
            r['games']=gg
            out.append(raw_ev(p,Y)*iso_corr(MA.gfut(p),MA.effpk(p)))
    finally: r['games']=g0
    return float(np.mean(out))
# ===== WIRED ev =====
def ev(p,Y=2026):
    # (1) delist -> near-zero (no future keeper value) — D10: scrap re-anchored to the LIVE start value
    if delisted(p): return round(0.02*v0_start(p))
    e=_prod_path(p,Y)                                        # (3) isotonic guard inside; family games-axis smoothing
    if _isreal(p) and MA.gfut(p)=='RUC':                  # ASK1: cap PRIOR-DOMINATED ruck production leg only
        _cpv=RUC_PRIOR_CAP*draftval(p); _v0u=_v0_uncapped(p)  #   bind iff C*PVC < e <= V0_uncapped (hot prior, no demonstrated growth);
        if _cpv<e<=_v0u: e=_cpv                               #   e>V0u (demonstrated) or e<=C*PVC (already low) -> byte-exact

    # (2) staleness family — D10: prorated bars + V0 basis (old-PVC draftval PURGED from every penalty path)
    pos=MA.gfut(p); el=PR.tenure(p,Y); ns=nseas_pro(p,Y); v0=v0_start(p); par=PR.par_at(pos,min(MA.effpk(p),cp.KMAX),min(max(el,1),6)); pr=bestlvl(p,Y)/max(1,par)
    if ns==0:                                                 # SIT-OUT: derived games-ramp treatment (V0-anchored, prorated, scoring-aware, continuous at graduation)
        return round(sitout_ev(p,Y,e))
    keyruc = pos in ('KEY_FWD','KEY_DEF','RUC'); onset = (4 if keyruc else 3)
    if el>=onset and ns<=1:                                   # stalled: essentially no production after the window
        frac=0.25*max(0.4,1-0.10*(el-onset))*(1.6 if keyruc else 1.0)
        e=min(e, v0*frac)
    elif el>=onset+2 and pr<0.55:                             # mediocre-for-years (played but never near par) -> decays too
        frac=0.45*max(0.3,1-0.08*(el-onset))*(1.5 if keyruc else 1.0)
        e=min(e, v0*frac)
    return round(e)
# ==== M3 PROPORTIONAL-TENURE/AGE BLEND (BAKE CANDIDATE v2, D7 02/07/2026 — design + backtest:
# session_2026-07-02/m3_design_proportional_tenure.md; NOT baked until Luke's bake word) ====
# Mid-season the age/tenure clocks advance a FULL year while the season is only fE elapsed. M3 evaluates
# the in-progress season as a VALUE-SPACE interpolation between the full-click evaluation and the
# clock-pinned evaluation (the _M3PIN plumbing above):  v = w*ev_click + (1-w)*ev_pin,
# w = 1 - s*(1-fE), s = clip(1 - g_Y/11, 0, 1) (M2's evidence-replacement scope, same denominator).
# On-pace players (g_Y >= 11) have s=0 -> untouched BY CONSTRUCTION. Completed seasons (Y != the
# in-progress season) are untouched by construction. fE = SEASON_PROG = 0.58 at this cut, recomputed per
# evaluation date (fE -> 1 as the season completes). RL_M3_FE=1 = kill-switch (byte-exact inert).
# RE-REGISTERED ACCEPTANCE at this config (D7): A3 >= 0.75 (Luke's amended bar) with ZERO on-pace
# collateral >2% and B-gates holding.
M3_FE=float(os.environ.get('RL_M3_FE','0.58'))                # elapsed-season fraction; 1.0 -> lever off
M3_DEN=11.0                                                   # M2's evidence-replacement denominator (on-pace floor)
_ev_click=ev                                                  # the full-click evaluation (M1+asc + M2 + caps)
def _m3_s(p,Y):
    gy=sum(x['games'] for x in p['scoring'] if x['year']==Y)
    return float(np.clip(1.0-gy/M3_DEN,0.0,1.0))
def _ev_m3(p,Y=2026):
    v=_ev_click(p,Y)
    if Y!=M3_INPROG_Y or M3_FE>=1.0 or delisted(p): return v  # delisted: both evals identical (no clock read) — skip the double eval
    s=_m3_s(p,Y)
    if s<=0.0: return v                                       # on-pace: untouched by construction
    w=1.0-s*(1.0-M3_FE)
    _M3PIN['on']=True
    try: vpin=_ev_click(p,Y)
    finally: _M3PIN['on']=False
    return round(w*v+(1.0-w)*vpin)
# ==== PRICING FLOOR (BAKE CANDIDATE v2, D7 02/07/2026 — Luke's ruling, B5 amendment: the crater floor
# becomes a PRICING FEATURE; prototype engine/prototypes/floor_pricing_clamp.py 66fbf0f6, D6) ====
# D12 03/07/2026 (Luke ruling R8): floor basis RE-ANCHORED old-PVC draftval -> live V0 start value.
# Schedule (FLOOR_YRS) values UNCHANGED — only the denominator moves onto the same ruler as every other
# penalty path (D10 re-anchored those; the floor was the declared dv-basis holdout). Obituary E3.
#   ev(p,Y) = max(ev_prefloor(p,Y), floor_yrs(Y - draft year) * v0_start(p))
# Scope: REAL store players (id in _REAL — gate synths keep the raw engine, same guard as the v7 overlay),
# NATIONAL-DRAFT entrants only; MSD/SSP (type!='ND'), delisted, retired and pickless players are NEVER
# floored (byte-exact passthrough). Pure lower bound: any player at/above floor is untouched byte-exact
# by construction (max()). TAIL VARIANT A — FLAT .05 yrs 7+ (as signed; Luke's D7 ruling). The FLOOR-SAVES
# table prints on every gates-board run (ship_gates_check.py B5 block) — mispricings stay VISIBLE.
FLOOR_YRS={1:0.45,2:0.35,3:0.28,4:0.21,5:0.13,6:0.09}         # yrs 1-6 (signed schedule)
FLOOR_TAIL=0.05                                               # yrs 7+ FLAT (VARIANT A, as signed)
def floor_frac(yis): return FLOOR_YRS.get(yis,FLOOR_TAIL)
ev_prefloor=_ev_m3                                            # harnesses read this for the saves table / lower-bound re-verify
def ev(p,Y=2026):
    v=ev_prefloor(p,Y)
    if not _isreal(p) or p.get('type')!='ND' or p.get('_retired') or p.get('_pickless') or delisted(p):
        return v                                              # out of scope: byte-exact passthrough
    yis=Y-int(p.get('year') or 0)
    if yis<1: return v
    fl=floor_frac(yis)*v0_start(p)     # D12: RE-ANCHORED draftval -> live V0 (schedule unchanged; Luke R8)
    return v if v>=fl else round(fl)
def find(nm):
    c=[p for p in MA.data if nm.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]; return c[0] if c else None
print("=== AFTER (wired: delist + staleness + isotonic) — named players ===")
print(f"{'player':22s}{'pos':8s}{'pk':>3s}{'g':>3s}{'ten':>4s}{'dlst':>5s}{'draft':>6s}{'BEFORE':>7s}{'AFTER':>7s}  reasoning")
before={'Ronin O':526,'Will Martyn':554,'Sam Philp':714,'Oscar Ryan':570,'Tew Jiath':509,'Jakob Ryan':594,'Harrison Jones':528,'Keidean Coleman':723,'Dylan Stephens':761}
reason={'Ronin O':'delisted, 0g -> ~0','Will Martyn':'delisted, 0g -> ~0','Sam Philp':'delisted, 0g -> ~0','Oscar Ryan':'stalled 0g ten3 -> 1/4 draft','Tew Jiath':'stalled 0g ten3 -> 1/4 draft','Jakob Ryan':'stalled 0g ten4 -> notch below 1/4','Harrison Jones':'mediocre 7yr KEY_FWD -> decayed','Keidean Coleman':'career-maker, holds','Dylan Stephens':'declined MID, should fall below Coleman'}
for nm in before:
    p=find(nm)
    if not p: continue
    print(f"{p['player'][:22]:22s}{MA.gfut(p):8s}{MA.effpk(p):3d}{nseas(p):3d}{PR.tenure(p,2026):4d}{('Y' if delisted(p) else '-'):>5s}{draftval(p):6.0f}{before[nm]:7d}{ev(p):7d}  {reason[nm]}")
print("\n=== MONOTONICITY + deep-pick AFTER ===")
for pos in ['KEY_FWD','MID']:
    for pk in [1,2,3,20,60]:
        sp=synth(pk,PR.par_at(pos,min(pk,cp.KMAX),4),pos); print(f"  {pos:8s} pk{pk:2d} @par -> {ev(sp)}", end='')
    print()
c=find('Keidean Coleman'); s=find('Dylan Stephens')
print(f"\n=== Coleman vs Stephens: Coleman {ev(c)} {'>=' if ev(c)>=ev(s) else '<'} Stephens {ev(s)} -> {'FIXED' if ev(c)>=ev(s) else 'STILL INVERTED'}")

print("\n\n════════ DIAGNOSE Harrison/Stephens + GATE1 + deep collapse + falsifier (wired) ════════")
def band_dump(p):
    b=b6(p); pos=MA.gfut(p); par=PR.par_at(pos,min(MA.effpk(p),cp.KMAX),min(max(PR.tenure(p,2026),1),6))
    recent=[ (x['year'],x['avg']) for x in p['scoring'] if x['games']>=6][-3:]
    return b,par,recent
for nm in ['Harrison Jones','Dylan Stephens','Keidean Coleman']:
    p=find(nm); b,par,recent=band_dump(p)
    print(f"  {nm:16s} par{par:.0f} band[q10..q97]={[round(x) for x in b]} recent={recent} best{bestlvl(p):.0f} pr{bestlvl(p)/par:.2f} ev{ev(p)}")
print("  -> if band q50/q70 high vs recent, cond_prior is pricing career not decline; if q97 tail high, upside inflates")
# refine: DECLINE/MEDIOCRE via RECENT production (last-2-season avg vs par), not just best
def recent_ratio(p,Y=2026):
    s=[a*REF/era.get(y,REF) for y,a in [(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6 and x['year']<=Y]][-2:]
    return (np.mean(s)/max(1,PR.par_at(MA.gfut(p),min(MA.effpk(p),cp.KMAX),min(max(PR.tenure(p,Y),1),6)))) if s else 0.0
print("\n  RECENT ratio (last-2 avg / par):")
for nm in ['Harrison Jones','Dylan Stephens','Keidean Coleman','Oscar Ryan']:
    p=find(nm); print(f"    {nm:16s} recent_ratio={recent_ratio(p):.2f}")
print("\n=== GATE1 (wired) MID/KEY_FWD by tenure ===")
for pos in ['MID','KEY_FWD','GEN_DEF']:
    refs=[p for p in MA.data if MA.gfut(p)==pos and p.get('type')=='ND' and p.get('pick') and 2012<=p['year']<=2019 and nseas(p)>=4 and not delisted(p)][:14]
    ser={}
    for k in range(0,6):
        vs=[ev(p,cp.debutyr(p)-1+k) for p in refs if cp.debutyr(p)-1+k<=2026 and any(s['year']<=cp.debutyr(p)-1+k and s['games']>=6 for s in p['scoring'])]
        if vs: ser[k]=np.mean(vs)
    base=ser.get(2,1); print(f"  {pos:8s} "+" ".join(f"yr{k}:{round(100*v/base)}" for k,v in sorted(ser.items())))
print("\n=== 2019 deep-pick (pk>40) REAL collapse (wired) ===")
deep=[p for p in MA.data if p.get('type')=='ND' and p.get('pick') and p['year']==2019 and MA.effpk(p)>40 and MA.GRP.get(p.get('pos'))]
tot_before=sum(raw_ev(p) for p in deep); tot_after=sum(ev(p) for p in deep); tot_draft=sum(draftval(p) for p in deep)
print(f"  {len(deep)} deep picks: BEFORE sum {tot_before:.0f} | AFTER sum {tot_after:.0f} | draft sum {tot_draft:.0f} | realized PVC sum {tot_draft:.0f}")
print(f"  AFTER/draft = {100*tot_after/tot_draft:.0f}% (was {100*tot_before/tot_draft:.0f}%) -> collapse toward realized")
print("\n=== FALSIFIER still clean (wired)? ===")
def mkf(pk,avg): return synth(pk,avg,'MID')
e1=ev(mkf(1,70)); e2=ev(mkf(20,72)); bu=ev(mkf(1,40)); el=ev(mkf(20,95)); md=ev(mkf(1,62))
print(f"  PRIMARY pk1@70 {e1} {'>' if e1>e2 else '<'} pk20@72 {e2} | ELITE pk20@95 {el} {'>' if el>md else '<'} pk1@62 {md} | grid {'PASS' if all(ev(mkf(1,86+d))>ev(mkf(20,67+d)) for d in [-30,-12,0,12,25]) else 'FAIL'}")
