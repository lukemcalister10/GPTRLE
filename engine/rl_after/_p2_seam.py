import io, contextlib, numpy as np
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; cp=g['cp']; cm=g['cm']; q97m=g['q97m']; Q=cp.Q
def R(sub,exp=None):
    hs=[p for p in MA.data if sub.lower() in p['player'].lower() and MA.GRP.get(p.get('pos'))]
    if exp is not None: hs=[p for p in hs if g['ev'](p,2026)==exp]
    return hs[0] if len(hs)==1 else [q['player'] for q in hs]

def band_from_feat(feat):
    f=np.array([feat]); b=np.sort([float(cm[q].predict(f)[0]) for q in Q])
    return np.append(b, max(float(q97m.predict(f)[0]), b[4]))
def bmid(feat): return float(np.median(band_from_feat(feat)))
# feature indices: 0-5 onehot, 6=log(effpk), 7=exposure, 8=dev_tenure, 9=Leff(FIXED), 10=age
IPK,IEXP,ITEN,ILVL,IAGE=6,7,8,9,10

P=R('Darcy Parish')
print("=== base feats (as-of) ===")
anchors=[('Parish yr1 (2016)',P,2016),('Parish yr3 (2018)',P,2018),('Parish yr5 (2020)',P,2020),
         ('Jeffrey present',R('Joel Jeffrey',1773),2026),('Reid yr1',R('Harley Reid'),2026)]
base={}
for nm,p,Y in anchors:
    ft=list(cp._feat(p,Y)); lv=ft[ILVL]; bm=bmid(ft)
    base[nm]=(p,Y,ft)
    print(f"  {nm:20s} pk{MA.effpk(p):>2d} exp{ft[IEXP]:5.1f} ten{ft[ITEN]:4.1f} age{ft[IAGE]:4.1f}  Leff(FIXED)={lv:5.1f}  band_mid={bm:5.1f}  OFFSET(band-Leff)={bm-lv:+5.1f}")

def sweep(nm, idx, vals, label, fmt="{:.0f}"):
    p,Y,ft0=base[nm]; lv=ft0[ILVL]
    print(f"\n  [{nm}] vary {label} (Leff FIXED {lv:.1f}); band_mid / OFFSET:")
    row=[]
    for v in vals:
        ft=list(ft0); ft[idx]=(np.log(v) if idx==IPK else v)
        bm=bmid(ft); row.append((v,bm,bm-lv))
    print("     "+label+": "+"  ".join(f"{fmt.format(v)}->{bm:.0f}(+{off:.0f})" for v,bm,off in row))

print("\n=== PART 1 SWEEPS: what lifts the ceiling above the fixed level ===")
# On book-Parish yr3 (proven-ish mediocre, pk5, level 77.7): does pick/tenure/age/exposure decay the offset?
for nm in ['Parish yr3 (2018)']:
    sweep(nm, IPK,  [1,5,10,20,40,60], "pick")
    sweep(nm, ITEN, [1,2,3,4,5,6,8],   "dev_tenure")
    sweep(nm, IAGE, [19,21,23,25,27,29],"age")
    sweep(nm, IEXP, [10,30,60,90,120],  "exposure(recency-wtd games)")
print("\n=== SEAM CROSS-CHECK: same tenure sweep on Reid(pk1 first-yr) and Jeffrey(pk30) ===")
for nm in ['Reid yr1','Jeffrey present']:
    sweep(nm, ITEN, [1,2,3,4,5,6,8], "dev_tenure")
    sweep(nm, IPK,  [1,5,10,20,40,60], "pick")
print("\n=> The feature whose sweep DECAYS the offset toward 0 is the seam (fix can gate on it).")
print("   If pick keeps the offset high at all tenures -> pedigree-locked (hard to make first-year-safe on tenure alone).")
