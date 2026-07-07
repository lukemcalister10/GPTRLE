import os, sys
if os.environ.get('PYTHONHASHSEED') != '0':   # determinism: pin hash seed so set()/dict iteration order is stable across runs (no value impact)
    os.environ['PYTHONHASHSEED'] = '0'; os.execv(sys.executable, [sys.executable] + sys.argv)
import json, numpy as np, math
from collections import defaultdict
import io as _io, contextlib as _ctx
import single_source as _SS
_SS.assert_startup()            # GUARDS 3 + 3b (lookalike tripwire + engine-opens) before the board is built
_SS.lock_tier2()               # stamp + read-only-lock the frozen train-time caches (peak model + pvc_snapshot)
# ==== ONE ENGINE INSTANCE (F1 FIX 2026-07-05, Luke one-source rewire) ====================================
# BEFORE: rl_export exec'd rl_model.py into its OWN namespace for the display fields, while _merged_recover
# imported a SEPARATE rl_model as MA for the values -- TWO live instances whose player objects differed by
# id(). The valuation gate was `id(p) in _REAL`, and _REAL held the ids of MA's objects, so it matched 0/805
# of the objects rl_export priced -> the ruck cap, v7 age-taper and B5 floor were SILENTLY DROPPED from the
# shipped board (over-pricing ~2/3 of players; Emmett shipped 1361 vs engine 855). F1.
# AFTER: the board is built from THE SAME instance the values come from. _merged_recover imports rl_model as
# MA and wires ev(); we take `players` AND every display fn from that MA, and price MA's own player objects,
# so every _REAL layer fires on the board exactly as in the engine. Belt-and-suspenders: the _REAL gate is
# now keyed by stable key (not id, see _merged_recover), and a hard export<->engine parity gate runs at build
# end (below, before json.dump) -- the build FAILS if any board value != the engine's gated ev().
_ens = {}
with _ctx.redirect_stdout(_io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], _ens)
_ev = _ens['ev']; g = _ens['MA'].__dict__          # THE engine instance (rl_model imported as MA, valuation-wired)
g['BASE_REF']=g['AGE_REF']=2026; g['_pe_clear']()  # _merged_recover's load left MA's clock at a historical V0-build year; pin to the present before pulling AGE_REF / building display fields
players=g['players']; GRP=g['GRP']; bnow=g['bnow']; effpk=g['effpk']; age=g['age']; level_now=g['level_now']
level_stable=g['level_stable']; seasons=g['seasons']; srel=g['srel']; peak_est=g['peak_est']
basepk_c=g['basepk_c']; bandof=g['bandof']; survival=g['survival']; track_delta=g['track_delta']
los_decay=g['los_decay']; clamp=g['clamp']; hist=g['hist']; pkbest=g['pkbest']; PEAK_AGE=g['PEAK_AGE']
PVC=g['PVC']; SCALE=g['SCALE']; debut=g['debut']; data=g['data']; BANDS=g['BANDS']; NB=len(BANDS)
expected_c=g['expected_c']; realized_cv=g['realized_cv']; natcv=g['_natcv']; PICKEQ=g['PICKEQ']; MECH_STATS=g['MECH_STATS']
P_estab=g['P_estab']; established=g['established']; _durable=g['_durable']; _recent_starter=g['_recent_starter']; level_now=g['level_now']; AGE_REF=g['AGE_REF']  # establishment-P + Brodie (JS-parity bake)
val=g['val']; proj_from_peak=g['proj_from_peak']; gfut=g['gfut']; futblend=g['futblend']

# ONE PRICE (D4, Luke's ruling 02/07/2026): the board renders engine ev() -- _merged_recover is the single
# valuation source. The forward/backward season view asks the engine the as-of-year question:
# vM2/vM1/v/vP1/vP2 = ev(p, 2024/2025/2026/2027/2028); the view owns no math.
with _ctx.redirect_stdout(_io.StringIO()):
    for _p in players:
        _p['_v'] = _ev(_p, 2026)
        _p['_vM2'], _p['_vM1'], _p['_vP1'], _p['_vP2'] = _ev(_p, 2024), _ev(_p, 2025), _ev(_p, 2027), _ev(_p, 2028)
        _p['_cvx'] = 1.0
    for _p in g['back_extra']:
        _p['_v'] = _p['_vM2'] = _p['_vM1'] = _p['_vP1'] = _p['_vP2'] = _ev(_p, 2026)
        _p['_cvx'] = 1.0
