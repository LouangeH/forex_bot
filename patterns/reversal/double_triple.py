# forex_bot/patterns/reversal/double_triple.py

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
    average_prominence_score,
    build_reversal_match,
    clamp_0_1,
    level_closeness_score,
    median_atr,
    pattern_is_recent,
    recent_pivots,
)

from .config import (
    ReversalPatternConfig,
)


class DoubleTripleDetector(
    PatternDetector
):
    """
    Détecte :

    H-L-H
        Double Top

    L-H-L
        Double Bottom

    H-L-H-L-H
        Triple Top

    L-H-L-H-L
        Triple Bottom
    """

    name = "double_triple_detector"

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

        found: list[
            PatternMatch
        ] = []

        # =================================================
        # DOUBLE
        # =================================================

        for index in range(
            len(pivots) - 2
        ):

            sequence = pivots[
                index:
                index + 3
            ]

            match = (
                self._detect_double(
                    context,
                    sequence,
                )
            )

            if match is not None:

                found.append(
                    match
                )

        # =================================================
        # TRIPLE
        # =================================================

        for index in range(
            len(pivots) - 4
        ):

            sequence = pivots[
                index:
                index + 5
            ]

            match = (
                self._detect_triple(
                    context,
                    sequence,
                )
            )

            if match is not None:

                found.append(
                    match
                )

        return tuple(
            found
        )

    def _detect_double(
        self,
        context,
        sequence,
    ) -> PatternMatch | None:

        first, middle, last = (
            sequence
        )

        types = tuple(

            pivot.pivot.pivot_type

            for pivot
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
                last.pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        # ==========================================
        # DOUBLE TOP
        # ==========================================

        if types == (

            PivotType.HIGH,

            PivotType.LOW,

            PivotType.HIGH,
        ):

            level_score = (
                level_closeness_score(

                    prices=(
                        first.pivot.price,
                        last.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .level_tolerance_atr
                    ),
                )
            )

            valley_depth = (

                min(
                    first.pivot.price,
                    last.pivot.price,
                )

                -

                middle.pivot.price
            )

            pattern_type = (
                PatternType.DOUBLE_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

            breakout_level = (
                middle.pivot.price
            )

        # ==========================================
        # DOUBLE BOTTOM
        # ==========================================

        elif types == (

            PivotType.LOW,

            PivotType.HIGH,

            PivotType.LOW,
        ):

            level_score = (
                level_closeness_score(

                    prices=(
                        first.pivot.price,
                        last.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .level_tolerance_atr
                    ),
                )
            )

            valley_depth = (

                middle.pivot.price

                -

                max(
                    first.pivot.price,
                    last.pivot.price,
                )
            )

            pattern_type = (
                PatternType.DOUBLE_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

            breakout_level = (
                middle.pivot.price
            )

        else:

            return None

        minimum_depth = (

            self._config
            .min_swing_depth_atr

            * atr
        )

        if (
            level_score <= 0

            or

            valley_depth
            < minimum_depth
        ):

            return None

        depth_score = clamp_0_1(

            valley_depth

            /

            max(
                minimum_depth * 2,
                1e-12,
            )
        )

        prominence_score = (
            average_prominence_score(
                sequence
            )
        )

        confidence = (

            0.45
            * level_score

            +

            0.35
            * depth_score

            +

            0.20
            * prominence_score
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        return build_reversal_match(

            context=context,

            pattern_type=(
                pattern_type
            ),

            bias=bias,

            pivots=sequence,

            confidence=confidence,

            detector_name=(
                self.name
            ),

            detector_version=(
                self.version
            ),

            breakout_level=(
                breakout_level
            ),

            metrics=(

                PatternMetric(
                    "level_closeness_score",
                    level_score,
                ),

                PatternMetric(
                    "swing_depth_atr",
                    valley_depth / atr,
                ),

                PatternMetric(
                    "prominence_score",
                    prominence_score,
                ),
            ),
        )

    def _detect_triple(
        self,
        context,
        sequence,
    ) -> PatternMatch | None:

        a, b, c, d, e = (
            sequence
        )

        types = tuple(

            pivot.pivot.pivot_type

            for pivot
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
                e.pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        if types == (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        ):

            levels = (
                a.pivot.price,
                c.pivot.price,
                e.pivot.price,
            )

            depth_1 = (

                min(
                    a.pivot.price,
                    c.pivot.price,
                )

                - b.pivot.price
            )

            depth_2 = (

                min(
                    c.pivot.price,
                    e.pivot.price,
                )

                - d.pivot.price
            )

            pattern_type = (
                PatternType.TRIPLE_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

            breakout_level = min(
                b.pivot.price,
                d.pivot.price,
            )

        elif types == (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        ):

            levels = (
                a.pivot.price,
                c.pivot.price,
                e.pivot.price,
            )

            depth_1 = (

                b.pivot.price

                -

                max(
                    a.pivot.price,
                    c.pivot.price,
                )
            )

            depth_2 = (

                d.pivot.price

                -

                max(
                    c.pivot.price,
                    e.pivot.price,
                )
            )

            pattern_type = (
                PatternType.TRIPLE_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

            breakout_level = max(
                b.pivot.price,
                d.pivot.price,
            )

        else:

            return None

        level_score = (
            level_closeness_score(

                prices=levels,

                atr=atr,

                tolerance_atr=(
                    self._config
                    .triple_level_tolerance_atr
                ),
            )
        )

        minimum_depth = (

            atr

            * self._config
            .min_swing_depth_atr
        )

        if (
            level_score <= 0

            or

            depth_1
            < minimum_depth

            or

            depth_2
            < minimum_depth
        ):

            return None

        mean_depth = (
            depth_1
            + depth_2
        ) / 2

        depth_score = clamp_0_1(

            mean_depth

            /

            max(
                minimum_depth * 2,
                1e-12,
            )
        )

        prominence_score = (
            average_prominence_score(
                sequence
            )
        )

        confidence = (

            0.50
            * level_score

            +

            0.30
            * depth_score

            +

            0.20
            * prominence_score
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
                    "level_closeness_score",
                    level_score,
                ),

                PatternMetric(
                    "average_swing_depth_atr",
                    mean_depth / atr,
                ),
            ),
        )