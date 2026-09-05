from dataclasses import dataclass
from datetime import datetime

from forex_bot.core.models import Pivot
from forex_bot.core.enums import PivotType


@dataclass(
    frozen=True,
    slots=True,
)
class PivotCandidate:
    """
    Pivot potentiel détecté avant le filtrage final.

    Cet objet reste interne au module pivots.
    """

    pivot_type: PivotType

    candle_index: int

    price: float

    prominence: float

    atr: float

    prominence_atr: float


@dataclass(
    frozen=True,
    slots=True,
)
class DetectedPivot:
    """
    Pivot final accompagné des informations
    permettant de comprendre sa qualité.

    pivot :
        représentation métier générale.

    atr :
        volatilité lorsque le pivot s'est formé.

    prominence_atr :
        importance du pivot normalisée par ATR.

    confirmation_index :
        index de la dernière bougie ayant confirmé
        le pivot.

    confirmation_candle_time :
        heure d'ouverture de cette bougie.

    Très important pour éviter le look-ahead bias.
    """

    pivot: Pivot

    atr: float

    prominence_atr: float

    confirmation_index: int

    confirmation_candle_time: datetime