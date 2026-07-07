import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; nseas=g['nseas']; cp=g['cp']; LR=cp.LEVEL_RAMP
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def gm(p,y):
    r=g_y(p,y); return r['games'] if r else 0
# exposure/shrink regime for thin-2026 players across the career-age spectrum
thin=[p for p in MA.data if 1<=gm(p,2026)<=5 and gm(p,2025)>=10]
print("=== EXPOSURE REGIME of thin-2026 players (shrink active only if exp<LEVEL_RAMP=14) ===")
nlow=sum(1 for p in thin if cp._exposure(p,2026)<LR)
print(f"thin-2026 players (1-5g in 26, >=10g in 25): {len(thin)};  in shrink regime (exp<{LR}): {nlow} ({100*nlow/len(thin):.0f}%)")
exps=sorted(cp._exposure(p,2026) for p in thin)
print(f"exposure distn: min={exps[0]:.0f} p25={exps[len(exps)//4]:.0f} median={exps[len(exps)//2]:.0f} p75={exps[3*len(exps)//4]:.0f} max={exps[-1]:.0f}")

# on-pace over-correction scan
onp=[p for p in MA.data if nseas(p,2026)>=6 and 11<=gm(p,2026)<=14 and gm(p,2025)>=18]
base={p['key']:ev(p,2026) for p in onp}
CURR_Y=2026; F=14.0/24.0
def _swt_pro(yr,Y):
    f=F if Y==CURR_Y else 1.0
    return cp.RECENCY_DECAY**max(0.0,(Y-yr)-(1.0-f))
cp._swt=_swt_pro
moves=[]
for p in onp:
    b=base[p['key']]; a=ev(p,2026)
    if b>0: moves.append((100*(a-b)/b, p['key'], g_y(p,2025)['avg'], g_y(p,2026)['avg']))
moves.sort(key=lambda t:abs(t[0]),reverse=True)
over=[m for m in moves if abs(m[0])>2]
print(f"\n=== ON-PACE (established, 11-14g): {len(onp)} players; moving >2%: {len(over)} ({100*len(over)/len(onp):.0f}%) ===")
print("biggest movers (move%, key, avg25, avg26):")
for m,k,a25,a26 in moves[:8]: print(f"  {m:+5.1f}%  {k:20s} 25avg={a25:.0f} 26avg={a26:.0f} gap={a25-a26:+.0f}")
print(f"median |move| on-pace: {np.median([abs(m[0]) for m in moves]):.1f}%")
