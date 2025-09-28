# streamlit_project/plotly_theme.py
from __future__ import annotations
import plotly.graph_objects as go
from .theme import ThemeTokens

def apply_plotly_template(fig: go.Figure, t: ThemeTokens) -> go.Figure:
    fig.update_layout(
        template="plotly_white",  # base, but we'll override colors
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=t.text, family=t.mono_stack, size=12),
        xaxis=dict(gridcolor=t.grid, linecolor=t.axis, zeroline=False, showspikes=True, spikethickness=1, spikecolor=t.axis),
        yaxis=dict(gridcolor=t.grid, linecolor=t.axis, zeroline=False, showspikes=True, spikethickness=1, spikecolor=t.axis),
        legend=dict(borderwidth=0),
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )
    return fig

def style_candles(fig: go.Figure, t: ThemeTokens) -> go.Figure:
    for tr in fig.data:
        if isinstance(tr, go.Candlestick):
            tr.increasing.line.color = t.candle_up
            tr.increasing.fillcolor = t.candle_up
            tr.decreasing.line.color = t.candle_down
            tr.decreasing.fillcolor = t.candle_down
    return fig

def style_volume_bars(fig: go.Figure, t: ThemeTokens) -> go.Figure:
    for tr in fig.data:
        if isinstance(tr, go.Bar) and tr.name and tr.name.lower() == "volume":
            tr.marker = dict(color=t.info)
    return fig

def default_overlay_colors(t: ThemeTokens):
    # rotate these for overlays like MAs/Bands
    return [t.overlay_1, t.overlay_2, t.overlay_3, t.primary, t.info, t.warning, t.success]