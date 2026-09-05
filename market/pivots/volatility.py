from collections.abc import Sequence

from forex_bot.core.models import Candle


def true_range(
    current: Candle,
    previous: Candle,
) -> float:
    """
    True Range d'une bougie.

    TR = maximum de :

    1. HIGH - LOW
    2. |HIGH - clôture précédente|
    3. |LOW - clôture précédente|

    Cela permet de prendre en compte les gaps
    et pas seulement la taille de la bougie.
    """

    high_low = (
        current.high
        - current.low
    )

    high_previous_close = abs(
        current.high
        - previous.close
    )

    low_previous_close = abs(
        current.low
        - previous.close
    )

    return max(
        high_low,
        high_previous_close,
        low_previous_close,
    )


def atr_at_index(
    candles: Sequence[Candle],
    index: int,
    period: int,
) -> float | None:
    """
    Calcule l'ATR disponible AU MOMENT du pivot.

    Important :
    nous utilisons seulement les bougies antérieures
    ou égales au pivot.

    Nous n'utilisons jamais les bougies futures
    pour calculer sa volatilité.

    Cela évite le look-ahead bias dans les backtests.
    """

    if index < period:

        return None

    start_index = (
        index
        - period
        + 1
    )

    true_ranges: list[float] = []

    for current_index in range(
        start_index,
        index + 1,
    ):

        previous_index = (
            current_index
            - 1
        )

        current = candles[
            current_index
        ]

        previous = candles[
            previous_index
        ]

        true_ranges.append(
            true_range(
                current,
                previous,
            )
        )

    if not true_ranges:

        return None

    return (
        sum(true_ranges)
        / len(true_ranges)
    )