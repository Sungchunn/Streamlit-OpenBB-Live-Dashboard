"""
Streamlit UI components for technical indicator configuration
"""
import streamlit as st
from typing import Dict, Any
from .indicator_config import IndicatorConfig, get_preset_names, get_preset_descriptions


def create_indicator_sidebar() -> IndicatorConfig:
    """Create sidebar UI for indicator configuration and return IndicatorConfig"""

    st.sidebar.header("📊 Technical Indicators")

    # Initialize session state for indicator config
    if 'indicator_config' not in st.session_state:
        st.session_state.indicator_config = IndicatorConfig()

    config = st.session_state.indicator_config

    # Preset selection
    with st.sidebar.expander("📋 Presets", expanded=True):
        st.write("Quick configurations:")

        preset_names = get_preset_names()
        preset_descriptions = get_preset_descriptions()

        # Show preset descriptions
        for preset in preset_names:
            if st.button(f"📌 {preset.replace('_', ' ').title()}", key=f"preset_{preset}"):
                config = IndicatorConfig.from_preset(preset)
                st.session_state.indicator_config = config
                st.rerun()

        # Show current preset info
        if preset_names:
            selected_preset = st.selectbox(
                "Preset descriptions:",
                options=preset_names,
                format_func=lambda x: f"{x.replace('_', ' ').title()}: {preset_descriptions[x]}",
                key="preset_info"
            )

    # Trend Indicators
    with st.sidebar.expander("📈 Trend Indicators"):
        # SMA
        sma_enabled = st.checkbox("Simple Moving Averages", value=bool(config.sma), key="sma_enabled")
        if sma_enabled:
            sma_periods = st.multiselect(
                "SMA Periods",
                options=[5, 10, 20, 50, 100, 200],
                default=config.sma or [20, 50],
                key="sma_periods"
            )
            config.sma = sma_periods if sma_periods else None
        else:
            config.sma = None

        # EMA
        ema_enabled = st.checkbox("Exponential Moving Averages", value=bool(config.ema), key="ema_enabled")
        if ema_enabled:
            ema_periods = st.multiselect(
                "EMA Periods",
                options=[5, 10, 12, 20, 26, 50, 200],
                default=config.ema or [20, 50],
                key="ema_periods"
            )
            config.ema = ema_periods if ema_periods else None
        else:
            config.ema = None

        # Ichimoku
        config.ichimoku = st.checkbox("Ichimoku Cloud", value=config.ichimoku, key="ichimoku_enabled")
        if config.ichimoku:
            col1, col2, col3 = st.columns(3)
            with col1:
                config.ichimoku_params = (
                    st.number_input("Conversion", min_value=1, max_value=50, value=config.ichimoku_params[0], key="ichimoku_conversion"),
                    config.ichimoku_params[1],
                    config.ichimoku_params[2]
                )
            with col2:
                config.ichimoku_params = (
                    config.ichimoku_params[0],
                    st.number_input("Base", min_value=1, max_value=50, value=config.ichimoku_params[1], key="ichimoku_base"),
                    config.ichimoku_params[2]
                )
            with col3:
                config.ichimoku_params = (
                    config.ichimoku_params[0],
                    config.ichimoku_params[1],
                    st.number_input("Span B", min_value=1, max_value=100, value=config.ichimoku_params[2], key="ichimoku_span_b")
                )

        # ADX/DMI
        config.adx = st.checkbox("ADX (Average Directional Index)", value=config.adx, key="adx_enabled")
        config.dmi = st.checkbox("DMI (Directional Movement Index)", value=config.dmi, key="dmi_enabled")
        if config.adx or config.dmi:
            adx_length = st.slider("ADX/DMI Length", min_value=5, max_value=50, value=config.adx_length, key="adx_length")
            config.adx_length = adx_length
            config.dmi_length = adx_length

    # Momentum Indicators
    with st.sidebar.expander("⚡ Momentum Indicators"):
        # RSI
        config.rsi = st.checkbox("RSI (Relative Strength Index)", value=config.rsi, key="rsi_enabled")
        if config.rsi:
            config.rsi_length = st.slider("RSI Length", min_value=5, max_value=50, value=config.rsi_length, key="rsi_length")

        # MACD
        config.macd = st.checkbox("MACD", value=config.macd, key="macd_enabled")
        if config.macd:
            col1, col2, col3 = st.columns(3)
            with col1:
                config.macd_fast = st.number_input("Fast", min_value=5, max_value=30, value=config.macd_fast, key="macd_fast")
            with col2:
                config.macd_slow = st.number_input("Slow", min_value=15, max_value=50, value=config.macd_slow, key="macd_slow")
            with col3:
                config.macd_signal = st.number_input("Signal", min_value=5, max_value=20, value=config.macd_signal, key="macd_signal")

        # Stochastic
        config.stochastic = st.checkbox("Stochastic Oscillator", value=config.stochastic, key="stochastic_enabled")
        if config.stochastic:
            col1, col2, col3 = st.columns(3)
            with col1:
                config.stoch_k = st.number_input("%K", min_value=5, max_value=30, value=config.stoch_k, key="stoch_k")
            with col2:
                config.stoch_d = st.number_input("%D", min_value=1, max_value=10, value=config.stoch_d, key="stoch_d")
            with col3:
                config.stoch_smooth_k = st.number_input("Smooth %K", min_value=1, max_value=10, value=config.stoch_smooth_k, key="stoch_smooth_k")

    # Volatility Indicators
    with st.sidebar.expander("💥 Volatility Indicators"):
        # ATR
        config.atr = st.checkbox("ATR (Average True Range)", value=config.atr, key="atr_enabled")
        if config.atr:
            config.atr_length = st.slider("ATR Length", min_value=5, max_value=50, value=config.atr_length, key="atr_length")

        # Bollinger Bands
        config.bbands = st.checkbox("Bollinger Bands", value=config.bbands, key="bbands_enabled")
        if config.bbands:
            col1, col2 = st.columns(2)
            with col1:
                config.bb_length = st.number_input("BB Length", min_value=5, max_value=50, value=config.bb_length, key="bb_length")
            with col2:
                config.bb_std = st.number_input("Std Dev", min_value=1.0, max_value=3.0, value=config.bb_std, step=0.1, key="bb_std")

        # Keltner Channels
        config.keltner = st.checkbox("Keltner Channels", value=config.keltner, key="keltner_enabled")
        if config.keltner:
            col1, col2 = st.columns(2)
            with col1:
                config.kel_length = st.number_input("Keltner Length", min_value=5, max_value=50, value=config.kel_length, key="kel_length")
            with col2:
                config.kel_mult = st.number_input("Multiplier", min_value=0.5, max_value=3.0, value=config.kel_mult, step=0.1, key="kel_mult")

    # Volume/Flow Indicators
    with st.sidebar.expander("📊 Volume/Flow Indicators"):
        config.obv = st.checkbox("OBV (On Balance Volume)", value=config.obv, key="obv_enabled")

        config.mfi = st.checkbox("MFI (Money Flow Index)", value=config.mfi, key="mfi_enabled")
        if config.mfi:
            config.mfi_length = st.slider("MFI Length", min_value=5, max_value=50, value=config.mfi_length, key="mfi_length")

        config.vwap = st.checkbox("VWAP (Volume Weighted Average Price)", value=config.vwap, key="vwap_enabled")

        config.volume_profile = st.checkbox("Volume Profile (Approximation)", value=config.volume_profile, key="volume_profile_enabled")
        if config.volume_profile:
            config.volume_profile_bins = st.slider("Profile Bins", min_value=20, max_value=100, value=config.volume_profile_bins, key="volume_profile_bins")

    # Market Breadth
    with st.sidebar.expander("📊 Market Breadth"):
        st.info("⚠️ Works best with major index symbols")
        config.advance_decline = st.checkbox("Advance/Decline Line", value=config.advance_decline, key="advance_decline_enabled")

        config.percent_above_ma = st.checkbox("% Above Moving Average", value=config.percent_above_ma, key="percent_above_ma_enabled")
        if config.percent_above_ma:
            config.breadth_ma_length = st.slider("Breadth MA Length", min_value=10, max_value=200, value=config.breadth_ma_length, key="breadth_ma_length")

    # Control buttons
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
            config = IndicatorConfig()
            st.session_state.indicator_config = config
            st.rerun()

    with col2:
        compute_button = st.button("🔄 Compute", key="compute_indicators", type="primary", use_container_width=True)

    # Update session state
    st.session_state.indicator_config = config

    return config, compute_button


