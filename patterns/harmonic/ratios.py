# forex_bot/patterns/harmonic/ratios.py

from __future__ import annotations

from statistics import fmean

from .types import (
    RatioBand,
)


def safe_ratio(
    numerator: float,
    denominator: float,
) -> float | None:
    """
    Division protégée.

    Un pattern avec une jambe pratiquement nulle
    doit être rejeté, pas provoquer une exception.
    """

    if (
        denominator <= 0
    ):

        return None

    return (
        numerator
        / denominator
    )


def ratio_band_score(
    value: float,
    band: RatioBand,
) -> float:
    """
    Score compris entre 0 et 1.

    Hors de l'intervalle :
        0.

    À la valeur idéale :
        1.

    Aux limites :
        environ 0.5.

    On ne donne volontairement pas zéro à une
    valeur située exactement à la limite puisque
    cette valeur reste techniquement autorisée.
    """

    if (
        value < band.minimum

        or

        value > band.maximum
    ):

        return 0.0

    target = (

        band.ideal

        if band.ideal is not None

        else (
            band.minimum
            + band.maximum
        ) / 2
    )

    if value == target:

        return 1.0

    if value < target:

        maximum_distance = max(

            target
            - band.minimum,

            1e-12,
        )

    else:

        maximum_distance = max(

            band.maximum
            - target,

            1e-12,
        )

    distance = abs(
        value
        - target
    )

    proximity = max(

        0.0,

        1.0
        - distance
        / maximum_distance,
    )

    return (

        0.50

        +

        0.50
        * proximity
    )


def combined_ratio_score(
    scores: tuple[
        float,
        ...
    ],
) -> float:
    """
    Si un seul ratio obligatoire est invalide,
    la figure entière est rejetée.
    """

    if not scores:

        return 0.0

    if any(
        score <= 0
        for score
        in scores
    ):

        return 0.0

    return fmean(
        scores
    )