# forex_bot/patterns/geometry/scoring.py

from forex_bot.patterns.geometry.structure import (
    LineStructure,
)


def clamp_0_1(
    value: float,
) -> float:

    return min(
        1.0,
        max(
            0.0,
            value,
        ),
    )


def line_pattern_confidence(
    structure: LineStructure,
    *,
    geometry_score: float,
) -> float:
    """
    Score final :

    40 % :
        qualité des lignes.

    25 % :
        géométrie propre à la figure.

    20 % :
        nombre de contacts.

    15 % :
        précision des contacts.
    """

    fit = (
        structure.fit_score
    )

    touches = clamp_0_1(

        (
            structure.upper.touches
            + structure.lower.touches
        )

        / 8.0
    )

    mean_error_atr = (

        structure.upper_error_atr
        + structure.lower_error_atr

    ) / 2

    precision = clamp_0_1(

        1.0
        - mean_error_atr
    )

    return clamp_0_1(

        0.40
        * fit

        +

        0.25
        * clamp_0_1(
            geometry_score
        )

        +

        0.20
        * touches

        +

        0.15
        * precision
    )