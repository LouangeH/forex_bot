# forex_bot/patterns/reversal/diamond.py

from __future__ import annotations

from statistics import median

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
    PivotType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.patterns.base import (
    PatternDetector,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from forex_bot.patterns.geometry.regression import (
    fit_linear_boundary,
)

from .common import (
    clamp_0_1,
    prior_market_bias,
)

from .config import (
    ReversalPatternConfig,
)


class DiamondDetector(
    PatternDetector
):
    """
    Diamond :

    première moitié :
        expansion.

    deuxième moitié :
        contraction.
    """

    name = "diamond_detector"

    version = "1.0.0"

    def __init__(
        self,
        config:
        ReversalPatternConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or ReversalPatternConfig()
        )

    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        minimum_index = max(

            0,

            context.as_of_index

            -

            self._config
            .diamond_lookback_bars
        )

        pivots = [

            item

            for item
            in context.pivots

            if (

                item.pivot.candle_index
                >= minimum_index

                and

                item.confirmation_index
                <= context.as_of_index
            )
        ]

        if len(pivots) < 8:

            return ()

        pivots.sort(
            key=lambda item:
            item.pivot.candle_index
        )

        # On travaille sur les pivots les plus récents.
        start_index = (
            pivots[0]
            .pivot
            .candle_index
        )

        end_index = (
            pivots[-1]
            .pivot
            .candle_index
        )

        midpoint = (

            start_index
            + end_index

        ) // 2

        first_half = [

            item

            for item
            in pivots

            if (
                item.pivot.candle_index
                <= midpoint
            )
        ]

        second_half = [

            item

            for item
            in pivots

            if (
                item.pivot.candle_index
                >= midpoint
            )
        ]

        first_highs = [
            item
            for item
            in first_half
            if (
                item.pivot.pivot_type
                == PivotType.HIGH
            )
        ]

        first_lows = [
            item
            for item
            in first_half
            if (
                item.pivot.pivot_type
                == PivotType.LOW
            )
        ]

        second_highs = [
            item
            for item
            in second_half
            if (
                item.pivot.pivot_type
                == PivotType.HIGH
            )
        ]

        second_lows = [
            item
            for item
            in second_half
            if (
                item.pivot.pivot_type
                == PivotType.LOW
            )
        ]

        minimum = (
            self._config
            .diamond_min_pivots_per_half
        )

        if any(

            len(group) < minimum

            for group
            in (
                first_highs,
                first_lows,
                second_highs,
                second_lows,
            )
        ):

            return ()

        upper_first = (
            fit_linear_boundary(

                tuple(
                    (
                        item.pivot.candle_index,
                        item.pivot.price,
                    )

                    for item
                    in first_highs
                )
            )
        )

        lower_first = (
            fit_linear_boundary(

                tuple(
                    (
                        item.pivot.candle_index,
                        item.pivot.price,
                    )

                    for item
                    in first_lows
                )
            )
        )

        upper_second = (
            fit_linear_boundary(

                tuple(
                    (
                        item.pivot.candle_index,
                        item.pivot.price,
                    )

                    for item
                    in second_highs
                )
            )
        )

        lower_second = (
            fit_linear_boundary(

                tuple(
                    (
                        item.pivot.candle_index,
                        item.pivot.price,
                    )

                    for item
                    in second_lows
                )
            )
        )

        boundaries = (
            upper_first,
            lower_first,
            upper_second,
            lower_second,
        )

        if any(

            boundary.r_squared
            <
            self._config
            .diamond_min_r_squared

            for boundary
            in boundaries
        ):

            return ()

        atr = median(

            item.atr

            for item
            in pivots

            if item.atr > 0
        )

        if atr <= 0:

            return ()

        first_upper_slope = (
            upper_first.slope
            / atr
        )

        first_lower_slope = (
            lower_first.slope
            / atr
        )

        second_upper_slope = (
            upper_second.slope
            / atr
        )

        second_lower_slope = (
            lower_second.slope
            / atr
        )

        threshold = (
            self._config
            .context_min_slope_atr
        )

        # Première moitié :
        # divergence.
        if not (

            first_upper_slope
            > threshold

            and

            first_lower_slope
            < -threshold
        ):

            return ()

        # Deuxième moitié :
        # convergence.
        if not (

            second_upper_slope
            < -threshold

            and

            second_lower_slope
            > threshold
        ):

            return ()

        start_width = (

            upper_first.value_at(
                start_index
            )

            -

            lower_first.value_at(
                start_index
            )
        )

        middle_width = (

            upper_first.value_at(
                midpoint
            )

            -

            lower_first.value_at(
                midpoint
            )
        )

        end_width = (

            upper_second.value_at(
                end_index
            )

            -

            lower_second.value_at(
                end_index
            )
        )

        if (
            start_width <= 0
            or
            middle_width <= 0
            or
            end_width <= 0
        ):

            return ()

        expansion_ratio = (

            middle_width
            - start_width

        ) / start_width

        contraction_ratio = (

            middle_width
            - end_width

        ) / middle_width

        if (
            expansion_ratio
            <
            self._config
            .diamond_min_expansion_ratio

            or

            contraction_ratio
            <
            self._config
            .diamond_min_contraction_ratio
        ):

            return ()

        prior_bias, prior_slope = (
            prior_market_bias(

                context=context,

                start_index=start_index,

                atr_reference=atr,

                bars=(
                    self._config.context_bars
                ),

                minimum_slope_atr=(
                    self._config
                    .context_min_slope_atr
                ),
            )
        )

        if (
            prior_bias
            == MarketBias.BULLISH
        ):

            pattern_type = (
                PatternType.DIAMOND_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

            breakout_level = (
                lower_second.value_at(
                    context.as_of_index
                )
            )

        elif (
            prior_bias
            == MarketBias.BEARISH
        ):

            pattern_type = (
                PatternType.DIAMOND_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

            breakout_level = (
                upper_second.value_at(
                    context.as_of_index
                )
            )

        else:

            # On refuse de deviner Top ou Bottom
            # sans contexte directionnel.
            return ()

        fit_score = sum(

            boundary.r_squared

            for boundary
            in boundaries

        ) / 4

        expansion_score = clamp_0_1(

            expansion_ratio

            /

            (
                self._config
                .diamond_min_expansion_ratio

                * 2
            )
        )

        contraction_score = clamp_0_1(

            contraction_ratio

            /

            (
                self._config
                .diamond_min_contraction_ratio

                * 2
            )
        )

        confidence = (

            0.40
            * fit_score

            +

            0.30
            * expansion_score

            +

            0.30
            * contraction_score
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return ()

        return (

            PatternMatch(

                symbol=context.symbol,

                timeframe=context.timeframe,

                pattern_type=(
                    pattern_type
                ),

                family=(
                    PatternFamily.CLASSICAL
                ),

                role=(
                    PatternRole.REVERSAL
                ),

                status=(
                    PatternStatus.CONFIRMED
                ),

                bias=bias,

                start_time=(
                    context.candles[
                        start_index
                    ].open_time
                ),

                end_time=(
                    context.candles[
                        end_index
                    ].open_time
                ),

                start_index=(
                    start_index
                ),

                end_index=(
                    end_index
                ),

                confidence=(
                    confidence
                ),

                detector_name=(
                    self.name
                ),

                detector_version=(
                    self.version
                ),

                # Les frontières actives sont
                # celles de la contraction finale.
                upper_boundary=(
                    upper_second
                ),

                lower_boundary=(
                    lower_second
                ),

                breakout_level=(
                    breakout_level
                ),

                metrics=(

                    PatternMetric(
                        "diamond_expansion_ratio",
                        expansion_ratio,
                    ),

                    PatternMetric(
                        "diamond_contraction_ratio",
                        contraction_ratio,
                    ),

                    PatternMetric(
                        "diamond_prior_slope_atr",
                        prior_slope,
                    ),

                    PatternMetric(
                        "diamond_first_upper_slope_atr",
                        first_upper_slope,
                    ),

                    PatternMetric(
                        "diamond_first_lower_slope_atr",
                        first_lower_slope,
                    ),

                    PatternMetric(
                        "diamond_second_upper_slope_atr",
                        second_upper_slope,
                    ),

                    PatternMetric(
                        "diamond_second_lower_slope_atr",
                        second_lower_slope,
                    ),
                ),

                source_pivot_indexes=tuple(

                    item.pivot.candle_index

                    for item
                    in pivots
                ),
            ),

        )