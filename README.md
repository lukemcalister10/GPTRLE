# afl-rl-engine — AFL SuperCoach RL valuation engine

**Start here: `START_HERE.md`** (3-step resume: `bootstrap.sh` → `verify_restore.sh` → hold).

Canonical seed: final checkpoint 2026-07-02 from the retiring build chat.
- engine head: `c47cb43d` (BAKED v2.4: ruck cap 1.4 + REPL-1; was 8aed420a) · rl_model.py: `ce4468d6` · store: `644d1254` · band: `34faa865`
- source bundle: `rl_complete_8aed420a_final2026-07-02.tar.gz` (md5 `414706b0eb8b90d32c05f96c323dbc7b`)
- restore-verified in three environments (build container, offline clean extraction, repo-seeding container): 9 PASS / 0 FAIL, panel 10/10.

Process rules: `docs/process/`. Required external inputs: `REQUIRED_INPUTS.md`. Nothing bakes without Luke's explicit go.
