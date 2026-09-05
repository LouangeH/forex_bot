# forex_bot/patterns/harmonic/cypher.py

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
    CYPHER,
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


class CypherDetector(
    PatternDetector
):

    name = "cypher_detector"

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
                5,
            )
        ):

            if not valid_pattern_duration(

                pivots=sequence,

                context=context,

                config=self._config,
            ):

                continue

            match = self._evaluate(
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

    def _evaluate(
        self,
        context,
        sequence,
    ):

        x, a, b, c, d = (
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

        xa = abs(
            a.pivot.price
            - x.pivot.price
        )

        ab = abs(
            b.pivot.price
            - a.pivot.price
        )

        xc = abs(
            c.pivot.price
            - x.pivot.price
        )

        cd = abs(
            d.pivot.price
            - c.pivot.price
        )

        b_xa = safe_ratio(
            ab,
            xa,
        )

        c_xa = safe_ratio(
            xc,
            xa,
        )

        d_xc = safe_ratio(
            cd,
            xc,
        )

        if None in (
            b_xa,
            c_xa,
            d_xc,
        ):

            return None

        ratio_score = (
            combined_ratio_score(
                (
                    ratio_band_score(
                        b_xa,
                        CYPHER.b_xa,
                    ),

                    ratio_band_score(
                        c_xa,
                        CYPHER.c_xa,
                    ),

                    ratio_band_score(
                        d_xc,
                        CYPHER.d_xc,
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

            CYPHER.bullish_type

            if bias
            == MarketBias.BULLISH

            else

            CYPHER.bearish_type
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
                    "cypher_b_xa",
                    b_xa,
                ),

                PatternMetric(
                    "cypher_c_xa",
                    c_xa,
                ),

                PatternMetric(
                    "cypher_d_xc",
                    d_xc,
                ),
            ),
        )