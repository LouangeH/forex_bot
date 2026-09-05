# forex_bot/patterns/config.py

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.validators import (
    non_negative_float,
    positive_float,
    positive_int,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class LinePatternConfig:
    """
    Configuration des figures composées
    de deux frontières :

    - triangles ;
    - wedges ;
    - channels ;
    - ranges ;
    - plus tard flags/pennants.

    Les pentes sont normalisées par ATR.
    """

    # Nombre maximal de bougies étudiées.
    lookback_bars: int = 80

    # Nombre maximal de pivots récents.
    max_pivots: int = 14

    # Nombre minimum de sommets nécessaires.
    min_high_touches: int = 2

    # Nombre minimum de creux nécessaires.
    min_low_touches: int = 2

    # Une figure trop courte est rejetée.
    min_pattern_bars: int = 6

    # Si le dernier pivot est trop ancien,
    # la figure n'est plus considérée active.
    max_end_age_bars: int = 12

    # Qualité minimale de la régression.
    min_r_squared: float = 0.65

    # Une pente dont la valeur normalisée
    # est inférieure à ceci sera considérée
    # pratiquement horizontale.
    horizontal_slope_atr: float = 0.06

    # Pente minimale pour dire qu'une droite
    # est réellement montante/descendante.
    directional_slope_atr: float = 0.03

    # Réduction minimale de largeur
    # pour considérer que deux lignes convergent.
    min_convergence_ratio: float = 0.15

    # Tolérance de différence entre
    # les pentes d'un canal parallèle.
    max_parallel_slope_difference_atr: float = 0.06

    # Taille minimale de la figure.
    min_width_atr: float = 0.20

    # Empêche de considérer une structure énorme
    # comme une seule figure.
    max_width_atr: float = 8.0

    def __post_init__(self) -> None:

        positive_int(
            "lookback_bars",
            self.lookback_bars,
        )

        positive_int(
            "max_pivots",
            self.max_pivots,
        )

        positive_int(
            "min_high_touches",
            self.min_high_touches,
        )

        positive_int(
            "min_low_touches",
            self.min_low_touches,
        )

        positive_int(
            "min_pattern_bars",
            self.min_pattern_bars,
        )

        non_negative_float(
            "max_end_age_bars",
            self.max_end_age_bars,
        )

        ratio_0_1(
            "min_r_squared",
            self.min_r_squared,
        )

        non_negative_float(
            "horizontal_slope_atr",
            self.horizontal_slope_atr,
        )

        positive_float(
            "directional_slope_atr",
            self.directional_slope_atr,
        )

        non_negative_float(
            "min_convergence_ratio",
            self.min_convergence_ratio,
        )

        non_negative_float(
            "max_parallel_slope_difference_atr",
            self.max_parallel_slope_difference_atr,
        )

        positive_float(
            "min_width_atr",
            self.min_width_atr,
        )

        positive_float(
            "max_width_atr",
            self.max_width_atr,
        )

        if (
            self.max_width_atr
            <= self.min_width_atr
        ):

            raise DomainValidationError(
                "max_width_atr doit être "
                "supérieur à min_width_atr."
            )