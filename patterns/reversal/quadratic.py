# forex_bot/patterns/reversal/quadratic.py

from __future__ import annotations

from dataclasses import dataclass

import math

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.validators import (
    finite_float,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class QuadraticFit:
    """
    y = ax² + bx + c
    """

    a: float
    b: float
    c: float

    r_squared: float

    vertex_x: float
    vertex_y: float

    def __post_init__(self) -> None:

        for name in (
            "a",
            "b",
            "c",
            "vertex_x",
            "vertex_y",
        ):

            finite_float(
                name,
                getattr(
                    self,
                    name,
                ),
            )

        ratio_0_1(
            "r_squared",
            self.r_squared,
        )

    def value_at(
        self,
        x: float,
    ) -> float:

        return (

            self.a * x * x

            +

            self.b * x

            +

            self.c
        )


def _solve_3x3(
    matrix,
    vector,
):
    """
    Résolution par élimination de Gauss.

    Cela nous évite de dépendre de NumPy
    uniquement pour trois équations.
    """

    augmented = [

        [
            float(value)
            for value
            in row
        ]

        +

        [
            float(vector[index])
        ]

        for index, row
        in enumerate(matrix)
    ]

    size = 3

    for column in range(size):

        pivot_row = max(

            range(
                column,
                size,
            ),

            key=lambda row:
            abs(
                augmented[row][column]
            ),
        )

        if (
            abs(
                augmented[
                    pivot_row
                ][column]
            )
            < 1e-18
        ):

            raise DomainValidationError(
                "Régression quadratique "
                "impossible : matrice singulière."
            )

        augmented[
            column
        ], augmented[
            pivot_row
        ] = (

            augmented[
                pivot_row
            ],

            augmented[
                column
            ],
        )

        pivot_value = (
            augmented[
                column
            ][column]
        )

        for cell in range(
            column,
            size + 1,
        ):

            augmented[
                column
            ][cell] /= (
                pivot_value
            )

        for row in range(size):

            if row == column:

                continue

            factor = (
                augmented[
                    row
                ][column]
            )

            for cell in range(
                column,
                size + 1,
            ):

                augmented[
                    row
                ][cell] -= (

                    factor
                    * augmented[
                        column
                    ][cell]
                )

    return tuple(

        augmented[index][-1]

        for index
        in range(size)
    )


def fit_quadratic(
    values: tuple[
        float,
        ...
    ],
) -> QuadraticFit:
    """
    Ajuste les valeurs à :

        y = ax² + bx + c

    x vaut simplement :
        0, 1, 2, ..., n-1.
    """

    if len(values) < 3:

        raise DomainValidationError(
            "Une régression quadratique exige "
            "au moins trois points."
        )

    n = len(values)

    xs = tuple(
        float(index)
        for index
        in range(n)
    )

    sum_x = sum(xs)

    sum_x2 = sum(
        x ** 2
        for x in xs
    )

    sum_x3 = sum(
        x ** 3
        for x in xs
    )

    sum_x4 = sum(
        x ** 4
        for x in xs
    )

    sum_y = sum(
        values
    )

    sum_xy = sum(

        x * y

        for x, y
        in zip(
            xs,
            values,
            strict=True,
        )
    )

    sum_x2y = sum(

        x * x * y

        for x, y
        in zip(
            xs,
            values,
            strict=True,
        )
    )

    # Équations normales :
    #
    # [Σx4 Σx3 Σx2] [a]   [Σx2y]
    # [Σx3 Σx2 Σx ] [b] = [Σxy ]
    # [Σx2 Σx  n   ] [c]   [Σy  ]

    a, b, c = _solve_3x3(

        (
            (
                sum_x4,
                sum_x3,
                sum_x2,
            ),
            (
                sum_x3,
                sum_x2,
                sum_x,
            ),
            (
                sum_x2,
                sum_x,
                float(n),
            ),
        ),

        (
            sum_x2y,
            sum_xy,
            sum_y,
        ),
    )

    predictions = tuple(

        a * x * x
        + b * x
        + c

        for x
        in xs
    )

    mean_y = (
        sum(values)
        / n
    )

    residual_sum = sum(

        (
            actual
            - predicted
        ) ** 2

        for actual, predicted
        in zip(
            values,
            predictions,
            strict=True,
        )
    )

    total_sum = sum(

        (
            actual
            - mean_y
        ) ** 2

        for actual
        in values
    )

    if math.isclose(
        total_sum,
        0.0,
        abs_tol=1e-18,
    ):

        r_squared = 1.0

    else:

        r_squared = (

            1.0

            -

            residual_sum
            / total_sum
        )

    r_squared = min(
        1.0,
        max(
            0.0,
            r_squared,
        ),
    )

    if (
        abs(a)
        < 1e-18
    ):

        vertex_x = (
            float(n - 1) / 2
        )

    else:

        vertex_x = (
            -b
            / (2 * a)
        )

    vertex_y = (

        a
        * vertex_x
        * vertex_x

        +

        b
        * vertex_x

        +

        c
    )

    return QuadraticFit(

        a=a,
        b=b,
        c=c,

        r_squared=(
            r_squared
        ),

        vertex_x=(
            vertex_x
        ),

        vertex_y=(
            vertex_y
        ),
    )