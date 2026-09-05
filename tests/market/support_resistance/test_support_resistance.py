from datetime import (
    datetime,
    timedelta,
    timezone,
)

from forex_bot.core.enums import (
    PivotType,
    Timeframe,
    ZoneType,
)

from forex_bot.core.models import (
    Candle,
    Pivot,
    SymbolSpec,
)

from forex_bot.market.pivots.types import (
    DetectedPivot,
)

from forex_bot.market.support_resistance import (
    SupportResistanceConfig,
    SupportResistanceDetector,
    ZoneBook,
)


START = datetime(
    2026,
    8,
    21,
    tzinfo=timezone.utc,
)


def make_candles(
    count: int = 30,
) -> list[Candle]:

    candles = []

    for index in range(count):

        base = (
            1.1050
            + (index % 4) * 0.0002
        )

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

                open=base,

                high=(
                    base + 0.0005
                ),

                low=(
                    base - 0.0005
                ),

                close=base,

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
    )


def make_pivot(
    candles,
    *,
    index: int,
    pivot_type: PivotType,
    confirmation_index: int,
    prominence_atr: float = 1.0,
) -> DetectedPivot:

    candle = candles[index]

    price = (
        candle.high
        if (
            pivot_type
            == PivotType.HIGH
        )
        else candle.low
    )

    return DetectedPivot(

        pivot=Pivot(

            symbol="EURUSD",

            timeframe=(
                Timeframe.M15
            ),

            pivot_type=(
                pivot_type
            ),

            candle_index=index,

            time=(
                candle.open_time
            ),

            price=price,

            strength=4,

            prominence=0.001,
        ),

        atr=0.001,

        prominence_atr=(
            prominence_atr
        ),

        confirmation_index=(
            confirmation_index
        ),

        confirmation_candle_time=(
            candles[
                confirmation_index
            ].open_time
        ),
    )


def detector():

    return SupportResistanceDetector(

        SupportResistanceConfig(

            min_touches=2,

            target_touches=3,

            # Désactivé pour les tests
            # structurels artificiels.
            min_pivot_prominence_atr=0,

            cluster_distance_atr=1.0,

            min_cluster_distance_points=5,

            zone_padding_atr=0.05,

            max_cluster_width_atr=2.0,

            reaction_bars=4,

            min_quality=0,
        )
    )


def test_two_low_pivots_create_support():

    candles = make_candles()

    pivots = [

        make_pivot(
            candles,
            index=5,
            pivot_type=PivotType.LOW,
            confirmation_index=7,
        ),

        make_pivot(
            candles,
            index=13,
            pivot_type=PivotType.LOW,
            confirmation_index=15,
        ),
    ]

    zones = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),
    )

    supports = [

        zone

        for zone
        in zones

        if (
            zone.zone.zone_type
            == ZoneType.SUPPORT
        )
    ]

    assert len(supports) == 1

    assert (
        supports[0].zone.touches
        == 2
    )


def test_two_high_pivots_create_resistance():

    candles = make_candles()

    pivots = [

        make_pivot(
            candles,
            index=6,
            pivot_type=PivotType.HIGH,
            confirmation_index=8,
        ),

        make_pivot(
            candles,
            index=14,
            pivot_type=PivotType.HIGH,
            confirmation_index=16,
        ),
    ]

    zones = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),
    )

    resistances = [

        zone

        for zone
        in zones

        if (
            zone.zone.zone_type
            == ZoneType.RESISTANCE
        )
    ]

    assert len(resistances) == 1


def test_future_confirmation_is_not_used():

    candles = make_candles()

    pivots = [

        make_pivot(
            candles,
            index=5,
            pivot_type=PivotType.LOW,
            confirmation_index=7,
        ),

        make_pivot(
            candles,
            index=13,
            pivot_type=PivotType.LOW,
            confirmation_index=15,
        ),
    ]

    # À l'index 14, le deuxième pivot
    # n'est pas encore confirmé.
    zones = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),

        as_of_index=14,
    )

    supports = [

        zone

        for zone
        in zones

        if (
            zone.zone.zone_type
            == ZoneType.SUPPORT
        )
    ]

    assert len(supports) == 0


def test_zone_has_stable_id():

    candles = make_candles()

    pivots = [

        make_pivot(
            candles,
            index=5,
            pivot_type=PivotType.LOW,
            confirmation_index=7,
        ),

        make_pivot(
            candles,
            index=13,
            pivot_type=PivotType.LOW,
            confirmation_index=15,
        ),
    ]

    first = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),
    )

    second = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),
    )

    assert (
        first[0].zone_id
        == second[0].zone_id
    )


def test_zone_book_returns_nearest_support():

    candles = make_candles()

    pivots = [

        make_pivot(
            candles,
            index=5,
            pivot_type=PivotType.LOW,
            confirmation_index=7,
        ),

        make_pivot(
            candles,
            index=13,
            pivot_type=PivotType.LOW,
            confirmation_index=15,
        ),
    ]

    zones = detector().detect(

        candles=candles,

        pivots=pivots,

        symbol_spec=symbol_spec(),
    )

    book = ZoneBook(
        zones
    )

    support = (
        book.nearest_support(
            1.2000
        )
    )

    assert support is not None

    assert (
        support.zone.zone_type
        == ZoneType.SUPPORT
    )