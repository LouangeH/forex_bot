from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import math
from typing import TypeVar

from .exceptions import DomainValidationError


EnumType = TypeVar(
    "EnumType",
    bound=Enum,
)


def non_empty_text(
    name: str,
    value: str,
) -> str:
    """
    Refuse les textes vides.
    """

    if not isinstance(value, str):
        raise DomainValidationError(
            f"{name} doit être un texte."
        )

    cleaned = value.strip()

    if not cleaned:
        raise DomainValidationError(
            f"{name} ne peut pas être vide."
        )

    return cleaned


def finite_float(
    name: str,
    value: float,
) -> float:
    """
    Refuse :
    - NaN ;
    - +inf ;
    - -inf.

    Ces valeurs peuvent rendre les calculs techniques
    extrêmement dangereux.
    """

    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DomainValidationError(
            f"{name} doit être numérique."
        ) from exc

    if not math.isfinite(number):
        raise DomainValidationError(
            f"{name} doit être fini."
        )

    return number


def positive_float(
    name: str,
    value: float,
) -> float:

    number = finite_float(
        name,
        value,
    )

    if number <= 0:
        raise DomainValidationError(
            f"{name} doit être > 0."
        )

    return number


def non_negative_float(
    name: str,
    value: float,
) -> float:

    number = finite_float(
        name,
        value,
    )

    if number < 0:
        raise DomainValidationError(
            f"{name} doit être >= 0."
        )

    return number


def non_negative_int(
    name: str,
    value: int,
) -> int:
    """
    bool est volontairement refusé car en Python :
    isinstance(True, int) == True.
    """

    if isinstance(value, bool):
        raise DomainValidationError(
            f"{name} doit être un entier."
        )

    if not isinstance(value, int):
        raise DomainValidationError(
            f"{name} doit être un entier."
        )

    if value < 0:
        raise DomainValidationError(
            f"{name} doit être >= 0."
        )

    return value


def positive_int(
    name: str,
    value: int,
) -> int:

    result = non_negative_int(
        name,
        value,
    )

    if result == 0:
        raise DomainValidationError(
            f"{name} doit être > 0."
        )

    return result


def ratio_0_1(
    name: str,
    value: float,
) -> float:
    """
    Vérifie un ratio compris entre 0 et 1.

    Exemple :
    confidence = 0.82
    """

    number = finite_float(
        name,
        value,
    )

    if not 0.0 <= number <= 1.0:
        raise DomainValidationError(
            f"{name} doit être compris entre 0 et 1."
        )

    return number


def aware_utc(
    name: str,
    value: datetime,
) -> datetime:
    """
    Toutes les heures internes du bot seront stockées
    en UTC.

    Cela évite les confusions entre :
    - heure Equiti ;
    - heure UAE ;
    - heure de Paris ;
    - heure du VPS.
    """

    if not isinstance(value, datetime):
        raise DomainValidationError(
            f"{name} doit être un datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise DomainValidationError(
            f"{name} doit avoir un fuseau horaire."
        )

    return value.astimezone(
        timezone.utc
    )


def decimal_number(
    name: str,
    value,
) -> Decimal:
    """
    Les montants financiers utilisent Decimal.

    Les prix de marché utiliseront float pour les
    calculs géométriques et statistiques.

    Mais :
    - balance ;
    - equity ;
    - risque en argent ;
    - commissions ;

    seront manipulés avec Decimal.
    """

    try:

        if isinstance(value, Decimal):
            result = value

        else:
            result = Decimal(
                str(value)
            )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:

        raise DomainValidationError(
            f"{name} n'est pas un Decimal valide."
        ) from exc

    if not result.is_finite():
        raise DomainValidationError(
            f"{name} doit être fini."
        )

    return result


def ratio_decimal_0_1(
    name: str,
    value,
    *,
    allow_zero: bool = True,
) -> Decimal:

    result = decimal_number(
        name,
        value,
    )

    if allow_zero:
        valid_lower = result >= 0

    else:
        valid_lower = result > 0

    if (
        not valid_lower
        or result > 1
    ):
        raise DomainValidationError(
            f"{name} doit être compris entre 0 et 1."
        )

    return result


def ensure_enum(
    name: str,
    value,
    enum_class: type[EnumType],
) -> EnumType:
    """
    Empêche par exemple :

        direction="BUY"

    à la place de :

        TradeDirection.BUY

    Cela évite beaucoup de bugs silencieux.
    """

    if not isinstance(
        value,
        enum_class,
    ):
        raise DomainValidationError(
            f"{name} doit être un "
            f"{enum_class.__name__}."
        )

    return value


def normalized_casefold(
    value: str,
) -> str:
    """
    Normalisation utilisée pour comparer
    proprement les noms de broker/serveur.
    """

    return " ".join(
        value
        .strip()
        .casefold()
        .split()
    )