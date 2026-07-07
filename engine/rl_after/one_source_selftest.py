#!/usr/bin/env python3
"""ONE-SOURCE SELF-TEST (DPP-strip final consolidation, 2026-07-05). Run from engine/rl_after (or the
bootstrapped workspace) under the panel env. Proves the board + book are regenerable from the SINGLE store,
that every published value equals the engine's gated ev(), and that the FOUR single-source guards hold.
Exits NON-ZERO (build FAILS) on any violation -- never warns.

Preconditions: build the board and book first, in this order --
    python3 rl_export.py            # writes rl_app_data.json (+ stamps read-only) ; F1 export<->engine gate
    python3 s4_matrix_M1v7.py       # writes s4_matrix.json  (+ stamps read-only) ; F2 book<->board gate
    python3 one_source_selftest.py  # this file: guards 1-3 + F1/F2 + data ground-truth + regenerability
    python3 guard_correction_canary.py   # GUARD 4 (full-rebuild correction-sticks canary), run separately

Checks:
  GUARD 3  single source: exactly one rl_model_data*.json, no lookalikes; engine opens only classified inputs
  GUARD 1  derived read-only + stamped: board + book are 0o444 and carry a .srcmd5 stamp
  GUARD 2  source-hash: each derived stamp == current source md5
  (1) engine loads from the single store; derived active == 805, keys unique
  (2) EXPORT PARITY (F1): board v == a freshly, independently recomputed engine gated ev(), key-for-key
  (3) BOOK PARITY  (F2): book cur == board v for every shared player
  (4) DATA GROUND TRUTH: Kako 2025 23@55.2 / 2026 6@55.0 ; Bontempelli 13-season track regenerated == source
  (5) POSITION MODEL: store carries drafted/present/future single-valued columns; raw_multipos GONE
"""
import io, os, re, sys, json, stat, contextlib
import single_source as SS

FAIL=[]
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ")+msg)
    if not cond: FAIL.append(msg)

HERE=os.path.dirname(os.path.abspath(__file__))
def hp(*p): return os.path.join(HERE,*p)

print("=== GUARD 5: BOOT-STORE (this dir's store == the checked-out, pinned store) ===")
# The four guards above validate whichever dir this file is imported from (HERE) against ITSELF — so a
# stale-but-self-consistent workspace passes them. GUARD 5 anchors on the CHECKOUT: it asserts HERE's store
# and engine head equal data/expected_boot.json in the repo. Fails the self-test (build) on a stale boot.
_repo=None
for _c in (os.environ.get('RL_REPO'), os.environ.get('CLAUDE_PROJECT_DIR'),
           os.path.abspath(os.path.join(HERE,'..','..'))):
    if _c and os.path.exists(os.path.join(_c,'boot_guard.py')): _repo=_c; break
if _repo:
    if _repo not in sys.path: sys.path.insert(0,_repo)
    import boot_guard as _BG
    try:
        _BG.assert_boot('one_source_selftest', store_path=hp('rl_model_data.json'),
                        engine_head_path=hp('_merged_recover.py'), halt=False)
        check(True, "GUARD 5: boot-store — this dir's store+head == pinned checkout store")
    except AssertionError as _e:
        _det=[l.strip() for l in str(_e).splitlines() if l.strip() and set(l.strip())!={'='} and 'HALTED' not in l]
        check(False, "GUARD 5: boot-store FAILED — %s"%(' '.join(_det) if _det else "boot-store mismatch"))
else:
    check(False, "GUARD 5: cannot locate the checkout (set RL_REPO/CLAUDE_PROJECT_DIR) to verify the boot store")

print("=== GUARD 3: SINGLE SOURCE (lookalike tripwire + engine opens) ===")
_g3=[]
SS.assert_single_source(lambda c,m: _g3.append(m) if not c else None)
SS.assert_engine_opens(lambda c,m: _g3.append(m) if not c else None)
for m in _g3: check(False, m)
check(not _g3, "exactly one rl_model_data*.json, no lookalikes, engine opens only classified inputs")

print("=== GUARD 1 + GUARD 2: derived files read-only + source-md5-stamped + content-intact ===")
_sm=SS.source_md5()
for _name in SS.TIER1_DERIVED:
    _p=hp(_name)
    if not os.path.exists(_p): check(False, "%s present (build it first)"%_name); continue
    _mode=stat.S_IMODE(os.stat(_p).st_mode)
    check(not (_mode & stat.S_IWUSR), "GUARD 1: %s is read-only (mode %o)"%(_name,_mode))
    check(os.path.exists(SS._stamp_path(_p)), "GUARD 1: %s carries a .srcmd5 stamp"%_name)
    check(SS._md5(_p)==SS.read_own_stamp(_name), "GUARD 1: %s content md5 == stamped own_md5 (not hand-edited)"%_name)
    check(SS.read_stamp(_name)==_sm, "GUARD 2: %s stamp == current source md5 %s"%(_name,_sm[:8]))
print("       source md5 = %s"%_sm)

