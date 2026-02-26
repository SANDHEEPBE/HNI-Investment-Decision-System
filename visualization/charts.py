# visualization/charts.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from visualization.utils import save_and_show
from data_pipeline.live_data import fetch_live_price
from models.forecast_model import lstm_predict

sns.set(style="whitegrid")


# PART 1 — MARKET CAP CHARTS

def plot_marketcap_comparison(segments_dict):

    all_entries = []
    for seg, comp_list in segments_dict.items():
        for comp in comp_list:
            all_entries.append({
                "Segment": seg,
                "Company": comp["Name"],
                "MarketCap": comp["MarketCap"]
            })

    df = pd.DataFrame(all_entries)

    plt.figure(figsize=(12, 8))
    sns.barplot(x="MarketCap", y="Company", hue="Segment", data=df)
    plt.title("Market Capitalization by Segment")

    save_and_show(plt.gcf(), "MarketCap_by_Segment.png")


def plot_segment_distribution(segments_dict):

    counts = {k: len(v) for k, v in segments_dict.items()}

    plt.figure(figsize=(8, 8))
    plt.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%")
    plt.title("Segment Distribution")

    save_and_show(plt.gcf(), "Segment_distribution.png")

#  PART 2 — COMPANY CHARTS

def generate_company_charts(symbol, historical_df, health_score=None):

    if historical_df is None or historical_df.empty:
        print("⚠ Invalid historical data")
        return

    if "Date" not in historical_df.columns:
        historical_df = historical_df.reset_index()

    #  ADD LIVE DATA

    live = fetch_live_price(symbol)

    if live is not None:
        live_row = pd.DataFrame([{
            "Date": pd.to_datetime(live["Time"]),
            "Open": live["Open"],
            "High": live["High"],
            "Low": live["Low"],
            "Close": live["Close"],
            "Volume": live["Volume"]
        }])

        historical_df = pd.concat([historical_df, live_row], ignore_index=True)


    # Historical Price Trend


    plt.figure(figsize=(10, 5))
    plt.plot(historical_df["Date"], historical_df["Close"])
    plt.title(f"{symbol} Historical Price Trend")

    save_and_show(plt.gcf(), f"{symbol}_historical_price_trend")

   
    # Moving Average — 1 YEAR
  

    df1 = historical_df.tail(252)
    ma100 = df1["Close"].rolling(100, min_periods=1).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df1["Date"], df1["Close"], label="Close")
    plt.plot(df1["Date"], ma100, label="100-Day MA")
    plt.legend()
    plt.title(f"{symbol} Moving Average — 1yr")

    save_and_show(plt.gcf(), f"{symbol}_Moving_Average_1yr")

    # Moving Averages — 5 YEARS

    df5 = historical_df.tail(1260)

    ma100 = df5["Close"].rolling(100, min_periods=1).mean()
    ma200 = df5["Close"].rolling(200, min_periods=1).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df5["Date"], df5["Close"], label="Close")
    plt.plot(df5["Date"], ma100, label="100-Day MA")
    plt.plot(df5["Date"], ma200, label="200-Day MA")
    plt.legend()
    plt.title(f"{symbol} Moving Averages — 5yr")

    save_and_show(plt.gcf(), f"{symbol}_Moving_Averages_5yr")

    # LSTM FORECAST
  
    if getattr(generate_company_charts, "_forecast_done", False):
        return

    forecast = lstm_predict(symbol, historical_df)

    if forecast is None:
        print("⚠ Forecast unavailable")
        return

    last_date = historical_df["Date"].iloc[-1]
    last_close = historical_df["Close"].iloc[-1]

    # WEEK FORECAST

    week_vals = forecast["7_day"]
    week_vals = week_vals - week_vals[0] + last_close

    week_dates = pd.bdate_range(
        start=last_date,
        periods=len(week_vals) + 1
    )[1:]

    plt.figure(figsize=(8, 4))

    hist_tail = historical_df.tail(60)

    plt.plot(hist_tail["Date"], hist_tail["Close"], label="Historical")

    plt.plot(week_dates, week_vals, label="Predicted")

    plt.legend()
    plt.title(f"{symbol} Forecast — 1 Week")

    save_and_show(plt.gcf(), f"{symbol}_forecast_week")

    # MONTH FORECAST

    month_vals = forecast["30_day"]
    month_vals = month_vals - month_vals[0] + last_close

    month_dates = pd.bdate_range(
        start=last_date,
        periods=len(month_vals) + 1
    )[1:]

    plt.figure(figsize=(10, 5))

    hist_tail = historical_df.tail(120)

    plt.plot(hist_tail["Date"], hist_tail["Close"], label="Historical")
    plt.plot(month_dates, month_vals, label="Predicted")

    plt.legend()
    plt.title(f"{symbol} Forecast — 1 Month")

    save_and_show(plt.gcf(), f"{symbol}_forecast_month")

    generate_company_charts._forecast_done = True


# HEALTH SCORE COMPARISON

def plot_health_score_comparison(df):

    if df is None or df.empty:
        print(" No data for comparison")
        return

    names = df["Symbol"]
    scores = df["HealthScore"]

    plt.figure(figsize=(12, 6))

    bars = plt.bar(names, scores)

    plt.ylabel("Health Score")
    plt.xlabel("Companies")
    plt.title("Company Health Score Comparison")

    plt.xticks(rotation=45)

    # Highlight best company
    best_idx = scores.idxmax()
    bars[best_idx].set_color("green")

    # Score labels
    for i, v in enumerate(scores):
        plt.text(i, v + 1, f"{v:.1f}", ha='center')

    plt.tight_layout()
    plt.savefig("charts/Company_Health_Score_Comparison.png")
    plt.show()

    print("📊 Saved: charts\\Company_Health_Score_Comparison.png")