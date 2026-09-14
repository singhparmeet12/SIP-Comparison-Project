import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "powerbi_ready")

def load_data():
    """Load and cache the preprocessed star-schema datasets."""
    dim_asset = pd.read_csv(os.path.join(DATA_DIR, "Dim_Asset.csv"))
    fact_monthly = pd.read_csv(os.path.join(DATA_DIR, "Fact_MonthlySIP_Prices.csv"))
    fact_daily = pd.read_csv(os.path.join(DATA_DIR, "Fact_DailyPrices.csv"))
    
    fact_monthly["SIP_Date"] = pd.to_datetime(fact_monthly["SIP_Date"])
    fact_daily["Date"] = pd.to_datetime(fact_daily["Date"])
    
    return dim_asset, fact_monthly, fact_daily

def format_currency_inr(amount_in_rupees, include_symbol=True):
    """Format rupee values cleanly into Lakhs or Crores."""
    if pd.isna(amount_in_rupees) or amount_in_rupees is None:
        return "--"
    sym = "₹" if include_symbol else ""
    abs_val = abs(amount_in_rupees)
    sign = "-" if amount_in_rupees < 0 else ""
    
    if abs_val >= 10000000.0:  # 1 Crore
        return f"{sign}{sym}{abs_val / 10000000.0:.2f} Cr"
    else:
        return f"{sign}{sym}{abs_val / 100000.0:.2f} L"

def format_pct(value, include_sign=False):
    """Format percentage values."""
    if pd.isna(value) or value is None:
        return "--"
    plus = "+" if (include_sign and value > 0) else ""
    return f"{plus}{value:.1f}%"

def run_nifty_benchmark(fact_monthly, fact_daily, start_year, monthly_sip):
    """Calculate exact SIP metrics for NIFTY 50 Benchmark (NIFTYBEES.NS)."""
    nifty_monthly = fact_monthly[
        (fact_monthly["Ticker"] == "NIFTYBEES.NS") & (fact_monthly["Year"] >= start_year)
    ].sort_values("SIP_Date").copy()
    
    total_months = len(nifty_monthly)
    total_invested = total_months * monthly_sip
    
    nifty_monthly["units"] = monthly_sip / nifty_monthly["SIP_Buy_Price"]
    nifty_monthly["cum_units"] = nifty_monthly["units"].cumsum()
    nifty_monthly["cum_invested"] = (np.arange(total_months) + 1) * monthly_sip
    nifty_monthly["portfolio_val"] = nifty_monthly["cum_units"] * nifty_monthly["SIP_Buy_Price"]
    nifty_monthly["net_pl"] = nifty_monthly["portfolio_val"] - nifty_monthly["cum_invested"]
    
    peak_wealth = nifty_monthly["portfolio_val"].max()
    peak_idx = nifty_monthly["portfolio_val"].idxmax()
    peak_date = nifty_monthly.loc[peak_idx, "SIP_Date"]
    
    worst_loss = nifty_monthly["net_pl"].min()
    worst_idx = nifty_monthly["net_pl"].idxmin()
    worst_date = nifty_monthly.loc[worst_idx, "SIP_Date"]
    
    # Latest daily price
    nifty_daily = fact_daily[fact_daily["Ticker"] == "NIFTYBEES.NS"].sort_values("Date")
    if len(nifty_daily) > 0:
        latest_price = nifty_daily["Adj_Close"].iloc[-1]
    else:
        latest_price = nifty_monthly["SIP_Buy_Price"].iloc[-1]
        
    current_val_today = nifty_monthly["cum_units"].iloc[-1] * latest_price
    current_drop_pct = ((current_val_today - peak_wealth) / peak_wealth) * 100.0
    
    # Annualized XIRR approximation
    eff_years = (total_months / 12.0) / 2.0
    annual_return = ((current_val_today / total_invested) ** (1.0 / eff_years) - 1.0) * 100.0
    
    return {
        "ticker": "NIFTYBEES.NS",
        "name": "Nifty 50 Benchmark",
        "total_months": total_months,
        "total_invested": total_invested,
        "current_val": current_val_today,
        "peak_wealth": peak_wealth,
        "peak_date": peak_date,
        "current_drop_pct": current_drop_pct,
        "worst_loss": worst_loss,
        "worst_date": worst_date,
        "annual_return": annual_return,
        "timeline_df": nifty_monthly[["SIP_Date", "portfolio_val", "cum_invested", "net_pl"]]
    }

def run_stock_basket_simulation(fact_monthly, fact_daily, selected_tickers, start_year, monthly_sip):
    """Calculate exact SIP metrics for user-selected stocks basket."""
    if not selected_tickers:
        return None
        
    num_stocks = len(selected_tickers)
    per_stock_sip = monthly_sip / num_stocks
    
    sub = fact_monthly[
        (fact_monthly["Ticker"].isin(selected_tickers)) & (fact_monthly["Year"] >= start_year)
    ].copy()
    
    unique_dates = sorted(sub["SIP_Date"].unique())
    total_months = len(unique_dates)
    total_invested = total_months * monthly_sip
    
    timeline = []
    for idx, d in enumerate(unique_dates):
        months_so_far = idx + 1
        invested_so_far = months_so_far * monthly_sip
        
        basket_val = 0.0
        for t in selected_tickers:
            t_sub = sub[(sub["Ticker"] == t) & (sub["SIP_Date"] <= d)]
            if len(t_sub) > 0:
                units = (per_stock_sip / t_sub["SIP_Buy_Price"]).sum()
                curr_price = t_sub.sort_values("SIP_Date")["SIP_Buy_Price"].iloc[-1]
                basket_val += units * curr_price
                
        net_pl = basket_val - invested_so_far
        timeline.append({
            "SIP_Date": d,
            "portfolio_val": basket_val,
            "cum_invested": invested_so_far,
            "net_pl": net_pl
        })
        
    tdf = pd.DataFrame(timeline)
    
    peak_wealth = tdf["portfolio_val"].max()
    peak_idx = tdf["portfolio_val"].idxmax()
    peak_date = tdf.loc[peak_idx, "SIP_Date"]
    
    worst_loss = tdf["net_pl"].min()
    worst_idx = tdf["net_pl"].idxmin()
    worst_date = tdf.loc[worst_idx, "SIP_Date"]
    
    # Current valuation using latest daily prices
    current_val_today = 0.0
    for t in selected_tickers:
        t_sub = sub[sub["Ticker"] == t]
        total_units = (per_stock_sip / t_sub["SIP_Buy_Price"]).sum()
        daily_t = fact_daily[fact_daily["Ticker"] == t].sort_values("Date")
        if len(daily_t) > 0:
            latest_price = daily_t["Adj_Close"].iloc[-1]
        else:
            latest_price = t_sub.sort_values("SIP_Date")["SIP_Buy_Price"].iloc[-1]
        current_val_today += total_units * latest_price
        
    current_drop_pct = ((current_val_today - peak_wealth) / peak_wealth) * 100.0
    eff_years = (total_months / 12.0) / 2.0
    annual_return = ((current_val_today / total_invested) ** (1.0 / eff_years) - 1.0) * 100.0
    
    return {
        "tickers": selected_tickers,
        "num_stocks": num_stocks,
        "total_months": total_months,
        "total_invested": total_invested,
        "current_val": current_val_today,
        "peak_wealth": peak_wealth,
        "peak_date": peak_date,
        "current_drop_pct": current_drop_pct,
        "worst_loss": worst_loss,
        "worst_date": worst_date,
        "annual_return": annual_return,
        "timeline_df": tdf
    }
