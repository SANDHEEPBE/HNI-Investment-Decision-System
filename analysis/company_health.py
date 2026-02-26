import yfinance as yf
import pandas as pd
import numpy as np
from data_pipeline.live_data import fetch_live_price

# COMPANY LIST

def fetch_company_list_yf(tickers=None):

    default_tickers = [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","COST","ADBE",
        "PEP","CSCO","NFLX","CRM","ACN","SNOW","DDOG","RBLX","ZM","PLTR",
        "NET","OKTA","PINS","TWLO"
    ]

    tickers = tickers or default_tickers

    companies = {}

    for t in tickers:
        try:
            info = yf.Ticker(t).info
            companies[t] = {
                "Name": info.get("longName", t),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "MarketCap": info.get("marketCap", 0)
            }
        except Exception:
            continue

    return companies

# NORMALIZATION HELPERS

def score_revenue_growth(g):
    if g >= 20: return 90
    if g >= 10: return 75
    if g >= 5:  return 60
    if g > 0:   return 50
    return 30


def score_profit_margin(m):
    if m >= 0.25: return 90
    if m >= 0.15: return 75
    if m >= 0.08: return 60
    if m > 0:     return 50
    return 30


def score_debt_ratio(d):
    if d < 0.3: return 90
    if d < 0.5: return 75
    if d < 0.7: return 60
    return 40


def score_cashflow(fcf):
    return 85 if fcf > 0 else 40


def score_volatility(v):
    if v > 0.03: return 50
    if v > 0.015: return 70
    return 90

# HEALTH SCORE ENGINE

