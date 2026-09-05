# forex_bot/patterns/reversal/v_patterns.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
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

from .common import (
    build_reversal_match,
    clamp_0_1,
    pattern_is_recent,
    recent_pivots,
)

from .config import (
    ReversalPatternConfig,
)


class VPatternDetector(
    PatternDetector
):
    """
    Détecte les retournements rapides :

          /\
         /  \
        /    \

    ou :

        \    /
         \  /
          \/
    """

    name = "v_pattern_detector"

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

        pivots = recent_pivots(
            context,
            self._config,
        )

        found = []

        for pivot in pivots:

            match = self._detect_one(
                context,
                pivot,
            )

            if match is not None:

                found.append(
                    match
                )

        return tuple(
            found
        )

    def _detect_one(
        self,
        context,
        detected_pivot,
    ) -> PatternMatch | None:

        pivot = (
            detected_pivot.pivot
        )

        if not pattern_is_recent(

            context=context,

            last_index=(
                pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        left_index = (

            pivot.candle_index
            - self._config.v_leg_bars
        )

        right_index = (

            pivot.candle_index
            + self._config.v_leg_bars
        )

        if (
            left_index < 0

            or

            right_index
            > context.as_of_index
        ):

            return None

        left_price = (
            context.candles[
                left_index
            ].close
        )

        right_price = (
            context.candles[
                right_index
            ].close
        )

        atr = (
            detected_pivot.atr
        )

        if atr <= 0:

            return None

        if (
            pivot.pivot_type
            == PivotType.HIGH
        ):

            left_move = (
                pivot.price
                - left_price
            )

            right_move = (
                pivot.price
                - right_price
            )

            pattern_type = (
                PatternType.V_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

        else:

            left_move = (
                left_price
                - pivot.price
            )

            right_move = (
                right_price
                - pivot.price
            )

            pattern_type = (
                PatternType.V_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

        if (
            left_move <= 0
            or
            right_move <= 0
        ):

            return None

        left_atr = (
            left_move / atr
        )

        right_atr = (
            right_move / atr
        )

        if (
            left_atr
            < self._config.v_min_leg_atr

            or

            right_atr
            < self._config.v_min_leg_atr
        ):

            return None

        left_efficiency = (
            self._efficiency(

                context=context,

                start_index=left_index,

                end_index=(
                    pivot.candle_index
                ),
            )
        )

        right_efficiency = (
            self._efficiency(

                context=context,

                start_index=(
                    pivot.candle_index
                ),

                end_index=right_index,
            )
        )

        if (
            left_efficiency
            < self._config.v_min_efficiency

            or

            right_efficiency
            < self._config.v_min_efficiency
        ):

            return None

        symmetry = (

            min(
                left_move,
                right_move,
            )

            /

            max(
                left_move,
                right_move,
            )
        )

        if (
            symmetry
            < self._config.v_min_symmetry_ratio
        ):

            return None

        magnitude_score = clamp_0_1(

            (
                left_atr
                + right_atr
            )

            /

            (
                self._config
                .v_min_leg_atr
                * 4
            )
        )

        efficiency_score = (

            left_efficiency
            + right_efficiency

        ) / 2

        confidence = (

            0.40
            * magnitude_score

            +

            0.35
            * efficiency_score

            +

            0.25
            * symmetry
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        # Pour cette figure, les pivots métier
        # ne couvrent que le sommet/creux central.
        #
        # Nous construisons donc manuellement
        # un PatternMatch avec les vraies bornes
        # temporelles de la forme V.
        return PatternMatch(

            symbol=context.symbol,

            timeframe=context.timeframe,

            pattern_type=pattern_type,

            family=(
                __import__(
                    "forex_bot.core.enums",
                    fromlist=["PatternFamily"],
                ).PatternFamily.CLASSICAL
            ),

            role=(
                __import__(
                    "forex_bot.core.enums",
                    fromlist=["PatternRole"],
                ).PatternRole.REVERSAL
            ),

            status=(
                __import__(
                    "forex_bot.core.enums",
                    fromlist=["PatternStatus"],
                ).PatternStatus.CONFIRMED
            ),

            bias=bias,

            start_time=(
                context.candles[
                    left_index
                ].open_time
            ),

            end_time=(
                context.candles[
                    right_index
                ].open_time
            ),

            start_index=left_index,

            end_index=right_index,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            upper_boundary=None,

            lower_boundary=None,

            breakout_level=None,

            metrics=(

                PatternMetric(
                    "left_leg_atr",
                    left_atr,
                ),

                PatternMetric(
                    "right_leg_atr",
                    right_atr,
                ),

                PatternMetric(
                    "left_efficiency",
                    left_efficiency,
                ),

                PatternMetric(
                    "right_efficiency",
                    right_efficiency,
                ),

                PatternMetric(
                    "v_symmetry",
                    symmetry,
                ),
            ),

            source_pivot_indexes=(
                pivot.candle_index,
            ),
        )

    @staticmethod
    def _efficiency(
        *,
        context,
        start_index,
        end_index,
    ) -> float:

        candles = context.candles[
            start_index:
            end_index + 1
        ]

        if len(candles) < 2:

            return 0.0

        net = abs(

            candles[-1].close
            - candles[0].close
        )

        path = sum(

            abs(
                current.close
                - previous.close
            )

            for previous, current
            in zip(
                candles,
                candles[1:],
                strict=False,
            )
        )

        if path <= 0:

            return 0.0

        return min(
            1.0,
            net / path,
        )