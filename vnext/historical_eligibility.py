"""Reviewed DraftGuru historical list-eligibility source for TASK-003."""
from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pandas as pd

from benchmark import EligibilityDecision

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "historical"
MATRIX_NAME = "historical_eligibility_2018_2024.csv"
KEYS_NAME = "database_player_keys.csv"
EXCLUSIONS_NAME = "draftguru_players_excluded_from_repository_mapping.csv"
EXPECTED_ORIGINS = tuple(range(2018, 2025))


def _decode_csv(data_dir: Path, name: str, manifest: dict[str, Any]) -> bytes:
    source = data_dir / f"{name}.gz.b64"
    encoded = "".join(source.read_text(encoding="ascii").split())
    raw = gzip.decompress(base64.b64decode(encoded, validate=True))
    expected = manifest["files"][name]
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected["sha256"]:
        raise ValueError(f"historical eligibility hash mismatch for {name}")
    if len(raw) != int(expected["bytes"]):
        raise ValueError(f"historical eligibility byte-count mismatch for {name}")
    return raw


def _read_csv_bytes(raw: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)


class DraftGuruEligibilityResolver:
    """Resolve one repository player/origin from reviewed DraftGuru evidence."""

    def __init__(self, data_dir: Path | str = DEFAULT_DATA_DIR):
        self.data_dir = Path(data_dir)
        self.manifest = json.loads((self.data_dir / "final_manifest.json").read_text(encoding="utf-8"))
        self.summary = json.loads((self.data_dir / "finalization_summary.json").read_text(encoding="utf-8"))
        self.matrix_bytes = _decode_csv(self.data_dir, MATRIX_NAME, self.manifest)
        self.keys_bytes = _decode_csv(self.data_dir, KEYS_NAME, self.manifest)
        self.exclusions_bytes = _decode_csv(self.data_dir, EXCLUSIONS_NAME, self.manifest)
        self.matrix = _read_csv_bytes(self.matrix_bytes)
        self.database_keys = _read_csv_bytes(self.keys_bytes)
        self.identity_exclusions = _read_csv_bytes(self.exclusions_bytes)
        self._validate()
        self._rows = {
            (str(row.player_key), int(row.origin_year)): row._asdict()
            for row in self.matrix.itertuples(index=False)
        }

    @property
    def matrix_sha256(self) -> str:
        return hashlib.sha256(self.matrix_bytes).hexdigest()

    def _validate(self) -> None:
        required = {
            "player_key",
            "database_name",
            "origin_year",
            "eligible",
            "decision_method",
            "club",
            "draftguru_player_slug",
            "draftguru_name",
            "source_url",
        }
        missing = sorted(required - set(self.matrix.columns))
        if missing:
            raise ValueError(f"historical eligibility matrix missing columns: {missing}")

        if self.matrix.duplicated(["player_key", "origin_year"]).any():
            sample = self.matrix.loc[
                self.matrix.duplicated(["player_key", "origin_year"], keep=False),
                ["player_key", "origin_year"],
            ].head(5).to_dict("records")
            raise ValueError(f"duplicate historical eligibility rows: {sample}")

        origins = set(self.matrix["origin_year"].astype(int))
        if origins != set(EXPECTED_ORIGINS):
            raise ValueError(f"historical eligibility origins differ from locked origins: {sorted(origins)}")

        valid_bools = {"True", "False"}
        if not set(self.matrix["eligible"]).issubset(valid_bools):
            raise ValueError("historical eligibility contains invalid boolean values")

        valid_methods = {"draftguru_verified_presence", "draftguru_verified_absence"}
        if not set(self.matrix["decision_method"]).issubset(valid_methods):
            raise ValueError("historical eligibility contains invalid decision methods")

        expected_keys = set(self.database_keys["player_key"])
        matrix_keys = set(self.matrix["player_key"])
        if matrix_keys != expected_keys:
            raise ValueError(
                "historical eligibility key universe mismatch: "
                f"missing={sorted(expected_keys - matrix_keys)[:5]} "
                f"extra={sorted(matrix_keys - expected_keys)[:5]}"
            )

        counts = self.matrix.groupby("player_key")["origin_year"].nunique()
        if len(counts) != len(expected_keys) or not (counts == len(EXPECTED_ORIGINS)).all():
            raise ValueError("every repository player key must have exactly seven eligibility origins")

        present = self.matrix[self.matrix["eligible"] == "True"]
        if (present["decision_method"] != "draftguru_verified_presence").any():
            raise ValueError("eligible rows must use draftguru_verified_presence")
        if (present[["club", "draftguru_player_slug", "draftguru_name", "source_url"]] == "").any(axis=None):
            raise ValueError("eligible rows must retain DraftGuru identity, club and source URL")

        absent = self.matrix[self.matrix["eligible"] == "False"]
        if (absent["decision_method"] != "draftguru_verified_absence").any():
            raise ValueError("ineligible rows must use draftguru_verified_absence")
        if (self.matrix["source_url"] == "").any():
            raise ValueError("every eligibility decision must retain a source URL")

        expected_rows = int(self.summary["matrix_rows"])
        if len(self.matrix) != expected_rows:
            raise ValueError(f"historical eligibility row count mismatch: {len(self.matrix)} != {expected_rows}")

    def evidence(self, player_key: str, origin_year: int) -> dict[str, Any]:
        key = (str(player_key), int(origin_year))
        if key not in self._rows:
            raise KeyError(f"historical eligibility unavailable for {key}")
        return dict(self._rows[key])

    def __call__(self, player: dict[str, Any], origin_year: int) -> EligibilityDecision:
        player_key = str(player.get("key") or player.get("player") or "")
        try:
            row = self.evidence(player_key, origin_year)
        except KeyError:
            return EligibilityDecision(None, "historical_eligibility_unavailable")
        eligible = row["eligible"] == "True"
        return EligibilityDecision(eligible, str(row["decision_method"]))

    def evidence_frame(self) -> pd.DataFrame:
        out = self.matrix.copy()
        out["origin_year"] = out["origin_year"].astype(int)
        out["eligible"] = out["eligible"].map({"True": True, "False": False})
        return out.sort_values(["origin_year", "player_key"]).reset_index(drop=True)


def load_historical_players(path: Path | str = ROOT / "engine" / "rl_after" / "rl_model_data.json") -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("players", "data", "active"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError("historical player data does not contain a recognised player list")
