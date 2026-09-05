# forex_bot/patterns/harmonic/shark.py

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
    build_harmonic_match,
    final_harmonic_confidence,
    harmonic_bias,
    prominence_score,
)

from .config import (
    HarmonicConfig,
)

from .profiles import (
    SHARK,
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


class SharkDetector(
    PatternDetector
):

    name = "shark_detector"

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

        o, x, a, b, c = (
            sequence
        )

        ox = abs(
            x.pivot.price
            - o.pivot.price
        )

        xa = abs(
            a.pivot.price
            - x.pivot.price
        )

        ab = abs(
            b.pivot.price
            - a.pivot.price
        )

        bc = abs(
            c.pivot.price
            - b.pivot.price
        )

        oc = abs(
            c.pivot.price
            - o.pivot.price
        )

        ab_ox = safe_ratio(
            ab,
            ox,
        )

        bc_xa = safe_ratio(
            bc,
            xa,
        )

        c_ox = safe_ratio(
            oc,
            ox,
        )

        if None in (
            ab_ox,
            bc_xa,
            c_ox,
        ):

            return None

        ratio_score = (
            combined_ratio_score(
                (
                    ratio_band_score(
                        ab_ox,
                        SHARK.ab_ox,
                    ),

                    ratio_band_score(
                        bc_xa,
                        SHARK.bc_xa,
                    ),

                    ratio_band_score(
                        c_ox,
                        SHARK.c_ox,
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

            SHARK.bullish_type

            if bias
            == MarketBias.BULLISH

            else

            SHARK.bearish_type
        )

        return build_harmonic_match(

            context=context,

            pivots=sequence,

            pattern_type=pattern_type,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            metrics=(

                PatternMetric(
                    "shark_ab_ox",
                    ab_ox,
                ),

                PatternMetric(
                    "shark_bc_xa",
                    bc_xa,
                ),

                PatternMetric(
                    "shark_c_ox",
                    c_ox,
                ),
            ),
        )