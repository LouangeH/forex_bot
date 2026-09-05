# forex_bot/patterns/harmonic/scanner.py

from __future__ import annotations

from collections.abc import Sequence

from forex_bot.core.enums import (
    PivotType,
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


def recent_pivots(
    context: PatternContext,
    config: HarmonicConfig,
) -> tuple[
    DetectedPivot,
    ...
]:
    """
    Pivots accessibles au moteur harmonique.

    Protection importante :
    confirmation_index doit déjà être connue.
    """

    minimum_index = max(

        0,

        context.as_of_index
        - config.lookback_bars,
    )

    pivots = [

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

    pivots.sort(
        key=lambda item:
        item.pivot.candle_index
    )

    return tuple(

        pivots[
            -config.max_recent_pivots:
        ]
    )


def alternating_windows(
    pivots: Sequence[
        DetectedPivot
    ],
    length: int,
) -> tuple[
    tuple[
        DetectedPivot,
        ...
    ],
    ...
]:
    """
    Retourne uniquement les séquences alternées :

        LOW HIGH LOW HIGH LOW

    ou

        HIGH LOW HIGH LOW HIGH

    Une figure harmonique basée sur des swings
    ne doit pas accepter par exemple :

        LOW LOW HIGH HIGH LOW
    """

    windows = []

    for start in range(

        0,

        len(pivots)
        - length
        + 1,
    ):

        window = tuple(
            pivots[
                start:
                start + length
            ]
        )

        alternating = all(

            first.pivot.pivot_type
            != second.pivot.pivot_type

            for first, second
            in zip(
                window,
                window[1:],
                strict=False,
            )
        )

        if alternating:

            windows.append(
                window
            )

    return tuple(
        windows
    )


def valid_pattern_duration(
    *,
    pivots: Sequence[DetectedPivot],
    context: PatternContext,
    config: HarmonicConfig,
) -> bool:

    first_index = (
        pivots[0]
        .pivot
        .candle_index
    )

    last_index = (
        pivots[-1]
        .pivot
        .candle_index
    )

    duration = (
        last_index
        - first_index
    )

    if not (

        config.min_pattern_bars

        <= duration

        <= config.max_pattern_bars
    ):

        return False

    age = (

        context.as_of_index

        - last_index
    )

    return (
        age
        <= config.max_pattern_age_bars
    )