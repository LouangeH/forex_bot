# forex_bot/patterns/continuation/common.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
    TradeDirection,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .config import (
    ContinuationPatternConfig,
)

from .scoring import (
    continuation_confidence,
)

from .types import (
    ConsolidationStructure,
    ImpulseLeg,
)


def build_continuation_match(
    *,
    context: PatternContext,

    impulse: ImpulseLeg,

    consolidation:
    ConsolidationStructure,

    pattern_type: PatternType,

    detector_name: str,

    detector_version: str,

    geometry_score: float,

    config:
    ContinuationPatternConfig,

    extra_metrics: tuple[
        PatternMetric,
        ...
    ] = (),
) -> PatternMatch:
    """
    Construction standardisée d'une figure
    de continuation.
    """

    if (
        impulse.direction
        == TradeDirection.BUY
    ):

        bias = (
            MarketBias.BULLISH
        )

        breakout_level = (
            consolidation
            .upper
            .value_at(
                context.as_of_index
            )
        )

    else:

        bias = (
            MarketBias.BEARISH
        )

        breakout_level = (
            consolidation
            .lower
            .value_at(
                context.as_of_index
            )
        )

    confidence = (
        continuation_confidence(

            impulse=impulse,

            consolidation=(
                consolidation
            ),

            geometry_score=(
                geometry_score
            ),

            config=config,
        )
    )

    source_indexes = tuple(

        sorted(

            set(

                consolidation
                .high_pivot_indexes

                +

                consolidation
                .low_pivot_indexes

                +

                (
                    impulse.start_index,
                    impulse.end_index,
                )
            )
        )
    )

    return PatternMatch(

        symbol=(
            context.symbol
        ),

        timeframe=(
            context.timeframe
        ),

        pattern_type=(
            pattern_type
        ),

        family=(
            PatternFamily.CLASSICAL
        ),

        role=(
            PatternRole.CONTINUATION
        ),

        status=(
            PatternStatus.CONFIRMED
        ),

        bias=bias,

        start_time=(

            context.candles[
                impulse.start_index
            ].open_time
        ),

        end_time=(

            context.candles[
                consolidation.end_index
            ].open_time
        ),

        start_index=(
            impulse.start_index
        ),

        end_index=(
            consolidation.end_index
        ),

        confidence=(
            confidence
        ),

        detector_name=(
            detector_name
        ),

        detector_version=(
            detector_version
        ),

        upper_boundary=(
            consolidation.upper
        ),

        lower_boundary=(
            consolidation.lower
        ),

        breakout_level=(
            breakout_level
        ),

        metrics=(

            impulse.metrics()

            +

            consolidation.metrics()

            +

            extra_metrics
        ),

        source_pivot_indexes=(
            source_indexes
        ),
    )