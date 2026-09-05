from collections.abc import Sequence

from forex_bot.core.enums import (
    PivotType,
)

from forex_bot.core.models import (
    Candle,
    SymbolSpec,
)

from .config import (
    PivotDetectorConfig,
)

from .types import (
    PivotCandidate,
)

from .volatility import (
    atr_at_index,
)


class PivotCandidateDetector:
    """
    Recherche les pivots POTENTIELS.

    Cette classe ne décide pas encore
    lesquels sont suffisamment importants.
    """

    def __init__(
        self,
        config: PivotDetectorConfig,
    ) -> None:

        self._config = config

    def detect(
        self,
        candles: Sequence[Candle],
        symbol_spec: SymbolSpec,
    ) -> tuple[
        PivotCandidate,
        ...
    ]:

        candidates: list[
            PivotCandidate
        ] = []

        tolerance = (
            self._config
            .plateau_tolerance_points
            * symbol_spec.point
        )

        # Les premiers indices ne peuvent pas
        # devenir pivots car ils n'ont pas assez
        # de bougies à gauche.
        #
        # ATR exige également suffisamment
        # d'historique.
        first_index = max(
            self._config.left_bars,
            self._config.atr_period,
        )

        # Les dernières bougies ne peuvent pas
        # devenir pivots tant que les bougies
        # de confirmation à droite n'existent pas.
        last_index = (
            len(candles)
            - self._config.right_bars
            - 1
        )

        if (
            last_index
            < first_index
        ):

            return ()

        for index in range(
            first_index,
            last_index + 1,
        ):

            atr = atr_at_index(
                candles,
                index,
                self._config.atr_period,
            )

            if (
                atr is None
                or atr <= 0
            ):

                continue

            current = candles[index]

            left = candles[
                index
                - self._config.left_bars
                :
                index
            ]

            right = candles[
                index + 1
                :
                index
                + self._config.right_bars
                + 1
            ]

            high_candidate = (
                self._is_high_candidate(
                    current=current,
                    left=left,
                    right=right,
                    tolerance=tolerance,
                )
            )

            if high_candidate:

                prominence = (
                    self._high_prominence(
                        current=current,
                        left=left,
                        right=right,
                    )
                )

                candidates.append(
                    PivotCandidate(
                        pivot_type=(
                            PivotType.HIGH
                        ),
                        candle_index=index,
                        price=current.high,
                        prominence=prominence,
                        atr=atr,
                        prominence_atr=(
                            prominence
                            / atr
                        ),
                    )
                )

            low_candidate = (
                self._is_low_candidate(
                    current=current,
                    left=left,
                    right=right,
                    tolerance=tolerance,
                )
            )

            if low_candidate:

                prominence = (
                    self._low_prominence(
                        current=current,
                        left=left,
                        right=right,
                    )
                )

                candidates.append(
                    PivotCandidate(
                        pivot_type=(
                            PivotType.LOW
                        ),
                        candle_index=index,
                        price=current.low,
                        prominence=prominence,
                        atr=atr,
                        prominence_atr=(
                            prominence
                            / atr
                        ),
                    )
                )

        return tuple(
            candidates
        )

    @staticmethod
    def _is_high_candidate(
        *,
        current: Candle,
        left: Sequence[Candle],
        right: Sequence[Candle],
        tolerance: float,
    ) -> bool:
        """
        Vérifie :

        HIGH actuel >= HIGH gauche
        et
        HIGH actuel >= HIGH droite.

        Une petite tolérance permet de gérer
        les doubles sommets / plateaux.
        """

        left_max = max(
            candle.high
            for candle
            in left
        )

        right_max = max(
            candle.high
            for candle
            in right
        )

        return (
            current.high
            >= left_max - tolerance
            and
            current.high
            >= right_max - tolerance
        )

    @staticmethod
    def _is_low_candidate(
        *,
        current: Candle,
        left: Sequence[Candle],
        right: Sequence[Candle],
        tolerance: float,
    ) -> bool:

        left_min = min(
            candle.low
            for candle
            in left
        )

        right_min = min(
            candle.low
            for candle
            in right
        )

        return (
            current.low
            <= left_min + tolerance
            and
            current.low
            <= right_min + tolerance
        )

    @staticmethod
    def _high_prominence(
        *,
        current: Candle,
        left: Sequence[Candle],
        right: Sequence[Candle],
    ) -> float:
        """
        Pour un sommet :

        on cherche jusqu'où le marché est descendu
        de chaque côté.

        On conserve le plus petit des deux mouvements.

        Ainsi un sommet n'est considéré important
        que s'il est réellement visible DES DEUX CÔTÉS.
        """

        left_base = min(
            candle.low
            for candle
            in left
        )

        right_base = min(
            candle.low
            for candle
            in right
        )

        left_move = (
            current.high
            - left_base
        )

        right_move = (
            current.high
            - right_base
        )

        return max(
            0.0,
            min(
                left_move,
                right_move,
            ),
        )

    @staticmethod
    def _low_prominence(
        *,
        current: Candle,
        left: Sequence[Candle],
        right: Sequence[Candle],
    ) -> float:

        left_ceiling = max(
            candle.high
            for candle
            in left
        )

        right_ceiling = max(
            candle.high
            for candle
            in right
        )

        left_move = (
            left_ceiling
            - current.low
        )

        right_move = (
            right_ceiling
            - current.low
        )

        return max(
            0.0,
            min(
                left_move,
                right_move,
            ),
        )