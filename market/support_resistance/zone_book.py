# forex_bot/market/support_resistance/zone_book.py

from collections.abc import Sequence

from forex_bot.core.enums import (
    ZoneType,
)

from .types import (
    DetectedZone,
)


class ZoneBook:
    """
    Permet aux futures stratégies de rechercher
    facilement les zones détectées.

    Cette classe ne modifie jamais les zones.
    """

    def __init__(
        self,
        zones: Sequence[DetectedZone],
    ) -> None:

        self._zones = tuple(
            sorted(
                zones,

                key=lambda zone:
                zone.center_price,
            )
        )

    @property
    def all(
        self,
    ) -> tuple[
        DetectedZone,
        ...
    ]:

        return self._zones

    @property
    def supports(
        self,
    ) -> tuple[
        DetectedZone,
        ...
    ]:

        return tuple(

            zone

            for zone
            in self._zones

            if (
                zone.zone.zone_type
                == ZoneType.SUPPORT
            )
        )

    @property
    def resistances(
        self,
    ) -> tuple[
        DetectedZone,
        ...
    ]:

        return tuple(

            zone

            for zone
            in self._zones

            if (
                zone.zone.zone_type
                == ZoneType.RESISTANCE
            )
        )

    def containing(
        self,
        price: float,
    ) -> tuple[
        DetectedZone,
        ...
    ]:
        """
        Retourne les zones contenant
        directement le prix.
        """

        return tuple(

            zone

            for zone
            in self._zones

            if (
                zone.lower_price
                <= price
                <= zone.upper_price
            )
        )

    def nearest_support(
        self,
        price: float,
    ) -> DetectedZone | None:
        """
        Support immédiatement sous le prix.

        Si le prix se trouve déjà dans un support,
        cette zone est retournée.
        """

        containing_supports = [

            zone

            for zone
            in self.supports

            if (
                zone.lower_price
                <= price
                <= zone.upper_price
            )
        ]

        if containing_supports:

            return max(
                containing_supports,

                key=lambda zone:
                zone.score.total,
            )

        candidates = [

            zone

            for zone
            in self.supports

            if (
                zone.upper_price
                < price
            )
        ]

        if not candidates:

            return None

        return max(
            candidates,

            key=lambda zone:
            zone.upper_price,
        )

    def nearest_resistance(
        self,
        price: float,
    ) -> DetectedZone | None:
        """
        Résistance immédiatement au-dessus du prix.
        """

        containing_resistances = [

            zone

            for zone
            in self.resistances

            if (
                zone.lower_price
                <= price
                <= zone.upper_price
            )
        ]

        if containing_resistances:

            return max(
                containing_resistances,

                key=lambda zone:
                zone.score.total,
            )

        candidates = [

            zone

            for zone
            in self.resistances

            if (
                zone.lower_price
                > price
            )
        ]

        if not candidates:

            return None

        return min(
            candidates,

            key=lambda zone:
            zone.lower_price,
        )

    def above(
        self,
        price: float,
    ) -> tuple[
        DetectedZone,
        ...
    ]:

        return tuple(

            zone

            for zone
            in self._zones

            if (
                zone.lower_price
                > price
            )
        )

    def below(
        self,
        price: float,
    ) -> tuple[
        DetectedZone,
        ...
    ]:

        return tuple(

            zone

            for zone
            in self._zones

            if (
                zone.upper_price
                < price
            )
        )