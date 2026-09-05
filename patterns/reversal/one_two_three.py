# forex_bot/patterns/reversal/one_two_three.py

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
    median_atr,
    pattern_is_recent,
    recent_pivots,
)

from .config import (
    ReversalPatternConfig,
)


class OneTwoThreeDetector(
    PatternDetector
):
    """
    1-2-3 Top :

        H1
          \
           L2
          /
        H3 inférieur à H1

    Confirmation future :
        cassure du point 2.

    1-2-3 Bottom :
        structure inverse.
    """

    name = "one_two_three_detector"

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

        for index in range(
            len(pivots) - 2
        ):

            sequence = pivots[
                index:
                index + 3
            ]

            match = self._detect_one(
                context,
                sequence,
            )

            if match:

                found.append(
                    match
                )

        return tuple(
            found
        )

    def _detect_one(
        self,
        context,
        sequence,
    ):

        first, second, third = (
            sequence
        )

        types = tuple(

            item.pivot.pivot_type

            for item
            in sequence
        )

        atr = median_atr(
            sequence
        )

        if (
            atr is None
            or atr <= 0
        ):

            return None

        if not pattern_is_recent(

            context=context,

            last_index=(
                third.pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        minimum_reversal = (

            atr

            * self._config
            .one_two_three_min_reversal_atr
        )

        # ==========================================
        # TOP
        # ==========================================

        if types == (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        ):

            reversal_size = (

                first.pivot.price
                - third.pivot.price
            )

            swing_size = (

                first.pivot.price
                - second.pivot.price
            )

            if (
                reversal_size
                < minimum_reversal

                or

                swing_size <= 0
            ):

                return None

            pattern_type = (
                PatternType
                .ONE_TWO_THREE_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

            breakout_level = (
                second.pivot.price
            )

        # ==========================================
        # BOTTOM
        # ==========================================

        elif types == (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        ):

            reversal_size = (

                third.pivot.price
                - first.pivot.price
            )

            swing_size = (

                second.pivot.price
                - first.pivot.price
            )

            if (
                reversal_size
                < minimum_reversal

                or

                swing_size <= 0
            ):

                return None

            pattern_type = (
                PatternType
                .ONE_TWO_THREE_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

            breakout_level = (
                second.pivot.price
            )

        else:

            return None

        reversal_score = clamp_0_1(

            reversal_size

            /

            max(
                minimum_reversal * 2,
                1e-12,
            )
        )

        swing_score = clamp_0_1(

            (
                swing_size / atr
            )

            /

            max(
                self._config
                .min_swing_depth_atr
                * 2,

                1e-12,
            )
        )

        confidence = (

            0.60
            * reversal_score

            +

            0.40
            * swing_score
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        return build_reversal_match(

            context=context,

            pattern_type=pattern_type,

            bias=bias,

            pivots=sequence,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            breakout_level=(
                breakout_level
            ),

            metrics=(

                PatternMetric(
                    "point_3_reversal_atr",
                    reversal_size / atr,
                ),

                PatternMetric(
                    "point_1_2_swing_atr",
                    swing_size / atr,
                ),
            ),
        )