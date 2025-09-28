"""
Data fetching module using OpenBB Platform for financial data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import streamlit as st
from .indicator_config import IndicatorConfig

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
    def get_technical_indicators(_self, symbol: str, period: str = "1y", config: Optional[IndicatorConfig] = None) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Calculate technical indicators for a stock based on configuration

        Args:
            symbol: Stock ticker symbol
            period: Time period for data
            config: IndicatorConfig object specifying which indicators to calculate

        Returns:
            Dictionary with different technical indicators
        """
        if not _self.obb_available:
            return None

        if config is None:
            config = IndicatorConfig()

        try:
            # First get price data
            price_data = _self.get_stock_price_data(symbol, period)

            if price_data is None or price_data.empty:
                return None

            indicators = {}
            active_indicators = config.get_active_indicators()

            # Process each active indicator
            for indicator_name, params in active_indicators.items():
                try:
                    if indicator_name == 'sma':
                        for window in params:
                            if len(price_data) >= window:
                                result = _self._compute_sma(price_data, window)
                                if result is not None:
                                    indicators[f'sma_{window}'] = result

                    elif indicator_name == 'ema':
                        for window in params:
                            if len(price_data) >= window:
                                result = _self._compute_ema(price_data, window)
                                if result is not None:
                                    indicators[f'ema_{window}'] = result

                    elif indicator_name == 'rsi':
                        if len(price_data) >= params + 1:
                            result = _self._compute_rsi(price_data, params)
                            if result is not None:
                                indicators['rsi'] = result

                    elif indicator_name == 'macd':
                        fast, slow, signal = params
                        if len(price_data) >= slow + signal:
                            result = _self._compute_macd(price_data, fast, slow, signal)
                            if result is not None:
                                indicators['macd'] = result

                    elif indicator_name == 'stochastic':
                        k, d, smooth_k = params
                        if len(price_data) >= k + d:
                            result = _self._compute_stochastic(price_data, k, d, smooth_k)
                            if result is not None:
                                indicators['stochastic'] = result

                    elif indicator_name == 'atr':
                        if len(price_data) >= params:
                            result = _self._compute_atr(price_data, params)
                            if result is not None:
                                indicators['atr'] = result

                    elif indicator_name == 'bbands':
                        length, std = params
                        if len(price_data) >= length:
                            result = _self._compute_bollinger_bands(price_data, length, std)
                            if result is not None:
                                indicators['bbands'] = result

                    elif indicator_name == 'keltner':
                        length, mult = params
                        if len(price_data) >= length:
                            result = _self._compute_keltner_channels(price_data, length, mult)
                            if result is not None:
                                indicators['keltner'] = result

                    elif indicator_name == 'adx':
                        if len(price_data) >= params:
                            result = _self._compute_adx(price_data, params)
                            if result is not None:
                                indicators['adx'] = result

                    elif indicator_name == 'dmi':
                        if len(price_data) >= params:
                            result = _self._compute_dmi(price_data, params)
                            if result is not None:
                                indicators['dmi'] = result

                    elif indicator_name == 'ichimoku':
                        conversion, base, span_b = params
                        if len(price_data) >= max(conversion, base, span_b):
                            result = _self._compute_ichimoku(price_data, conversion, base, span_b)
                            if result is not None:
                                indicators['ichimoku'] = result

                    elif indicator_name == 'obv':
                        if 'volume' in price_data.columns:
                            result = _self._compute_obv(price_data)
                            if result is not None:
                                indicators['obv'] = result

                    elif indicator_name == 'mfi':
                        if 'volume' in price_data.columns and len(price_data) >= params:
                            result = _self._compute_mfi(price_data, params)
                            if result is not None:
                                indicators['mfi'] = result

                    elif indicator_name == 'vwap':
                        if 'volume' in price_data.columns:
                            result = _self._compute_vwap(price_data)
                            if result is not None:
                                indicators['vwap'] = result

                    elif indicator_name == 'volume_profile':
                        if 'volume' in price_data.columns:
                            result = _self._compute_volume_profile(price_data, params)
                            if result is not None:
                                indicators['volume_profile'] = result

                except Exception as e:
                    st.info(f"Could not compute {indicator_name}: {str(e)}")
                    continue

            return indicators

        except Exception as e:
            st.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
            return None

    def _compute_sma(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Simple Moving Average"""
        try:
            # Try OpenBB first
            result = obb.technical.sma(data=data, target="close", window=window)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback to pandas
            sma = data['close'].rolling(window=window).mean()
            return pd.DataFrame({'sma': sma}, index=data.index)

    def _compute_ema(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Exponential Moving Average"""
        try:
            # Try OpenBB first
            result = obb.technical.ema(data=data, target="close", window=window)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback to pandas
            ema = data['close'].ewm(span=window).mean()
            return pd.DataFrame({'ema': ema}, index=data.index)

    def _compute_rsi(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Relative Strength Index"""
        try:
            # Try OpenBB first
            result = obb.technical.rsi(data=data, target="close", window=window)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return pd.DataFrame({'rsi': rsi}, index=data.index)

    def _compute_macd(self, data: pd.DataFrame, fast: int, slow: int, signal: int) -> Optional[pd.DataFrame]:
        """Compute MACD"""
        try:
            # Try OpenBB first
            result = obb.technical.macd(data=data, target="close", fast=fast, slow=slow, signal=signal)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            ema_fast = data['close'].ewm(span=fast).mean()
            ema_slow = data['close'].ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            return pd.DataFrame({
                'macd': macd_line,
                'signal': signal_line,
                'hist': histogram
            }, index=data.index)

    def _compute_stochastic(self, data: pd.DataFrame, k: int, d: int, smooth_k: int) -> Optional[pd.DataFrame]:
        """Compute Stochastic Oscillator"""
        try:
            # Try OpenBB first
            result = obb.technical.stoch(data=data, k=k, d=d, smooth_k=smooth_k)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            low_k = data['low'].rolling(window=k).min()
            high_k = data['high'].rolling(window=k).max()
            k_percent = 100 * (data['close'] - low_k) / (high_k - low_k)
            k_percent_smooth = k_percent.rolling(window=smooth_k).mean()
            d_percent = k_percent_smooth.rolling(window=d).mean()
            return pd.DataFrame({
                '%K': k_percent_smooth,
                '%D': d_percent
            }, index=data.index)

    def _compute_atr(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Average True Range"""
        try:
            # Try OpenBB first
            result = obb.technical.atr(data=data, window=window)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=window).mean()
            return pd.DataFrame({'atr': atr}, index=data.index)

    def _compute_bollinger_bands(self, data: pd.DataFrame, window: int, std_dev: float) -> Optional[pd.DataFrame]:
        """Compute Bollinger Bands"""
        try:
            # Try OpenBB first
            result = obb.technical.bbands(data=data, target="close", window=window, std=std_dev)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            sma = data['close'].rolling(window=window).mean()
            std = data['close'].rolling(window=window).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return pd.DataFrame({
                'bb_upper': upper,
                'bb_mid': sma,
                'bb_lower': lower
            }, index=data.index)

    def _compute_keltner_channels(self, data: pd.DataFrame, window: int, multiplier: float) -> Optional[pd.DataFrame]:
        """Compute Keltner Channels"""
        try:
            # Try OpenBB first (if available)
            result = obb.technical.keltner(data=data, window=window, scalar=multiplier)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            ema = data['close'].ewm(span=window).mean()
            atr_data = self._compute_atr(data, window)
            if atr_data is not None and 'atr' in atr_data.columns:
                atr = atr_data['atr']
                upper = ema + (atr * multiplier)
                lower = ema - (atr * multiplier)
                return pd.DataFrame({
                    'kel_upper': upper,
                    'kel_mid': ema,
                    'kel_lower': lower
                }, index=data.index)
            return None

    def _compute_adx(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Average Directional Index"""
        try:
            # Try OpenBB first
            result = obb.technical.adx(data=data, window=window)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation (simplified)
            dmi_data = self._compute_dmi(data, window)
            if dmi_data is not None and '+di' in dmi_data.columns and '-di' in dmi_data.columns:
                plus_di = dmi_data['+di']
                minus_di = dmi_data['-di']
                dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
                adx = dx.rolling(window=window).mean()
                return pd.DataFrame({'adx': adx}, index=data.index)
            return None

    def _compute_dmi(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Directional Movement Index"""
        try:
            # Fallback implementation
            high_diff = data['high'].diff()
            low_diff = data['low'].diff()

            plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
            minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)

            atr_data = self._compute_atr(data, window)
            if atr_data is not None and 'atr' in atr_data.columns:
                atr = atr_data['atr']
                plus_di = 100 * pd.Series(plus_dm, index=data.index).rolling(window=window).mean() / atr
                minus_di = 100 * pd.Series(minus_dm, index=data.index).rolling(window=window).mean() / atr
                return pd.DataFrame({
                    '+di': plus_di,
                    '-di': minus_di
                }, index=data.index)
            return None
        except:
            return None

    def _compute_ichimoku(self, data: pd.DataFrame, conversion: int, base: int, span_b: int) -> Optional[pd.DataFrame]:
        """Compute Ichimoku Cloud"""
        try:
            # Fallback implementation
            conv_high = data['high'].rolling(window=conversion).max()
            conv_low = data['low'].rolling(window=conversion).min()
            conversion_line = (conv_high + conv_low) / 2

            base_high = data['high'].rolling(window=base).max()
            base_low = data['low'].rolling(window=base).min()
            base_line = (base_high + base_low) / 2

            leading_span_a = ((conversion_line + base_line) / 2).shift(base)

            span_b_high = data['high'].rolling(window=span_b).max()
            span_b_low = data['low'].rolling(window=span_b).min()
            leading_span_b = ((span_b_high + span_b_low) / 2).shift(base)

            lagging_span = data['close'].shift(-base)

            return pd.DataFrame({
                'conversion_line': conversion_line,
                'base_line': base_line,
                'leading_span_a': leading_span_a,
                'leading_span_b': leading_span_b,
                'lagging_span': lagging_span
            }, index=data.index)
        except:
            return None

    def _compute_obv(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Compute On Balance Volume"""
        try:
            # Try OpenBB first
            result = obb.technical.obv(data=data)
            return result.to_df() if hasattr(result, 'to_df') else result
        except:
            # Fallback implementation
            price_change = data['close'].diff()
            volume_direction = np.where(price_change > 0, data['volume'],
                                      np.where(price_change < 0, -data['volume'], 0))
            obv = volume_direction.cumsum()
            return pd.DataFrame({'obv': obv}, index=data.index)

    def _compute_mfi(self, data: pd.DataFrame, window: int) -> Optional[pd.DataFrame]:
        """Compute Money Flow Index"""
        try:
            # Fallback implementation
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            money_flow = typical_price * data['volume']

            price_change = typical_price.diff()
            positive_flow = money_flow.where(price_change > 0, 0).rolling(window=window).sum()
            negative_flow = money_flow.where(price_change < 0, 0).rolling(window=window).sum()

            money_flow_ratio = positive_flow / negative_flow.abs()
            mfi = 100 - (100 / (1 + money_flow_ratio))
            return pd.DataFrame({'mfi': mfi}, index=data.index)
        except:
            return None

    def _compute_vwap(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Compute Volume Weighted Average Price"""
        try:
            # Implementation for daily VWAP
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            volume_price = typical_price * data['volume']
            vwap = volume_price.cumsum() / data['volume'].cumsum()
            return pd.DataFrame({'vwap': vwap}, index=data.index)
        except:
            return None

    def _compute_volume_profile(self, data: pd.DataFrame, bins: int) -> Optional[pd.DataFrame]:
        """Compute Volume Profile approximation"""
        try:
            price_range = data['close']
            volume = data['volume']

            # Create histogram of prices weighted by volume
            hist, bin_edges = np.histogram(price_range, bins=bins, weights=volume)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # Create DataFrame with price bins and volume
            volume_profile = pd.DataFrame({
                'price_bin': bin_centers,
                'volume_sum': hist
            })

            return volume_profile
        except:
            return None

    def get_many_price_data(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Fetch price data for multiple symbols efficiently.
        Uses an inner cached function to avoid caching the bound method (self).
        """
        # Normalize to uppercase & tuple for the cache key
        symbols_tuple = tuple(sorted({s.upper() for s in symbols if isinstance(s, str) and s.strip()}))

        @st.cache_data(ttl=300)
        def _load_many(symbols_key: Tuple[str, ...], period_key: str) -> Dict[str, pd.DataFrame]:
            results: Dict[str, pd.DataFrame] = {}
            for sym in symbols_key:
                try:
                    df = self.get_stock_price_data(sym, period_key)
                    if df is not None and not df.empty:
                        results[sym] = df
                    else:
                        st.warning(f"No data available for {sym}")
                except Exception as e:
                    st.warning(f"Failed to load data for {sym}: {e}")
            return results

        return _load_many(symbols_tuple, period)

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