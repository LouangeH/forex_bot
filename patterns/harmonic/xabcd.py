# forex_bot/patterns/harmonic/xabcd.py

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
    DEFAULT_XABCD_PROFILES,
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

from .types import (
    XABCDProfile,
)


class XABCDDetector(
    PatternDetector
):
    """
    Moteur générique pour :

    Gartley
    Bat
    Butterfly
    Crab
    Deep Crab
    """

    name = "xabcd_detector"

    version = "1.0.0"

    def __init__(
        self,
        config:
        HarmonicConfig
        | None = None,

        profiles:
        tuple[XABCDProfile, ...]
        = DEFAULT_XABCD_PROFILES,
    ) -> None:

        self._config = (
            config
            or HarmonicConfig()
        )

        self._profiles = profiles

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

        windows = (
            alternating_windows(
                pivots,
                5,
            )
        )

        found = []

        for sequence in windows:

            if not valid_pattern_duration(

                pivots=sequence,

                context=context,

                config=self._config,
            ):

                continue

            matches = (
                self._evaluate_sequence(
                    context,
                    sequence,
                )
            )

            found.extend(
                matches
            )

        return tuple(
            found
        )

    def _evaluate_sequence(
        self,
        context,
        sequence,
    ):

        x, a, b, c, d = (
            sequence
        )

        types = tuple(

            pivot.pivot.pivot_type

            for pivot
            in sequence
        )

        bullish_structure = (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        )

        bearish_structure = (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        )

        if types not in (
            bullish_structure,
            bearish_structure,
        ):

            return ()

        prices = (

            x.pivot.price,
            a.pivot.price,
            b.pivot.price,
            c.pivot.price,
            d.pivot.price,
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

            return ()

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

        cd = abs(
            d.pivot.price
            - c.pivot.price
        )

        ad = abs(
            a.pivot.price
            - d.pivot.price
        )

        b_xa = safe_ratio(
            ab,
            xa,
        )

        bc_ab = safe_ratio(
            bc,
            ab,
        )

        cd_bc = safe_ratio(
            cd,
            bc,
        )

        ad_xa = safe_ratio(
            ad,
            xa,
        )

        if None in (
            b_xa,
            bc_ab,
            cd_bc,
            ad_xa,
        ):

            return ()

        pivot_score = (
            prominence_score(
                sequence
            )
        )

        bias = harmonic_bias(
            sequence
        )

        found = []

        for profile in (
            self._profiles
        ):

            scores = (

                ratio_band_score(
                    b_xa,
                    profile.b_xa,
                ),

                ratio_band_score(
                    bc_ab,
                    profile.bc_ab,
                ),

                ratio_band_score(
                    cd_bc,
                    profile.cd_bc,
                ),

                ratio_band_score(
                    ad_xa,
                    profile.ad_xa,
                ),
            )

            ratio_score = (
                combined_ratio_score(
                    scores
                )
            )

            if ratio_score <= 0:

                continue

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

                continue

            pattern_type = (

                profile.bullish_type

                if (
                    bias
                    == MarketBias.BULLISH
                )

                else

                profile.bearish_type
            )

            found.append(

                build_harmonic_match(

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
                            "b_xa",
                            b_xa,
                        ),

                        PatternMetric(
                            "bc_ab",
                            bc_ab,
                        ),

                        PatternMetric(
                            "cd_bc",
                            cd_bc,
                        ),

                        PatternMetric(
                            "ad_xa",
                            ad_xa,
                        ),

                        PatternMetric(
                            "harmonic_ratio_score",
                            ratio_score,
                        ),

                        PatternMetric(
                            "harmonic_pivot_score",
                            pivot_score,
                        ),
                    ),
                )
            )

        return tuple(
            found
        )