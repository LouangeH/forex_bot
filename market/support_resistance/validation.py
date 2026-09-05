# forex_bot/market/support_resistance/validation.py

from collections.abc import Sequence

from forex_bot.core.enums import (
    PivotType,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    Candle,
    SymbolSpec,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from forex_bot.market.pivots.validation import (
    validate_candle_series,
)


def validate_support_resistance_inputs(
    *,
    candles: Sequence[Candle],

    pivots: Sequence[DetectedPivot],

    symbol_spec: SymbolSpec,

    as_of_index: int,
) -> None:
    """
    Vérifie la cohérence des données avant
    toute détection S/R.

    as_of_index représente la dernière bougie
    que le moteur a le droit de connaître.
    """

    validate_candle_series(
        candles,
        symbol_spec,
    )

    if not (
        0
        <= as_of_index
        < len(candles)
    ):

        raise DomainValidationError(
            "as_of_index invalide."
        )

    expected_symbol = (
        candles[0].symbol
    )

    expected_timeframe = (
        candles[0].timeframe
    )

    for detected in pivots:

        pivot = detected.pivot

        if (
            pivot.symbol
            != expected_symbol
        ):

            raise DomainValidationError(
                "Un pivot appartient "
                "à un autre symbole."
            )

        if (
            pivot.timeframe
            != expected_timeframe
        ):

            raise DomainValidationError(
                "Un pivot appartient "
                "à un autre timeframe."
            )

        if (
            pivot.candle_index
            >= len(candles)
        ):

            raise DomainValidationError(
                "pivot.candle_index "
                "dépasse les données."
            )

        if (
            detected.confirmation_index
            >= len(candles)
        ):

            raise DomainValidationError(
                "confirmation_index "
                "dépasse les données."
            )

        pivot_candle = candles[
            pivot.candle_index
        ]

        confirmation_candle = candles[
            detected.confirmation_index
        ]

        if (
            pivot.time
            != pivot_candle.open_time
        ):

            raise DomainValidationError(
                "Heure du pivot incohérente."
            )

        if (
            detected
            .confirmation_candle_time
            != confirmation_candle.open_time
        ):

            raise DomainValidationError(
                "Heure de confirmation "
                "incohérente."
            )

        # Petite tolérance liée aux arrondis
        # des prix du broker.
        tolerance = max(
            symbol_spec.point * 2,
            1e-12,
        )

        expected_price = (
            pivot_candle.high
            if (
                pivot.pivot_type
                == PivotType.HIGH
            )
            else pivot_candle.low
        )

        if (
            abs(
                pivot.price
                - expected_price
            )
            > tolerance
        ):

            raise DomainValidationError(
                "Le prix du pivot ne correspond "
                "pas au HIGH/LOW de sa bougie."
            )