g['BASE_REF']=g['AGE_REF']=2026; g['_pe_clear']()  # the ev loop advanced the clock to the last as-of year; re-pin to the present so the DISPLAY layer (peak_est/level_now/track/...) reads 2026, as the prior 2-instance display did

def player_rec(p):
    grp=bnow(p); gf=gfut(p); fb=futblend(p); ep=effpk(p); b=bandof(ep); ln=level_now(p); lns=level_stable(p)
    g['STBL']=False; pn=peak_est(p); g['STBL']=True; ps=peak_est(p); g['STBL']=False
    dlt,_=track_delta(gf,ep,srel(p)); surv=survival(b,dlt if dlt is not None else 0,p['games'])
    cg=sum(r['games'] for r in p['scoring']); sr=srel(p)
    track=[{'s':s,'a':round(sr[s][0],2)} for s in sorted(sr) if s<=10]
    has26=any(r['year']==2026 and r['games']>=3 for r in p['scoring'])
    mech=p['type'] if p['type'] in PICKEQ else None
    return {'name':p['player'],'key':p['key'],'grp':grp,'gf':gf,'fut':[[gg,round(w,4)] for gg,w in fb],'age':age(p),'ln':(round(ln,6) if ln is not None else None),'h26':bool(has26),
            'lns':(round(lns,6) if lns is not None else None),'pn':round(pn,6),'ps':round(ps,6),'ep':ep,'band':b,
            'surv':1.0,'pedDecay':round(max(0.0,1-(seasons(p)-1)/4.5),6),'losd':round(los_decay(p),6),
            'g':p['games'],'cg':cg,'yr':p['year'],'pk':p['pick'],'ty':p['type'],'unpl':bool(p.get('_unplayed')),
            'lnNull':level_now(p) is None,'track':track,'v':p['_v'],'bk':bool(p.get('_backonly')),
            'vP1':p.get('_vP1'),'vP2':p.get('_vP2'),'vM1':p.get('_vM1'),'vM2':p.get('_vM2'),'cvx':p.get('_cvx',1.0),'b2hc':p.get('_b2hc',0.0),
            'P':1.0,   # establishment prob, FROZEN (draft-cohort property, not the SuperCoach toggle); 1.0 = established/inert
            'pedOnly':bool(p.get('_unplayed') and (debut(p)>AGE_REF or p.get('_pedonly'))),   # pure-pedigree no-P case (genuine pre-debut); in-window 0-game players are NOT pedOnly -> they get P
            'brodieBase':bool(seasons(p)>=5 and not _durable(p) and not _recent_starter(p) and (level_now(p) is not None) and level_now(p)>=80),  # Brodie signal minus the RUC bit (JS applies RUC exemption live)
            'cat':p.get('_cat'),'draft':p.get('_draft'),'club':p.get('_club'),'mech':mech}
active=[player_rec(p) for p in players]
back=[player_rec(p) for p in g['back_extra']]   # board-history-only rows (retired players recalled for -1/-2)
coh=[]
for p in hist:
    grp=GRP[p['pos']]; ep=effpk(p); pk=pkbest(p); rec={'grp':grp,'ep':ep,'pkbest':(round(pk,6) if pk else None)}
    if pk: rec['relc']=round(clamp((pk/max(basepk_c(grp,ep),40.0))**2.2,0.40,3.0),6)
    coh.append(rec)
def pct(a,q):
    a=sorted(a)
    if not a: return None
    i=(len(a)-1)*q; lo=int(i); f=i-lo; return a[lo]*(1-f)+a[min(lo+1,len(a)-1)]*f

# ===== ANALYTICS A: bid categories (Father-Son / Academy / Next Gen) vs normal, by pick range + by club =====
# Use NATIONAL picks with matured careers (drafted <= 2021) so realised value is meaningful.
def cat_of(p):
    c=(p.get('_cat') or '')
    if 'Father-Son' in c: return 'Father-Son'
    if 'Academy' in c: return 'Academy'
    if 'Next Gen' in c: return 'Next Gen'
    return 'Open'
