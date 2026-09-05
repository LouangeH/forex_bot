# forex_bot/patterns/harmonic/config.py

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.core.validators import (
    positive_float,
    positive_int,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class HarmonicConfig:
    """
    Paramètres généraux du moteur harmonique.

    Les ratios propres aux figures sont séparés
    dans profiles.py.
    """

    lookback_bars: int = 200

    max_recent_pivots: int = 30

    min_pattern_bars: int = 6

    max_pattern_bars: int = 120

    max_pattern_age_bars: int = 12

    # Empêche des micro-figures composées
    # presque uniquement de bruit.
    min_leg_atr: float = 0.30

    # Score minimal d'une figure harmonique.
    min_confidence: float = 0.62

    # Poids du score lié aux ratios Fibonacci.
    ratio_weight: float = 0.85

    # Poids lié à la qualité des pivots.
    prominence_weight: float = 0.15

    def __post_init__(self) -> None:

        for field_name in (
            "lookback_bars",
            "max_recent_pivots",
            "min_pattern_bars",
            "max_pattern_bars",
            "max_pattern_age_bars",
        ):

            positive_int(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        positive_float(
            "min_leg_atr",
            self.min_leg_atr,
        )

        for field_name in (
            "min_confidence",
            "ratio_weight",
            "prominence_weight",
        ):

            ratio_0_1(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        total = (

            self.ratio_weight

            +

            self.prominence_weight
        )

        if abs(
            total - 1.0
        ) > 1e-9:

            raise ValueError(
                "ratio_weight + prominence_weight "
                "doit être égal à 1."
            )