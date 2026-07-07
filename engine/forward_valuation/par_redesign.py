"""PAR-CENTRED REDESIGN — A/B/C built. STANDALONE mock; nothing wired into engine value().
  A: floor beta DERIVED from per-position par-production / (PVC x mult), cap a margin below the lowest (not pinned).
  B: non-play tilt lives in BAND space (p50 tilt + p10 widen, p90 PRESERVED). Level feature stays PURE par-centred.
  C: tilt magnitude = base-rate-relative shortfall vs play-rate at position x tenure (tenure ramp emerges; rucks right).
Change-one-thing in training: the only redefined feature is cp._lvl_eff = pure par-centred (no tilt -> stays in-distn).

Run: cd /home/claude/rl_after && PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 \
     RL_REPL_DROP=3 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=200 PAR_RAMPS=14 \
     python3 ../forward_valuation/par_redesign.py
"""
import sys,os,io,contextlib,copy,collections,numpy as np
sys.path.insert(0,'/home/claude/rl_after'); sys.path.insert(0,'/home/claude/rl_workspace/forward_valuation')
import importlib.util
def _L(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()): s.loader.exec_module(m)
    return m
_FV=os.environ.get('RL_FV','/home/claude/rl_workspace/forward_valuation')   # D10: parameterized (D8 mixed-pair root cause); default byte-identical
rd=_L('rd',os.path.join(_FV,'dist_redesign.py')); cp=rd.cp; dp=rd.dp; MA=cp.MA
pb=_L('pb',os.path.join(_FV,'par_build.py')); F=pb.fit()
with contextlib.redirect_stdout(io.StringIO()): import compute
MA.BASE_REF=MA.AGE_REF=2026; MA._pe_clear()
SEASON_PROG=getattr(MA,'SEASON_PROG',0.58); CUR_ROUNDS=round(SEASON_PROG*22)
GROUPS=['MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC']
MULT={'MID':1.10,'GEN_DEF':1.04,'GEN_FWD':1.0,'KEY_DEF':1.0,'KEY_FWD':0.86,'RUC':1.0}

RAMP        = float(os.environ.get('PAR_RAMPS','14').split(',')[0])  # confidence ramp (level feature only now)
BETA_MARGIN = 0.08    # cap sits this far below the lowest per-position par-production ratio
# POSITION-SPECIFIC beta (cont.27): the floor must track PRODUCTION per position, not pedigree. Par defenders price
# near the replacement cliff (real check: Quaynor/Chapman/Bergman ~370-720), so they need a much lower floor than
# scorers. TWO tiers: scorers ~0.5, defenders ~0.28. *** TRIGGER: if >~2 tiers are needed (e.g. KPP wants its own),
# ABANDON beta x PVC and switch to a realized-level floor -- position-specific beta IS that idea at lower fidelity. ***
BETA_POS = {'MID':0.50,'GEN_FWD':0.50,'KEY_FWD':0.50,'RUC':0.50,'GEN_DEF':0.28,'KEY_DEF':0.28}  # KPP=watch-item
# band-space non-play tilt caps (Fork B guardrail):
TILT_CAP    = 0.60    # p50 may fall at most this fraction of the (p50-p10) gap
WIDEN_K     = 0.60    # p10 extends down by WIDEN_K * shortfall * (p50-p10)   (fat-left)
#   p90 and p70 are PRESERVED (upside/optionality untouched)

# ---------- par surface (cached, nan-safe) ----------
_FB={g:(float(np.median(F['POS'][g][:,2])) if len(F['POS'][g]) else 60.0) for g in GROUPS}
_PC={}
def _lvl_safe(pos,pick):
    lv,ess=pb.level_at(F,pos,min(max(pick,1),70))
    if not np.isfinite(lv) or ess<3.0:
        lf=F['levelfn'].get(pos)
        if lf is not None:
            lv2,_=pb.loclin(np.log(min(max(pick,1),70)),lf[0],lf[1],1.0)
            if np.isfinite(lv2): return lv2
        return _FB[pos]
    return lv
def par_at(pos,pick,T):
    k=(pos,int(round(pick)),int(max(1,min(T,6))))
    if k not in _PC: _PC[k]=_lvl_safe(pos,pick)+F['ramp_shr'][pos][k[2]]
    return _PC[k]
def draftyr(p): return cp.debutyr(p)-1
def tenure(p,Y): return max(1,Y-draftyr(p))