RANGES=[(1,10),(11,20),(21,30),(31,45),(46,99)]
def rlabel(pk):
    for lo,hi in RANGES:
        if lo<=pk<=hi: return '%d-%d'%(lo,hi if hi<99 else 99)
    return '46-99'
# matured cohort: national + rookie picks, drafted 2008-2023, who played a senior game.
# MATURITY FLOOR (time-based): a career is only judged once it's had 3+ seasons to develop. We do NOT
# use "played a 10+ game season" as the gate, because realized_cv reads a young player's current
# output as his career peak -- a 19yo key forward who plays 15 low-scoring games passes a games test
# but his value is understated, not settled. Time is the only fair gate, applied to academy and open alike.
MATURITY_SEASONS=3
def judgeable(p): return (2026-debut(p))>=MATURITY_SEASONS
matured=[p for p in data if p['type'] in ('ND','RD') and p['pick'] and 2008<=p['year']<=2023 and p['pos'] in GRP and judgeable(p)]
def EP(p): return effpk(p)
_openp=[p for p in matured if cat_of(p)=='Open']
open_base=[None]*100
for k in range(1,100):
    vs=[realized_cv(p) for p in _openp if abs(EP(p)-k)<=6]
    open_base[k]=float(np.mean(vs)) if vs else None
_last=open_base[1] or 300.0
for k in range(1,100):
    if open_base[k] is None: open_base[k]=_last
    else: _last=open_base[k]
def overshoot(p):  # realised value minus what an OPEN pick at the same effective slot returns (>0 = beat the slot)
    return realized_cv(p)-open_base[min(99,EP(p))]
CAT_BY_RANGE={}
for cat in ['Open','Father-Son','Academy','Next Gen']:
    row={}
    for lo,hi in RANGES:
        grp=[p for p in matured if cat_of(p)==cat and lo<=EP(p)<=hi]
        key='%d-%d'%(lo,hi if hi<99 else 99)
        if not grp: row[key]=None; continue
        played=[p for p in grp if pkbest(p) is not None]
        row[key]={'n':len(grp),'hit':round(100*len(played)/len(grp)),
            'mean_val':round(float(np.mean([realized_cv(p) for p in grp]))),
            'mean_over':round(float(np.mean([overshoot(p) for p in grp]))),
            'open_val':round(float(np.mean([open_base[min(99,EP(p))] for p in grp])))}
    CAT_BY_RANGE[cat]=row
# club-level: which clubs over/undershoot expected value with academy / father-son / next-gen
CAT_BY_CLUB={}
for cat in ['Father-Son','Academy','Next Gen']:
    cl=defaultdict(list)
    for p in matured:
        if cat_of(p)==cat: cl[p['_club']].append(p)
    rows=[]
    for club,grp in cl.items():
        if len(grp)<2: continue
        played=[p for p in grp if pkbest(p) is not None]
        rows.append({'club':club,'n':len(grp),'hit':round(100*len(played)/len(grp)),
            'mean_over':round(float(np.mean([overshoot(p) for p in grp]))),
            'mean_val':round(float(np.mean([realized_cv(p) for p in grp])))})
    rows.sort(key=lambda r:-r['mean_over'])
    CAT_BY_CLUB[cat]=rows

# ===== ANALYTICS B: entry mechanisms (pickless) -> outcomes + pick-equivalent (from the model) =====
MECH=sorted(MECH_STATS.values(), key=lambda m:m['pick_equiv'])

# ---- standard curve/projector exports (ported; cohort defs use real ND+RD) ----
ftcoh=[p for p in data if p.get('_ft') and p.get('_grp') in ('ND','RD') and 2008<=p['year']<=2021 and p['pos'] in GRP]
PROJ2={}
band_peaks={b:[pkbest(p) for p in ftcoh if bandof(p['pick'])==b and pkbest(p)] for b in range(NB)}
band_nb={b:sum(1 for p in ftcoh if bandof(p['pick'])==b and not pkbest(p)) for b in range(NB)}
for pos in sorted(set(GRP.values())):
    for b in range(NB):
        grp=[p for p in ftcoh if GRP[p['pos']]==pos and bandof(p['pick'])==b]
        pk=[pkbest(p) for p in grp if pkbest(p)]; nb=sum(1 for p in grp if not pkbest(p))
        if len(pk)>=4: pk_use=pk; nb_use=nb; src='cohort'
        else: pk_use=(pk+band_peaks[b]); nb_use=nb+band_nb[b]; src='mixed'
        if not pk_use: pk_use=band_peaks[b] or [70.0]
        n=len(pk); tot=n+nb
        PROJ2[pos+'|'+str(b)]={'p10':round(pct(pk_use,0.10),2),'p50':round(pct(pk_use,0.50),2),'p90':round(pct(pk_use,0.90),2),
            'peak_age':PEAK_AGE[pos],'n':n,'src':src,'nb':nb_use,'establish':int(round(100*n/tot)) if tot else 0}
