from __future__ import annotations

from .enums import (
    AccountMode,
    GuardStatus,
    RuntimeMode,
    SafetyReason,
)

from .models import (
    AccountSnapshot,
    BrokerPolicy,
    ExecutionContext,
    ExecutionSafetyLimits,
    GuardDecision,
    LiveTradingGate,
    RiskLimits,
    RiskSnapshot,
)

from .validators import (
    normalized_casefold,
)


class AccountSafetyGuard:
    """
    Vérifie que le compte utilisé est bien
    celui autorisé.

    Cette classe ne connaît pas MT5 directement.
    Elle reçoit seulement AccountSnapshot.
    """

    @staticmethod
    def evaluate(
        *,
        runtime_mode: RuntimeMode,
        account: AccountSnapshot,
        broker_policy: BrokerPolicy,
        live_gate: LiveTradingGate,
    ) -> GuardDecision:

        reasons: list[
            SafetyReason
        ] = []

        details: list[str] = []

        # ==========================================
        # 1. KILL SWITCH
        # ==========================================

        if live_gate.kill_switch_active:

            reasons.append(
                SafetyReason
                .KILL_SWITCH_ACTIVE
            )

            details.append(
                "Kill switch actif."
            )

        company = normalized_casefold(
            account.broker.company
        )

        server = normalized_casefold(
            account.broker.server
        )

        # ==========================================
        # 2. BROKER
        # ==========================================

        # Le nom de la compagnie doit contenir
        # tous les tokens autorisés.
        if not all(
            token in company
            for token
            in broker_policy
            .required_company_tokens
        ):

            reasons.append(
                SafetyReason
                .BROKER_NOT_ALLOWED
            )

            details.append(
                "Le broker du compte "
                "n'est pas autorisé."
            )

        # ==========================================
        # 3. BACKTEST
        # ==========================================

        if runtime_mode == RuntimeMode.BACKTEST:

            reasons.append(
                SafetyReason
                .BACKTEST_EXECUTION_FORBIDDEN
            )

            details.append(
                "BACKTEST ne peut jamais "
                "envoyer d'ordre au broker."
            )

        # ==========================================
        # 4. DEMO EQUITI
        # ==========================================

        elif runtime_mode == RuntimeMode.DEMO:

            if (
                account.mode
                != AccountMode.DEMO
            ):

                reasons.append(
                    SafetyReason
                    .ACCOUNT_MODE_MISMATCH
                )

                details.append(
                    "Le programme est en DEMO "
                    "mais le compte MT5 "
                    "n'est pas DEMO."
                )

            if (
                server
                not in broker_policy
                .allowed_demo_servers
            ):

                reasons.append(
                    SafetyReason
                    .SERVER_NOT_ALLOWED
                )

                details.append(
                    f"Serveur Demo interdit : "
                    f"{account.broker.server}"
                )

        # ==========================================
        # 5. LIVE EQUITI UAE
        # ==========================================

        elif runtime_mode == RuntimeMode.LIVE:

            if (
                account.mode
                != AccountMode.LIVE
            ):

                reasons.append(
                    SafetyReason
                    .ACCOUNT_MODE_MISMATCH
                )

                details.append(
                    "Le programme est en LIVE "
                    "mais le compte MT5 "
                    "n'est pas réel."
                )

            if (
                server
                not in broker_policy
                .allowed_live_servers
            ):

                reasons.append(
                    SafetyReason
                    .SERVER_NOT_ALLOWED
                )

                details.append(
                    f"Serveur LIVE interdit : "
                    f"{account.broker.server}"
                )

            # Premier verrou.
            if not live_gate.allow_live_trading:

                reasons.append(
                    SafetyReason
                    .LIVE_NOT_ARMED
                )

                details.append(
                    "allow_live_trading=False."
                )

            # Deuxième verrou.
            if (
                live_gate.confirmation_phrase
                != live_gate
                .required_confirmation_phrase
            ):

                reasons.append(
                    SafetyReason
                    .LIVE_CONFIRMATION_INVALID
                )

                details.append(
                    "Phrase de confirmation "
                    "LIVE incorrecte."
                )

            # Troisième verrou.
            if (
                account.login
                not in live_gate
                .authorized_live_logins
            ):

                reasons.append(
                    SafetyReason
                    .LIVE_LOGIN_NOT_AUTHORIZED
                )

                details.append(
                    f"Login LIVE "
                    f"{account.login} "
                    "non autorisé."
                )

        # ==========================================
        # 6. DROITS DU COMPTE
        # ==========================================

        if not account.trade_allowed:

            reasons.append(
                SafetyReason
                .ACCOUNT_TRADING_DISABLED
            )

            details.append(
                "trade_allowed=False."
            )

        if not account.expert_trading_allowed:

            reasons.append(
                SafetyReason
                .EXPERT_TRADING_DISABLED
            )

            details.append(
                "expert_trading_allowed=False."
            )

        # ==========================================
        # RÉSULTAT
        # ==========================================

        if reasons:

            # Supprime les doublons en
            # conservant l'ordre.
            unique_reasons = tuple(
                dict.fromkeys(
                    reasons
                )
            )

            return GuardDecision(
                status=GuardStatus.BLOCK,
                reasons=unique_reasons,
                details=tuple(
                    details
                ),
            )

        return GuardDecision(
            status=GuardStatus.ALLOW,
            reasons=(
                SafetyReason.OK,
            ),
            details=(
                "Compte et broker autorisés.",
            ),
        )


