# AFL RL Engine

A SuperCoach keeper-league forecasting and valuation project.

## Current project entry point
Read these in order:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/current/HANDOVER.md`](docs/current/HANDOVER.md)
3. [`docs/current/ROADMAP_TO_PRODUCTION.md`](docs/current/ROADMAP_TO_PRODUCTION.md)
4. the active task under [`docs/tasks/`](docs/tasks/)

## Two engines

### Legacy production engine
The current production implementation remains under `engine/rl_after/`. It is frozen during the challenger build and protected by `artifacts/legacy_manifest.json`.

The original Claude-era restoration and process instructions remain in `START_HERE.md` and related documents as historical/legacy operating material. They are not the governing workflow for vNext unless a rule has been carried into `AGENTS.md` or `docs/current/`.

### vNext challenger
`vnext/` contains the independent leakage-safe trajectory forecasting work through progress 05. It is not yet authorised to replace production.

## Setup

```bash
python -m pip install -r requirements-vnext.txt
python scripts/verify_legacy_manifest.py
cd vnext && pytest -q
```

Refresh the compact project handover after accepted changes:

```bash
python scripts/generate_handover.py
```

## Development rule
A challenger component replaces production only after it beats declared simple baselines and the legacy engine under the locked outcome-based protocol in `docs/current/VALIDATION_PROTOCOL.md`.
