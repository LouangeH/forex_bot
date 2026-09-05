# forex_bot/market/support_resistance/detector.py

from collections.abc import Sequence

from statistics import median

from forex_bot.core.enums import (
    PivotType,
    Timeframe,
    ZoneType,
)

from forex_bot.core.models import (
    Candle,
    PriceZone,
    SymbolSpec,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from .clustering import (
    ZoneClusterer,
)

from .config import (
    SupportResistanceConfig,
)

from .reaction import (
    ReactionAnalyzer,
)

from .scoring import (
    ZoneScorer,
)

from .types import (
    DetectedZone,
    ZoneTouch,
)

from .validation import (
    validate_support_resistance_inputs,
)


class SupportResistanceDetector:
    """
    Façade du moteur Support/Résistance.

    Les autres parties du programme n'auront
    besoin de connaître que cette classe.
    """

    DETECTOR_NAME = (
        "support_resistance"
    )

    DETECTOR_VERSION = "1.0.0"

    def __init__(
        self,
        config:
        SupportResistanceConfig
        | None = None,
    ) -> None:

        self._config = (
            config
            or SupportResistanceConfig()
        )

        self._reaction_analyzer = (
            ReactionAnalyzer(
                self._config
            )
        )

        self._clusterer = (
            ZoneClusterer(
                self._config
            )
        )

        self._scorer = (
            ZoneScorer(
                self._config
            )
        )

    @property
    def config(
        self,
    ) -> SupportResistanceConfig:

        return self._config

    def detect(
        self,
        *,
        candles: Sequence[Candle],

        pivots: Sequence[DetectedPivot],

        symbol_spec: SymbolSpec,

        as_of_index: int | None = None,
    ) -> tuple[
        DetectedZone,
        ...
    ]:
        """
        Détecte les zones connues au moment demandé.

        as_of_index=None :
            utilise la dernière bougie fournie.

        Les bougies reçues doivent être clôturées.
        """

        resolved_as_of = (
            len(candles) - 1

            if as_of_index is None

            else as_of_index
        )

        validate_support_resistance_inputs(

            candles=candles,

            pivots=pivots,

            symbol_spec=symbol_spec,

            as_of_index=(
                resolved_as_of
            ),
        )

        timeframe = (
            candles[0].timeframe
        )

        # =========================================
        # PROTECTION LOOK-AHEAD
        # =========================================

        known_pivots = [

            pivot

            for pivot
            in pivots

            if (
                pivot.confirmation_index
                <= resolved_as_of
            )

            and (
                pivot.prominence_atr
                >=
                self._config
                .min_pivot_prominence_atr
            )
        ]

        touches = [

            self._create_touch(

                candles=candles,

                detected_pivot=pivot,

                as_of_index=(
                    resolved_as_of
                ),
            )

            for pivot
            in known_pivots
        ]

        # Pivot Low → Support.
        support_touches = [

            touch

            for touch
            in touches

            if (
                touch.pivot_type
                == PivotType.LOW
            )
        ]

        # Pivot High → Résistance.
        resistance_touches = [

            touch

            for touch
            in touches

            if (
                touch.pivot_type
                == PivotType.HIGH
            )
        ]

        zones: list[
            DetectedZone
        ] = []

        zones.extend(
            self._build_zones(

                touches=support_touches,

                zone_type=(
                    ZoneType.SUPPORT
                ),

                timeframe=timeframe,

                symbol_spec=(
                    symbol_spec
                ),

                as_of_index=(
                    resolved_as_of
                ),
            )
        )

        zones.extend(
            self._build_zones(

                touches=(
                    resistance_touches
                ),

                zone_type=(
                    ZoneType.RESISTANCE
                ),

                timeframe=timeframe,

                symbol_spec=(
                    symbol_spec
                ),

                as_of_index=(
                    resolved_as_of
                ),
            )
        )

        # Ordre déterministe :
        # d'abord type, puis niveau.
        zones.sort(
            key=lambda detected: (
                detected
                .zone
                .zone_type
                .value,

                detected.center_price,
            )
        )

        return tuple(
            zones
        )

    def _create_touch(
        self,
        *,
        candles: Sequence[Candle],

        detected_pivot: DetectedPivot,

        as_of_index: int,
    ) -> ZoneTouch:
        """
        Transforme un DetectedPivot de l'étape 2
        en contact utilisable par le moteur S/R.
        """

        reaction_atr = (
            self
            ._reaction_analyzer
            .reaction_atr(

                candles=candles,

                pivot=detected_pivot,

                as_of_index=(
                    as_of_index
                ),
            )
        )

        prominence_component = min(

            detected_pivot
            .prominence_atr,

            self._config
            .prominence_weight_cap,
        )

        weight = (

            1.0

            + prominence_component

            + (
                reaction_atr
                * self._config
                .reaction_weight_factor
            )
        )

        return ZoneTouch(

            pivot_type=(
                detected_pivot
                .pivot
                .pivot_type
            ),

            pivot_index=(
                detected_pivot
                .pivot
                .candle_index
            ),

            confirmation_index=(
                detected_pivot
                .confirmation_index
            ),

            pivot_time=(
                detected_pivot
                .pivot
                .time
            ),

            confirmation_time=(
                detected_pivot
                .confirmation_candle_time
            ),

            price=(
                detected_pivot
                .pivot
                .price
            ),

            atr=(
                detected_pivot.atr
            ),

            prominence_atr=(
                detected_pivot
                .prominence_atr
            ),

            reaction_atr=(
                reaction_atr
            ),

            weight=weight,
        )

    def _build_zones(
        self,
        *,
        touches: Sequence[ZoneTouch],

        zone_type: ZoneType,

        timeframe: Timeframe,

        symbol_spec: SymbolSpec,

        as_of_index: int,
    ) -> list[
        DetectedZone
    ]:

        clusters = (
            self._clusterer.cluster(

                touches=touches,

                symbol_spec=symbol_spec,
            )
        )

        zones: list[
            DetectedZone
        ] = []

        for cluster in clusters:

            if (
                len(cluster)
                < self._config.min_touches
            ):

                continue

            detected = (
                self._build_one_zone(

                    touches=cluster,

                    zone_type=zone_type,

                    timeframe=timeframe,

                    symbol_spec=(
                        symbol_spec
                    ),

                    as_of_index=(
                        as_of_index
                    ),
                )
            )

            if (
                detected.score.total
                < self._config.min_quality
            ):

                continue

            zones.append(
                detected
            )

        return zones

    def _build_one_zone(
        self,
        *,
        touches: Sequence[ZoneTouch],

        zone_type: ZoneType,

        timeframe: Timeframe,

        symbol_spec: SymbolSpec,

        as_of_index: int,
    ) -> DetectedZone:
        """
        Construit une zone unique
        à partir d'un cluster.
        """

        total_weight = sum(
            touch.weight
            for touch
            in touches
        )

        weighted_center = (
            sum(

                touch.price
                * touch.weight

                for touch
                in touches
            )
            /
            total_weight
        )

        median_atr = median(
            touch.atr
            for touch
            in touches
        )

        minimum_padding = (

            self._config
            .min_zone_half_width_points

            * symbol_spec.point
        )

        atr_padding = (

            median_atr

            * self._config
            .zone_padding_atr
        )

        padding = max(
            minimum_padding,
            atr_padding,
        )

        raw_lower = (
            min(
                touch.price
                for touch
                in touches
            )
            - padding
        )

        raw_upper = (
            max(
                touch.price
                for touch
                in touches
            )
            + padding
        )

        # On rend la zone symétrique autour
        # du centre pondéré.
        half_width = max(

            weighted_center
            - raw_lower,

            raw_upper
            - weighted_center,
        )

        lower_price = (
            weighted_center
            - half_width
        )

        upper_price = (
            weighted_center
            + half_width
        )

        score = (
            self._scorer.score(

                touches=touches,

                lower_price=(
                    lower_price
                ),

                upper_price=(
                    upper_price
                ),

                as_of_index=(
                    as_of_index
                ),
            )
        )

        chronological = sorted(

            touches,

            key=lambda touch: (
                touch.confirmation_index,
                touch.pivot_index,
            ),
        )

        # Si min_touches = 2,
        # la zone devient officiellement connue
        # quand le deuxième contact est confirmé.
        confirmation_touch = (
            chronological[
                self._config
                .min_touches
                - 1
            ]
        )

        last_touch = (
            chronological[-1]
        )

        zone = PriceZone(

            symbol=(
                symbol_spec.symbol
            ),

            timeframe=timeframe,

            zone_type=zone_type,

            lower_price=(
                lower_price
            ),

            upper_price=(
                upper_price
            ),

            touches=len(
                touches
            ),

            first_seen=min(
                touch.pivot_time
                for touch
                in touches
            ),

            last_seen=max(
                touch.pivot_time
                for touch
                in touches
            ),

            quality=(
                score.total
            ),

            pivot_indexes=tuple(
                sorted(
                    touch.pivot_index

                    for touch
                    in touches
                )
            ),
        )

        return DetectedZone(

            zone=zone,

            median_atr=(
                median_atr
            ),

            confirmed_from_index=(
                confirmation_touch
                .confirmation_index
            ),

            confirmed_from_time=(
                confirmation_touch
                .confirmation_time
            ),

            last_updated_index=(
                last_touch
                .confirmation_index
            ),

            last_updated_time=(
                last_touch
                .confirmation_time
            ),

            touches_detail=tuple(
                sorted(

                    touches,

                    key=lambda touch:
                    touch.pivot_index,
                )
            ),

            score=score,

            detector_name=(
                self.DETECTOR_NAME
            ),

            detector_version=(
                self.DETECTOR_VERSION
            ),
        )