devcoh=[p for p in data if p.get('_ft') and p.get('_grp') in ('ND','RD') and 2008<=p['year']<=2025 and p['pos'] in GRP]
cellP=defaultdict(list); cellB=defaultdict(list)
for p in devcoh:
    pos=GRP[p['pos']]; b=bandof(p['pick']); d=debut(p)
    for r in p['scoring']:
        s=r['year']-d+1
        if 1<=s<=10 and r['games']>=4: cellP[(pos,b,s)].append(r['avg']); cellB[(b,s)].append(r['avg'])
def trcol(getter,minn):
    p10=[];p50=[];p90=[];par=[];nn=[]
    for s in range(1,11):
        vals=getter(s)
        if len(vals)>=minn:
            p10.append(round(pct(vals,0.10),1)); p50.append(round(pct(vals,0.50),1)); p90.append(round(pct(vals,0.90),1))
            par.append(round(float(np.mean(vals)),1)); nn.append(len(vals))
        else: p10.append(None);p50.append(None);p90.append(None);par.append(None);nn.append(len(vals))
    return {'p10':p10,'p50':p50,'p90':p90,'par':par,'n':nn}
TRAJ={}; TRAJB={}
for b in range(NB): TRAJB[str(b)]=trcol(lambda s,b=b:cellB[(b,s)],8)
for pos in sorted(set(GRP.values())):
    for b in range(NB):
        col=trcol(lambda s,pos=pos,b=b:cellP[(pos,b,s)],4)
        if any(v is not None for v in col['p50']): TRAJ[pos+'|'+str(b)]=col
CENTERS=[(lo+hi)/2.0 for lo,hi in BANDS]
# Pick Projector (ported)
devall=[p for p in data if p.get('_ft') and p.get('_grp') in ('ND','RD') and 2008<=p['year']<=2025 and p.get('pos') in GRP and effpk(p) is not None]
recs=[]
for p in devall:
    d=debut(p); seas={}; ever11=False
    for r in p['scoring']:
        ss=r['year']-d+1
        if 1<=ss<=10 and r['games']>=4: seas[ss]=r['avg']
        if r['games']>=11: ever11=True
    recs.append({'pos':GRP[p['pos']],'ep':effpk(p),'seas':seas,'ever':ever11})
def wq(vals,wts,q):
    if not vals: return None
    o=sorted(zip(vals,wts)); v=[a for a,_ in o]; w=[b for _,b in o]; cw=[];c=0.0
    for x in w: c+=x; cw.append(c)
    tot=cw[-1]
    if tot<=0: return None
    t=q*tot
    for i in range(len(v)):
        if cw[i]>=t:
            if i==0 or cw[i]==cw[i-1]: return v[i]
            return v[i-1]+(v[i]-v[i-1])*((t-cw[i-1])/(cw[i]-cw[i-1]))
    return v[-1]
def kern(dpk,h): return math.exp(-0.5*(dpk/h)**2)
def bw(pk): return min(9.0,max(2.0,2.0+0.10*pk))
QS=[0.02,0.10,0.25,0.50,0.75,0.90,0.98]; PICKS=range(1,61); SEAS=range(1,11); MINEFF=10.0
posset=sorted(set(GRP.values())); recs_by_pos={ps:[r for r in recs if r['pos']==ps] for ps in posset}
def collect(rset,pk,ss):
    h=bw(pk); va=[]; wa=[]
    for r in rset:
        if ss in r['seas']:
            w=kern(abs(r['ep']-pk),h)
            if w>1e-4: va.append(r['seas'][ss]); wa.append(w)
    return va,wa
