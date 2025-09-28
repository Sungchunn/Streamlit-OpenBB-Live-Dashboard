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

    # Fast-fail guard to catch stale imports/paths
    assert hasattr(data_fetcher, "get_many_price_data"), (
        "get_many_price_data is missing on FinancialDataFetcher. "
        "Did you update streamlit_project/data_fetcher.py and restart the app?"
    )

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

    # Multi-symbol comparison (moved up)
    st.sidebar.subheader("📈 Multi-Symbol Comparison")
    compare_symbols_input = st.sidebar.text_input(
        "Additional symbols to compare",
        placeholder="e.g., GOOGL, MSFT, TSLA",
        help="Enter comma-separated ticker symbols to compare with the primary symbol."
    )

    # Parse the input into a list
    if compare_symbols_input:
        compare_symbols = [s.strip().upper() for s in compare_symbols_input.split(",") if s.strip()]
    else:
        compare_symbols = []

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

            # Fetch additional data needed for tabs
            progress_bar.progress(40)
            status_text.text("📊 Preparing data...")

            # Get technical indicators if needed
            indicators = None
            if show_technicals and (compute_button or any(indicator_config.get_active_indicators().values())):
                status_text.text("🔍 Calculating technical indicators...")
                indicators = data_fetcher.get_technical_indicators(symbol, period, indicator_config)

            # Get company info and ratios if needed
            company_info = None
            ratios = None
            if show_metrics:
                status_text.text("📈 Fetching company metrics...")
                company_info = data_fetcher.get_company_info(symbol)
                ratios = data_fetcher.get_financial_ratios(symbol)

            progress_bar.progress(80)
            status_text.text("📋 Organizing data...")

            # Create tab navigation
            tabs = st.tabs(["📊 Overview", "📈 Volume", "🔧 Technicals", "📋 Fundamentals", "🔀 Compare"])

            # Overview Tab
            with tabs[0]:
                # Display price chart
                price_chart = chart_generator.create_price_chart(price_data, symbol, chart_type)
                st.plotly_chart(price_chart, use_container_width=True)

                # Key metrics
                st.subheader("📋 Key Metrics")
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

            # Volume Tab
            with tabs[1]:
                if show_volume:
                    volume_chart = chart_generator.create_volume_chart(price_data, symbol)
                    st.plotly_chart(volume_chart, use_container_width=True)
                else:
                    st.info("📊 Enable 'Show Volume Chart' in the sidebar to view volume data.")

            # Technicals Tab
            with tabs[2]:
                if show_technicals and indicators:
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
                elif show_technicals:
                    st.info("📊 Select technical indicators from the sidebar and click 'Compute'")
                else:
                    st.info("📊 Enable 'Show Technical Analysis' in the sidebar to view indicators.")

            # Fundamentals Tab
            with tabs[3]:
                if show_metrics:
                    chart_generator.create_metrics_display(company_info, ratios)
                else:
                    st.info("📊 Enable 'Show Company Metrics' in the sidebar to view fundamentals.")

            # Compare Tab
            with tabs[4]:
                st.subheader("📈 Multi-Symbol Comparison")

                # Combine primary symbol with comparison symbols
                all_symbols = [symbol] + [s.upper().strip() for s in compare_symbols if isinstance(s, str) and s.strip()]

                if len(all_symbols) <= 1:
                    st.info("💡 Add more symbols in the sidebar 'Multi-Symbol Comparison' section to compare.")
                    st.markdown("**Example symbols to try:** AAPL, GOOGL, MSFT, TSLA, SPY, QQQ")
                else:
                    # Fetch data for all symbols
                    with st.spinner(f"📊 Loading data for {len(all_symbols)} symbols..."):
                        comparison_data = data_fetcher.get_many_price_data(all_symbols, period)

                    if len(comparison_data) >= 2:
                        # Comparison mode selection
                        comparison_mode = st.radio(
                            "Compare mode",
                            ["Rebased Price (index=100)", "Returns", "Correlation"],
                            horizontal=True,
                            key="comparison_mode"
                        )

                        if comparison_mode == "Rebased Price (index=100)":
                            rebased_chart = chart_generator.create_rebased_price_chart(comparison_data)
                            st.plotly_chart(rebased_chart, use_container_width=True)

                        elif comparison_mode == "Returns":
                            returns_mode = st.selectbox(
                                "Returns aggregation",
                                ["Daily", "Cumulative"],
                                index=1,
                                key="returns_mode"
                            )
                            returns_chart = chart_generator.create_returns_chart(
                                comparison_data,
                                mode="cumulative" if returns_mode == "Cumulative" else "daily"
                            )
                            st.plotly_chart(returns_chart, use_container_width=True)

                        else:  # Correlation
                            correlation_chart = chart_generator.create_correlation_heatmap(comparison_data)
                            st.plotly_chart(correlation_chart, use_container_width=True)

                        # Small multiples
                        with st.expander("📊 Small Multiples (Price + SMA20/50)"):
                            if st.checkbox("Show small multiples", key="show_small_multiples"):
                                small_multiple_charts = chart_generator.create_small_multiples(comparison_data)

                                if small_multiple_charts:
                                    # Create responsive columns
                                    num_charts = len(small_multiple_charts)
                                    cols_per_row = min(4, max(2, num_charts))
                                    columns = st.columns(cols_per_row)

                                    for i, chart in enumerate(small_multiple_charts):
                                        with columns[i % cols_per_row]:
                                            st.plotly_chart(chart, use_container_width=True)
                    else:
                        st.warning("⚠️ Could not load sufficient data for comparison. Check symbol validity.")

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
            📈 OpenBB Financial Dashboard | Technical Indicators & Multi-Symbol Comparison |
            Powered by OpenBB Platform & Streamlit | Data via Yahoo Finance
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()