# forex_bot/patterns/continuation/scoring.py

from __future__ import annotations

from .config import (
    ContinuationPatternConfig,
)

from .types import (
    ConsolidationStructure,
    ImpulseLeg,
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


def continuation_confidence(
    *,
    impulse: ImpulseLeg,

    consolidation: ConsolidationStructure,

    geometry_score: float,

    config: ContinuationPatternConfig,
) -> float:
    """
    Score technique final.

    ATTENTION :

    confidence=0.85 signifie :
    la figure respecte fortement nos critères.

    Cela ne signifie PAS :
    85 % de chance de gagner.
    """

    line_fit = (
        consolidation.fit_score
    )

    retracement_score = (
        clamp_0_1(

            1.0
            - consolidation
            .retracement_ratio
        )
    )

    size_score = (
        clamp_0_1(

            1.0
            - consolidation
            .height_vs_impulse
        )
    )

    score = (

        0.30
        * impulse.score

        +

        0.25
        * line_fit

        +

        0.20
        * clamp_0_1(
            geometry_score
        )

        +

        0.15
        * retracement_score

        +

        0.10
        * size_score
    )

    return clamp_0_1(
        score
    )


def closeness_score(
    value: float,

    target: float,

    tolerance: float,
) -> float:
    """
    Retourne 1 lorsque value est exactement
    sur la cible.

    Le score diminue ensuite progressivement.
    """

    if tolerance <= 0:

        return (
            1.0
            if value == target
            else 0.0
        )

    return clamp_0_1(

        1.0

        -

        abs(
            value
            - target
        )

        / tolerance
    )