# forex_bot/patterns/continuation/config.py

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.core.exceptions import DomainValidationError

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
class ContinuationPatternConfig:
    """
    Paramètres communs aux figures de continuation.

    Les valeurs servent de point de départ.

    Nous pourrons les calibrer par backtesting
    sans modifier les algorithmes.
    """

    # -----------------------------------------------------
    # IMPULSION
    # -----------------------------------------------------

    # Nombre maximal de bougies dans lesquelles
    # on recherche le mouvement impulsif.
    impulse_lookback_bars: int = 80

    # Durée minimale / maximale d'une impulsion.
    min_impulse_bars: int = 3
    max_impulse_bars: int = 30

    # L'impulsion doit déplacer le marché
    # d'au moins cette quantité d'ATR.
    min_impulse_atr: float = 2.0

    # Mesure la propreté du mouvement.
    #
    # 1.0 = mouvement presque parfaitement direct.
    min_impulse_efficiency: float = 0.45

    # Proportion minimale de bougies allant
    # dans le sens de l'impulsion.
    min_directional_candle_ratio: float = 0.55

    # -----------------------------------------------------
    # CONSOLIDATION
    # -----------------------------------------------------

    min_consolidation_bars: int = 4
    max_consolidation_bars: int = 30

    min_consolidation_highs: int = 2
    min_consolidation_lows: int = 2

    # Qualité minimale des régressions linéaires.
    min_line_r_squared: float = 0.55

    # Pente presque horizontale.
    horizontal_slope_atr: float = 0.06

    # Pente réellement directionnelle.
    directional_slope_atr: float = 0.03

    # Tolérance entre les pentes d'un canal.
    max_parallel_difference_atr: float = 0.08

    # Convergence minimale pour un pennant.
    min_pennant_convergence: float = 0.20

    # -----------------------------------------------------
    # RETRACEMENT
    # -----------------------------------------------------

    max_flag_retracement: float = 0.60

    max_pennant_retracement: float = 0.55

    max_rectangle_retracement: float = 0.60

    # La consolidation ne doit pas devenir
    # presque aussi grande que le mât.
    max_consolidation_height_vs_impulse: float = 0.65

    # -----------------------------------------------------
    # MEASURED MOVE
    # -----------------------------------------------------

    # CD / AB doit être approximativement proche de 1.
    measured_move_leg_ratio_min: float = 0.75
    measured_move_leg_ratio_max: float = 1.25

    # Retracement BC par rapport à AB.
    measured_move_correction_min: float = 0.20
    measured_move_correction_max: float = 0.65

    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    min_confidence: float = 0.55

    def __post_init__(self) -> None:

        for name in (
            "impulse_lookback_bars",
            "min_impulse_bars",
            "max_impulse_bars",
            "min_consolidation_bars",
            "max_consolidation_bars",
            "min_consolidation_highs",
            "min_consolidation_lows",
        ):

            positive_int(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        if (
            self.max_impulse_bars
            < self.min_impulse_bars
        ):

            raise DomainValidationError(
                "max_impulse_bars doit être "
                ">= min_impulse_bars."
            )

        if (
            self.max_consolidation_bars
            < self.min_consolidation_bars
        ):

            raise DomainValidationError(
                "max_consolidation_bars doit être "
                ">= min_consolidation_bars."
            )

        for name in (
            "min_impulse_atr",
            "horizontal_slope_atr",
            "directional_slope_atr",
            "max_parallel_difference_atr",
            "min_pennant_convergence",
            "max_consolidation_height_vs_impulse",
        ):

            non_negative_float(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        for name in (
            "min_impulse_efficiency",
            "min_directional_candle_ratio",
            "min_line_r_squared",
            "max_flag_retracement",
            "max_pennant_retracement",
            "max_rectangle_retracement",
            "measured_move_correction_min",
            "measured_move_correction_max",
            "min_confidence",
        ):

            ratio_0_1(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        positive_float(
            "measured_move_leg_ratio_min",
            self.measured_move_leg_ratio_min,
        )

        positive_float(
            "measured_move_leg_ratio_max",
            self.measured_move_leg_ratio_max,
        )

        if (
            self.measured_move_leg_ratio_max
            < self.measured_move_leg_ratio_min
        ):

            raise DomainValidationError(
                "measured_move_leg_ratio_max "
                "doit être >= "
                "measured_move_leg_ratio_min."
            )

        if (
            self.measured_move_correction_max
            < self.measured_move_correction_min
        ):

            raise DomainValidationError(
                "measured_move_correction_max "
                "doit être >= "
                "measured_move_correction_min."
            )