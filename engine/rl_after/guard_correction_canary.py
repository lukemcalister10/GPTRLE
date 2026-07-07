#!/usr/bin/env python3
"""GUARD 4 — CORRECTION-STICKS CANARY (DPP-strip build, 2026-07-05).

Proves the Kako class ("data that lives outside the one store") is DEAD: write a throwaway edit to the
SOURCE store, run a FULL rebuild (board + book), and assert the edit SURVIVES all the way to both derived
artifacts. If any generator re-injects / overrides / ignores the store (the way the old book-local Kako
patch did), the sentinel will NOT move and the guard FAILS the build. The source + all derived artifacts +
stamps are restored byte-for-byte afterwards, so the canary is side-effect-free.

Run from the workspace under the panel env:  python3 guard_correction_canary.py
"""
import os, sys, json, subprocess, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
def hp(*p): return os.path.join(HERE, *p)
# backups live OUTSIDE the source dir -- a *.canarybak next to the store would (correctly) trip the
# lookalike tripwire (guard 3), so we stage them in a temp dir instead.
BAKDIR = os.path.join(tempfile.gettempdir(), 'dpp_canary_bak')
STORE = hp('rl_model_data.json')
BOARD = hp('rl_app_data.json')
BOOK  = hp('s4_matrix.json')
SENTINEL_KEY = 'josh-ward'          # a stable, active, mid-value board+book player (form-responsive)
BUMP = 40.0                         # a large, unmistakable avg bump on his latest qualifying season

FAIL = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond: FAIL.append(msg)

def _backup(path):
    os.makedirs(BAKDIR, exist_ok=True)
    b = os.path.join(BAKDIR, os.path.basename(path) + '.canarybak')   # OUTSIDE the source dir (no lookalike trip)
    if os.path.exists(path):
        try: os.chmod(path, 0o644)
        except OSError: pass
        shutil.copy2(path, b)
        return b
    return None

def _restore(path, b):
    if b and os.path.exists(b):
        try:
            if os.path.exists(path): os.chmod(path, 0o644)
        except OSError: pass
        shutil.copy2(b, path); os.remove(b)

def _env():
    e = dict(os.environ)
    e.setdefault('PYTHONHASHSEED', '0')
    return e

def _rebuild():
    for script in ('rl_export.py', 's4_matrix_M1v7.py'):
        r = subprocess.run([sys.executable, script], cwd=HERE, env=_env(),
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if r.returncode != 0:
            return False, "%s failed: %s" % (script, r.stderr.decode()[-500:])
    return True, ''

def _board_val(key):
    d = json.load(open(BOARD))['active']
    for r in d:
        if r['key'] == key: return r['v']
    return None

def _book_val(key):
    d = json.load(open(BOOK))
    for v in d.values():
        if v.get('key') == key: return v.get('cur')
    return None

def main():
    print("=== GUARD 4: correction-sticks canary (full rebuild; sentinel=%s +%.0f) ===" % (SENTINEL_KEY, BUMP))
    # baseline: use the current board+book if present (a fresh build precedes this in the pipeline), else rebuild
    if not (os.path.exists(BOARD) and os.path.exists(BOOK)):
        ok, err = _rebuild()
        if not ok: check(False, "baseline rebuild: " + err); return _finish()
    base_board = _board_val(SENTINEL_KEY); base_book = _book_val(SENTINEL_KEY)
    check(base_board is not None, "sentinel %s present on the board (baseline v=%s)" % (SENTINEL_KEY, base_board))
    check(base_book is not None, "sentinel %s present in the book (baseline cur=%s)" % (SENTINEL_KEY, base_book))
    if base_board is None or base_book is None: return _finish()

    # backups (store + derived + their stamps)
    baks = {p: _backup(p) for p in (STORE, BOARD, BOOK, BOARD + '.srcmd5', BOOK + '.srcmd5')}
    try:
        # throwaway edit to the SOURCE: bump the sentinel's latest qualifying (>=6g) season avg by BUMP
        store = json.load(open(STORE))
        p = next((x for x in store if x.get('key') == SENTINEL_KEY), None)
        if p is None: check(False, "sentinel not in store"); return _finish(baks)
        qual = sorted([r for r in p['scoring'] if r['games'] >= 6], key=lambda r: r['year'])
        if not qual: check(False, "sentinel has no qualifying season to edit"); return _finish(baks)
        edit_year = qual[-1]['year']; orig_avg = qual[-1]['avg']
        for r in p['scoring']:
            if r['year'] == edit_year: r['avg'] = orig_avg + BUMP
        os.chmod(STORE, 0o644)
        json.dump(store, open(STORE, 'w'))
        print("  edited store: %s %d avg %.1f -> %.1f" % (SENTINEL_KEY, edit_year, orig_avg, orig_avg + BUMP))

        ok, err = _rebuild()
        if not ok: check(False, "post-edit rebuild: " + err); return _finish(baks)
        new_board = _board_val(SENTINEL_KEY); new_book = _book_val(SENTINEL_KEY)
        # the edit must SURVIVE to BOTH board and book (value moves up materially)
        check(new_board is not None and new_board > base_board,
              "edit SURVIVES to the BOARD: %s v %s -> %s (must rise)" % (SENTINEL_KEY, base_board, new_board))
        check(new_book is not None and new_book > base_book,
              "edit SURVIVES to the BOOK: %s cur %s -> %s (must rise)" % (SENTINEL_KEY, base_book, new_book))
        # board==book parity must still hold on the edited sentinel (single-source coherence)
        check(new_board == new_book, "edited sentinel board==book (%s vs %s)" % (new_board, new_book))
    finally:
        for path, b in baks.items(): _restore(path, b)
        _rebuild()   # restore clean derived artifacts from the restored store
    return _finish()

def _finish(baks=None):
    if baks:
        for path, b in baks.items(): _restore(path, b)
    if FAIL:
        print("\nGUARD 4 FAILED: %d check(s)\n  - %s" % (len(FAIL), "\n  - ".join(FAIL)))
        sys.exit(1)
    print("\nGUARD 4 PASSED: a source correction sticks all the way to board + book (Kako class is dead).")
    sys.exit(0)

if __name__ == '__main__':
    main()
