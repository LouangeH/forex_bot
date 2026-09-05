# forex_bot/patterns/continuation/impulse.py

from __future__ import annotations

from statistics import median

from forex_bot.core.enums import (
    PivotType,
    TradeDirection,
)

from forex_bot.patterns.context import (
    PatternContext,
)

from .config import (
    ContinuationPatternConfig,
)

from .types import (
    ImpulseLeg,
)


class ImpulseDetector:
    """
    Recherche la meilleure impulsion récente.

    LOW -> HIGH :
        impulsion haussière.

    HIGH -> LOW :
        impulsion baissière.
    """

    def __init__(
        self,
        config: ContinuationPatternConfig,
    ) -> None:

        self._config = config

    def detect_best(
        self,
        context: PatternContext,
    ) -> ImpulseLeg | None:

        minimum_index = max(

            0,

            context.as_of_index
            - self._config
            .impulse_lookback_bars,
        )

        pivots = [

            item

            for item
            in context.pivots

            if (

                item.pivot.candle_index
                >= minimum_index

                and

                item.confirmation_index
                <= context.as_of_index
            )
        ]

        pivots.sort(
            key=lambda item:
            item.pivot.candle_index
        )

        candidates: list[
            ImpulseLeg
        ] = []

        for start_position, start in enumerate(
            pivots
        ):

            for end in pivots[
                start_position + 1:
            ]:

                if (
                    start.pivot.pivot_type
                    == end.pivot.pivot_type
                ):

                    continue

                duration = (

                    end.pivot.candle_index

                    -

                    start.pivot.candle_index
                )

                if (
                    duration
                    < self._config.min_impulse_bars
                ):

                    continue

                if (
                    duration
                    > self._config.max_impulse_bars
                ):

                    break

                if (

                    start.pivot.pivot_type
                    == PivotType.LOW

                    and

                    end.pivot.pivot_type
                    == PivotType.HIGH
                ):

                    direction = (
                        TradeDirection.BUY
                    )

                elif (

                    start.pivot.pivot_type
                    == PivotType.HIGH

                    and

                    end.pivot.pivot_type
                    == PivotType.LOW
                ):

                    direction = (
                        TradeDirection.SELL
                    )

                else:

                    continue

                candidate = (
                    self._build_candidate(

                        context=context,

                        start=start,

                        end=end,

                        direction=direction,
                    )
                )

                if candidate is not None:

                    candidates.append(
                        candidate
                    )

        if not candidates:

            return None

        # On privilégie :
        #
        # 1. qualité ;
        # 2. récence ;
        # 3. amplitude.
        return max(

            candidates,

            key=lambda leg: (

                leg.score,

                leg.end_index,

                leg.distance_atr,
            ),
        )

    def _build_candidate(
        self,
        *,
        context: PatternContext,

        start,

        end,

        direction: TradeDirection,
    ) -> ImpulseLeg | None:

        start_index = (
            start.pivot.candle_index
        )

        end_index = (
            end.pivot.candle_index
        )

        start_price = (
            start.pivot.price
        )

        end_price = (
            end.pivot.price
        )

        distance = abs(
            end_price
            - start_price
        )

        atr_reference = median(

            value

            for value
            in (
                start.atr,
                end.atr,
            )

            if value > 0
        )

        if atr_reference <= 0:

            return None

        distance_atr = (
            distance
            / atr_reference
        )

        if (
            distance_atr
            < self._config.min_impulse_atr
        ):

            return None

        candles = context.candles[
            start_index
            :
            end_index + 1
        ]

        # ------------------------------------------------
        # EFFICIENCY
        # ------------------------------------------------
        #
        # Un mouvement :
        #
        # +10 -9 +10 -9 +10
        #
        # est beaucoup moins propre qu'un :
        #
        # +2 +2 +2 +2 +2
        #
        # même si la destination finale
        # peut être similaire.

        path = 0.0

        for previous, current in zip(
            candles,
            candles[1:],
            strict=False,
        ):

            path += abs(
                current.close
                - previous.close
            )

        net_move = abs(

            candles[-1].close

            -

            candles[0].close
        )

        efficiency = (

            min(
                1.0,

                net_move
                / path
            )

            if path > 0

            else 0.0
        )

        # ------------------------------------------------
        # BOUGIES DIRECTIONNELLES
        # ------------------------------------------------

        if (
            direction
            == TradeDirection.BUY
        ):

            directional_count = sum(

                1

                for candle
                in candles

                if (
                    candle.close
                    > candle.open
                )
            )

        else:

            directional_count = sum(

                1

                for candle
                in candles

                if (
                    candle.close
                    < candle.open
                )
            )

        directional_ratio = (

            directional_count
            / len(candles)
        )

        if (
            efficiency
            < self._config
            .min_impulse_efficiency
        ):

            return None

        if (
            directional_ratio
            < self._config
            .min_directional_candle_ratio
        ):

            return None

        amplitude_score = min(

            1.0,

            distance_atr

            /

            max(

                self._config
                .min_impulse_atr
                * 2,

                1e-12,
            ),
        )

        efficiency_score = min(

            1.0,

            efficiency

            /

            max(

                self._config
                .min_impulse_efficiency,

                1e-12,
            ),
        )

        directional_score = min(

            1.0,

            directional_ratio

            /

            max(

                self._config
                .min_directional_candle_ratio,

                1e-12,
            ),
        )

        score = (

            0.45
            * amplitude_score

            +

            0.35
            * efficiency_score

            +

            0.20
            * directional_score
        )

        return ImpulseLeg(

            direction=direction,

            start_index=start_index,

            end_index=end_index,

            start_price=start_price,

            end_price=end_price,

            atr_reference=(
                atr_reference
            ),

            distance=distance,

            distance_atr=(
                distance_atr
            ),

            duration_bars=(
                end_index
                - start_index
            ),

            efficiency=(
                efficiency
            ),

            directional_candle_ratio=(
                directional_ratio
            ),

            score=min(

                1.0,

                max(
                    0.0,
                    score,
                ),
            ),
        )