def display_indicator_summary(config: IndicatorConfig):
    """Display a summary of active indicators"""
    active_indicators = config.get_active_indicators()

    if not active_indicators:
        st.sidebar.info("No indicators selected")
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Active Indicators:**")

    indicator_groups = {
        "Trend": [],
        "Momentum": [],
        "Volatility": [],
        "Volume": [],
        "Breadth": []
    }

    for indicator, params in active_indicators.items():
        if indicator in ['sma', 'ema', 'ichimoku', 'adx', 'dmi']:
            indicator_groups["Trend"].append(indicator)
        elif indicator in ['rsi', 'macd', 'stochastic']:
            indicator_groups["Momentum"].append(indicator)
        elif indicator in ['atr', 'bbands', 'keltner']:
            indicator_groups["Volatility"].append(indicator)
        elif indicator in ['obv', 'mfi', 'vwap', 'volume_profile']:
            indicator_groups["Volume"].append(indicator)
        elif indicator in ['advance_decline', 'percent_above_ma']:
            indicator_groups["Breadth"].append(indicator)

    for group, indicators in indicator_groups.items():
        if indicators:
            st.sidebar.markdown(f"**{group}:** {', '.join([ind.upper() for ind in indicators])}")


def create_performance_info():
    """Display performance optimization info"""
    with st.sidebar.expander("⚙️ Performance Tips"):
        st.markdown("""
        **Optimization Tips:**
        - Use presets for quick setup
        - Fewer indicators = faster computation
        - Data is cached for 15 minutes
        - Click "Compute" to apply changes

        **Indicator Notes:**
        - SMA/EMA: Trend identification
        - RSI/Stochastic: Overbought/oversold
        - MACD: Momentum shifts
        - Bollinger/Keltner: Volatility bands
        - VWAP: Intraday benchmark
        - Volume Profile: Price-volume distribution
        """)


def handle_indicator_errors(error_messages: list):
    """Handle and display indicator computation errors"""
    if error_messages:
        with st.sidebar.expander("⚠️ Computation Issues", expanded=True):
            for error in error_messages:
                st.warning(error)

            st.info("""
            **Common Issues:**
            - Insufficient data for indicator period
            - Missing volume data for volume indicators
            - Breadth indicators need index constituents
            """)