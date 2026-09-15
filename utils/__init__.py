# utils package
from .analytics import (
    load_data,
    compute_exact_xirr,
    format_currency_inr,
    format_pct,
    run_nifty_benchmark,
    run_gold_benchmark,
    run_stock_basket_simulation
)

__all__ = [
    "load_data",
    "compute_exact_xirr",
    "format_currency_inr",
    "format_pct",
    "run_nifty_benchmark",
    "run_gold_benchmark",
    "run_stock_basket_simulation"
]
