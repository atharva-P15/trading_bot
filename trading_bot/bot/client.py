"""
Binance Futures Testnet client factory.
python-binance 1.0.x exposes futures through binance.client.Client;
we override the FUTURES_URL to point at the USDT-M Testnet.
"""

from binance.client import Client

from bot.config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    FUTURES_TESTNET_BASE_URL,
    validate_credentials,
)
from bot.exceptions import ClientInitError
from bot.logging_config import get_logger

logger = get_logger(__name__)

# python-binance constructs futures URLs as: base + "/fapi/v1/..."
# The Testnet FAPI root is https://testnet.binancefuture.com/fapi
_FUTURES_FAPI_URL = f"{FUTURES_TESTNET_BASE_URL}/fapi"


def get_futures_client() -> Client:
    """
    Build and return a Binance Client configured for USDT-M Futures Testnet.

    Raises:
        ClientInitError: if credentials are missing or client init fails.
    """
    validate_credentials()

    try:
        client = Client(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
        )
        # Override the futures base URL to target Testnet
        client.FUTURES_URL = _FUTURES_FAPI_URL
        logger.debug("Binance Client initialised → Futures Testnet: %s", _FUTURES_FAPI_URL)
        return client

    except Exception as exc:
        logger.error("Failed to create Binance client: %s", exc)
        raise ClientInitError(f"Could not initialise Binance client: {exc}") from exc
