# PrimeTrade.ai - Binance Futures Testnet Trading Bot

A Python CLI trading bot for **Binance USDT-M Futures Testnet**.
Place `MARKET` and `LIMIT` orders from the command line with clean validation,
structured logging, and rich terminal output.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup (Windows PowerShell)](#setup-windows-powershell)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Usage Examples](#usage-examples)
- [Sample Output](#sample-output)
- [Logging](#logging)
- [Assumptions](#assumptions)
- [Tech Stack](#tech-stack)

---

## Project Overview

This bot connects to the [Binance Futures Testnet](https://testnet.binancefuture.com)
and lets you place orders entirely from the terminal.

| Feature | Detail |
|---|---|
| Order types | `MARKET`, `LIMIT` |
| Sides | `BUY`, `SELL` |
| Market | USDT-M Futures Testnet |
| Auth | `.env` — never hard-coded |
| Logging | Rotating file + coloured console |
| CLI UX | Typer + Rich (coloured tables, panels) |

---

## Project Structure

```
trading_bot/
│
├── bot/                    # Core library package
│   ├── __init__.py
│   ├── client.py           # Binance UMFutures client factory
│   ├── config.py           # Env-var configuration & constants
│   ├── exceptions.py       # Custom exception hierarchy
│   ├── logging_config.py   # Rotating file + console logging
│   ├── orders.py           # Order placement logic
│   └── validators.py       # All input validation
│
├── logs/
│   └── trading_bot.log     # Runtime log (auto-created, rotates at 5 MB)
│
├── sample_logs/
│   ├── market_order.log    # Example log — MARKET BUY
│   └── limit_order.log     # Example log — LIMIT SELL
│
├── cli.py                  # Typer CLI entry point
├── requirements.txt
├── .env.example            # API key template
├── .gitignore
└── README.md
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11 or later |
| pip | bundled with Python |
| Git | any recent version |

---

## Setup (Windows PowerShell)

### 1 — Clone the repository

```powershell
git clone https://github.com/your-username/trading-bot.git
cd trading-bot\trading_bot
```

### 2 — Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you see an execution-policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then re-run the activate command.

### 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Configuration

### 4 — Get your Testnet API keys

1. Go to <https://testnet.binancefuture.com>
2. Log in (create an account if needed — it's free and uses test funds).
3. Navigate to **API Management** → **Create API**.
4. Copy your **API Key** and **Secret Key**.

### 5 — Create your `.env` file

```powershell
Copy-Item .env.example .env
```

Open `.env` in any editor and fill in your keys:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Security**: `.env` is listed in `.gitignore` and will never be committed.

---

## Running the Bot

All commands are run from inside the `trading_bot/` directory with the
virtual environment activated.

### View help

```powershell
python cli.py --help
```

---

## Usage Examples

### Market BUY order

```powershell
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### Market SELL order

```powershell
python cli.py --symbol BTCUSDT --side SELL --order-type MARKET --quantity 0.001
```

### Limit BUY order

```powershell
python cli.py --symbol BTCUSDT --side BUY --order-type LIMIT --quantity 0.001 --price 60000.00
```

### Limit SELL order

```powershell
python cli.py --symbol ETHUSDT --side SELL --order-type LIMIT --quantity 0.01 --price 3200.50
```

### Short options

```powershell
python cli.py -s BTCUSDT --side BUY -t MARKET -q 0.001
```

---

## Sample Output

**Market BUY — terminal output:**

```
┌─────────────────────────────────────┐
│            📋 Order Summary          │
├──────────────┬──────────────────────┤
│ Field        │ Value                │
├──────────────┼──────────────────────┤
│ Symbol       │ BTCUSDT              │
│ Side         │ BUY                  │
│ Order Type   │ MARKET               │
│ Quantity     │ 0.001                │
│ Price        │ MARKET (best avail.) │
└──────────────┴──────────────────────┘

┌─────────────────────────────────────┐
│           ✅ Order Response          │
├──────────────────┬───────────────────┤
│ Order ID         │ 4149431553        │
│ Symbol           │ BTCUSDT           │
│ Side             │ BUY               │
│ Type             │ MARKET            │
│ Status           │ FILLED            │
│ Quantity         │ 0.001             │
│ Executed Qty     │ 0.001             │
│ Avg Price        │ 62345.10          │
└──────────────────┴───────────────────┘

╭─────────────────────────────────────────╮
│ ✅ Order placed successfully!            │
│ Order ID: 4149431553  |  Status: FILLED │
╰─────────────────────────────────────────╯
```

---

## Logging

Every run appends structured entries to `logs/trading_bot.log`.

```
2025-10-14 09:12:01 | INFO     | __main__   | CLI invoked | symbol=BTCUSDT side=BUY type=MARKET qty=0.001 price=None
2025-10-14 09:12:01 | DEBUG    | bot.client | UMFutures client initialised → https://testnet.binancefuture.com
2025-10-14 09:12:01 | INFO     | bot.orders | Placing BUY MARKET order | symbol=BTCUSDT | qty=0.001
2025-10-14 09:12:02 | INFO     | bot.orders | Order placed successfully | orderId=4149431553 | status=FILLED
```

- Log rotates at **5 MB** and keeps **3 backups** (`trading_bot.log.1`, `.2`, `.3`).
- See `sample_logs/` for realistic pre-recorded examples.

---

## Assumptions

| # | Assumption |
|---|---|
| 1 | Only **USDT-M** (USD-margined) Futures Testnet is targeted — not COIN-M. |
| 2 | **LIMIT** orders use `timeInForce=GTC` (Good Till Cancelled) by default. |
| 3 | Quantity precision must satisfy the symbol's `LOT_SIZE` filter on Testnet. If the bot returns a precision error, round your `--quantity` to fewer decimals. |
| 4 | The bot does **not** manage open positions or cancel orders — it is a one-shot order placer. |
| 5 | Network access to `testnet.binancefuture.com` is required (port 443). |
| 6 | `MARKET` orders on Futures Testnet may require the account to have a valid hedge-mode or one-way-mode position; default is **one-way mode**. |

---

## Tech Stack

| Library | Purpose |
|---|---|
| [python-binance](https://python-binance.readthedocs.io/) | Binance Futures REST API client |
| [Typer](https://typer.tiangolo.com/) | CLI framework with auto-generated `--help` |
| [Rich](https://rich.readthedocs.io/) | Coloured terminal output, tables, panels |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | `.env` file loading |
| Python `logging` | Rotating file + console log handler |


