import os
import base64
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.getenv("TRADING212_API_KEY")
API_SECRET = os.getenv("TRADING212_API_SECRET")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE", "live")

BASE_URL = f"https://{'demo' if ACCOUNT_TYPE == 'demo' else 'live'}.trading212.com"
_credentials = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
HEADERS = {"Authorization": f"Basic {_credentials}"}

print(f"DEBUG key: '{API_KEY[:6]}...{API_KEY[-4:]}' secret: {'set' if API_SECRET else 'MISSING'}" if API_KEY else "DEBUG: API_KEY is None/empty")


def fetch_portfolio():
    r = requests.get(f"{BASE_URL}/api/v0/equity/portfolio", headers=HEADERS)
    if not r.ok:
        print(f"DEBUG response: {r.status_code} {r.text}")
    r.raise_for_status()
    return r.json()


def fetch_cash():
    r = requests.get(f"{BASE_URL}/api/v0/equity/account/cash", headers=HEADERS)
    r.raise_for_status()
    return r.json()


def format_change(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}€{value:,.2f}"


def build_discord_payload(positions, cash):
    total_invested = cash.get("invested", 0)
    total_ppl = cash.get("ppl", 0)
    free_cash = cash.get("free", 0)
    total_value = cash.get("total", total_invested + free_cash)
    ppl_pct = (total_ppl / total_invested * 100) if total_invested else 0

    color = 0x2ECC71 if total_ppl >= 0 else 0xE74C3C  # green or red

    # Sort positions by absolute P&L descending
    sorted_positions = sorted(positions, key=lambda p: abs(p.get("ppl", 0)), reverse=True)

    holdings_lines = []
    for p in sorted_positions[:15]:  # cap at 15 to avoid Discord limits
        ticker = p.get("ticker", "?").split("_")[0]
        qty = p.get("quantity", 0)
        current_price = p.get("currentPrice", 0)
        ppl = p.get("ppl", 0)
        position_value = qty * current_price
        ppl_sign = "📈" if ppl >= 0 else "📉"
        holdings_lines.append(
            f"`{ticker:<10}` {qty:.4f} shares  ·  €{position_value:,.2f}  ·  {ppl_sign} {format_change(ppl)}"
        )

    holdings_text = "\n".join(holdings_lines) if holdings_lines else "No open positions."

    embed = {
        "title": "📊 Daily Portfolio Report",
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {
                "name": "Portfolio Summary",
                "value": (
                    f"**Total Value:** €{total_value:,.2f}\n"
                    f"**Invested:** €{total_invested:,.2f}\n"
                    f"**Total P&L:** {format_change(total_ppl)} ({ppl_sign_str(ppl_pct)}%)\n"
                    f"**Free Cash:** €{free_cash:,.2f}"
                ),
                "inline": False,
            },
            {
                "name": f"Holdings ({len(positions)} positions)",
                "value": holdings_text,
                "inline": False,
            },
        ],
        "footer": {"text": "Trading212 Tracker"},
    }

    return {"content": "<@414107432894332928>", "embeds": [embed]}


def ppl_sign_str(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}"


def send_to_discord(payload):
    r = requests.post(WEBHOOK_URL, json=payload)
    r.raise_for_status()


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching portfolio...")
    positions = fetch_portfolio()
    cash = fetch_cash()
    payload = build_discord_payload(positions, cash)
    send_to_discord(payload)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Report sent to Discord.")


if __name__ == "__main__":
    main()
