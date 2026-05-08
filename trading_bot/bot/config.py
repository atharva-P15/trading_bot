"""
Centralised configuration loaded from environment variables.
Reads the .env file automatically via python-dotenv.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from bot.exceptions import ClientInitError

# Load .env from project root (parent of bot/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# ── Binance Futures Testnet ──────────────────────────────────────────────────
BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")

# Base URL for USDT-M Futures Testnet
FUTURES_TESTNET_BASE_URL: str = "https://testnet.binancefuture.com"

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE: Path = LOG_DIR / "trading_bot.log"
LOG_MAX_BYTES: int = 5 * 1024 * 1024   # 5 MB per file
LOG_BACKUP_COUNT: int = 3

# ── Trading constants ────────────────────────────────────────────────────────
VALID_SIDES: tuple[str, ...] = ("BUY", "SELL")
VALID_ORDER_TYPES: tuple[str, ...] = ("MARKET", "LIMIT")


def validate_credentials() -> None:
    """Raise ClientInitError if API keys are missing."""
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise ClientInitError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file. "
            "Copy .env.example → .env and fill in your Testnet keys."
        )
