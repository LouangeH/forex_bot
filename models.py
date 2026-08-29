from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
import hashlib

from .enums import (
    AccountMode,
    AuditEventType,
    AuditSeverity,
    EntryType,
    GuardStatus,
    MarketBias,
    PatternFamily,
    PatternRole,
    PatternStatus,
    PatternType,
    PivotType,
    RuntimeMode,
    SafetyReason,
    SignalState,
    Timeframe,
    TradeDirection,
    ZoneType,
)

from .exceptions import (
    DomainValidationError,
)

from .validators import (
    aware_utc,
    decimal_number,
    ensure_enum,
    finite_float,
    non_empty_text,
    non_negative_float,
    non_negative_int,
    positive_float,
    positive_int,
    ratio_0_1,
    ratio_decimal_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class Candle:
    """
    Une bougie OHLC complète.

    frozen=True :
        empêche sa modification accidentelle.

    slots=True :
        empêche l'ajout accidentel d'attributs
        inexistants et réduit la mémoire utilisée.
    """

    symbol: str
    timeframe: Timeframe

    open_time: datetime

    open: float
    high: float
    low: float
    close: float

    tick_volume: int = 0

    spread_points: int | None = None

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        ensure_enum(
            "timeframe",
            self.timeframe,
            Timeframe,
        )

        object.__setattr__(
            self,
            "open_time",
            aware_utc(
                "open_time",
                self.open_time,
            ),
        )

        for field_name in (
            "open",
            "high",
            "low",
            "close",
        ):

            object.__setattr__(
                self,
                field_name,
                positive_float(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        # HIGH doit être le prix le plus élevé
        # de la bougie.
        if self.high < max(
            self.open,
            self.close,
            self.low,
        ):
            raise DomainValidationError(
                "Bougie invalide : HIGH est "
                "inférieur à une valeur OHLC."
            )

        # LOW doit être le prix le plus bas.
        if self.low > min(
            self.open,
            self.close,
            self.high,
        ):
            raise DomainValidationError(
                "Bougie invalide : LOW est "
                "supérieur à une valeur OHLC."
            )

        non_negative_int(
            "tick_volume",
            self.tick_volume,
        )

        if self.spread_points is not None:

            non_negative_int(
                "spread_points",
                self.spread_points,
            )

    @property
    def range_size(self) -> float:

        return (
            self.high
            - self.low
        )

    @property
    def body_size(self) -> float:

        return abs(
            self.close
            - self.open
        )

    @property
    def upper_wick(self) -> float:

        return (
            self.high
            - max(
                self.open,
                self.close,
            )
        )

    @property
    def lower_wick(self) -> float:

        return (
            min(
                self.open,
                self.close,
            )
            - self.low
        )

    @property
    def is_bullish(self) -> bool:

        return (
            self.close
            > self.open
        )

    @property
    def is_bearish(self) -> bool:

        return (
            self.close
            < self.open
        )


@dataclass(
    frozen=True,
    slots=True,
)
class Tick:
    """
    Dernier prix Bid/Ask.
    """

    symbol: str
    timestamp: datetime

    bid: float
    ask: float

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        object.__setattr__(
            self,
            "timestamp",
            aware_utc(
                "timestamp",
                self.timestamp,
            ),
        )

        object.__setattr__(
            self,
            "bid",
            positive_float(
                "bid",
                self.bid,
            ),
        )

        object.__setattr__(
            self,
            "ask",
            positive_float(
                "ask",
                self.ask,
            ),
        )

        if self.ask < self.bid:

            raise DomainValidationError(
                "Tick invalide : "
                "ASK ne peut pas être < BID."
            )

    @property
    def spread_price(self) -> float:

        return (
            self.ask
            - self.bid
        )


@dataclass(
    frozen=True,
    slots=True,
)
class SymbolSpec:
    """
    Spécifications réelles d'un instrument
    fournies par Equiti/MT5.

    Le Risk Manager utilisera ces informations
    au lieu d'inventer une valeur de pip.
    """

    symbol: str

    digits: int

    point: float
    tick_size: float
    tick_value: float

    volume_min: float
    volume_max: float
    volume_step: float

    trade_enabled: bool = True

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        non_negative_int(
            "digits",
            self.digits,
        )

        for field_name in (
            "point",
            "tick_size",
            "tick_value",
            "volume_min",
            "volume_max",
            "volume_step",
        ):

            object.__setattr__(
                self,
                field_name,
                positive_float(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        if (
            self.volume_min
            > self.volume_max
        ):
            raise DomainValidationError(
                "volume_min ne peut pas "
                "dépasser volume_max."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class BrokerIdentity:
    """
    Identité du broker observée depuis MT5.
    """

    company: str
    server: str

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "company",
            non_empty_text(
                "company",
                self.company,
            ),
        )

        object.__setattr__(
            self,
            "server",
            non_empty_text(
                "server",
                self.server,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class AccountSnapshot:
    """
    Photographie du compte MT5.

    Aucun password n'est stocké ici.
    """

    login: int

    mode: AccountMode

    broker: BrokerIdentity

    currency: str

    balance: Decimal
    equity: Decimal

    margin: Decimal
    free_margin: Decimal

    trade_allowed: bool

    expert_trading_allowed: bool

    captured_at: datetime

    def __post_init__(self) -> None:

        positive_int(
            "login",
            self.login,
        )

        ensure_enum(
            "mode",
            self.mode,
            AccountMode,
        )

        if not isinstance(
            self.broker,
            BrokerIdentity,
        ):
            raise DomainValidationError(
                "broker doit être BrokerIdentity."
            )

        object.__setattr__(
            self,
            "currency",
            non_empty_text(
                "currency",
                self.currency,
            ),
        )

        object.__setattr__(
            self,
            "captured_at",
            aware_utc(
                "captured_at",
                self.captured_at,
            ),
        )

        for field_name in (
            "balance",
            "equity",
            "margin",
            "free_margin",
        ):

            object.__setattr__(
                self,
                field_name,
                decimal_number(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        if self.margin < 0:

            raise DomainValidationError(
                "margin ne peut pas "
                "être négative."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class BrokerPolicy:
    """
    Allowlist stricte des brokers.

    Pour notre projet :
        required_company_tokens=("equiti",)

    Les noms exacts des serveurs Equiti seront
    fournis par la configuration.

    Cela permet de changer de compte Equiti
    sans modifier cette classe.
    """

    required_company_tokens: tuple[str, ...]

    allowed_demo_servers: frozenset[str]

    allowed_live_servers: frozenset[str]

    def __post_init__(self) -> None:

        if not self.required_company_tokens:

            raise DomainValidationError(
                "required_company_tokens "
                "ne peut pas être vide."
            )

        tokens = tuple(
            non_empty_text(
                "company_token",
                token,
            ).casefold()
            for token
            in self.required_company_tokens
        )

        object.__setattr__(
            self,
            "required_company_tokens",
            tokens,
        )

        demo_servers = frozenset(
            non_empty_text(
                "demo_server",
                server,
            ).casefold()
            for server
            in self.allowed_demo_servers
        )

        live_servers = frozenset(
            non_empty_text(
                "live_server",
                server,
            ).casefold()
            for server
            in self.allowed_live_servers
        )

        object.__setattr__(
            self,
            "allowed_demo_servers",
            demo_servers,
        )

        object.__setattr__(
            self,
            "allowed_live_servers",
            live_servers,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LiveTradingGate:
    """
    Triple verrouillage du compte réel.

    Le LIVE exige simultanément :

    1. allow_live_trading=True
    2. phrase volontaire correcte
    3. login autorisé

    Et le kill switch reste prioritaire.
    """

    allow_live_trading: bool = False

    kill_switch_active: bool = False

    confirmation_phrase: str = ""

    required_confirmation_phrase: str = (
        "I_ACCEPT_REAL_MONEY_RISK"
    )

    authorized_live_logins: frozenset[int] = (
        frozenset()
    )

    def __post_init__(self) -> None:

        required = non_empty_text(
            "required_confirmation_phrase",
            self.required_confirmation_phrase,
        )

        object.__setattr__(
            self,
            "required_confirmation_phrase",
            required,
        )

        for login in (
            self.authorized_live_logins
        ):

            positive_int(
                "authorized_live_login",
                login,
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RiskLimits:
    """
    Contrat commun de tous les futurs
    Risk Managers.

    Règles déjà validées :
        1 % par trade.
        5 % total.

    Les autres protections sont déjà prévues
    mais restent configurables.
    """

    max_risk_per_trade: Decimal = (
        Decimal("0.01")
    )

    max_total_open_risk: Decimal = (
        Decimal("0.05")
    )

    max_daily_loss: Decimal | None = None

    max_drawdown: Decimal | None = None

    max_currency_exposure: (
        Decimal | None
    ) = None

    max_symbol_exposure: (
        Decimal | None
    ) = None

    max_open_positions: int | None = None

    max_positions_per_symbol: (
        int | None
    ) = None

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "max_risk_per_trade",
            ratio_decimal_0_1(
                "max_risk_per_trade",
                self.max_risk_per_trade,
                allow_zero=False,
            ),
        )

        object.__setattr__(
            self,
            "max_total_open_risk",
            ratio_decimal_0_1(
                "max_total_open_risk",
                self.max_total_open_risk,
                allow_zero=False,
            ),
        )

        if (
            self.max_risk_per_trade
            > self.max_total_open_risk
        ):
            raise DomainValidationError(
                "Le risque d'un seul trade "
                "ne peut pas dépasser "
                "le risque total."
            )

        ratio_fields = (
            "max_daily_loss",
            "max_drawdown",
            "max_currency_exposure",
            "max_symbol_exposure",
        )

        for field_name in ratio_fields:

            value = getattr(
                self,
                field_name,
            )

            if value is not None:

                object.__setattr__(
                    self,
                    field_name,
                    ratio_decimal_0_1(
                        field_name,
                        value,
                        allow_zero=False,
                    ),
                )

        count_fields = (
            "max_open_positions",
            "max_positions_per_symbol",
        )

        for field_name in count_fields:

            value = getattr(
                self,
                field_name,
            )

            if value is not None:

                positive_int(
                    field_name,
                    value,
                )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionSafetyLimits:
    """
    Protections techniques indépendantes
    de la stratégie.
    """

    require_stop_loss: bool = True

    max_spread_points: int | None = None

    max_slippage_points: int | None = None

    max_tick_age_seconds: int = 10

    max_candle_age_seconds: (
        int | None
    ) = None

    max_orders_per_minute: int = 10

    cooldown_seconds_between_orders: int = 1

    def __post_init__(self) -> None:

        optional_counts = (
            "max_spread_points",
            "max_slippage_points",
            "max_candle_age_seconds",
        )

        for field_name in optional_counts:

            value = getattr(
                self,
                field_name,
            )

            if value is not None:

                non_negative_int(
                    field_name,
                    value,
                )

        positive_int(
            "max_tick_age_seconds",
            self.max_tick_age_seconds,
        )

        positive_int(
            "max_orders_per_minute",
            self.max_orders_per_minute,
        )

        non_negative_int(
            "cooldown_seconds_between_orders",
            self.cooldown_seconds_between_orders,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class SessionRules:
    """
    Règles horaires de notre stratégie.
    """

    timezone_name: str = "Europe/Paris"

    no_new_entries_after: time = time(
        18,
        0,
    )

    friday_break_even_if_profitable: bool = True

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "timezone_name",
            non_empty_text(
                "timezone_name",
                self.timezone_name,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class Pivot:
    """
    Pivot High ou Pivot Low.
    """

    symbol: str
    timeframe: Timeframe

    pivot_type: PivotType

    candle_index: int

    time: datetime

    price: float

    strength: int

    prominence: float = 0.0

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        ensure_enum(
            "timeframe",
            self.timeframe,
            Timeframe,
        )

        ensure_enum(
            "pivot_type",
            self.pivot_type,
            PivotType,
        )

        non_negative_int(
            "candle_index",
            self.candle_index,
        )

        object.__setattr__(
            self,
            "time",
            aware_utc(
                "time",
                self.time,
            ),
        )

        object.__setattr__(
            self,
            "price",
            positive_float(
                "price",
                self.price,
            ),
        )

        positive_int(
            "strength",
            self.strength,
        )

        object.__setattr__(
            self,
            "prominence",
            non_negative_float(
                "prominence",
                self.prominence,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LinearBoundary:
    """
    Droite mathématique :

        y = slope*x + intercept

    Utilisée pour :
    - triangles ;
    - flags ;
    - wedges ;
    - channels ;
    - pennants.
    """

    slope: float

    intercept: float

    r_squared: float

    touches: int

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "slope",
            finite_float(
                "slope",
                self.slope,
            ),
        )

        object.__setattr__(
            self,
            "intercept",
            finite_float(
                "intercept",
                self.intercept,
            ),
        )

        object.__setattr__(
            self,
            "r_squared",
            ratio_0_1(
                "r_squared",
                self.r_squared,
            ),
        )

        if self.touches < 2:

            raise DomainValidationError(
                "Une droite technique doit "
                "avoir au moins 2 contacts."
            )

    def value_at(
        self,
        candle_index: int,
    ) -> float:
        """
        Calcule la valeur théorique
        de la droite à l'index demandé.
        """

        non_negative_int(
            "candle_index",
            candle_index,
        )

        return (
            self.slope
            * candle_index
            + self.intercept
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PriceZone:
    """
    Zone de Support ou Résistance.

    Une zone est préférable à un prix exact.
    """

    symbol: str
    timeframe: Timeframe

    zone_type: ZoneType

    lower_price: float
    upper_price: float

    touches: int

    first_seen: datetime
    last_seen: datetime

    quality: float

    pivot_indexes: tuple[int, ...] = ()

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        ensure_enum(
            "timeframe",
            self.timeframe,
            Timeframe,
        )

        ensure_enum(
            "zone_type",
            self.zone_type,
            ZoneType,
        )

        object.__setattr__(
            self,
            "lower_price",
            positive_float(
                "lower_price",
                self.lower_price,
            ),
        )

        object.__setattr__(
            self,
            "upper_price",
            positive_float(
                "upper_price",
                self.upper_price,
            ),
        )

        if (
            self.lower_price
            > self.upper_price
        ):
            raise DomainValidationError(
                "lower_price ne peut pas "
                "dépasser upper_price."
            )

        positive_int(
            "touches",
            self.touches,
        )

        object.__setattr__(
            self,
            "first_seen",
            aware_utc(
                "first_seen",
                self.first_seen,
            ),
        )

        object.__setattr__(
            self,
            "last_seen",
            aware_utc(
                "last_seen",
                self.last_seen,
            ),
        )

        if (
            self.last_seen
            < self.first_seen
        ):
            raise DomainValidationError(
                "last_seen ne peut pas "
                "précéder first_seen."
            )

        object.__setattr__(
            self,
            "quality",
            ratio_0_1(
                "quality",
                self.quality,
            ),
        )

        for index in self.pivot_indexes:

            non_negative_int(
                "pivot_index",
                index,
            )

        if (
            len(
                set(
                    self.pivot_indexes
                )
            )
            != len(
                self.pivot_indexes
            )
        ):
            raise DomainValidationError(
                "pivot_indexes contient "
                "des doublons."
            )

    @property
    def midpoint(self) -> float:

        return (
            self.lower_price
            + self.upper_price
        ) / 2

    @property
    def width(self) -> float:

        return (
            self.upper_price
            - self.lower_price
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PatternMetric:
    """
    Une mesure utilisée pour démontrer
    mathématiquement pourquoi une figure
    a été reconnue.

    Exemples :
    - retracement_ratio ;
    - resistance_slope ;
    - convergence_ratio ;
    - pole_height ;
    - fibonacci_ratio.
    """

    name: str
    value: float

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "name",
            non_empty_text(
                "metric_name",
                self.name,
            ),
        )

        object.__setattr__(
            self,
            "value",
            finite_float(
                "metric_value",
                self.value,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PatternMatch:
    """
    Figure reconnue par un détecteur.

    ATTENTION :
    PatternMatch != TradeSignal.
    """

    symbol: str
    timeframe: Timeframe

    pattern_type: PatternType

    family: PatternFamily
    role: PatternRole

    status: PatternStatus

    bias: MarketBias

    start_time: datetime
    end_time: datetime

    start_index: int
    end_index: int

    confidence: float

    detector_name: str
    detector_version: str

    upper_boundary: (
        LinearBoundary | None
    ) = None

    lower_boundary: (
        LinearBoundary | None
    ) = None

    breakout_level: (
        float | None
    ) = None

    metrics: tuple[
        PatternMetric,
        ...
    ] = ()

    source_pivot_indexes: tuple[
        int,
        ...
    ] = ()

    custom_name: str | None = None

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        ensure_enum(
            "timeframe",
            self.timeframe,
            Timeframe,
        )

        ensure_enum(
            "pattern_type",
            self.pattern_type,
            PatternType,
        )

        ensure_enum(
            "family",
            self.family,
            PatternFamily,
        )

        ensure_enum(
            "role",
            self.role,
            PatternRole,
        )

        ensure_enum(
            "status",
            self.status,
            PatternStatus,
        )

        ensure_enum(
            "bias",
            self.bias,
            MarketBias,
        )

        object.__setattr__(
            self,
            "start_time",
            aware_utc(
                "start_time",
                self.start_time,
            ),
        )

        object.__setattr__(
            self,
            "end_time",
            aware_utc(
                "end_time",
                self.end_time,
            ),
        )

        if (
            self.end_time
            < self.start_time
        ):
            raise DomainValidationError(
                "end_time ne peut pas "
                "précéder start_time."
            )

        non_negative_int(
            "start_index",
            self.start_index,
        )

        if (
            self.end_index
            < self.start_index
        ):
            raise DomainValidationError(
                "end_index doit être "
                ">= start_index."
            )

        object.__setattr__(
            self,
            "confidence",
            ratio_0_1(
                "confidence",
                self.confidence,
            ),
        )

        object.__setattr__(
            self,
            "detector_name",
            non_empty_text(
                "detector_name",
                self.detector_name,
            ),
        )

        object.__setattr__(
            self,
            "detector_version",
            non_empty_text(
                "detector_version",
                self.detector_version,
            ),
        )

        if (
            self.breakout_level
            is not None
        ):

            object.__setattr__(
                self,
                "breakout_level",
                positive_float(
                    "breakout_level",
                    self.breakout_level,
                ),
            )

        metric_names = [
            metric.name
            for metric
            in self.metrics
        ]

        if (
            len(metric_names)
            != len(set(metric_names))
        ):
            raise DomainValidationError(
                "Une figure contient "
                "des métriques dupliquées."
            )

        for index in (
            self.source_pivot_indexes
        ):

            non_negative_int(
                "source_pivot_index",
                index,
            )

        if (
            len(
                set(
                    self.source_pivot_indexes
                )
            )
            != len(
                self.source_pivot_indexes
            )
        ):
            raise DomainValidationError(
                "source_pivot_indexes contient "
                "des doublons."
            )

        # CUSTOM nous permet d'ajouter plus tard
        # une figure inconnue aujourd'hui sans
        # modifier le core.
        if (
            self.pattern_type
            == PatternType.CUSTOM
        ):

            if self.custom_name is None:

                raise DomainValidationError(
                    "custom_name est obligatoire "
                    "pour PatternType.CUSTOM."
                )

            object.__setattr__(
                self,
                "custom_name",
                non_empty_text(
                    "custom_name",
                    self.custom_name,
                ),
            )

        elif self.custom_name is not None:

            raise DomainValidationError(
                "custom_name est réservé "
                "à PatternType.CUSTOM."
            )

    @property
    def pattern_name(self) -> str:

        if self.custom_name:

            return self.custom_name

        return self.pattern_type.value

    @property
    def pattern_id(self) -> str:
        """
        Empreinte déterministe de la figure.

        Même figure + même période +
        même détecteur = même ID.
        """

        raw = (
            f"{self.symbol}|"
            f"{self.timeframe.value}|"
            f"{self.pattern_name}|"
            f"{self.start_time.isoformat()}|"
            f"{self.end_time.isoformat()}|"
            f"{self.start_index}|"
            f"{self.end_index}|"
            f"{self.detector_name}|"
            f"{self.detector_version}"
        )

        return hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

    def metric(
        self,
        name: str,
    ) -> float | None:

        for metric in self.metrics:

            if metric.name == name:

                return metric.value

        return None


@dataclass(
    frozen=True,
    slots=True,
)
class TradeSignal:
    """
    Signal proposé par une stratégie.

    Il ne contient PAS encore :
    - volume ;
    - lot ;
    - autorisation de risque.

    Le Risk Manager viendra après.
    """

    symbol: str
    timeframe: Timeframe

    direction: TradeDirection

    entry_type: EntryType

    candle_time: datetime

    generated_at: datetime

    entry_reference: float

    stop_loss: float

    take_profit: float | None

    breakout_level: float | None

    strategy_name: str

    strategy_version: str

    reasons: tuple[str, ...]

    pattern_ids: tuple[str, ...] = ()

    state: SignalState = (
        SignalState.PROPOSED
    )

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "symbol",
            non_empty_text(
                "symbol",
                self.symbol,
            ),
        )

        ensure_enum(
            "timeframe",
            self.timeframe,
            Timeframe,
        )

        ensure_enum(
            "direction",
            self.direction,
            TradeDirection,
        )

        ensure_enum(
            "entry_type",
            self.entry_type,
            EntryType,
        )

        ensure_enum(
            "state",
            self.state,
            SignalState,
        )

        object.__setattr__(
            self,
            "candle_time",
            aware_utc(
                "candle_time",
                self.candle_time,
            ),
        )

        object.__setattr__(
            self,
            "generated_at",
            aware_utc(
                "generated_at",
                self.generated_at,
            ),
        )

        object.__setattr__(
            self,
            "entry_reference",
            positive_float(
                "entry_reference",
                self.entry_reference,
            ),
        )

        object.__setattr__(
            self,
            "stop_loss",
            positive_float(
                "stop_loss",
                self.stop_loss,
            ),
        )

        if self.take_profit is not None:

            object.__setattr__(
                self,
                "take_profit",
                positive_float(
                    "take_profit",
                    self.take_profit,
                ),
            )

        if self.breakout_level is not None:

            object.__setattr__(
                self,
                "breakout_level",
                positive_float(
                    "breakout_level",
                    self.breakout_level,
                ),
            )

        object.__setattr__(
            self,
            "strategy_name",
            non_empty_text(
                "strategy_name",
                self.strategy_name,
            ),
        )

        object.__setattr__(
            self,
            "strategy_version",
            non_empty_text(
                "strategy_version",
                self.strategy_version,
            ),
        )

        # Protection fondamentale du SL.
        if (
            self.direction
            == TradeDirection.BUY
        ):

            if (
                self.stop_loss
                >= self.entry_reference
            ):

                raise DomainValidationError(
                    "Pour BUY, le Stop Loss "
                    "doit être sous l'entrée."
                )

            if (
                self.take_profit is not None
                and self.take_profit
                <= self.entry_reference
            ):

                raise DomainValidationError(
                    "Pour BUY, le Take Profit "
                    "doit être au-dessus "
                    "de l'entrée."
                )

        if (
            self.direction
            == TradeDirection.SELL
        ):

            if (
                self.stop_loss
                <= self.entry_reference
            ):

                raise DomainValidationError(
                    "Pour SELL, le Stop Loss "
                    "doit être au-dessus "
                    "de l'entrée."
                )

            if (
                self.take_profit is not None
                and self.take_profit
                >= self.entry_reference
            ):

                raise DomainValidationError(
                    "Pour SELL, le Take Profit "
                    "doit être sous l'entrée."
                )

        if not self.reasons:

            raise DomainValidationError(
                "Un signal doit expliquer "
                "pourquoi il existe."
            )

        clean_reasons = tuple(
            non_empty_text(
                "reason",
                reason,
            )
            for reason
            in self.reasons
        )

        object.__setattr__(
            self,
            "reasons",
            clean_reasons,
        )

        if (
            len(set(self.pattern_ids))
            != len(self.pattern_ids)
        ):

            raise DomainValidationError(
                "pattern_ids contient "
                "des doublons."
            )

    @property
    def signal_id(self) -> str:
        """
        Identifiant anti-doublon.

        On n'utilise pas le prix Bid/Ask instantané
        car il change à chaque tick.

        Ainsi le même signal M15 reste le même signal.
        """

        breakout = (
            "NONE"
            if self.breakout_level is None
            else f"{self.breakout_level:.10f}"
        )

        raw = (
            f"{self.symbol}|"
            f"{self.timeframe.value}|"
            f"{self.candle_time.isoformat()}|"
            f"{self.direction.value}|"
            f"{self.entry_type.value}|"
            f"{breakout}|"
            f"{self.strategy_name}|"
            f"{self.strategy_version}|"
            f"{','.join(sorted(self.pattern_ids))}"
        )

        return hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class RiskSnapshot:
    """
    Résumé des risques calculés avant
    l'ouverture d'un trade.

    Les champs sont des RATIOS.

    Exemple :
        new_trade_risk = 0.01
        signifie 1 %.
    """

    new_trade_risk: Decimal

    total_open_risk_after_trade: Decimal

    daily_loss: Decimal = Decimal("0")

    drawdown: Decimal = Decimal("0")

    currency_exposure_after_trade: (
        Decimal | None
    ) = None

    symbol_exposure_after_trade: (
        Decimal | None
    ) = None

    open_positions_after_trade: int = 1

    positions_on_symbol_after_trade: int = 1

    def __post_init__(self) -> None:

        ratio_fields = (
            "new_trade_risk",
            "total_open_risk_after_trade",
            "daily_loss",
            "drawdown",
        )

        for field_name in ratio_fields:

            object.__setattr__(
                self,
                field_name,
                ratio_decimal_0_1(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        optional_fields = (
            "currency_exposure_after_trade",
            "symbol_exposure_after_trade",
        )

        for field_name in optional_fields:

            value = getattr(
                self,
                field_name,
            )

            if value is not None:

                object.__setattr__(
                    self,
                    field_name,
                    ratio_decimal_0_1(
                        field_name,
                        value,
                    ),
                )

        non_negative_int(
            "open_positions_after_trade",
            self.open_positions_after_trade,
        )

        non_negative_int(
            "positions_on_symbol_after_trade",
            self.positions_on_symbol_after_trade,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionContext:
    """
    Informations techniques nécessaires
    pour décider si l'exécution est sûre.
    """

    connection_healthy: bool

    market_open: bool

    symbol_tradable: bool

    stop_loss_present: bool

    volume_valid: bool

    sufficient_margin: bool

    duplicate_signal: bool

    tick_age_seconds: int

    candle_age_seconds: int | None

    spread_points: int

    slippage_points: int | None

    orders_last_minute: int

    seconds_since_last_order: int | None

    def __post_init__(self) -> None:

        non_negative_int(
            "tick_age_seconds",
            self.tick_age_seconds,
        )

        non_negative_int(
            "spread_points",
            self.spread_points,
        )

        non_negative_int(
            "orders_last_minute",
            self.orders_last_minute,
        )

        optional_fields = (
            "candle_age_seconds",
            "slippage_points",
            "seconds_since_last_order",
        )

        for field_name in optional_fields:

            value = getattr(
                self,
                field_name,
            )

            if value is not None:

                non_negative_int(
                    field_name,
                    value,
                )


@dataclass(
    frozen=True,
    slots=True,
)
class GuardDecision:
    """
    Résultat standard d'une protection.
    """

    status: GuardStatus

    reasons: tuple[
        SafetyReason,
        ...
    ]

    details: tuple[str, ...] = ()

    def __post_init__(self) -> None:

        ensure_enum(
            "status",
            self.status,
            GuardStatus,
        )

        if not self.reasons:

            raise DomainValidationError(
                "GuardDecision doit contenir "
                "au moins une raison."
            )

        for reason in self.reasons:

            ensure_enum(
                "reason",
                reason,
                SafetyReason,
            )

        if (
            self.status
            == GuardStatus.ALLOW
        ):

            if self.reasons != (
                SafetyReason.OK,
            ):

                raise DomainValidationError(
                    "ALLOW doit contenir "
                    "uniquement SafetyReason.OK."
                )

        if (
            self.status
            == GuardStatus.BLOCK
        ):

            if SafetyReason.OK in self.reasons:

                raise DomainValidationError(
                    "BLOCK ne peut pas "
                    "contenir SafetyReason.OK."
                )

    @property
    def allowed(self) -> bool:

        return (
            self.status
            == GuardStatus.ALLOW
        )


@dataclass(
    frozen=True,
    slots=True,
)
class AuditEvent:
    """
    Événement destiné au journal d'audit.

    Un jour nous pourrons reconstruire :
    - pourquoi un trade a été ouvert ;
    - pourquoi un trade a été refusé ;
    - quelle stratégie l'a généré ;
    - quelle protection est intervenue.
    """

    timestamp: datetime

    event_type: AuditEventType

    severity: AuditSeverity

    message: str

    correlation_id: str | None = None

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "timestamp",
            aware_utc(
                "timestamp",
                self.timestamp,
            ),
        )

        ensure_enum(
            "event_type",
            self.event_type,
            AuditEventType,
        )

        ensure_enum(
            "severity",
            self.severity,
            AuditSeverity,
        )

        object.__setattr__(
            self,
            "message",
            non_empty_text(
                "message",
                self.message,
            ),
        )

        if self.correlation_id is not None:

            object.__setattr__(
                self,
                "correlation_id",
                non_empty_text(
                    "correlation_id",
                    self.correlation_id,
                ),
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeProfile:
    """
    Configuration métier globale.

    Elle sera créée au démarrage puis injectée
    dans les différents services.

    Une stratégie n'ira jamais lire directement
    des variables globales ou le fichier .env.
    """

    mode: RuntimeMode

    broker_policy: BrokerPolicy

    live_gate: LiveTradingGate

    risk_limits: RiskLimits = RiskLimits()

    execution_limits: (
        ExecutionSafetyLimits
    ) = ExecutionSafetyLimits()

    session_rules: (
        SessionRules
    ) = SessionRules()

    def __post_init__(self) -> None:

        ensure_enum(
            "mode",
            self.mode,
            RuntimeMode,
        )