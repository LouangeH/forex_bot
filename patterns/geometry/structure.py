# forex_bot/patterns/geometry/structure.py

from __future__ import annotations

from dataclasses import dataclass

from statistics import median

from forex_bot.core.enums import (
    PivotType,
)

from forex_bot.core.models import (
    LinearBoundary,
    PatternMetric,
)

from forex_bot.patterns.config import (
    LinePatternConfig,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .regression import (
    fit_linear_boundary,
    mean_absolute_error,
)


@dataclass(
    frozen=True,
    slots=True,
)
class LineStructure:
    """
    Représentation mathématique d'une figure
    possédant une frontière supérieure
    et une frontière inférieure.
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

    upper_error_atr: float

    lower_error_atr: float

    high_pivot_indexes: tuple[
        int,
        ...
    ]

    low_pivot_indexes: tuple[
        int,
        ...
    ]

    @property
    def duration_bars(self) -> int:

        return (
            self.end_index
            - self.start_index
        )

    @property
    def fit_score(self) -> float:

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
        """
        Toutes les valeurs utilisées pour reconnaître
        la figure seront conservées.

        Cela sera indispensable pour les backtests.
        """

        return (

            PatternMetric(
                "upper_slope_atr",
                self.upper_slope_atr,
            ),

            PatternMetric(
                "lower_slope_atr",
                self.lower_slope_atr,
            ),

            PatternMetric(
                "start_gap_atr",
                self.start_gap_atr,
            ),

            PatternMetric(
                "end_gap_atr",
                self.end_gap_atr,
            ),

            PatternMetric(
                "convergence_ratio",
                self.convergence_ratio,
            ),

            PatternMetric(
                "parallel_difference_atr",
                self.parallel_difference_atr,
            ),

            PatternMetric(
                "upper_r_squared",
                self.upper.r_squared,
            ),

            PatternMetric(
                "lower_r_squared",
                self.lower.r_squared,
            ),

            PatternMetric(
                "upper_error_atr",
                self.upper_error_atr,
            ),

            PatternMetric(
                "lower_error_atr",
                self.lower_error_atr,
            ),

            PatternMetric(
                "duration_bars",
                float(
                    self.duration_bars
                ),
            ),

            PatternMetric(
                "high_touches",
                float(
                    self.upper.touches
                ),
            ),

            PatternMetric(
                "low_touches",
                float(
                    self.lower.touches
                ),
            ),
        )


class LineStructureBuilder:
    """
    Transforme les Pivot High / Pivot Low
    récents en deux droites mathématiques.
    """

    def __init__(
        self,
        config: LinePatternConfig,
    ) -> None:

        self._config = config

    def build(
        self,
        context: PatternContext,
    ) -> LineStructure | None:

        minimum_index = max(

            0,

            context.as_of_index
            - self._config.lookback_bars,
        )

        usable = [

            pivot

            for pivot
            in context.pivots

            if (

                pivot.pivot.candle_index
                >= minimum_index

                and

                pivot.confirmation_index
                <= context.as_of_index
            )
        ]

        usable.sort(
            key=lambda item:
            item.pivot.candle_index
        )

        # On limite également le nombre
        # de pivots analysés.
        usable = usable[
            -self._config.max_pivots:
        ]

        highs = [

            pivot

            for pivot
            in usable

            if (
                pivot.pivot.pivot_type
                == PivotType.HIGH
            )
        ]

        lows = [

            pivot

            for pivot
            in usable

            if (
                pivot.pivot.pivot_type
                == PivotType.LOW
            )
        ]

        if (

            len(highs)
            < self._config.min_high_touches

            or

            len(lows)
            < self._config.min_low_touches
        ):

            return None

        start_index = min(

            pivot.pivot.candle_index

            for pivot
            in highs + lows
        )

        end_index = max(

            pivot.pivot.candle_index

            for pivot
            in highs + lows
        )

        if (
            end_index
            - start_index
            < self._config.min_pattern_bars
        ):

            return None

        if (
            context.as_of_index
            - end_index
            > self._config.max_end_age_bars
        ):

            return None

        atr_values = [

            pivot.atr

            for pivot
            in highs + lows

            if pivot.atr > 0
        ]

        if not atr_values:

            return None

        atr_reference = median(
            atr_values
        )

        high_points = [

            (
                pivot.pivot.candle_index,
                pivot.pivot.price,
            )

            for pivot
            in highs
        ]

        low_points = [

            (
                pivot.pivot.candle_index,
                pivot.pivot.price,
            )

            for pivot
            in lows
        ]

        upper = fit_linear_boundary(
            high_points
        )

        lower = fit_linear_boundary(
            low_points
        )

        # Distance entre les deux droites
        # au début de la figure.
        start_gap = (

            upper.value_at(
                start_index
            )

            -

            lower.value_at(
                start_index
            )
        )

        # Distance à la fin.
        end_gap = (

            upper.value_at(
                end_index
            )

            -

            lower.value_at(
                end_index
            )
        )

        # Une frontière supérieure ne peut pas
        # être sous la frontière inférieure.
        if (
            start_gap <= 0
            or
            end_gap <= 0
        ):

            return None

        start_gap_atr = (
            start_gap
            / atr_reference
        )

        end_gap_atr = (
            end_gap
            / atr_reference
        )

        if not (

            self._config.min_width_atr

            <= end_gap_atr

            <= self._config.max_width_atr
        ):

            return None

        # Ex :
        #
        # largeur début = 4 ATR
        # largeur fin   = 2 ATR
        #
        # convergence = 50 %
        convergence_ratio = (

            start_gap
            - end_gap

        ) / start_gap

        upper_slope_atr = (
            upper.slope
            / atr_reference
        )

        lower_slope_atr = (
            lower.slope
            / atr_reference
        )

        parallel_difference_atr = abs(

            upper_slope_atr
            - lower_slope_atr
        )

        upper_error_atr = (

            mean_absolute_error(
                upper,
                high_points,
            )

            / atr_reference
        )

        lower_error_atr = (

            mean_absolute_error(
                lower,
                low_points,
            )

            / atr_reference
        )

        return LineStructure(

            start_index=start_index,

            end_index=end_index,

            upper=upper,

            lower=lower,

            atr_reference=atr_reference,

            upper_slope_atr=(
                upper_slope_atr
            ),

            lower_slope_atr=(
                lower_slope_atr
            ),

            start_gap_atr=(
                start_gap_atr
            ),

            end_gap_atr=(
                end_gap_atr
            ),

            convergence_ratio=(
                convergence_ratio
            ),

            parallel_difference_atr=(
                parallel_difference_atr
            ),

            upper_error_atr=(
                upper_error_atr
            ),

            lower_error_atr=(
                lower_error_atr
            ),

            high_pivot_indexes=tuple(

                pivot.pivot.candle_index

                for pivot
                in highs
            ),

            low_pivot_indexes=tuple(

                pivot.pivot.candle_index

                for pivot
                in lows
            ),
        )