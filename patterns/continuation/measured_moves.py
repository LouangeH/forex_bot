# forex_bot/patterns/continuation/measured_moves.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
    PivotType,
)

from forex_bot.core.models import (
    PatternMatch,
)

from forex_bot.patterns.base import (
    PatternDetector,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .config import (
    ContinuationPatternConfig,
)

from .scoring import (
    clamp_0_1,
    closeness_score,
)

from .types import (
    MeasuredMoveGeometry,
)


class MeasuredMoveDetector(
    PatternDetector
):
    """
    Détecte :

    - Measured Move Up ;
    - Measured Move Down.

    Structure A-B-C-D.
    """

    name = (
        "measured_move_detector"
    )

    version = "1.0.0"

    def __init__(
        self,
        config:
        ContinuationPatternConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or ContinuationPatternConfig()
        )

    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        pivots = [

            item

            for item
            in context.pivots

            if (
                item.confirmation_index
                <= context.as_of_index
            )
        ]

        pivots.sort(
            key=lambda item:
            item.pivot.candle_index
        )

        if len(pivots) < 4:

            return ()

        candidates: list[
            PatternMatch
        ] = []

        for start in range(
            0,
            len(pivots) - 3,
        ):

            a, b, c, d = (
                pivots[
                    start
                    :
                    start + 4
                ]
            )

            types = (

                a.pivot.pivot_type,

                b.pivot.pivot_type,

                c.pivot.pivot_type,

                d.pivot.pivot_type,
            )

            # =====================================
            # MEASURED MOVE UP
            # =====================================

            if types == (

                PivotType.LOW,

                PivotType.HIGH,

                PivotType.LOW,

                PivotType.HIGH,
            ):

                match = (
                    self._build_bullish(

                        context=context,

                        a=a,
                        b=b,
                        c=c,
                        d=d,
                    )
                )

            # =====================================
            # MEASURED MOVE DOWN
            # =====================================

            elif types == (

                PivotType.HIGH,

                PivotType.LOW,

                PivotType.HIGH,

                PivotType.LOW,
            ):

                match = (
                    self._build_bearish(

                        context=context,

                        a=a,
                        b=b,
                        c=c,
                        d=d,
                    )
                )

            else:

                match = None

            if match is not None:

                candidates.append(
                    match
                )

        return tuple(

            sorted(

                candidates,

                key=lambda item: (

                    item.end_index,

                    item.confidence,
                ),
            )
        )

    def _build_bullish(
        self,
        *,
        context,

        a,
        b,
        c,
        d,
    ) -> PatternMatch | None:

        first_leg = (

            b.pivot.price
            - a.pivot.price
        )

        correction = (

            b.pivot.price
            - c.pivot.price
        )

        second_leg = (

            d.pivot.price
            - c.pivot.price
        )

        if (

            first_leg <= 0

            or

            correction <= 0

            or

            second_leg <= 0
        ):

            return None

        return self._build(

            context=context,

            a=a,
            b=b,
            c=c,
            d=d,

            first_leg=first_leg,

            correction=correction,

            second_leg=second_leg,

            pattern_type=(
                PatternType
                .MEASURED_MOVE_UP
            ),

            bias=(
                MarketBias.BULLISH
            ),
        )

    def _build_bearish(
        self,
        *,
        context,

        a,
        b,
        c,
        d,
    ) -> PatternMatch | None:

        first_leg = (

            a.pivot.price
            - b.pivot.price
        )

        correction = (

            c.pivot.price
            - b.pivot.price
        )

        second_leg = (

            c.pivot.price
            - d.pivot.price
        )

        if (

            first_leg <= 0

            or

            correction <= 0

            or

            second_leg <= 0
        ):

            return None

        return self._build(

            context=context,

            a=a,
            b=b,
            c=c,
            d=d,

            first_leg=first_leg,

            correction=correction,

            second_leg=second_leg,

            pattern_type=(
                PatternType
                .MEASURED_MOVE_DOWN
            ),

            bias=(
                MarketBias.BEARISH
            ),
        )

    def _build(
        self,
        *,
        context,

        a,
        b,
        c,
        d,

        first_leg: float,

        correction: float,

        second_leg: float,

        pattern_type: PatternType,

        bias: MarketBias,
    ) -> PatternMatch | None:

        leg_ratio = (

            second_leg
            / first_leg
        )

        correction_ratio = (

            correction
            / first_leg
        )

        if not (

            self._config
            .measured_move_leg_ratio_min

            <= leg_ratio

            <=

            self._config
            .measured_move_leg_ratio_max
        ):

            return None

        if not (

            self._config
            .measured_move_correction_min

            <= correction_ratio

            <=

            self._config
            .measured_move_correction_max
        ):

            return None

        # -----------------------------------------
        # SCORE DE SIMILARITÉ DES DEUX JAMBES
        # -----------------------------------------

        leg_tolerance = max(

            1.0

            -

            self._config
            .measured_move_leg_ratio_min,

            self._config
            .measured_move_leg_ratio_max

            -

            1.0,

            1e-12,
        )

        leg_score = (
            closeness_score(

                leg_ratio,

                1.0,

                leg_tolerance,
            )
        )

        correction_midpoint = (

            self._config
            .measured_move_correction_min

            +

            self._config
            .measured_move_correction_max

        ) / 2

        correction_tolerance = (

            self._config
            .measured_move_correction_max

            -

            self._config
            .measured_move_correction_min

        ) / 2

        correction_score = (
            closeness_score(

                correction_ratio,

                correction_midpoint,

                max(
                    correction_tolerance,
                    1e-12,
                ),
            )
        )

        score = (
            clamp_0_1(

                0.70
                * leg_score

                +

                0.30
                * correction_score
            )
        )

        if (
            score
            < self._config.min_confidence
        ):

            return None

        geometry = (
            MeasuredMoveGeometry(

                a_index=(
                    a.pivot.candle_index
                ),

                b_index=(
                    b.pivot.candle_index
                ),

                c_index=(
                    c.pivot.candle_index
                ),

                d_index=(
                    d.pivot.candle_index
                ),

                first_leg=(
                    first_leg
                ),

                correction=(
                    correction
                ),

                second_leg=(
                    second_leg
                ),

                leg_ratio=(
                    leg_ratio
                ),

                correction_ratio=(
                    correction_ratio
                ),

                score=score,
            )
        )

        return PatternMatch(

            symbol=(
                context.symbol
            ),

            timeframe=(
                context.timeframe
            ),

            pattern_type=(
                pattern_type
            ),

            family=(
                PatternFamily.CLASSICAL
            ),

            role=(
                PatternRole.CONTINUATION
            ),

            status=(
                PatternStatus.CONFIRMED
            ),

            bias=bias,

            start_time=(
                a.pivot.time
            ),

            end_time=(
                d.pivot.time
            ),

            start_index=(
                a.pivot.candle_index
            ),

            end_index=(
                d.pivot.candle_index
            ),

            confidence=score,

            detector_name=(
                self.name
            ),

            detector_version=(
                self.version
            ),

            upper_boundary=None,

            lower_boundary=None,

            breakout_level=None,

            metrics=(
                geometry.metrics()
            ),

            source_pivot_indexes=(

                a.pivot.candle_index,

                b.pivot.candle_index,

                c.pivot.candle_index,

                d.pivot.candle_index,
            ),
        )