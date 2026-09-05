# forex_bot/patterns/continuation/rectangles.py

from __future__ import annotations

from forex_bot.core.enums import (
    PatternType,
    TradeDirection,
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
    build_continuation_match,
)

from .config import (
    ContinuationPatternConfig,
)

from .consolidation import (
    ConsolidationBuilder,
)

from .impulse import (
    ImpulseDetector,
)

from .scoring import (
    clamp_0_1,
)


class ContinuationRectangleDetector(
    PatternDetector
):
    """
    Rectangle précédé d'une impulsion.

    Contrairement au HorizontalRangeDetector,
    celui-ci possède une direction de continuation.
    """

    name = (
        "continuation_rectangle_detector"
    )

    version = "1.0.0"

    def __init__(
        self,
        config:
        ContinuationPatternConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or ContinuationPatternConfig()
        )

        self._impulse_detector = (
            ImpulseDetector(
                self._config
            )
        )

        self._consolidation_builder = (
            ConsolidationBuilder(
                self._config
            )
        )

    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        impulse = (
            self._impulse_detector
            .detect_best(
                context
            )
        )

        if impulse is None:

            return ()

        consolidation = (
            self._consolidation_builder
            .build(

                context=context,

                impulse=impulse,
            )
        )

        if consolidation is None:

            return ()

        if (

            consolidation
            .retracement_ratio

            >

            self._config
            .max_rectangle_retracement
        ):

            return ()

        upper = abs(

            consolidation
            .upper_slope_atr
        )

        lower = abs(

            consolidation
            .lower_slope_atr
        )

        horizontal = (
            self._config
            .horizontal_slope_atr
        )

        if (

            upper > horizontal

            or

            lower > horizontal
        ):

            return ()

        if (

            consolidation
            .parallel_difference_atr

            >

            self._config
            .max_parallel_difference_atr
        ):

            return ()

        pattern_type = (

            PatternType.BULL_RECTANGLE

            if (
                impulse.direction
                == TradeDirection.BUY
            )

            else

            PatternType.BEAR_RECTANGLE
        )

        upper_score = (
            clamp_0_1(

                1.0

                -

                upper

                /

                max(
                    horizontal,
                    1e-12,
                )
            )
        )

        lower_score = (
            clamp_0_1(

                1.0

                -

                lower

                /

                max(
                    horizontal,
                    1e-12,
                )
            )
        )

        geometry_score = (

            upper_score
            + lower_score

        ) / 2

        match = (
            build_continuation_match(

                context=context,

                impulse=impulse,

                consolidation=(
                    consolidation
                ),

                pattern_type=(
                    pattern_type
                ),

                detector_name=(
                    self.name
                ),

                detector_version=(
                    self.version
                ),

                geometry_score=(
                    geometry_score
                ),

                config=(
                    self._config
                ),

                extra_metrics=(

                    PatternMetric(
                        "rectangle_upper_horizontal_score",
                        upper_score,
                    ),

                    PatternMetric(
                        "rectangle_lower_horizontal_score",
                        lower_score,
                    ),
                ),
            )
        )

        if (
            match.confidence
            < self._config.min_confidence
        ):

            return ()

        return (
            match,
        )