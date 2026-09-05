# forex_bot/patterns/classical/triangles.py

from forex_bot.core.enums import (
    MarketBias,
    PatternRole,
    PatternType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.patterns.base import (
    PatternDetector,
)

from forex_bot.patterns.config import (
    LinePatternConfig,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from forex_bot.patterns.geometry.scoring import (
    clamp_0_1,
)

from forex_bot.patterns.geometry.structure import (
    LineStructureBuilder,
)

from .common import (
    build_line_pattern_match,
)


class TriangleDetector(
    PatternDetector
):
    """
    Détecte :

    - Ascending Triangle ;
    - Descending Triangle ;
    - Symmetrical Triangle.
    """

    name = "triangle_detector"

    version = "1.0.0"

    def __init__(
        self,
        config:
        LinePatternConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or LinePatternConfig()
        )

        self._builder = (
            LineStructureBuilder(
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

        structure = (
            self._builder.build(
                context
            )
        )

        if structure is None:

            return ()

        if (

            structure.upper.r_squared
            < self._config.min_r_squared

            or

            structure.lower.r_squared
            < self._config.min_r_squared
        ):

            return ()

        if (
            structure.convergence_ratio
            <
            self._config
            .min_convergence_ratio
        ):

            return ()

        upper = (
            structure.upper_slope_atr
        )

        lower = (
            structure.lower_slope_atr
        )

        horizontal = (
            self._config
            .horizontal_slope_atr
        )

        directional = (
            self._config
            .directional_slope_atr
        )

        convergence_score = (
            clamp_0_1(

                structure
                .convergence_ratio

                /

                max(
                    self._config
                    .min_convergence_ratio
                    * 2,

                    1e-12,
                )
            )
        )

        # =========================================
        # ASCENDING TRIANGLE
        #
        # Résistance horizontale
        # +
        # support montant.
        # =========================================

        if (

            abs(upper)
            <= horizontal

            and

            lower
            >= directional
        ):

            return (

                build_line_pattern_match(

                    context=context,

                    structure=structure,

                    pattern_type=(
                        PatternType
                        .ASCENDING_TRIANGLE
                    ),

                    role=(
                        PatternRole
                        .CONTINUATION
                    ),

                    bias=(
                        MarketBias.BULLISH
                    ),

                    detector_name=(
                        self.name
                    ),

                    detector_version=(
                        self.version
                    ),

                    geometry_score=(
                        convergence_score
                    ),

                    extra_metrics=(

                        PatternMetric(

                            "horizontal_upper_score",

                            clamp_0_1(

                                1.0
                                -
                                abs(upper)
                                /
                                max(
                                    horizontal,
                                    1e-12,
                                )
                            ),
                        ),

                    ),
                ),

            )

        # =========================================
        # DESCENDING TRIANGLE
        # =========================================

        if (

            abs(lower)
            <= horizontal

            and

            upper
            <= -directional
        ):

            return (

                build_line_pattern_match(

                    context=context,

                    structure=structure,

                    pattern_type=(
                        PatternType
                        .DESCENDING_TRIANGLE
                    ),

                    role=(
                        PatternRole
                        .CONTINUATION
                    ),

                    bias=(
                        MarketBias.BEARISH
                    ),

                    detector_name=(
                        self.name
                    ),

                    detector_version=(
                        self.version
                    ),

                    geometry_score=(
                        convergence_score
                    ),

                    extra_metrics=(

                        PatternMetric(

                            "horizontal_lower_score",

                            clamp_0_1(

                                1.0
                                -
                                abs(lower)
                                /
                                max(
                                    horizontal,
                                    1e-12,
                                )
                            ),
                        ),

                    ),
                ),

            )

        # =========================================
        # SYMMETRICAL TRIANGLE
        # =========================================

        if (

            upper
            <= -directional

            and

            lower
            >= directional
        ):

            return (

                build_line_pattern_match(

                    context=context,

                    structure=structure,

                    pattern_type=(
                        PatternType
                        .SYMMETRICAL_TRIANGLE
                    ),

                    role=(
                        PatternRole.BILATERAL
                    ),

                    bias=(
                        MarketBias.NEUTRAL
                    ),

                    detector_name=(
                        self.name
                    ),

                    detector_version=(
                        self.version
                    ),

                    geometry_score=(
                        convergence_score
                    ),
                ),

            )

        return ()