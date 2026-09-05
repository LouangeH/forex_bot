# forex_bot/market/support_resistance/reaction.py

from collections.abc import Sequence

from forex_bot.core.enums import (
    PivotType,
)

from forex_bot.core.models import (
    Candle,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from .config import (
    SupportResistanceConfig,
)


class ReactionAnalyzer:
    """
    Mesure la réaction du marché après un pivot.

    Le résultat est exprimé en ATR.

    Exemple :

        reaction_atr = 1.4

    signifie que le prix s'est éloigné du niveau
    d'environ 1.4 ATR.
    """

    def __init__(
        self,
        config: SupportResistanceConfig,
    ) -> None:

        self._config = config

    def reaction_atr(
        self,
        *,
        candles: Sequence[Candle],

        pivot: DetectedPivot,

        as_of_index: int,
    ) -> float:

        start_index = (
            pivot.pivot.candle_index
            + 1
        )

        end_index = min(
            as_of_index,

            pivot.pivot.candle_index
            + self._config.reaction_bars,
        )

        if (
            start_index
            > end_index
        ):

            return 0.0

        window = candles[
            start_index
            :
            end_index + 1
        ]

        if (
            not window
            or pivot.atr <= 0
        ):

            return 0.0

        if (
            pivot.pivot.pivot_type
            == PivotType.HIGH
        ):

            lowest_after = min(
                candle.low
                for candle
                in window
            )

            reaction = (
                pivot.pivot.price
                - lowest_after
            )

        else:

            highest_after = max(
                candle.high
                for candle
                in window
            )

            reaction = (
                highest_after
                - pivot.pivot.price
            )

        return max(
            0.0,
            reaction / pivot.atr,
        )