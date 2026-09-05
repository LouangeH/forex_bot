from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from forex_bot.core.enums import (
    PivotType,
    Timeframe,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    Candle,
    SymbolSpec,
)

from forex_bot.market.pivots import (
    PivotDetector,
    PivotDetectorConfig,
)


START = datetime(
    2026,
    8,
    21,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_candles(
    closes: list[float],
) -> list[Candle]:
    """
    Construit des bougies artificielles M15.

    Nous connaissons volontairement leur forme
    afin de pouvoir vérifier précisément
    le résultat du détecteur.
    """

    candles = []

    for index, close in enumerate(
        closes
    ):

        candles.append(
            Candle(
                symbol="EURUSD",

                timeframe=(
                    Timeframe.M15
                ),

                open_time=(
                    START
                    + timedelta(
                        minutes=15 * index
                    )
                ),

                open=close,

                high=(
                    close + 0.0005
                ),

                low=(
                    close - 0.0005
                ),

                close=close,

                tick_volume=100,
            )
        )

    return candles


def symbol_spec() -> SymbolSpec:

    return SymbolSpec(
        symbol="EURUSD",

        digits=5,

        point=0.00001,

        tick_size=0.00001,

        tick_value=1.0,

        volume_min=0.01,

        volume_max=100.0,

        volume_step=0.01,

        trade_enabled=True,
    )


def detector() -> PivotDetector:

    return PivotDetector(
        PivotDetectorConfig(
            left_bars=2,

            right_bars=2,

            # Petite période uniquement
            # pour les données artificielles.
            atr_period=2,

            # On désactive pratiquement
            # le filtre de prominence
            # pour tester la structure.
            min_prominence_atr=0.0,

            min_separation_bars=2,

            plateau_tolerance_points=0.0,
        )
    )


def test_detects_clear_pivot_high():

    candles = make_candles(
        [
            1.1000,
            1.1010,
            1.1020,

            # Sommet évident.
            1.1100,

            1.1020,
            1.1010,
            1.1000,
        ]
    )

    pivots = detector().detect(
        candles,
        symbol_spec(),
    )

    highs = [
        detected
        for detected
        in pivots
        if (
            detected
            .pivot
            .pivot_type
            == PivotType.HIGH
        )
    ]

    assert len(highs) == 1

    assert (
        highs[0]
        .pivot
        .candle_index
        == 3
    )


def test_detects_clear_pivot_low():

    candles = make_candles(
        [
            1.1100,
            1.1090,
            1.1080,

            # Creux évident.
            1.1000,

            1.1080,
            1.1090,
            1.1100,
        ]
    )

    pivots = detector().detect(
        candles,
        symbol_spec(),
    )

    lows = [
        detected
        for detected
        in pivots
        if (
            detected
            .pivot
            .pivot_type
            == PivotType.LOW
        )
    ]

    assert len(lows) == 1

    assert (
        lows[0]
        .pivot
        .candle_index
        == 3
    )


def test_pivot_requires_future_confirmation():

    complete = make_candles(
        [
            1.1000,
            1.1010,
            1.1020,

            1.1100,

            1.1020,
            1.1010,
        ]
    )

    # Nous retirons la dernière bougie.
    #
    # Le pivot n'a donc pas encore les
    # 2 bougies nécessaires à droite.
    incomplete = complete[:-1]

    pivots = detector().detect(
        incomplete,
        symbol_spec(),
    )

    high_indexes = {
        detected
        .pivot
        .candle_index

        for detected
        in pivots

        if (
            detected
            .pivot
            .pivot_type
            == PivotType.HIGH
        )
    }

    assert 3 not in high_indexes


def test_confirmation_index_is_correct():

    candles = make_candles(
        [
            1.1000,
            1.1010,
            1.1020,

            1.1100,

            1.1020,
            1.1010,
            1.1000,
        ]
    )

    pivots = detector().detect(
        candles,
        symbol_spec(),
    )

    pivot = next(
        detected
        for detected
        in pivots
        if (
            detected
            .pivot
            .pivot_type
            == PivotType.HIGH
        )
    )

    # Pivot = index 3
    # right_bars = 2
    #
    # Donc il ne devient confirmé
    # qu'à l'index 5.
    assert (
        pivot.confirmation_index
        == 5
    )


def test_invalid_candle_order_is_rejected():

    candles = make_candles(
        [
            1.1000,
            1.1010,
            1.1020,
            1.1030,
        ]
    )

    reversed_candles = list(
        reversed(candles)
    )

    with pytest.raises(
        DomainValidationError
    ):

        detector().detect(
            reversed_candles,
            symbol_spec(),
        )


def test_different_symbol_is_rejected():

    candles = make_candles(
        [
            1.1000,
            1.1010,
            1.1020,
            1.1030,
        ]
    )

    wrong_spec = SymbolSpec(
        symbol="GBPUSD",

        digits=5,

        point=0.00001,

        tick_size=0.00001,

        tick_value=1.0,

        volume_min=0.01,

        volume_max=100.0,

        volume_step=0.01,
    )

    with pytest.raises(
        DomainValidationError
    ):

        detector().detect(
            candles,
            wrong_spec,
        )