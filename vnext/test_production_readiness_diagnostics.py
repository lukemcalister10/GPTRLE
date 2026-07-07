from pathlib import Path
import pandas as pd

from production_readiness_diagnostics import main


def test_diagnostic_scaffold_reports_coverage_validity_and_deltas(tmp_path: Path):
    universe = tmp_path / "universe.csv"
    vnext = tmp_path / "vnext.csv"
    candidate = tmp_path / "candidate.csv"
    artifacts = tmp_path / "artifacts"; artifacts.mkdir(); (artifacts / "manifest.json").write_text('{"fit": false}')
    pd.DataFrame({"legacy_key": ["a", "b"], "player_name": ["A", "B"]}).to_csv(universe, index=False)
    pd.DataFrame({"key": ["a", "b"], "lead": [1, 1], "p_meaningful": [0.5, 0.6], "exp_points": [100, 200], "p80": [0.4, 0.5], "p90": [0.2, 0.3]}).to_csv(vnext, index=False)
    pd.DataFrame({"key": ["a"], "lead": [1], "p_meaningful": [0.7], "exp_points": [120], "p80": [0.45], "p90": [0.25]}).to_csv(candidate, index=False)

    assert main(["--universe", str(universe), "--vnext", str(vnext), "--candidate", str(candidate), "--artifacts", str(artifacts), "--out", str(tmp_path / "out")]) == 0

    cov = pd.read_csv(tmp_path / "out" / "coverage_summary.csv")
    assert cov.loc[cov.dataset == "candidate", "missing_from_dataset"].iloc[0] == 1
    comp = pd.read_csv(tmp_path / "out" / "compare_vnext_to_candidate.csv")
    assert comp.loc[0, "delta_exp_points"] == 20
    assert (tmp_path / "out" / "README.md").read_text().startswith("# Production readiness")
