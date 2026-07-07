"""ENGINE cm PROVIDER (post ONE-price, D4 2026-07-02).

HISTORY: this module was the cont.27 BOARD SWITCH — its wire() overwrote every p['_v'] with the
TR.production_value router before export. Luke's ONE-price ruling (02/07/2026, in writing) DELETED the
board valuation path: the board now renders engine ev() directly (rl_export.py). Per deleted layer see
BOARD_LAYERS_OBITUARY.md (magnitudes, rationale, deletion commit, resurrection refs).

WHAT REMAINS (engine dependency, unchanged semantics): build() — train-or-load the PAR-CENTRED cm at the
env's RL_PRIOR_TREES (the cache at /home/claude/cm_<trees>.pkl is a pure speed optimisation: PR.retrain()
is deterministic, cache==retrain byte-for-byte). _merged_recover.py imports this module for W.build() and
reaches rd/cp/dp through W.TR (the tail_restore namespace spine).
"""
import io, contextlib, importlib.util, os, pickle
_FV = os.environ.get('RL_FV', '/home/claude/rl_workspace/forward_valuation')   # D10: parameterized (D8 mixed-pair root cause); default byte-identical
def _ld(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()): s.loader.exec_module(m); return m

# par_redesign (PR) is the par-centred chain; tail_restore (TR) is the bound namespace spine (rd/cp/dp).
PR = _ld('PR', os.path.join(_FV, 'par_redesign.py'))
TR = _ld('TR', os.path.join(_FV, 'tail_restore.py'))
TR.bind(PR)
rd = PR.rd; cp = PR.cp; dp = PR.dp; MA = PR.MA

_CM = None
def build():
    """Train (or load cached) the PAR-CENTRED cm at the env's RL_PRIOR_TREES. The cache is a pure speed optimisation:
    PR.retrain() is deterministic (PYTHONHASHSEED=0 + random_state=0 + fixed trees), so cache==retrain byte-for-byte."""
    global _CM
    if _CM is None:
        trees = os.environ.get('RL_PRIOR_TREES', '400')
        cache = f'/home/claude/cm_{trees}.pkl'
        cp._lvl_eff = PR.lvl_par                       # par-centred feature for INFERENCE (PR.retrain sets this for training)
        if os.path.exists(cache):
            with open(cache, 'rb') as fh: _CM = pickle.load(fh)
        else:
            with contextlib.redirect_stdout(io.StringIO()): _CM = PR.retrain()
            try:
                with open(cache, 'wb') as fh: pickle.dump(_CM, fh)
            except Exception: pass
    return _CM
