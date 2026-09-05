# forex_bot/patterns/harmonic/types.py

from __future__ import annotations

from dataclasses import dataclass

from forex_bot.core.enums import (
    PatternType,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.validators import (
    ensure_enum,
    positive_float,
)


@dataclass(
    frozen=True,
    slots=True,
)
class RatioBand:
    """
    Intervalle autorisé pour un ratio harmonique.

    Exemple :

        minimum = 0.55
        maximum = 0.70
        ideal   = 0.618

    Cela signifie que le ratio est accepté
    entre 0.55 et 0.70, mais 0.618 produit
    le meilleur score.
    """

    minimum: float
    maximum: float
    ideal: float | None = None

    def __post_init__(self) -> None:

        positive_float(
            "minimum",
            self.minimum,
        )

        positive_float(
            "maximum",
            self.maximum,
        )

        if (
            self.maximum
            < self.minimum
        ):

            raise DomainValidationError(
                "maximum doit être >= minimum."
            )

        if self.ideal is not None:

            positive_float(
                "ideal",
                self.ideal,
            )

            if not (
                self.minimum
                <= self.ideal
                <= self.maximum
            ):

                raise DomainValidationError(
                    "ideal doit être compris "
                    "dans l'intervalle."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class XABCDProfile:
    """
    Profil utilisé par :

    Gartley
    Bat
    Butterfly
    Crab
    Deep Crab
    """

    bullish_type: PatternType
    bearish_type: PatternType

    b_xa: RatioBand
    bc_ab: RatioBand
    cd_bc: RatioBand
    ad_xa: RatioBand

    def __post_init__(self) -> None:

        ensure_enum(
            "bullish_type",
            self.bullish_type,
            PatternType,
        )

        ensure_enum(
            "bearish_type",
            self.bearish_type,
            PatternType,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CypherProfile:

    bullish_type: PatternType
    bearish_type: PatternType

    b_xa: RatioBand
    c_xa: RatioBand
    d_xc: RatioBand


@dataclass(
    frozen=True,
    slots=True,
)
class SharkProfile:

    bullish_type: PatternType
    bearish_type: PatternType

    ab_ox: RatioBand
    bc_xa: RatioBand
    c_ox: RatioBand


@dataclass(
    frozen=True,
    slots=True,
)
class ABCDProfile:

    bullish_type: PatternType
    bearish_type: PatternType

    bc_ab: RatioBand

    # CD devrait être approximativement
    # similaire à AB.
    cd_ab: RatioBand

    # Extension CD par rapport à BC.
    cd_bc: RatioBand


@dataclass(
    frozen=True,
    slots=True,
)
class ThreeDrivesProfile:

    bullish_type: PatternType
    bearish_type: PatternType

    drive_ratio: RatioBand

    correction_ratio: RatioBand