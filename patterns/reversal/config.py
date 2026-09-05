# forex_bot/patterns/reversal/config.py

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
class ReversalPatternConfig:
    """
    Configuration commune aux figures
    de retournement.

    Les distances importantes sont exprimées
    principalement en ATR afin que les règles
    puissent fonctionner sur plusieurs instruments
    et différentes périodes de volatilité.
    """

    # =====================================================
    # GÉNÉRAL
    # =====================================================

    lookback_bars: int = 120

    max_pattern_age_bars: int = 12

    min_confidence: float = 0.55

    # =====================================================
    # DOUBLE / TRIPLE TOP & BOTTOM
    # =====================================================

    # Deux sommets/creux peuvent être considérés
    # comme "égaux" si leur différence ne dépasse
    # pas cette fraction d'ATR.
    level_tolerance_atr: float = 0.35

    # Profondeur minimale entre deux sommets/creux.
    min_swing_depth_atr: float = 0.80

    # Tolérance légèrement supérieure pour
    # trois niveaux.
    triple_level_tolerance_atr: float = 0.45

    # =====================================================
    # HEAD & SHOULDERS
    # =====================================================

    shoulder_tolerance_atr: float = 0.50

    min_head_height_atr: float = 0.60

    # La neckline peut être inclinée,
    # mais pas de manière absurde.
    max_neckline_slope_atr: float = 0.30

    # =====================================================
    # V TOP / V BOTTOM
    # =====================================================

    v_leg_bars: int = 6

    v_min_leg_atr: float = 1.50

    v_min_efficiency: float = 0.45

    # Évite d'appeler V une structure
    # totalement asymétrique.
    v_min_symmetry_ratio: float = 0.40

    # =====================================================
    # 1-2-3
    # =====================================================

    one_two_three_min_reversal_atr: float = 0.40

    # =====================================================
    # QUASIMODO
    # =====================================================

    quasimodo_structure_break_atr: float = 0.20

    quasimodo_shoulder_tolerance_atr: float = 0.60

    # =====================================================
    # ROUNDING
    # =====================================================

    rounding_min_bars: int = 24
    rounding_max_bars: int = 60
    rounding_window_step: int = 4

    rounding_atr_period: int = 14

    rounding_min_r_squared: float = 0.65

    # Hauteur minimale de la courbure.
    rounding_min_curvature_atr: float = 1.20

    # Le sommet/creux de la parabole doit
    # rester dans la partie centrale.
    rounding_vertex_min_fraction: float = 0.20
    rounding_vertex_max_fraction: float = 0.80

    # =====================================================
    # BROADENING
    # =====================================================

    broadening_min_divergence_ratio: float = 0.15

    broadening_min_r_squared: float = 0.60

    # =====================================================
    # DIAMOND
    # =====================================================

    diamond_lookback_bars: int = 80

    diamond_min_pivots_per_half: int = 2

    diamond_min_expansion_ratio: float = 0.15

    diamond_min_contraction_ratio: float = 0.15

    diamond_min_r_squared: float = 0.55

    # Analyse la tendance précédant la figure.
    context_bars: int = 20

    context_min_slope_atr: float = 0.03

    def __post_init__(self) -> None:

        integer_fields = (
            "lookback_bars",
            "max_pattern_age_bars",
            "v_leg_bars",
            "rounding_min_bars",
            "rounding_max_bars",
            "rounding_window_step",
            "rounding_atr_period",
            "diamond_lookback_bars",
            "diamond_min_pivots_per_half",
            "context_bars",
        )

        for field_name in integer_fields:

            positive_int(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        ratio_fields = (
            "min_confidence",
            "v_min_efficiency",
            "v_min_symmetry_ratio",
            "rounding_min_r_squared",
            "rounding_vertex_min_fraction",
            "rounding_vertex_max_fraction",
            "broadening_min_r_squared",
            "diamond_min_r_squared",
        )

        for field_name in ratio_fields:

            ratio_0_1(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        positive_fields = (
            "level_tolerance_atr",
            "min_swing_depth_atr",
            "triple_level_tolerance_atr",
            "shoulder_tolerance_atr",
            "min_head_height_atr",
            "max_neckline_slope_atr",
            "v_min_leg_atr",
            "one_two_three_min_reversal_atr",
            "quasimodo_structure_break_atr",
            "quasimodo_shoulder_tolerance_atr",
            "rounding_min_curvature_atr",
            "broadening_min_divergence_ratio",
            "diamond_min_expansion_ratio",
            "diamond_min_contraction_ratio",
            "context_min_slope_atr",
        )

        for field_name in positive_fields:

            positive_float(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        if (
            self.rounding_max_bars
            < self.rounding_min_bars
        ):

            raise DomainValidationError(
                "rounding_max_bars doit être >= "
                "rounding_min_bars."
            )

        if (
            self.rounding_vertex_max_fraction
            <= self.rounding_vertex_min_fraction
        ):

            raise DomainValidationError(
                "La limite maximale du vertex "
                "doit dépasser la limite minimale."
            )