# ---------- Fork C: base-rate play-rate per position x tenure (all rostered, incl 0-game) ----------
def _build_base_rate():
    pool=[p for p in MA.data if MA.GRP.get(p.get('pos'))
          and (p.get('pick') or p.get('_ft')) and 2003<=draftyr(p)<=2018]
    by=collections.defaultdict(list)
    for p in pool:
        pos=MA.gfut(p); d0=draftyr(p)
        rows={x['year']:x['games'] for x in p['scoring']}
        maxten=max([y-d0 for y in rows],default=0)
        for T in range(1,7):
            rostered = (T==1) or (maxten>=T)      # yr1: all drafted; later: still on a list (a row at tenure>=T)
            if rostered: by[(pos,T)].append(rows.get(d0+T,0)/22.0)
    return {k:float(np.median(v)) for k,v in by.items() if v}
BASE_RATE=_build_base_rate()

def player_rate(p,Y):
    """FM#3 denominator + RECENCY-WEIGHTED per-season rate (recent form governs, as the level feature does).
    Debut season counts since-debut (av=games -> rate 1.0, no late-debut penalty); a recent 0-game season
    (g=0, full av) pulls the rate down at weight 1.0 -> catches the 'proven player fell off this year' case."""
    rows={x['year']:x['games'] for x in p['scoring'] if x['games']>0}
    if not rows: return 0.0
    debut=min(rows); dec=cp.RECENCY_DECAY; num=den=0.0
    for y in range(debut,Y+1):
        g=rows.get(y,0); av=(g if y==debut else (CUR_ROUNDS if y==MA.BASE_REF else 22))
        if av<=0: continue
        wt=dec**max(0,Y-y); num+=wt*(g/av); den+=wt
    return num/den if den>0 else 0.0
def shortfall(p,Y):
    pos=MA.gfut(p); T=tenure(p,Y)
    base=BASE_RATE.get((pos,T), BASE_RATE.get((pos,min(T,5)),0.5))
    # 0-game current-season players: rate measured since-draft over elapsed rounds
    pr = 0.0 if not any(x['games']>0 for x in p['scoring']) else player_rate(p,Y)
    return max(0.0, base-pr)

# ---------- THE redefined feature: PURE par-centred (no tilt; train+inference identical) ----------
def lvl_par(p,Y):
    pos=MA.gfut(p); pk=min(MA.effpk(p),cp.KMAX); T=tenure(p,Y)
    par=par_at(pos,pk,T); w=min(1.0, cp._exposure(p,Y)/RAMP)
    return float(par+(cp._lvl_wt(p,Y)-par)*w)

# ---------- Fork B: band-space non-play tilt (p50 down bounded, p10 widen, p70/p90 preserved) ----------
def tilt_band(band, s):
    if s<=0: return band
    p10,p30,p50,p70,p90=band; gap=max(1.0,p50-p10)
    drop=min(TILT_CAP, s)                                  # bounded fraction of the gap
    p50n=p50-drop*gap; p30n=p30-drop*0.7*(p30-p10); p10n=p10-WIDEN_K*s*gap
    return np.array([p10n,p30n,p50n,p70,p90])             # p70,p90 PRESERVED

_ORIG=cp._lvl_eff
def retrain():
    cp._lvl_eff=lvl_par; return rd.build()
def restore(): cp._lvl_eff=_ORIG

def synth(base,avg,games,year=2026,seasons=1):
    q=copy.deepcopy(base); q['year']=year-seasons
    q['scoring']=[{'year':year-seasons+1+i,'games':games,'avg':avg} for i in range(seasons)]
    return q
def band5(p,cm,Y=2026): return cp.cond_prior_band(p,cm,Y)
def priceband(p,b): return rd._price_repl(p,b,dp.SCALE_DIST,'bal')
def PVCm(pos,pick): return MA.PVC[pick]*MULT[pos]
def f(nm):
    c=[p for p in MA.players if nm.lower() in p['player'].lower() and MA.GRP.get(p['pos'])]; return c[0] if c else None