class RiskSafetyGuard:
    """
    Dernière barrière indépendante du
    Risk Manager.

    Même si un futur Risk Manager contient
    un bug, ce garde vérifiera encore
    les limites finales.
    """

    @staticmethod
    def evaluate(
        *,
        snapshot: RiskSnapshot,
        limits: RiskLimits,
    ) -> GuardDecision:

        reasons: list[
            SafetyReason
        ] = []

        details: list[str] = []

        if (
            snapshot.new_trade_risk
            > limits.max_risk_per_trade
        ):

            reasons.append(
                SafetyReason
                .MAX_TRADE_RISK
            )

            details.append(
                "Risque du trade supérieur "
                "à la limite."
            )

        if (
            snapshot.total_open_risk_after_trade
            > limits.max_total_open_risk
        ):

            reasons.append(
                SafetyReason
                .MAX_TOTAL_RISK
            )

            details.append(
                "Risque total du portefeuille "
                "supérieur à la limite."
            )

        if (
            limits.max_daily_loss
            is not None
            and snapshot.daily_loss
            >= limits.max_daily_loss
        ):

            reasons.append(
                SafetyReason
                .MAX_DAILY_LOSS
            )

            details.append(
                "Limite de perte journalière "
                "atteinte."
            )

        if (
            limits.max_drawdown
            is not None
            and snapshot.drawdown
            >= limits.max_drawdown
        ):

            reasons.append(
                SafetyReason
                .MAX_DRAWDOWN
            )

            details.append(
                "Drawdown maximal atteint."
            )

        if (
            limits.max_currency_exposure
            is not None
            and
            snapshot
            .currency_exposure_after_trade
            is not None
            and
            snapshot
            .currency_exposure_after_trade
            > limits.max_currency_exposure
        ):

            reasons.append(
                SafetyReason
                .MAX_CURRENCY_EXPOSURE
            )

            details.append(
                "Exposition maximale "
                "à une devise dépassée."
            )

        if (
            limits.max_symbol_exposure
            is not None
            and
            snapshot
            .symbol_exposure_after_trade
            is not None
            and
            snapshot
            .symbol_exposure_after_trade
            > limits.max_symbol_exposure
        ):

            reasons.append(
                SafetyReason
                .MAX_SYMBOL_EXPOSURE
            )

            details.append(
                "Exposition maximale "
                "au symbole dépassée."
            )

        if (
            limits.max_open_positions
            is not None
            and
            snapshot.open_positions_after_trade
            > limits.max_open_positions
        ):

            reasons.append(
                SafetyReason
                .MAX_OPEN_POSITIONS
            )

            details.append(
                "Nombre maximal de positions "
                "ouvertes dépassé."
            )

        if (
            limits.max_positions_per_symbol
            is not None
            and
            snapshot
            .positions_on_symbol_after_trade
            > limits.max_positions_per_symbol
        ):

            reasons.append(
                SafetyReason
                .MAX_POSITIONS_PER_SYMBOL
            )

            details.append(
                "Nombre maximal de positions "
                "sur ce symbole dépassé."
            )

        if reasons:

            return GuardDecision(
                status=GuardStatus.BLOCK,
                reasons=tuple(
                    dict.fromkeys(
                        reasons
                    )
                ),
                details=tuple(
                    details
                ),
            )

        return GuardDecision(
            status=GuardStatus.ALLOW,
            reasons=(
                SafetyReason.OK,
            ),
            details=(
                "Limites de risque respectées.",
            ),
        )


