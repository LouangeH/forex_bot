# forex_bot/patterns/harmonic/abcd.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
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
    all_legs_large_enough,
    build_harmonic_match,
    final_harmonic_confidence,
    harmonic_bias,
    median_pattern_atr,
    prominence_score,
)

from .config import (
    HarmonicConfig,
)

from .profiles import (
    ABCD,
)

from .ratios import (
    combined_ratio_score,
    ratio_band_score,
    safe_ratio,
)

from .scanner import (
    alternating_windows,
    recent_pivots,
    valid_pattern_duration,
)


class ABCDDetector(
    PatternDetector
):

    name = "abcd_detector"

    version = "1.0.0"

    def __init__(
        self,
        config:
        HarmonicConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or HarmonicConfig()
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

        for sequence in (
            alternating_windows(
                pivots,
                4,
            )
        ):

            if not valid_pattern_duration(

                pivots=sequence,

                context=context,

                config=self._config,
            ):

                continue

            match = (
                self._evaluate(
                    context,
                    sequence,
                )
            )

            if match is not None:

                found.append(
                    match
                )

        return tuple(
            found
        )

    def _evaluate(
        self,
        context,
        sequence,
    ):

        a, b, c, d = (
            sequence
        )

        prices = tuple(
            item.pivot.price
            for item
            in sequence
        )

        atr = median_pattern_atr(
            sequence
        )

        if (
            atr is None

            or not all_legs_large_enough(

                prices=prices,

                atr=atr,

                minimum_atr=(
                    self._config.min_leg_atr
                ),
            )
        ):

            return None

        ab = abs(
            b.pivot.price
            - a.pivot.price
        )

        bc = abs(
            c.pivot.price
            - b.pivot.price
        )

        cd = abs(
            d.pivot.price
            - c.pivot.price
        )

        bc_ab = safe_ratio(
            bc,
            ab,
        )

        cd_ab = safe_ratio(
            cd,
            ab,
        )

        cd_bc = safe_ratio(
            cd,
            bc,
        )

        if None in (
            bc_ab,
            cd_ab,
            cd_bc,
        ):

            return None

        ratio_score = (
            combined_ratio_score(
                (
                    ratio_band_score(
                        bc_ab,
                        ABCD.bc_ab,
                    ),

                    ratio_band_score(
                        cd_ab,
                        ABCD.cd_ab,
                    ),

                    ratio_band_score(
                        cd_bc,
                        ABCD.cd_bc,
                    ),
                )
            )
        )

        if ratio_score <= 0:

            return None

        pivot_score = (
            prominence_score(
                sequence
            )
        )

        confidence = (
            final_harmonic_confidence(

                ratio_score=(
                    ratio_score
                ),

                pivot_score=(
                    pivot_score
                ),

                config=(
                    self._config
                ),
            )
        )

        if (
            confidence
            < self._config.min_confidence
        ):

            return None

        bias = harmonic_bias(
            sequence
        )

        pattern_type = (

            ABCD.bullish_type

            if (
                bias
                == MarketBias.BULLISH
            )

            else

            ABCD.bearish_type
        )

        return build_harmonic_match(

            context=context,

            pivots=sequence,

            pattern_type=(
                pattern_type
            ),

            confidence=(
                confidence
            ),

            detector_name=(
                self.name
            ),

            detector_version=(
                self.version
            ),

            metrics=(

                PatternMetric(
                    "bc_ab",
                    bc_ab,
                ),

                PatternMetric(
                    "cd_ab",
                    cd_ab,
                ),

                PatternMetric(
                    "cd_bc",
                    cd_bc,
                ),

                PatternMetric(
                    "harmonic_ratio_score",
                    ratio_score,
                ),
            ),
        )