# forex_bot/patterns/reversal/rounding.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.market.pivots.volatility import (
    atr_at_index,
)

from forex_bot.patterns.base import (
    PatternDetector,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .common import (
    clamp_0_1,
)

from .config import (
    ReversalPatternConfig,
)

from .quadratic import (
    fit_quadratic,
)


class RoundingDetector(
    PatternDetector
):
    """
    Détection mathématique par parabole.

    Rounding Top :
        coefficient a < 0.

    Rounding Bottom :
        coefficient a > 0.
    """

    name = "rounding_detector"

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

        best = None

        for length in range(

            self._config.rounding_min_bars,

            self._config.rounding_max_bars
            + 1,

            self._config.rounding_window_step,
        ):

            start_index = (

                context.as_of_index
                - length
                + 1
            )

            if start_index < 0:

                continue

            candidate = (
                self._evaluate_window(

                    context=context,

                    start_index=start_index,

                    end_index=(
                        context.as_of_index
                    ),
                )
            )

            if candidate is None:

                continue

            if (
                best is None

                or

                candidate.confidence
                > best.confidence
            ):

                best = candidate

        if best is None:

            return ()

        return (
            best,
        )

    def _evaluate_window(
        self,
        *,
        context,
        start_index,
        end_index,
    ):

        candles = context.candles[
            start_index:
            end_index + 1
        ]

        closes = tuple(
            candle.close
            for candle
            in candles
        )

        fit = fit_quadratic(
            closes
        )

        if (
            fit.r_squared
            <
            self._config
            .rounding_min_r_squared
        ):

            return None

        size = len(candles)

        vertex_fraction = (

            fit.vertex_x

            /

            max(
                float(size - 1),
                1.0,
            )
        )

        if not (

            self._config
            .rounding_vertex_min_fraction

            <= vertex_fraction

            <=

            self._config
            .rounding_vertex_max_fraction
        ):

            return None

        atr = atr_at_index(

            context.candles,

            end_index,

            self._config
            .rounding_atr_period,
        )

        if (
            atr is None
            or atr <= 0
        ):

            return None

        start_prediction = (
            fit.value_at(
                0
            )
        )

        end_prediction = (
            fit.value_at(
                size - 1
            )
        )

        edge_average = (

            start_prediction
            + end_prediction

        ) / 2

        # ==========================================
        # TOP
        # ==========================================

        if fit.a < 0:

            curvature = (

                fit.vertex_y
                - edge_average
            )

            pattern_type = (
                PatternType.ROUNDING_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

        # ==========================================
        # BOTTOM
        # ==========================================

        elif fit.a > 0:

            curvature = (

                edge_average
                - fit.vertex_y
            )

            pattern_type = (
                PatternType.ROUNDING_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

        else:

            return None

        curvature_atr = (

            curvature / atr
        )

        if (
            curvature_atr
            <
            self._config
            .rounding_min_curvature_atr
        ):

            return None

        left_height = abs(

            fit.vertex_y
            - start_prediction
        )

        right_height = abs(

            fit.vertex_y
            - end_prediction
        )

        symmetry = (

            min(
                left_height,
                right_height,
            )

            /

            max(
                left_height,
                right_height,
                1e-12,
            )
        )

        curvature_score = clamp_0_1(

            curvature_atr

            /

            (
                self._config
                .rounding_min_curvature_atr

                * 2
            )
        )

        confidence = (

            0.50
            * fit.r_squared

            +

            0.30
            * curvature_score

            +

            0.20
            * symmetry
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        return PatternMatch(

            symbol=context.symbol,

            timeframe=context.timeframe,

            pattern_type=pattern_type,

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
                candles[0].open_time
            ),

            end_time=(
                candles[-1].open_time
            ),

            start_index=start_index,

            end_index=end_index,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            upper_boundary=None,

            lower_boundary=None,

            breakout_level=None,

            metrics=(

                PatternMetric(
                    "quadratic_a",
                    fit.a,
                ),

                PatternMetric(
                    "quadratic_b",
                    fit.b,
                ),

                PatternMetric(
                    "quadratic_c",
                    fit.c,
                ),

                PatternMetric(
                    "quadratic_r_squared",
                    fit.r_squared,
                ),

                PatternMetric(
                    "vertex_fraction",
                    vertex_fraction,
                ),

                PatternMetric(
                    "curvature_atr",
                    curvature_atr,
                ),

                PatternMetric(
                    "rounding_symmetry",
                    symmetry,
                ),
            ),

            source_pivot_indexes=(),
        )