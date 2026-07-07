import json, numpy as np, math, re
import pgrid   # establishment-P surface (Praw + mat_mult); ported onto the board 2026-06-21 (was compute.py-only)
from unidecode import unidecode
data=json.load(open('rl_model_data.json')); P=json.load(open('params.json')); PMD=json.load(open('rl_passmark.json'))
# --- POSITION MODEL (DPP STRIP 2026-07-05, final consolidation): the DPP weighted-blend is DELETED. The store
#   now carries THREE clean SINGLE-VALUED columns (no probabilistic legs anywhere):
#   drafted_position : career/draft position -> drives the cohort curves (the engine's internal p['pos'])
#   present_position : the player's CURRENT position -> the YEAR-0 leg of his own valuation (p['_pos_now'])
#   future_position  : the player's SETTLED FUTURE position -> the YEARS-1+ leg + curve/peak/runway (p['_futpos'])
# Pricing reads present_position for the year-0 REPL bar (bnow) and future_position for the years-1+ REPL bar
# and the peak/curve (gfut). In THIS build future_position == present_position for every player, so bnow==gfut
# and every player resolves as a single position -- but the SEAM is live: a later transition model can populate
# future_position where it should differ from present, with no schema change and no code change. The old
# raw_multipos blend (futblend weights, gfut multi-leg, _fut list) is GONE; each dual is collapsed to its
# primary (present/dominant) leg. See evidence/dpp_strip/ for the full re-pricing.
for _p in data:
    _p['pos']=_p['drafted_position']
    _pp=_p.get('present_position')
    _p['_pos_now']=_pp if (_pp and _pp!=_p['pos']) else None
    _p['_futpos']=_p.get('future_position') or _pp    # single settled-future position (fallback to present)
# --- MSD/IRE credit machinery SCRUBBED 2026-07-05 (Luke directive, one-source rewire) ------------
# The v3.3.1 MSD mid-season debut standardisation (MSD_Y1_MULT=1.5x debut-year game boost, folded into
# the career total) is DELETED, together with the four credit/bust phantom rows and the _double_count /
# _phantom apparatus. Real mid-season draftees are now priced from their raw recorded games -- no boost,
# no labelled replacement. See evidence/f1f2_rewire/ for the before/after decomposition.
# ------------------------------------------------------------------------------------------------
PEAK=P['PEAK']; PEAK_AGE=P['PEAK_AGE']; pm_pos=PMD['pm_pos']; pm_band={int(k):v for k,v in PMD['pm_band'].items()}; BANDS=PMD['bands']; NB=len(BANDS)
AGE_CURVE={g:{int(a):f for a,f in c.items()} for g,c in P.get('AGE_CURVE',{}).items()}   # per-position empirical age curve (Phase-2 dev projection only; present value() untouched)
def _smooth_tail(c):                                   # enforce monotonic non-increasing post-peak + >=1%/yr continued decline (kills thin-tail plateaus/blips, e.g. RUC holding flat at 35)
    if not c: return c
    pk=max(c,key=c.get); out=dict(c)
    for a in sorted(c):
        if a>pk: out[a]=min(c[a], out[a-1]-0.010)
    return out
AGE_CURVE={g:_smooth_tail(c) for g,c in AGE_CURVE.items()}
GRP={'MID':'MID','RUC':'RUC','GFWD':'GEN_FWD','KFWD':'KEY_FWD','GDEF':'GEN_DEF','DEF':'GEN_DEF','KDEF':'KEY_DEF'}
# A player's CAREER/draft position (p['pos']) drives his contribution to the cohort curves.
# An optional p['_pos_now'] is his CURRENT position and drives only his own active valuation
# (e.g. Dangerfield: drafted+developed a MID -> feeds the MID pool; plays FWD now -> valued as a forward).
def bnow(p): return GRP.get(p.get('_pos_now')) or GRP[p['pos']]     # PRESENT position -> year-0 REPL bar
def gfut(p):                                  # SETTLED FUTURE position (single) -> drives curve/peak/runway + years-1+ REPL
    fp=p.get('_futpos')
    if fp: return GRP.get(fp) or bnow(p)
    return bnow(p)                            # no future_position (e.g. gate synths) -> present position
def futblend(p): return [(gfut(p),1.0)]       # DPP STRIP: years-1+ leg is a SINGLE position (future_position), no blend
# Real-life entry mechanisms. National draft ('ND') is the pick scale. Rookie ('RD') extends it.
# The rest entered with NO national slot -> their _eff (pick-equivalent) is derived empirically AFTER the PVC is built.
PICKLESS={'SSP','MSD','IRE','UNR','PDA','PDN','PDS'}
PMAX=0.25
BETA_POS={'MID':1.10,'GEN_DEF':0.84,'GEN_FWD':0.98,'KEY_FWD':0.92,'KEY_DEF':0.63,'RUC':0.95}
ICPT_POS={'MID':4.08,'GEN_DEF':1.92,'GEN_FWD':2.40,'KEY_FWD':1.58,'KEY_DEF':0.06,'RUC':2.79}
BUST_BAND={int(k):v for k,v in PMD['BUST_BAND'].items()}
def norm(n): return " ".join(re.sub(r"[^a-z ]"," ",unidecode(n).lower()).split())
def slug(n): return re.sub(r"[^a-z0-9]+","-",unidecode(n).lower()).strip('-')
# birthyear is carried in-data (_by, from the sheet Age col); no fuzzy matching needed.
AGE_REF=2026                          # "now" anchor for the age clock; bumped by forward/back board views (re-ages everyone, leaves demonstrated form fixed). Default 2026 reproduces the shipped values byte-for-byte.
BASE_REF=2026                         # true-now anchor for demonstrated form + scoring truncation. offset=AGE_REF-BASE_REF drives the Phase-2 dev projection; BASE_REF==AGE_REF==2026 reproduces shipped values byte-for-byte.
_LEVEL_OVR=None                       # when set, level_now returns this (used to integrate value over the level distribution in the variance layer); None in all default/parity paths.
def by(p): return p.get('_by') or (p['year']-18)   # FIX: _by can be present-but-None (cont.22 DOB fold-in wrote explicit None for ~302 DOB-less records); .get(key,default) would return None and crash _age_at. Guard like L367.
def _cycle_year(p): return p['year']-(1 if p.get('type')=='MSD' else 0)   # MSD draft_year IS the debut year, so its ND/RD-cycle equivalent is -1; SSP draft_year already IS the cycle year
def _age_at(p,ref): return max(ref-by(p), 18+(ref-_cycle_year(p)))
def age(p): return _age_at(p,AGE_REF)
def debut(p): return p['year'] if p['type']=='MSD' else p['year']+1   # ONLY MSD (mid-season) debuts in its draft_year; ND/RD/SSP AND post-draft signings (PDA/PDN/PDS/IRE/UNR) are off-season -> debut year+1 (fixes 2025 post-draft first-years leaking onto the -1 backward board)
def seasons(p): return max(1,AGE_REF-debut(p))
def effpk(p): return p.get('_eff', min(99, (p['pick'] or 60)))
def bandof(pk):
    for i,(lo,hi) in enumerate(BANDS):
        if lo<=pk<=hi: return i
    return len(BANDS)-1
DEF_CURVE=[56,62,67,71,74,77,79,80,80,79]
def expected(g,band,s):
    s=max(1,min(10,int(s))); c=pm_pos.get('%d|%s'%(band,g)) or pm_band.get(band) or DEF_CURVE; v=c[s-1]
    if v is None:
        vv=[x for x in c if x is not None]; v=vv[min(s-1,len(vv)-1)] if vv else DEF_CURVE[s-1]
    return v
def bandpeak(g,band):
    c=pm_pos.get('%d|%s'%(band,g)) or pm_band.get(band) or DEF_CURVE; vv=[x for x in c if x is not None]; return max(vv) if vv else 75
# ---- empirical basepk & position mix per band ----
def srel(p):
    d=debut(p); o={}
    for r in p['scoring']:
        s=r['year']-d+1
        if 1<=s<=14 and r['games']>=4: o[s]=(r['avg'],r['games'],r['year'])
    return o
def pkbest(p):
    d=debut(p); s=sorted([r['avg'] for r in p['scoring'] if r['games']>=10 and r['year']>=d],reverse=True)[:2]; return float(np.mean(s)) if s else None
# ---- entry classification on REAL pick numbers. ND is the national-pick scale; RD extends it by that
# year's national-pick count. PICKLESS mechanisms (MSD/SSP/Ireland/Unregistered/post-draft) carry NO slot;
# their _eff (pick-equivalent) is derived empirically from realised value AFTER the PVC exists (see below). ----
from collections import Counter as _Cnt
_NDC=dict(_Cnt(p['year'] for p in data if p['type']=='ND'))   # national-draft size per year, from the data
for _p in data:
    _p['_eyr']=_p['year']
    if _p['type']=='ND':
        _p['_ft']=True; _p['_grp']='ND'; _p['_eff']=min(99,_p['pick'] or 99)
    elif _p['type']=='RD':
        _p['_ft']=True; _p['_grp']='RD'; _p['_eff']=min(99,_NDC.get(_p['year'],75)+(_p['pick'] or 15))
    else:                                                     # pickless entry mechanism
        _p['_ft']=False; _p['_grp']=_p['type']; _p['_eff']=75   # placeholder; replaced by pick-equivalent after PVC
# cohort = national draft + first-time RD only (the ND and its extension). MSD/SSP are separate drafts, excluded here.
hist=[p for p in data if p.get('_ft') and p.get('_grp') in ('ND','RD') and 2003<=p['year']<=2021 and p['pos'] in GRP]  # 2003 lower bound (Luke cont.12): folds in the 2003-2005 cohorts; scores comparable at matched experience (no era drift), only ~1% miss a pre-2005 debut season
# --- PVC-pool-only exclusion + slide-up (Luke): players flagged _pvc_exclude are dropped from the PICK-CURVE builders
# (build_pvc / build_pvc_v34 / _natcv34) ONLY; they stay in hist for BASEPK_REG, establishment, and forward valuation,
# so the forward/Now board is byte-identical and they still appear. In the same draft year, remaining players slide UP
# to fill each vacated slot (curve attribution only -- stored pick/effpk untouched). Uses _epk in the curve pools only.
from collections import defaultdict as _dd
_pvc_excl_eff=_dd(list)
for _p in hist:
    if _p.get('_pvc_exclude'): _pvc_excl_eff[_p['year']].append(effpk(_p))
for _p in hist:
    if not _p.get('_pvc_exclude') and _p['year'] in _pvc_excl_eff:
        _e=effpk(_p); _p['_pvc_eff']=_e-sum(1 for _x in _pvc_excl_eff[_p['year']] if _x<_e)
