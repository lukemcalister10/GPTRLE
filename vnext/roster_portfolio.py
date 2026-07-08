"""Roster portfolio roles for contender, balanced and rebuilder teams.

A player's market/asset value is not the same thing as the value of occupying a
specific roster slot.  This module keeps those concepts separate so a valuable player
who does not improve a contender's best side becomes a trade candidate rather than a
false automatic keeper or cut.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Iterable, Mapping


class PortfolioRole(StrEnum):
    CORE = "core"
    EMERGENCY_DEPTH = "emergency_depth"
    DEVELOPMENT = "development"
    TRADE_CANDIDATE = "trade_candidate"
    CUT_CANDIDATE = "cut_candidate"


@dataclass(frozen=True, slots=True)
class PortfolioProfile:
    name: str
    core_size: int
    emergency_depth_size: int
    future_asset_weight: float
    trade_asset_weight: float
    stranded_asset_penalty: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("profile name must be non-empty")
        if self.core_size < 23:
            raise ValueError("core_size must cover the 23-player scoring lineup")
        if self.emergency_depth_size < 0:
            raise ValueError("emergency_depth_size must be non-negative")
        for field_name in (
            "future_asset_weight",
            "trade_asset_weight",
            "stranded_asset_penalty",
        ):
            value = getattr(self, field_name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{field_name} must be finite and non-negative")


CONTENDER_PORTFOLIO = PortfolioProfile(
    name="contender",
    core_size=26,
    emergency_depth_size=6,
    future_asset_weight=0.15,
    trade_asset_weight=0.85,
    stranded_asset_penalty=0.75,
)
BALANCED_PORTFOLIO = PortfolioProfile(
    name="balanced",
    core_size=27,
    emergency_depth_size=7,
    future_asset_weight=0.45,
    trade_asset_weight=0.65,
    stranded_asset_penalty=0.35,
)
REBUILDER_PORTFOLIO = PortfolioProfile(
    name="rebuilder",
    core_size=23,
    emergency_depth_size=5,
    future_asset_weight=0.90,
    trade_asset_weight=0.80,
    stranded_asset_penalty=0.10,
)

DEFAULT_PORTFOLIO_PROFILES: Mapping[str, PortfolioProfile] = {
    profile.name: profile
    for profile in (CONTENDER_PORTFOLIO, BALANCED_PORTFOLIO, REBUILDER_PORTFOLIO)
}


@dataclass(frozen=True, slots=True)
class PortfolioPlayer:
    player_id: str
    lineup_utility: float
    emergency_utility: float
    future_asset_utility: float
    trade_utility: float
    in_best_23: bool = False
    in_extended_core: bool = False
    required_positional_cover: bool = False

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        for field_name in (
            "lineup_utility",
            "emergency_utility",
            "future_asset_utility",
            "trade_utility",
        ):
            if not isfinite(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be finite")


def classify_portfolio_role(
    player: PortfolioPlayer,
    profile: PortfolioProfile,
    *,
    cut_threshold: float = 0.0,
    trade_threshold: float = 0.0,
    development_threshold: float = 0.0,
) -> PortfolioRole:
    """Classify a player by roster function rather than one scalar keeper rank.

    Thresholds are explicit diagnostic parameters.  They must be calibrated before
    production use.
    """

    if player.in_best_23 or player.in_extended_core:
        return PortfolioRole.CORE
    if player.required_positional_cover or player.emergency_utility > cut_threshold:
        # Valuable non-core assets still become trade candidates when their market
        # value materially exceeds their emergency role for a contender.
        stranded_value = max(player.trade_utility, player.future_asset_utility)
        if (
            profile.stranded_asset_penalty > 0
            and stranded_value * profile.stranded_asset_penalty
            > player.emergency_utility
            and player.trade_utility > trade_threshold
        ):
            return PortfolioRole.TRADE_CANDIDATE
        return PortfolioRole.EMERGENCY_DEPTH

    weighted_future = profile.future_asset_weight * player.future_asset_utility
    weighted_trade = profile.trade_asset_weight * player.trade_utility
    if weighted_trade > trade_threshold:
        return PortfolioRole.TRADE_CANDIDATE
    if weighted_future > development_threshold:
        return PortfolioRole.DEVELOPMENT
    return PortfolioRole.CUT_CANDIDATE


def classify_roster(
    players: Iterable[PortfolioPlayer],
    profile: PortfolioProfile,
    **thresholds: float,
) -> dict[str, PortfolioRole]:
    return {
        player.player_id: classify_portfolio_role(player, profile, **thresholds)
        for player in players
    }
