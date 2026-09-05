# forex_bot/patterns/context.py

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from forex_bot.core.exceptions import DomainValidationError
from forex_bot.core.models import Candle, SymbolSpec

from forex_bot.market.pivots.types import DetectedPivot

from forex_bot.market.support_resistance.types import (
    DetectedZone,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PatternContext:
    """
    Photographie immuable du marché envoyée
    aux détecteurs de figures.

    Les détecteurs n'ont aucun accès direct à MT5.

    Cela permet :
    - les tests ;
    - le backtesting ;
    - le fonctionnement live ;
    - d'éviter le look-ahead bias.
    """

    candles: tuple[Candle, ...]

    pivots: tuple[DetectedPivot, ...]

    zones: tuple[DetectedZone, ...]

    symbol_spec: SymbolSpec

    as_of_index: int

    @classmethod
    def build(
        cls,
        *,
        candles: Sequence[Candle],
        pivots: Sequence[DetectedPivot],
        zones: Sequence[DetectedZone],
        symbol_spec: SymbolSpec,
        as_of_index: int | None = None,
    ) -> "PatternContext":

        if not candles:

            raise DomainValidationError(
                "PatternContext exige au moins "
                "une bougie."
            )

        resolved_as_of = (
            len(candles) - 1

            if as_of_index is None

            else as_of_index
        )

        if not (
            0
            <= resolved_as_of
            < len(candles)
        ):

            raise DomainValidationError(
                "as_of_index est hors "
                "de la série."
            )

        symbol = candles[0].symbol

        timeframe = candles[0].timeframe

        if (
            symbol
            != symbol_spec.symbol
        ):

            raise DomainValidationError(
                "Le symbole des bougies "
                "ne correspond pas "
                "au SymbolSpec."
            )

        for candle in candles:

            if (
                candle.symbol != symbol
                or
                candle.timeframe
                != timeframe
            ):

                raise DomainValidationError(
                    "Toutes les bougies doivent "
                    "avoir le même symbole "
                    "et timeframe."
                )

        # On supprime automatiquement
        # les pivots qui n'étaient pas encore
        # connus au moment analysé.
        known_pivots = tuple(

            pivot

            for pivot
            in pivots

            if (
                pivot.confirmation_index
                <= resolved_as_of
            )
        )

        # Même protection pour les zones.
        known_zones = tuple(

            zone

            for zone
            in zones

            if (
                zone.confirmed_from_index
                <= resolved_as_of
            )
        )

        return cls(

            candles=tuple(candles),

            pivots=known_pivots,

            zones=known_zones,

            symbol_spec=symbol_spec,

            as_of_index=resolved_as_of,
        )

    @property
    def symbol(self) -> str:

        return self.candles[0].symbol

    @property
    def timeframe(self):

        return self.candles[0].timeframe

    @property
    def as_of_candle(self) -> Candle:

        return self.candles[
            self.as_of_index
        ]