def _in_pvc(p): return not p.get('_pvc_exclude')          # PVC-curve pool membership (forward board unaffected)
def _epk(p):    return p.get('_pvc_eff', effpk(p))         # slid effective pick, curve attribution only
def _rw(y):                                  # v2.1: equal weighting (recency shown immaterial; reverted by request)
    return 1.0
BPK={}; POOL={}; MIX={}
from collections import Counter
for b in range(NB):
    grp=[p for p in hist if bandof(p['pick'])==b]
    cc=Counter(GRP[p['pos']] for p in grp); MIX[b]={g:cc.get(g,0)/len(grp) for g in sorted(set(GRP.values()))}
    for g in sorted(set(GRP.values())):
        pw=[(pkbest(p),_rw(p['year'])) for p in grp if GRP[p['pos']]==g and pkbest(p) is not None]
        if len(pw)>=4: BPK[(g,b)]=float(np.average([x[0] for x in pw],weights=[x[1] for x in pw]))
    aw=[(pkbest(p),_rw(p['year'])) for p in grp if pkbest(p) is not None]
    POOL[b]=float(np.average([x[0] for x in aw],weights=[x[1] for x in aw])) if aw else 75
# position-anchored, monotone baseline peak: a later pick can't out-baseline an earlier one (kills small-sample inversions),
# and thin bands scale a reliable same-position band by the all-position band gradient instead of borrowing the all-position LEVEL.
BASEPK_REG={}
for g in sorted(set(GRP.values())):
    rel={b:BPK[(g,b)] for b in range(NB) if (g,b) in BPK}
    row=[]
    for b in range(NB):
        if b in rel: row.append(rel[b])
        elif rel:
            b0=min(rel,key=lambda x:abs(x-b)); row.append(rel[b0]*(POOL[b]/POOL[b0]))
        else: row.append(POOL[b])
    for b in range(1,NB): row[b]=min(row[b],row[b-1])   # v3.4 basepk de-bias: clamp ALL bands (was 1..5) -> a later pick can never out-baseline an earlier one (kills the late-pick survivorship spike; fixes Xerri-type)
    for b in range(NB): BASEPK_REG[(g,b)]=row[b]
def basepk(g,b): return BASEPK_REG.get((g,b)) or POOL.get(b) or bandpeak(g,b)
BAND_ANCHOR=PMD['BAND_ANCHOR']
def bandcoord(pk):
    if pk<=BAND_ANCHOR[0]: return 0.0
    if pk>=BAND_ANCHOR[-1]: return float(NB-1)
    for _i in range(NB-1):
        if BAND_ANCHOR[_i]<=pk<=BAND_ANCHOR[_i+1]:
            return _i+(pk-BAND_ANCHOR[_i])/(BAND_ANCHOR[_i+1]-BAND_ANCHOR[_i])
    return float(NB-1)
def basepk_c(g,pk):
    fb=bandcoord(pk); lo=int(fb); hi=min(NB-1,lo+1); f=fb-lo
    return (1-f)*basepk(g,lo)+f*basepk(g,hi)
def expected_c(g,pk,s):
    fb=bandcoord(pk); lo=int(fb); hi=min(NB-1,lo+1); f=fb-lo
    return (1-f)*expected(g,lo,s)+f*expected(g,hi,s)
CAPT_GAIN=0.35; CAPT_EXP=1.25; CAPT_CAP=18.0
def capt_prem(lev):
    over=max(0.0,lev-CAPT_THRESH)
    if over<=0: return 0.0
    cb=CAPT_GAIN*over**CAPT_EXP
    return cb*CAPT_CAP/(CAPT_CAP+cb)
GRACE={'KEY_FWD':2.5,'KEY_DEF':2.5,'RUC':2.5,'MID':1.0,'GEN_DEF':1.0,'GEN_FWD':1.0}
LOS_C=0.16; LOS_P=1.82                 # progressive: gentle yr2 ~.85, steepening (yr3~.57 yr4~.31 yr5~.16)
def los(p): return AGE_REF-p['year']
def los_decay(p):
    g=GRP[p['pos']]; s=los(p); over=max(0.0,s-GRACE.get(g,1.0))
    return math.exp(-LOS_C*over**LOS_P)   # yr1 -> pick value (debut signal deferred to next version)
# ---- model core ----
STBL=False                                   # SCALE-anchor mode: project on a stable (v18-equivalent) basis
RW_S={2026:2.0,2025:1.0,2024:0.4,2023:0.2}
def level_stable(p):
    n=d=0
    for r in p['scoring']:
        w=RW_S.get(r['year'],0)
        if w and r['games']>=2: n+=r['avg']*r['games']*w; d+=r['games']*w
    return n/d if d else None
SPIKE_CAP={'KEY_DEF':0.60}             # position cap on improving-form confidence (default 0.83). KEY_DEF spikes empirically revert (study: ~0.55 retention vs ~0.84 elsewhere); back-test-validated. Knob: other positions overridable for research.
ROLE_HC_MAX=0.07                       # role-decay: max level haircut to a past-peak veteran whose current role+output have collapsed (filtered <3g season). Tuned so an O'Brien-class case lands ~1/3 down on value.
_SG={}
def _season_games():                   # games of the season leader in BASE_REF (season-progress proxy); robust as the year fills in
    if BASE_REF not in _SG:
        _SG[BASE_REF]=max([r['games'] for _p in data for r in _p['scoring'] if r['year']==BASE_REF] or [22])
    return _SG[BASE_REF]
def _role_decay_hc(p,baseline):        # O'Brien rule: a past-peak player who's been dropped on ability (role collapsed, output cratered), not injury
    if baseline is None: return 0.0
    if _season_games() < 7: return 0.0                            # dormant until the season-leader has 7 games (rounds 1-6 too noisy)
    g=GRP[p['pos']]; a_=_age_at(p,BASE_REF)
    if a_ < PEAK_AGE[g]+1: return 0.0                              # not past peak -> spares young cameos (McCabe/Hardeman etc.)
    cur=next((r for r in p['scoring'] if r['year']==BASE_REF),None)
    if not cur or not (1<=cur['games']<3): return 0.0             # only the filtered sub-3-game current season; >=3g already shows in level_demo
    if cur['games']/max(_season_games(),1) >= 0.35: return 0.0    # role didn't actually collapse
    drop=clamp((baseline-cur['avg'])/baseline,0.0,1.0)
    if drop < 0.30: return 0.0                                     # output not far below baseline -> spares elite cameos (Gulden 2g@112.5)
    return clamp(ROLE_HC_MAX*drop,0.0,ROLE_HC_MAX)
