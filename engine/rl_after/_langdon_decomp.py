import io, contextlib, copy
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
MA = g['MA']; ev = g['ev']

L = next(p for p in MA.data if p['player'] == 'Ed Langdon')
def fut(gdef, mid): return [["GDEF", float(gdef)], ["MID", float(mid)]]
def setL(pos_now, gdef, mid):
    L['_pos_now'] = pos_now; L['_fut'] = fut(gdef, mid)

print("as-loaded fields:", {k: L.get(k) for k in ['pos', '_pos_now', '_fut']})
base = ev(L)
print("as-loaded EV (fixed store):", base)

# ---- memoization probe: toggle, reprice, restore, reprice ----
saved = copy.deepcopy({k: L.get(k) for k in ['_pos_now', '_fut']})
L['_pos_now'] = 'GFWD'; v_probe = ev(L)
L['_pos_now'] = saved['_pos_now']; L['_fut'] = saved['_fut']; v_restore = ev(L)
print("PROBE _pos_now->GFWD:", v_probe, " | restored:", v_restore,
      "(round-trip OK)" if v_restore == base else "(!! MEMO/STATE ISSUE)")
print()

# ---- 2x2 ----
# columns: pos_now in {GFWD(old), GDEF(new)}; rows: _fut in {50/50(old), 70/30(new)}
grid = {}
for pos_now in ['GFWD', 'GDEF']:
    for (gd, md) in [(50, 50), (70, 30)]:
        setL(pos_now, gd, md)
        grid[(pos_now, (gd, md))] = ev(L)

# restore authoritative fixed state
setL('GDEF', 70, 30)
assert ev(L) == base, "failed to restore fixed state"

OLD  = grid[('GFWD', (50, 50))]   # anchor -> expect 1122
NEW  = grid[('GDEF', (70, 30))]   # anchor -> expect 593
BARo = grid[('GDEF', (50, 50))]   # _pos_now toggled alone
POLo = grid[('GFWD', (70, 30))]   # _fut toggled alone

print("2x2 grid (EV):")
print("                _fut 50/50 (OLD)   _fut 70/30 (NEW)")
print(f"  _pos_now GFWD(OLD)   {OLD:>8}          {POLo:>8}")
print(f"  _pos_now GDEF(NEW)   {BARo:>8}          {NEW:>8}")
print()
print(f"ANCHOR CHECK  OLD={OLD} (expect 1122: {'OK' if OLD==1122 else 'FAIL'})   NEW={NEW} (expect 593: {'OK' if NEW==593 else 'FAIL'})")
print()

dTot  = NEW - OLD
dBar1 = BARo - OLD          # BAR added first (from OLD)
dPol1 = POLo - OLD          # POLE added first (from OLD)
dBar2 = NEW  - POLo         # BAR added last (to POLE-only)
dPol2 = NEW  - BARo         # POLE added last (to BAR-only)
inter = dTot - dBar1 - dPol1

print(f"TOTAL move (OLD->NEW):            {dTot:+d}")
print(f"  BAR  (_pos_now GFWD->GDEF) alone from OLD: {dBar1:+d}")
print(f"  POLE (_fut 50/50->70/30)   alone from OLD: {dPol1:+d}")
print(f"  interaction (non-additivity):              {inter:+d}")
print()
print("order-dependence (with interaction present):")
print(f"  BAR  first {dBar1:+d}   last {dBar2:+d}   -> Shapley {0.5*(dBar1+dBar2):+.1f}")
print(f"  POLE first {dPol1:+d}   last {dPol2:+d}   -> Shapley {0.5*(dPol1+dPol2):+.1f}")
print()
sh_bar = 0.5*(dBar1+dBar2); sh_pol = 0.5*(dPol1+dPol2)
print(f"share of total move:  BAR {100*sh_bar/dTot:.0f}%   POLE {100*sh_pol/dTot:.0f}%   (Shapley split of {dTot:+d})")
