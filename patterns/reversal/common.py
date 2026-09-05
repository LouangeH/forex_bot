# forex_bot/patterns/reversal/common.py

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
    LinearBoundary,
    PatternMatch,
    PatternMetric,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from forex_bot.patterns.geometry.regression import (
    fit_linear_boundary,
)

from .config import (
    ReversalPatternConfig,
)


def clamp_0_1(
    value: float,
) -> float:

    return min(
        1.0,
        max(
            0.0,
            value,
        ),
    )


def recent_pivots(
    context: PatternContext,
    config: ReversalPatternConfig,
) -> tuple[
    DetectedPivot,
    ...
]:
    """
    Retourne uniquement les pivots :

    - déjà confirmés ;
    - suffisamment récents ;
    - dans l'ordre chronologique.
    """

    minimum_index = max(

        0,

        context.as_of_index
        - config.lookback_bars,
    )

    values = [

        pivot

        for pivot
        in context.pivots

        if (
            pivot.confirmation_index
            <= context.as_of_index

            and

            pivot.pivot.candle_index
            >= minimum_index
        )
    ]

    values.sort(
        key=lambda item:
        item.pivot.candle_index
    )

    return tuple(
        values
    )


def median_atr(
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


def level_closeness_score(
    *,
    prices: Sequence[float],
    atr: float,
    tolerance_atr: float,
) -> float:
    """
    Mesure à quel point plusieurs prix
    se trouvent au même niveau.

    1.0 :
        niveaux pratiquement identiques.

    0.0 :
        écart >= tolérance.
    """

    if (
        len(prices) < 2
        or atr <= 0
        or tolerance_atr <= 0
    ):

        return 0.0

    difference = (
        max(prices)
        - min(prices)
    )

    normalized = (
        difference
        / atr
    )

    return clamp_0_1(

        1.0

        -

        normalized
        / tolerance_atr
    )


def average_prominence_score(
    pivots: Sequence[
        DetectedPivot
    ],
) -> float:
    """
    Score simple utilisant la prominence
    déjà calculée à l'étape 2.
    """

    if not pivots:

        return 0.0

    value = fmean(

        pivot.prominence_atr

        for pivot
        in pivots
    )

    return clamp_0_1(
        value / 1.50
    )


def pattern_is_recent(
    *,
    context: PatternContext,
    last_index: int,
    config: ReversalPatternConfig,
) -> bool:

    return (

        context.as_of_index
        - last_index

        <=

        config.max_pattern_age_bars
    )


def neckline_from_pivots(
    first: DetectedPivot,
    second: DetectedPivot,
) -> LinearBoundary:
    """
    Construit mathématiquement une neckline
    à partir de deux creux ou deux sommets.
    """

    return fit_linear_boundary(
        (
            (
                first.pivot.candle_index,
                first.pivot.price,
            ),
            (
                second.pivot.candle_index,
                second.pivot.price,
            ),
        )
    )


def build_reversal_match(
    *,
    context: PatternContext,

    pattern_type: PatternType,

    bias: MarketBias,

    pivots: Sequence[
        DetectedPivot
    ],

    confidence: float,

    detector_name: str,

    detector_version: str,

    breakout_level: float | None = None,

    upper_boundary:
    LinearBoundary | None = None,

    lower_boundary:
    LinearBoundary | None = None,

    metrics: tuple[
        PatternMetric,
        ...
    ] = (),
) -> PatternMatch:
    """
    Construction standardisée des figures
    classiques de retournement.
    """

    first = pivots[0]
    last = pivots[-1]

    return PatternMatch(

        symbol=context.symbol,

        timeframe=context.timeframe,

        pattern_type=pattern_type,

        family=(
            PatternFamily.CLASSICAL
        ),

        role=(
            PatternRole.REVERSAL
        ),

        status=(
            PatternStatus.CONFIRMED
        ),

        bias=bias,

        start_time=(
            first.pivot.time
        ),

        end_time=(
            last.pivot.time
        ),

        start_index=(
            first.pivot.candle_index
        ),

        end_index=(
            last.pivot.candle_index
        ),

        confidence=(
            clamp_0_1(
                confidence
            )
        ),

        detector_name=(
            detector_name
        ),

        detector_version=(
            detector_version
        ),

        upper_boundary=(
            upper_boundary
        ),

        lower_boundary=(
            lower_boundary
        ),

        breakout_level=(
            breakout_level
        ),

        metrics=metrics,

        source_pivot_indexes=tuple(

            pivot.pivot.candle_index

            for pivot
            in pivots
        ),
    )


def prior_market_bias(
    *,
    context: PatternContext,

    start_index: int,

    atr_reference: float,

    bars: int,

    minimum_slope_atr: float,
) -> tuple[
    MarketBias,
    float,
]:
    """
    Estime la tendance juste AVANT une figure.

    On applique une régression linéaire
    sur les clôtures précédentes.

    Retour :
        MarketBias
        slope normalisée par ATR.
    """

    first_index = max(
        0,
        start_index - bars,
    )

    if (
        start_index
        - first_index
        < 2
    ):

        return (
            MarketBias.NEUTRAL,
            0.0,
        )

    points = [

        (
            index,
            context.candles[
                index
            ].close,
        )

        for index
        in range(
            first_index,
            start_index,
        )
    ]

    boundary = (
        fit_linear_boundary(
            points
        )
    )

    slope_atr = (

        boundary.slope
        / atr_reference
    )

    if (
        slope_atr
        >= minimum_slope_atr
    ):

        return (
            MarketBias.BULLISH,
            slope_atr,
        )

    if (
        slope_atr
        <= -minimum_slope_atr
    ):

        return (
            MarketBias.BEARISH,
            slope_atr,
        )

    return (
        MarketBias.NEUTRAL,
        slope_atr,
    )