"""Smoothed, position-aware establishment surface (2026-06-18 redesign; decoupled from rl_model 2026-06-21).
Replaces the coarse hand-banded grid + credibility blend. Monotone (rises in games, falls in years);
KEY/RUC keep OWN shapes partially pooled toward GEN by sample size. Year-ordinal = season number
(1 = debut season). The caller INJECTS data via build(data, GRP, debut) -> no rl_model import (was a cycle)."""
import numpy as _np

# ---- axes ----
BAND_EDGES = [(0,0),(1,2),(3,5),(6,9),(10,14),(15,22),(23,40),(41,10**9)]
BAND_LBL   = ["0","1-2","3-5","6-9","10-14","15-22","23-40","41+"]
NB = len(BAND_EDGES); NY = 7
def band(G):
    if G<1: return 0
    if G<3: return 1
    if G<6: return 2
    if G<10: return 3
    if G<15: return 4
    if G<23: return 5
    if G<41: return 6
    return 7
def ybucket(Y): return min(max(int(Y),1),NY)
POOL_K = 10.0          # KEY/RUC own-weight = n/(n+K)
FLOOR_41 = 0.93        # 41+ cumulative games => essentially established

def _wpava(vals,wts,incr=True):
    n=len(vals)
    if n==0: return []
    s=1.0 if incr else -1.0
    bval,bw,bcnt=[],[],[]
    for i in range(n):
        cv=s*vals[i]; cw=max(wts[i],1e-9); cc=1
        while bval and bval[-1]>cv+1e-12:
            pv,pw,pc=bval.pop(),bw.pop(),bcnt.pop()
            cv=(pv*pw+cv*cw)/(pw+cw); cw=pw+cw; cc=pc+cc
        bval.append(cv); bw.append(cw); bcnt.append(cc)
    out=[]
    for v,c in zip(bval,bcnt): out+=[s*v]*c
    return out

def _smooth(M,W):
    M=[row[:] for row in M]
    for _ in range(3):
        for y in range(NY): M[y]=_wpava(M[y],W[y],incr=True)
        for b in range(NB):
            col=_wpava([M[y][b] for y in range(NY)],[W[y][b] for y in range(NY)],incr=False)
            for y in range(NY): M[y][b]=col[y]
    for y in range(NY): M[y][NB-1]=max(M[y][NB-1],FLOOR_41)
    return M

# ---- surface state (set by build(); injected data avoids importing rl_model) ----
GRID=None; _XK=None; _GRIDx=None; _BUILT=False
def build(data, GRP, debut):
    """Build the establishment surface from the MATURE cohort (ND/RD, debut<=2019) in the caller's data."""
    global GRID,_XK,_GRIDx,_BUILT
    def grp3(p):
        g=GRP.get(p['pos']); return 'RUC' if g=='RUC' else ('KEY' if g in('KEY_DEF','KEY_FWD') else 'GEN')
    def est(p):
        cg=sum(r['games'] for r in p['scoring']); bg=max([r['games'] for r in p['scoring']],default=0)
        return cg>=50 and bg>=11
    def gthru(p,S):
        d=debut(p); return sum(r['games'] for r in p['scoring'] if d<=r['year']<d+S)
    _raw={g:[[[0,0] for _ in range(NB)] for _ in range(NY)] for g in ('GEN','KEY','RUC')}
    _bgames=[[0.0,0] for _ in range(NB)]
    for p in data:
        if p['pos'] not in GRP: continue
        if p.get('_grp') in('ND','RD') and debut(p)<=2019:
            e=est(p); g3=grp3(p); ten=2026-debut(p)
            for S in range(1,min(ten,NY+2)+1):
                G=gthru(p,S); y=ybucket(S)-1; b=band(G)
                _raw[g3][y][b][0]+=e; _raw[g3][y][b][1]+=1
                _bgames[b][0]+=G; _bgames[b][1]+=1
    def _mat(g3):
        M=[[(_raw[g3][y][b][0]/_raw[g3][y][b][1] if _raw[g3][y][b][1] else 0.5) for b in range(NB)] for y in range(NY)]
        W=[[float(_raw[g3][y][b][1]) for b in range(NB)] for y in range(NY)]
        return M,W
    _gM,_gW=_mat('GEN'); GEN=_smooth(_gM,_gW); GRID={'GEN':GEN}
    for g3 in ('KEY','RUC'):
        M,W=_mat(g3); MP=[[0.0]*NB for _ in range(NY)]; WP=[[0.0]*NB for _ in range(NY)]
        for y in range(NY):
            for b in range(NB):
                n=W[y][b]; w_own=n/(n+POOL_K)
                MP[y][b]=w_own*M[y][b]+(1-w_own)*GEN[y][b]; WP[y][b]=n+POOL_K
        GRID[g3]=_smooth(MP,WP)
    _XK=_np.array([(_bgames[b][0]/_bgames[b][1] if _bgames[b][1] else m)
                   for b,m in enumerate([0,1.5,4,7.5,12,18,31,55])],float)
    for b in range(1,NB):
        if _XK[b]<=_XK[b-1]: _XK[b]=_XK[b-1]+0.5
    _GRIDx={g3:[_np.array(GRID[g3][y],float) for y in range(NY)] for g3 in GRID}
    _BUILT=True

def Praw(g3,Y,G):
    """Smoothed establishment rate for group g3 at year-ordinal Y, cumulative games G (linear-interp, monotone)."""
    y=ybucket(Y)-1
    return float(_np.interp(float(G),_XK,_GRIDx[g3][y]))

# ---- mature-entry discount (graded by entry-age tier, shaped by games; caller passes ea=entry_age) ----
MATURE_FACTOR=0.747                                   # legacy flat factor, retained for reference
_MAT_KNOTS=[0.0,4.0,15.0,31.0,60.0]
_MAT_2122=[0.70,0.51,0.80,0.77,1.00]                  # entry-age 21-22
_MAT_23  =[0.18,0.13,0.34,0.34,0.92]                  # entry-age 23+
def mat_mult(ea,G):
    if ea<=20: return 1.0
    tier=_MAT_2122 if ea<=22 else _MAT_23
    return float(min(1.0,_np.interp(float(G),_MAT_KNOTS,tier)))
