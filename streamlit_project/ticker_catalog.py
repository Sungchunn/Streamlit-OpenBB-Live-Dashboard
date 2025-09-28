"""
Ticker catalog loader with searchable functionality
"""
from __future__ import annotations
import os
import pandas as pd
import streamlit as st

try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except Exception:
    OPENBB_AVAILABLE = False


@st.cache_data(ttl=24*3600, show_spinner=False)
def load_ticker_catalog(market: str = "US") -> pd.DataFrame:
    """
    Return columns: symbol, name, exchange (strings).
    `market` can be "US", "EU", "HK", "TH", etc. Fallback to local CSV if API not available.
    """
    # 1) Try OpenBB sources by market (adjust as needed)
    if OPENBB_AVAILABLE:
        try:
            # Attempt a broad search / symbol universe by provider
            # NOTE: APIs differ by OpenBB version; handle multiple shapes.
            # Try yfinance symbols for US as a baseline (limited), then fmp if present.
            if market.upper() == "US":
                # Option A: Financial Modeling Prep via OpenBB if available
                try:
                    res = obb.equity.search(query="", limit=5000, provider="fmp")
                    df = res.to_df() if hasattr(res, "to_df") else pd.DataFrame(res)
                except Exception:
                    # Option B: generic equity search with yfinance (may be sparse)
                    try:
                        res = obb.equity.search(query="", limit=2000, provider="yfinance")
                        df = res.to_df() if hasattr(res, "to_df") else pd.DataFrame(res)
                    except Exception:
                        df = pd.DataFrame()

            else:
                # Non-US markets: try yfinance search first
                try:
                    res = obb.equity.search(query="", limit=5000, provider="yfinance")
                    df = res.to_df() if hasattr(res, "to_df") else pd.DataFrame(res)
                except Exception:
                    df = pd.DataFrame()

            if not df.empty:
                # Normalize column names commonly returned by OpenBB
                symbol_col = next((c for c in df.columns if c.lower() in ("symbol", "ticker")), None)
                name_col = next((c for c in df.columns if c.lower() in ("name", "company", "companyname", "shortname", "longname")), None)
                exch_col = next((c for c in df.columns if c.lower() in ("exchange", "exchangeShortName", "exchangeshortname", "mic")), None)

                out = pd.DataFrame({
                    "symbol": df[symbol_col].astype(str) if symbol_col and symbol_col in df.columns else pd.Series(dtype=str),
                    "name": df[name_col].astype(str) if name_col and name_col in df.columns else "",
                    "exchange": df[exch_col].astype(str) if exch_col and exch_col in df.columns else market.upper()
                }).dropna(subset=["symbol"]).drop_duplicates(subset=["symbol"])

                # Filter out overly long/invalid symbols
                out = out[out["symbol"].str.len().between(1, 12)]
                if len(out) > 0:
                    return out
        except Exception:
            pass

    # 2) Fallback to local CSV
    # Place a CSV at ./data/tickers_us.csv with columns: symbol,name,exchange
    csv_map = {
        "US": "data/tickers_us.csv",
        "EU": "data/tickers_eu.csv",
        "HK": "data/tickers_hk.csv",
        "TH": "data/tickers_th.csv",
    }
    path = csv_map.get(market.upper(), csv_map["US"])
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Ensure required columns exist
        for col in ["symbol", "name", "exchange"]:
            if col not in df.columns:
                df[col] = ""
        df["symbol"] = df["symbol"].astype(str).str.upper()
        return df[["symbol", "name", "exchange"]].dropna(subset=["symbol"]).drop_duplicates("symbol")

    # 3) Last-resort tiny seed
    return pd.DataFrame([
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Class A)", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
        {"symbol": "NVDA", "name": "NVIDIA Corp.", "exchange": "NASDAQ"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
        {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc. (Class B)", "exchange": "NYSE"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
        {"symbol": "V", "name": "Visa Inc. (Class A)", "exchange": "NYSE"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "exchange": "NYSE Arca"},
        {"symbol": "QQQ", "name": "Invesco QQQ Trust", "exchange": "NASDAQ"},
        {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "exchange": "NYSE Arca"},
        {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "exchange": "NYSE Arca"},
        {"symbol": "XLK", "name": "Technology Select Sector SPDR Fund", "exchange": "NYSE Arca"},
    ])


def format_label(row: pd.Series) -> str:
    """Format ticker display label: 'SYMBOL — Company (Exchange)'"""
    name = row.get("name") or ""
    exch = row.get("exchange") or ""
    if name and exch:
        return f"{row['symbol']} — {name} ({exch})"
    if name:
        return f"{row['symbol']} — {name}"
    return f"{row['symbol']}"


def get_popular_tickers() -> list:
    """Get list of popular tickers for quick access"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META",
        "BRK.B", "JPM", "V", "SPY", "QQQ", "IWM", "VTI"
    ]