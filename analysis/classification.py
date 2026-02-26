# analysis/classification.py
import pandas as pd
from data_pipeline.live_data import fetch_company_list, fetch_live_price
from data_pipeline.historical_data import fetch_historical
from visualization.charts import plot_segment_distribution, plot_marketcap_comparison


def classify_by_marketcap(companies_dict):
    
    print("Fetching live + historical data...")
    print("Analyzing market capitalization & performance...\n")

    segments = {
        ">500B": [],
        "100B-500B": [],
        "<100B": []
    }

    for symbol, info in companies_dict.items():

        hist_df = fetch_historical(symbol)
        live_data = fetch_live_price(symbol)

        if live_data:
            latest_price = live_data["Close"]
        else:
            latest_price = info.get("LatestPrice", None)

        # Compute 5-year return
        if hist_df is not None and not hist_df.empty and latest_price:
            start_price = hist_df["Close"].iloc[0]
            total_return = ((latest_price - start_price) / start_price) * 100
        else:
            total_return = 0

        company_entry = {
            "Symbol": symbol,
            "Name": info["Name"],
            "MarketCap": info.get("MarketCap", 0),
            "TotalReturn": total_return
        }

        market_cap = info.get("MarketCap", 0)

        if market_cap > 500_000_000_000:
            segments[">500B"].append(company_entry)
        elif market_cap > 100_000_000_000:
            segments["100B-500B"].append(company_entry)
        else:
            segments["<100B"].append(company_entry)

    # Sort by MarketCap
    for key in segments:
        segments[key] = sorted(
            segments[key],
            key=lambda x: x["MarketCap"],
            reverse=True
        )

    # Overall best investment
    all_companies = [c for seg in segments.values() for c in seg]

    overall_best = max(
        all_companies,
        key=lambda x: x["MarketCap"] * (1 + x["TotalReturn"] / 100)
    )

    return segments, overall_best