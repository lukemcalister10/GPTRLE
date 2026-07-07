#!/usr/bin/env python3
"""SINGLE-SOURCE GUARD LIBRARY (DPP-strip build, 2026-07-05).

Enforces the SINGLE_SOURCE_INVARIANT: exactly ONE writable source of truth (the store
rl_model_data.json); every DERIVED artifact is written ONLY by its generator, stamped with the
source md5, and set read-only so it can never be hand-edited into a hidden divergence. This is the
permanent machinery behind the four guards (see SINGLE_SOURCE_INVARIANT.md). Every guard FAILS the
build (raises / non-zero exit) -- none warns.

Tiers of derived file:
  TIER-1 (per-build published outputs): board rl_app_data.json, book s4_matrix.json. Regenerated from
         the store EVERY build, stamped with the CURRENT source md5, startup-asserted (guard 2).
  TIER-2 (train-time caches): peak_model_v4.pkl, pvc_snapshot.json. Built rarely by the peak-model
         generator, deliberately FROZEN to break the SCALE<->PVC<->peak_est bootstrap cycle; stamped
         read-only with their OWN train-time source md5 (provenance), NOT per-build source-asserted
         (rebuilding them is a modelling action). The lookalike tripwire + read-only still protect them.
"""
import os, re, json, glob, hashlib, stat, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_NAME   = 'rl_model_data.json'
SOURCE_GLOB   = 'rl_model_data*.json'                       # the source pattern (guard 3 lookalike sweep)
LOOKALIKE_PAT = ['rl_model_data.json.*', 'rl_model_data*.bak', 'rl_model_data*.pre_stage0',
                 'rl_model_data*.stage0', 'rl_model_data*~']
TIER1_DERIVED = ['rl_app_data.json', 's4_matrix.json']     # board, book
TIER2_DERIVED = ['peak_model_v4.pkl', 'pvc_snapshot.json']  # train-time caches
# the ONLY files rl_model.py is permitted to open (source + classified authored inputs + frozen caches)
ALLOWED_OPENS = {SOURCE_NAME, 'params.json', 'rl_passmark.json',
                 'peak_model_v4.pkl', 'bust_prior_table.json', 'pvc_snapshot.json'}

def _hp(*p): return os.path.join(HERE, *p)
def _md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''): h.update(chunk)
    return h.hexdigest()

def source_md5(): return _md5(_hp(SOURCE_NAME))
def _stamp_path(path): return path + '.srcmd5'

def _chmod_writable(path):
    if os.path.exists(path):
        try: os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except OSError: pass

def prepare_write(name):
    """Call BEFORE a generator overwrites a derived file: clears the read-only bit so the write succeeds."""
    _chmod_writable(_hp(name)); _chmod_writable(_stamp_path(_hp(name)))

def stamp_derived(name, tier=1, srcmd5=None):
    """GUARD 1: the generator is the only writer. Stamp <name>.srcmd5 with the source md5 AND the derived
    file's own content md5, and set the file (and its stamp) READ-ONLY. The own-md5 makes GUARD 1 a real
    build-time FAIL even where the OS read-only bit is toothless (e.g. running as root): any post-generation
    hand-edit of the board/book changes its content md5 and is caught by assert_derived_integrity()."""
    path = _hp(name); srcmd5 = srcmd5 or source_md5()
    own = _md5(path)
    with open(_stamp_path(path), 'w') as f:
        json.dump({'source': SOURCE_NAME, 'source_md5': srcmd5, 'own_md5': own, 'derived': name, 'tier': tier},
                  f, sort_keys=True)
    ro = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    for p in (path, _stamp_path(path)):
        try: os.chmod(p, ro)
        except OSError: pass
    return srcmd5

def stamp_tier2_frozen(name):
    """TIER-2 (frozen train-time cache) stamp: record the cache's OWN md5 as provenance + tier=2 and set it
    read-only. NOT per-build source-asserted (the peak model + its train-time PVC are deliberately frozen to
    break the SCALE<->PVC<->peak_est bootstrap cycle; rebuilding them is a modelling action). The lookalike
    tripwire + read-only still forbid hand-edits / hidden copies."""
    path = _hp(name)
    if not os.path.exists(path): return None
    own = _md5(path)
    _chmod_writable(_stamp_path(path))
    with open(_stamp_path(path), 'w') as f:
        json.dump({'derived': name, 'tier': 2, 'frozen': True, 'own_md5': own,
                   'note': 'train-time cache; regenerated only by the peak-model build; not per-build source-asserted'},
                  f, sort_keys=True)
    ro = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    for p in (path, _stamp_path(path)):
        try: os.chmod(p, ro)
        except OSError: pass
    return own