def wavg(va,wa): return sum(v*w for v,w in zip(va,wa))/sum(wa)
PJALL={}
for ss in SEAS:
    for pk in PICKS:
        va,wa=collect(recs,pk,ss)
        if va: PJALL[(pk,ss)]={'q':[wq(va,wa,q) for q in QS],'par':wavg(va,wa)}
PJ={}
for pos in posset:
    arr=[]
    for pk in PICKS:
        h=bw(pk); denom=0.0; ever=0.0
        for r in recs_by_pos[pos]:
            w=kern(abs(r['ep']-pk),h); denom+=w
            if r['ever']: ever+=w
        est=round(100*ever/denom) if denom>0 else None
        qs=[]; par=[]; nn=[]
        for ss in SEAS:
            vp,wp=collect(recs_by_pos[pos],pk,ss); eff=sum(wp) if wp else 0.0; allc=PJALL.get((pk,ss))
            if eff>=MINEFF and vp: q=[wq(vp,wp,qq) for qq in QS]; pr=wavg(vp,wp)
            elif vp and allc:
                a=clamp(eff/MINEFF,0,1); q=[a*wq(vp,wp,QS[i])+(1-a)*allc['q'][i] for i in range(len(QS))]; pr=a*wavg(vp,wp)+(1-a)*allc['par']
            elif allc: q=allc['q'][:]; pr=allc['par']
            else: q=None; pr=None
            qs.append([round(x,1) for x in q] if q else None); par.append(round(pr,1) if pr is not None else None); nn.append(round(eff,1))
        arr.append({'q':qs,'par':par,'n':nn,'est':est})
    PJ[pos]=arr
DEBUT_AGE={'ND':19,'RD':19,'SSP':19,'MSD':19,'PSD':19,'IRE':19,'UNR':19,'PDA':19,'PDN':19,'PDS':19}
_ndc=g['_NDC']; _medNDC=int(round(float(np.median(list(_ndc.values())))))
TYPEOFF={'ND':0,'RD':_medNDC}   # rookie picks sit after the national draft on the projector's pick scale
TILT={k:g[k] for k in ['TILT_REF','GAIN_UP','W_UP','UP_MAX','TILT_HI','GAIN_DN','W_DN','DN_MAX','TILT_LO','NBAD_REF','SUS_MIN']}
out={'active':active,'back':back,'cohort':coh,
     'BASEPK_REG':{f'{k[0]}|{k[1]}':round(v,3) for k,v in g['BASEPK_REG'].items()},
     'POOL':{str(k):round(v,3) for k,v in g['POOL'].items()},
     'MIX':{str(b):{gg:round(w,4) for gg,w in g['MIX'][b].items()} for b in g['MIX']},
     'BAND_ANCHOR':g['BAND_ANCHOR'],'bands':g['BANDS'],'CENTERS':[round(c,2) for c in CENTERS],'PJ':PJ,'DEBUT_AGE':DEBUT_AGE,
     'PEAK':g['PEAK'],'PEAK_AGE':g['PEAK_AGE'],'REPL':g['REPL'],'DELTAS':{str(k):v for k,v in g['DELTAS'].items()},
     'pm_pos':g['pm_pos'],'pm_band':{str(k):v for k,v in g['pm_band'].items()},
     'GAMMA':g['GAMMA'],'PMAX':g['PMAX'],'S_SH':g['S_SH'],'BETA_POS':g['BETA_POS'],'ICPT_POS':g['ICPT_POS'],
     'BUST_BAND':{str(k):v for k,v in g['BUST_BAND'].items()},'GRACE':g['GRACE'],'LOS_C':g['LOS_C'],'LOS_P':g['LOS_P'],
     'CAPT_THRESH':g['CAPT_THRESH'],'CAPT_GAIN':g['CAPT_GAIN'],'CAPT_EXP':g['CAPT_EXP'],'CAPT_CAP':g['CAPT_CAP'],
     'ALPHA':g['ALPHA'],'CURVE_H':g['CURVE_H'],'LENS':g['LENS'],'SEASON_PROG':g['SEASON_PROG'],
     'PICKEQ':PICKEQ,'MECH':MECH,'TYPEOFF':TYPEOFF,'CAT_BY_RANGE':CAT_BY_RANGE,'CAT_BY_CLUB':CAT_BY_CLUB,'RANGES':['%d-%d'%(lo,hi if hi<99 else 99) for lo,hi in RANGES],
     **TILT,'SCALE':round(SCALE,5),'PVC':{str(k):v for k,v in PVC.items()},
     'BASE_YEAR':2026,                                                  # board view N maps to draft year BASE_YEAR+N
     'intake':105000,                                                  # Luke ground-truth: empirical entry+1 class value = avg(2024 -1 board 100964, gap-corrected 2023 -2 board 109545) ~ 105000. Supersedes the durable pick-sum (which under-counts vs the convex board value).
     'intakePickSum':round(sum((PVC[k] if k in PVC else PVC[max(PVC)]) for k in range(1,61)) + 6*PVC.get(80,PVC[max(PVC)]) + 13*PVC.get(90,PVC[max(PVC)]) + 9*PVC.get(84,PVC[max(PVC)])),   # durable per-season pick-equiv replenishment (60 ND +6 RD +13 post-draft +9 SSP), ex-transient MSD — reference only
     'intakeFull':round(sum((PVC[k] if k in PVC else PVC[max(PVC)]) for k in range(1,61)) + 6*PVC.get(80,PVC[max(PVC)]) + 13*PVC.get(90,PVC[max(PVC)]) + 27*PVC.get(84,PVC[max(PVC)])),  # + transient MSD (9 SSP+18 MSD = 27 at pick-84 equiv)
     'picks':[{'n':n,'v':PVC[n]} for n in range(1,31)]}                 # Option-A replenishment: future-draft picks as board assets (value=PVC, label year rolls with the view)
