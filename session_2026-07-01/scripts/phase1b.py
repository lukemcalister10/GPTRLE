import io,contextlib,copy
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']; raw_ev=g['raw_ev']; nseas=g['nseas']
def g_y(p,y): return next((r for r in p['scoring'] if r['year']==y), None)
def cf_full(p,full=22):
    q=copy.deepcopy(p); rec=g_y(q,2026); avg=rec.get('avg')
    if avg is None and rec.get('total'): avg=rec['total']/rec['games']
    rec['games']=full
    if 'total' in rec and avg is not None: rec['total']=avg*full
    return ev(q,2026), raw_ev(q,2026)
# TRACE ed-richards
p=next(x for x in MA.data if x['key']=='ed-richards')
print("=== ed-richards ===", "pos", MA.gfut(p))
print("scoring tail:", [(r['year'],r['games'],r.get('avg')) for r in p['scoring'] if r['year']>=2021])
v25,v26=ev(p,2025),ev(p,2026)
print(f"ev25={v25} ev26={v26} drop={v25-v26} ({100*(v25-v26)/v25:.1f}%)  raw25={raw_ev(p,2025):.0f} raw26={raw_ev(p,2026):.0f}")
print(f"nseas25={nseas(p,2025)} nseas26={nseas(p,2026)}")
for fg in [14,18,22]:
    vcf,rcf=cf_full(p,fg); print(f"  cf 2026->{fg}g @same avg: ev={vcf} raw={rcf:.0f}  (lift vs ev26={vcf-v26:+d})")
# FLAT-RATE scan: established on-pace players whose 2026 rate ~= 2025 rate
print("\n=== FLAT-RATE on-pace subset (|avg26-avg25|<=6, 11-14g, 25>=18g, nseas>=6): does full-games lift them? ===")
rows=[]
for q in MA.data:
    r26=g_y(q,2026); r25=g_y(q,2025)
    if not r26 or not r25 or not (11<=r26['games']<=14) or r25['games']<18: continue
    if nseas(q,2026)<6: continue
    a25,a26=r25.get('avg'),r26.get('avg')
    if a25 is None or a26 is None or abs(a26-a25)>6: continue
    try: v25,v26=ev(q,2025),ev(q,2026)
    except: continue
    vcf,_=cf_full(q,22)
    rows.append((q['key'],a25,a26,v25,v26,vcf))
rows.sort(key=lambda t:t[3]-t[4],reverse=True)
print(f"{'key':20s} {'a25':>5s} {'a26':>5s} {'ev25':>5s} {'ev26':>5s} {'ev_cf22':>7s} {'drop%':>6s} {'cf_lift':>7s}")
for k,a25,a26,v25,v26,vcf in rows[:14]:
    print(f"{k:20s} {a25:>5.1f} {a26:>5.1f} {v25:>5d} {v26:>5d} {vcf:>7d} {100*(v25-v26)/v25:>5.0f}% {vcf-v26:>+7d}")
