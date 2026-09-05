from collections.abc import Sequence

from forex_bot.core.models import (
    Candle,
    Pivot,
    SymbolSpec,
)

from .candidate_detector import (
    PivotCandidateDetector,
)

from .config import (
    PivotDetectorConfig,
)

from .selector import (
    PivotSelector,
)

from .types import (
    DetectedPivot,
)

from .validation import (
    validate_candle_series,
)


class PivotDetector:
    """
    Façade principale de détection des pivots.

    Les autres modules utiliseront CETTE classe.

    Ils n'auront pas besoin de savoir comment
    fonctionnent :
    - l'ATR ;
    - les candidats ;
    - la suppression des doublons.
    """

    def __init__(
        self,
        config: PivotDetectorConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or PivotDetectorConfig()
        )

        self._candidate_detector = (
            PivotCandidateDetector(
                self._config
            )
        )

        self._selector = PivotSelector(
            self._config
        )

    @property
    def config(
        self,
    ) -> PivotDetectorConfig:

        return self._config

    def detect(
        self,
        candles: Sequence[Candle],
        symbol_spec: SymbolSpec,
    ) -> tuple[
        DetectedPivot,
        ...
    ]:
        """
        Détecte uniquement les pivots confirmés.

        CONTRAT IMPORTANT :

        `candles` doit contenir uniquement
        des bougies clôturées.

        Le futur module MT5 sera responsable
        de retirer la bougie actuellement
        en formation avant d'appeler cette méthode.
        """

        validate_candle_series(
            candles,
            symbol_spec,
        )

        candidates = (
            self._candidate_detector
            .detect(
                candles,
                symbol_spec,
            )
        )

        selected = (
            self._selector.select(
                candidates
            )
        )

        detected: list[
            DetectedPivot
        ] = []

        for candidate in selected:

            candle = candles[
                candidate.candle_index
            ]

            confirmation_index = (
                candidate.candle_index
                + self._config.right_bars
            )

            # Ce contrôle devrait normalement
            # toujours être vrai grâce au
            # CandidateDetector.
            #
            # Nous le conservons néanmoins comme
            # barrière supplémentaire.
            if (
                confirmation_index
                >= len(candles)
            ):

                continue

            confirmation_candle = (
                candles[
                    confirmation_index
                ]
            )

            pivot = Pivot(
                symbol=candle.symbol,

                timeframe=(
                    candle.timeframe
                ),

                pivot_type=(
                    candidate.pivot_type
                ),

                candle_index=(
                    candidate.candle_index
                ),

                time=(
                    candle.open_time
                ),

                price=(
                    candidate.price
                ),

                strength=(
                    self._config
                    .confirmation_strength
                ),

                prominence=(
                    candidate.prominence
                ),
            )

            detected.append(
                DetectedPivot(
                    pivot=pivot,

                    atr=(
                        candidate.atr
                    ),

                    prominence_atr=(
                        candidate
                        .prominence_atr
                    ),

                    confirmation_index=(
                        confirmation_index
                    ),

                    confirmation_candle_time=(
                        confirmation_candle
                        .open_time
                    ),
                )
            )

        return tuple(
            detected
        )