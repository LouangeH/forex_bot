# forex_bot/patterns/classical/wedges.py

from forex_bot.core.enums import (
    MarketBias,
    PatternRole,
    PatternType,
)

from forex_bot.core.models import (
    PatternMatch,
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


class WedgeDetector(
    PatternDetector
):
    """
    Rising Wedge :
        deux pentes positives ;
        support plus rapide ;
        convergence.

    Falling Wedge :
        deux pentes négatives ;
        résistance descend plus vite ;
        convergence.
    """

    name = "wedge_detector"

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

        directional = (
            self._config
            .directional_slope_atr
        )

        geometry_score = (
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

        # RISING WEDGE
        if (

            upper >= directional

            and

            lower >= directional

            and

            lower > upper
        ):

            return (

                build_line_pattern_match(

                    context=context,

                    structure=structure,

                    pattern_type=(
                        PatternType.RISING_WEDGE
                    ),

                    role=(
                        PatternRole.REVERSAL
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
                        geometry_score
                    ),
                ),

            )

        # FALLING WEDGE
        if (

            upper <= -directional

            and

            lower <= -directional

            and

            upper < lower
        ):

            return (

                build_line_pattern_match(

                    context=context,

                    structure=structure,

                    pattern_type=(
                        PatternType.FALLING_WEDGE
                    ),

                    role=(
                        PatternRole.REVERSAL
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
                        geometry_score
                    ),
                ),

            )

        return ()