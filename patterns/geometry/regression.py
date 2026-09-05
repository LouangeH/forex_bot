# forex_bot/patterns/geometry/regression.py

from __future__ import annotations

from collections.abc import Sequence

from statistics import fmean

import math

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    LinearBoundary,
)


def fit_linear_boundary(
    points: Sequence[
        tuple[int, float]
    ],
) -> LinearBoundary:
    """
    Calcule une régression linéaire :

        y = a*x + b

    x :
        index de la bougie.

    y :
        prix du pivot.

    Retourne :
        slope
        intercept
        R²
        nombre de contacts.
    """

    if len(points) < 2:

        raise DomainValidationError(
            "Une droite nécessite "
            "au moins deux points."
        )

    xs = [
        float(x)
        for x, _
        in points
    ]

    ys = [
        float(y)
        for _, y
        in points
    ]

    mean_x = fmean(xs)

    mean_y = fmean(ys)

    denominator = sum(
        (
            x - mean_x
        ) ** 2

        for x
        in xs
    )

    if denominator <= 0:

        raise DomainValidationError(
            "Les points doivent avoir "
            "des indices différents."
        )

    slope = (

        sum(

            (
                x - mean_x
            )

            * (
                y - mean_y
            )

            for x, y
            in zip(
                xs,
                ys,
                strict=True,
            )
        )

        / denominator
    )

    intercept = (
        mean_y
        - slope * mean_x
    )

    predicted = [

        slope * x
        + intercept

        for x
        in xs
    ]

    residual_sum = sum(

        (
            real - expected
        ) ** 2

        for real, expected
        in zip(
            ys,
            predicted,
            strict=True,
        )
    )

    total_sum = sum(

        (
            value - mean_y
        ) ** 2

        for value
        in ys
    )

    if math.isclose(
        total_sum,
        0.0,
        abs_tol=1e-18,
    ):

        r_squared = (
            1.0

            if math.isclose(
                residual_sum,
                0.0,
                abs_tol=1e-18,
            )

            else 0.0
        )

    else:

        r_squared = (
            1.0
            - residual_sum
            / total_sum
        )

    # Protection contre de petites erreurs
    # numériques des float.
    r_squared = min(
        1.0,
        max(
            0.0,
            r_squared,
        ),
    )

    return LinearBoundary(

        slope=slope,

        intercept=intercept,

        r_squared=r_squared,

        touches=len(points),
    )


def mean_absolute_error(
    boundary: LinearBoundary,

    points: Sequence[
        tuple[int, float]
    ],
) -> float:
    """
    Distance moyenne entre les vrais pivots
    et la droite théorique.

    Plus cette valeur est faible,
    meilleure est la frontière.
    """

    if not points:

        raise DomainValidationError(
            "points ne peut pas être vide."
        )

    return fmean(

        abs(
            price
            - boundary.value_at(index)
        )

        for index, price
        in points
    )