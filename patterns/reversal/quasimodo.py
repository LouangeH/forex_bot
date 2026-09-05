# forex_bot/patterns/reversal/quasimodo.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
    PatternType,
    PivotType,
)

from forex_bot.core.models import (
    PatternMatch,
    PatternMetric,
)

from forex_bot.patterns.base import (
    PatternDetector,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .common import (
    build_reversal_match,
    clamp_0_1,
    level_closeness_score,
    median_atr,
    pattern_is_recent,
    recent_pivots,
)

from .config import (
    ReversalPatternConfig,
)


class QuasimodoDetector(
    PatternDetector
):
    """
    Détecte :

    Bearish QM:
        H L HH LL LH

    Bullish QM:
        L H LL HH HL
    """

    name = "quasimodo_detector"

    version = "1.0.0"

    def __init__(
        self,
        config:
        ReversalPatternConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or ReversalPatternConfig()
        )

    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        pivots = recent_pivots(
            context,
            self._config,
        )

        found = []

        for index in range(
            len(pivots) - 4
        ):

            sequence = pivots[
                index:
                index + 5
            ]

            match = self._detect_one(
                context,
                sequence,
            )

            if match:

                found.append(
                    match
                )

        return tuple(
            found
        )

    def _detect_one(
        self,
        context,
        sequence,
    ):

        p1, p2, p3, p4, p5 = (
            sequence
        )

        types = tuple(

            item.pivot.pivot_type

            for item
            in sequence
        )

        atr = median_atr(
            sequence
        )

        if (
            atr is None
            or atr <= 0
        ):

            return None

        if not pattern_is_recent(

            context=context,

            last_index=(
                p5.pivot.candle_index
            ),

            config=self._config,
        ):

            return None

        minimum_break = (

            self._config
            .quasimodo_structure_break_atr

            * atr
        )

        # ==========================================
        # BEARISH
        # ==========================================

        if types == (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        ):

            higher_high = (

                p3.pivot.price
                - p1.pivot.price
            )

            lower_low = (

                p2.pivot.price
                - p4.pivot.price
            )

            shoulder_score = (
                level_closeness_score(

                    prices=(
                        p1.pivot.price,
                        p5.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .quasimodo_shoulder_tolerance_atr
                    ),
                )
            )

            if (
                higher_high < minimum_break

                or

                lower_low < minimum_break

                or

                p5.pivot.price
                >= p3.pivot.price

                or

                shoulder_score <= 0
            ):

                return None

            pattern_type = (
                PatternType
                .QUASIMODO_BEARISH
            )

            bias = (
                MarketBias.BEARISH
            )

        # ==========================================
        # BULLISH
        # ==========================================

        elif types == (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        ):

            lower_low = (

                p1.pivot.price
                - p3.pivot.price
            )

            higher_high = (

                p4.pivot.price
                - p2.pivot.price
            )

            shoulder_score = (
                level_closeness_score(

                    prices=(
                        p1.pivot.price,
                        p5.pivot.price,
                    ),

                    atr=atr,

                    tolerance_atr=(
                        self._config
                        .quasimodo_shoulder_tolerance_atr
                    ),
                )
            )

            if (
                lower_low < minimum_break

                or

                higher_high < minimum_break

                or

                p5.pivot.price
                <= p3.pivot.price

                or

                shoulder_score <= 0
            ):

                return None

            pattern_type = (
                PatternType
                .QUASIMODO_BULLISH
            )

            bias = (
                MarketBias.BULLISH
            )

        else:

            return None

        structure_score = clamp_0_1(

            (
                higher_high
                + lower_low
            )

            /

            max(
                minimum_break * 4,
                1e-12,
            )
        )

        confidence = (

            0.55
            * structure_score

            +

            0.45
            * shoulder_score
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        # Pas de breakout_level unique ici.
        #
        # Quasimodo est une structure plus complexe :
        # les niveaux seront conservés dans metrics.
        return build_reversal_match(

            context=context,

            pattern_type=pattern_type,

            bias=bias,

            pivots=sequence,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            breakout_level=None,

            metrics=(

                PatternMetric(
                    "qm_higher_high_atr",
                    higher_high / atr,
                ),

                PatternMetric(
                    "qm_lower_low_atr",
                    lower_low / atr,
                ),

                PatternMetric(
                    "qm_shoulder_score",
                    shoulder_score,
                ),

                PatternMetric(
                    "qm_retest_level",
                    p5.pivot.price,
                ),

                PatternMetric(
                    "qm_structure_break_level",
                    p4.pivot.price,
                ),
            ),
        )