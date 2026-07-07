"""VERIFY ANCHORS — run on a fresh-session bootstrap to confirm the rebuilt model is intact.
  cd /home/claude/rl_after && PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 python3 ../verify_anchors.py
State checked: rebuilt prior (exposure + level_eff-shrinkage + age features) + ruck tax 0.25 + UNIFORM REPL -3
(cont.25 dial; per-group fwd-4/other-2 split REVERTED to uniform -3 on 2026-06-28 -> anchors REFRESHED below).
Anchors as of the 2026-06-28 REPL-uniformization refresh. If these drift, something changed — STOP and reconcile before building.
"""
import os,io,importlib.util,contextlib,numpy as np,sys
os.environ.setdefault('RL_GAMMA','0.85'); os.environ.setdefault('RL_PICK1','3000')
def _ld(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()): s.loader.exec_module(m); return m
_so=sys.stdout
rd=_ld('rd','/home/claude/rl_workspace/forward_valuation/dist_redesign.py'); cp=rd.cp; dp=rd.dp; MA=cp.MA
_pv=MA.proj_value
sys.stdout=io.StringIO(); import compute; sys.stdout=_so
cm=rd.build(); MA.BASE_REF=MA.AGE_REF=2026; MA._pe_clear()
def f(nm):
    c=[p for p in MA.players if nm.lower() in p['player'].lower()]; return c[0] if c else None
# Post-SOFT-FLOOR anchors (cont.25, REFRESHED 2026-06-28 for uniform REPL -3). Proven players have w=0; young high-picks floored:
#   Zeke Uwland (GEN_DEF pk2, general games-floor) 1518; Jed Walter (KEY_FWD pk3, KPP year-floor) 1087;
#   Jonty Faull (KEY_FWD pk14, KPP year-floor) 757. Mechanism = SOFT FLOOR in dist_redesign.py; see UNRESOLVED U25-A.
EXPECT={'Nick Daicos':7089,'Marcus Bontempelli':3163,'Christian Petracca':3087,'Tom McCarthy':2666,
        'Jeremy Cameron':1132,'Max Gawn':2567,'Nick Madden':1508,'Toby Conway':1051,'Lachlan McAndrew':1719,
        'Mark Keane':2349,'Riley Bice':786,'Zeke Uwland':1518,'Jed Walter':1087,'Jonty Faull':757}
print('CONFIG: PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=%s RL_REPL_DROP=%s (uniform; FWD/OTHER inert) RL_RECENCY_DECAY=%s RL_LEVEL_RAMP=%s'
      % (rd.RUCK_TAX,rd.REPL_DROP_PTS,cp.RECENCY_DECAY,cp.LEVEL_RAMP))
ok=True
for nm,exp in EXPECT.items():
    got=rd.redesign_value(f(nm),cm); m='OK' if got==exp else 'DRIFT (exp %d)'%exp; ok&=(got==exp)
    print('  %-22s %-8s = %-6d %s' % (nm[:22],MA.gfut(f(nm)),got,m))
shar=round(_pv(f('Sharman'),0)); print('  engine Sharman proj_value(0) = %d  (~310, engine untouched)' % shar)
print('  board: %d active players' % len(MA.players))
cov={q:0 for q in cp.Q}; n=0
for p in MA.data:
    if not MA.GRP.get(p['pos']) or cp.debutyr(p)>2021 or not (p.get('pick') or p.get('_ft')): continue
    d0=cp.debutyr(p)-1; last=max([x['year'] for x in p['scoring']]+[d0])
    for Y in range(d0,min(last,2021)+1):
        t=cp.fwd_best3_from(p,Y,2026); band=cp.cond_prior_band(p,cm,Y); n+=1
        for i,q in enumerate(cp.Q):
            if t<=band[i]: cov[q]+=1
print('  CALIB GATE (in-distribution): %s n=%d (expect 11/30/49/70/90)' % ({q:round(100*cov[q]/max(n,1)) for q in cp.Q},n))
print('ALL ANCHORS OK' if ok else '*** ANCHOR DRIFT — reconcile before building ***')
