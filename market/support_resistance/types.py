# forex_bot/market/support_resistance/types.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib

from forex_bot.core.enums import (
    PivotType,
    ZoneType,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    PriceZone,
)

from forex_bot.core.validators import (
    aware_utc,
    ensure_enum,
    non_negative_float,
    non_negative_int,
    positive_float,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ZoneTouch:
    """
    Représente un pivot ayant réellement participé
    à la création d'une zone.

    On conserve toutes les informations importantes
    pour pouvoir auditer la zone plus tard.
    """

    pivot_type: PivotType

    pivot_index: int
    confirmation_index: int

    pivot_time: datetime
    confirmation_time: datetime

    price: float

    atr: float

    prominence_atr: float

    reaction_atr: float

    weight: float

    def __post_init__(self) -> None:

        ensure_enum(
            "pivot_type",
            self.pivot_type,
            PivotType,
        )

        non_negative_int(
            "pivot_index",
            self.pivot_index,
        )

        non_negative_int(
            "confirmation_index",
            self.confirmation_index,
        )

        if (
            self.confirmation_index
            < self.pivot_index
        ):

            raise DomainValidationError(
                "confirmation_index ne peut pas "
                "précéder pivot_index."
            )

        object.__setattr__(
            self,
            "pivot_time",
            aware_utc(
                "pivot_time",
                self.pivot_time,
            ),
        )

        object.__setattr__(
            self,
            "confirmation_time",
            aware_utc(
                "confirmation_time",
                self.confirmation_time,
            ),
        )

        if (
            self.confirmation_time
            < self.pivot_time
        ):

            raise DomainValidationError(
                "confirmation_time ne peut pas "
                "précéder pivot_time."
            )

        object.__setattr__(
            self,
            "price",
            positive_float(
                "price",
                self.price,
            ),
        )

        object.__setattr__(
            self,
            "atr",
            positive_float(
                "atr",
                self.atr,
            ),
        )

        object.__setattr__(
            self,
            "prominence_atr",
            non_negative_float(
                "prominence_atr",
                self.prominence_atr,
            ),
        )

        object.__setattr__(
            self,
            "reaction_atr",
            non_negative_float(
                "reaction_atr",
                self.reaction_atr,
            ),
        )

        object.__setattr__(
            self,
            "weight",
            positive_float(
                "weight",
                self.weight,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ZoneScoreBreakdown:
    """
    Décomposition complète du score.

    Au lieu de seulement enregistrer :

        quality = 0.81

    nous saurons POURQUOI la zone a obtenu 0.81.
    """

    touches: float

    prominence: float

    reaction: float

    recency: float

    compactness: float

    total: float

    def __post_init__(self) -> None:

        for field_name in (
            "touches",
            "prominence",
            "reaction",
            "recency",
            "compactness",
            "total",
        ):

            object.__setattr__(
                self,
                field_name,
                ratio_0_1(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )


@dataclass(
    frozen=True,
    slots=True,
)
class DetectedZone:
    """
    Représentation complète d'une zone détectée.

    PriceZone vient du CORE.

    Toutes les informations propres à notre
    algorithme S/R restent dans ce module.
    """

    zone: PriceZone

    median_atr: float

    # Moment où suffisamment de touches étaient
    # enfin confirmées pour reconnaître la zone.
    confirmed_from_index: int

    confirmed_from_time: datetime

    # Dernier contact ayant actualisé la zone.
    last_updated_index: int

    last_updated_time: datetime

    touches_detail: tuple[
        ZoneTouch,
        ...
    ]

    score: ZoneScoreBreakdown

    detector_name: str = (
        "support_resistance"
    )

    detector_version: str = "1.0.0"

    def __post_init__(self) -> None:

        if not isinstance(
            self.zone,
            PriceZone,
        ):

            raise DomainValidationError(
                "zone doit être PriceZone."
            )

        object.__setattr__(
            self,
            "median_atr",
            positive_float(
                "median_atr",
                self.median_atr,
            ),
        )

        non_negative_int(
            "confirmed_from_index",
            self.confirmed_from_index,
        )

        non_negative_int(
            "last_updated_index",
            self.last_updated_index,
        )

        if (
            self.last_updated_index
            < self.confirmed_from_index
        ):

            raise DomainValidationError(
                "last_updated_index invalide."
            )

        object.__setattr__(
            self,
            "confirmed_from_time",
            aware_utc(
                "confirmed_from_time",
                self.confirmed_from_time,
            ),
        )

        object.__setattr__(
            self,
            "last_updated_time",
            aware_utc(
                "last_updated_time",
                self.last_updated_time,
            ),
        )

        if not self.touches_detail:

            raise DomainValidationError(
                "Une zone doit contenir "
                "des contacts."
            )

        if (
            len(self.touches_detail)
            != self.zone.touches
        ):

            raise DomainValidationError(
                "Le nombre de touches "
                "est incohérent."
            )

        expected_type = (
            PivotType.LOW
            if (
                self.zone.zone_type
                == ZoneType.SUPPORT
            )
            else PivotType.HIGH
        )

        for touch in self.touches_detail:

            if (
                touch.pivot_type
                != expected_type
            ):

                raise DomainValidationError(
                    "Type de pivot incompatible "
                    "avec la zone."
                )

        if not isinstance(
            self.score,
            ZoneScoreBreakdown,
        ):

            raise DomainValidationError(
                "score invalide."
            )

        if (
            abs(
                self.zone.quality
                - self.score.total
            )
            > 1e-9
        ):

            raise DomainValidationError(
                "zone.quality et score.total "
                "doivent être identiques."
            )

    @property
    def center_price(self) -> float:

        return self.zone.midpoint

    @property
    def lower_price(self) -> float:

        return self.zone.lower_price

    @property
    def upper_price(self) -> float:

        return self.zone.upper_price

    @property
    def zone_id(self) -> str:
        """
        Identifiant déterministe.

        Une zone construite avec exactement
        les mêmes pivots garde le même ID.
        """

        pivot_indexes = ",".join(
            str(index)
            for index
            in sorted(
                self.zone.pivot_indexes
            )
        )

        raw = (
            f"{self.zone.symbol}|"
            f"{self.zone.timeframe.value}|"
            f"{self.zone.zone_type.value}|"
            f"{pivot_indexes}|"
            f"{self.detector_name}|"
            f"{self.detector_version}"
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()