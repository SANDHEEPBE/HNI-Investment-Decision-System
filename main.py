# main.py
import os
from data_pipeline.live_data import fetch_live_price
import pandas as pd

# Completely silence TensorFlow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import yfinance as yf
import numpy as np
from visualization.charts import plot_health_score_comparison

from analysis.classification import classify_by_marketcap
from analysis.company_health import (
    analyze_company_health,
    compare_all_health_scores,
    fetch_company_list_yf
)

from visualization.charts import (
    plot_marketcap_comparison,
    plot_segment_distribution,
    generate_company_charts,
    plot_health_score_comparison  
)

# MAIN MENU

def main_menu():
    while True:
        print("\nMAIN MENU")
        print("=" * 50)
        print(" HNI INVESTMENT DECISION SUPPORT SYSTEM (MVP)")
        print("=" * 50)
        print("Select an option:\n")
        print("1. Investment Suggestions by Market Classification")
        print("2. Company Health Analysis")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            part1()
        elif choice == '2':
            part2()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please choose 1, 2, or 3")

# PART 1 — INVESTMENT SUGGESTIONS

def part1():

    print("\nINVESTMENT SUGGESTIONS")

    companies_dict = fetch_company_list_yf()
    if not companies_dict:
        print("No company data available from API.")
        return

    suggestions, overall_best = classify_by_marketcap(companies_dict)

    for seg_name, comp_list in suggestions.items():
        print(f"\n{seg_name} — BEST {len(comp_list)}")

        for idx, c in enumerate(comp_list, 1):
            print(
                f"{idx}. {c['Name']} ({c['Symbol']}) "
                f"— Market Cap: ${c['MarketCap']:.0f}"
            )

    print("\n📊 Overall Best Investment (All Segments)")
    print("=" * 50)
    print(f"{overall_best['Name']} ({overall_best['Symbol']})")
    print(f"Market Cap: ${overall_best['MarketCap']:,}")
    print("Trend: Strong Upward Momentum")
    print("Risk Level: Moderate")

    # Charts
    plot_marketcap_comparison(suggestions)
    plot_segment_distribution(suggestions)

    input("\nBack to Menu — Press ENTER to continue...")

# PART 2 — COMPANY HEALTH ANALYSIS

def part2():

    companies_dict = fetch_company_list_yf()
    if not companies_dict:
        print("No company data available from API.")
        return

    print("\n Company Selection")
    print("=" * 50)
    print("COMPANY HEALTH ANALYSIS")

    symbols = list(companies_dict.keys())

    for i, sym in enumerate(symbols, 1):
        print(f"{i}. {companies_dict[sym]['Name']} ({sym})")

    print(f"{len(symbols) + 1}. Compare Health Scores of All Companies")

    choice = input("\nEnter Company Name, Symbol, or option: ").strip().upper()

    # OPTION → COMPARE ALL COMPANIES
 
    if choice.isdigit() and int(choice) == len(symbols) + 1:

        df = compare_all_health_scores()

        print("\n📊 Company Health Score Comparison (Top Companies)")
        for idx, row in enumerate(df.itertuples(), 1):
            print(
                f"{idx}. {row.Name} ({row.Symbol}) "
                f"— Health Score: {row.HealthScore:.2f}"
            )

        print(f"\n Best Company: {df.iloc[0].Name} ({df.iloc[0].Symbol})")
        plot_health_score_comparison(df)
        print(df)

        input("\nBack to Menu — Press ENTER to continue...")
        return

    # SELECT SPECIFIC COMPANY

    selected_symbol = None

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(symbols):
            selected_symbol = symbols[idx]

    if not selected_symbol:
        for sym, info in companies_dict.items():
            if choice == sym or choice.lower() == info['Name'].lower():
                selected_symbol = sym
                break

    if not selected_symbol:
        print(f"Company '{choice}' not found.")
        return

    # FETCH COMPANY HEALTH DATA

    company_data = analyze_company_health(selected_symbol)

    if not company_data:
        print("Error fetching company health data.")
        return

    # Company Details

    print("\n Company Details")
    print(f"Company: {company_data['Name']}")
    print(f"Symbol: {company_data['Symbol']}")
    print(f"Sector: {company_data.get('Sector', 'N/A')}")
    print(f"Industry: {company_data.get('Industry', 'N/A')}")
    print(f"Market Cap: ${company_data['MarketCap']:,}")

    # -----------------------------------------------------
    # Health Score & Recommendation
    # -----------------------------------------------------
    ml_score = (
        company_data['HealthScore']
        if not np.isnan(company_data['HealthScore'])
        else 50
    )

    print("\n Overall Health Score")
    print("=" * 50)
    print(f"Health Score: {ml_score:.2f} %")

    if ml_score > 85:
        status = "EXCELLENT INVESTMENT QUALITY"
        risk = "Medium"
        outlook_long = "Strong Growth"
        outlook_short = "Bullish with Volatility"
    elif ml_score > 70:
        status = "GOOD INVESTMENT QUALITY"
        risk = "Moderate"
        outlook_long = "Steady Growth"
        outlook_short = "Mild Volatility"
    else:
        status = "CAUTION ADVISED"
        risk = "High"
        outlook_long = "Uncertain Growth"
        outlook_short = "Volatile"

    print(f"Status: {status}")
    print(f"Risk Level: {risk}")
    print(f"Long-Term Outlook: {outlook_long}")
    print(f"Short-Term Outlook: {outlook_short}")

    # Plot Options

    hist_df = company_data['Historical']

    if isinstance(hist_df, str):
        print(f" Warning: Historical data not available for {selected_symbol}.")
        return

    # ADD LIVE DATA TO HISTORICAL DATA

    live = fetch_live_price(selected_symbol)

    if live is not None:

        live_row = pd.DataFrame([{
            "Date": pd.to_datetime(live["Time"]),
            "Open": live["Open"],
            "High": live["High"],
            "Low": live["Low"],
            "Close": live["Close"],
            "Volume": live["Volume"]
        }])

        # Ensure historical has Date column
        if "Date" not in hist_df.columns:
            hist_df = hist_df.reset_index()

        hist_df = pd.concat([hist_df, live_row], ignore_index=True)

    # -----------------------------------------------------
    # Generate Charts (UNCHANGED)
    # -----------------------------------------------------
    generate_company_charts(
        selected_symbol,
        hist_df,
        health_score=ml_score
    )

    input("\nBack to Menu — Press ENTER to continue...")


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    main_menu()