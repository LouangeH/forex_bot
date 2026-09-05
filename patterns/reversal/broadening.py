# forex_bot/patterns/reversal/broadening.py

from __future__ import annotations

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

from forex_bot.patterns.classical.common import (
    build_line_pattern_match,
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
    prior_market_bias,
)

from .config import (
    ReversalPatternConfig,
)


class BroadeningDetector(
    PatternDetector
):
    """
    Détecte une structure divergente :

    upper slope > 0
    lower slope < 0
    largeur finale > largeur initiale.
    """

    name = "broadening_detector"

    version = "1.0.0"

    def __init__(
        self,
        reversal_config:
        ReversalPatternConfig
        | None = None,

        line_config:
        LinePatternConfig
        | None = None,
    ) -> None:

        self._config = (

            reversal_config

            or

            ReversalPatternConfig()
        )

        self._line_config = (

            line_config

            or

            LinePatternConfig()
        )

        self._builder = (
            LineStructureBuilder(
                self._line_config
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
            <
            self._config
            .broadening_min_r_squared

            or

            structure.lower.r_squared
            <
            self._config
            .broadening_min_r_squared
        ):

            return ()

        directional = (
            self._line_config
            .directional_slope_atr
        )

        if not (

            structure
            .upper_slope_atr
            >= directional

            and

            structure
            .lower_slope_atr
            <= -directional
        ):

            return ()

        divergence = (

            -structure
            .convergence_ratio
        )

        if (
            divergence
            <
            self._config
            .broadening_min_divergence_ratio
        ):

            return ()

        prior_bias, prior_slope = (
            prior_market_bias(

                context=context,

                start_index=(
                    structure.start_index
                ),

                atr_reference=(
                    structure.atr_reference
                ),

                bars=(
                    self._config.context_bars
                ),

                minimum_slope_atr=(
                    self._config
                    .context_min_slope_atr
                ),
            )
        )

        # Après une tendance haussière :
        # potentiel Broadening Top.
        if (
            prior_bias
            == MarketBias.BULLISH
        ):

            pattern_type = (
                PatternType.BROADENING_TOP
            )

            bias = (
                MarketBias.BEARISH
            )

            role = (
                PatternRole.REVERSAL
            )

        # Après tendance baissière :
        # potentiel Broadening Bottom.
        elif (
            prior_bias
            == MarketBias.BEARISH
        ):

            pattern_type = (
                PatternType.BROADENING_BOTTOM
            )

            bias = (
                MarketBias.BULLISH
            )

            role = (
                PatternRole.REVERSAL
            )

        else:

            pattern_type = (
                PatternType
                .BROADENING_FORMATION
            )

            bias = (
                MarketBias.NEUTRAL
            )

            role = (
                PatternRole.NEUTRAL
            )

        divergence_score = clamp_0_1(

            divergence

            /

            (
                self._config
                .broadening_min_divergence_ratio

                * 2
            )
        )

        return (

            build_line_pattern_match(

                context=context,

                structure=structure,

                pattern_type=(
                    pattern_type
                ),

                role=role,

                bias=bias,

                detector_name=(
                    self.name
                ),

                detector_version=(
                    self.version
                ),

                geometry_score=(
                    divergence_score
                ),

                extra_metrics=(

                    PatternMetric(
                        "broadening_divergence_ratio",
                        divergence,
                    ),

                    PatternMetric(
                        "prior_trend_slope_atr",
                        prior_slope,
                    ),
                ),
            ),

        )