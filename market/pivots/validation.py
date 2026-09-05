from collections.abc import Sequence

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    Candle,
    SymbolSpec,
)


def validate_candle_series(
    candles: Sequence[Candle],
    symbol_spec: SymbolSpec,
) -> None:
    """
    Vérifie qu'une série de bougies peut être
    utilisée par le détecteur.

    Protections :
    - série non vide ;
    - même symbole ;
    - même timeframe ;
    - ordre chronologique strict ;
    - aucune bougie dupliquée.
    """

    if not candles:

        raise DomainValidationError(
            "La série de bougies est vide."
        )

    expected_symbol = candles[0].symbol
    expected_timeframe = candles[0].timeframe

    if (
        expected_symbol
        != symbol_spec.symbol
    ):

        raise DomainValidationError(
            "Le symbole des bougies ne correspond "
            "pas aux spécifications du symbole."
        )

    previous_time = None

    seen_times = set()

    for index, candle in enumerate(candles):

        if (
            candle.symbol
            != expected_symbol
        ):

            raise DomainValidationError(
                f"Bougie {index} : "
                "symbole différent."
            )

        if (
            candle.timeframe
            != expected_timeframe
        ):

            raise DomainValidationError(
                f"Bougie {index} : "
                "timeframe différent."
            )

        if (
            candle.open_time
            in seen_times
        ):

            raise DomainValidationError(
                f"Bougie dupliquée : "
                f"{candle.open_time}."
            )

        seen_times.add(
            candle.open_time
        )

        if (
            previous_time is not None
            and candle.open_time
            <= previous_time
        ):

            raise DomainValidationError(
                "Les bougies doivent être "
                "strictement chronologiques."
            )

        previous_time = (
            candle.open_time
        )