print("=== (1) ENGINE LOADS from the single store; active == 805 ===")
g={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(hp('_merged_recover.py')).read().split('print("=== AFTER')[0], g)
MA=g['MA']; ev=g['ev']
active_keys=[p['key'] for p in MA.players]
check(len(active_keys)==805, "engine active players == 805 (got %d)"%len(active_keys))
check(len(set(active_keys))==len(active_keys), "active keys unique")

print("=== (2) EXPORT PARITY (F1): board v == independently recomputed engine gated ev(), key-for-key ===")
board_path=os.environ.get('RL_APP_DATA','rl_app_data.json')
if not os.path.exists(board_path):
    check(False, "board %s present (run rl_export.py first)"%board_path)
else:
    board={r['key']:r['v'] for r in json.load(open(board_path))['active']}
    check(set(board)==set(active_keys), "board active set == engine active set, key-for-key")
    gated={}
    with contextlib.redirect_stdout(io.StringIO()):
        for p in MA.players:
            v=ev(p,2026); ev(p,2024); ev(p,2025); ev(p,2027); ev(p,2028)   # replicate the export's as-of sequence
            gated[p['key']]=v
    mism=[(k,board[k],gated.get(k)) for k in board if board[k]!=gated.get(k)]
    check(not mism, "every board v == engine gated ev (F1); mismatches=%d %s"%(len(mism),mism[:8]))

print("=== (3) BOOK PARITY (F2): book cur == board v for shared players ===")
book_path=os.environ.get('S4_MATRIX','s4_matrix.json')
if not os.path.exists(book_path):
    check(False, "book %s present (run s4_matrix_M1v7.py first)"%book_path)
elif os.path.exists(board_path):
    book={v['key']:v.get('cur') for v in json.load(open(book_path)).values() if v.get('key')}
    board={r['key']:r['v'] for r in json.load(open(board_path))['active']}
    shared=[k for k in board if k in book]
    absent=[k for k in board if k not in book]
    bmis=[(k,book[k],board[k]) for k in shared if book[k]!=board[k]]
    check(not bmis, "every shared book cur == board v (F2); mismatches=%d %s"%(len(bmis),bmis[:8]))
    print("       (%d board players outside the cohort book, _pvc_exclude: %s)"%(len(absent),sorted(absent)))

print("=== (4) DATA GROUND TRUTH: Kako + Bontempelli regenerated from source ===")
store=json.load(open(hp('rl_model_data.json')))
kako=[p for p in store if p['key']=='isaac-kako']
check(len(kako)==1, "exactly one isaac-kako in the store")
if kako:
    ksc={r['year']:(r['games'],r['avg']) for r in kako[0]['scoring']}
    check(ksc.get(2025)==(23,55.2), "Kako 2025 == 23 games @ 55.2 (owner ground truth); got %s"%(ksc.get(2025),))
    check(ksc.get(2026)==(6,55.0),  "Kako 2026 == 6 games @ 55.0; got %s"%(ksc.get(2026),))
bont=[p for p in store if p['key']=='marcus-bontempelli']
check(len(bont)==1, "exactly one marcus-bontempelli in the store")
if bont:
    src=sorted(((r['year'],r['avg'],r['games']) for r in bont[0]['scoring']))
    ep=[p for p in MA.data if p['key']=='marcus-bontempelli'][0]
    regen=sorted(((r['year'],r['avg'],r['games']) for r in ep['scoring']))
    check(len(src)==13, "Bontempelli has 13 seasons in source (got %d)"%len(src))
    check(src==regen, "regenerated 13-season track == source, season-for-season")
    print("       Bontempelli seasons %s..%s  first=%s last=%s"%(src[0][0],src[-1][0],src[0],src[-1]))

print("=== (5) POSITION MODEL: three single-valued columns; DPP blend GONE ===")
_keys=set(); [_keys.update(p.keys()) for p in store]
check('drafted_position' in _keys and 'present_position' in _keys and 'future_position' in _keys,
      "store carries drafted_position + present_position + future_position")
check('raw_multipos' not in _keys, "raw_multipos (the DPP blend) is GONE from the store")
_multi=[p['key'] for p in store if isinstance(p.get('present_position'),list) or isinstance(p.get('future_position'),list)]
check(not _multi, "present/future positions are single-valued (no list legs); offenders=%s"%_multi[:5])
# in THIS build future == present for every record (the seam resolves identically now)
_seam=[p['key'] for p in store if p.get('future_position')!=p.get('present_position')]
check(not _seam, "future_position == present_position for every record this build; offenders=%s"%_seam[:5])

print("\n"+("SELF-TEST FAILED: %d check(s)\n  - "%len(FAIL)+"\n  - ".join(FAIL) if FAIL else
      "SELF-TEST PASSED: single source; guards 1-3; board==engine (F1); book==board (F2); Kako+Bontempelli ground-truth; DPP blend stripped."))
print("  (GUARD 4 — correction-sticks canary — runs separately: python3 guard_correction_canary.py)")
sys.exit(1 if FAIL else 0)
