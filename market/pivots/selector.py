from collections.abc import Sequence

from forex_bot.core.enums import (
    PivotType,
)

from .config import (
    PivotDetectorConfig,
)

from .types import (
    PivotCandidate,
)


class PivotSelector:
    """
    Transforme les candidats en pivots significatifs.

    Deux opérations :

    1. élimination des pivots trop faibles ;
    2. suppression des doublons proches.
    """

    def __init__(
        self,
        config: PivotDetectorConfig,
    ) -> None:

        self._config = config

    def select(
        self,
        candidates: Sequence[
            PivotCandidate
        ],
    ) -> tuple[
        PivotCandidate,
        ...
    ]:

        strong_candidates = [
            candidate
            for candidate
            in candidates
            if (
                candidate.prominence_atr
                >=
                self._config
                .min_prominence_atr
            )
        ]

        high_candidates = [
            candidate
            for candidate
            in strong_candidates
            if (
                candidate.pivot_type
                == PivotType.HIGH
            )
        ]

        low_candidates = [
            candidate
            for candidate
            in strong_candidates
            if (
                candidate.pivot_type
                == PivotType.LOW
            )
        ]

        selected_highs = (
            self._non_maximum_suppression(
                high_candidates
            )
        )

        selected_lows = (
            self._non_maximum_suppression(
                low_candidates
            )
        )

        selected = (
            list(selected_highs)
            + list(selected_lows)
        )

        # On remet tout dans l'ordre
        # chronologique après sélection.
        selected.sort(
            key=lambda item:
            item.candle_index
        )

        return tuple(
            selected
        )

    def _non_maximum_suppression(
        self,
        candidates: Sequence[
            PivotCandidate
        ],
    ) -> tuple[
        PivotCandidate,
        ...
    ]:
        """
        Technique inspirée de la vision informatique.

        Si plusieurs candidats proches représentent
        probablement le même sommet/creux :

        nous gardons le candidat possédant
        la meilleure prominence normalisée.

        Cela permet par exemple de transformer :

            H H H

        en :

              H
        """

        if not candidates:

            return ()

        # Les meilleurs candidats passent d'abord.
        ranked = sorted(
            candidates,
            key=lambda candidate: (
                -candidate.prominence_atr,
                -candidate.prominence,
                candidate.candle_index,
            ),
        )

        selected: list[
            PivotCandidate
        ] = []

        for candidate in ranked:

            too_close = any(
                abs(
                    candidate.candle_index
                    - existing.candle_index
                )
                <
                self._config
                .min_separation_bars

                for existing
                in selected
            )

            if too_close:

                continue

            selected.append(
                candidate
            )

        selected.sort(
            key=lambda candidate:
            candidate.candle_index
        )

        return tuple(
            selected
        )