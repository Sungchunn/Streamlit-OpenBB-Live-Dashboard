"""
Visualization components for the financial dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional

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

    def create_technical_indicators_chart(self, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame], symbol: str) -> go.Figure:
        """
        Create chart with technical indicators

        Args:
            data: Price data
            indicators: Dictionary of technical indicators
            symbol: Stock symbol

        Returns:
            Plotly figure with subplots
        """
        if data is None or data.empty:
            return go.Figure().add_annotation(text="No data available", showarrow=False)

        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=[f'{symbol} Price with Moving Averages', 'RSI', 'MACD'],
            row_heights=[0.6, 0.2, 0.2]
        )

        # Price chart
        close_col = 'close' if 'close' in data.columns else data.columns[0]
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[close_col],
            mode='lines',
            name='Price',
            line=dict(color=self.color_palette['primary'], width=2)
        ), row=1, col=1)

        # Add moving averages if available
        if indicators and 'SMA_20' in indicators:
            sma_20 = indicators['SMA_20']
            if not sma_20.empty and 'sma' in sma_20.columns:
                fig.add_trace(go.Scatter(
                    x=sma_20.index,
                    y=sma_20['sma'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=self.color_palette['secondary'], width=1)
                ), row=1, col=1)

        if indicators and 'SMA_50' in indicators:
            sma_50 = indicators['SMA_50']
            if not sma_50.empty and 'sma' in sma_50.columns:
                fig.add_trace(go.Scatter(
                    x=sma_50.index,
                    y=sma_50['sma'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=self.color_palette['success'], width=1)
                ), row=1, col=1)

        # RSI
        if indicators and 'RSI' in indicators:
            rsi = indicators['RSI']
            if not rsi.empty and 'rsi' in rsi.columns:
                fig.add_trace(go.Scatter(
                    x=rsi.index,
                    y=rsi['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.color_palette['warning'], width=1)
                ), row=2, col=1)

                # Add RSI reference lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        if indicators and 'MACD' in indicators:
            macd = indicators['MACD']
            if not macd.empty:
                if 'MACD_12_26_9' in macd.columns:
                    fig.add_trace(go.Scatter(
                        x=macd.index,
                        y=macd['MACD_12_26_9'],
                        mode='lines',
                        name='MACD',
                        line=dict(color=self.color_palette['primary'], width=1)
                    ), row=3, col=1)

                if 'MACDs_12_26_9' in macd.columns:
                    fig.add_trace(go.Scatter(
                        x=macd.index,
                        y=macd['MACDs_12_26_9'],
                        mode='lines',
                        name='Signal',
                        line=dict(color=self.color_palette['secondary'], width=1)
                    ), row=3, col=1)

                if 'MACDh_12_26_9' in macd.columns:
                    fig.add_trace(go.Bar(
                        x=macd.index,
                        y=macd['MACDh_12_26_9'],
                        name='Histogram',
                        marker_color=self.color_palette['info']
                    ), row=3, col=1)

        fig.update_layout(
            height=800,
            template='plotly_white',
            showlegend=True,
            title_text=f"{symbol} Technical Analysis"
        )

        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=1)

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