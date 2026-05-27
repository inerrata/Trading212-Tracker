# Trading212 Tracker

A lightweight Python script that fetches your Trading 212 portfolio and sends a daily report embed to a Discord channel via webhook.

## Features

- Pulls open positions and account cash summary from the Trading 212 API
- Sorts holdings by absolute P&L (biggest movers first)
- Sends a formatted Discord embed with portfolio summary and per-position breakdown
- Supports both Live and Demo Trading 212 accounts

## Example Output

The Discord embed includes:
- **Total portfolio value**, invested capital, total P&L (with %), and free cash
- **Per-position breakdown** — ticker, quantity, current value, and P&L with 📈/📉 indicators
- Up to 15 positions displayed (sorted by absolute P&L)

## Requirements

- Python 3.8+
- A Trading 212 **Invest** or **Stocks ISA** account (CFD not supported)
- A Trading 212 API key and secret
- A Discord webhook URL

## Installation

```bash
git clone https://github.com/inerrata/Trading212-Tracker.git
cd Trading212-Tracker
pip install requests python-dotenv
```

## Configuration

Create a `.env` file in the project root:

```env
TRADING212_API_KEY=your_api_key_here
TRADING212_API_SECRET=your_api_secret_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
ACCOUNT_TYPE=live  # or "demo" for paper trading
```

### Getting your API credentials

1. Open the Trading 212 app
2. Go to **Settings → API**
3. Generate a new key — make sure you're in the correct account mode (Live or Demo) before generating, as keys are environment-specific

## Usage

Run the script manually:

```bash
python tracker.py
```

### Scheduled runs

To run it automatically on a schedule, add a cron job:

```bash
# Example: run every day at 8am
0 8 * * * /usr/bin/python3 /path/to/tracker.py
```

Or use Task Scheduler on Windows.

## Notes

- The Trading 212 API is currently in **beta** and only supports Invest and Stocks ISA account types
- API keys generated in Demo mode will not work against the Live endpoint and vice versa
- Currency displayed is based on your primary account currency
