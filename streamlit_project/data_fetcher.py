"""
Data fetching module using OpenBB Platform for financial data
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st

try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except ImportError:
    OPENBB_AVAILABLE = False
    st.error("OpenBB not available. Please install openbb package.")

class FinancialDataFetcher:
    """Handles all data fetching operations using OpenBB API"""

    def __init__(self):
        self.obb_available = OPENBB_AVAILABLE

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_stock_price_data(_self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock price data

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')

        Returns:
            DataFrame with OHLCV data or None if error
        """
        if not _self.obb_available:
            return None

        try:
            # Calculate start date based on period
            end_date = datetime.now()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
            else:  # Default to 1 year
                start_date = end_date - timedelta(days=365)

            # Fetch data using OpenBB
            data = obb.equity.price.historical(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                provider="yfinance"
            )

            if hasattr(data, 'to_df'):
                df = data.to_df()
            else:
                df = data

            return df

        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_company_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company information and key metrics

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with company info or None if error
        """
        if not _self.obb_available:
            return None

        try:
            # Get company profile
            profile = obb.equity.profile(symbol=symbol, provider="yfinance")

            if hasattr(profile, 'to_df'):
                profile_df = profile.to_df()
                if not profile_df.empty:
                    return profile_df.iloc[0].to_dict()

            return None

        except Exception as e:
            st.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None

    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_financial_ratios(_self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get key financial ratios and metrics

        Args:
            symbol: Stock ticker symbol

        Returns:
            DataFrame with financial ratios or None if error
        """
        if not _self.obb_available:
            return None

        try:
            # Get key metrics
            metrics = obb.equity.fundamental.metrics(symbol=symbol, provider="yfinance")

            if hasattr(metrics, 'to_df'):
                return metrics.to_df()
            else:
                return metrics

        except Exception as e:
            st.error(f"Error fetching financial ratios for {symbol}: {str(e)}")
            return None

    @st.cache_data(ttl=900)  # Cache for 15 minutes
    def get_technical_indicators(_self, symbol: str, period: str = "1y") -> Optional[Dict[str, pd.DataFrame]]:
        """
        Calculate technical indicators for a stock

        Args:
            symbol: Stock ticker symbol
            period: Time period for data

        Returns:
            Dictionary with different technical indicators
        """
        if not _self.obb_available:
            return None

        try:
            # First get price data
            price_data = _self.get_stock_price_data(symbol, period)

            if price_data is None or price_data.empty:
                return None

            indicators = {}

            # Simple Moving Averages
            try:
                sma_20 = obb.technical.sma(data=price_data, target="close", window=20)
                sma_50 = obb.technical.sma(data=price_data, target="close", window=50)
                indicators['SMA_20'] = sma_20.to_df() if hasattr(sma_20, 'to_df') else sma_20
                indicators['SMA_50'] = sma_50.to_df() if hasattr(sma_50, 'to_df') else sma_50
            except:
                pass

            # RSI
            try:
                rsi = obb.technical.rsi(data=price_data, target="close", window=14)
                indicators['RSI'] = rsi.to_df() if hasattr(rsi, 'to_df') else rsi
            except:
                pass

            # MACD
            try:
                macd = obb.technical.macd(data=price_data, target="close")
                indicators['MACD'] = macd.to_df() if hasattr(macd, 'to_df') else macd
            except:
                pass

            return indicators

        except Exception as e:
            st.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
            return None

    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_market_news(_self, symbol: str, limit: int = 10) -> Optional[pd.DataFrame]:
        """
        Get latest news for a stock

        Args:
            symbol: Stock ticker symbol
            limit: Number of news articles to fetch

        Returns:
            DataFrame with news articles or None if error
        """
        if not _self.obb_available:
            return None

        try:
            news = obb.news.company(
                symbol=symbol,
                limit=limit,
                provider="yfinance"
            )

            if hasattr(news, 'to_df'):
                return news.to_df()
            else:
                return news

        except Exception as e:
            st.error(f"Error fetching news for {symbol}: {str(e)}")
            return None