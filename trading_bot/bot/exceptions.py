"""
Custom exceptions for the trading bot.
Keeps error semantics explicit and testable.
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""


class ValidationError(TradingBotError):
    """Raised when CLI input fails validation."""


class ClientInitError(TradingBotError):
    """Raised when the Binance client cannot be initialised (bad keys, network)."""


class OrderPlacementError(TradingBotError):
    """Raised when the Binance API rejects or fails to place an order."""
