# forex_bot/patterns/harmonic/three_drives.py

from __future__ import annotations

from forex_bot.core.enums import (
    MarketBias,
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
    build_harmonic_match,
    final_harmonic_confidence,
    prominence_score,
)

from .config import (
    HarmonicConfig,
)

from .profiles import (
    THREE_DRIVES,
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


class ThreeDrivesDetector(
    PatternDetector
):

    name = "three_drives_detector"

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
                6,
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

        p0, p1, p2, p3, p4, p5 = (
            sequence
        )

        types = tuple(

            item.pivot.pivot_type

            for item
            in sequence
        )

        three_drives_top = (

            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
        )

        three_drives_bottom = (

            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
            PivotType.HIGH,
            PivotType.LOW,
        )

        if types == three_drives_top:

            drive_1 = (
                p1.pivot.price
                - p0.pivot.price
            )

            correction_1 = (
                p1.pivot.price
                - p2.pivot.price
            )

            drive_2 = (
                p3.pivot.price
                - p2.pivot.price
            )

            correction_2 = (
                p3.pivot.price
                - p4.pivot.price
            )

            drive_3 = (
                p5.pivot.price
                - p4.pivot.price
            )

            pattern_type = (
                THREE_DRIVES
                .bearish_type
            )

        elif types == three_drives_bottom:

            drive_1 = (
                p0.pivot.price
                - p1.pivot.price
            )

            correction_1 = (
                p2.pivot.price
                - p1.pivot.price
            )

            drive_2 = (
                p2.pivot.price
                - p3.pivot.price
            )

            correction_2 = (
                p4.pivot.price
                - p3.pivot.price
            )

            drive_3 = (
                p4.pivot.price
                - p5.pivot.price
            )

            pattern_type = (
                THREE_DRIVES
                .bullish_type
            )

        else:

            return None

        if min(
            drive_1,
            drive_2,
            drive_3,
            correction_1,
            correction_2,
        ) <= 0:

            return None

        drive_2_1 = safe_ratio(
            drive_2,
            drive_1,
        )

        drive_3_2 = safe_ratio(
            drive_3,
            drive_2,
        )

        correction_1_ratio = (
            safe_ratio(
                correction_1,
                drive_1,
            )
        )

        correction_2_ratio = (
            safe_ratio(
                correction_2,
                drive_2,
            )
        )

        if None in (
            drive_2_1,
            drive_3_2,
            correction_1_ratio,
            correction_2_ratio,
        ):

            return None

        ratio_score = (
            combined_ratio_score(
                (
                    ratio_band_score(
                        drive_2_1,
                        THREE_DRIVES
                        .drive_ratio,
                    ),

                    ratio_band_score(
                        drive_3_2,
                        THREE_DRIVES
                        .drive_ratio,
                    ),

                    ratio_band_score(
                        correction_1_ratio,
                        THREE_DRIVES
                        .correction_ratio,
                    ),

                    ratio_band_score(
                        correction_2_ratio,
                        THREE_DRIVES
                        .correction_ratio,
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

        return build_harmonic_match(

            context=context,

            pivots=sequence,

            pattern_type=pattern_type,

            confidence=confidence,

            detector_name=self.name,

            detector_version=self.version,

            metrics=(

                PatternMetric(
                    "drive_2_drive_1",
                    drive_2_1,
                ),

                PatternMetric(
                    "drive_3_drive_2",
                    drive_3_2,
                ),

                PatternMetric(
                    "correction_1_ratio",
                    correction_1_ratio,
                ),

                PatternMetric(
                    "correction_2_ratio",
                    correction_2_ratio,
                ),
            ),
        )