from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from forex_bot.core.enums import (
    AccountMode,
    EntryType,
    GuardStatus,
    RuntimeMode,
    SafetyReason,
    Timeframe,
    TradeDirection,
)

from forex_bot.core.exceptions import (
    DomainValidationError,
)

from forex_bot.core.models import (
    AccountSnapshot,
    BrokerIdentity,
    BrokerPolicy,
    Candle,
    LiveTradingGate,
    RiskLimits,
    RiskSnapshot,
    TradeSignal,
)

from forex_bot.core.safety import (
    AccountSafetyGuard,
    RiskSafetyGuard,
)


NOW = datetime(
    2026,
    8,
    21,
    12,
    0,
    tzinfo=timezone.utc,
)


def broker_policy():

    return BrokerPolicy(
        required_company_tokens=(
            "equiti",
        ),
        allowed_demo_servers=frozenset(
            {
                "Equiti-Demo",
            }
        ),
        allowed_live_servers=frozenset(
            {
                "Equiti-UAE-Live",
            }
        ),
    )


def equiti_account(
    mode,
    server,
    login=123456,
):

    return AccountSnapshot(
        login=login,
        mode=mode,
        broker=BrokerIdentity(
            company=(
                "Equiti Securities "
                "Currencies Brokers LLC"
            ),
            server=server,
        ),
        currency="USD",
        balance=Decimal("10000"),
        equity=Decimal("10000"),
        margin=Decimal("0"),
        free_margin=Decimal("10000"),
        trade_allowed=True,
        expert_trading_allowed=True,
        captured_at=NOW,
    )


def test_invalid_candle_is_rejected():

    with pytest.raises(
        DomainValidationError
    ):

        Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M15,
            open_time=NOW,

            open=1.1000,

            # Impossible :
            # le close sera supérieur au high.
            high=1.1050,

            low=1.0900,

            close=1.1100,
        )


def test_candle_is_immutable():

    candle = Candle(
        symbol="EURUSD",
        timeframe=Timeframe.M15,
        open_time=NOW,

        open=1.1000,
        high=1.1100,
        low=1.0900,
        close=1.1050,
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        candle.close = 1.2000


def test_buy_with_wrong_stop_loss_is_rejected():

    with pytest.raises(
        DomainValidationError
    ):

        TradeSignal(
            symbol="EURUSD",

            timeframe=Timeframe.M15,

            direction=TradeDirection.BUY,

            entry_type=EntryType.MARKET,

            candle_time=NOW,

            generated_at=NOW,

            entry_reference=1.1000,

            # Erreur volontaire :
            # BUY => SL doit être sous l'entrée.
            stop_loss=1.1100,

            take_profit=None,

            breakout_level=1.0990,

            strategy_name="test_strategy",

            strategy_version="1.0.0",

            reasons=(
                "Test",
            ),
        )


def test_equiti_demo_is_allowed():

    decision = (
        AccountSafetyGuard.evaluate(
            runtime_mode=RuntimeMode.DEMO,

            account=equiti_account(
                AccountMode.DEMO,
                "Equiti-Demo",
            ),

            broker_policy=broker_policy(),

            live_gate=LiveTradingGate(),
        )
    )

    assert (
        decision.status
        == GuardStatus.ALLOW
    )


def test_other_broker_is_blocked():

    account = AccountSnapshot(
        login=123456,

        mode=AccountMode.DEMO,

        broker=BrokerIdentity(
            company="Unknown Broker",
            server="Equiti-Demo",
        ),

        currency="USD",

        balance=Decimal("10000"),
        equity=Decimal("10000"),

        margin=Decimal("0"),
        free_margin=Decimal("10000"),

        trade_allowed=True,

        expert_trading_allowed=True,

        captured_at=NOW,
    )

    decision = (
        AccountSafetyGuard.evaluate(
            runtime_mode=RuntimeMode.DEMO,

            account=account,

            broker_policy=broker_policy(),

            live_gate=LiveTradingGate(),
        )
    )

    assert not decision.allowed

    assert (
        SafetyReason.BROKER_NOT_ALLOWED
        in decision.reasons
    )


def test_real_account_is_blocked_by_default():

    decision = (
        AccountSafetyGuard.evaluate(
            runtime_mode=RuntimeMode.LIVE,

            account=equiti_account(
                AccountMode.LIVE,
                "Equiti-UAE-Live",
                login=999,
            ),

            broker_policy=broker_policy(),

            # Aucun verrou LIVE activé.
            live_gate=LiveTradingGate(),
        )
    )

    assert not decision.allowed

    assert (
        SafetyReason.LIVE_NOT_ARMED
        in decision.reasons
    )


def test_real_requires_all_three_locks():

    decision = (
        AccountSafetyGuard.evaluate(
            runtime_mode=RuntimeMode.LIVE,

            account=equiti_account(
                AccountMode.LIVE,
                "Equiti-UAE-Live",
                login=999,
            ),

            broker_policy=broker_policy(),

            live_gate=LiveTradingGate(

                # Verrou 1
                allow_live_trading=True,

                # Verrou 2
                confirmation_phrase=(
                    "I_ACCEPT_REAL_MONEY_RISK"
                ),

                # Verrou 3
                authorized_live_logins=(
                    frozenset(
                        {
                            999,
                        }
                    )
                ),
            ),
        )
    )

    assert decision.allowed


def test_kill_switch_always_wins():

    decision = (
        AccountSafetyGuard.evaluate(
            runtime_mode=RuntimeMode.LIVE,

            account=equiti_account(
                AccountMode.LIVE,
                "Equiti-UAE-Live",
                login=999,
            ),

            broker_policy=broker_policy(),

            live_gate=LiveTradingGate(
                allow_live_trading=True,

                kill_switch_active=True,

                confirmation_phrase=(
                    "I_ACCEPT_REAL_MONEY_RISK"
                ),

                authorized_live_logins=(
                    frozenset(
                        {
                            999,
                        }
                    )
                ),
            ),
        )
    )

    assert not decision.allowed

    assert (
        SafetyReason.KILL_SWITCH_ACTIVE
        in decision.reasons
    )


def test_one_percent_trade_is_allowed():

    limits = RiskLimits()

    risk = RiskSnapshot(
        new_trade_risk=Decimal(
            "0.01"
        ),

        total_open_risk_after_trade=Decimal(
            "0.05"
        ),
    )

    decision = RiskSafetyGuard.evaluate(
        snapshot=risk,
        limits=limits,
    )

    assert decision.allowed


def test_more_than_one_percent_is_blocked():

    limits = RiskLimits()

    risk = RiskSnapshot(
        new_trade_risk=Decimal(
            "0.011"
        ),

        total_open_risk_after_trade=Decimal(
            "0.011"
        ),
    )

    decision = RiskSafetyGuard.evaluate(
        snapshot=risk,
        limits=limits,
    )

    assert not decision.allowed

    assert (
        SafetyReason.MAX_TRADE_RISK
        in decision.reasons
    )


def test_more_than_five_percent_total_is_blocked():

    limits = RiskLimits()

    risk = RiskSnapshot(
        new_trade_risk=Decimal(
            "0.01"
        ),

        total_open_risk_after_trade=Decimal(
            "0.051"
        ),
    )

    decision = RiskSafetyGuard.evaluate(
        snapshot=risk,
        limits=limits,
    )

    assert not decision.allowed

    assert (
        SafetyReason.MAX_TOTAL_RISK
        in decision.reasons
    )