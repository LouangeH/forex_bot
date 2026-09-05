# forex_bot/patterns/continuation/consolidation.py

from __future__ import annotations

from statistics import median

from forex_bot.core.enums import (
    PivotType,
    TradeDirection,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from forex_bot.patterns.geometry.regression import (
    fit_linear_boundary,
)

from .config import (
    ContinuationPatternConfig,
)

from .types import (
    ConsolidationStructure,
    ImpulseLeg,
)


class ConsolidationBuilder:
    """
    Analyse uniquement la structure située
    APRÈS l'impulsion.

    Cela empêche un ancien pivot de fausser
    la géométrie du Flag/Pennant.
    """

    def __init__(
        self,
        config: ContinuationPatternConfig,
    ) -> None:

        self._config = config

    def build(
        self,
        *,
        context: PatternContext,

        impulse: ImpulseLeg,
    ) -> ConsolidationStructure | None:

        start_index = (
            impulse.end_index
            + 1
        )

        end_index = (
            context.as_of_index
        )

        duration = (

            end_index
            - start_index
            + 1
        )

        if (
            duration
            < self._config
            .min_consolidation_bars
        ):

            return None

        if (
            duration
            > self._config
            .max_consolidation_bars
        ):

            return None

        pivots = [

            item

            for item
            in context.pivots

            if (

                item.pivot.candle_index
                >= start_index

                and

                item.pivot.candle_index
                <= end_index

                and

                item.confirmation_index
                <= context.as_of_index
            )
        ]

        highs = [

            item

            for item
            in pivots

            if (
                item.pivot.pivot_type
                == PivotType.HIGH
            )
        ]

        lows = [

            item

            for item
            in pivots

            if (
                item.pivot.pivot_type
                == PivotType.LOW
            )
        ]

        if (
            len(highs)
            < self._config
            .min_consolidation_highs
        ):

            return None

        if (
            len(lows)
            < self._config
            .min_consolidation_lows
        ):

            return None

        high_points = [

            (
                item.pivot.candle_index,
                item.pivot.price,
            )

            for item
            in highs
        ]

        low_points = [

            (
                item.pivot.candle_index,
                item.pivot.price,
            )

            for item
            in lows
        ]

        upper = fit_linear_boundary(
            high_points
        )

        lower = fit_linear_boundary(
            low_points
        )

        if (
            upper.r_squared
            < self._config.min_line_r_squared
        ):

            return None

        if (
            lower.r_squared
            < self._config.min_line_r_squared
        ):

            return None

        atr_reference = median(

            item.atr

            for item
            in highs + lows

            if item.atr > 0
        )

        upper_start = (
            upper.value_at(
                start_index
            )
        )

        lower_start = (
            lower.value_at(
                start_index
            )
        )

        upper_end = (
            upper.value_at(
                end_index
            )
        )

        lower_end = (
            lower.value_at(
                end_index
            )
        )

        start_gap = (
            upper_start
            - lower_start
        )

        end_gap = (
            upper_end
            - lower_end
        )

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

        convergence_ratio = (

            (
                start_gap
                - end_gap
            )

            / start_gap
        )

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

        window = context.candles[
            start_index
            :
            end_index + 1
        ]

        observed_high = max(

            candle.high

            for candle
            in window
        )

        observed_low = min(

            candle.low

            for candle
            in window
        )

        observed_height = (

            observed_high
            - observed_low
        )

        height_vs_impulse = (

            observed_height
            / impulse.distance
        )

        # ------------------------------------------------
        # RETRACEMENT DU MÂT
        # ------------------------------------------------

        if (
            impulse.direction
            == TradeDirection.BUY
        ):

            adverse_extreme = min(

                candle.low

                for candle
                in window
            )

            retracement_distance = max(

                0.0,

                impulse.end_price
                - adverse_extreme,
            )

        else:

            adverse_extreme = max(

                candle.high

                for candle
                in window
            )

            retracement_distance = max(

                0.0,

                adverse_extreme
                - impulse.end_price,
            )

        retracement_ratio = (

            retracement_distance
            / impulse.distance
        )

        return ConsolidationStructure(

            start_index=start_index,

            end_index=end_index,

            upper=upper,

            lower=lower,

            atr_reference=(
                atr_reference
            ),

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

            retracement_ratio=(
                retracement_ratio
            ),

            height_vs_impulse=(
                height_vs_impulse
            ),

            high_pivot_indexes=tuple(

                item.pivot.candle_index

                for item
                in highs
            ),

            low_pivot_indexes=tuple(

                item.pivot.candle_index

                for item
                in lows
            ),
        )