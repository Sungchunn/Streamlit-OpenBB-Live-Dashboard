"""
OpenBB Financial Dashboard
A Streamlit dashboard for financial data analysis using OpenBB Platform
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Import guard for project modules
try:
    from streamlit_project.data_fetcher import FinancialDataFetcher
    from streamlit_project.visualizations import ChartGenerator
    from streamlit_project.indicator_config import IndicatorConfig
    from streamlit_project.indicator_ui import (
        create_indicator_sidebar,
        display_indicator_summary,
        create_performance_info,
        handle_indicator_errors
    )
except Exception as e:
    st.set_page_config(page_title="OpenBB Financial Dashboard", layout="wide")
    st.error(f"Failed to import project modules: {e}\n"
             "Make sure the working directory is the project root and "
             "'streamlit_project' has an __init__.py.")
    raise

# Page configuration
st.set_page_config(
    page_title="OpenBB Financial Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-section {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize data fetcher and chart generator"""
    data_fetcher = FinancialDataFetcher()
    chart_generator = ChartGenerator()
    return data_fetcher, chart_generator

def main():
    """Main application function with enhanced technical indicators"""

    # Header
    st.markdown('<h1 class="main-header">📈 OpenBB Financial Dashboard</h1>', unsafe_allow_html=True)

    # Initialize components
    data_fetcher, chart_generator = initialize_components()

    # Check if OpenBB is available
    if not data_fetcher.obb_available:
        st.error("❌ OpenBB Platform is not available. Please install it using: `pip install openbb`")
        st.stop()

    # Sidebar controls
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("🎛️ Dashboard Controls")

    # Stock symbol input
    symbol = st.sidebar.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        help="Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
    ).upper()

    # Time period selection
    period_options = {
        "1 Day": "1d",
        "5 Days": "5d",
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }

    selected_period = st.sidebar.selectbox(
        "Select Time Period",
        options=list(period_options.keys()),
        index=5  # Default to 1 Year
    )
    period = period_options[selected_period]

    # Chart type selection
    chart_type = st.sidebar.radio(
        "Chart Type",
        options=["candlestick", "line"],
        index=0
    )

    # Features to display
    st.sidebar.subheader("📊 Display Options")
    show_volume = st.sidebar.checkbox("Show Volume Chart", value=True)
    show_technicals = st.sidebar.checkbox("Show Technical Analysis", value=True)
    show_metrics = st.sidebar.checkbox("Show Company Metrics", value=True)
    show_news = st.sidebar.checkbox("Show Latest News", value=False)

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Technical Indicators Configuration
    indicator_config, compute_button = create_indicator_sidebar()

    # Display active indicators summary
    display_indicator_summary(indicator_config)

    # Performance info
    create_performance_info()

    # Add refresh button
    if st.sidebar.button("🔄 Refresh Data", type="secondary"):
        st.cache_data.clear()
        st.rerun()

    # Validate symbol input
    if not symbol or len(symbol) < 1:
        st.warning("⚠️ Please enter a valid stock symbol")
        st.stop()

    # Main content area
    with st.container():
        st.subheader(f"📊 Analysis for {symbol}")

        # Create progress bar for data loading
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Fetch price data
            status_text.text("📈 Fetching price data...")
            progress_bar.progress(20)
            price_data = data_fetcher.get_stock_price_data(symbol, period)

            if price_data is None or price_data.empty:
                st.error(f"❌ No price data found for symbol: {symbol}")
                st.stop()

            # Display price chart
            progress_bar.progress(40)
            status_text.text("📊 Creating price chart...")
            price_chart = chart_generator.create_price_chart(price_data, symbol, chart_type)
            st.plotly_chart(price_chart, use_container_width=True)

            # Volume chart
            if show_volume:
                progress_bar.progress(50)
                status_text.text("📊 Creating volume chart...")
                volume_chart = chart_generator.create_volume_chart(price_data, symbol)
                st.plotly_chart(volume_chart, use_container_width=True)

            # Create columns for metrics and additional info
            col1, col2 = st.columns([2, 1])

            with col1:
                # Enhanced Technical analysis with configurable indicators
                if show_technicals and (compute_button or any(indicator_config.get_active_indicators().values())):
                    progress_bar.progress(60)
                    status_text.text("🔍 Calculating technical indicators...")

                    # Use enhanced indicators with configuration
                    indicators = data_fetcher.get_technical_indicators(symbol, period, indicator_config)

                    if indicators:
                        # Create enhanced technical chart
                        technical_chart = chart_generator.create_technical_indicators_chart(
                            price_data, indicators, symbol, indicator_config
                        )
                        st.plotly_chart(technical_chart, use_container_width=True)

                        # Volume profile chart if enabled
                        if 'volume_profile' in indicators:
                            volume_profile_chart = chart_generator.create_volume_profile_chart(
                                indicators['volume_profile'], symbol
                            )
                            st.plotly_chart(volume_profile_chart, use_container_width=True)
                    else:
                        st.info("📊 No technical indicators computed. Select indicators from the sidebar.")
                elif show_technicals:
                    st.info("📊 Select technical indicators from the sidebar and click 'Compute'")

            with col2:
                # Company metrics
                if show_metrics:
                    progress_bar.progress(70)
                    status_text.text("📈 Fetching company metrics...")
                    company_info = data_fetcher.get_company_info(symbol)
                    ratios = data_fetcher.get_financial_ratios(symbol)
                    chart_generator.create_metrics_display(company_info, ratios)

                # News section
                if show_news:
                    progress_bar.progress(75)
                    status_text.text("📰 Fetching latest news...")
                    news_data = data_fetcher.get_market_news(symbol, limit=5)
                    chart_generator.create_news_display(news_data)

            # Data summary
            progress_bar.progress(80)
            status_text.text("📋 Preparing data summary...")

            st.subheader("📋 Data Summary")

            # Display basic statistics
            if not price_data.empty:
                col1, col2, col3, col4 = st.columns(4)

                latest_price = price_data['close'].iloc[-1] if 'close' in price_data.columns else price_data.iloc[-1, 0]
                price_change = ((latest_price - price_data['close'].iloc[0]) / price_data['close'].iloc[0] * 100) if 'close' in price_data.columns and len(price_data) > 1 else 0

                with col1:
                    st.metric(
                        "Latest Price",
                        f"${latest_price:.2f}",
                        f"{price_change:+.2f}%"
                    )

                with col2:
                    high_price = price_data['high'].max() if 'high' in price_data.columns else price_data.max().max()
                    st.metric("Period High", f"${high_price:.2f}")

                with col3:
                    low_price = price_data['low'].min() if 'low' in price_data.columns else price_data.min().min()
                    st.metric("Period Low", f"${low_price:.2f}")

                with col4:
                    avg_volume = price_data['volume'].mean() if 'volume' in price_data.columns else 0
                    volume_str = f"{avg_volume/1e6:.1f}M" if avg_volume > 1e6 else f"{avg_volume/1e3:.1f}K"
                    st.metric("Avg Volume", volume_str)

            # Raw data expander
            with st.expander("📊 View Raw Data"):
                st.dataframe(price_data.tail(100), use_container_width=True)

            # Clear progress bar and status
            progress_bar.progress(100)
            status_text.text("✅ Dashboard loaded successfully!")

            # Auto-hide progress after a delay
            import time
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()

        except Exception as error:
            st.error(f"❌ An error occurred: {str(error)}")
            progress_bar.empty()
            status_text.empty()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            📈 OpenBB Financial Dashboard | Enhanced Technical Indicators |
            Powered by OpenBB Platform & Streamlit | Data via Yahoo Finance
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()