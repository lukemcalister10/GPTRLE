"""Owner-independent smooth positional scarcity premium.

The premium is derived from global league cut lines.  It is additive to intrinsic
forecast value, uses only current official eligibility, and remains smooth below the
optimal 368-player allocation so non-selected players are not forced to zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ScarcityPolicy:
    bandwidth: float = 40.0
    premium_scale: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.bandwidth) or self.bandwidth <= 0:
            raise ValueError("bandwidth must be finite and positive")
        if not isfinite(self.premium_scale) or self.premium_scale < 0:
            raise ValueError("premium_scale must be finite and non-negative")


DEFAULT_SCARCITY_POLICY = ScarcityPolicy()


@dataclass(frozen=True, slots=True)
class ScarcityResult:
    intrinsic_value: float
    scarcity_premium: float
    combined_value: float
    best_position: str | None


def _logistic_activation(value: float, cut_line: float, bandwidth: float) -> float:
    z = (value - cut_line) / bandwidth
    if z >= 0:
        return 1.0 / (1.0 + exp(-z))
    exp_z = exp(z)
    return exp_z / (1.0 + exp_z)


def scarcity_premium(
    *,
    intrinsic_value: float,
    eligible_positions: frozenset[str],
    position_cut_lines: Mapping[str, float],
    unrestricted_cut_line: float,
    policy: ScarcityPolicy = DEFAULT_SCARCITY_POLICY,
) -> ScarcityResult:
    """Return the best smooth scarcity premium available through eligibility.

    For each eligible position:

    ``scarcity gap = max(0, position cut line - unrestricted cut line)``

    The gap is multiplied by a logistic activation centred on that position's cut
    line.  Additional positions are not summed; the best eligible premium is used to
    avoid double-counting production or awarding a symmetric DPP bonus.
    """

    if not isfinite(intrinsic_value):
        raise ValueError("intrinsic_value must be finite")
    if not eligible_positions:
        raise ValueError("eligible_positions must be non-empty")
    if not isfinite(unrestricted_cut_line):
        raise ValueError("unrestricted_cut_line must be finite")

    candidates: list[tuple[float, str]] = []
    for position in sorted(eligible_positions):
        if position not in position_cut_lines:
            raise KeyError(f"missing cut line for {position}")
        cut_line = float(position_cut_lines[position])
        if not isfinite(cut_line):
            raise ValueError(f"cut line must be finite for {position}")
        gap = max(0.0, cut_line - unrestricted_cut_line)
        activation = _logistic_activation(intrinsic_value, cut_line, policy.bandwidth)
        candidates.append((policy.premium_scale * gap * activation, position))

    premium, position = max(candidates, key=lambda item: (item[0], item[1]))
    if premium == 0:
        position = None
    return ScarcityResult(
        intrinsic_value=intrinsic_value,
        scarcity_premium=premium,
        combined_value=intrinsic_value + premium,
        best_position=position,
    )
