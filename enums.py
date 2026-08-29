from enum import Enum


class Timeframe(str, Enum):
    """
    Timeframes que notre moteur est capable de représenter.

    Notre stratégie actuelle entre principalement en M15,
    mais le moteur pourra plus tard analyser H1, H4, etc.
    """

    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


class RuntimeMode(str, Enum):
    """
    Mode dans lequel le programme fonctionne.

    BACKTEST :
        données historiques uniquement.

    DEMO :
        compte Equiti Demo.

    LIVE :
        compte Equiti UAE réel.
    """

    BACKTEST = "BACKTEST"
    DEMO = "DEMO"
    LIVE = "LIVE"


class AccountMode(str, Enum):
    """
    Type réel du compte retourné par MT5.
    """

    DEMO = "DEMO"
    LIVE = "LIVE"


class TradeDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class EntryType(str, Enum):
    """
    Notre stratégie actuelle utilisera MARKET.

    LIMIT et STOP sont déjà prévus pour éviter
    de modifier le core si une nouvelle stratégie
    les utilise dans le futur.
    """

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class MarketBias(str, Enum):
    """
    Orientation du marché ou d'une figure.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class PivotType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class ZoneType(str, Enum):
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"


class PatternFamily(str, Enum):
    """
    Famille technique d'une figure.
    """

    CLASSICAL = "CLASSICAL"
    HARMONIC = "HARMONIC"
    CANDLESTICK = "CANDLESTICK"
    STRUCTURAL = "STRUCTURAL"
    CUSTOM = "CUSTOM"


class PatternRole(str, Enum):
    """
    Fonction de la figure dans son contexte.

    On sépare le ROLE du TYPE car une figure comme
    un wedge peut agir comme continuation ou retournement
    selon le contexte.
    """

    CONTINUATION = "CONTINUATION"
    REVERSAL = "REVERSAL"
    BILATERAL = "BILATERAL"
    NEUTRAL = "NEUTRAL"


class PatternStatus(str, Enum):
    """
    Cycle de vie d'une figure.
    """

    FORMING = "FORMING"
    CONFIRMED = "CONFIRMED"
    BROKEN_OUT = "BROKEN_OUT"
    INVALIDATED = "INVALIDATED"


class PatternType(str, Enum):
    """
    Catalogue des principales figures utilisées
    en analyse technique Forex.

    CUSTOM permet d'ajouter ultérieurement une figure
    sans modifier cette architecture.
    """

    # =====================================================
    # FLAGS
    # =====================================================

    BULL_FLAG = "BULL_FLAG"
    BEAR_FLAG = "BEAR_FLAG"

    # =====================================================
    # PENNANTS
    # =====================================================

    BULL_PENNANT = "BULL_PENNANT"
    BEAR_PENNANT = "BEAR_PENNANT"

    # =====================================================
    # TRIANGLES
    # =====================================================

    ASCENDING_TRIANGLE = "ASCENDING_TRIANGLE"
    DESCENDING_TRIANGLE = "DESCENDING_TRIANGLE"
    SYMMETRICAL_TRIANGLE = "SYMMETRICAL_TRIANGLE"

    # =====================================================
    # RECTANGLES / RANGES
    # =====================================================

    BULL_RECTANGLE = "BULL_RECTANGLE"
    BEAR_RECTANGLE = "BEAR_RECTANGLE"
    HORIZONTAL_RANGE = "HORIZONTAL_RANGE"

    # =====================================================
    # CHANNELS
    # =====================================================

    RISING_CHANNEL = "RISING_CHANNEL"
    FALLING_CHANNEL = "FALLING_CHANNEL"
    HORIZONTAL_CHANNEL = "HORIZONTAL_CHANNEL"

    # =====================================================
    # WEDGES
    # =====================================================

    RISING_WEDGE = "RISING_WEDGE"
    FALLING_WEDGE = "FALLING_WEDGE"

    # =====================================================
    # CUP PATTERNS
    # =====================================================

    CUP_AND_HANDLE = "CUP_AND_HANDLE"
    INVERTED_CUP_AND_HANDLE = "INVERTED_CUP_AND_HANDLE"

    # =====================================================
    # MEASURED MOVES
    # =====================================================

    MEASURED_MOVE_UP = "MEASURED_MOVE_UP"
    MEASURED_MOVE_DOWN = "MEASURED_MOVE_DOWN"

    # =====================================================
    # DOUBLE / TRIPLE TOP & BOTTOM
    # =====================================================

    DOUBLE_TOP = "DOUBLE_TOP"
    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"

    TRIPLE_TOP = "TRIPLE_TOP"
    TRIPLE_BOTTOM = "TRIPLE_BOTTOM"

    # =====================================================
    # HEAD AND SHOULDERS
    # =====================================================

    HEAD_AND_SHOULDERS = "HEAD_AND_SHOULDERS"
    INVERSE_HEAD_AND_SHOULDERS = "INVERSE_HEAD_AND_SHOULDERS"

    # =====================================================
    # ROUNDING
    # =====================================================

    ROUNDING_TOP = "ROUNDING_TOP"
    ROUNDING_BOTTOM = "ROUNDING_BOTTOM"

    # =====================================================
    # DIAMOND
    # =====================================================

    DIAMOND_TOP = "DIAMOND_TOP"
    DIAMOND_BOTTOM = "DIAMOND_BOTTOM"

    # =====================================================
    # BROADENING / MEGAPHONE
    # =====================================================

    BROADENING_TOP = "BROADENING_TOP"
    BROADENING_BOTTOM = "BROADENING_BOTTOM"
    BROADENING_FORMATION = "BROADENING_FORMATION"

    # =====================================================
    # V PATTERNS
    # =====================================================

    V_TOP = "V_TOP"
    V_BOTTOM = "V_BOTTOM"

    # =====================================================
    # 1-2-3 PATTERNS
    # =====================================================

    ONE_TWO_THREE_TOP = "ONE_TWO_THREE_TOP"
    ONE_TWO_THREE_BOTTOM = "ONE_TWO_THREE_BOTTOM"

    # =====================================================
    # QUASIMODO
    # =====================================================

    QUASIMODO_BEARISH = "QUASIMODO_BEARISH"
    QUASIMODO_BULLISH = "QUASIMODO_BULLISH"

    # =====================================================
    # HARMONIC PATTERNS
    # =====================================================

    AB_CD_BULLISH = "AB_CD_BULLISH"
    AB_CD_BEARISH = "AB_CD_BEARISH"

    GARTLEY_BULLISH = "GARTLEY_BULLISH"
    GARTLEY_BEARISH = "GARTLEY_BEARISH"

    BAT_BULLISH = "BAT_BULLISH"
    BAT_BEARISH = "BAT_BEARISH"

    BUTTERFLY_BULLISH = "BUTTERFLY_BULLISH"
    BUTTERFLY_BEARISH = "BUTTERFLY_BEARISH"

    CRAB_BULLISH = "CRAB_BULLISH"
    CRAB_BEARISH = "CRAB_BEARISH"

    DEEP_CRAB_BULLISH = "DEEP_CRAB_BULLISH"
    DEEP_CRAB_BEARISH = "DEEP_CRAB_BEARISH"

    CYPHER_BULLISH = "CYPHER_BULLISH"
    CYPHER_BEARISH = "CYPHER_BEARISH"

    SHARK_BULLISH = "SHARK_BULLISH"
    SHARK_BEARISH = "SHARK_BEARISH"

    THREE_DRIVES_BULLISH = "THREE_DRIVES_BULLISH"
    THREE_DRIVES_BEARISH = "THREE_DRIVES_BEARISH"

    # =====================================================
    # STRUCTURES
    # =====================================================

    ELLIOTT_IMPULSE = "ELLIOTT_IMPULSE"
    ELLIOTT_ZIGZAG = "ELLIOTT_ZIGZAG"
    ELLIOTT_FLAT = "ELLIOTT_FLAT"
    ELLIOTT_TRIANGLE = "ELLIOTT_TRIANGLE"

    WOLFE_WAVE_BULLISH = "WOLFE_WAVE_BULLISH"
    WOLFE_WAVE_BEARISH = "WOLFE_WAVE_BEARISH"

    WYCKOFF_ACCUMULATION = "WYCKOFF_ACCUMULATION"
    WYCKOFF_DISTRIBUTION = "WYCKOFF_DISTRIBUTION"
    WYCKOFF_SPRING = "WYCKOFF_SPRING"
    WYCKOFF_UPTHRUST = "WYCKOFF_UPTHRUST"

    # =====================================================
    # JAPANESE CANDLESTICKS
    # Ils serviront surtout comme confirmation.
    # =====================================================

    DOJI = "DOJI"
    DRAGONFLY_DOJI = "DRAGONFLY_DOJI"
    GRAVESTONE_DOJI = "GRAVESTONE_DOJI"
    LONG_LEGGED_DOJI = "LONG_LEGGED_DOJI"

    SPINNING_TOP = "SPINNING_TOP"

    HAMMER = "HAMMER"
    INVERTED_HAMMER = "INVERTED_HAMMER"
    HANGING_MAN = "HANGING_MAN"
    SHOOTING_STAR = "SHOOTING_STAR"

    BULLISH_ENGULFING = "BULLISH_ENGULFING"
    BEARISH_ENGULFING = "BEARISH_ENGULFING"

    BULLISH_HARAMI = "BULLISH_HARAMI"
    BEARISH_HARAMI = "BEARISH_HARAMI"

    PIERCING_LINE = "PIERCING_LINE"
    DARK_CLOUD_COVER = "DARK_CLOUD_COVER"

    MORNING_STAR = "MORNING_STAR"
    EVENING_STAR = "EVENING_STAR"

    THREE_WHITE_SOLDIERS = "THREE_WHITE_SOLDIERS"
    THREE_BLACK_CROWS = "THREE_BLACK_CROWS"

    TWEEZER_TOP = "TWEEZER_TOP"
    TWEEZER_BOTTOM = "TWEEZER_BOTTOM"

    BULLISH_MARUBOZU = "BULLISH_MARUBOZU"
    BEARISH_MARUBOZU = "BEARISH_MARUBOZU"

    # Figure future inconnue aujourd'hui.
    CUSTOM = "CUSTOM"


class SignalState(str, Enum):
    """
    Cycle de vie d'un signal.
    """

    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class GuardStatus(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


class SafetyReason(str, Enum):
    """
    Codes standards expliquant pourquoi une opération
    est acceptée ou refusée.

    Ils seront réutilisés dans :
    - Risk Manager ;
    - logs ;
    - Telegram ;
    - rapports ;
    - tests.
    """

    OK = "OK"
    OTHER = "OTHER"

    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"

    BACKTEST_EXECUTION_FORBIDDEN = (
        "BACKTEST_EXECUTION_FORBIDDEN"
    )

    BROKER_NOT_ALLOWED = "BROKER_NOT_ALLOWED"
    SERVER_NOT_ALLOWED = "SERVER_NOT_ALLOWED"

    ACCOUNT_MODE_MISMATCH = "ACCOUNT_MODE_MISMATCH"

    LIVE_NOT_ARMED = "LIVE_NOT_ARMED"

    LIVE_CONFIRMATION_INVALID = (
        "LIVE_CONFIRMATION_INVALID"
    )

    LIVE_LOGIN_NOT_AUTHORIZED = (
        "LIVE_LOGIN_NOT_AUTHORIZED"
    )

    ACCOUNT_TRADING_DISABLED = (
        "ACCOUNT_TRADING_DISABLED"
    )

    EXPERT_TRADING_DISABLED = (
        "EXPERT_TRADING_DISABLED"
    )

    CONNECTION_UNHEALTHY = "CONNECTION_UNHEALTHY"

    MARKET_DATA_INVALID = "MARKET_DATA_INVALID"
    MARKET_DATA_STALE = "MARKET_DATA_STALE"

    SYMBOL_NOT_TRADABLE = "SYMBOL_NOT_TRADABLE"

    MARKET_CLOSED = "MARKET_CLOSED"

    SESSION_CUTOFF = "SESSION_CUTOFF"

    STOP_LOSS_REQUIRED = "STOP_LOSS_REQUIRED"
    INVALID_STOP_LOSS = "INVALID_STOP_LOSS"

    INVALID_VOLUME = "INVALID_VOLUME"

    INSUFFICIENT_MARGIN = "INSUFFICIENT_MARGIN"

    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"

    ORDER_RATE_LIMIT = "ORDER_RATE_LIMIT"

    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"

    SLIPPAGE_TOO_HIGH = "SLIPPAGE_TOO_HIGH"

    MAX_TRADE_RISK = "MAX_TRADE_RISK"

    MAX_TOTAL_RISK = "MAX_TOTAL_RISK"

    MAX_DAILY_LOSS = "MAX_DAILY_LOSS"

    MAX_DRAWDOWN = "MAX_DRAWDOWN"

    MAX_CURRENCY_EXPOSURE = (
        "MAX_CURRENCY_EXPOSURE"
    )

    MAX_SYMBOL_EXPOSURE = (
        "MAX_SYMBOL_EXPOSURE"
    )

    MAX_OPEN_POSITIONS = "MAX_OPEN_POSITIONS"

    MAX_POSITIONS_PER_SYMBOL = (
        "MAX_POSITIONS_PER_SYMBOL"
    )


class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditEventType(str, Enum):
    STARTUP = "STARTUP"
    SHUTDOWN = "SHUTDOWN"

    HEARTBEAT = "HEARTBEAT"

    ACCOUNT_CHECK = "ACCOUNT_CHECK"
    DATA_CHECK = "DATA_CHECK"

    PATTERN_DETECTED = "PATTERN_DETECTED"

    SIGNAL_CREATED = "SIGNAL_CREATED"
    SIGNAL_REJECTED = "SIGNAL_REJECTED"

    RISK_CHECK = "RISK_CHECK"

    ORDER_REQUESTED = "ORDER_REQUESTED"
    ORDER_EXECUTED = "ORDER_EXECUTED"
    ORDER_FAILED = "ORDER_FAILED"

    POSITION_CHANGED = "POSITION_CHANGED"

    SAFETY_BLOCK = "SAFETY_BLOCK"