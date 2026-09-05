# forex_bot/patterns/continuation/types.py

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.core.enums import (
    TradeDirection,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    LinearBoundary,
    PatternMetric,
)

from forex_bot.core.validators import (
    ensure_enum,
    finite_float,
    non_negative_float,
    non_negative_int,
    positive_float,
    positive_int,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ImpulseLeg:
    """
    Mouvement impulsif précédant une figure
    de continuation.

    Pour Flag/Pennant, cet objet représente
    essentiellement le "mât".
    """

    direction: TradeDirection

    start_index: int
    end_index: int

    start_price: float
    end_price: float

    atr_reference: float

    distance: float
    distance_atr: float

    duration_bars: int

    efficiency: float

    directional_candle_ratio: float

    score: float

    def __post_init__(self) -> None:

        ensure_enum(
            "direction",
            self.direction,
            TradeDirection,
        )

        non_negative_int(
            "start_index",
            self.start_index,
        )

        non_negative_int(
            "end_index",
            self.end_index,
        )

        if (
            self.end_index
            <= self.start_index
        ):

            raise DomainValidationError(
                "Une impulsion doit finir "
                "après son début."
            )

        positive_float(
            "start_price",
            self.start_price,
        )

        positive_float(
            "end_price",
            self.end_price,
        )

        positive_float(
            "atr_reference",
            self.atr_reference,
        )

        positive_float(
            "distance",
            self.distance,
        )

        positive_float(
            "distance_atr",
            self.distance_atr,
        )

        positive_int(
            "duration_bars",
            self.duration_bars,
        )

        ratio_0_1(
            "efficiency",
            self.efficiency,
        )

        ratio_0_1(
            "directional_candle_ratio",
            self.directional_candle_ratio,
        )

        ratio_0_1(
            "score",
            self.score,
        )

        if (
            self.direction
            == TradeDirection.BUY
            and
            self.end_price
            <= self.start_price
        ):

            raise DomainValidationError(
                "Une impulsion haussière doit "
                "finir au-dessus de son départ."
            )

        if (
            self.direction
            == TradeDirection.SELL
            and
            self.end_price
            >= self.start_price
        ):

            raise DomainValidationError(
                "Une impulsion baissière doit "
                "finir sous son départ."
            )

    def metrics(
        self,
    ) -> tuple[
        PatternMetric,
        ...
    ]:

        return (

            PatternMetric(
                "impulse_distance_atr",
                self.distance_atr,
            ),

            PatternMetric(
                "impulse_duration_bars",
                float(
                    self.duration_bars
                ),
            ),

            PatternMetric(
                "impulse_efficiency",
                self.efficiency,
            ),

            PatternMetric(
                "impulse_directional_candle_ratio",
                self.directional_candle_ratio,
            ),

            PatternMetric(
                "impulse_score",
                self.score,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ConsolidationStructure:
    """
    Consolidation située APRÈS l'impulsion.

    Elle possède :
    - une frontière haute ;
    - une frontière basse ;
    - des pentes ;
    - une convergence ;
    - un retracement.
    """

    start_index: int
    end_index: int

    upper: LinearBoundary
    lower: LinearBoundary

    atr_reference: float

    upper_slope_atr: float
    lower_slope_atr: float

    start_gap_atr: float
    end_gap_atr: float

    convergence_ratio: float

    parallel_difference_atr: float

    retracement_ratio: float

    height_vs_impulse: float

    high_pivot_indexes: tuple[
        int,
        ...
    ]

    low_pivot_indexes: tuple[
        int,
        ...
    ]

    def __post_init__(self) -> None:

        non_negative_int(
            "start_index",
            self.start_index,
        )

        non_negative_int(
            "end_index",
            self.end_index,
        )

        if (
            self.end_index
            <= self.start_index
        ):

            raise DomainValidationError(
                "La consolidation doit "
                "avoir une durée positive."
            )

        positive_float(
            "atr_reference",
            self.atr_reference,
        )

        for name in (
            "upper_slope_atr",
            "lower_slope_atr",
            "convergence_ratio",
        ):

            finite_float(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        non_negative_float(
            "start_gap_atr",
            self.start_gap_atr,
        )

        non_negative_float(
            "end_gap_atr",
            self.end_gap_atr,
        )

        non_negative_float(
            "parallel_difference_atr",
            self.parallel_difference_atr,
        )

        non_negative_float(
            "retracement_ratio",
            self.retracement_ratio,
        )

        non_negative_float(
            "height_vs_impulse",
            self.height_vs_impulse,
        )

        if (
            self.upper.touches < 2
            or
            self.lower.touches < 2
        ):

            raise DomainValidationError(
                "La consolidation exige "
                "deux contacts minimum "
                "par frontière."
            )

    @property
    def duration_bars(
        self,
    ) -> int:

        return (
            self.end_index
            - self.start_index
        )

    @property
    def fit_score(
        self,
    ) -> float:

        return (
            self.upper.r_squared
            + self.lower.r_squared
        ) / 2

    def metrics(
        self,
    ) -> tuple[
        PatternMetric,
        ...
    ]:

        return (

            PatternMetric(
                "consolidation_upper_slope_atr",
                self.upper_slope_atr,
            ),

            PatternMetric(
                "consolidation_lower_slope_atr",
                self.lower_slope_atr,
            ),

            PatternMetric(
                "consolidation_start_gap_atr",
                self.start_gap_atr,
            ),

            PatternMetric(
                "consolidation_end_gap_atr",
                self.end_gap_atr,
            ),

            PatternMetric(
                "consolidation_convergence_ratio",
                self.convergence_ratio,
            ),

            PatternMetric(
                "consolidation_parallel_difference_atr",
                self.parallel_difference_atr,
            ),

            PatternMetric(
                "consolidation_retracement_ratio",
                self.retracement_ratio,
            ),

            PatternMetric(
                "consolidation_height_vs_impulse",
                self.height_vs_impulse,
            ),

            PatternMetric(
                "consolidation_fit_score",
                self.fit_score,
            ),

            PatternMetric(
                "consolidation_duration_bars",
                float(
                    self.duration_bars
                ),
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class MeasuredMoveGeometry:
    """
    Géométrie A-B-C-D d'un Measured Move.
    """

    a_index: int
    b_index: int
    c_index: int
    d_index: int

    first_leg: float

    correction: float

    second_leg: float

    leg_ratio: float

    correction_ratio: float

    score: float

    def __post_init__(self) -> None:

        if not (
            self.a_index
            < self.b_index
            < self.c_index
            < self.d_index
        ):

            raise DomainValidationError(
                "Les points A-B-C-D doivent "
                "être strictement chronologiques."
            )

        for name in (
            "first_leg",
            "correction",
            "second_leg",
            "leg_ratio",
            "correction_ratio",
        ):

            positive_float(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        ratio_0_1(
            "score",
            self.score,
        )

    def metrics(
        self,
    ) -> tuple[
        PatternMetric,
        ...
    ]:

        return (

            PatternMetric(
                "measured_move_first_leg",
                self.first_leg,
            ),

            PatternMetric(
                "measured_move_correction",
                self.correction,
            ),

            PatternMetric(
                "measured_move_second_leg",
                self.second_leg,
            ),

            PatternMetric(
                "measured_move_leg_ratio",
                self.leg_ratio,
            ),

            PatternMetric(
                "measured_move_correction_ratio",
                self.correction_ratio,
            ),

            PatternMetric(
                "measured_move_score",
                self.score,
            ),
        )