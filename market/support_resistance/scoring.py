# forex_bot/market/support_resistance/scoring.py

import math

from collections.abc import Sequence

from statistics import fmean

from .config import (
    SupportResistanceConfig,
)

from .types import (
    ZoneScoreBreakdown,
    ZoneTouch,
)


class ZoneScorer:
    """
    Calcule un score technique de 0 à 1.

    IMPORTANT :

    0.85 ne signifie PAS
    "85 % de chance de gagner".

    Cela signifie simplement que la zone respecte
    fortement nos critères techniques.
    """

    def __init__(
        self,
        config: SupportResistanceConfig,
    ) -> None:

        self._config = config

    def score(
        self,
        *,
        touches: Sequence[ZoneTouch],

        lower_price: float,

        upper_price: float,

        as_of_index: int,
    ) -> ZoneScoreBreakdown:

        # =========================================
        # 1. NOMBRE DE TOUCHES
        # =========================================

        touch_score = min(
            1.0,

            len(touches)
            / self._config.target_touches,
        )

        # =========================================
        # 2. IMPORTANCE DES PIVOTS
        # =========================================

        prominence_score = min(
            1.0,

            (
                fmean(
                    touch.prominence_atr
                    for touch
                    in touches
                )
                /
                self._config
                .target_prominence_atr
            ),
        )

        # =========================================
        # 3. RÉACTION DU PRIX
        # =========================================

        reaction_score = min(
            1.0,

            (
                fmean(
                    touch.reaction_atr
                    for touch
                    in touches
                )
                /
                self._config
                .target_reaction_atr
            ),
        )

        # =========================================
        # 4. RÉCENCE
        # =========================================

        last_confirmation_index = max(
            touch.confirmation_index
            for touch
            in touches
        )

        age_bars = max(
            0,

            as_of_index
            - last_confirmation_index,
        )

        # Décroissance exponentielle.
        #
        # Après recency_half_life_bars :
        # score ≈ 0.5.
        recency_score = math.exp(

            -math.log(2.0)

            * age_bars

            / self._config
            .recency_half_life_bars
        )

        # =========================================
        # 5. COMPACTNESS
        # =========================================

        compactness_score = (
            self._compactness(
                touches=touches,

                lower_price=lower_price,

                upper_price=upper_price,
            )
        )

        weights = (
            self._config.score_weights
        )

        total = (

            touch_score
            * weights.touches

            +

            prominence_score
            * weights.prominence

            +

            reaction_score
            * weights.reaction

            +

            recency_score
            * weights.recency

            +

            compactness_score
            * weights.compactness
        )

        # Protection contre 1.0000000002
        # dû aux flottants.
        total = min(
            1.0,

            max(
                0.0,
                total,
            ),
        )

        return ZoneScoreBreakdown(

            touches=touch_score,

            prominence=(
                prominence_score
            ),

            reaction=(
                reaction_score
            ),

            recency=(
                recency_score
            ),

            compactness=(
                compactness_score
            ),

            total=total,
        )

    @staticmethod
    def _compactness(
        *,
        touches: Sequence[ZoneTouch],

        lower_price: float,

        upper_price: float,
    ) -> float:
        """
        Une bonne zone possède des contacts
        relativement concentrés.

        On calcule leur dispersion pondérée.
        """

        width = (
            upper_price
            - lower_price
        )

        if width <= 0:

            return 1.0

        total_weight = sum(
            touch.weight
            for touch
            in touches
        )

        center = (
            sum(
                touch.price
                * touch.weight

                for touch
                in touches
            )
            /
            total_weight
        )

        variance = (
            sum(

                touch.weight
                * (
                    touch.price
                    - center
                ) ** 2

                for touch
                in touches
            )
            /
            total_weight
        )

        standard_deviation = (
            math.sqrt(
                max(
                    0.0,
                    variance,
                )
            )
        )

        normalized_dispersion = (
            standard_deviation
            / width
        )

        return max(
            0.0,

            1.0
            - min(
                1.0,

                normalized_dispersion
                * 2,
            ),
        )