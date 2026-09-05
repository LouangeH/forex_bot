# forex_bot/patterns/continuation/flags.py

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


class FlagDetector(
    PatternDetector
):
    """
    Détecte :

    - Bull Flag ;
    - Bear Flag.
    """

    name = "flag_detector"

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

            consolidation.retracement_ratio

            >

            self._config
            .max_flag_retracement
        ):

            return ()

        if (

            consolidation
            .height_vs_impulse

            >

            self._config
            .max_consolidation_height_vs_impulse
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

        upper = (
            consolidation
            .upper_slope_atr
        )

        lower = (
            consolidation
            .lower_slope_atr
        )

        horizontal = (
            self._config
            .horizontal_slope_atr
        )

        directional = (
            self._config
            .directional_slope_atr
        )

        # ==========================================
        # BULL FLAG
        # ==========================================

        if (
            impulse.direction
            == TradeDirection.BUY
        ):

            valid_direction = (

                upper
                <= horizontal

                and

                lower
                <= horizontal

                and

                (

                    upper
                    <= -directional

                    or

                    lower
                    <= -directional

                    or

                    (

                        abs(upper)
                        <= horizontal

                        and

                        abs(lower)
                        <= horizontal
                    )
                )
            )

            pattern_type = (
                PatternType.BULL_FLAG
            )

        # ==========================================
        # BEAR FLAG
        # ==========================================

        else:

            valid_direction = (

                upper
                >= -horizontal

                and

                lower
                >= -horizontal

                and

                (

                    upper
                    >= directional

                    or

                    lower
                    >= directional

                    or

                    (

                        abs(upper)
                        <= horizontal

                        and

                        abs(lower)
                        <= horizontal
                    )
                )
            )

            pattern_type = (
                PatternType.BEAR_FLAG
            )

        if not valid_direction:

            return ()

        parallel_score = (
            clamp_0_1(

                1.0

                -

                (

                    consolidation
                    .parallel_difference_atr

                    /

                    max(

                        self._config
                        .max_parallel_difference_atr,

                        1e-12,
                    )
                )
            )
        )

        retracement_score = (
            clamp_0_1(

                1.0

                -

                (

                    consolidation
                    .retracement_ratio

                    /

                    max(

                        self._config
                        .max_flag_retracement,

                        1e-12,
                    )
                )
            )
        )

        geometry_score = (

            0.60
            * parallel_score

            +

            0.40
            * retracement_score
        )

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
                        "flag_parallel_score",
                        parallel_score,
                    ),

                    PatternMetric(
                        "flag_retracement_score",
                        retracement_score,
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