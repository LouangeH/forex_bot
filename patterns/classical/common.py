# forex_bot/patterns/classical/common.py

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from forex_bot.patterns.geometry.scoring import (
    line_pattern_confidence,
)

from forex_bot.patterns.geometry.structure import (
    LineStructure,
)


def build_line_pattern_match(
    *,
    context: PatternContext,

    structure: LineStructure,

    pattern_type: PatternType,

    role: PatternRole,

    bias: MarketBias,

    detector_name: str,

    detector_version: str,

    geometry_score: float,

    extra_metrics: tuple[
        PatternMetric,
        ...
    ] = (),
) -> PatternMatch:
    """
    Construit le PatternMatch final
    de manière standardisée.
    """

    confidence = (
        line_pattern_confidence(

            structure,

            geometry_score=(
                geometry_score
            ),
        )
    )

    if (
        bias
        == MarketBias.BULLISH
    ):

        breakout_level = (
            structure.upper.value_at(
                context.as_of_index
            )
        )

    elif (
        bias
        == MarketBias.BEARISH
    ):

        breakout_level = (
            structure.lower.value_at(
                context.as_of_index
            )
        )

    else:

        # Exemple :
        # triangle symétrique.
        #
        # Il peut casser dans les deux sens.
        # Le BreakoutEngine surveillera
        # donc les deux frontières.
        breakout_level = None

    source_indexes = tuple(

        sorted(

            set(

                structure.high_pivot_indexes

                +

                structure.low_pivot_indexes
            )
        )
    )

    return PatternMatch(

        symbol=context.symbol,

        timeframe=context.timeframe,

        pattern_type=pattern_type,

        family=(
            PatternFamily.CLASSICAL
        ),

        role=role,

        # La figure est confirmée géométriquement.
        #
        # BROKEN_OUT sera réservé
        # au futur BreakoutEngine.
        status=(
            PatternStatus.CONFIRMED
        ),

        bias=bias,

        start_time=(
            context.candles[
                structure.start_index
            ].open_time
        ),

        end_time=(
            context.candles[
                structure.end_index
            ].open_time
        ),

        start_index=(
            structure.start_index
        ),

        end_index=(
            structure.end_index
        ),

        confidence=confidence,

        detector_name=(
            detector_name
        ),

        detector_version=(
            detector_version
        ),

        upper_boundary=(
            structure.upper
        ),

        lower_boundary=(
            structure.lower
        ),

        breakout_level=(
            breakout_level
        ),

        metrics=(

            structure.metrics()

            + extra_metrics
        ),

        source_pivot_indexes=(
            source_indexes
        ),
    )