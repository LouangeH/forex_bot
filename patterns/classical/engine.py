# forex_bot/patterns/engine.py

from __future__ import annotations

from collections.abc import Sequence

from forex_bot.core.models import (
    PatternMatch,
)

from .base import (
    PatternDetector,
)

from .context import (
    PatternContext,
)


class PatternEngine:
    """
    Moteur central des figures.

    Il ne sait pas ce qu'est :
    - un triangle ;
    - un flag ;
    - un Gartley ;
    - un Head & Shoulders.

    Il sait uniquement exécuter
    des PatternDetector.
    """

    def __init__(
        self,
        detectors: Sequence[
            PatternDetector
        ],
    ) -> None:

        self._detectors = tuple(
            detectors
        )

    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        found: list[
            PatternMatch
        ] = []

        for detector in (
            self._detectors
        ):

            found.extend(
                detector.detect(
                    context
                )
            )

        # ========================================
        # ANTI-DOUBLON
        # ========================================

        unique: dict[
            str,
            PatternMatch,
        ] = {}

        for pattern in found:

            existing = unique.get(
                pattern.pattern_id
            )

            if (

                existing is None

                or

                pattern.confidence
                > existing.confidence
            ):

                unique[
                    pattern.pattern_id
                ] = pattern

        return tuple(

            sorted(

                unique.values(),

                key=lambda pattern: (

                    pattern.end_index,

                    -pattern.confidence,

                    pattern.pattern_name,
                ),
            )
        )
        
from forex_bot.patterns.engine import (
    PatternEngine,
)

from forex_bot.patterns.classical import (
    ChannelDetector,
    HorizontalRangeDetector,
    TriangleDetector,
    WedgeDetector,
)

from forex_bot.patterns.continuation import (
    ContinuationRectangleDetector,
    FlagDetector,
    MeasuredMoveDetector,
    PennantDetector,
)

from forex_bot.patterns.reversal import (
    BroadeningDetector,
    DiamondDetector,
    DoubleTripleDetector,
    HeadShouldersDetector,
    OneTwoThreeDetector,
    QuasimodoDetector,
    RoundingDetector,
    VPatternDetector,
)


engine = PatternEngine(

    detectors=[

        # ==========================================
        # CLASSICAL GEOMETRY
        # ==========================================

        TriangleDetector(),

        WedgeDetector(),

        ChannelDetector(),

        HorizontalRangeDetector(),

        # ==========================================
        # CONTINUATION
        # ==========================================

        FlagDetector(),

        PennantDetector(),

        ContinuationRectangleDetector(),

        MeasuredMoveDetector(),

        # ==========================================
        # REVERSAL
        # ==========================================

        DoubleTripleDetector(),

        HeadShouldersDetector(),

        VPatternDetector(),

        OneTwoThreeDetector(),

        QuasimodoDetector(),

        RoundingDetector(),

        BroadeningDetector(),

        DiamondDetector(),
    ]
    
    from forex_bot.patterns.harmonic import (
    ABCDDetector,
    CypherDetector,
    SharkDetector,
    ThreeDrivesDetector,
    XABCDDetector,
)


harmonic_detectors = [

    XABCDDetector(),

    ABCDDetector(),

    CypherDetector(),

    SharkDetector(),

    ThreeDrivesDetector(),
]
)