# ==== PERMANENT EXPORT<->ENGINE VALUE-PARITY GATE (F1 regression tripwire, 2026-07-05) ==================
# Every board value MUST equal the engine's gated ev() for that player, recomputed INDEPENDENTLY here and
# matched by STABLE KEY. This is exactly the check the shipped board silently failed (2nd rl_model instance
# -> id-gate matched 0/805 -> ruck cap / age-taper / floor dropped). If any active player diverges beyond
# epsilon, the build FAILS LOUDLY -- no mispriced board is ever written. eps=0: ev() is integer-valued and
# the board renders it verbatim, so parity is exact by construction on this single-instance build.
_PARITY_EPS=0
_by_key={r['key']:r for r in active}
_parity_fail=[]
with _ctx.redirect_stdout(_io.StringIO()):
    for _p in players:
        _bv=_by_key.get(_p['key'],{}).get('v'); _gv=_ev(_p,2026)
        if _bv is None or abs(_bv-_gv)>_PARITY_EPS: _parity_fail.append((_p['key'],_bv,_gv))
g['BASE_REF']=g['AGE_REF']=2026; g['_pe_clear']()
if _parity_fail:
    raise SystemExit("EXPORT<->ENGINE PARITY GATE FAILED for %d/%d players (board v != engine gated ev, eps=%s):\n  "%(len(_parity_fail),len(active),_PARITY_EPS)
                     + "\n  ".join("%s: board=%s engine=%s"%(k,b,gg) for k,b,gg in _parity_fail[:25]))
print('PARITY GATE PASS: all %d active board values == engine gated ev() (matched by key, eps=%s)'%(len(active),_PARITY_EPS))

_SS.prepare_write('rl_app_data.json')                       # clear the read-only bit from a prior guarded build
json.dump(out,open('rl_app_data.json','w'),sort_keys=True)   # sort_keys: byte-deterministic output regardless of PYTHONHASHSEED (key order no longer jitters)
_srcmd5=_SS.stamp_derived('rl_app_data.json',tier=1)        # GUARD 1: stamp with source md5 + set read-only (generator is the only writer)
print('exported active=%d cohort=%d | mechanisms=%d categories analysed | board stamped src=%s (read-only)'%(len(active),len(coh),len(MECH),_srcmd5[:8]))
print('CAT_BY_RANGE Academy:',{k:(v['mean_over'] if v else None) for k,v in CAT_BY_RANGE['Academy'].items()})
print('CAT_BY_RANGE Open   :',{k:(v['mean_over'] if v else None) for k,v in CAT_BY_RANGE['Open'].items()})
