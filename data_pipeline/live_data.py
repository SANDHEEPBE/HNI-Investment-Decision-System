import yfinance as yf
from datetime import datetime
import time
import threading

COMPANIES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla Inc.",
    "COST": "Costco Wholesale Corp.",
    "ADBE": "Adobe Inc.",
    "PEP": "PepsiCo Inc.",
    "CSCO": "Cisco Systems Inc.",
    "NFLX": "Netflix Inc.",
    "CRM": "Salesforce Inc.",
    "ACN": "Accenture PLC",
    "SNOW": "Snowflake Inc.",
    "DDOG": "Datadog Inc.",
    "RBLX": "Roblox Corp.",
    "ZM": "Zoom Video Communications",
    "PLTR": "Palantir Technologies Inc.",
    "NET": "Cloudflare Inc.",
    "OKTA": "Okta Inc.",
    "PINS": "Pinterest Inc.",
    "TWLO": "Twilio Inc."
}

# Company Profile Information

def fetch_company_list():
    company_data = {}

    for symbol, name in COMPANIES.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            company_data[symbol] = {
                "Name": name,
                "Symbol": symbol,
                "Sector": info.get("sector", "Unknown"),
                "Industry": info.get("industry", "Unknown"),
                "MarketCap": info.get("marketCap", 0)
            }

        except Exception:
            continue

    return company_data

# Fetch Latest Live Price 

def fetch_live_price(symbol):
    try:
        ticker = yf.Ticker(symbol)

        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return None

        latest = data.iloc[-1]

        return {
            "Symbol": symbol,
            "Time": latest.name,
            "Open": latest["Open"],
            "High": latest["High"],
            "Low": latest["Low"],
            "Close": latest["Close"],
            "Volume": latest["Volume"]
        }

    except Exception:
        return None

# Continuous Live Updates Per Minute

def stream_live_prices():

    try:
        while True:

            for symbol in COMPANIES.keys():
                _ = fetch_live_price(symbol)

            time.sleep(60) 

    except Exception:
        pass  

# AUTO-START BACKGROUND STREAM THREAD

_live_thread = threading.Thread(
    target=stream_live_prices,
    daemon=True 
)

_live_thread.start()