def calculate_health_score(symbol):

    t = yf.Ticker(symbol)

    try:
        financials = t.financials
        balance = t.balance_sheet
        cashflow = t.cashflow
        fast = t.fast_info
        info = t.info  
    except Exception:
        return 50, [], [], [], {}, pd.DataFrame()

    # REVENUE GROWTH

    rev_score = 50
    rev_growth = None

    try:
        if financials is not None and "Total Revenue" in financials.index:
            rev = financials.loc["Total Revenue"].dropna()
            if len(rev) >= 2:
                rev_growth = (rev.iloc[0] - rev.iloc[1]) / abs(rev.iloc[1])
    except Exception:
        pass

    if rev_growth is not None:
        if rev_growth > 0.25:
            rev_score = 95
        elif rev_growth > 0.15:
            rev_score = 85
        elif rev_growth > 0.08:
            rev_score = 70
        elif rev_growth > 0:
            rev_score = 55
        else:
            rev_score = 35

    # PROFITABILITY

    profit_score = 50
    pm = None
    roe = None

    try:
        if financials is not None and "Net Income" in financials.index and "Total Revenue" in financials.index:
            ni = financials.loc["Net Income"].dropna()
            rev = financials.loc["Total Revenue"].dropna()
            if len(ni) > 0 and len(rev) > 0:
                pm = ni.iloc[0] / rev.iloc[0]
    except Exception:
        pass

    try:
        if balance is not None and "Total Stockholder Equity" in balance.index:
            equity = balance.loc["Total Stockholder Equity"].dropna()
            if len(equity) > 0 and 'ni' in locals() and len(ni) > 0:
                roe = ni.iloc[0] / equity.iloc[0]
    except Exception:
        pass

    if pm is not None:
        if pm > 0.30:
            profit_score += 20
        elif pm > 0.15:
            profit_score += 12
        elif pm > 0.05:
            profit_score += 6

    if roe is not None:
        if roe > 0.25:
            profit_score += 15
        elif roe > 0.15:
            profit_score += 10
        elif roe > 0.05:
            profit_score += 5

    profit_score = min(profit_score, 95)

    # FINANCIAL STABILITY

    debt_score = 50
    debt_ratio = None
    current_ratio = None

    try:
        if balance is not None:
            if "Total Debt" in balance.index and "Total Stockholder Equity" in balance.index:
                debt = balance.loc["Total Debt"].dropna()
                equity = balance.loc["Total Stockholder Equity"].dropna()
                if len(debt) > 0 and len(equity) > 0:
                    debt_ratio = debt.iloc[0] / equity.iloc[0]

            if "Current Assets" in balance.index and "Current Liabilities" in balance.index:
                ca = balance.loc["Current Assets"].dropna()
                cl = balance.loc["Current Liabilities"].dropna()
                if len(ca) > 0 and len(cl) > 0 and cl.iloc[0] != 0:
                    current_ratio = ca.iloc[0] / cl.iloc[0]
    except Exception:
        pass

    if debt_ratio is not None:
        if debt_ratio < 0.4:
            debt_score += 20
        elif debt_ratio < 0.8:
            debt_score += 10
        else:
            debt_score -= 10

    if current_ratio is not None:
        if current_ratio > 2:
            debt_score += 15
        elif current_ratio > 1:
            debt_score += 8
        else:
            debt_score -= 5

    debt_score = max(30, min(debt_score, 95))

    # CASH FLOW QUALITY

    cash_score = 50
    cashflow_status = "Unknown"
    fcf = None

    try:
        if cashflow is not None and "Free Cash Flow" in cashflow.index:
            fcf_series = cashflow.loc["Free Cash Flow"].dropna()
            if len(fcf_series) > 0:
                fcf = fcf_series.iloc[0]
    except Exception:
        pass

    if fcf is not None:
        if fcf > 5e10:
            cash_score = 95
        elif fcf > 1e10:
            cash_score = 85
        elif fcf > 0:
            cash_score = 70
        else:
            cash_score = 40

        cashflow_status = "Strong" if fcf > 0 else "Weak"

    # MARKET RISK (VOLATILITY)
    
    vol_score = 70
    vol_status = "Unknown"
    volatility = None

    hist = t.history(period="1y")
    live_data = fetch_live_price(symbol)

    if live_data is not None and not hist.empty:
        latest_row = {
            "Open": live_data["Open"],
            "High": live_data["High"],
            "Low": live_data["Low"],
            "Close": live_data["Close"],
            "Volume": live_data["Volume"]
        }

        hist.loc[live_data["Time"]] = latest_row
        hist = hist.sort_index()

    # Volatility calculation 

    if not hist.empty:
        returns = hist["Close"].pct_change().dropna()
        if not returns.empty:
            volatility = returns.std()

    # FINAL WEIGHTED SCORE

    health_score = (
        rev_score * 0.25 +
        profit_score * 0.25 +
        debt_score * 0.20 +
        cash_score * 0.15 +
        vol_score * 0.15
    )

    key_financials = {
        "Revenue Growth": rev_growth,
        "Profit Margin": pm,
        "Debt Ratio": debt_ratio,
        "Cash Flow": cashflow_status,
        "Volatility": vol_status
    }

    return health_score, [], [], [], key_financials, hist


# ANALYZE SINGLE COMPANY

def analyze_company_health(symbol):

    companies = fetch_company_list_yf()

    if symbol not in companies:
        return None

    score, strengths, weaknesses, risks, key_financials, hist = calculate_health_score(symbol)

    return {
        "Symbol": symbol,
        "Name": companies[symbol]["Name"],
        "Sector": companies[symbol]["Sector"],
        "Industry": companies[symbol]["Industry"],
        "MarketCap": companies[symbol]["MarketCap"],
        "HealthScore": score,
        "KeyFinancials": key_financials,
        "Historical": hist
    }


# COMPARE ALL COMPANIES

def compare_all_health_scores():

    companies = fetch_company_list_yf()

    rows = []

    for sym in companies:
        score, *_ = calculate_health_score(sym)

        rows.append({
            "Symbol": sym,
            "Name": companies[sym]["Name"],
            "HealthScore": round(score, 2)
        })

    df = pd.DataFrame(rows)

    return df.sort_values("HealthScore", ascending=False).reset_index(drop=True)