"""
Order placement logic.
Uses python-binance Client.futures_create_order() which maps to
POST /fapi/v1/order on the configured Futures URL.
"""

from typing import Any, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.exceptions import OrderPlacementError
from bot.logging_config import get_logger

logger = get_logger(__name__)


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> dict[str, Any]:
    """Build the keyword-argument dict for futures_create_order()."""
    params: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"   # Good Till Cancelled — standard default
    return params


def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict[str, Any]:
    """
    Place a MARKET or LIMIT order on Binance Futures Testnet.

    Args:
        client:     Configured Binance Client (Futures Testnet URL set).
        symbol:     Trading pair, e.g. "BTCUSDT".
        side:       "BUY" or "SELL".
        order_type: "MARKET" or "LIMIT".
        quantity:   Order size in base asset units.
        price:      Required for LIMIT orders; None for MARKET.

    Returns:
        Raw API response dict from Binance.

    Raises:
        OrderPlacementError: on any API / network failure.
    """
    params = _build_order_params(symbol, side, order_type, quantity, price)

    logger.info(
        "Placing %s %s order | symbol=%s | qty=%s%s",
        side,
        order_type,
        symbol,
        quantity,
        f" | price={price}" if price else "",
    )
    logger.debug("Full order params: %s", params)

    try:
        response: dict[str, Any] = client.futures_create_order(**params)
        logger.info(
            "Order placed successfully | orderId=%s | status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        logger.debug("Full API response: %s", response)
        return response

    except BinanceAPIException as exc:
        # 4xx / 5xx API errors — invalid symbol, auth failure, bad params, etc.
        logger.error(
            "BinanceAPIException [%s]: %s",
            exc.status_code,
            exc.message,
        )
        raise OrderPlacementError(
            f"Binance API error (HTTP {exc.status_code}): {exc.message}"
        ) from exc

    except BinanceRequestException as exc:
        # Network-level failures (timeout, SSL, DNS, etc.)
        logger.error("BinanceRequestException: %s", exc.message)
        raise OrderPlacementError(
            f"Network error communicating with Binance: {exc.message}"
        ) from exc

    except Exception as exc:
        logger.error("Unexpected error while placing order: %s", exc)
        raise OrderPlacementError(f"Unexpected error: {exc}") from exc
