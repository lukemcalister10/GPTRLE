"""cm TRAINER + REPL-NETTING UTILITY (post ONE-price, D4 2026-07-02).

HISTORY: this module held redesign_value() — the cont.25 consolidated board value chain (REPL−3 board
application, pedigree soft floor, Brodie ×0.5, lens tilt, RUCK_TAX on speculative ruck value) that the
TR.production_value router called for established players on the traded board. Luke's ONE-price ruling
(02/07/2026, in writing) DELETED the board valuation path: the board renders engine ev(). Per deleted
layer see BOARD_LAYERS_OBITUARY.md (magnitudes, rationale, deletion commit, resurrection refs).

WHAT REMAINS (engine dependencies, unchanged semantics):
  - REPL_DROP / REPL_DROP_PTS: the uniform −3 acquirable-replacement dial. The ENGINE applies it itself
    (its price6() lowers MA.REPL by REPL_DROP around dp.v_at_peak — _merged_recover.py); replacement-level
    netting was never board-only, so nothing needed promotion at the delete.
  - _price_repl: REPL-adjusted E[v] over a band — the shared netting utility (par_redesign.priceband and
    the par-derivation harnesses price through it).
  - build(): the conditional-prior cm trainer (component 1) — PR.retrain()/W.build() reach it.
"""
import sys; sys.path.insert(0,'/home/claude/rl_after')
import os; os.environ.setdefault('RL_GAMMA','0.85'); os.environ.setdefault('RL_PICK1','3000')
import io,contextlib,numpy as np,copy
import importlib.util
def _load(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()): s.loader.exec_module(m); return m
_HERE=os.path.dirname(__file__)
dp=_load('dp',os.path.join(_HERE,'distribution_pricing.py'))
cp=_load('cp',os.path.join(_HERE,'conditional_prior.py'))
MA=dp.MA

REPL_DROP_PTS = float(os.environ.get('RL_REPL_DROP','3'))   # acquirable-replacement recalibration, UNIFORM -3 (cont.25 dial).
# Per-group split (fwd -4 / other -2) REVERTED to uniform -3 (Luke, 2026-06-28): the DPP strip removes the forward-eligibility
# basis for the forward-specific extra. PLACEHOLDER -> re-validate the drop per position on the clean single-position base.
# NOTE: legacy env RL_REPL_DROP_FWD / RL_REPL_DROP_OTHER are now INERT (ignored); set RL_REPL_DROP to override.
REPL_DROP = {g: REPL_DROP_PTS for g in ['MID','GEN_DEF','GEN_FWD','KEY_DEF','KEY_FWD','RUC']}  # engine price6() applies this
# around dp.v_at_peak (MA.REPL lowered, saved/restored). 0 = netting against the unmodified replacement bar.

def _price_repl(p, band, scale, lens):                      # REPL-adjusted E[v] over a band (shared netting utility)
    if not REPL_DROP: return scale*float(np.dot(dp.WQ,[dp.v_at_peak(p,L,lens) for L in band]))
    _sav=dict(MA.REPL)
    try:
        for g in MA.REPL: MA.REPL[g]=_sav[g]-REPL_DROP.get(g,0)
        return scale*float(np.dot(dp.WQ,[dp.v_at_peak(p,L,lens) for L in band]))
    finally: MA.REPL.update(_sav)

def build(cap=2026, resolved_cut=2021):
    cmodels,_=cp.build_cond_prior(cap=cap, resolved_cut=resolved_cut)
    return cmodels
