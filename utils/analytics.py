import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "powerbi_ready")

def load_data():
    """Load and cache the preprocessed star-schema datasets."""
    dim_asset = pd.read_csv(os.path.join(DATA_DIR, "Dim_Asset.csv"))
    fact_monthly = pd.read_csv(os.path.join(DATA_DIR, "Fact_MonthlySIP_Prices.csv"))
    fact_daily = pd.read_csv(os.path.join(DATA_DIR, "Fact_DailyPrices.csv"))
    
    # Fail-safe check: Ensure GOLDBEES.NS is merged if missing from the consolidated fact table (stale cache / partial files)
    if "GOLDBEES.NS" not in fact_monthly["Ticker"].values:
        gold_m_path = os.path.join(DATA_DIR, "GOLDBEES_MonthlySIP_Prices.csv")
        if os.path.exists(gold_m_path):
            gold_m = pd.read_csv(gold_m_path)
            fact_monthly = pd.concat([fact_monthly, gold_m], ignore_index=True)
            
    if "GOLDBEES.NS" not in fact_daily["Ticker"].values:
        gold_d_path = os.path.join(DATA_DIR, "GOLDBEES_DailyPrices.csv")
        if os.path.exists(gold_d_path):
            gold_d = pd.read_csv(gold_d_path)
            fact_daily = pd.concat([fact_daily, gold_d], ignore_index=True)

    fact_monthly["SIP_Date"] = pd.to_datetime(fact_monthly["SIP_Date"])
    fact_daily["Date"] = pd.to_datetime(fact_daily["Date"])
    
    return dim_asset, fact_monthly, fact_daily

def compute_exact_xirr(sip_dates, monthly_sip, terminal_date, terminal_val):
    """Compute exact annualized XIRR using bisection search on dated cash flows."""
    if len(sip_dates) == 0 or monthly_sip <= 0 or terminal_val is None:
        return 0.0
        
    d0 = pd.to_datetime(sip_dates[0])
    years = [(pd.to_datetime(d) - d0).days / 365.25 for d in sip_dates]
    cfs = [-float(monthly_sip)] * len(sip_dates)
    
    t_end = (pd.to_datetime(terminal_date) - d0).days / 365.25
    years.append(t_end)
    cfs.append(float(terminal_val))
    
    years = np.array(years)
    cfs = np.array(cfs)
    
    def npv(r):
        if r <= -0.9999:
            return 1e12
        return np.sum(cfs / ((1.0 + r) ** years))
    
    low, high = -0.999, 10.0
    f_low, f_high = npv(low), npv(high)
    if f_low * f_high > 0:
        high = 50.0
        f_high = npv(high)
        if f_low * f_high > 0:
            eff_years = (len(sip_dates) / 12.0) / 2.0
            return ((terminal_val / (len(sip_dates) * monthly_sip)) ** (1.0 / eff_years) - 1.0) * 100.0 if eff_years > 0 else 0.0
            
    for _ in range(150):
        mid = (low + high) / 2.0
        f_mid = npv(mid)
        if abs(f_mid) < 1e-4 or (high - low) < 1e-6:
            return mid * 100.0
        if f_low * f_mid < 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return mid * 100.0

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
    if total_months == 0:
        return {
            "ticker": "NIFTYBEES.NS",
            "name": "Nifty 50 Benchmark",
            "total_months": 0,
            "total_invested": 0.0,
            "current_val": 0.0,
            "peak_wealth": 0.0,
            "peak_date": pd.Timestamp.now(),
            "current_drop_pct": 0.0,
            "worst_loss": 0.0,
            "worst_date": pd.Timestamp.now(),
            "annual_return": 0.0,
            "timeline_df": pd.DataFrame(columns=["SIP_Date", "portfolio_val", "cum_invested", "net_pl"])
        }
        
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
    current_drop_pct = ((current_val_today - peak_wealth) / peak_wealth) * 100.0 if peak_wealth > 0 else 0.0
    
    terminal_date = nifty_daily["Date"].iloc[-1] if len(nifty_daily) > 0 else nifty_monthly["SIP_Date"].iloc[-1]
    annual_return = compute_exact_xirr(nifty_monthly["SIP_Date"].tolist(), monthly_sip, terminal_date, current_val_today)
    
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

