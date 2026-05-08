"""
Input validation helpers.
All functions raise ValidationError with a human-readable message on failure.
"""

import re
from typing import Optional

from bot.config import VALID_ORDER_TYPES, VALID_SIDES
from bot.exceptions import ValidationError

# Binance symbol pattern: 1-10 uppercase letters (e.g. BTCUSDT, ETHUSDT)
_SYMBOL_RE = re.compile(r"^[A-Z]{2,20}$")


def validate_symbol(symbol: str) -> str:
    """Return the symbol uppercased, or raise ValidationError."""
    sym = symbol.strip().upper()
    if not _SYMBOL_RE.match(sym):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. "
            "Expected uppercase letters only, e.g. BTCUSDT, ETHUSDT."
        )
    return sym


def validate_side(side: str) -> str:
    """Return the side uppercased, or raise ValidationError."""
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    """Return the order type uppercased, or raise ValidationError."""
    ot = order_type.strip().upper()
    if ot not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return ot


def validate_quantity(quantity: float) -> float:
    """Ensure quantity is a strictly positive number."""
    if quantity <= 0:
        raise ValidationError(
            f"Quantity must be a positive number, got {quantity}."
        )
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    For LIMIT orders: price must be provided and positive.
    For MARKET orders: price must be None (ignored if provided).
    """
    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValidationError(
                "A --price is required for LIMIT orders. "
                "Example: --price 65000.50"
            )
        if price <= 0:
            raise ValidationError(
                f"Price must be a positive number, got {price}."
            )
        return price

    # MARKET order — price is irrelevant
    if price is not None:
        # Warn-worthy but not fatal; we simply ignore it
        pass
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> tuple[str, str, str, float, Optional[float]]:
    """
    Run all validators in sequence and return normalised values.
    Raises ValidationError on the first problem found.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    return symbol, side, order_type, quantity, price
