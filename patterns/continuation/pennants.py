# forex_bot/patterns/continuation/pennants.py

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


class PennantDetector(
    PatternDetector
):
    """
    Bull Pennant / Bear Pennant.

    La géométrie de consolidation est similaire
    à un petit triangle symétrique.

    La direction vient de l'impulsion précédente.
    """

    name = "pennant_detector"

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
            .max_pennant_retracement
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
            .convergence_ratio

            <

            self._config
            .min_pennant_convergence
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

        directional = (
            self._config
            .directional_slope_atr
        )

        # Pour un véritable pennant :
        #
        # résistance descend
        # support monte.
        if not (

            upper
            <= -directional

            and

            lower
            >= directional
        ):

            return ()

        pattern_type = (

            PatternType.BULL_PENNANT

            if (
                impulse.direction
                == TradeDirection.BUY
            )

            else

            PatternType.BEAR_PENNANT
        )

        convergence_score = (
            clamp_0_1(

                consolidation
                .convergence_ratio

                /

                max(

                    self._config
                    .min_pennant_convergence
                    * 2,

                    1e-12,
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
                        .max_pennant_retracement,

                        1e-12,
                    )
                )
            )
        )

        geometry_score = (

            0.65
            * convergence_score

            +

            0.35
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
                        "pennant_convergence_score",
                        convergence_score,
                    ),

                    PatternMetric(
                        "pennant_retracement_score",
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