def run_gold_benchmark(fact_monthly, fact_daily, start_year, monthly_sip):
    """Calculate exact SIP metrics for Gold Benchmark (GOLDBEES.NS)."""
    # Fail-safe check: if GOLDBEES.NS is not in fact_monthly (e.g. stale cache or old DataFrame), load from standalone CSV
    if "GOLDBEES.NS" not in fact_monthly["Ticker"].values:
        gold_m_path = os.path.join(DATA_DIR, "GOLDBEES_MonthlySIP_Prices.csv")
        if os.path.exists(gold_m_path):
            gold_m = pd.read_csv(gold_m_path)
            gold_m["SIP_Date"] = pd.to_datetime(gold_m["SIP_Date"])
            fact_monthly = pd.concat([fact_monthly, gold_m], ignore_index=True)

    gold_monthly = fact_monthly[
        (fact_monthly["Ticker"].str.strip() == "GOLDBEES.NS") & (fact_monthly["Year"] >= start_year)
    ].sort_values("SIP_Date").copy()
    
    total_months = len(gold_monthly)
    if total_months == 0:
        return {
            "ticker": "GOLDBEES.NS",
            "name": "Nippon India ETF Gold BeES",
            "total_months": 0,
            "total_invested": 0.0,
            "current_val": 0.0,
            "peak_wealth": 0.0,
            "peak_date": pd.Timestamp.now(),
            "current_drop_pct": 0.0,
            "worst_loss": 0.0,
            "worst_date": pd.Timestamp.now(),
            "annual_return": 0.0,
            "timeline_df": pd.DataFrame(columns=["SIP_Date", "portfolio_val", "cum_invested", "net_pl"])
        }
        
    total_invested = total_months * monthly_sip
    
    gold_monthly["units"] = monthly_sip / gold_monthly["SIP_Buy_Price"]
    gold_monthly["cum_units"] = gold_monthly["units"].cumsum()
    gold_monthly["cum_invested"] = (np.arange(total_months) + 1) * monthly_sip
    gold_monthly["portfolio_val"] = gold_monthly["cum_units"] * gold_monthly["SIP_Buy_Price"]
    gold_monthly["net_pl"] = gold_monthly["portfolio_val"] - gold_monthly["cum_invested"]
    
    peak_wealth = gold_monthly["portfolio_val"].max()
    peak_idx = gold_monthly["portfolio_val"].idxmax()
    peak_date = gold_monthly.loc[peak_idx, "SIP_Date"]
    
    worst_loss = gold_monthly["net_pl"].min()
    worst_idx = gold_monthly["net_pl"].idxmin()
    worst_date = gold_monthly.loc[worst_idx, "SIP_Date"]
    
    # Latest daily price
    gold_daily = fact_daily[fact_daily["Ticker"].str.strip() == "GOLDBEES.NS"].sort_values("Date")
    if len(gold_daily) == 0:
        gold_d_path = os.path.join(DATA_DIR, "GOLDBEES_DailyPrices.csv")
        if os.path.exists(gold_d_path):
            gold_daily = pd.read_csv(gold_d_path)
            gold_daily["Date"] = pd.to_datetime(gold_daily["Date"])
            gold_daily = gold_daily.sort_values("Date")

    if len(gold_daily) > 0:
        latest_price = gold_daily["Adj_Close"].iloc[-1]
    else:
        latest_price = gold_monthly["SIP_Buy_Price"].iloc[-1]
        
    current_val_today = gold_monthly["cum_units"].iloc[-1] * latest_price
    current_drop_pct = ((current_val_today - peak_wealth) / peak_wealth) * 100.0 if peak_wealth > 0 else 0.0
    
    terminal_date = gold_daily["Date"].iloc[-1] if len(gold_daily) > 0 else gold_monthly["SIP_Date"].iloc[-1]
    annual_return = compute_exact_xirr(gold_monthly["SIP_Date"].tolist(), monthly_sip, terminal_date, current_val_today)
    
    return {
        "ticker": "GOLDBEES.NS",
        "name": "Nippon India ETF Gold BeES",
        "total_months": total_months,
        "total_invested": total_invested,
        "current_val": current_val_today,
        "peak_wealth": peak_wealth,
        "peak_date": peak_date,
        "current_drop_pct": current_drop_pct,
        "worst_loss": worst_loss,
        "worst_date": worst_date,
        "annual_return": annual_return,
        "timeline_df": gold_monthly[["SIP_Date", "portfolio_val", "cum_invested", "net_pl"]]
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
    if total_months == 0 or len(sub) == 0:
        return {
            "tickers": selected_tickers,
            "num_stocks": num_stocks,
            "total_months": 0,
            "total_invested": 0.0,
            "current_val": 0.0,
            "peak_wealth": 0.0,
            "peak_date": pd.Timestamp.now(),
            "current_drop_pct": 0.0,
            "worst_loss": 0.0,
            "worst_date": pd.Timestamp.now(),
            "annual_return": 0.0,
            "timeline_df": pd.DataFrame(columns=["SIP_Date", "portfolio_val", "cum_invested", "net_pl"])
        }
        
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
    if len(tdf) == 0:
        return {
            "tickers": selected_tickers,
            "num_stocks": num_stocks,
            "total_months": 0,
            "total_invested": 0.0,
            "current_val": 0.0,
            "peak_wealth": 0.0,
            "peak_date": pd.Timestamp.now(),
            "current_drop_pct": 0.0,
            "worst_loss": 0.0,
            "worst_date": pd.Timestamp.now(),
            "annual_return": 0.0,
            "timeline_df": pd.DataFrame(columns=["SIP_Date", "portfolio_val", "cum_invested", "net_pl"])
        }
        
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
        if len(t_sub) == 0:
            continue
        total_units = (per_stock_sip / t_sub["SIP_Buy_Price"]).sum()
        daily_t = fact_daily[fact_daily["Ticker"] == t].sort_values("Date")
        if len(daily_t) > 0:
            latest_price = daily_t["Adj_Close"].iloc[-1]
        elif len(t_sub) > 0:
            latest_price = t_sub.sort_values("SIP_Date")["SIP_Buy_Price"].iloc[-1]
        else:
            latest_price = 0.0
        current_val_today += total_units * latest_price
        
    current_drop_pct = ((current_val_today - peak_wealth) / peak_wealth) * 100.0 if peak_wealth > 0 else 0.0
    terminal_date = fact_daily["Date"].max()
    annual_return = compute_exact_xirr(unique_dates, monthly_sip, terminal_date, current_val_today)
    
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
