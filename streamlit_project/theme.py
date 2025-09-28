# streamlit_project/theme.py
from __future__ import annotations
from dataclasses import dataclass
import streamlit as st

@dataclass
class ThemeTokens:
    # accent colors only - let streamlit handle base colors
    primary: str
    success: str
    info: str
    warning: str
    danger: str

    # text colors
    text: str
    text_secondary: str

    # chart-specific
    grid: str
    axis: str

    # candles
    candle_up: str
    candle_down: str

    # overlays
    overlay_1: str
    overlay_2: str
    overlay_3: str

    # font stack
    mono_stack: str

def tv_tokens_dark() -> ThemeTokens:
    return ThemeTokens(
        primary="#2962FF",
        success="#4CAF50",
        info="#00BCD4",
        warning="#FF9800",
        danger="#F44336",
        text="#D1D4DC",
        text_secondary="#868CA0",
        grid="rgba(209, 212, 220, 0.1)",
        axis="rgba(209, 212, 220, 0.2)",
        candle_up="#26A69A",
        candle_down="#EF5350",
        overlay_1="#2962FF",
        overlay_2="#FF6D00",
        overlay_3="#E91E63",
        mono_stack="'SF Mono', 'Monaco', 'Consolas', monospace"
    )

def tv_tokens_light() -> ThemeTokens:
    return ThemeTokens(
        primary="#2962FF",
        success="#4CAF50",
        info="#00BCD4",
        warning="#FF9800",
        danger="#F44336",
        text="#131722",
        text_secondary="#787B86",
        grid="rgba(19, 23, 34, 0.1)",
        axis="rgba(19, 23, 34, 0.2)",
        candle_up="#26A69A",
        candle_down="#EF5350",
        overlay_1="#2962FF",
        overlay_2="#FF6D00",
        overlay_3="#E91E63",
        mono_stack="'SF Mono', 'Monaco', 'Consolas', monospace"
    )

def terminal_tokens_dark() -> ThemeTokens:
    return ThemeTokens(
        primary="#00FF88",
        success="#00FF88",
        info="#00DDFF",
        warning="#FFDD00",
        danger="#FF4444",
        text="#00FF88",
        text_secondary="#00CC66",
        grid="rgba(0, 255, 136, 0.1)",
        axis="rgba(0, 255, 136, 0.2)",
        candle_up="#00FF88",
        candle_down="#FF4444",
        overlay_1="#00DDFF",
        overlay_2="#FFDD00",
        overlay_3="#FF8800",
        mono_stack="'SF Mono', 'Monaco', 'Consolas', monospace"
    )

def terminal_tokens_light() -> ThemeTokens:
    return ThemeTokens(
        primary="#008844",
        success="#008844",
        info="#0088CC",
        warning="#CC8800",
        danger="#CC2222",
        text="#004422",
        text_secondary="#006633",
        grid="rgba(0, 68, 34, 0.1)",
        axis="rgba(0, 68, 34, 0.2)",
        candle_up="#008844",
        candle_down="#CC2222",
        overlay_1="#0088CC",
        overlay_2="#CC8800",
        overlay_3="#CC4400",
        mono_stack="'SF Mono', 'Monaco', 'Consolas', monospace"
    )

def get_tokens(skin: str, is_dark_mode: bool = True) -> ThemeTokens:
    if skin.lower().startswith("trading"):
        return tv_tokens_dark() if is_dark_mode else tv_tokens_light()
    return terminal_tokens_dark() if is_dark_mode else terminal_tokens_light()

def apply_theme(t: ThemeTokens) -> None:
    # minimal CSS - just accent colors
    st.markdown(f"""
    <style>
    .stApp {{
        font-family: {t.mono_stack};
    }}
    </style>
    """, unsafe_allow_html=True)