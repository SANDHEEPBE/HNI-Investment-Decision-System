# HNI Investment Decision Support System (MVP)
---

## Overview
---

The HNI Investment Decision Support System (MVP) is a data-driven prototype designed to assist High Net Worth Individuals (HNIs) in making informed equity investment decisions.

The system provides:

- Structured investment suggestions across market-capitalization segments  
- Focused analysis of large-cap global leaders including the “Magnificent Seven”  
- Quantitative company health scoring  
- Risk-aware insights using financial fundamentals and market behavior  
- Visual analytics for decision support  

The solution integrates live market data, historical trends, and analytical modeling into a single workflow.

---

## Objectives
---

### Part 1 — Investment Suggestions

Provide curated company recommendations based on market capitalization:

- Magnificent Seven technology leaders  
- Companies with Market Cap > USD 500 Billion — Top 5  
- Market Cap USD 100B–500B — Top 7  
- Market Cap < USD 100B — Top 10  

Ranking is based on:

- Market strength  
- Stability  
- Growth indicators  
- Liquidity  
- Risk profile  

### Part 2 — Company Health Analysis

**Input:** Company Name or Symbol (e.g., NVDA)

**Output:**

- Overall Health Score (%)  
- Risk Assessment  
- Growth Indicators  
- Financial Strength  
- Cash Flow & Profitability Insights  
- Pros and Cons for Investment Decision  

---

## Key Features
---

### Data Pipeline

- Live price retrieval (latest market snapshot)  
- Historical data collection  
- Automated preprocessing and normalization  
- Integration of live + historical datasets  

**Endpoints / Sources**

- Yahoo Finance API (via yfinance)  
- Live data fetch module  
- Historical OHLCV data  

---

## Data Formats Used
---

| Format | Purpose | Pros | Cons |
|--------|---------|------|------|
| Pandas DataFrame | Core processing | Fast, flexible | Memory-heavy for huge datasets |
| CSV | Storage/export | Portable, simple | No schema enforcement |
| JSON | API exchange | Structured | Larger file size |
| NumPy Arrays | Modeling | Efficient numeric ops | Less human-readable |

---

## Financial Modeling Techniques
---

### Statistical Methods

- Trend analysis  
- Moving averages  
- Volatility estimation  

### Machine Learning / AI

- Health scoring model based on weighted financial metrics  
- Risk categorization  
- Predictive trend assessment  

### Time-Series Considerations

- Historical behavior analysis  
- Momentum tracking  
- Short-term vs long-term outlook  

---

## Company Health Score Factors
---

Health score combines multiple dimensions:

- Revenue growth  
- Profit margins  
- Debt ratio  
- Cash flow strength  
- Market stability  
- Risk indicators  
- Historical performance  

**Score Interpretation**

| Score | Meaning |
|--------|---------|
| 85–100 | Excellent |
| 70–85 | Good |
| 50–70 | Moderate |
| < 50 | High Risk |

---

## Visualization Outputs
---

The system generates decision-support visuals including:

- Market capitalization comparison (Bar Chart)  
- Segment distribution (Pie Chart)  
- Historical price trends (Line Chart)  
- Moving averages (Trend indicators)  
- Health score comparison across companies  
- Company-specific analytics dashboard  

---

## Technology Stack
---

### Core Technologies

- Python 3.x  

### Data Processing

- Pandas  
- NumPy  

### Data Acquisition

- yfinance (Yahoo Finance API)  

### Visualization

- Matplotlib  

### Development Environment

- VS Code / Jupyter Notebook  
- Git & GitHub  

---

## How to Run the Project
---

### 1. Install Dependencies

```bash
pip install yfinance pandas numpy matplotlib
