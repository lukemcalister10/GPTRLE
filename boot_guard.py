#!/usr/bin/env python3
"""BOOT-STORE GUARD — Guard 5 of the single-source family (stale-boot hardening, 2026-07-05).

WHY THIS EXISTS
  The four data guards (single_source.py) protect the DATA MODEL — one writable source, derived
  read-only + stamped, lookalike tripwire, correction canary. They do NOT protect which DIRECTORY a
  script reads: single_source.py resolves `HERE = dirname(__file__)`, so when it (and the self-test)
  run from the persistent workspace copy `/home/claude/rl_workspace/rl_after`, they validate the
  workspace against ITSELF and pass — even when the workspace holds a stale store (e.g. baked-v2.4
  644d1254) while the checked-out repo carries the real candidate (e1b4d8bf). That is the exact hole
  that produced hours of ghost premises. This guard closes it: it asserts, on ENTRY, that the store a
  script is about to read equals BOTH (a) the checked-out repo's store and (b) the pinned expected in
  data/expected_boot.json — and HALTS (non-zero) with a loud message otherwise. No script proceeds
  against an unverified store.

DESIGN
  - Repo-anchored, never workspace-anchored: the checkout is located via RL_REPO / CLAUDE_PROJECT_DIR /
    this file's own directory (boot_guard.py lives at the repo root and is always invoked from the
    checkout), NEVER by walking up from a workspace copy (which has no path back to the checkout).
  - The pinned expected md5s live in ONE place (data/expected_boot.json); this is the manual
    three-assertion check (engine head / store / band) made automatic and permanent.
  - FAILS the build (SystemExit / non-zero exit), never warns — consistent with guards 1-4.

USAGE
  Python:  import boot_guard; boot_guard.assert_boot('ship_gates', store_path=RA + '/rl_model_data.json')
  Shell:   python3 boot_guard.py <label> <store_path> [<engine_head_path> [<band_path>]]  || exit 1
"""
import os, sys, json, hashlib

def repo_root():
    """Locate the CHECKED-OUT repo, robustly, from anywhere (incl. a workspace cwd)."""
    for cand in (os.environ.get('RL_REPO'), os.environ.get('CLAUDE_PROJECT_DIR'),
                 os.path.dirname(os.path.abspath(__file__))):
        if cand and os.path.exists(os.path.join(cand, 'data', 'expected_boot.json')):
            return os.path.abspath(cand)
    # last resort: this file's dir (keeps a clear error if the manifest is genuinely absent)
    return os.path.dirname(os.path.abspath(__file__))

def _md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()

def expected(root=None):
    root = root or repo_root()
    with open(os.path.join(root, 'data', 'expected_boot.json')) as f:
        return json.load(f)

def _fmt(m):    # pinned file may hold either full md5 or 8-char; compare on the common prefix
    return (m or '')[:8]

def assert_boot(label, store_path=None, engine_head_path=None, band_path=None, halt=True):
    """Assert the store (and optionally engine head / band) a script is about to READ matches the
    checked-out repo AND the pinned expected. HALT (SystemExit) on any mismatch. Returns True on pass.

    label            : short name of the caller, quoted in the halt message (e.g. 'run_panel').
    store_path       : the rl_model_data.json the caller will actually read (the workspace copy for the
                       engine-loading scripts). REQUIRED for the store assertion.
    engine_head_path : optional _merged_recover.py the caller will read (three-assertion parity).
    band_path        : optional cm_400.pkl the caller will read.
    """
    root = repo_root()
    exp = expected(root)
    fails = []

    # (0) checkout integrity: the repo's own store must equal the pin. Catches a store swapped into the
    #     checkout without updating the pin (or a pin edited without re-baking) — either direction fails.
    repo_store = os.path.join(root, 'engine', 'rl_after', 'rl_model_data.json')
    repo_md5 = _md5(repo_store) if os.path.exists(repo_store) else None
    if _fmt(repo_md5) != _fmt(exp.get('store')):
        fails.append("checkout store %s != pinned store %s (data/expected_boot.json) — repo/pin out of sync"
                     % (_fmt(repo_md5), _fmt(exp.get('store'))))

    def _chk(kind, path, pin, ref_md5):
        if path is None:
            return
        if not os.path.exists(path):
            fails.append("%s to read %s at %s — FILE ABSENT (re-run bootstrap.sh to seed the workspace)"
                         % (label, kind, path)); return
        got = _md5(path)
        if _fmt(got) != _fmt(pin):
            fails.append("%s about to read %s\n        at %s\n        md5 %s  !=  expected %s (pinned; repo checkout %s)\n"
                         "        STALE BOOT: this is not the checked-out store. Re-run bootstrap.sh to re-seed the "
                         "workspace from the checked-out source; never boot on an unverified store."
                         % (label, kind, path, _fmt(got), _fmt(pin), _fmt(ref_md5)))

    _chk('STORE  rl_model_data.json', store_path,       exp.get('store'),       repo_md5)
    _chk('ENGINE _merged_recover.py', engine_head_path, exp.get('engine_head'), None)
    _chk('BAND   cm_400.pkl',         band_path,        exp.get('band'),        None)

    if fails:
        msg = ("\n==================== STALE-BOOT GUARD (Guard 5) FAILED — BUILD HALTED ====================\n"
               "  - " + "\n  - ".join(fails) +
               "\n=========================================================================================")
        if halt:
            raise SystemExit(msg)
        raise AssertionError(msg)
    print("boot-store guard (Guard 5) PASS  [%s]  store %s == pinned %s (%s)"
          % (label, _fmt(repo_md5), _fmt(exp.get('store')), exp.get('tag')))
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: boot_guard.py <label> <store_path> [<engine_head_path> [<band_path>]]", file=sys.stderr)
        sys.exit(2)
    _label = sys.argv[1]
    _store = sys.argv[2]
    _eng   = sys.argv[3] if len(sys.argv) > 3 else None
    _band  = sys.argv[4] if len(sys.argv) > 4 else None
    try:
        assert_boot(_label, store_path=_store, engine_head_path=_eng, band_path=_band, halt=True)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            sys.exit(1)
        raise
