"""GATE 1 flatness: engine VALUE by tenure for REAL native players, per position, survivorship-clean.
Early-career-value proof: value should be ~flat across tenure (a yr1 winner ~ a yr5 winner), not artificially rising/falling."""
import io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0])
_BOARD_PATH=False   # D14: in-sample/walk-forward gate — board-only laws (V0 curve, KPP floor) OFF (Luke's exemption).
era={}
for Y in range(2009,2026):
    a=[s['avg'] for p in MA.data for s in p.get('scoring') or [] if s['year']==Y and s['games']>=6]
    if a: era[Y]=float(np.mean(a))
REF=float(np.mean(list(era.values()))); eadj=lambda y,a:a*REF/era.get(y,REF)
def realized_prod(p):
    s=sorted([eadj(x['year'],x['avg']) for x in p['scoring'] if x['games']>=6],reverse=True)[:3]
    return float(np.mean(s)) if s else 0.0
# real native rostered players, grouped by position x tenure. survivorship-clean: only players still playing (not delisted)
live=[p for p in MA.data if p.get('type')=='ND' and MA.GRP.get(p.get('pos')) and not (p.get('_retired') or (p.get('_last_listed') and p['_last_listed']<2026)) and p.get('scoring')]
print(f"live native n={len(live)}")
print("=== engine VALUE by tenure (normalised to position yr3-4 median=100); flat = early-career value priced consistently ===")
for pos in ['MID','KEY_FWD','GEN_FWD','KEY_DEF','GEN_DEF','RUC']:
    grp={}
    for p in live:
        if MA.gfut(p)!=pos: continue
        T=PR.tenure(p,2026)
        if not (1<=T<=6): continue
        try: e=ev(p)
        except: continue
        grp.setdefault(T,[]).append(e)
    base=np.median(grp.get(3,grp.get(2,[100]))+grp.get(4,[])) or 100
    line=" ".join(f"T{t}:{np.median(grp[t])/base*100:4.0f}({len(grp[t])})" for t in range(1,7) if t in grp and len(grp[t])>=3)
    print(f"  {pos:8s} {line}")
print("  (~100 across T1..6 = flat/consistent; rising = under-pricing young; falling = over-pricing young)")
# value vs realized production correlation (engine tracks reality)
EV=[];PR_=[]
for p in live:
    if PR.tenure(p,2026)<3: continue
    try: e=ev(p)
    except: continue
    EV.append(e); PR_.append(realized_prod(p))
print(f"\n  corr(engine value, realized production) over {len(EV)} mature live players = {np.corrcoef(EV,PR_)[0,1]:.3f}")
