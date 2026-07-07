#!/usr/bin/env python3
"""
D15 v2 verification — shared engine harness.

Runs a named engine tree (CONTROL / v2.3 / v2.4) in an ISOLATED subprocess so no
two trees ever share a Python interpreter (module cache) inside one computation.
Each tree is materialised by `git archive <sha>` of the FULL engine/rl_after +
engine/forward_valuation subtrees, so wire_redesign.py / par_redesign.py / etc.
travel with their _merged_recover.py (they differ across trees; mixing them would
be tree-mixing). The engine-file md5 is asserted against the pinned value before
any computation runs.

Reproducible from a fresh clone of fa6abd0: this file only needs the three commits
(all ancestors of fa6abd0) and the pinned venv. The prior model `cm` is seeded from
the committed data/cm_400.pkl (md5 34faa865) for speed; if that cache is absent the
engine deterministically retrains it byte-for-byte (PYTHONHASHSEED=0 + random_state=0).
"""
import os, sys, io, json, shutil, hashlib, tempfile, subprocess

# Pinned run environment (relay STEP 0). RL_RUC_PRIOR_CAP left at its 1.73 default.
PINS = dict(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
            RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')

# label -> (git sha, expected _merged_recover.py md5[:8])
TREES = {
    'CONTROL': ('f4a4d34', '8aed420a'),   # canonical control (git "Initial verified seed", head 8aed420a)
    'v2.3':    ('def39f5', 'f3e537ba'),   # PR #17 head
    'v2.4':    ('fa6abd0', '7c199a1f'),   # this branch HEAD (D14 curve + KPP floor)
}


def repo_root():
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()


def ensure_cm_cache(root):
    """Seed /home/claude/cm_<trees>.pkl from the committed data cache (speed only)."""
    trees = PINS['RL_PRIOR_TREES']
    cache = f'/home/claude/cm_{trees}.pkl'
    src = os.path.join(root, 'data', f'cm_{trees}.pkl')
    if not os.path.exists(cache) and os.path.exists(src):
        try:
            os.makedirs('/home/claude', exist_ok=True)
            shutil.copy(src, cache)
        except Exception:
            pass  # engine will deterministically retrain -> byte-identical


def materialize(sha, root):
    """git archive the tree's engine subtrees into a fresh tempdir; assert nothing.
    Returns (rundir, engine_md5)."""
    d = tempfile.mkdtemp(prefix=f'd15_{sha[:7]}_')
    tar = subprocess.run(['git', 'archive', sha, 'engine/rl_after', 'engine/forward_valuation'],
                         cwd=root, stdout=subprocess.PIPE, check=True).stdout
    subprocess.run(['tar', '-x', '-C', d], input=tar, check=True)
    ra = os.path.join(d, 'engine', 'rl_after')
    md5 = hashlib.md5(open(os.path.join(ra, '_merged_recover.py'), 'rb').read()).hexdigest()[:8]
    return d, md5


def tree_env(rundir, root):
    e = dict(os.environ)
    e.update(PINS)
    e['RL_FV'] = os.path.join(rundir, 'engine', 'forward_valuation')
    e['PYTHONPATH'] = os.path.join(rundir, 'engine', 'rl_after') + os.pathsep + os.path.join(root, 'vendor')
    return e


_WORKER = r'''
import io, contextlib, json, sys, hashlib
BOARD_PATH = __BOARD__
src = open('_merged_recover.py').read()
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(src.split('print("=== AFTER')[0], g)
g['_ENG_MD5'] = hashlib.md5(src.encode()).hexdigest()[:8]
g['_BOARD_PATH'] = BOARD_PATH
with contextlib.redirect_stdout(io.StringIO()):
    exec(__PROBE__, g)
sys.stdout.write("<<<D15JSON>>>" + json.dumps(g['RESULT']))
'''


def run_tree(label, probe_code, board_path=True, root=None, timeout=600):
    """Load engine tree `label` in an isolated subprocess, exec `probe_code` in the
    engine globals (which must set `RESULT`), return (RESULT, engine_md5, sha).
    Asserts the engine md5 against TREES before running."""
    root = root or repo_root()
    ensure_cm_cache(root)
    sha, exp = TREES[label]
    rundir, md5 = materialize(sha, root)
    assert md5 == exp, f"{label}: engine md5 {md5} != expected {exp} (tree assertion FAILED)"
    ra = os.path.join(rundir, 'engine', 'rl_after')
    code = _WORKER.replace('__BOARD__', repr(bool(board_path))).replace('__PROBE__', repr(probe_code))
    try:
        out = subprocess.run([sys.executable, '-c', code], cwd=ra, env=tree_env(rundir, root),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    finally:
        shutil.rmtree(rundir, ignore_errors=True)
    if '<<<D15JSON>>>' not in out.stdout:
        raise RuntimeError(f"{label} probe FAILED (rc={out.returncode})\n"
                           f"--- STDOUT tail ---\n{out.stdout[-3000:]}\n"
                           f"--- STDERR tail ---\n{out.stderr[-3000:]}")
    return json.loads(out.stdout.split('<<<D15JSON>>>')[1]), md5, sha
