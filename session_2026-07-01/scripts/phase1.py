import io,contextlib,copy
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; raw_ev=g['raw_ev']; iso=g['iso_corr']; nseas=g['nseas']; nqual=g.get('_nqual'); draftval=g['draftval']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
# candidates: established, on-pace 2026 (played ~all avail), full 2025
cand=[]
for p in MA.data:
    r26=g_y(p,2026); r25=g_y(p,2025)
    if not r26 or not r25: continue
    if not (11<=r26['games']<=14): continue
    if r25['games']<18: continue
    if nseas(p,2026)<6: continue
    try:
        v25=ev(p,2025); v26=ev(p,2026)
    except Exception: continue
    cand.append((v25-v26, p, r26, r25, v25, v26))
cand.sort(key=lambda t: t[0], reverse=True)
print(f"candidates (established, 2026 games 11-14, 2025>=18g, nseas>=6): {len(cand)}")
for drop,p,r26,r25,v25,v26 in cand[:6]:
    print(f"  {p['key']:22s} 25:{r25['games']}g/{r25.get('avg','?')} 26:{r26['games']}g/{r26.get('avg','?')}  ev25={v25} ev26={v26} drop={drop}")
# detail + counterfactual on #1
drop,p,r26,r25,v25,v26=cand[0]
print(f"\n=== TRACE {p['key']} ({MA.gfut(p)}) ===")
print("2026 record fields:", {k:r26[k] for k in r26})
print(f"scoring tail:", [(r['year'],r['games'],r.get('avg')) for r in p['scoring'] if r['year']>=2022])
print(f"ev25={v25}  ev26={v26}  DROP={v25-v26} ({100*(v25-v26)/v25:.1f}%)")
print(f"raw_ev25={raw_ev(p,2025):.1f}  raw_ev26={raw_ev(p,2026):.1f}")
print(f"iso={iso(MA.gfut(p),MA.effpk(p)):.4f} (Y-independent)")
print(f"nseas 25={nseas(p,2025)} 26={nseas(p,2026)} | nqual 25={nqual(p,2025)} 26={nqual(p,2026)}")
# COUNTERFACTUAL: 2026 games -> full-season equiv at SAME rate
q=copy.deepcopy(p); rec=g_y(q,2026); avg=rec.get('avg')
if avg is None and rec.get('total'): avg=rec['total']/rec['games']
FULL=22; rec['games']=FULL
if 'total' in rec and avg is not None: rec['total']=avg*FULL
vcf=ev(q,2026); rcf=raw_ev(q,2026)
print(f"\nCOUNTERFACTUAL 2026 set to {FULL}g at same avg({avg}): ev_cf={vcf}  raw_ev_cf={rcf:.1f}")
print(f"  gap closed vs ev25: ev26={v26} -> ev_cf={vcf} (target ev25={v25});  artifact size={vcf-v26}")