def level_demo(p):                     # demonstrated form at BASE_REF (the true now); scoring truncated to <=BASE_REF
    if STBL: return level_stable(p)
    sc=[(r['year'],r['avg'],r['games']) for r in p['scoring'] if r['year']<=BASE_REF]
    qs=sorted([(y,a,gm) for (y,a,gm) in sc if gm>=3])
    if not qs: return None
    ly,la,lg=qs[-1]
    # thin-prior MERGE: a sub-3-game CURRENT-year cameo folds into the most-recent qualifying season (kept as that
    # season's games) so those games COUNT (up or down) instead of being dropped by the >=3 filter. Transient by
    # design: once the live season reaches 3 games it becomes its own qualifying season and these games pull back out.
    cur=[(y,a,gm) for (y,a,gm) in sc if y==BASE_REF and 0<gm<3]
    if cur and ly<BASE_REF:
        _ca,_cg=cur[0][1],cur[0][2]; la=(la*lg+_ca*_cg)/(lg+_cg); lg=lg+_cg
    if len(qs)==1: return la
    pn=pd=0
    for (y,a,gm) in qs[:-1]:
        w=(0.60**(ly-y))*min(gm,18)*(0.25 if gm<8 else 1.0); pn+=a*w; pd+=w   # prior: recency-weighted, tiny samples drowned
    prior=pn/pd if pd else la; growth=la-prior; base=lg/16.0
    a_=_age_at(p,BASE_REF); pa_=PEAK_AGE[GRP[p['pos']]]; old=a_>pa_+3
    proven=sum(1 for (y,a,gm) in qs if gm>=10)>=4
    if proven and not old:                                   # robust baseline: a one-year spike is as much an outlier as a one-year dip
        rc=sorted(a for (y,a,gm) in qs[-4:]); n=len(rc); med=rc[n//2] if n%2 else (rc[n//2-1]+rc[n//2])/2.0
        baseline=0.5*prior+0.5*med
    else: baseline=prior
    # B1 late-breakout fix: a large, sustained step-up over a weak early base drags the median/prior
    # baseline below the demonstrated level. Raise baseline to the sustained run-mean (K=3, ratio>=1.4),
    # only-raise guard (never drags a steady star down). Lifts the Richards/Xerri/Pickett/Ash/Blakey cohort.
    _b1=[(y,a,gm) for (y,a,gm) in qs if gm>=10]
    if len(_b1)>=3:
        _run=_b1[-3:]; _pre=[a for (y,a,gm) in _b1 if y<_run[0][0]]
        _op=(sum(_pre)/len(_pre)) if _pre else prior; _rm=sum(a for (y,a,gm) in _run)/3.0
        if _op>0 and min(a for (y,a,gm) in _run)>_op and _rm/_op>=1.4: baseline=max(baseline,_rm)
    # thin-prior RECENCY-FLOOR: the most-recent season's games can never weigh LESS, per game, than older games.
    # Floor conf at the recent season's share of the recency-weighted game mass (recency decay -> a recent game
    # weighs MORE than an older one). Fixes the inversion where an equal-games older season out-weighted the recent one.
    _pmass=sum((0.60**(ly-y))*min(gm,18) for (y,a,gm) in qs[:-1])
    _cfloor=min(lg,18)/(min(lg,18)+_pmass) if (min(lg,18)+_pmass)>0 else 0.0
    if growth>=0:                                            # improving: trust the rise but temper (don't fully chase a partial-season jump)
        conf=base*(1.0+growth/40.0); cap=SPIKE_CAP.get(GRP[p['pos']],0.83)
        _gg=gfut(p)                                          # DPP STRIP: settled-future eligibility lifts the spike cap (was the dual-leg lift; Serong KDEF now-MID -> 0.83)
        if _gg: cap=max(cap,SPIKE_CAP.get(_gg,0.83))
        conf=max(conf,_cfloor)                               # recency-floor (binds only when the recent season is under-trusted vs the prior)
    elif old:                                                # older decline: likely real -> trust recent
        agef=clamp((a_-pa_)/6.0,0.0,1.0); conf=base*(0.60+0.60*agef); cap=0.92
    else: conf=base*0.30; cap=0.92                           # proven prime sudden drop -> likely a blip, regress to baseline
    conf=clamp(conf,0.20,cap)
    lvl=conf*la+(1-conf)*baseline
    return lvl*(1.0-_role_decay_hc(p,lvl))
def _agecurve(g,a):                    # interpolated fraction-of-peak from the per-position empirical curve
    c=AGE_CURVE.get(g)
    if not c: return 1.0
    lo,hi=min(c),max(c); a=max(lo,min(hi,a)); a0=int(math.floor(a)); f=a-a0
    return c[a0]*(1-f)+c.get(min(hi,a0+1),c[a0])*f
def _dev_advance(L,p):                  # roll demonstrated form from BASE_REF age to AGE_REF age along the dev curve
    if L is None: return None
    a0=_age_at(p,BASE_REF); a1=age(p)
    if a1==a0: return L                                         # identity at offset 0 -> vP0==v, present board untouched
    g=bnow(p); c0=_agecurve(g,a0); c1=_agecurve(g,a1)
    if c0<1e-6: return L
    cp=basepk_c(g,effpk(p))                                     # pedigree-implied peak (independent of L -> no recursion)
    w=clamp(p['games']/130.0,0.30,0.85)                        # own-form trust by sample size; back-test will tune
    L1=L + w*(L*(c1/c0-1.0)) + (1-w)*(cp*(c1-c0))              # blend the CHANGE (own arc vs pedigree catch-up); zero at offset 0
    return clamp(L1, L*0.5, L*1.6)                              # growth/decline guard
def level_now(p): return _LEVEL_OVR if _LEVEL_OVR is not None else _dev_advance(level_demo(p),p)
def latest_avg(p):
    sl=sorted([r for r in p['scoring'] if r['games']>=4],key=lambda r:r['year']); return sl[-1]['avg'] if sl else None
def best2(p):
    d=debut(p); s=sorted([r['avg'] for r in p['scoring'] if r['games']>=7 and r['year']>=d],reverse=True)[:2]; return float(np.mean(s)) if s else 0
REPL={'MID':80.1,'GEN_DEF':78.3,'RUC':78.5,'KEY_DEF':68.4,'GEN_FWD':70.9,'KEY_FWD':66.8}  # v3.3 derived (rl_replacement_derive.py): Rule-1 pool, kfru 0.5, GDEF/MID 50/50 @4.16/5.20, KDEF@2.0, GFWD@4.0, KFWD@2.0, RUC@1.64  [BAKE 2026-07-04: KEY_FWD REPL-1, 67.8->66.8, owner dial]
DELTAS={-8:.58,-7:.62,-6:.68,-5:.74,-4:.80,-3:.86,-2:.92,-1:.97,0:1.0,1:.99,2:.98,3:.96,4:.94,5:.91,6:.88,7:.84,8:.79,9:.73,10:.66,11:.58,12:.50,13:.42,14:.34}
def frac(a,pa): return DELTAS[max(-8,min(14,int(round(a-pa))))]
KAPPA=0.10;SCONV=30.0;LOWBASE=54.0;GAMMA=float(__import__('os').environ.get('RL_GAMMA','0.85'))  # 0.85=SCAR(concave); 1.0=VOR(linear) via RL_GAMMA env (for the SCAR-vs-VOR dual-column build)
S_SH=3.0
def comp(v): return v   # no compression (v2.0)
def posval(x): return S_SH*math.log(1+math.exp(min(x/S_SH,40.0)))   # position value above replacement
CAPT_THRESH=107.4; CAPT_M=116.0; CAPT_W=5.0   # captaincy line (slider); 2026-06-21 M6: last-5 rank-25 ~=107.4 (unbiased upload), was 108.0
def _pcap(a): return 1.0/(1.0+math.exp(-(a-CAPT_M)/CAPT_W))
def capt_bonus(level):
    if level<=CAPT_THRESH: return 0.0
    n=max(2,int(round(level-CAPT_THRESH))*2); h=(level-CAPT_THRESH)/n; ss=0.0
    for i in range(n+1): ss+=(0.5 if i in (0,n) else 1.0)*_pcap(CAPT_THRESH+i*h)
    return CAPT_GAIN*ss*h
def pedmix(pk): return 0.50+0.32*math.exp(-(pk-1)/9.0)
def clamp(x,a,b): return max(a,min(b,x))
LENS={'now':0.34,'bal':0.15,'fut':0.05}
LTILT=0.30; LTSPREAD=6.0           # lens = bounded (+/-30%) tilt around balanced, by age-vs-peak phase
def lens_tilt(p,lens):
    if lens=='bal': return 1.0
    g=bnow(p); phase=clamp((age(p)-PEAK_AGE[g])/LTSPREAD,-1.0,1.0)
    return clamp(1+LTILT*phase,0.7,1.3) if lens=='now' else clamp(1-LTILT*phase,0.7,1.3)
RWE={1:1.0,2:1.3,3:1.6,4:1.7,5:1.7}
def track_delta(g,pk,sr):
    num=den=tg=0
    for s,(a,gm,yr) in sr.items():
        if STBL and s>8: continue
        rec=1.0 if STBL else 0.78**(2026-yr)     # calendar recency: recent seasons govern the estimate
        w=RWE.get(s,1.7)*min(gm,22)*rec; num+=(a-expected_c(g,pk,s))*w; den+=w; tg+=gm
    return (num/den,tg) if den else (None,0)
def cohort_peak(g,pk,sr):
    delta,tg=track_delta(g,pk,sr)
    if delta is None: return None,0
    conf=clamp(tg/45.0,0,1); bb=0.60+(BETA_POS.get(g,0.95)-0.60)*conf
    return basepk_c(g,pk)+bb*delta+ICPT_POS.get(g,2.79)*conf, tg
def survival(b,delta,games):
    # Bust is already priced once in the pedigree curve (PVC carries 1-BUST_BAND); the band-average
    # washout must NOT be re-charged here. So the survival haircut applies ONLY to a player who is
    # tracking *below* his own bar (mult>1) -- an at-par or above-par player gets no extra bust tax.
    bp=BUST_BAND.get(b,0.15); mult=clamp(1.0-delta/20.0,0.4,1.6); fade=max(0.0,1-games/40.0)
    return 1-bp*max(0.0,mult-1.0)*fade
def proj_from_peak(g,lp,a,cur,lens,g0=None,fut=None,pre_hc=0.0):
    # g = SETTLED (future) position: drives PEAK_AGE, level trajectory, key-premium, runway.
    # g0 = year-0 (present) position for REPL; fut = years-1+ REPL blend [(pos,wt)]. Defaults reproduce single-position behaviour.
    pa=PEAK_AGE[g]; d=LENS[lens]; cl=cur if cur else lp*frac(a,pa); prod=0.0
    if g0 is None: g0=g
    if fut is None: fut=[(g,1.0)]
    for k in range(18):
        ag=a+k
        if ag>38 or frac(ag,pa)<0.42: break
        lev=lp*frac(ag,pa)
        if ag<=pa: lev=max(lev,cl)
        if k==0: lev=max(lev,cl)
        if k==0 and pre_hc>0 and BASE_REF==2026 and AGE_REF==2026: lev*=(1-pre_hc)  # B2 present-unavailability haircut (Now board only)
        base=lev+capt_prem(lev)
        if k==0: prod+=posval(base-REPL[g0])*21/((1+d)**k)
        else: prod+=sum(w*posval(base-REPL[gg]) for gg,w in fut)*21/((1+d)**k)
    if g in('KEY_FWD','KEY_DEF'): prod*=1.05
    runway=clamp((25-a)/6.0,0,1); elite=clamp((lp/PEAK[g]-0.97)/0.30,0,1); prod*=(1+runway*elite*PMAX)
    return prod
def prod_floor(p,lens='bal'):
    g=bnow(p); a=age(p); pa_=PEAK_AGE[g]; cur=level_now(p)
    if cur is None: return 0
    d=LENS[lens]; H=clamp((40-a)/3.0,1.0,3.0); prod=0.0; k=0
    while k<H:
        ag=a+k; wt=min(1.0,H-k)
        lev=cur*min(1.0, frac(ag,pa_)/max(frac(a,pa_),1e-6))
        if k==0 and p.get('_b2hc',0)>0 and BASE_REF==2026 and AGE_REF==2026: lev*=(1-p['_b2hc'])
        prod+=wt*posval(lev+capt_prem(lev)-REPL[g])*21/((1+d)**k); k+=1
    return val(prod)
# ===== cont.20: v4 LEARNED FORWARD-PROJECTION (peak_est spine) =====
# Replaces old blended cohort+demoPeak. Model = forward-realised best-3 (>=Y, completeness-weighted), bust-inclusive.
# Feeds BOTH production (player_raw->proj_from_peak) and the pedestal's `relative`. Lazy-loaded: needs sklearn at
# BUILD time only (shipped board is static HTML). Late-binds PVC (built at line ~503, after this def).
_V4MODEL=None; _BUSTPT=None; _V4PVC=None
_POSI={'MID':0,'GEN_DEF':1,'GEN_FWD':2,'KEY_DEF':3,'KEY_FWD':4,'RUC':5}
V4_SPIKE_RETAIN={'KEY_DEF':0.69}   # cont.20: pull v4 spike-excess toward baseline for UNCONFIRMED KEY_DEF spikes (v4 over-trusts +0.28; level_now SPIKE_CAP can't reach the projection). Dial-able; KEY_FWD off by default.
# cont.20: EXPLICIT unproven-floor (researched position x pick x tenure expected peak). Beats v4 on OUT-OF-SAMPLE
# GROUP calibration (4.8 vs 6.0 weighted cell bias) — v4 systematically OVER-projects piners (MID +12, generals +5).
# Blended into peak_est by games-played weight: unproven -> explicit floor; proven -> v4 (form). NOT double-count:
# one peak estimate blended (not summed), and prod_floor independently protects demonstrated production.
EXP_PEAK_BASE={'MID':60.5,'GEN_DEF':56.9,'GEN_FWD':49.6,'KEY_DEF':51.1,'KEY_FWD':44.7,'RUC':66.6}  # T=1 expected peak by pos (realised piner means)
EXP_RETAIN={  # position-specific pining decay normalized to T1 (smoothed monotone from realised outcomes): RUC/KEY_DEF slow-burn, MID/fwds steeper
 'RUC':[1.00,0.95,0.91,0.85],'KEY_DEF':[1.00,0.95,0.95,0.93],'MID':[1.00,0.92,0.83,0.65],
 'GEN_DEF':[1.00,0.96,0.92,0.88],'GEN_FWD':[1.00,0.90,0.88,0.83],'KEY_FWD':[1.00,0.95,0.85,0.80]}
EXP_PICK_SLOPE=-10.72; EXP_LOGREF=4.0073   # expected peak vs (log effpk - logref); negative = deeper pick projects lower
EXP_BLEND_GAMES=45.0    # career games at which v4 (form) fully replaces the explicit floor (dial-able knob)
def _explicit_peak(p,Y):
    pos=GRP.get(p['pos'])
    if pos not in EXP_PEAK_BASE: return None
    T=max(Y-debut(p)+1,1); ret=EXP_RETAIN[pos][min(T,4)-1]
    pe=EXP_PEAK_BASE[pos]*ret+EXP_PICK_SLOPE*(math.log(min(effpk(p),70))-EXP_LOGREF)
    return clamp(pe,30.0,105.0)
def _v4_init():
    global _V4MODEL,_BUSTPT,_V4PVC
    if _V4MODEL is None:
        import pickle as _pk
        _V4MODEL=_pk.load(open('peak_model_v4.pkl','rb'))['model']
        _BUSTPT=json.load(open('bust_prior_table.json'))
        _V4PVC=json.load(open('pvc_snapshot.json'))   # peak-model's TRAIN-TIME PVC feature (logPVC), FROZEN by design to break the SCALE<->PVC<->peak_est bootstrap cycle. This is NOT the live PVC and must NOT track it: build_peak_model_v4.py trained the pickle on THIS PVC (see its co-emit of pvc_snapshot.json); feeding the live (post-bake) PVC here would be train/serve skew. Pinned + stamped read-only (Phase-4 disposition, DPP-strip build); regenerated only by the peak-model build.
def _v4_bp(po,pk): return _BUSTPT[po][str(min(max(int(round(pk)),1),70))]
def _v4_best(ss,n):
    a=sorted([x['avg'] for x in ss if x['games']>=6],reverse=True)[:n]; return float(np.mean(a)) if a else None
def _v4_age(p,Y):
    by=p.get('_by'); return (Y-by) if by else (Y-(debut(p)-18))
def _v4_feats(p,Y):
    d=debut(p); pos=GRP[p['pos']]; ep=min(effpk(p),70); T=Y-d+1
    sub=[x for x in p['scoring'] if x['year']<=Y]; gg=sum(x['games'] for x in sub); nss=len([x for x in sub if x['games']>=6])
    b2=_v4_best(sub,2); b1=_v4_best(sub,1); maxg=max([x['games'] for x in sub],default=0)
    rs=[x for x in sub if x['games']>=6][-2:]
    recent=float(np.average([x['avg'] for x in rs],weights=[x['games'] for x in rs])) if rs else 0
    last=[x for x in sub if x['year']==Y]; la=last[0]['avg'] if last else 0; lg=last[0]['games'] if last else 0
    early=sum(x['games'] for x in sub if x['year']-d+1<=2); seq=[x['avg'] for x in sub if x['games']>=6]; slope=(seq[-1]-seq[0]) if len(seq)>1 else 0.0
    bestyr=max([x['year'] for x in sub if x['games']>=6 and x['avg']==(b1 or -1)],default=Y); ysb=Y-bestyr
    return [np.log(_V4PVC[str(ep)]),ep,_POSI[pos],b2 or 0,b1 or 0,recent,la,lg,gg,nss,maxg,early,slope,ysb,_v4_age(p,Y),T,_v4_bp(pos,ep)]
def _v4_draft_feat(p):
    pos=GRP[p['pos']]; ep=min(effpk(p),70); return [np.log(_V4PVC[str(ep)]),ep,_POSI[pos],0,0,0,0,0,0,0,0,0,0,0,_v4_age(p,debut(p)-1),0,_v4_bp(pos,ep)]
def _v4_spike_guard(p,Y,pe):           # KEY_DEF spike caution on the PROJECTION (level_now SPIKE_CAP is a separate path)
    r=V4_SPIKE_RETAIN.get(GRP.get(p['pos']))
    if not r: return pe
    ss=sorted([x for x in p['scoring'] if x['year']<=Y and x['games']>=6],key=lambda x:x['year'])
    if len(ss)<3: return pe             # need 2 prior seasons (baseline) + the spike
    base=(ss[-2]['avg']+ss[-3]['avg'])/2.0
    if base>=55 and ss[-1]['avg']>=1.30*base and pe>base: pe=base+r*(pe-base)   # unconfirmed (spike is latest >=6g season as-of Y)
    return pe
_PE_CACHE={}
def _pe_clear(): _PE_CACHE.clear()     # call after toggling V4_SPIKE_RETAIN or BASE_REF-independent state in tests
def peak_est(p):                       # cont.20: learned v4 forward-projection (MEMOIZED by (player,BASE_REF)); was blended cohort+demoPeak
    _k=(id(p),BASE_REF)
    if _k in _PE_CACHE: return _PE_CACHE[_k]
    g=gfut(p); ln=level_now(p); pk=effpk(p)
    cp,tg=cohort_peak(g,pk,srel(p))
    if cp is None: cp=basepk_c(g,pk)
    if ln is None: _PE_CACHE[_k]=cp; return cp   # no demonstrated level -> cohort prior (in-window 0-game players hit unpl_eq in value() before here)
    _v4_init(); Y=BASE_REF
    v4pe=float(_V4MODEL.predict([_v4_feats(p,Y)])[0]) if (Y-debut(p)+1)>=1 else float(_V4MODEL.predict([_v4_draft_feat(p)])[0])
    v4pe=_v4_spike_guard(p,Y,v4pe)
    exp=_explicit_peak(p,Y)
    if exp is not None:
        w=clamp(p.get('games',0)/EXP_BLEND_GAMES,0.0,1.0)   # unproven -> explicit floor; proven -> v4 (form)
        pe=(1.0-w)*exp+w*v4pe
    else:
        pe=v4pe
    _PE_CACHE[_k]=pe
    return pe
def player_raw(p,lens='bal'):
    g0 = bnow(p) if AGE_REF==BASE_REF else gfut(p)   # A2 (PARKED 4): on forward boards (AGE_REF>BASE_REF) the year-0 present has rolled to the future position, so its replacement bar uses gfut, not the present bucket
    return proj_from_peak(gfut(p),peak_est(p),age(p),level_now(p),lens,g0=g0,fut=futblend(p),pre_hc=p.get('_b2hc',0.0))
def pa(g): return PEAK_AGE[g]
# unplayed prospects: recent national/rookie draftees not yet debuted (valued on pedigree alone, like the old engine)
extra=[]
for p in data:
    if p['_grp'] in ('ND','RD') and p['year']>=2024 and p['pos'] in GRP and sum(r['games'] for r in p['scoring'])==0:
        q=dict(p); q['_unplayed']=True; extra.append(q)
def active(p):
    if p['pos'] not in GRP or p.get('_retired'): return False
    if p.get('_last_listed') is not None and p['_last_listed']<2026: return False  # delisted before 2026 -> off Now (recalled onto back-boards)
    if p.get('_unplayed') or p.get('_force_active'): return True
    played=any(r['games']>=1 for r in p['scoring'])
    recent=p.get('_has26') or any(r['year']>=2024 for r in p['scoring']) or p['year']>=2024
    return played and recent
players=[p for p in (data+extra) if active(p)]
def _dkey(p): return (p['key'] or slug(p['player']))+('|u' if p.get('_unplayed') and not p['key'] else '')
def _rich(p): return (-(p['year'] or 9999), len(p['scoring']), 1 if p.get('pick') else 0)  # collapse duplicate-key groups to the EARLIEST entry (original draft record); fuller-history/real-pick as tiebreak
_best={}; _order=[]
for p in players:
    k=_dkey(p)
    if k not in _best: _order.append(k); _best[k]=p
    elif _rich(p) > _rich(_best[k]): _best[k]=p     # prefer fuller-history / real-pick record over a thin traded-club row
players=[_best[k] for k in _order]
played=[p for p in players if not p.get('_unplayed')]
STBL=True
ref=np.percentile([player_raw(p,'bal') for p in played],99); SCALE=7000/ref**GAMMA   # anchor on stable basis
STBL=False
for p in played: p['_pr']=player_raw(p,'bal')
val=lambda r: round(SCALE*r**GAMMA) if r>0 else 0
# ---- UNIFIED pick value: expected baseline draftee, position-mix + survival weighted, same currency ----
def pick_raw(k,lens='bal'):
    b=bandof(k); s=0
    for g,w in MIX[b].items():
        if w<=0: continue
        s+=w*proj_from_peak(g, basepk(g,b), 19, None, lens)
    return s*(1-BUST_BAND.get(b,0.15))
# value-based pick curve: recency-weighted MEAN PEAK VALUE per pick, monotone-regularised
def peakval(p):
    g=GRP[p['pos']]; pk=pkbest(p); ep=effpk(p)
    if pk is None: return val(pick_raw(ep))*0.25
    return val(proj_from_peak(g,pk,PEAK_AGE[g],pk,'bal'))*clamp((pk/max(basepk_c(g,ep),40.0))**2.2,0.40,3.0)
def _sgn(x): return (x>0)-(x<0)
def _edge(h0,h1,d0,d1):
    m=((2*h0+h1)*d0-h0*d1)/(h0+h1)
    if _sgn(m)!=_sgn(d0): m=0.0
    elif _sgn(d0)!=_sgn(d1) and abs(m)>3*abs(d0): m=3*d0
    return m
def _pchip(xs,ys,xq):
    n=len(xs); h=[xs[i+1]-xs[i] for i in range(n-1)]; dl=[(ys[i+1]-ys[i])/h[i] for i in range(n-1)]
    m=[0.0]*n
    m[0]=_edge(h[0],h[1],dl[0],dl[1]) if n>2 else dl[0]
    m[-1]=_edge(h[n-2],h[n-3],dl[n-2],dl[n-3]) if n>2 else dl[-1]
    for i in range(1,n-1):
        if dl[i-1]*dl[i]<=0: m[i]=0.0
        else:
            w1=2*h[i]+h[i-1]; w2=h[i]+2*h[i-1]; m[i]=(w1+w2)/(w1/dl[i-1]+w2/dl[i])
    out=[]
    for x in xq:
        i=0
        while i<n-2 and x>xs[i+1]: i+=1
        t=(x-xs[i])/h[i]; t2=t*t; t3=t2*t
        out.append((2*t3-3*t2+1)*ys[i]+(t3-2*t2+t)*h[i]*m[i]+(-2*t3+3*t2)*ys[i+1]+(t3-t2)*h[i]*m[i+1])
    return out
ALPHA=0.6                                          # risk-aversion dial for pick curve (lower = more risk-averse)
def _ce(vals,al):
    v=np.array([max(x,1.0) for x in vals]); return float((np.mean(v**al))**(1.0/al))
def build_pvc(alpha):
    raw=[float('nan')]*99
    for _k in range(1,100):
        vs=[peakval(p) for p in hist if _in_pvc(p) and abs(_epk(p)-_k)<=4]
        if vs: raw[_k-1]=_ce(vs,alpha)
    for _i in range(99):
        if raw[_i]!=raw[_i]: raw[_i]=raw[_i-1] if _i else 5000.0
    raw=[float(round(x)) for x in raw]                # snap to int so iso pooling is language-stable
    vv=[-v for v in raw]; idx=[[i] for i in range(99)]; i=0       # weighted-equal isotonic (decreasing)
    while i<len(vv)-1:
        if vv[i]>vv[i+1]+1e-9:
            nv=(vv[i]*len(idx[i])+vv[i+1]*len(idx[i+1]))/(len(idx[i])+len(idx[i+1]))
            vv[i]=nv; idx[i]+=idx[i+1]; del vv[i+1]; del idx[i+1]; i=max(0,i-1)
        else: i+=1
    iso=[0.0]*99
    for v,ix in zip(vv,idx):
        for j in ix: iso[j]=-v
    kx=[];ky=[];i=0                                              # PCHIP through plateau centres -> smooth, strict
    while i<99:
        j=i
        while j+1<99 and abs(iso[j+1]-iso[i])<1e-6: j+=1
        kx.append((i+j)/2.0); ky.append(iso[i]); i=j+1
    if kx[0]>0: kx=[0.0]+kx; ky=[iso[0]]+ky
    if kx[-1]<98: kx=kx+[98.0]; ky=ky+[iso[-1]]
    sm=_pchip(list(kx),list(ky),list(range(99)))
    for i in range(1,99): sm[i]=min(sm[i],sm[i-1]-1)
    return {k:max(210,int(round(sm[k-1]))) for k in range(1,100)}
# ============================================================================
# v3.4 PICK-VALUE CURVE (shipped 2026-06-20; the "R-0 proposal", locked by Luke).
# Replaces the legacy build_pvc above (kept for reference + the scale anchor). Method:
#   MEASURE  : posval(best2 + captaincy - REPL), busts -> 0   (NO bust floor, NO survivor clamp)
#   RISK     : tiered CE alpha PVC_ALPHA_LO->HI (0.6 at pick1 -> 0.8 cheap end, flat after pick 50)
#   SMOOTHER : varying-bandwidth local-linear (W 3 at the steep top -> 9 in the noisy tail)
#   TOP      : parametric power-decay a*k^b fit to picks 1-8, blended into loclin below ~pick 12
#   MONOTONE : light isotonic (PAVA) final pass -> non-increasing (plateaus allowed)
#   SCALE    : posval-VOR units mapped to SCAR by anchoring the pooled top band (picks 1-3) to the
#              legacy realised value -> preserves the board's top; players (forward model) untouched.
# Set PVC_REPL_BUF=5 for the R-5 (cheap-end-propped) variant. Full rationale: HANDOVER cont.(10).
# ============================================================================
PVC_ALPHA_LO, PVC_ALPHA_HI = 0.6, 0.8     # tiered risk dial for the pick curve (cost-tiered CE)
PVC_REPL_BUF = 0                          # replacement buffer: 0 = R-0 (shipped); 5 = R-5 (cheap end propped)
def _ce0(vals,al):                        # CE flooring busts at 0 (legacy _ce floors at 1, wrong for busts->0)
    v=np.array([max(x,0.0) for x in vals]); return float((np.mean(v**al))**(1.0/al)) if len(v) else 0.0
def _nv_bwd(p):                           # v3.4 backward per-pick value: posval-VOR on best2, busts -> 0
    b2=best2(p)
    return posval(b2+capt_prem(b2)-(REPL[GRP[p['pos']]]-PVC_REPL_BUF)) if b2>0 else 0.0
def _alpha_pvc(k): return PVC_ALPHA_LO+(PVC_ALPHA_HI-PVC_ALPHA_LO)*min(k-1,49)/49.0
def _loclin1(series,k,W,N):               # weighted local-linear fit over a 1..N series, evaluated at k
    pts=[(j+1,series[j],(W+1-abs(j+1-k))) for j in range(N) if abs(j+1-k)<=W and series[j]==series[j]]
    Wt=sum(w for *_,w in pts); xb=sum(w*x for x,_,w in pts)/Wt; yb=sum(w*y for _,y,w in pts)/Wt
    sxx=sum(w*(x-xb)**2 for x,_,w in pts)
    if sxx<1e-9: return yb
    b=sum(w*(x-xb)*(y-yb) for x,y,w in pts)/sxx
    return (yb-b*xb)+b*k
def build_pvc_v34():
    N=99
    raw=[float('nan')]*N                                          # 1. raw band value, new measure, tiered alpha, +-4
    for k in range(1,N+1):
        vs=[_nv_bwd(p) for p in hist if _in_pvc(p) and abs(_epk(p)-k)<=4]
        if vs: raw[k-1]=_ce0(vs,_alpha_pvc(k))
    for i in range(N):
        if raw[i]!=raw[i]: raw[i]=raw[i-1] if i else 0.0
    Wf=lambda k:int(round(3+6*min(k-1,60)/60.0))                  # 2. varying-bandwidth local-linear (3 top -> 9 tail)
    llv=[_loclin1(raw,k,Wf(k),N) for k in range(1,N+1)]
    kf=np.arange(1,9); yf=np.array([max(raw[i],1e-6) for i in range(8)])   # 3. parametric power top, fit to picks 1-8
    _B,_lA=np.polyfit(np.log(kf),np.log(yf),1); _A=math.exp(_lA)
    par=[_A*(k**_B) for k in range(1,N+1)]
    blend=[par[k-1] if k<=6 else llv[k-1] if k>=12 else                    # blend parametric top into loclin below
           ((12-k)/6.0)*par[k-1]+(1-(12-k)/6.0)*llv[k-1] for k in range(1,N+1)]
    vv=[-t for t in blend]; idx=[[i] for i in range(N)]; i=0     # 4. light isotonic (decreasing) -> monotone
    while i<len(vv)-1:
        if vv[i]>vv[i+1]+1e-9:
            m=(vv[i]*len(idx[i])+vv[i+1]*len(idx[i+1]))/(len(idx[i])+len(idx[i+1]))
            vv[i]=m; idx[i]+=idx[i+1]; del vv[i+1]; del idx[i+1]; i=max(0,i-1)
        else: i+=1
    iso=[0.0]*N
    for v,ix in zip(vv,idx):
        for j in ix: iso[j]=-v
    legacy=build_pvc(ALPHA)                                     # 5. SCALE posval-VOR -> SCAR: anchor the pooled top
    legacy_top=float(np.mean([legacy[k] for k in (1,2,3)]))     #    band (picks 1-3) to the CURRENT board's top so the
    new_top=float(np.mean(iso[:3]))                             #    board scale is preserved (players already untouched);
    SCALE_PVC=legacy_top/new_top if new_top>0 else 1.0          #    v3.4 is then a pure SHAPE change. (legacy = old curve,
    pvc=[v*SCALE_PVC for v in iso]                              #    used for the anchor only.)
    for i in range(1,N): pvc[i]=min(pvc[i],pvc[i-1])             # 6. enforce non-increasing (plateaus allowed)
    return {k:max(210,int(round(pvc[k-1]))) for k in range(1,N+1)}
PVC=build_pvc_v34()
CURVE_H=1.0                            # curve HEIGHT multiplier (slider); 1.0 = natural CE shape (best/pick1~2.96)
PVC={k:max(210,int(round(v*CURVE_H))) for k,v in PVC.items()}
# ── PICK-1 ANCHOR (Luke, 2026-06-21): pick 1 = a fixed target; the WHOLE board (picks + players) scales to it.
#    Replaces the implicit "99th-pct player → 7000" anchor with an explicit, stable "pick 1 → RL_PICK1".
#    Everything scales linearly with SCALE, so one global factor preserves all relativities/trades.
_P1=float(__import__('os').environ.get('RL_PICK1','3000'))
BOARD_FACTOR=_P1/PVC[1]; SCALE=SCALE*BOARD_FACTOR            # SCALE reassigned → val() (late-binding) scales players too
PVC={k:int(round(v*BOARD_FACTOR)) for k,v in PVC.items()}
# --- de-plateau (Luke): the monotone pass pools noisy mid-curve bands to a flat run; ramp each interior flat run
#     linearly through its real endpoints so picks decline smoothly, leaving the genuine DEEP-TAIL floor flat
#     (runs starting at pick>=46 are the floor and stay flat). Mid-curve only; pure shape, anchor (pick1) untouched.
def _deplateau(P, start_before=46):
    P=dict(P); N=len(P); i=1
    while i<=N:
        j=i
        while j<N and P[j+1]==P[i]: j+=1
        if j>i and j<N and P[j+1]<P[i] and i<start_before:          # interior flat run with a lower neighbour, mid-curve
            hi=P[i-1] if i>1 else P[i]; lo=P[j+1]; span=j-(i-1)+1
            for t,k in enumerate(range(i,j+1),1): P[k]=int(round(hi+(lo-hi)*t/span))
        i=j+1
    for k in range(2,N+1): P[k]=min(P[k],P[k-1])                    # safety monotone
    return P
PVC=_deplateau(PVC)
SEASON_PROG=0.58                              # ~round 14 of 24 (mid-Jun 2026). knob: 0=preseason ... 1=season done
def _playsig(g): return 1-math.exp(-g/6.0)    # saturating establishment from senior games
def debut_factor(p):                          # step-1 debut signal on pick-anchored value; asymmetric by pick
    ep=effpk(p); s=los(p); cg=sum(r['games'] for r in p['scoring'])
    elapsed=clamp((s-1)+SEASON_PROG,0.0,1.6)                  # seasons of opportunity so far (season-aware)
    ref=0.58*min(1.0,elapsed)                                 # expected establishment by now (low mid-yr1)
    sig=_playsig(cg)-ref
    Apos=(0.05+0.30*math.exp(-((ep-34)/24.0)**2))*clamp(ep/14.0,0.30,1.0)*clamp((22-cg)/22.0,0.0,1.0)  # positive: damped for high picks AND fades as a real sample accrues
    Aneg=0.16+0.12*math.exp(-((ep-34)/30.0)**2)              # negative: meaningful across the board
    return clamp(1+(Apos if sig>=0 else Aneg)*sig, 0.78, 1.28)
SLIP_CAP=0.78; SLIP_REF=150.0; SLIP_CONF=12.0; SLIP_MAXLOS=3   # step-2: position-aware DOWNSIDE slip, developing players, sample-confident
def track_slip(dlt,games):                    # dlt = avg pts vs the player's own position+experience bar (track_delta)
    if dlt is None or dlt>=0: return 1.0      # on/above bar -> no slip (upside stays in prior/production: no double-count)
    raw=clamp(1+dlt/SLIP_REF, SLIP_CAP, 1.0)
    conf=clamp(games/SLIP_CONF,0.0,1.0)       # small samples slip only partially (don't over-read a handful of games)
    return 1-conf*(1-raw)
def base_prod(g,k): return proj_from_peak(g, basepk(g,bandof(k)), 19, None, 'bal')   # baseline draftee, that position/pick
# --- v2.3 asymmetric output tilt: lift overperformers fully, drag underperformers GENTLY & sustained-scaled ---
TILT_REF=16.0
GAIN_UP=0.45; W_UP=55.0; UP_MAX=0.75; TILT_HI=1.22     # upside (output lifts: faster, fuller)
GAIN_DN=0.75; W_DN=70.0; DN_MAX=0.85; TILT_LO=0.55    # downside (gentler, slower)
NBAD_REF=2.0; SUS_MIN=0.35                             # sustained below-par scaler (years tracking behind)
def _fa(a,pa): return DELTAS[max(-8,min(14,int(round(a-pa))))]
def sustained_below(p,g,ep):
    n=0
    for s,(av,gm,yr) in srel(p).items():
        if av < expected_c(g,ep,s)-1.0: n+=1
    return n
def out_tilt(p,g,ep):
    ln=level_now(p)
    if ln is None: return 1.0
    sr=srel(p); cs=max(sr) if sr else max(1,los(p))       # current career season
    sig=ln-expected_c(g,ep,cs)                            # output vs the season-stage expected bar (dev curve)
    if sig>=0:
        conf=clamp(p['games']/W_UP,0,UP_MAX)
        t=1.0+GAIN_UP*sig/TILT_REF*conf
    else:
        sus=clamp(sustained_below(p,g,ep)/NBAD_REF,SUS_MIN,1.0)   # 1 half-season barely drags; 2+ yrs behind drags hard
        conf=clamp(p['games']/W_DN,0,DN_MAX)*sus
        t=1.0+GAIN_DN*sig/TILT_REF*conf
    return clamp(t,TILT_LO,TILT_HI)
P_HOOK=None                            # v3.4: when set, P_HOOK(p) supplies the establishment-probability weight on the pedigree track for NOT-yet-established players (replaces the seasons-only `decay`); established players keep `decay`.
PROD_GATE='off'                        # cont.20: rigid establishment blend REMOVED (was 'blenddemo'); v4 projection replaces it. ORIG note: 'blenddemo' = games-weighted rescue-only floor + 2/3 blend toward fully-gated. Modes: 'off' | 'full'/'fulldemo' (straight) | 'blend'/'blenddemo' (2/3). demo = floor at max(pedestal, games-weighted demonstrated value); plain = floor at pedestal.
def established(p):                     # v3.4 establishment definition: 50 career games + one >=11-game season
    cg=sum(r['games'] for r in p['scoring']); bg=max([r['games'] for r in p['scoring']],default=0)
    return cg>=50 and bg>=11
def grp3(p):
    _g=GRP.get(p['pos']); return 'RUC' if _g=='RUC' else ('KEY' if _g in('KEY_DEF','KEY_FWD') else 'GEN')
def _durable(p):
    ys=sorted(r['year'] for r in p['scoring'] if r['games']>=16)
    return any((y+1) in ys for y in ys)
def _recent_starter(p):
    g25=next((r['games'] for r in p['scoring'] if r['year']==2025),0)
    g26=next((r['games'] for r in p['scoring'] if r['year']==2026),0)
    return g25>=16 or g26>=9
def brodie_sig(p):                      # Brodie role-reliability cut (ported onto the board 2026-06-21, was compute.py-only):
    ln=level_now(p)                     # non-ruck, 5+ seasons, NOT a recent starter, NEVER durable, level>=80 -> value x0.5
    return (grp3(p)!='RUC' and seasons(p)>=5 and not _durable(p) and not _recent_starter(p) and ln is not None and ln>=80)
def value(p,lens='bal'):
    ep=effpk(p); b=bandof(ep); decu=los_decay(p)
    unpl_eq=PVC[min(ep,70)]*decu*debut_factor(p)
    if p.get('_unplayed') and (debut(p)>AGE_REF or p.get('_pedonly')): return round(unpl_eq*lens_tilt(p,lens))   # pure pedigree for genuine pre-debut prospects (window not open) OR explicit draft-value (`_pedonly`, P inert by design); in-window 0-game players fall through to the P-gated branch so 0->1 games is continuous
    g=gfut(p)   # settled future position drives pedigree/form-delta/out-tilt (matches peak_est); prod_floor stays present
    if level_now(p) is None:                                          # 0-game but IN opportunity window (debut season+): P applies continuously (prospect-path RETIRED 2026-06-18); genuine pre-debut prospects hit the _unplayed branch above and keep pure pedigree
        Pz = 1.0 if P_HOOK is None else P_HOOK(p)
        return round(unpl_eq * Pz * lens_tilt(p,lens))
    surv=1.0   # cont.20: survival() REMOVED from value path (v4 subsumes the bust-tracking haircut; verified 11.8pt separation vs survival's <=9%)
    Pz = None if P_HOOK is None else P_HOOK(p)                # v3.4: establishment-P, computed ONCE; gates BOTH the production term (below) and the pedigree pedestal (decay_eff), each carrying P exactly once
    prod_v=val(player_raw(p,'bal'))*surv                      # anchor at balanced; lens is a bounded tilt below
    relative=clamp((peak_est(p)/max(basepk_c(g,ep),40.0))**2.2, 0.40, 3.0)
    # out_tilt CUT (cont.21): audited redundant with v4 — corr(out_tilt_sig, realised-v4)=-0.05, marginal R2=+0.001, coef after v4=-0.04. Same form double-count as the removed survival(). relative stays at the v4 pedigree multiplier.
    if g in('RUC','KEY_FWD','KEY_DEF') and age(p)<=22 and relative<1.0:   # v3.4 relative-floor: young key-pos debut can't drag the pedestal below the clean pick baseline; YEAR-SCALED (more chances seen -> less lift)
        _sc={1:1.0,2:0.8,3:0.5,4:0.2}.get(2026-p['year'],0.0); relative=relative+_sc*(1.0-relative)
    decay=max(0.0,1-(seasons(p)-1)/4.5)
    decay_eff = decay if Pz is None else min(decay, Pz)   # v3.4: establishment-P only ever PULLS DOWN (min) on the pedigree track; established players P=1 -> min=decay, untouched
    pedestal = PVC[min(ep,70)]*relative*surv*decay_eff
    pf = prod_floor(p,'bal')
    prod_full = max(prod_v, pf)                           # full production estimate: projection OR demonstrated-level floor, whichever is higher
    if Pz is not None and PROD_GATE!='off':                # v3.4 PRODUCTION-GATING. fully_gated = P*production + (1-P)*floor. floor = pedestal ('full'/'blend') OR a games-weighted demonstrated floor ('fulldemo'/'blenddemo') so survivors who banked games aren't stripped to the bare pick. 'full*'=straight; 'blend*'=Luke's 2/3 toward fully-gated.
        if PROD_GATE in ('fulldemo','blenddemo'):
            cred = min(1.0, p['games']/50.0); gfloor = max(pedestal, cred*pf + (1.0-cred)*pedestal)   # rescue-only: never below the pick's pedestal
        else:
            gfloor = pedestal
        fully_gated = Pz*prod_full + (1.0-Pz)*gfloor
        if PROD_GATE in ('full','fulldemo'):     prod_full = fully_gated
        elif PROD_GATE in ('blend','blenddemo'): prod_full = (1.0/3.0)*prod_full + (2.0/3.0)*fully_gated
    res=max(prod_full, pedestal)
    if brodie_sig(p): res*=0.5                            # Brodie role-reliability cut (now on the board; flows to convex/backward via value())
    return round(res*lens_tilt(p,lens))
# ---- PICK-EQUIVALENT for the no-slot entry mechanisms (MSD/SSP/Ireland/Unregistered/post-draft) ----
# "What national pick is an X player worth?" Build a national realised-career-value curve (no effpk
# dependence, same risk-averse pooling as the PVC), then invert it against each mechanism's pooled value.
def realized_cv(p):   # LEGACY helper, retained ONLY for rl_export's father-son/academy/next-gen overshoot panel
    pk=pkbest(p)
    if pk is None: return 0.0
    _g=GRP[p['pos']]; return float(val(proj_from_peak(_g,pk,PEAK_AGE[_g],pk,'bal')))
_natcv=[None]*100     # LEGACY national curve, retained for the export panel above; the PATHWAY board now uses _natcv34
for _k in range(1,100):
    _vs=[realized_cv(p) for p in data if p['_grp']=='ND' and (p['pick'] or 99) and abs((p['pick'] or 99)-_k)<=4 and p['pos'] in GRP]
    if _vs: _natcv[_k]=_ce(_vs,ALPHA)
for _k in range(1,100):
    if _natcv[_k] is None: _natcv[_k]=_natcv[_k-1] if _k>1 and _natcv[_k-1] else 300.0
_natcv34=[None]*100   # v3.4 (Luke cont.12): pathways measured backward THE SAME WAY as picks -- _nv_bwd (posval-VOR
for _k in range(1,100):   # on best2, busts->0) + tiered alpha, inverted against the v3.4 per-pick national curve (NOT legacy realized_cv).
    _vs=[_nv_bwd(p) for p in hist if _in_pvc(p) and abs(_epk(p)-_k)<=4]
    if _vs: _natcv34[_k]=_ce(_vs,_alpha_pvc(_k))
for _k in range(1,100):
    if _natcv34[_k] is None: _natcv34[_k]=_natcv34[_k-1] if _k>1 and _natcv34[_k-1] else _natcv34[1]
for _k in range(2,100):   # enforce non-increasing: a deeper pick can't realise MORE than a shallower one. The raw
    if _natcv34[_k]>_natcv34[_k-1]: _natcv34[_k]=_natcv34[_k-1]   # tail oscillates on tiny samples, which makes the inversion ill-conditioned; cumulative-min cleans it.
def _pick_equiv(v):
    best=99; bd=1e18
    for _k in range(1,100):
        if _natcv34[_k] is not None and abs(_natcv34[_k]-v)<bd: bd=abs(_natcv34[_k]-v); best=_k
    return best
PATH_LO=2003; PATH_ALPHA=PVC_ALPHA_HI       # same lower bound as the pick curve; pathways land in the cheap tail -> tail alpha (=0.8)
PICKEQ={}; MECH_STATS={}
_MECH_NAME={'MSD':'Mid-Season','SSP':'SSP / pre-season supp.','IRE':'Ireland','UNR':'Unregistered',
            'PDA':'Post-draft Academy','PDN':'Post-draft Next-Gen','PDS':'Post-draft Scholarship'}
for _t in PICKLESS:
    _all=[p for p in data if p['type']==_t and p['pos'] in GRP and _cycle_year(p)>=PATH_LO]
    if not _all: continue
    _best=None                               # per-pathway MOST-FAVOURABLE upper cutoff (>=2021; later if it raises pooled value)
    for _cut in range(2021,2027):
        _coh=[p for p in _all if _cycle_year(p)<=_cut]
        if len(_coh)<8: continue
        _pl=_ce([_nv_bwd(p) for p in _coh],PATH_ALPHA)
        if _best is None or _pl>_best[0]: _best=(_pl,_cut,_coh)
    if _best is None:                        # tiny pathway -> full cohort
        _coh=_all; _pl=_ce([_nv_bwd(p) for p in _coh],PATH_ALPHA); _cut=max(_cycle_year(p) for p in _coh)
    else: _pl,_cut,_coh=_best
    eq=_pick_equiv(_pl); PICKEQ[_t]=eq
    played=[p for p in _coh if pkbest(p) is not None]
    MECH_STATS[_t]={'name':_MECH_NAME.get(_t,_t),'n':len(_coh),'played_n':len(played),'cutoff':_cut,
        'hit_rate':round(100*len(played)/len(_coh),1),
        'pooled_value':round(_pl),'pick_equiv':eq,
        'mean_career_avg':round(float(np.mean([pkbest(p) for p in played])),1) if played else None,
        'mean_career_games':round(float(np.mean([p['games'] for p in _coh])),1)}
# assign the mechanism pick-equivalent as the pedigree anchor for those players (production still differentiates them)
for p in data+extra:
    if p['type'] in PICKEQ: p['_eff']=PICKEQ[p['type']]
print('PICK-EQUIVALENTS:',{ _MECH_NAME.get(k,k):v for k,v in sorted(PICKEQ.items(),key=lambda x:x[1])})

# ==== ESTABLISHMENT-P (ported from compute.py 2026-06-21 -> SINGLE SOURCE OF TRUTH; the BOARD now applies it).
# The consuming machinery (PROD_GATE + the min(decay,Pz) line in value()) was already here but inert with P_HOOK=None.
# P personalises bust risk: a not-yet-established player's pedigree track + production are weighted by P(establish).
# Built on REAL types (runs BEFORE the present-identity overrides below, exactly as compute.py did). ====
pgrid.build(data, GRP, debut)           # build the establishment surface from THIS engine's data (no rl_model import inside pgrid)
def entry_age(p): return (debut(p)-1)-by(p)
_PB=[(1,3),(4,6),(7,9),(10,13),(14,18),(19,24),(25,31),(32,39),(40,48),(49,58),(59,99)]
_cohP=[p for p in data if p.get('_grp') in('ND','RD') and debut(p)<=2019 and p['pos'] in GRP]
def _brateP(lo,hi):
    _gg=[p for p in _cohP if lo<=effpk(p)<=hi]
    return (sum(established(p) for p in _gg)/len(_gg), len(_gg)) if _gg else (0.0,0)
_brawP=[_brateP(lo,hi) for lo,hi in _PB]
def _pavaP(vals,wts):                    # weighted isotonic (monotone non-increasing establishment rate by pick)
    b=[[vals[i]*wts[i],wts[i],i,i] for i in range(len(vals))]; i=0
    while i<len(b)-1:
        if b[i][0]/b[i][1] < b[i+1][0]/b[i+1][1]-1e-9:
            b[i][0]+=b[i+1][0]; b[i][1]+=b[i+1][1]; b[i][3]=b[i+1][3]; del b[i+1]; i=max(0,i-1)
        else: i+=1
    f=[0.0]*len(vals)
    for blk in b:
        for k in range(blk[2],blk[3]+1): f[k]=blk[0]/blk[1]
    return f
_pfitP=_pavaP([r for r,_ in _brawP],[max(1,n) for _,n in _brawP]); _pctrP=[(lo+hi)/2.0 for lo,hi in _PB]
def _pick_curveP(ep):                    # smooth monotone-interpolated establishment rate at this pick (no band cliffs)
    if ep<=_pctrP[0]: return _pfitP[0]
    if ep>=_pctrP[-1]: return _pfitP[-1]
    for i in range(len(_pctrP)-1):
        if _pctrP[i]<=ep<=_pctrP[i+1]:
            t=(ep-_pctrP[i])/(_pctrP[i+1]-_pctrP[i]); return _pfitP[i]+t*(_pfitP[i+1]-_pfitP[i])
    return _pfitP[-1]
_ovP=sum(established(p) for p in _cohP)/len(_cohP); _grpoffP={}     # position offset = group est rate / overall (capped)
for _gv in set(GRP.values()):
    _gg=[p for p in _cohP if GRP.get(p['pos'])==_gv]
    _grpoffP[_gv]=(sum(established(p) for p in _gg)/len(_gg))/_ovP if _gg else 1.0
def pick_prior(p): return float(np.clip(_pick_curveP(effpk(p))*_grpoffP.get(GRP.get(p['pos']),1.0),0.05,0.97))
_PATHK=12; _pfloorP=_pfitP[-1]; _pathpr={}                          # each pathway its own pool, shrunk to the late-pick floor when thin
for _t in ['MSD','SSP','IRE','UNR','PDA','PDN','PDS']:
    _gp=[p for p in data if p.get('type')==_t and debut(p)<=2022 and p['pos'] in GRP]
    if _gp:
        _r=sum(established(p) for p in _gp)/len(_gp); _w=len(_gp)/(len(_gp)+_PATHK); _pathpr[_t]=_w*_r+(1-_w)*_pfloorP
def P_estab(p):
    if established(p): return 1.0
    g3=grp3(p); Y=2026-debut(p)+1; d=debut(p)            # CLOCK FIX: Y = season ordinal (1=debut season)
    def _gm(r): return r['games']   # MSD debut-season game boost SCRUBBED 2026-07-05 (was x2.0 half-season standardisation)
    Gn=sum(_gm(r) for r in p['scoring'] if d<=r['year']<2026)+(sum(r['games'] for r in p['scoring'] if r['year']==2026)/SEASON_PROG)
    base=pgrid.Praw(g3,Y,Gn)*pgrid.mat_mult(entry_age(p),Gn)         # smoothed surface x mature-entry discount
    prior=_pathpr[p['type']] if p['type'] in _pathpr else pick_prior(p)
    base=base+(1-SEASON_PROG)*max(0.0,prior-base)        # mid-season benefit-of-doubt toward the pick/pathway prior
    return float(np.clip(base,0.10,0.99))
P_HOOK=None                            # cont.20: establishment-P gating DEACTIVATED (xP_establish deleted); v4 projection replaces it. (was: P_HOOK=P_estab)

# ---- PRESENT-IDENTITY OVERRIDES (Luke ground-truth, 2026-06-18): value each player's CURRENT self as a fresh
# entry via the named window. DB history is untouched -- real type/year drove every cohort/pool surface, built
# ABOVE this line; only these players' pedigree anchor + entry clock + pathway reset. SINGLE SOURCE OF TRUTH here
# so the EXPORTED BOARD inherits it (this previously lived only in compute.py, so the shipped board never applied
# it -> Keane/McAndrew anchored on raw IRE/MSD; Perez/Hall-Kahan kept their raw entry clock). Forward = SSP fix.
PRESENT_ID_OVERRIDES={
    "Flynn Perez":    ('SSP', 2025),   # 2025 SSP window
    "Hugo Hall-Kahan":('MSD', 2026),   # 2026 mid-season draft
    "Lachlan McAndrew":('SSP', 2024),  # 2024 SSP window
    "Mark Keane":     ('SSP', 2022),   # 2022 SSP window
}
for _p in data:
    _o=PRESENT_ID_OVERRIDES.get(_p.get('player'))
    if _o: _p['type'],_p['year']=_o; _p['_grp']=_o[0]; _p['_eff']=PICKEQ[_o[0]]

# B2: current-season unavailability haircut (present component, Now board only). Established player
# (>=3 seasons, recent peak>=90) with 0 games in 2026 and season >1/3 done -> age-banded present haircut:
# <27 8.8%, 27-29 3.9%, 30+ 0 (age curve already prices 30+ decline). Transient -> next build's return data supersedes it.
for _p in data+extra: _p['_b2hc']=0.0
def _b2band(_a): return 0.088 if _a<27 else (0.039 if _a<30 else 0.0)
if SEASON_PROG>1.0/3.0:
    for _p in players:
        if _p.get('_unplayed') or _p.get('_retired'): continue
        _pre=[r for r in _p['scoring'] if r['year']<2026]
        if len(_pre)<3: continue
        _g26=next((r['games'] for r in _p['scoring'] if r['year']==2026),0)
        if _g26==0 and max(r['avg'] for r in _pre[-3:])>=90.0: _p['_b2hc']=_b2band(_age_at(_p,2026))
_pe_clear()   # FIX (cont.22): SCALE@436 memoised peak_est while pickless players still held the placeholder _eff (pick-equivalent isn't applied until L726). Clearing here, after all attributes are finalised and before the board build, makes pickless players price on their real pick-equivalent instead of the stale placeholder (e.g. Sharman 1147->303).
for p in players: p['_vpt']=value(p,'bal'); p['_v']=p['_vpt']   # _vpt = point value (GH integrand basis + JS live-recompute target); _v reset to convex below
players.sort(key=lambda p:-p['_v'])
# --- Phase-2 variance layer: E[value] over the projected level distribution x survival ---
# Calibrated from the back-test: level CoV ~0.23 young / ~0.18 vet (per 2yr); 2yr survival ~0.94 proven
# down to ~0.80 for low-evidence older players. At offset 0: sigma=0, survival=1 -> proj_value==value -> vP0==v.
_GHx=[-2.0201829,-0.9585725,0.0,0.9585725,2.0201829]; _GHw=[0.0199532,0.3936193,0.9453087,0.3936193,0.0199532]
_SQ2PI=math.sqrt(2.0); _SQPI=math.sqrt(math.pi)
def _cov_age(a): return 0.23 if a<=24 else 0.18
def _cov(p): return _cov_age(_age_at(p,BASE_REF)) + 0.12*clamp((90-p['games'])/90.0,0,1)  # thin sample -> wider level spread
def _upside_w(p): return clamp((31-_age_at(p,BASE_REF))/12.0,0.0,1.0)                 # convexity = upside option; applies pre/near-peak, fades to 0 by ~33
def _cliff_disc(p,off):                                                               # prices the cliff for OLD + LOW-evidence only (proven players ~untouched)
    a=_age_at(p,BASE_REF); g=p['games']
    return 1.0 - 0.42*clamp((a-28)/7.0,0,1)*clamp((150-g)/150.0,0,1)*(off/2.0)
PRESENT_VAR=0.25      # present-level sampling-uncertainty variance -> option value priced INTO present value (0.0 = old point value). SHIPPED 0.25: present is more certain than the 0.5 forward dispersion; see HANDOVER conservation note.
CVX_CAP=1.25          # cap on the present convexity multiplier (guards the value-floor threshold artifact for fringe straddlers)
def proj_value(p,off):
    global _LEVEL_OVR
    mu=_dev_advance(level_demo(p),p)
    if mu is None: return value(p,'bal')
    pt=value(p,'bal')
    var = PRESENT_VAR if off==0 else off/2.0          # off=0 carries present sampling uncertainty (option value); off>=1 = forward dispersion (unchanged)
    s=_cov(p)*math.sqrt(var)*_upside_w(p)*mu          # upside dispersion (convexity), gated to pre-peak + evidence
    if s<1e-6: base=value(p,'bal')
    else:
        Ev=0.0
        for x,w in zip(_GHx,_GHw):
            _LEVEL_OVR=max(1.0, mu+_SQ2PI*s*x); Ev+=w*value(p,'bal')                   # Gauss-Hermite E[value | level~N(mu,s)]
        _LEVEL_OVR=None; base=Ev/_SQPI
    if off==0 and pt>0: base=clamp(base, pt, pt*CVX_CAP)    # present option value: additive only (floor pt, cap pt*CVX_CAP); no cliff at off=0
    r=round(_cliff_disc(p,off)*base)                                                  # x cliff discount (old+uncertain only)
    if off==0 and pt>0: r=max(r, round(pt))                # FLOOR present value at the point: guards cliff/rounding from pushing cvx (=v/vpt) below 1.0 (premium is additive-only)
    return r
for off,key in ((0,'_vP0'),(1,'_vP1'),(2,'_vP2')):
    AGE_REF=BASE_REF+off
    for p in players: p[key]=proj_value(p,off)
AGE_REF=BASE_REF
# Present value now PRICES CONVEXITY (option value): _v = proj_value(0) = E[value | present-level uncertainty], capped. vP0==v by construction.
for p in players:
    p['_v']=p['_vP0']
    p['_cvx']=min(round(p['_v']/p['_vpt'],6), CVX_CAP) if p['_vpt']>0 else 1.0   # convexity multiplier in [1.0, CVX_CAP]; min() honours the documented cap (round(v)/round(vpt) could otherwise edge past it at low values)
players.sort(key=lambda p:-p['_v'])
import numpy as _np
_prem=[(p['_cvx']-1) for p in players if not p.get('_unplayed') and p['_vpt']>0]
_poolpt=sum(p['_vpt'] for p in players); _poolcx=sum(p['_v'] for p in players)
print('Phase-2 CONVEXITY into present value: pool +%.1f%%  median premium +%.1f%%  max +%.0f%% (cap %.0f%%)  | vP0==v by construction'
      %(100*(_poolcx/_poolpt-1),100*_np.median(_prem),100*max(_prem),100*(CVX_CAP-1)))
# --- Phase-2 BACKWARD board (vM1/vM2): re-value on KNOWN truncated data, NOT a projection. ---
# "Board as of end-(2026-N) season": value every player who was ON AN AFL LIST at end of year Y=2026-N, using
# data through Y only, de-aged to Y (BASE_REF=AGE_REF=Y so dev_advance no-ops -> pure value(), no leakage). The
# population INCLUDES players who have since retired -- the DB carries retired records (incl. the 2024/2025 leavers
# Luke folded in); they are recalled onto the -N board for the years they were active (collected in `back_extra`,
# exported as board-history-only rows that never appear on the Now/forward board). Frozen 2026 SCALE/PVC.
import copy as _copy
def _trunc_p(p, upto):
    q=_copy.deepcopy(p); q['scoring']=[r for r in p['scoring'] if r['year']<=upto]
    q['games']=sum(r['games'] for r in q['scoring']); return q
def _lastgameyr(p):
    ys=[r['year'] for r in p['scoring'] if r['games']>=1]; return max(ys) if ys else None
def _on_board(p, N):                                    # on an AFL list at end of year Y=2026-N?
    Y=2026-N
    if debut(p)>Y: return False                         # not yet debuted by end of year Y. ND/RD/SSP debut=year+1 (=> year>Y-1, unchanged); MSD is mid-season (debut=year) so it now sits on its OWN entry-year board (mirrors the Now board carrying the current-year MSD class)
    ll=p.get('_last_listed')
    if ll is not None: return p['year']<=Y and ll>=Y     # Luke ground-truth delisting year (overrides the games proxy both ways)
    ly=_lastgameyr(p)
    return (debut(p)<=Y<=debut(p)+1) if ly is None else (ly>=Y)    # unplayed prospect: ONLY within its initial-contract window (matches section-c {entry+1,+2}); fixes long-retired/no-scoring players (Watson/Maibaum/Mohr) being recalled onto every prior board. Played: still active through Y.
def _backval(p, N):
    global BASE_REF, AGE_REF
    if not _on_board(p, N): return None
    Y=2026-N; BASE_REF=AGE_REF=Y
    try: return proj_value(_trunc_p(p, Y), 0)             # convex (option value) at the year-Y snapshot, same as Now -> consistent lens across the slider
    finally: BASE_REF=AGE_REF=2026
for p in players:                                       # (a) active players: vM stored on their record
    p['_vM1']=_backval(p,1); p['_vM2']=_backval(p,2)
_act_keys=set(_dkey(p) for p in players); _rb={}        # (b) retired OR delisted-not-retired players active in 2024/2025: dedup + recall
for p in data:
    _delisted = p.get('_last_listed') is not None and p['_last_listed']<2026
    _valuable = (p['_grp'] in ('ND','RD')) or any(r['games']>=1 for r in p['scoring'])  # pedigree anchor or demonstrated form (else unvalued, same as Now)
    if not (p.get('_retired') or (_delisted and _valuable)) or p['pos'] not in GRP: continue
    k=_dkey(p)
    if k in _act_keys: continue
    if k not in _rb or _rich(p)>_rich(_rb[k]): _rb[k]=p
back_extra=[]
for k,p in _rb.items():
    vM1=_backval(p,1); vM2=_backval(p,2)
    if vM1 is None and vM2 is None: continue            # retired before 2024 -> on neither back-board
    p['_vM1']=vM1; p['_vM2']=vM2; p['_backonly']=True; p['_v']=None; back_extra.append(p)
# (c) unplayed ND/RD prospects: carry on the BACKWARD boards across the entry+1/entry+2 window (mirror of the
#     year>=2024 Now-shell), so -2 values the 2023 class the same way Now/-1 value the 2025/2024 classes. Bounded to
#     (board_year - entry) in {1,2}, so a prospect appears only within its initial-contract window and never leaks onto
#     Now (entry+3 = 3-yrs-no-games bust cutoff). Board-history-only rows (no _v) -> the active pool is unchanged.
_pool_keys=set(_dkey(q) for q in players)|set(_rb.keys())
for p in data:
    if p['pos'] not in GRP or p['_grp'] not in ('ND','RD'): continue
    if any(r['games']>=1 for r in p['scoring']): continue          # unplayed prospects only (played-then-cut handled by the recall loop above)
    if _dkey(p) in _pool_keys: continue
    e=p['year']
    vM1=_backval(p,1) if (2025-e) in (1,2) else None               # board -1 (Y=2025): 2023/2024 entries
    vM2=_backval(p,2) if (2024-e) in (1,2) else None               # board -2 (Y=2024): 2022/2023 entries
    if vM1 is None and vM2 is None: continue
    p['_vM1']=vM1; p['_vM2']=vM2; p['_backonly']=True; p['_v']=None; back_extra.append(p)
_nM1=sum(1 for q in players+back_extra if q.get('_vM1') is not None)
_nM2=sum(1 for q in players+back_extra if q.get('_vM2') is not None)
print('Phase-2 backward board: on-board -1=%d, -2=%d (active %d + retired-recalled %d)'%(_nM1,_nM2,len(players),len(back_extra)))
# --- backward-board CONSERVATION NORMALISATION (Luke; re-ported from rl_build) ---
# The raw backward board inflates (-1 ~1.12x, -2 ~1.22x): going back, every player is younger w/ more runway and the
# diluting intakes are gone. Scale each -N board by (now-total / back-total) over the SHARED active set so the board is
# conserved (-N ~1.00x) and a good player no longer shows a uniformly higher rating one year back. Recalled retirees
# (no _v) ride the same factor. Forward board stays raw/melting (not flagged); symmetrise on request.
for _key in ('_vM1','_vM2'):
    _shared=[q for q in players if q.get(_key) is not None and q.get('_v')]
    _bt=sum(q[_key] for q in _shared)
    _f=(sum(q['_v'] for q in _shared)/_bt) if _bt>0 else 1.0
    for q in players+back_extra:
        if q.get(_key) is not None: q[_key]=int(round(q[_key]*_f))
    print('  %s conservation factor x%.4f (raw board was x%.3f)'%(_key,_f,1.0/_f if _f else 0))
# --- AGE_REF seam (for the Phase-2 forward-board pass) ---
# The age clock (age/seasons/los) reads the module global AGE_REF (default 2026). To re-age the whole
# board to a shifted year, set AGE_REF and recompute value() per player, e.g.:
#     def values_at(off):
#         global AGE_REF; AGE_REF=2026+off
#         try: return [value(p,'bal') for p in players]
#         finally: AGE_REF=2026
# Calibration (PVC/SCALE/dev curve/cohort) stays fixed; only each player's age advances; demonstrated
# form (srel/recency) is unchanged. NOTE (verified this session): a pure clock-advance with NO projected
# development INVERTS the dynasty ranking (young pedigree assets crater as decay=1-(seasons-1)/4.5 fades
# their pick value with nothing to replace it; established older players rise). The forward board is only
# meaningful once Phase 2 projects development to offset that fade -> build the two together.
def pe(v):
    if v>PVC[1]: return '1+'
    for k in range(1,51):
        if PVC[k]<=v: return str(k)
    return '50+'
def rk(nm):
    cs=sorted([p for p in players if norm(nm) in norm(p['player']) and (p.get('_has26') or p['year']>=2023 or p.get('_unplayed'))],key=lambda p:-p['_v'])
    if not cs: cs=sorted([p for p in players if norm(nm) in norm(p['player'])],key=lambda p:-p['_v'])
    if not cs: return '%-20s NF'%nm
    p=cs[0]; return '%-20s #%-3d val%4d ~pk%-3s %-7s pk%2d %-3s'%(p['player'][:20],players.index(p)+1,p['_v'],pe(p['_v']),GRP[p['pos']],p['pick'],p['type'])
print('PVC:',{k:PVC[k] for k in [1,3,5,10,15,20,30,45]})
print('TOP 15:')
for i,p in enumerate(players[:15],1): print('  %2d. %-22s %-7s val%4d ~pk%s'%(i,p['player'][:22],GRP[p['pos']],p['_v'],pe(p['_v'])))
print('--- recent draftees (should be ~>= their pick if producing; played>unplayed) ---')
for nm in ['Sullivan Robey','Sam Cumming','Jacob Farrow','Cooper Duff-Tytler','Harry Dean','Zeke Uwland','Dylan Patterson','Harry Kyle','Connor O\'Sullivan']: print('  '+rk(nm))
print('--- KPD check (established vs young) + anchors ---')
for nm in ['Josh Worrell','Sam Collins','Willem Duursma','Nick Daicos','Dayne Zorko','Finn Callaghan','Harry Sheezel']: print('  '+rk(nm))
