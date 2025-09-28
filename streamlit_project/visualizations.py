"""
Visualization components for the financial dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, Optional, List
from .indicator_config import IndicatorConfig

class ChartGenerator:
    """Handles all chart generation for the dashboard"""

    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8'
        }

    def create_price_chart(self, data: pd.DataFrame, symbol: str, chart_type: str = "candlestick") -> go.Figure:
        """
        Create price chart (candlestick or line chart)

        Args:
            data: OHLCV data
            symbol: Stock symbol
            chart_type: 'candlestick' or 'line'

        Returns:
            Plotly figure
        """
        if data is None or data.empty:
            return go.Figure().add_annotation(text="No data available", showarrow=False)

        fig = go.Figure()

        if chart_type == "candlestick" and all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name=symbol,
                increasing_line_color=self.color_palette['success'],
                decreasing_line_color=self.color_palette['danger']
            ))
        else:
            # Fallback to line chart
            close_col = 'close' if 'close' in data.columns else data.columns[0]
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[close_col],
                mode='lines',
                name=f'{symbol} Price',
                line=dict(color=self.color_palette['primary'], width=2)
            ))

        fig.update_layout(
            title=f'{symbol} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=500,
            xaxis_rangeslider_visible=False
        )

        return fig

    def create_volume_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create volume chart

        Args:
            data: OHLCV data with volume column
            symbol: Stock symbol

        Returns:
            Plotly figure
        """
        if data is None or data.empty or 'volume' not in data.columns:
            return go.Figure().add_annotation(text="No volume data available", showarrow=False)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color=self.color_palette['info']
        ))

        fig.update_layout(
            title=f'{symbol} Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            template='plotly_white',
            height=300
        )

        return fig

    def create_technical_indicators_chart(self, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame],
                                         symbol: str, config: Optional[IndicatorConfig] = None) -> go.Figure:
        """
        Create comprehensive chart with technical indicators based on configuration

        Args:
            data: Price data
            indicators: Dictionary of technical indicators
            symbol: Stock symbol
            config: IndicatorConfig specifying which indicators to display

        Returns:
            Plotly figure with dynamic subplots
        """
        if data is None or data.empty:
            return go.Figure().add_annotation(text="No data available", showarrow=False)

        if config is None:
            config = IndicatorConfig()

        # Determine required panels and their order
        panels = self._determine_panels(indicators, config)

        if not panels:
            # Fallback to simple price chart
            return self.create_price_chart(data, symbol)

        # Create dynamic subplots
        fig = make_subplots(
            rows=len(panels), cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[panel['title'] for panel in panels],
            row_heights=self._calculate_row_heights(panels)
        )

        # Plot each panel
        for i, panel in enumerate(panels, 1):
            self._plot_panel(fig, data, indicators, panel, i, symbol)

        # Update layout
        fig.update_layout(
            height=max(400, 200 * len(panels)),
            template='plotly_white',
            showlegend=True,
            title_text=f"{symbol} Technical Analysis",
            xaxis_rangeslider_visible=False
        )

        # Update axes titles
        for i, panel in enumerate(panels, 1):
            fig.update_yaxes(title_text=panel['ylabel'], row=i, col=1)
            if panel.get('yrange'):
                fig.update_yaxes(range=panel['yrange'], row=i, col=1)

        fig.update_xaxes(title_text="Date", row=len(panels), col=1)

        return fig

    def _determine_panels(self, indicators: Dict[str, pd.DataFrame], config: IndicatorConfig) -> List[Dict]:
        """Determine which panels to create based on available indicators"""
        panels = []

        # Price panel (always first)
        price_overlays = []

        # Check for trend overlays
        for key in indicators.keys():
            if key.startswith('sma_') or key.startswith('ema_'):
                price_overlays.append(key)

        # Check for volatility overlays
        if 'bbands' in indicators:
            price_overlays.append('bbands')
        if 'keltner' in indicators:
            price_overlays.append('keltner')
        if 'ichimoku' in indicators:
            price_overlays.append('ichimoku')
        if 'vwap' in indicators:
            price_overlays.append('vwap')

        panels.append({
            'type': 'price',
            'title': f'Price with Overlays',
            'ylabel': 'Price ($)',
            'indicators': price_overlays
        })

        # Momentum panel
        momentum_indicators = []
        if 'rsi' in indicators:
            momentum_indicators.append('rsi')
        if 'stochastic' in indicators:
            momentum_indicators.append('stochastic')

        if momentum_indicators:
            panels.append({
                'type': 'momentum',
                'title': 'Momentum Indicators',
                'ylabel': 'Value',
                'yrange': [0, 100],
                'indicators': momentum_indicators
            })

        # MACD panel
        if 'macd' in indicators:
            panels.append({
                'type': 'macd',
                'title': 'MACD',
                'ylabel': 'Value',
                'indicators': ['macd']
            })

        # Trend strength panel
        trend_indicators = []
        if 'adx' in indicators:
            trend_indicators.append('adx')
        if 'dmi' in indicators:
            trend_indicators.append('dmi')

        if trend_indicators:
            panels.append({
                'type': 'trend',
                'title': 'Trend Strength',
                'ylabel': 'Value',
                'yrange': [0, 100],
                'indicators': trend_indicators
            })

        # Volatility panel
        volatility_indicators = []
        if 'atr' in indicators:
            volatility_indicators.append('atr')

        if volatility_indicators:
            panels.append({
                'type': 'volatility',
                'title': 'Volatility',
                'ylabel': 'ATR',
                'indicators': volatility_indicators
            })

        # Volume/Flow panel
        volume_indicators = []
        if 'obv' in indicators:
            volume_indicators.append('obv')
        if 'mfi' in indicators:
            volume_indicators.append('mfi')

        if volume_indicators:
            panels.append({
                'type': 'volume',
                'title': 'Volume/Flow',
                'ylabel': 'Value',
                'indicators': volume_indicators
            })

        return panels

    def _calculate_row_heights(self, panels: List[Dict]) -> List[float]:
        """Calculate relative heights for each panel"""
        total_panels = len(panels)
        heights = []

        for panel in panels:
            if panel['type'] == 'price':
                heights.append(0.5)  # Price panel gets more space
            else:
                heights.append(0.5 / (total_panels - 1) if total_panels > 1 else 0.5)

        # Normalize to sum to 1.0
        total_height = sum(heights)
        return [h / total_height for h in heights]

    def _plot_panel(self, fig: go.Figure, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame],
                   panel: Dict, row: int, symbol: str):
        """Plot indicators for a specific panel"""

        if panel['type'] == 'price':
            self._plot_price_panel(fig, data, indicators, panel, row, symbol)
        elif panel['type'] == 'momentum':
            self._plot_momentum_panel(fig, indicators, panel, row)
        elif panel['type'] == 'macd':
            self._plot_macd_panel(fig, indicators, panel, row)
        elif panel['type'] == 'trend':
            self._plot_trend_panel(fig, indicators, panel, row)
        elif panel['type'] == 'volatility':
            self._plot_volatility_panel(fig, indicators, panel, row)
        elif panel['type'] == 'volume':
            self._plot_volume_panel(fig, indicators, panel, row)

    def _plot_price_panel(self, fig: go.Figure, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame],
                         panel: Dict, row: int, symbol: str):
        """Plot price data with overlays"""

        # Main price line
        close_col = 'close' if 'close' in data.columns else data.columns[0]
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[close_col],
            mode='lines',
            name='Price',
            line=dict(color=self.color_palette['primary'], width=2)
        ), row=row, col=1)

        # Moving averages
        colors = [self.color_palette['secondary'], self.color_palette['success'],
                 self.color_palette['warning'], self.color_palette['info']]
        color_idx = 0

        for indicator_key in panel['indicators']:
            if indicator_key.startswith('sma_'):
                window = indicator_key.split('_')[1]
                sma_data = indicators[indicator_key]
                if not sma_data.empty and 'sma' in sma_data.columns:
                    fig.add_trace(go.Scatter(
                        x=sma_data.index,
                        y=sma_data['sma'],
                        mode='lines',
                        name=f'SMA {window}',
                        line=dict(color=colors[color_idx % len(colors)], width=1)
                    ), row=row, col=1)
                    color_idx += 1

            elif indicator_key.startswith('ema_'):
                window = indicator_key.split('_')[1]
                ema_data = indicators[indicator_key]
                if not ema_data.empty and 'ema' in ema_data.columns:
                    fig.add_trace(go.Scatter(
                        x=ema_data.index,
                        y=ema_data['ema'],
                        mode='lines',
                        name=f'EMA {window}',
                        line=dict(color=colors[color_idx % len(colors)], width=1, dash='dash')
                    ), row=row, col=1)
                    color_idx += 1

            elif indicator_key == 'bbands':
                bb_data = indicators['bbands']
                if not bb_data.empty:
                    # Upper band
                    if 'bb_upper' in bb_data.columns:
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['bb_upper'],
                            mode='lines',
                            name='BB Upper',
                            line=dict(color='rgba(128,128,128,0.5)', width=1),
                            showlegend=False
                        ), row=row, col=1)

                    # Lower band
                    if 'bb_lower' in bb_data.columns:
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['bb_lower'],
                            mode='lines',
                            name='Bollinger Bands',
                            line=dict(color='rgba(128,128,128,0.5)', width=1),
                            fill='tonexty',
                            fillcolor='rgba(128,128,128,0.1)'
                        ), row=row, col=1)

                    # Middle line
                    if 'bb_mid' in bb_data.columns:
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['bb_mid'],
                            mode='lines',
                            name='BB Middle',
                            line=dict(color='gray', width=1, dash='dot'),
                            showlegend=False
                        ), row=row, col=1)

            elif indicator_key == 'keltner':
                kel_data = indicators['keltner']
                if not kel_data.empty:
                    if 'kel_upper' in kel_data.columns and 'kel_lower' in kel_data.columns:
                        fig.add_trace(go.Scatter(
                            x=kel_data.index,
                            y=kel_data['kel_upper'],
                            mode='lines',
                            name='Keltner Upper',
                            line=dict(color='purple', width=1),
                            showlegend=False
                        ), row=row, col=1)

                        fig.add_trace(go.Scatter(
                            x=kel_data.index,
                            y=kel_data['kel_lower'],
                            mode='lines',
                            name='Keltner Channels',
                            line=dict(color='purple', width=1),
                            fill='tonexty',
                            fillcolor='rgba(128,0,128,0.1)'
                        ), row=row, col=1)

            elif indicator_key == 'vwap':
                vwap_data = indicators['vwap']
                if not vwap_data.empty and 'vwap' in vwap_data.columns:
                    fig.add_trace(go.Scatter(
                        x=vwap_data.index,
                        y=vwap_data['vwap'],
                        mode='lines',
                        name='VWAP',
                        line=dict(color='orange', width=2, dash='dash')
                    ), row=row, col=1)

    def _plot_momentum_panel(self, fig: go.Figure, indicators: Dict[str, pd.DataFrame], panel: Dict, row: int):
        """Plot momentum indicators"""

        if 'rsi' in panel['indicators'] and 'rsi' in indicators:
            rsi_data = indicators['rsi']
            if not rsi_data.empty and 'rsi' in rsi_data.columns:
                fig.add_trace(go.Scatter(
                    x=rsi_data.index,
                    y=rsi_data['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.color_palette['warning'], width=1)
                ), row=row, col=1)

                # RSI reference lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", row=row, col=1)

        if 'stochastic' in panel['indicators'] and 'stochastic' in indicators:
            stoch_data = indicators['stochastic']
            if not stoch_data.empty:
                if '%K' in stoch_data.columns:
                    fig.add_trace(go.Scatter(
                        x=stoch_data.index,
                        y=stoch_data['%K'],
                        mode='lines',
                        name='Stoch %K',
                        line=dict(color=self.color_palette['primary'], width=1)
                    ), row=row, col=1)

                if '%D' in stoch_data.columns:
                    fig.add_trace(go.Scatter(
                        x=stoch_data.index,
                        y=stoch_data['%D'],
                        mode='lines',
                        name='Stoch %D',
                        line=dict(color=self.color_palette['secondary'], width=1)
                    ), row=row, col=1)

                # Stochastic reference lines
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=row, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=row, col=1)

    def _plot_macd_panel(self, fig: go.Figure, indicators: Dict[str, pd.DataFrame], panel: Dict, row: int):
        """Plot MACD indicator"""

        if 'macd' in indicators:
            macd_data = indicators['macd']
            if not macd_data.empty:
                # MACD line
                if 'macd' in macd_data.columns:
                    fig.add_trace(go.Scatter(
                        x=macd_data.index,
                        y=macd_data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color=self.color_palette['primary'], width=1)
                    ), row=row, col=1)

                # Signal line
                if 'signal' in macd_data.columns:
                    fig.add_trace(go.Scatter(
                        x=macd_data.index,
                        y=macd_data['signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color=self.color_palette['secondary'], width=1)
                    ), row=row, col=1)

                # Histogram
                if 'hist' in macd_data.columns:
                    colors = ['red' if x < 0 else 'green' for x in macd_data['hist']]
                    fig.add_trace(go.Bar(
                        x=macd_data.index,
                        y=macd_data['hist'],
                        name='Histogram',
                        marker_color=colors
                    ), row=row, col=1)

                # Zero line
                fig.add_hline(y=0, line_dash="dot", line_color="gray", row=row, col=1)

    def _plot_trend_panel(self, fig: go.Figure, indicators: Dict[str, pd.DataFrame], panel: Dict, row: int):
        """Plot trend strength indicators"""

        if 'adx' in panel['indicators'] and 'adx' in indicators:
            adx_data = indicators['adx']
            if not adx_data.empty and 'adx' in adx_data.columns:
                fig.add_trace(go.Scatter(
                    x=adx_data.index,
                    y=adx_data['adx'],
                    mode='lines',
                    name='ADX',
                    line=dict(color=self.color_palette['primary'], width=2)
                ), row=row, col=1)

                # ADX reference line (25 indicates strong trend)
                fig.add_hline(y=25, line_dash="dash", line_color="orange", row=row, col=1)

        if 'dmi' in panel['indicators'] and 'dmi' in indicators:
            dmi_data = indicators['dmi']
            if not dmi_data.empty:
                if '+di' in dmi_data.columns:
                    fig.add_trace(go.Scatter(
                        x=dmi_data.index,
                        y=dmi_data['+di'],
                        mode='lines',
                        name='+DI',
                        line=dict(color='green', width=1)
                    ), row=row, col=1)

                if '-di' in dmi_data.columns:
                    fig.add_trace(go.Scatter(
                        x=dmi_data.index,
                        y=dmi_data['-di'],
                        mode='lines',
                        name='-DI',
                        line=dict(color='red', width=1)
                    ), row=row, col=1)

    def _plot_volatility_panel(self, fig: go.Figure, indicators: Dict[str, pd.DataFrame], panel: Dict, row: int):
        """Plot volatility indicators"""

        if 'atr' in indicators:
            atr_data = indicators['atr']
            if not atr_data.empty and 'atr' in atr_data.columns:
                fig.add_trace(go.Scatter(
                    x=atr_data.index,
                    y=atr_data['atr'],
                    mode='lines',
                    name='ATR',
                    line=dict(color=self.color_palette['danger'], width=1)
                ), row=row, col=1)

    def _plot_volume_panel(self, fig: go.Figure, indicators: Dict[str, pd.DataFrame], panel: Dict, row: int):
        """Plot volume/flow indicators"""

        if 'obv' in panel['indicators'] and 'obv' in indicators:
            obv_data = indicators['obv']
            if not obv_data.empty and 'obv' in obv_data.columns:
                fig.add_trace(go.Scatter(
                    x=obv_data.index,
                    y=obv_data['obv'],
                    mode='lines',
                    name='OBV',
                    line=dict(color=self.color_palette['info'], width=1)
                ), row=row, col=1)

        if 'mfi' in panel['indicators'] and 'mfi' in indicators:
            mfi_data = indicators['mfi']
            if not mfi_data.empty and 'mfi' in mfi_data.columns:
                fig.add_trace(go.Scatter(
                    x=mfi_data.index,
                    y=mfi_data['mfi'],
                    mode='lines',
                    name='MFI',
                    line=dict(color='purple', width=1)
                ), row=row, col=1)

                # MFI reference lines
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=row, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=row, col=1)

    def create_volume_profile_chart(self, volume_profile_data: pd.DataFrame, symbol: str) -> go.Figure:
        """Create volume profile chart"""

        if volume_profile_data is None or volume_profile_data.empty:
            return go.Figure().add_annotation(text="No volume profile data available", showarrow=False)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=volume_profile_data['volume_sum'],
            y=volume_profile_data['price_bin'],
            orientation='h',
            name='Volume Profile',
            marker_color=self.color_palette['info']
        ))

        fig.update_layout(
            title=f'{symbol} Volume Profile (Approximation)',
            xaxis_title='Volume',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=400,
            showlegend=False
        )

        return fig

    def create_metrics_display(self, company_info: Optional[Dict[str, Any]], ratios: Optional[pd.DataFrame]) -> None:
        """
        Display key financial metrics in Streamlit

        Args:
            company_info: Company information dictionary
            ratios: Financial ratios DataFrame
        """
        st.subheader("📊 Key Metrics")

        if company_info:
            col1, col2, col3 = st.columns(3)

            with col1:
                market_cap = company_info.get('market_cap', 'N/A')
                if isinstance(market_cap, (int, float)) and market_cap > 0:
                    market_cap_str = f"${market_cap/1e9:.2f}B" if market_cap > 1e9 else f"${market_cap/1e6:.2f}M"
                else:
                    market_cap_str = 'N/A'
                st.metric("Market Cap", market_cap_str)

            with col2:
                pe_ratio = company_info.get('forward_pe', company_info.get('trailing_pe', 'N/A'))
                st.metric("P/E Ratio", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else 'N/A')

            with col3:
                dividend_yield = company_info.get('dividend_yield', 'N/A')
                dividend_str = f"{dividend_yield*100:.2f}%" if isinstance(dividend_yield, (int, float)) else 'N/A'
                st.metric("Dividend Yield", dividend_str)

        if ratios is not None and not ratios.empty:
            st.subheader("📈 Financial Ratios")
            st.dataframe(ratios, use_container_width=True)

    def create_news_display(self, news_data: Optional[pd.DataFrame]) -> None:
        """
        Display news articles in Streamlit

        Args:
            news_data: News articles DataFrame
        """
        st.subheader("📰 Latest News")

        if news_data is None or news_data.empty:
            st.info("No news data available")
            return

        for idx, article in news_data.head(5).iterrows():
            with st.expander(f"📄 {article.get('title', 'No title')[:100]}..."):
                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                if 'published' in article:
                    st.write(f"**Published:** {article['published']}")
                if 'summary' in article:
                    st.write(f"**Summary:** {article['summary']}")
                if 'url' in article:
                    st.write(f"**Link:** [Read more]({article['url']})")