# 🏛️ Institutional Wealth Analytics (2010–2026)
### Empirical Research Platform: Active Equity Stock Baskets vs Passive Nifty 50 Systematic Investment Plan (SIP)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Plotly](https://img.shields.io/badge/Plotly-Dash-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)

An institutional-grade quantitative research platform and dual-engine analytical suite (**Microsoft Power BI + Streamlit**) evaluating **16.6 years of historical market data (2010–2026)** to answer a foundational wealth creation question:

> **The Core Quantitative Hypothesis:** If an investor executes disciplined Rupee-Cost Averaging (SIP) on the 1st trading day of every month with zero emotional timing interference, can handpicked stock portfolios reliably beat the passive Nifty 50 index — and what is the true psychological cost in capital drawdowns?

---

## 📌 Key Empirical Findings (2010 – 2026)

Across 201 monthly SIP cycles spanning the 2010 Eurozone crisis, 2016 Demonetization, 2020 COVID-19 crash, and the 2024–2026 bull cycle:

1. **The Fallacy of Simple Point-to-Point CAGR:**
   Standard CAGR assumes a lump-sum entry at the absolute low. For a recurring SIP, staggered monthly deposits require calculating the exact **Internal Rate of Return (XIRR)**.
2. **True Capital Loss vs Paper Drawdown:**
   Standard finance metrics measure *Peak-to-Trough Drawdown*. Retail psychology, however, is driven by *Capital Preservation* ($\text{Net P&L}_t = \text{Portfolio Value}_t - \text{Total Deposited}_t$). While individual equities routinely plunged 20% to 50% below principal, Nifty 50's worst historical capital loss was capped at **-₹32,692 (-₹0.33 L)**, proving an impenetrable diversification shield.
3. **Verified Portfolio Case Study (Start Year: 2020 @ ₹39,500/month):**
   * **Total Capital Deposited (81 months):** ₹32.00 Lakhs
   * **Nifty 50 Benchmark:** Current Value: **₹44.37 Lakhs** (10.2% XIRR) | Peak Wealth: **₹46.08 Lakhs** | Worst Capital Loss: **-₹0.33 Lakhs**
   * **Active 4-Stock Basket (ITC, L&T, M&M, Maruti):** Current Value: **₹59.65 Lakhs** (20.3% XIRR) | Peak Wealth: **₹67.97 Lakhs** | Worst Capital Loss: **-₹0.43 Lakhs**
   * **Active Alpha:** **+₹15.28 Lakhs** (+10.1% annualized speed advantage).

---

## 🏗️ Repository Architecture

```
├── .streamlit/
│   └── config.toml                  # FinTech luxury theme tokens (#00876C primary, #F6F8FB background)
├── data/
│   ├── powerbi_ready/               # 16.6-year curated star-schema dataset
│   │   ├── Dim_Asset.csv            # 24 assets, sectors, categories
│   │   ├── Fact_DailyPrices.csv     # 89,800 daily adjusted closing records
│   │   └── Fact_MonthlySIP_Prices.csv # 4,379 1st-working-day monthly SIP prices
│   └── individual_stocks/           # Clean CSVs for individual securities
├── utils/
│   └── analytics.py                 # Pure Python quantitative financial engine
├── app.py                           # Full interactive 3-tab Streamlit web application
├── sip analytics.pbix               # Complete institutional Power BI Desktop file
├── 1_BlackRock_Aladdin_Executive_Light.json # Power BI custom design theme
├── requirements.txt                 # Application dependencies
└── walkthrough.md                   # Verification & deployment documentation
```

---

## 💻 Running the Streamlit App Locally

### 1. Clone the repository
```bash
git clone https://github.com/singhparmeet12/SIP-Comparison-Project.git
cd SIP-Comparison-Project
```

### 2. Set up virtual environment
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch Streamlit
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to explore the simulator, documentary, and data architecture tabs.

---

## ☁️ 1-Click Cloud Deployment (Streamlit Community Cloud)

This repository is pre-configured for instant zero-configuration deployment:
1. Fork or push this repository to your GitHub account.
2. Sign in to **[share.streamlit.io](https://share.streamlit.io)** using your GitHub credentials.
3. Click **"New App"** -> Select `SIP-Comparison-Project` -> Main file: `app.py`.
4. Click **"Deploy"**!

---

## 📊 Power BI Desktop Dashboard

To open and explore the interactive Power BI dashboard:
1. Launch **Microsoft Power BI Desktop**.
2. Open [`sip analytics.pbix`](./sip%20analytics.pbix).
3. The model incorporates DAX measures matching the Python quantitative engine with slicers for Start Year, SIP Budget, and multi-asset selection.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
