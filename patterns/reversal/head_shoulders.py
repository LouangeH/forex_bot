# forex_bot/patterns/reversal/head_shoulders.py

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
    level_closeness_score,
    median_atr,
    neckline_from_pivots,
    pattern_is_recent,
    recent_pivots,
)

from .config import (
    ReversalPatternConfig,
)


class HeadShouldersDetector(
    PatternDetector
):
    """
    Détecte :

    - Head & Shoulders ;
    - Inverse Head & Shoulders.
    """

    name = (
        "head_shoulders_detector"
    )

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
            len(pivots) - 4
        ):

            sequence = pivots[
                index:
                index + 5
            ]

            match = self._detect_one(
                context,
                sequence,
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
        sequence,
    ) -> PatternMatch | None:

        a, b, c, d, e = (
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
                e.pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        # ==========================================
        # HEAD & SHOULDERS
        # ==========================================

        if types == (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        ):

            shoulder_score = (
                level_closeness_score(

                    prices=(
                        a.pivot.price,
                        e.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .shoulder_tolerance_atr
                    ),
                )
            )

            shoulder_reference = max(
                a.pivot.price,
                e.pivot.price,
            )

            head_height = (

                c.pivot.price
                - shoulder_reference
            )

            if (
                shoulder_score <= 0
                or
                head_height
                <
                self._config
                .min_head_height_atr
                * atr
            ):

                return None

            neckline = (
                neckline_from_pivots(
                    b,
                    d,
                )
            )

            neckline_slope_atr = (

                neckline.slope
                / atr
            )

            if (
                abs(
                    neckline_slope_atr
                )
                >
                self._config
                .max_neckline_slope_atr
            ):

                return None

            pattern_type = (
                PatternType
                .HEAD_AND_SHOULDERS
            )

            bias = (
                MarketBias.BEARISH
            )

            breakout_level = (
                neckline.value_at(
                    context.as_of_index
                )
            )

            lower_boundary = (
                neckline
            )

            upper_boundary = None

        # ==========================================
        # INVERSE H&S
        # ==========================================

        elif types == (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        ):

            shoulder_score = (
                level_closeness_score(

                    prices=(
                        a.pivot.price,
                        e.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .shoulder_tolerance_atr
                    ),
                )
            )

            shoulder_reference = min(
                a.pivot.price,
                e.pivot.price,
            )

            head_height = (

                shoulder_reference
                - c.pivot.price
            )

            if (
                shoulder_score <= 0

                or

                head_height
                <
                self._config
                .min_head_height_atr
                * atr
            ):

                return None

            neckline = (
                neckline_from_pivots(
                    b,
                    d,
                )
            )

            neckline_slope_atr = (

                neckline.slope
                / atr
            )

            if (
                abs(
                    neckline_slope_atr
                )
                >
                self._config
                .max_neckline_slope_atr
            ):

                return None

            pattern_type = (
                PatternType
                .INVERSE_HEAD_AND_SHOULDERS
            )

            bias = (
                MarketBias.BULLISH
            )

            breakout_level = (
                neckline.value_at(
                    context.as_of_index
                )
            )

            upper_boundary = (
                neckline
            )

            lower_boundary = None

        else:

            return None

        head_score = clamp_0_1(

            (
                head_height / atr
            )

            /

            max(
                self._config
                .min_head_height_atr
                * 2,

                1e-12,
            )
        )

        neckline_score = clamp_0_1(

            1.0

            -

            abs(
                neckline_slope_atr
            )

            /

            max(
                self._config
                .max_neckline_slope_atr,

                1e-12,
            )
        )

        confidence = (

            0.40
            * shoulder_score

            +

            0.35
            * head_score

            +

            0.25
            * neckline_score
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

            upper_boundary=(
                upper_boundary
            ),

            lower_boundary=(
                lower_boundary
            ),

            metrics=(

                PatternMetric(
                    "shoulder_similarity",
                    shoulder_score,
                ),

                PatternMetric(
                    "head_height_atr",
                    head_height / atr,
                ),

                PatternMetric(
                    "neckline_slope_atr",
                    neckline_slope_atr,
                ),
            ),
        )