# forex_bot/patterns/classical/channels.py

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


class ChannelDetector(
    PatternDetector
):
    """
    Détecte :

    - Rising Channel ;
    - Falling Channel ;
    - Horizontal Channel.
    """

    name = "channel_detector"

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
            structure
            .parallel_difference_atr
            >
            self._config
            .max_parallel_slope_difference_atr
        ):

            return ()

        # Un canal ne doit pas fortement converger.
        if (
            structure.convergence_ratio
            >
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

        horizontal = (
            self._config
            .horizontal_slope_atr
        )

        geometry_score = (
            clamp_0_1(

                1.0

                -

                (
                    structure
                    .parallel_difference_atr

                    /

                    max(
                        self._config
                        .max_parallel_slope_difference_atr,

                        1e-12,
                    )
                )
            )
        )

        if (

            upper >= directional

            and

            lower >= directional
        ):

            pattern_type = (
                PatternType.RISING_CHANNEL
            )

            bias = (
                MarketBias.BULLISH
            )

        elif (

            upper <= -directional

            and

            lower <= -directional
        ):

            pattern_type = (
                PatternType.FALLING_CHANNEL
            )

            bias = (
                MarketBias.BEARISH
            )

        elif (

            abs(upper) <= horizontal

            and

            abs(lower) <= horizontal
        ):

            pattern_type = (
                PatternType.HORIZONTAL_CHANNEL
            )

            bias = (
                MarketBias.NEUTRAL
            )

        else:

            return ()

        return (

            build_line_pattern_match(

                context=context,

                structure=structure,

                pattern_type=pattern_type,

                role=(
                    PatternRole.CONTINUATION
                ),

                bias=bias,

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