# ============================ REPORT ============================
if __name__=='__main__':
    import sys as _s
    Cum=f('Sam Cumming'); Pat=f('Dylan Patterson')
    print(f"A/B/C mock | ramp={RAMP} | 200-tree mock fidelity | SEASON_PROG={SEASON_PROG}(~r{CUR_ROUNDS})")

    print("\n=== C. base-rate play-rate (median games/22, all rostered) — pos x tenure ===")
    print("  pos        " + "".join(f"  yr{T}" for T in range(1,7)))
    for g in GROUPS:
        print(f"  {g:9s} " + "".join(f"  {BASE_RATE.get((g,T),0):.2f}" for T in range(1,7)))

    cm=retrain(); _s.stdout.flush()

    print("\n=== A. derive beta: par-production / (PVC x mult), per position x pick (established par player) ===")
    print("  pos        pick   par   par-prod   PVCxmult     ratio")
    def find_pos(g):
        c=[p for p in MA.players if MA.GRP.get(p['pos']) and MA.gfut(p)==g and (p.get('pick') or p.get('_ft')) and MA.level_now(p) is not None]
        return c[0] if c else None
    ratios={}
    for g in ['MID','KEY_FWD','RUC','GEN_DEF']:
        base=find_pos(g)
        if base is None: print(f"  {g}: no native player"); continue
        for pk in [3,8,15,25]:
            plv=par_at(g,pk,3); q=copy.deepcopy(base); q['pick']=pk; q['_ft']=False; q['year']=2026-3
            q['scoring']=[{'year':2024+i,'games':22,'avg':plv} for i in range(3)]
            b=band5(q,cm); pr=priceband(q,b); pv=PVCm(g,pk); r=pr/pv; ratios[(g,pk)]=r
            print(f"  {g:9s} {pk:4d}  {plv:5.1f}   {pr:7.0f}   {pv:7.0f}     {r:.2f}   band[{b[0]:.0f}/{b[2]:.0f}/{b[4]:.0f}]")
    # beta from the binding (lowest) ratio among RELIABLE cells (drop pk3 KPP thin cells)
    rel={k:v for k,v in ratios.items() if not (k[0] in ('KEY_FWD','KEY_DEF') and k[1]<=3)}
    beta=max(0.1, min(rel.values())-BETA_MARGIN) if rel else 0.5
    print(f"  -> binding (reliable) ratio {min(rel.values()):.2f}; single-beta cap = {beta:.2f}  (vs cont.25 0.85) -- NB ratio is pick-dependent, see structure")
    def floorval(pos,pick): return BETA_POS.get(pos,0.5)*PVCm(pos,pick)   # POSITION-SPECIFIC
    _s.stdout.flush()

    print(f"\n=== B+verdict. three cases @ ramp {RAMP}, beta={beta:.2f} (band: raw -> tilted; value=max(E[v],floor)) ===")
    # Cumming
    cs=synth(Cum,61.3,7); b=band5(cs,cm); s=0.0; ev=priceband(cs,b); fl=floorval('MID',7); val=max(round(ev),round(fl))
    print(f"  Cumming 7g@61 : eff {lvl_par(cs,2026):5.1f} band[{b[0]:3.0f}/{b[2]:3.0f}/{b[4]:3.0f}] E[v] {ev:4.0f} floor {fl:.0f} -> VALUE {val}  {'PAR-HELD' if val>fl+1 else 'floored'}")
    # 61 vs 21 @3g
    out={}
    for tag,avg in [('61',61.3),('21',21.3)]:
        q=synth(Cum,avg,3); b=band5(q,cm); ev=priceband(q,b); fl=floorval('MID',7); out[tag]=(lvl_par(q,2026),ev,max(round(ev),round(fl)))
    print(f"  61-vs-21 @3g  : 61 eff {out['61'][0]:.1f} E[v] {out['61'][1]:.0f} VALUE {out['61'][2]} | 21 eff {out['21'][0]:.1f} E[v] {out['21'][1]:.0f} VALUE {out['21'][2]} | sep E[v] {out['61'][1]-out['21'][1]:+.0f} VALUE {out['61'][2]-out['21'][2]:+.0f}")
    # Patterson — band-space tilt
    if Pat:
        pos=MA.gfut(Pat); pk=MA.effpk(Pat); s=shortfall(Pat,2026); b=band5(Pat,cm); bt=tilt_band(b,s)
        evr=priceband(Pat,b); evt=priceband(Pat,bt); fl=floorval(pos,pk); val=max(round(evt),round(fl))
        print(f"  Patterson 0g  : pos {pos} pk{pk} shortfall {s:.2f} (base {BASE_RATE.get((pos,1)):.2f} - rate 0)")
        print(f"     raw  band[{b[0]:3.0f}/{b[1]:3.0f}/{b[2]:3.0f}/{b[3]:3.0f}/{b[4]:3.0f}] E[v] {evr:.0f}")
        print(f"     TILT band[{bt[0]:3.0f}/{bt[1]:3.0f}/{bt[2]:3.0f}/{bt[3]:3.0f}/{bt[4]:3.0f}] E[v] {evt:.0f} floor {fl:.0f} -> VALUE {val}  (low-p50/low-p10, p90 preserved {bt[4]:.0f}=={b[4]:.0f})")
    # year-3 NON-ESTABLISHER (MID) — the case that actually fires the tilt
    y3=synth(Cum,57.0,5,seasons=3)                          # 3 seasons, ~5 g/yr -> low play-rate at tenure 3
    y3['scoring']=[{'year':2024,'games':8,'avg':60},{'year':2025,'games':6,'avg':58},{'year':2026,'games':2,'avg':55}]
    pos='MID'; pk=7; s3=shortfall(y3,2026); b=band5(y3,cm); bt=tilt_band(b,s3)
    evr=priceband(y3,b); evt=priceband(y3,bt); fl=floorval(pos,pk); val=max(round(evt),round(fl))
    print(f"  yr3 non-establ: MID pk7 tenure {tenure(y3,2026)} rate {player_rate(y3,2026):.2f} vs base {BASE_RATE.get(('MID',3)):.2f} -> shortfall {s3:.2f}")
    print(f"     raw  band[{b[0]:3.0f}/{b[1]:3.0f}/{b[2]:3.0f}/{b[3]:3.0f}/{b[4]:3.0f}] E[v] {evr:.0f}")
    print(f"     TILT band[{bt[0]:3.0f}/{bt[1]:3.0f}/{bt[2]:3.0f}/{bt[3]:3.0f}/{bt[4]:3.0f}] E[v] {evt:.0f} floor {fl:.0f} -> VALUE {val}  (p50 {b[2]:.0f}->{bt[2]:.0f} bounded, p10 {b[0]:.0f}->{bt[0]:.0f} fat-left, p90 {bt[4]:.0f} preserved)")

    # ---- Fork B STRESS: tilt across shortfall x tenure (does p50 stay bounded / p90 survive at the extreme?) ----
    print("\n=== Fork B stress: bounded-tilt guardrail across tenure x recent-rate (MID pk7) ===")
    def mkcase(ten, recent_g):
        sc=[{'year':2026-ten+1+i,'games':22,'avg':62} for i in range(ten-1)]
        sc.append({'year':2026,'games':recent_g,'avg':58})           # recent season sets the rate
        q=copy.deepcopy(Cum); q['year']=2026-ten; q['scoring']=sc; return q
    print("  tenure recentG  rate  base  short |  raw p10/p50/p90  -> tilt p10/p50/p90 | p90 kept? p50 drop")
    # extreme: debut-then-vanish (played only debut season, then 0 for years) -> shortfall hits the cap
    def washout(ten):
        q=copy.deepcopy(Cum); q['year']=2026-ten
        q['scoring']=[{'year':2026-ten+1,'games':8,'avg':60}]   # debut season only; rest of career = 0 games
        return q
    cases=[('yr2',mkcase(2,4)),('yr3',mkcase(3,3)),('yr5',mkcase(5,2)),('yr5',mkcase(5,1)),('yr6',mkcase(6,0)),
           ('yr6*washout',washout(6))]
    for lbl,q in cases:
        ten=tenure(q,2026); rg=q['scoring'][-1]['games']; pr=player_rate(q,2026); base=BASE_RATE.get(('MID',min(ten,6)),0.5); s=max(0,base-pr)
        b=band5(q,cm); bt=tilt_band(b,s)
        kept = abs(bt[4]-b[4])<1e-6
        print(f"   {lbl:11s} r{rg:2d} {pr:.2f} {base:.2f} {s:.2f} | {b[0]:3.0f}/{b[2]:3.0f}/{b[4]:3.0f} -> {bt[0]:3.0f}/{bt[2]:3.0f}/{bt[4]:3.0f} | p90 {'kept' if kept else 'LOST!'} p50 {b[2]-bt[2]:+.1f} ({(b[2]-bt[2])/max(1,b[2]-b[0])*100:.0f}% gap, cap {TILT_CAP*100:.0f}%)")
    restore()
