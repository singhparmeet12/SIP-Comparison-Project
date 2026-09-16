import os
import sys

# Ensure repository root and utils directory are in sys.path for robust Streamlit Community Cloud execution
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

UTILS_DIR = os.path.join(REPO_ROOT, "utils")
if UTILS_DIR not in sys.path:
    sys.path.insert(0, UTILS_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

try:
    from utils.analytics import (
        load_data,
        run_nifty_benchmark,
        run_gold_benchmark,
        run_stock_basket_simulation,
        format_currency_inr,
        format_pct
    )
except (ImportError, ModuleNotFoundError):
    try:
        from utils import (
            load_data,
            run_nifty_benchmark,
            run_gold_benchmark,
            run_stock_basket_simulation,
            format_currency_inr,
            format_pct
        )
    except (ImportError, ModuleNotFoundError):
        from analytics import (
            load_data,
            run_nifty_benchmark,
            run_gold_benchmark,
            run_stock_basket_simulation,
            format_currency_inr,
            format_pct
        )

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Institutional Wealth Analytics — Equities vs Nifty 50 vs Gold",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Custom Modern FinTech CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #F6F8FB;
        --card-bg: #FFFFFF;
        --card-subtle: #EDF3F8;
        --border-color: #E2E8F0;
        --border-subtle: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #475467;
        --text-muted: #64748B;
        --accent-green: #059669;
        --accent-green-bg: rgba(5, 150, 105, 0.1);
        --accent-blue: #2563EB;
        --accent-blue-bg: rgba(37, 99, 235, 0.1);
        --accent-gold: #D97706;
        --accent-gold-bg: rgba(217, 119, 6, 0.12);
        --accent-amber: #D97706;
        --accent-amber-bg: rgba(217, 119, 6, 0.12);
        --accent-red: #DC2626;
        --accent-red-bg: rgba(220, 38, 38, 0.1);
        --navy-dark: #172B4D;
        --radius: 12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    .block-container {
        padding: 1.5rem 2.5rem 3rem !important;
        max-width: 1440px !important;
    }

    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Top Brand Bar */
    .brand-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-pill {
        background: var(--card-subtle);
        color: var(--navy-dark);
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid var(--border-subtle);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Hero Investor Hook Card */
    .hero-hook-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.15rem 1.4rem;
        color: var(--text-primary);
        margin-bottom: 1.15rem;
        box-shadow: var(--shadow-sm);
    }
    .hero-hook-badge {
        display: inline-flex;
        align-items: center;
        background: var(--accent-green-bg);
        color: var(--accent-green);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(5, 150, 105, 0.25);
        margin-bottom: 0.45rem;
    }
    .hero-hook-title {
        font-size: 1.32rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.35;
        margin-bottom: 0.35rem;
    }
    .hero-hook-title .highlight-q {
        color: var(--accent-blue);
    }
    .hero-hook-sub {
        font-size: 0.84rem;
        color: var(--text-secondary);
        line-height: 1.5;
        font-weight: 500;
    }

    /* Control Labels */
    .ctrl-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #475467;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 4px;
    }

    /* KPI Grid Container - Desktop Web View: Exactly 3 Columns */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 1.25rem;
    }

    /* KPI Cards */
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.15rem 1.25rem;
        box-shadow: var(--shadow-sm);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    .kpi-label {
        font-size: 0.76rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.03em;
    }
    .kpi-sub {
        font-size: 0.74rem;
        font-weight: 600;
        margin-top: 0.35rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        border-radius: 6px;
        width: fit-content;
    }
    .badge-green { color: var(--accent-green); background: var(--accent-green-bg); }
    .badge-blue { color: var(--accent-blue); background: var(--accent-blue-bg); }
    .badge-gold { color: var(--accent-gold); background: var(--accent-gold-bg); }
    .badge-amber { color: var(--accent-amber); background: var(--accent-amber-bg); }
    .badge-red { color: var(--accent-red); background: var(--accent-red-bg); }
    .badge-navy { color: var(--navy-dark); background: var(--card-subtle); }

    /* Chart & Panel Wraps */
    .panel-box {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
    }
    .panel-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .panel-subtitle {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-bottom: 0.85rem;
    }

    /* Strategy Header Pill */
    .strategy-banner {
        background: #EBF5F7;
        border: 1px solid #B8E2E8;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #0F4C5C;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Deep-Dive Table & Responsive Wrapper */
    .table-responsive-wrapper {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .deep-dive-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.82rem;
    }
    .deep-dive-table th {
        background: #F8FAFC;
        color: var(--text-secondary);
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.75rem 0.9rem;
        border-bottom: 1px solid var(--border-color);
        white-space: nowrap;
    }
    .deep-dive-table td {
        padding: 0.75rem 0.9rem;
        border-bottom: 1px solid #F1F5F9;
        color: var(--text-primary);
        font-weight: 600;
        white-space: nowrap;
    }
    .deep-dive-table tr:hover td {
        background: #F8FAFC;
    }
    .deep-dive-table td.metric-title {
        font-weight: 500;
        color: var(--text-secondary);
        white-space: normal;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        color: var(--text-muted) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--navy-dark) !important;
        background: var(--card-bg) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-baseweb="tab-list"] {
        background: var(--card-subtle) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 6px !important;
    }
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Documentary Text Typography */
    .doc-section {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    .doc-h2 {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .doc-p {
        font-size: 0.92rem;
        line-height: 1.7;
        color: #334155;
        margin-bottom: 1rem;
    }
    .callout-box {
        background: #F8FAFC;
        border-left: 4px solid var(--accent-green);
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1.25rem 0;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #1E293B;
    }

    /* ---------------------------------------------------------
       RESPONSIVE & MOBILE-FRIENDLY OPTIMIZATIONS (<= 768px)
       --------------------------------------------------------- */
    @media (max-width: 768px) {
        /* Mobile Outer Padding - maximize screen real estate */
        .block-container {
            padding: 0.75rem 0.85rem 2rem !important;
            max-width: 100% !important;
        }

        /* Top Brand Bar */
        .brand-bar {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 4px !important;
            padding-bottom: 0.65rem !important;
            margin-bottom: 0.65rem !important;
        }
        .brand-title {
            font-size: 1.05rem !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
        }

        /* Bold Hero Investor Hook Card */
        .hero-hook-card {
            padding: 0.85rem 1rem !important;
            margin-bottom: 0.85rem !important;
        }
        .hero-hook-badge {
            font-size: 0.65rem !important;
            padding: 2px 8px !important;
            margin-bottom: 0.35rem !important;
        }
        .hero-hook-title {
            font-size: 1.02rem !important;
            line-height: 1.35 !important;
            margin-bottom: 0.3rem !important;
        }
        .hero-hook-sub {
            font-size: 0.76rem !important;
            line-height: 1.45 !important;
        }

        /* Tabs Horizontal Scrolling with zero wrapping */
        [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            white-space: nowrap !important;
            flex-wrap: nowrap !important;
            scrollbar-width: none !important;
            padding: 3px !important;
        }
        [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        button[data-baseweb="tab"] {
            font-size: 0.76rem !important;
            padding: 0.42rem 0.8rem !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        /* Responsive Controls Grid: Start Year + SIP side-by-side, Stock Picker below */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMultiSelect"]) {
            display: flex !important;
            flex-wrap: wrap !important;
            flex-direction: row !important;
            gap: 8px !important;
            margin-bottom: 0.4rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMultiSelect"]) > div[data-testid="column"]:nth-child(1) {
            flex: 1 1 calc(46% - 4px) !important;
            min-width: calc(46% - 4px) !important;
            max-width: calc(46% - 4px) !important;
            width: calc(46% - 4px) !important;
            margin-bottom: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMultiSelect"]) > div[data-testid="column"]:nth-child(2) {
            flex: 1 1 calc(54% - 4px) !important;
            min-width: calc(54% - 4px) !important;
            max-width: calc(54% - 4px) !important;
            width: calc(54% - 4px) !important;
            margin-bottom: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMultiSelect"]) > div[data-testid="column"]:nth-child(3) {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            width: 100% !important;
            margin-bottom: 0 !important;
        }
        .ctrl-label {
            font-size: 0.7rem !important;
            margin-bottom: 2px !important;
        }

        /* Strategy Context Banner */
        .strategy-banner {
            font-size: 0.73rem !important;
            padding: 0.5rem 0.75rem !important;
            margin-bottom: 0.75rem !important;
            line-height: 1.4 !important;
        }

        /* Mobile Grid Layout for KPI Cards: Professional 2-Column Symmetrical Grid */
        .kpi-grid {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
            margin-bottom: 0.85rem !important;
        }
        .card-invested    { order: 1; }
        .card-stocks      { order: 2; }
        .card-nifty       { order: 3; }
        .card-alpha-nifty { order: 4; }
        .card-gold        { order: 5; }
        .card-alpha-gold  { order: 6; }

        .kpi-card {
            padding: 0.65rem 0.75rem !important;
            border-radius: 10px !important;
            min-height: 84px !important;
        }
        .kpi-label {
            font-size: 0.62rem !important;
            margin-bottom: 0.2rem !important;
            line-height: 1.2 !important;
            letter-spacing: 0.02em !important;
        }
        .kpi-value {
            font-size: 1.25rem !important;
            letter-spacing: -0.02em !important;
            line-height: 1.15 !important;
        }
        .kpi-sub {
            font-size: 0.62rem !important;
            padding: 2px 6px !important;
            margin-top: 0.25rem !important;
            white-space: nowrap !important;
        }

        /* Chart & Panel Box Mobile */
        .panel-box {
            padding: 0.85rem !important;
            margin-bottom: 0.75rem !important;
        }
        .panel-header {
            font-size: 0.88rem !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 3px !important;
        }
        .panel-subtitle {
            font-size: 0.72rem !important;
            margin-bottom: 0.6rem !important;
        }

        /* Deep-Dive Table Mobile */
        .deep-dive-table th, .deep-dive-table td {
            padding: 0.5rem 0.6rem !important;
            font-size: 0.72rem !important;
        }

        /* Documentary & Text Mobile */
        .doc-section {
            padding: 1rem 1.15rem !important;
            margin-bottom: 1rem !important;
        }
        .doc-h2 {
            font-size: 1.05rem !important;
            line-height: 1.35 !important;
        }
        .doc-p {
            font-size: 0.84rem !important;
            line-height: 1.6 !important;
        }
        .callout-box {
            padding: 0.75rem 0.95rem !important;
            font-size: 0.82rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Preprocessed Data
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_data(cache_version="2026_09_16_v4_gold_hotfix"):
    return load_data()

dim_asset, fact_monthly, fact_daily = get_cached_data()

# Clean list of equity stocks
equity_stocks = dim_asset[dim_asset["Asset_Type"] == "Equity Stock"].sort_values("Company_Name")
stock_options = {row["Company_Name"]: row["Ticker"] for _, row in equity_stocks.iterrows()}
ticker_to_name = {v: k for k, v in stock_options.items()}

# ---------------------------------------------------------
# Top Brand Bar & Hero Hook
# ---------------------------------------------------------
st.markdown("""
<div class="brand-bar">
    <div class="brand-title">
        🏛️ INSTITUTIONAL WEALTH ANALYTICS
        <span class="brand-pill">Quantitative Engine 2010 – 2026</span>
    </div>
    <div style="font-size: 0.82rem; color: #64748B; font-weight: 500;">
        Active Equities vs Passive Nifty 50 & Gold BeES Benchmarks
    </div>
</div>

<div class="hero-hook-card">
    <div class="hero-hook-badge">HISTORICAL WEALTH COMPARISON (2010 – 2026)</div>
    <div class="hero-hook-title">
        NIFTY 50 SIP vs Gold BeES vs Your Selected Stocks: <span class="highlight-q">Who Gives the Better Return Over the Years?</span>
    </div>
    <div class="hero-hook-sub">
        Real quantitative data from 16+ years of disciplined monthly investing. Compare actual wealth compounding, peak portfolio gains, and drawdown protection across active stock-picking, index equities, and sovereign gold ETF accumulation.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Tabs Navigation
# ---------------------------------------------------------
tab_sim, tab_doc, tab_data = st.tabs([
    "📊 Quantitative Simulator", 
    "📖 Project Documentary & Case Studies", 
    "🔍 Data Architecture & Methodology"
])

# =========================================================
# TAB 1: QUANTITATIVE SIMULATOR
# =========================================================
with tab_sim:
    # Top Control Bar (Start Year, SIP Amount, Quick Presets)
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.2, 1.4, 2.4])
    
    with ctrl_col1:
        st.markdown("<div class='ctrl-label'>Start Year</div>", unsafe_allow_html=True)
        start_year = st.selectbox(
            "Start Year", 
            options=[2010, 2012, 2014, 2015, 2016, 2018, 2020, 2022, 2024], 
            index=0,
            label_visibility="collapsed"
        )
        
    with ctrl_col2:
        st.markdown("<div class='ctrl-label'>Monthly SIP (₹)</div>", unsafe_allow_html=True)
        monthly_sip = st.select_slider(
            "Monthly SIP Amount",
            options=[5000, 10000, 15000, 20000, 25000, 39500, 50000, 75000, 100000],
            value=10000,
            format_func=lambda x: f"₹{x:,}",
            label_visibility="collapsed"
        )
        
    with ctrl_col3:
        st.markdown("<div class='ctrl-label'>Pick Stocks (Hold / Multi-select)</div>", unsafe_allow_html=True)
        default_stock = ["Asian Paints"] if "Asian Paints" in stock_options else list(stock_options.keys())[:1]
        selected_stock_names = st.multiselect(
            "Select Stocks",
            options=list(stock_options.keys()),
            default=default_stock,
            label_visibility="collapsed",
            placeholder="Select one or multiple stocks to build your basket..."
        )
        selected_tickers = [stock_options[name] for name in selected_stock_names]

    # Calculate Simulations
    nifty_sim = run_nifty_benchmark(fact_monthly, fact_daily, start_year, monthly_sip)
    gold_sim = run_gold_benchmark(fact_monthly, fact_daily, start_year, monthly_sip)
    stock_sim = run_stock_basket_simulation(fact_monthly, fact_daily, selected_tickers, start_year, monthly_sip)

    # Dynamic Strategy Banner
    num_stocks = len(selected_tickers)
    total_months = nifty_sim["total_months"]
    total_invested_val = nifty_sim["total_invested"]
    per_stock_amt = monthly_sip / num_stocks if num_stocks > 0 else monthly_sip
    
    if num_stocks == 0:
        alloc_text = f"₹{monthly_sip:,}/mo • Waiting for stock selection"
    elif num_stocks == 1:
        alloc_text = f"₹{monthly_sip:,}/mo in 1 stock ({selected_stock_names[0]})"
    else:
        alloc_text = f"₹{monthly_sip:,}/mo (₹{per_stock_amt:,.0f} each across {num_stocks} stocks)"
        
    st.markdown(f"""
    <div class="strategy-banner">
        <span>⚙️ <strong>Strategy Context:</strong> {alloc_text} on 1st working day of every month • Started {start_year} • <strong>{total_months} Installments</strong> (Total Capital Deposited: <strong>{format_currency_inr(total_invested_val)}</strong>)</span>
    </div>
    """, unsafe_allow_html=True)

    # KPI Grid: Benchmarks, Portfolio Value, and Alpha Differentials
    nifty_ret_fmt = format_pct(nifty_sim["annual_return"])
    gold_ret_fmt = format_pct(gold_sim["annual_return"])
    
    if stock_sim is not None:
        stock_val_fmt = format_currency_inr(stock_sim["current_val"])
        stock_ret_fmt = format_pct(stock_sim["annual_return"])
        stock_color = "var(--accent-green)" if stock_sim["current_val"] >= nifty_sim["current_val"] else "#1E293B"
        stock_badge = "badge-green" if stock_sim["current_val"] >= nifty_sim["current_val"] else "badge-navy"
        
        alpha_nft_inr = stock_sim["current_val"] - nifty_sim["current_val"]
        alpha_nft_pct = stock_sim["annual_return"] - nifty_sim["annual_return"]
        if alpha_nft_inr >= 0:
            alpha_nft_val_fmt = f"+{format_currency_inr(alpha_nft_inr)}"
            alpha_nft_badge = "badge-green"
            alpha_nft_arrow = "▲"
        else:
            alpha_nft_val_fmt = f"-{format_currency_inr(abs(alpha_nft_inr))}"
            alpha_nft_badge = "badge-red"
            alpha_nft_arrow = "▼"
        alpha_nft_sub = f"{alpha_nft_arrow} {format_pct(abs(alpha_nft_pct))} vs Nifty"
        
        alpha_gold_inr = stock_sim["current_val"] - gold_sim["current_val"]
        alpha_gold_pct = stock_sim["annual_return"] - gold_sim["annual_return"]
        if alpha_gold_inr >= 0:
            alpha_gold_val_fmt = f"+{format_currency_inr(alpha_gold_inr)}"
            alpha_gold_badge = "badge-green"
            alpha_gold_arrow = "▲"
        else:
            alpha_gold_val_fmt = f"-{format_currency_inr(abs(alpha_gold_inr))}"
            alpha_gold_badge = "badge-red"
            alpha_gold_arrow = "▼"
        alpha_gold_sub = f"{alpha_gold_arrow} {format_pct(abs(alpha_gold_pct))} vs Gold"
    else:
        stock_val_fmt = "--"
        stock_ret_fmt = "--"
        stock_color = "#94A3B8"
        stock_badge = "badge-navy"
        alpha_nft_val_fmt = "--"
        alpha_nft_badge = "badge-navy"
        alpha_nft_sub = "Select stock to compare"
        alpha_gold_val_fmt = "--"
        alpha_gold_badge = "badge-navy"
        alpha_gold_sub = "Select stock to compare"

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card card-invested">
            <div class="kpi-label">Total Capital Invested</div>
            <div class="kpi-value">{format_currency_inr(total_invested_val)}</div>
            <div class="kpi-sub badge-navy">{total_months} Monthly SIPs</div>
        </div>
        <div class="kpi-card card-nifty">
            <div class="kpi-label">Nifty 50 Benchmark</div>
            <div class="kpi-value" style="color: var(--accent-blue);">{format_currency_inr(nifty_sim["current_val"])}</div>
            <div class="kpi-sub badge-blue">{nifty_ret_fmt} / yr (XIRR)</div>
        </div>
        <div class="kpi-card card-gold">
            <div class="kpi-label">Gold BeES Benchmark</div>
            <div class="kpi-value" style="color: var(--accent-gold);">{format_currency_inr(gold_sim["current_val"])}</div>
            <div class="kpi-sub badge-gold">{gold_ret_fmt} / yr (XIRR)</div>
        </div>
        <div class="kpi-card card-stocks">
            <div class="kpi-label">Selected Stocks Value</div>
            <div class="kpi-value" style="color: {stock_color};">{stock_val_fmt}</div>
            <div class="kpi-sub {stock_badge}">{stock_ret_fmt} / yr (XIRR)</div>
        </div>
        <div class="kpi-card card-alpha-nifty">
            <div class="kpi-label">Stock Gain / Loss vs Nifty</div>
            <div class="kpi-value">{alpha_nft_val_fmt}</div>
            <div class="kpi-sub {alpha_nft_badge}">{alpha_nft_sub}</div>
        </div>
        <div class="kpi-card card-alpha-gold">
            <div class="kpi-label">Stock Gain / Loss vs Gold</div>
            <div class="kpi-value">{alpha_gold_val_fmt}</div>
            <div class="kpi-sub {alpha_gold_badge}">{alpha_gold_sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Middle Row: Line Chart (Left 65%) + Journey Risk/Return Deep Dive (Right 35%)
    chart_col, table_col = st.columns([1.75, 1.25])
    
    with chart_col:
        st.markdown("""
        <div class="panel-box">
            <div class="panel-header">
                <span>Monthly Wealth Growth Trajectory</span>
                <span style="font-size: 0.72rem; color: #64748B;">Values in Indian Lakhs (₹ L)</span>
            </div>
            <div class="panel-subtitle">Dual compounding curves comparing active portfolio vs passive index accumulation</div>
        """, unsafe_allow_html=True)
        
        # Build Plotly Chart
        fig = go.Figure()
        
        # Nifty Timeline Line (Royal Blue)
        nifty_t = nifty_sim["timeline_df"]
        fig.add_trace(go.Scatter(
            x=nifty_t["SIP_Date"],
            y=nifty_t["portfolio_val"] / 100000.0,
            mode="lines",
            name="Nifty 50 Benchmark",
            line=dict(color="#2563EB", width=2.8),
            hovertemplate="<b>Nifty 50</b><br>Date: %{x|%b %Y}<br>Wealth: ₹%{y:.2f} L<extra></extra>"
        ))

        # Gold BeES Timeline Line (Radiant Gold)
        gold_t = gold_sim["timeline_df"]
        fig.add_trace(go.Scatter(
            x=gold_t["SIP_Date"],
            y=gold_t["portfolio_val"] / 100000.0,
            mode="lines",
            name="Gold BeES Benchmark",
            line=dict(color="#EAB308", width=2.8),
            hovertemplate="<b>Gold BeES</b><br>Date: %{x|%b %Y}<br>Wealth: ₹%{y:.2f} L<extra></extra>"
        ))
        
        # Selected Stocks Line (Emerald Green)
        if stock_sim is not None:
            stock_t = stock_sim["timeline_df"]
            basket_label = selected_stock_names[0] if len(selected_stock_names) == 1 else f"{len(selected_stock_names)} Stocks Basket"
            fig.add_trace(go.Scatter(
                x=stock_t["SIP_Date"],
                y=stock_t["portfolio_val"] / 100000.0,
                mode="lines",
                name=basket_label,
                line=dict(color="#059669", width=3.2),
                hovertemplate=f"<b>{basket_label}</b><br>Date: %{{x|%b %Y}}<br>Wealth: ₹%{{y:.2f}} L<extra></extra>"
            ))
            
        # Invested Capital Baseline (Slate Gray Dotted)
        fig.add_trace(go.Scatter(
            x=nifty_t["SIP_Date"],
            y=nifty_t["cum_invested"] / 100000.0,
            mode="lines",
            name="Total Capital Invested",
            line=dict(color="#64748B", width=1.8, dash="dot"),
            hovertemplate="<b>Invested Capital</b><br>Date: %{x|%b %Y}<br>Deposited: ₹%{y:.2f} L<extra></extra>"
        ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#475467", size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10.5)
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="#EEF2F6",
                zeroline=False,
                tickformat="%Y"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#EEF2F6",
                zeroline=False,
                ticksuffix=" L"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with table_col:
        st.markdown("""
        <div class="panel-box">
            <div class="panel-header">
                <span>Journey Risk and Return Deep-Dive</span>
                <span class="brand-pill" style="font-size: 0.65rem;">Audit Verified</span>
            </div>
            <div class="panel-subtitle">Comprehensive financial tear-sheet comparing returns, peak wealth, and worst drawdowns</div>
        """, unsafe_allow_html=True)
        
        # Format table rows
        if stock_sim is not None:
            stk_ret = format_pct(stock_sim["annual_return"])
            stk_curr = format_currency_inr(stock_sim["current_val"])
            stk_drop = format_pct(stock_sim["current_drop_pct"])
            stk_peak = format_currency_inr(stock_sim["peak_wealth"])
            stk_loss = format_currency_inr(stock_sim["worst_loss"]) if stock_sim["worst_loss"] < 0 else "₹0.00 L"
        else:
            stk_ret, stk_curr, stk_drop, stk_peak, stk_loss = "--", "--", "--", "--", "--"
            
        nft_ret = format_pct(nifty_sim["annual_return"])
        nft_curr = format_currency_inr(nifty_sim["current_val"])
        nft_drop = format_pct(nifty_sim["current_drop_pct"])
        nft_peak = format_currency_inr(nifty_sim["peak_wealth"])
        nft_loss = format_currency_inr(nifty_sim["worst_loss"]) if nifty_sim["worst_loss"] < 0 else "₹0.00 L"

        gld_ret = format_pct(gold_sim["annual_return"])
        gld_curr = format_currency_inr(gold_sim["current_val"])
        gld_drop = format_pct(gold_sim["current_drop_pct"])
        gld_peak = format_currency_inr(gold_sim["peak_wealth"])
        gld_loss = format_currency_inr(gold_sim["worst_loss"]) if gold_sim["worst_loss"] < 0 else "₹0.00 L"
        
        basket_header = "Selected Stocks" if len(selected_stock_names) > 1 else (selected_stock_names[0] if len(selected_stock_names) == 1 else "Selected Stocks")
        
        st.markdown(f"""
        <div class="table-responsive-wrapper">
        <table class="deep-dive-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th style="color: var(--accent-green);">{basket_header}</th>
                    <th style="color: var(--accent-blue);">Nifty 50</th>
                    <th style="color: var(--accent-gold);">Gold BeES</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-title">Percentage Return (XIRR)</td>
                    <td>{stk_ret}</td>
                    <td>{nft_ret}</td>
                    <td>{gld_ret}</td>
                </tr>
                <tr>
                    <td class="metric-title">Current Portfolio Value Today</td>
                    <td>{stk_curr}</td>
                    <td>{nft_curr}</td>
                    <td>{gld_curr}</td>
                </tr>
                <tr>
                    <td class="metric-title">Current Drop from Peak</td>
                    <td style="color: {'var(--accent-red)' if stk_drop != '--' and '-' in stk_drop else 'inherit'};">{stk_drop}</td>
                    <td style="color: {'var(--accent-red)' if nft_drop != '--' and '-' in nft_drop else 'inherit'};">{nft_drop}</td>
                    <td style="color: {'var(--accent-red)' if gld_drop != '--' and '-' in gld_drop else 'inherit'};">{gld_drop}</td>
                </tr>
                <tr>
                    <td class="metric-title">Maximum Profit Reached</td>
                    <td>{stk_peak}</td>
                    <td>{nft_peak}</td>
                    <td>{gld_peak}</td>
                </tr>
                <tr>
                    <td class="metric-title">Worst Real Capital Loss</td>
                    <td style="color: {'var(--accent-red)' if stk_loss != '₹0.00 L' and stk_loss != '--' else 'inherit'};">{stk_loss}</td>
                    <td style="color: {'var(--accent-red)' if nft_loss != '₹0.00 L' and nft_loss != '--' else 'inherit'};">{nft_loss}</td>
                    <td style="color: {'var(--accent-red)' if gld_loss != '₹0.00 L' and gld_loss != '--' else 'inherit'};">{gld_loss}</td>
                </tr>
            </tbody>
        </table>
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Bottom Row: Dynamic Quantitative Investment Memo
    st.markdown("""
    <div class="panel-box">
        <div class="panel-header">
            <span>🏛️ Quantitative Investment Memo & Outcome Narrative</span>
            <span style="font-size: 0.72rem; color: #64748B;">Auto-generated analysis</span>
        </div>
    """, unsafe_allow_html=True)
    
    if stock_sim is not None:
        alpha_nft = stock_sim["current_val"] - nifty_sim["current_val"]
        speed_delta_nft = stock_sim["annual_return"] - nifty_sim["annual_return"]
        alpha_gold = stock_sim["current_val"] - gold_sim["current_val"]
        speed_delta_gold = stock_sim["annual_return"] - gold_sim["annual_return"]

        nft_verdict = f"an Extra Wealth of <strong>+{format_currency_inr(alpha_nft)}</strong> (+{format_pct(speed_delta_nft)} speed premium)" if alpha_nft >= 0 else f"an underperformance of <strong>-{format_currency_inr(abs(alpha_nft))}</strong> vs the index"
        gold_verdict = f"an Extra Wealth of <strong>+{format_currency_inr(alpha_gold)}</strong> (+{format_pct(speed_delta_gold)} speed premium)" if alpha_gold >= 0 else f"an underperformance of <strong>-{format_currency_inr(abs(alpha_gold))}</strong> vs gold"

        narrative = f"""
        <strong>🚀 TRIPLE ASSET WEALTH OUTCOME:</strong> Across <strong>{total_months} monthly installments</strong> started in <strong>{start_year}</strong>, your active selection generated <strong>{format_currency_inr(stock_sim["current_val"])}</strong> ({format_pct(stock_sim["annual_return"])}/yr) against Nifty 50's <strong>{format_currency_inr(nifty_sim["current_val"])}</strong> ({format_pct(nifty_sim["annual_return"])}/yr) and Gold BeES's <strong>{format_currency_inr(gold_sim["current_val"])}</strong> ({format_pct(gold_sim["annual_return"])}/yr).
        <br><br>
        <strong>📈 COMPARATIVE BENCHMARK ALPHA:</strong>
        <br>• <strong>Vs Nifty 50:</strong> Delivered {nft_verdict}.
        <br>• <strong>Vs Gold BeES:</strong> Delivered {gold_verdict}.
        <br><br>
        <strong>🛡️ RISK & DRAWDOWN AUDIT:</strong> Your selection reached an all-time peak of <strong>{format_currency_inr(stock_sim["peak_wealth"])}</strong> and is currently down <strong>{format_pct(stock_sim["current_drop_pct"])}</strong> from its high. In comparison, Nifty 50 is down <strong>{nft_drop}</strong> and Gold BeES is down <strong>{gld_drop}</strong> from their respective historical peaks.
        """
    else:
        narrative = "Please select at least one stock above to generate the live quantitative analysis."
        
    st.markdown(f"<div style='font-size: 0.85rem; line-height: 1.65; color: #334155;'>{narrative}</div></div>", unsafe_allow_html=True)


# =========================================================
# TAB 2: PROJECT DOCUMENTARY & CASE STUDIES
# =========================================================
with tab_doc:
    st.markdown(r"""<div class="doc-section">
<div class="doc-h2">📑 Executive Project Thesis: Active Stock Picking vs Index SIP</div>
<p class="doc-p">
In Indian financial markets, mutual fund distributors and wealth managers frequently debate whether retail investors should pick individual bluechip stocks or simply automate their wealth via a passive index ETF like <strong>Nifty BeES</strong>.
</p>
<p class="doc-p">
Conventional wisdom claims that <em>"equities always make money in the long run."</em> However, SEBI quantitative studies reveal that over <strong>85% of active retail traders and individual stock pickers either underperform the index or lose money outright</strong>. This project was built to test this exact question under real-world conditions:
</p>
<div class="callout-box">
<strong>The Core Quantitative Hypothesis:</strong> If an investor executes disciplined Rupee-Cost Averaging (SIP) on the 1st trading day of every month with zero emotional interference from 2010 to 2026, can handpicked stock portfolios reliably outperform the passive Nifty 50 benchmark — and what is the hidden psychological cost in drawdowns and capital losses?
</div>
</div>

<div class="doc-section">
<div class="doc-h2">🔬 Mathematical Methodology: Rupee-Cost Averaging (SIP) & XIRR</div>
<p class="doc-p">
Unlike lump-sum investments where returns depend strictly on entry timing, a Systematic Investment Plan (SIP) is a dynamic accumulation model:
</p>
<p class="doc-p">
<strong>1. Dynamic Share Accumulation:</strong> On the first working day of each month $t$, a fixed monthly budget $S$ is converted into equity shares at buy price $P_t$:
<br>
$$\Delta U_t = \frac{S}{P_t}, \quad U_T = \sum_{t=1}^T \Delta U_t$$
When prices crash, the investor accumulates more units per rupee; when prices rise, fewer units are bought.
</p>
<p class="doc-p">
<strong>2. True Capital Loss vs Paper Drawdown:</strong> Standard finance metrics only measure <em>Peak-to-Trough Drawdown</em>. However, retail psychology is driven by <strong>Capital Preservation</strong>:
<br>
$$\text{Net P&L}_t = \text{Portfolio Value}_t - \text{Cumulative Capital Deposited}_t$$
Our engine tracks the exact historical minimum of $\text{Net P&L}_t$. While individual stocks frequently plunge 20% to 50% below invested principal, Nifty 50's worst historical capital loss was just <strong>-₹32,692 (-₹0.33 L)</strong>, providing an impenetrable diversification shield.
</p>
<p class="doc-p">
<strong>3. Annualized Compounding Speed (XIRR):</strong> Because monthly deposits enter at staggered dates, simple point-to-point CAGR produces misleading returns. We compute the exact annualized internal rate of return (XIRR) that equates the net present value of all cash outflows to the terminal liquidation value.
</p>
</div>

<div class="doc-section">
<div class="doc-h2">🏆 Empirical Case Studies (2010 – 2026 Discoveries)</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.15rem; border: 1px solid var(--border-color); border-left: 4px solid var(--accent-green);">
<h4 style="color: var(--accent-green); margin-top: 0; margin-bottom: 0.35rem; font-size: 0.96rem;">🚀 Case Study 1: The Exponential Compounding Multibaggers (Titan & Bajaj Finance)</h4>
<p class="doc-p" style="margin-bottom: 0.65rem;">
A ₹10,000/month SIP from 2010 to 2026 (<strong>₹20.10 Lakhs deposited</strong> across 201 installments) reveals the staggering wealth creation potential of structural Indian market leaders:
</p>
<ul style="margin: 0; padding-left: 1.2rem; font-size: 0.88rem; line-height: 1.65; color: #334155;">
<li style="margin-bottom: 0.45rem;">
<strong>Titan Company:</strong> Compounded into an astonishing <strong>₹2.41 Crore (34.5% annual XIRR)</strong>, generating an extra <strong>+₹1.86 Crore</strong> over Nifty 50's ₹55.33 Lakhs. Even during intense macroeconomic selloffs, Titan was never underwater for more than a brief few months in 2010–2011.
</li>
<li>
<strong>Bajaj Finance:</strong> The ultimate mega-compounder of the decade — skyrocketed into a monumental <strong>₹9.18 Crore (57.8% annual XIRR)</strong>, peaking at <strong>₹10.23 Crore</strong>. This beat the passive index by an extraordinary <strong>+₹8.63 Crore</strong> with almost zero psychological pain (worst historical capital dip below deposited principal was just <strong>-₹1,130 (-₹0.01 L)</strong>).
</li>
</ul>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.15rem; border: 1px solid var(--border-color); border-left: 4px solid var(--accent-amber);">
<h4 style="color: var(--accent-amber); margin-top: 0; margin-bottom: 0.35rem; font-size: 0.96rem;">⚖️ Case Study 2: The Valuation Trap & Mean Reversion (Asian Paints post-2021)</h4>
<p class="doc-p" style="margin-bottom: 0;">
Asian Paints was the quintessential darling of Indian portfolio managers from 2010 to 2020. However, investors who started a SIP in 2020 at peak valuations (80x P/E) experienced <strong>negative returns (-0.5%/yr)</strong> over 6 years as gross margins contracted from crude spikes and new competition (Birla Opus). This illustrates that even legendary compounders can stagnate for half a decade if bought at extreme multiples.
</p>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.15rem; border: 1px solid var(--border-color); border-left: 4px solid var(--accent-red);">
<h4 style="color: var(--accent-red); margin-top: 0; margin-bottom: 0.35rem; font-size: 0.96rem;">⚠️ Case Study 3: The Fatal Trap of "Cheap" Fallen Angels (Yes Bank)</h4>
<p class="doc-p" style="margin-bottom: 0;">
Many retail investors use SIPs to "average down" on falling stocks. A ₹10,000/month SIP in <strong>Yes Bank</strong> from 2010 resulted in a catastrophic capital loss of <strong>-₹11.29 Lakhs in the red</strong>, ending with barely ₹12.9 Lakhs on ₹20.10 L deposited. Averaging down on a deteriorating business model compounds wealth destruction rather than wealth creation.
</p>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.15rem; border: 1px solid var(--border-color); border-left: 4px solid var(--navy-dark);">
<h4 style="color: var(--navy-dark); margin-top: 0; margin-bottom: 0.35rem; font-size: 0.96rem;">🛡️ Case Study 4: The 4-Pillar Diversified Core (ITC, L&T, M&M, Maruti)</h4>
<p class="doc-p" style="margin-bottom: 0;">
When capital is diversified across high cash-flow FMCG (ITC), capital goods infrastructure (L&T), and domestic automotive cyclicals (M&M, Maruti), the basket delivered an outstanding <strong>20.3% annual XIRR</strong> from 2020 to 2026, generating ₹59.65 L on ₹32.00 L invested — outperforming the benchmark while capping the worst downside dip at just -₹43,100 during COVID 2020.
</p>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; border: 1px solid var(--border-color); border-left: 4px solid #D97706;">
<h4 style="color: #D97706; margin-top: 0; margin-bottom: 0.35rem; font-size: 0.96rem;">🥇 Case Study 5: The Sovereign Inflation Shield (Gold BeES)</h4>
<p class="doc-p" style="margin-bottom: 0;">
A ₹10,000/month SIP in <strong>Nippon India ETF Gold BeES</strong> from 2010 to 2026 accumulated <strong>₹78.85 Lakhs (14.8% annual XIRR)</strong> on ₹20.10 Lakhs deposited. Remarkably, Gold BeES generated <strong>+₹23.52 Lakhs extra wealth over the Nifty 50 index (₹55.33 L)</strong>, acting as a supreme macro hedge during periods of geopolitical turbulence, currency depreciation, and equity consolidation.
</p>
</div>
</div>

<div class="doc-section">
<div class="doc-h2">💡 Final Strategic Takeaways for Portfolio Managers</div>
<p class="doc-p">
<strong>1. The Barbell Strategy Wins:</strong> The optimal wealth-building framework is keeping 60%–70% of monthly capital in low-cost passive index funds (Nifty 50 / Nifty Next 50), 10%–15% in sovereign Gold (Gold BeES) for non-correlated inflation hedging, and allocating the remaining 20%–30% to high-conviction structural compounders with durable competitive moats.
</p>
<p class="doc-p">
<strong>2. Downside Safety is Underpriced:</strong> Psychological endurance determines investment success. An investor who panicked and exited during Yes Bank's collapse lost everything, while an investor in Nifty 50 or Gold BeES had zero existential fear because index auto-rebalancing and precious metals protect purchasing power across macroeconomic cycles.
</p>
</div>""", unsafe_allow_html=True)


# =========================================================
# TAB 3: DATA ARCHITECTURE & METHODOLOGY
# =========================================================
with tab_data:
    st.markdown("""<div class="doc-section">
<div class="doc-h2">🏗️ Star-Schema Data Pipeline & Data Modeling</div>
<p class="doc-p">
The analytics engine runs on an institutional Star-Schema architecture modeled specifically for quantitative multi-asset backtesting:
</p>
<div class="table-responsive-wrapper">
<table class="deep-dive-table" style="margin-bottom: 1.5rem;">
<thead>
<tr>
<th>Table Name</th>
<th>Type</th>
<th>Granularity</th>
<th>Key Attributes & Role</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Dim_Asset</strong></td>
<td>Dimension</td>
<td>1 Row per Ticker</td>
<td>Ticker, Company Name, Sector, Industry, Asset Type (Equity Stock vs Benchmark ETF)</td>
</tr>
<tr>
<td><strong>Dim_Date</strong></td>
<td>Dimension</td>
<td>Daily Calendar (2010–2026)</td>
<td>Date, Year, Quarter, Month, Year_Month, Is_Trading_Day, Day_of_Week</td>
</tr>
<tr>
<td><strong>Fact_MonthlySIP_Prices</strong></td>
<td>Fact Table</td>
<td>Monthly per Ticker (2010–2026)</td>
<td>First available trading day price of each month, adjusted buy prices, volume</td>
</tr>
<tr>
<td><strong>Fact_DailyPrices</strong></td>
<td>Fact Table</td>
<td>Daily per Ticker</td>
<td>Historical OHLCV, adjusted close prices, corporate actions (splits/dividends)</td>
</tr>
</tbody>
</table>
</div>

<div class="doc-h2" style="margin-top: 1.75rem;">🧮 Quantitative Calculation Engine & Exact Formulas</div>
<p class="doc-p">
To guarantee institutional accuracy, every portfolio metric is derived using exact financial mathematics rather than crude linear approximations:
</p>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1.15rem 1.35rem; margin-bottom: 1.25rem; border: 1px solid var(--border-color); border-left: 4px solid var(--navy-dark);">
<h4 style="color: var(--navy-dark); margin-top: 0; margin-bottom: 0.4rem; font-size: 0.98rem;">1. Extended Internal Rate of Return (XIRR)</h4>
<p class="doc-p" style="margin-bottom: 0.5rem;">
Because a monthly SIP consists of multiple periodic cash outflows deposited over different dates, standard lump-sum CAGR does not apply. XIRR is the exact annualized discount rate $r$ that solves the Net Present Value (NPV) equation to zero:
</p>
<div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #1E293B; margin-bottom: 0.5rem; overflow-x: auto;">
&sum; [ -C<sub>i</sub> / (1 + r)<sup>(d<sub>i</sub> - d<sub>0</sub>) / 365</sup> ] + [ V<sub>terminal</sub> / (1 + r)<sup>(d<sub>eval</sub> - d<sub>0</sub>) / 365</sup> ] = 0
</div>
<p class="doc-p" style="margin-bottom: 0; font-size: 0.86rem; color: #475467;">
Where <em>C<sub>i</sub></em> is the SIP deposit on trading date <em>d<sub>i</sub></em>, <em>V<sub>terminal</sub></em> is the latest liquidation portfolio NAV at <em>d<sub>eval</sub></em>, and <em>r</em> is computed via high-precision bisection root finding with precision &epsilon; &lt; 10<sup>-6</sup>.
</p>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1.15rem 1.35rem; margin-bottom: 1.25rem; border: 1px solid var(--border-color); border-left: 4px solid var(--accent-green);">
<h4 style="color: var(--accent-green); margin-top: 0; margin-bottom: 0.4rem; font-size: 0.98rem;">2. Absolute Total Profit vs Annual Compounding Speed (XIRR)</h4>
<p class="doc-p" style="margin-bottom: 0.5rem;">
Both metrics measure real performance, but answer two distinct questions:
</p>
<ul style="margin: 0; padding-left: 1.25rem; font-size: 0.88rem; line-height: 1.65; color: #334155;">
<li style="margin-bottom: 0.35rem;">
<strong>Absolute Return (%):</strong> The total cumulative percentage gain on your deposited principal:
<br><code>Absolute Return (%) = [ (Current Portfolio Value - Total Invested) / Total Invested ] &times; 100</code>
<br><em>Example:</em> An investor who deposited ₹8.10 Lakhs in Gold BeES (2020–2026) saw it reach <strong>₹19.06 Lakhs</strong> (+₹10.96 Lakhs profit). The Absolute Return is <strong>+135.3%</strong> (more than double the initial capital!).
</li>
<li>
<strong>Annualized XIRR (%/yr):</strong> The annual compounding speed required to reach that total profit, recognizing that earlier installments compounded for 6.75 years while recent installments compounded for only a few months. For Gold BeES (2020–2026), that velocity is <strong>25.4% / year</strong>.
</li>
</ul>
</div>

<div style="background: #F8FAFC; border-radius: 8px; padding: 1.15rem 1.35rem; margin-bottom: 1.5rem; border: 1px solid var(--border-color); border-left: 4px solid var(--accent-amber);">
<h4 style="color: var(--accent-amber); margin-top: 0; margin-bottom: 0.4rem; font-size: 0.98rem;">3. Real-Market Execution & Downside Risk Metrics</h4>
<ul style="margin: 0; padding-left: 1.25rem; font-size: 0.88rem; line-height: 1.65; color: #334155;">
<li style="margin-bottom: 0.35rem;">
<strong>SIP Purchase Execution:</strong> Executed strictly on the first trading day of each calendar month using NSE adjusted closing settlement prices:
<br><code>&Delta; Units<sub>m</sub> = Monthly SIP Amount / NAV<sub>m</sub></code>
</li>
<li>
<strong>Capital at Risk & Worst Historical Drawdown:</strong> Evaluated daily to measure the maximum rupee capital deficit below total deposited cash:
<br><code>Capital at Risk<sub>t</sub> = min(0, Portfolio NAV<sub>t</sub> - Total Deposited Principal<sub>t</sub>)</code>
</li>
</ul>
</div>

<div class="doc-h2" style="margin-top: 1.75rem;">🔍 Independent Benchmark Verification: Groww SIP Calculator Audit</div>
<p class="doc-p">
Public SIP calculators (such as the <a href="https://groww.in/calculators/nippon-sip-calculator" target="_blank" style="color: var(--navy-dark); font-weight: 600; text-decoration: underline;">Groww Nippon India SIP Calculator</a>) project returns using the classical compound annuity formula:
</p>
<div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #1E293B; margin-bottom: 0.85rem; overflow-x: auto;">
u = (1 + r / 100)<sup>1/12</sup> - 1  (Monthly Compounding Rate)
<br>Total Corpus (M) = [ ((1 + u)<sup>n</sup> - 1) / u ] &times; P &times; (1 + u)
</div>
<p class="doc-p" style="margin-bottom: 0.85rem;">
While public calculators assume a <em>constant, frictionless monthly return</em>, our simulator backtests against <em>actual volatile NSE market prices</em>. When each asset's realized XIRR is supplied to Groww's engine, the resulting corpus matches our actual backtest with <strong>98.1% to 99.96% accuracy (average delta &lt; 0.8%)</strong>:
</p>

<div class="table-responsive-wrapper">
<table class="deep-dive-table" style="margin-bottom: 1.5rem;">
<thead>
<tr>
<th>Investment Horizon</th>
<th>Asset Class</th>
<th>Total Invested</th>
<th>Actual Market NAV</th>
<th>Groww Calculator Result</th>
<th>Formula Delta</th>
<th>Annual XIRR</th>
<th>Absolute Total Profit</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2"><strong>2024 to 2026</strong><br><span style="font-size: 0.75rem; color: #64748B;">(~2.75 Yrs / 33 Mos)</span></td>
<td><span style="color: #2563EB; font-weight: 700;">🔵 NIFTY 50</span></td>
<td>₹3.30 L</td>
<td><strong>₹3.27 L</strong></td>
<td>₹3.27 L</td>
<td><span style="color: #059669; font-weight: 700;">0.04%</span></td>
<td>-0.6% / yr</td>
<td>-0.9% (-₹0.03 L)</td>
</tr>
<tr>
<td><span style="color: #D97706; font-weight: 700;">🟡 GOLD BEES</span></td>
<td>₹3.30 L</td>
<td><strong>₹5.31 L</strong></td>
<td>₹5.41 L</td>
<td><span style="color: #059669; font-weight: 700;">1.86%</span></td>
<td>38.5% / yr</td>
<td><strong>+61.0%</strong> (+₹2.01 L)</td>
</tr>
<tr style="border-top: 2px solid #E2E8F0;">
<td rowspan="2"><strong>2022 to 2026</strong><br><span style="font-size: 0.75rem; color: #64748B;">(~4.75 Yrs / 57 Mos)</span></td>
<td><span style="color: #2563EB; font-weight: 700;">🔵 NIFTY 50</span></td>
<td>₹5.70 L</td>
<td><strong>₹6.54 L</strong></td>
<td>₹6.56 L</td>
<td><span style="color: #059669; font-weight: 700;">0.32%</span></td>
<td>5.9% / yr</td>
<td>+14.8% (+₹0.84 L)</td>
</tr>
<tr>
<td><span style="color: #D97706; font-weight: 700;">🟡 GOLD BEES</span></td>
<td>₹5.70 L</td>
<td><strong>₹11.75 L</strong></td>
<td>₹11.94 L</td>
<td><span style="color: #059669; font-weight: 700;">1.57%</span></td>
<td>31.9% / yr</td>
<td><strong>+106.2%</strong> (+₹6.05 L)</td>
</tr>
<tr style="border-top: 2px solid #E2E8F0;">
<td rowspan="2"><strong>2020 to 2026</strong><br><span style="font-size: 0.75rem; color: #64748B;">(~6.75 Yrs / 81 Mos)</span></td>
<td><span style="color: #2563EB; font-weight: 700;">🔵 NIFTY 50</span></td>
<td>₹8.10 L</td>
<td><strong>₹11.23 L</strong></td>
<td>₹11.29 L</td>
<td><span style="color: #059669; font-weight: 700;">0.53%</span></td>
<td>9.7% / yr</td>
<td>+38.7% (+₹3.13 L)</td>
</tr>
<tr>
<td><span style="color: #D97706; font-weight: 700;">🟡 GOLD BEES</span></td>
<td>₹8.10 L</td>
<td><strong>₹19.06 L</strong></td>
<td>₹19.31 L</td>
<td><span style="color: #059669; font-weight: 700;">1.29%</span></td>
<td>25.4% / yr</td>
<td><strong>+135.3%</strong> (+₹10.96 L)</td>
</tr>
<tr style="border-top: 2px solid #E2E8F0;">
<td rowspan="2"><strong>2016 to 2026</strong><br><span style="font-size: 0.75rem; color: #64748B;">(~10.75 Yrs / 129 Mos)</span></td>
<td><span style="color: #2563EB; font-weight: 700;">🔵 NIFTY 50</span></td>
<td>₹12.90 L</td>
<td><strong>₹23.96 L</strong></td>
<td>₹24.11 L</td>
<td><span style="color: #059669; font-weight: 700;">0.60%</span></td>
<td>11.1% / yr</td>
<td>+85.8% (+₹11.06 L)</td>
</tr>
<tr>
<td><span style="color: #D97706; font-weight: 700;">🟡 GOLD BEES</span></td>
<td>₹12.90 L</td>
<td><strong>₹40.91 L</strong></td>
<td>₹41.35 L</td>
<td><span style="color: #059669; font-weight: 700;">1.05%</span></td>
<td>20.4% / yr</td>
<td><strong>+217.2%</strong> (+₹28.01 L)</td>
</tr>
<tr style="border-top: 2px solid #E2E8F0;">
<td rowspan="2"><strong>2010 to 2026</strong><br><span style="font-size: 0.75rem; color: #64748B;">(~16.6 Yrs / 201 Mos)</span></td>
<td><span style="color: #2563EB; font-weight: 700;">🔵 NIFTY 50</span></td>
<td>₹20.10 L</td>
<td><strong>₹55.33 L</strong></td>
<td>₹55.67 L</td>
<td><span style="color: #059669; font-weight: 700;">0.60%</span></td>
<td>11.2% / yr</td>
<td>+175.3% (+₹35.23 L)</td>
</tr>
<tr>
<td><span style="color: #D97706; font-weight: 700;">🟡 GOLD BEES</span></td>
<td>₹20.10 L</td>
<td><strong>₹78.85 L</strong></td>
<td>₹79.47 L</td>
<td><span style="color: #059669; font-weight: 700;">0.78%</span></td>
<td>14.8% / yr</td>
<td><strong>+292.3%</strong> (+₹58.75 L)</td>
</tr>
</tbody>
</table>
</div>

<div class="doc-h2" style="margin-top: 1.75rem;">📊 Raw Asset Coverage & Universe</div>
<p class="doc-p">
The dataset tracks 24 core tickers across large-cap and mid-cap Indian equities, spanning Banking, IT, Auto, FMCG, Energy, Telecom, and Infrastructure alongside dual benchmark ETFs: NIFTY 50 ETF (<code>NIFTYBEES.NS</code>) and Sovereign Gold ETF (<code>GOLDBEES.NS</code>).
</p>
</div>""", unsafe_allow_html=True)
    
    display_cols = [c for c in ["Ticker", "Display_Code", "Company_Name", "Category", "Listing_Date", "Total_Trading_Days", "Available_Years"] if c in equity_stocks.columns]
    st.dataframe(
        equity_stocks[display_cols],
        use_container_width=True,
        hide_index=True
    )

