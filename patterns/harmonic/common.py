# forex_bot/patterns/harmonic/common.py

from __future__ import annotations

from collections.abc import Sequence

from statistics import fmean, median

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
    PivotType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .config import (
    HarmonicConfig,
)


def harmonic_bias(
    pivots: Sequence[
        DetectedPivot
    ],
) -> MarketBias | None:
    """
    Pattern qui termine sur un Pivot LOW :
        potentiel retournement haussier.

    Pattern qui termine sur un Pivot HIGH :
        potentiel retournement baissier.
    """

    last_type = (
        pivots[-1]
        .pivot
        .pivot_type
    )

    if (
        last_type
        == PivotType.LOW
    ):

        return (
            MarketBias.BULLISH
        )

    if (
        last_type
        == PivotType.HIGH
    ):

        return (
            MarketBias.BEARISH
        )

    return None


def median_pattern_atr(
    pivots: Sequence[
        DetectedPivot
    ],
) -> float | None:

    values = [

        pivot.atr

        for pivot
        in pivots

        if pivot.atr > 0
    ]

    if not values:

        return None

    return median(
        values
    )


def all_legs_large_enough(
    *,
    prices: Sequence[float],
    atr: float,
    minimum_atr: float,
) -> bool:
    """
    Empêche un pattern dont une jambe
    serait uniquement du bruit.
    """

    if (
        atr <= 0
        or len(prices) < 2
    ):

        return False

    minimum = (
        atr
        * minimum_atr
    )

    return all(

        abs(
            second
            - first
        )
        >= minimum

        for first, second
        in zip(
            prices,
            prices[1:],
            strict=False,
        )
    )


def prominence_score(
    pivots: Sequence[
        DetectedPivot
    ],
) -> float:

    if not pivots:

        return 0.0

    average = fmean(

        pivot.prominence_atr

        for pivot
        in pivots
    )

    return min(
        1.0,

        average
        / 1.50,
    )


def final_harmonic_confidence(
    *,
    ratio_score: float,
    pivot_score: float,
    config: HarmonicConfig,
) -> float:

    return min(

        1.0,

        (
            ratio_score
            * config.ratio_weight
        )

        +

        (
            pivot_score
            * config.prominence_weight
        ),
    )


def build_harmonic_match(
    *,
    context: PatternContext,

    pivots: Sequence[
        DetectedPivot
    ],

    pattern_type: PatternType,

    confidence: float,

    detector_name: str,

    detector_version: str,

    metrics: tuple[
        PatternMetric,
        ...
    ],
) -> PatternMatch:

    bias = harmonic_bias(
        pivots
    )

    if bias is None:

        raise ValueError(
            "Impossible de déterminer "
            "le bias harmonique."
        )

    return PatternMatch(

        symbol=context.symbol,

        timeframe=context.timeframe,

        pattern_type=(
            pattern_type
        ),

        family=(
            PatternFamily.HARMONIC
        ),

        role=(
            PatternRole.REVERSAL
        ),

        status=(
            PatternStatus.CONFIRMED
        ),

        bias=bias,

        start_time=(
            pivots[0]
            .pivot
            .time
        ),

        end_time=(
            pivots[-1]
            .pivot
            .time
        ),

        start_index=(
            pivots[0]
            .pivot
            .candle_index
        ),

        end_index=(
            pivots[-1]
            .pivot
            .candle_index
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

        upper_boundary=None,

        lower_boundary=None,

        # La formation harmonique terminée à D
        # n'est pas encore une cassure.
        breakout_level=None,

        metrics=metrics,

        source_pivot_indexes=tuple(

            pivot.pivot.candle_index

            for pivot
            in pivots
        ),
    )