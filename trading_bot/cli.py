"""
CLI entry point using Typer.
Usage examples (from the trading_bot/ directory):

  Market BUY:
    python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

  Limit SELL:
    python cli.py --symbol ETHUSDT --side SELL --order-type LIMIT --quantity 0.01 --price 3200.50
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import get_futures_client  # returns binance.client.Client (Testnet-patched)
from bot.exceptions import ClientInitError, OrderPlacementError, ValidationError
from bot.logging_config import get_logger, setup_logging
from bot.orders import place_order
from bot.validators import validate_all

# ── Initialise logging before anything else ──────────────────────────────────
setup_logging()
logger = get_logger(__name__)

app = typer.Typer(
    name="trading-bot",
    help="[bold cyan]PrimeTrade.ai[/bold cyan] — Binance Futures Testnet CLI Trading Bot",
    rich_markup_mode="rich",
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> None:
    """Print a formatted pre-order summary table."""
    table = Table(title="Order Summary", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    table.add_row("Order Type", order_type)
    table.add_row("Quantity", str(quantity))
    table.add_row("Price", str(price) if price else "MARKET (best available)")

    console.print(table)


def _print_response(response: dict) -> None:
    """Print the Binance API response in a readable table."""
    table = Table(title="Order Response", show_header=True, header_style="bold green")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    fields = [
        ("Order ID",      "orderId"),
        ("Client Order ID", "clientOrderId"),
        ("Symbol",        "symbol"),
        ("Side",          "side"),
        ("Type",          "type"),
        ("Status",        "status"),
        ("Quantity",      "origQty"),
        ("Executed Qty",  "executedQty"),
        ("Price",         "price"),
        ("Avg Price",     "avgPrice"),
        ("Time in Force", "timeInForce"),
        ("Reduce Only",   "reduceOnly"),
        ("Timestamp",     "updateTime"),
    ]

    for label, key in fields:
        value = response.get(key)
        if value is not None:
            table.add_row(label, str(value))

    console.print(table)


# ── Main command ──────────────────────────────────────────────────────────────

@app.command()
def trade(
    symbol: str = typer.Option(
        ...,
        "--symbol", "-s",
        help="Trading pair symbol, e.g. [bold]BTCUSDT[/bold], ETHUSDT.",
        metavar="SYMBOL",
    ),
    side: str = typer.Option(
        ...,
        "--side",
        help="Order direction: [bold green]BUY[/bold green] or [bold red]SELL[/bold red].",
        metavar="SIDE",
    ),
    order_type: str = typer.Option(
        ...,
        "--order-type", "-t",
        help="Order type: [bold]MARKET[/bold] or [bold]LIMIT[/bold].",
        metavar="TYPE",
    ),
    quantity: float = typer.Option(
        ...,
        "--quantity", "-q",
        help="Order quantity in base asset units (must be > 0).",
        metavar="QTY",
    ),
    price: Optional[float] = typer.Option(
        None,
        "--price", "-p",
        help="Limit price (required for LIMIT orders, ignored for MARKET).",
        metavar="PRICE",
    ),
) -> None:
    """
    [bold cyan]Place a MARKET or LIMIT order on Binance Futures Testnet.[/bold cyan]

    \b
    Examples:
      Market BUY:
        python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

      Limit SELL:
        python cli.py --symbol ETHUSDT --side SELL --order-type LIMIT --quantity 0.01 --price 3200.50
    """
    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s",
        symbol, side, order_type, quantity, price,
    )

    # ── 1. Validate inputs ───────────────────────────────────────────────────
    try:
        symbol, side, order_type, quantity, price = validate_all(
            symbol, side, order_type, quantity, price
        )
    except ValidationError as exc:
        logger.warning("Validation failed: %s", exc)
        err_console.print(
            Panel(f"[bold red]VALIDATION ERROR[/bold red]\n{exc}", border_style="red")
        )
        raise typer.Exit(code=1)

    # ── 2. Print pre-order summary ───────────────────────────────────────────
    _print_order_summary(symbol, side, order_type, quantity, price)

    # ── 3. Initialise client ─────────────────────────────────────────────────
    try:
        client = get_futures_client()
    except ClientInitError as exc:
        logger.error("Client init failed: %s", exc)
        err_console.print(
            Panel(f"[bold red]AUTHENTICATION ERROR[/bold red]\n{exc}", border_style="red")
        )
        raise typer.Exit(code=1)

    # ── 4. Place order ───────────────────────────────────────────────────────
    try:
        response = place_order(client, symbol, side, order_type, quantity, price)
    except OrderPlacementError as exc:
        logger.error("Order placement failed: %s", exc)
        err_console.print(
            Panel(f"[bold red]ORDER FAILED[/bold red]\n{exc}", border_style="red")
        )
        raise typer.Exit(code=1)

    # ── 5. Print response ────────────────────────────────────────────────────
    _print_response(response)
    console.print(
        Panel(
            f"[bold green]ORDER PLACED SUCCESSFULLY[/bold green]\n"
            f"Order ID: [cyan]{response.get('orderId')}[/cyan]  |  "
            f"Status: [yellow]{response.get('status')}[/yellow]",
            border_style="green",
        )
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
