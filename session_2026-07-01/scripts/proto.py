import io,contextlib,numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; nseas=g['nseas']; cp=g['cp']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def gm(p,y):
    r=g_y(p,y); return r['games'] if r else 0

# ---- pick targets BEFORE rebinding ----
# thin-2026 injured guns: established, strong 2025, 1-5 games in 2026
thin=[p for p in MA.data if nseas(p,2026)>=6 and 1<=gm(p,2026)<=5 and gm(p,2025)>=16 and (g_y(p,2025) or {}).get('avg',0)>=88]
thin.sort(key=lambda p: g_y(p,2025)['avg'], reverse=True)
thin=thin[:4]
onpace=[p for p in MA.data if p['key'] in ('ed-richards','rowan-marshall','andrew-brayshaw','lachlan-ash')]
# inert-check sample: 60 established players
samp=[p for p in MA.data if nseas(p,2026)>=6][:60]

# ---- BASELINE pass ----
base={}
for p in {q['key']:q for q in thin+onpace+samp}.values():
    k=p['key']; base[k]={}
    for Y in [2022,2023,2024,2025,2026]:
        try: base[k][Y]=ev(p,Y)
        except: base[k][Y]=None
# capture mechanism internals baseline for thin[0]
tp=thin[0]
base_exp=cp._exposure(tp,2026); base_lvl=cp._lvl_eff(tp,2026)

# ---- REBIND: decay proration keyed off Y ----
CURR_Y=2026; F=14.0/24.0
def _swt_pro(yr,Y):
    f=F if Y==CURR_Y else 1.0
    return cp.RECENCY_DECAY**max(0.0,(Y-yr)-(1.0-f))
cp._swt=_swt_pro

# ---- PRORATED pass ----
pro={}
for p in {q['key']:q for q in thin+onpace+samp}.values():
    k=p['key']; pro[k]={}
    for Y in [2022,2023,2024,2025,2026]:
        try: pro[k][Y]=ev(p,Y)
        except: pro[k][Y]=None
pro_exp=cp._exposure(tp,2026); pro_lvl=cp._lvl_eff(tp,2026)

# ---- VALIDATION 1: INERT at f=1 (historical byte-identical) ----
maxdiff=0; ndiff=0
for p in samp:
    k=p['key']
    for Y in [2022,2023,2024,2025]:
        a,b=base[k][Y],pro[k][Y]
        if a is not None and b is not None:
            d=abs(a-b); maxdiff=max(maxdiff,d); ndiff+= (d>0)
print(f"=== INERT check (60 established players x historical Y 2022-2025): max|Δ|={maxdiff}  #changed={ndiff}  (expect 0/0) ===")

# ---- VALIDATION 2: thin-2026 before/after ----
print("\n=== THIN-2026 injured guns: ev(2026) before -> after (drop vs their 2025) ===")
for p in thin:
    k=p['key']; v25=base[k][2025]; b26=base[k][2026]; a26=pro[k][2026]
    print(f"  {k:20s} 25:{gm(p,2025)}g/{g_y(p,2025)['avg']:.0f} 26:{gm(p,2026)}g/{g_y(p,2026)['avg']:.0f} | ev25={v25} ev26 {b26}->{a26} | dropVS25 {100*(v25-b26)/v25:.0f}%->{100*(v25-a26)/v25:.0f}%  lift {100*(a26-b26)/b26:+.0f}%")

# ---- VALIDATION 3: on-pace barely move ----
print("\n=== ON-PACE players: ev(2026) before/after (expect <~2%) ===")
for p in onpace:
    k=p['key']; b26=base[k][2026]; a26=pro[k][2026]
    print(f"  {k:20s} 26:{gm(p,2026)}g/{g_y(p,2026)['avg']:.0f} | ev26 {b26}->{a26}  ({100*(a26-b26)/b26:+.1f}%)")

# ---- VALIDATION 4: mechanism ----
print(f"\n=== MECHANISM ({tp['key']}, thin): recency-wtd exposure {base_exp:.1f}->{pro_exp:.1f} (LEVEL_RAMP={cp.LEVEL_RAMP}); reliability-shrunk level {base_lvl:.1f}->{pro_lvl:.1f} ===")