def lock_tier2():
    """One-shot: stamp + read-only-lock all present tier-2 caches (idempotent)."""
    return {n: stamp_tier2_frozen(n) for n in TIER2_DERIVED if os.path.exists(_hp(n))}

def read_stamp(name):
    sp = _stamp_path(_hp(name))
    if not os.path.exists(sp): return None
    try: return json.load(open(sp)).get('source_md5')
    except Exception: return None

def read_own_stamp(name):
    sp = _stamp_path(_hp(name))
    if not os.path.exists(sp): return None
    try: return json.load(open(sp)).get('own_md5')
    except Exception: return None

def assert_derived_integrity(fail, consume):
    """GUARD 1 (content-integrity): each consumed derived artifact's CURRENT content md5 == its stamped
    own_md5 -> catches any post-generation hand-edit even under root (where the read-only bit is toothless)."""
    for name in consume:
        p = _hp(name)
        if not os.path.exists(p): continue
        cur = _md5(p); own = read_own_stamp(name)
        fail(cur == own, "GUARD 1 (content-integrity): %s content md5 %s != stamped own_md5 %s (derived artifact hand-edited)"
             % (name, cur, own))

def assert_single_source(fail):
    """GUARD 3: LOOKALIKE TRIPWIRE. Exactly ONE file matches the source pattern in the source dir; no
    .pre_stage0/.stage0/.bak/backup lookalikes. Any extra match -> FAIL (never warn)."""
    matches = [os.path.basename(p) for p in glob.glob(_hp(SOURCE_GLOB))
               if not p.endswith('.srcmd5')]
    fail(matches == [SOURCE_NAME],
         "GUARD 3 (lookalike tripwire): exactly one %s expected, found %s" % (SOURCE_GLOB, sorted(matches)))
    looks = []
    for pat in LOOKALIKE_PAT:
        looks += [os.path.basename(p) for p in glob.glob(_hp(pat)) if not p.endswith('.srcmd5')]
    fail(not looks, "GUARD 3 (lookalike tripwire): source lookalikes present: %s" % sorted(set(looks)))

def assert_stamps(fail, consume):
    """GUARD 2: SOURCE-HASH ASSERTION. Before a step CONSUMES a derived artifact, assert its stamp == the
    CURRENT source md5 -> HALT on mismatch (a stale/hand-edited board/book, or one built from an older
    store). Producers stamp AFTER writing (guard 1); consumers assert BEFORE reading (this)."""
    sm = source_md5()
    for name in consume:
        fail(os.path.exists(_hp(name)),
             "GUARD 2 (source-hash assertion): derived artifact %s missing (build it first)" % name)
        st = read_stamp(name)
        fail(st == sm, "GUARD 2 (source-hash assertion): %s stamped %s != current source md5 %s (stale/hand-edited derived artifact)"
             % (name, st, sm))

def assert_engine_opens(fail):
    """GUARD 3b: rl_model.py opens ONLY the source + classified inputs (no stray/lookalike reads)."""
    src = open(_hp('rl_model.py')).read()
    opens = set(re.findall(r"open\('([^']+)'", src))
    stray = [o for o in opens if o not in ALLOWED_OPENS]
    fail(not stray, "GUARD 3b: rl_model.py opens files outside the classified set: %s" % stray)
    fail(not any('stage0' in o for o in opens), "GUARD 3b: rl_model.py reads a *stage0* lookalike")

def assert_startup(consume=(), halt=True):
    """BUILD STEP GUARD: run the standing guards (3 lookalike + 3b opens) always, plus guard 2 (source-hash
    assertion) for each derived artifact in `consume` that this step is about to read. HALT (SystemExit,
    non-zero) on any violation -- never warn.
      rl_export  -> assert_startup()                              (produces the board; asserts no stamps)
      s4_matrix  -> assert_startup(consume=['rl_app_data.json'])  (consumes the board for F2 parity)
      self-test  -> assert_startup(consume=TIER1_DERIVED)         (consumes both)"""
    fails = []
    def fail(cond, msg):
        if not cond: fails.append(msg)
    assert_single_source(fail); assert_engine_opens(fail); assert_stamps(fail, consume); assert_derived_integrity(fail, consume)
    if fails:
        msg = "SINGLE-SOURCE STARTUP GUARD FAILED (build HALTED):\n  - " + "\n  - ".join(fails)
        if halt: raise SystemExit(msg)
        raise AssertionError(msg)
    return True

if __name__ == '__main__':
    assert_startup(consume=[n for n in TIER1_DERIVED if os.path.exists(_hp(n))], halt=True)
    print("single-source startup guards PASS (source md5 %s)" % source_md5())