class ExecutionSafetyGuard:
    """
    Protection technique juste avant
    l'exécution d'un ordre.

    Cette protection sera appelée APRES :
        stratégie
        +
        Risk Manager

    mais AVANT :
        order_send()
    """

    @staticmethod
    def evaluate(
        *,
        context: ExecutionContext,
        limits: ExecutionSafetyLimits,
    ) -> GuardDecision:

        reasons: list[
            SafetyReason
        ] = []

        details: list[str] = []

        if not context.connection_healthy:

            reasons.append(
                SafetyReason
                .CONNECTION_UNHEALTHY
            )

        if not context.market_open:

            reasons.append(
                SafetyReason
                .MARKET_CLOSED
            )

        if not context.symbol_tradable:

            reasons.append(
                SafetyReason
                .SYMBOL_NOT_TRADABLE
            )

        if (
            limits.require_stop_loss
            and not context.stop_loss_present
        ):

            reasons.append(
                SafetyReason
                .STOP_LOSS_REQUIRED
            )

        if not context.volume_valid:

            reasons.append(
                SafetyReason
                .INVALID_VOLUME
            )

        if not context.sufficient_margin:

            reasons.append(
                SafetyReason
                .INSUFFICIENT_MARGIN
            )

        if context.duplicate_signal:

            reasons.append(
                SafetyReason
                .DUPLICATE_SIGNAL
            )

        if (
            context.tick_age_seconds
            > limits.max_tick_age_seconds
        ):

            reasons.append(
                SafetyReason
                .MARKET_DATA_STALE
            )

        if (
            limits.max_candle_age_seconds
            is not None
            and
            context.candle_age_seconds
            is not None
            and
            context.candle_age_seconds
            > limits.max_candle_age_seconds
        ):

            reasons.append(
                SafetyReason
                .MARKET_DATA_STALE
            )

        if (
            limits.max_spread_points
            is not None
            and
            context.spread_points
            > limits.max_spread_points
        ):

            reasons.append(
                SafetyReason
                .SPREAD_TOO_WIDE
            )

        if (
            limits.max_slippage_points
            is not None
            and
            context.slippage_points
            is not None
            and
            context.slippage_points
            > limits.max_slippage_points
        ):

            reasons.append(
                SafetyReason
                .SLIPPAGE_TOO_HIGH
            )

        if (
            context.orders_last_minute
            >= limits.max_orders_per_minute
        ):

            reasons.append(
                SafetyReason
                .ORDER_RATE_LIMIT
            )

        if (
            context.seconds_since_last_order
            is not None
            and
            context.seconds_since_last_order
            < limits.cooldown_seconds_between_orders
        ):

            reasons.append(
                SafetyReason
                .ORDER_RATE_LIMIT
            )

        if reasons:

            return GuardDecision(
                status=GuardStatus.BLOCK,
                reasons=tuple(
                    dict.fromkeys(
                        reasons
                    )
                ),
                details=tuple(
                    reason.value
                    for reason
                    in dict.fromkeys(
                        reasons
                    )
                ),
            )

        return GuardDecision(
            status=GuardStatus.ALLOW,
            reasons=(
                SafetyReason.OK,
            ),
            details=(
                "Protections techniques validées.",
            ),
        )