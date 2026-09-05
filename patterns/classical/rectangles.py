# forex_bot/patterns/classical/rectangles.py

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


class HorizontalRangeDetector(
    PatternDetector
):
    """
    Détecte une structure horizontale.

    La classification Bull Rectangle /
    Bear Rectangle sera faite plus tard
    à partir de la tendance précédente.
    """

    name = (
        "horizontal_range_detector"
    )

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

        horizontal = (
            self._config
            .horizontal_slope_atr
        )

        upper = (
            structure.upper_slope_atr
        )

        lower = (
            structure.lower_slope_atr
        )

        if (

            abs(upper)
            > horizontal

            or

            abs(lower)
            > horizontal
        ):

            return ()

        upper_score = (
            clamp_0_1(

                1.0

                -

                abs(upper)

                / max(
                    horizontal,
                    1e-12,
                )
            )
        )

        lower_score = (
            clamp_0_1(

                1.0

                -

                abs(lower)

                / max(
                    horizontal,
                    1e-12,
                )
            )
        )

        geometry_score = (

            upper_score
            + lower_score

        ) / 2

        return (

            build_line_pattern_match(

                context=context,

                structure=structure,

                pattern_type=(
                    PatternType.HORIZONTAL_RANGE
                ),

                role=(
                    PatternRole.NEUTRAL
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
                    geometry_score
                ),
            ),

        )