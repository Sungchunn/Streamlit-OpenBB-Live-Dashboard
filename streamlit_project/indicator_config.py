"""
Indicator configuration dataclass and preset management
"""
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple, Dict, Any


@dataclass
class IndicatorConfig:
    """Configuration class for technical indicators"""

    # Trend indicators
    sma: Optional[List[int]] = None      # e.g. [20, 50, 200]
    ema: Optional[List[int]] = None
    ichimoku: bool = False               # use defaults (9,26,52) unless overridden
    ichimoku_params: Tuple[int, int, int] = (9, 26, 52)
    adx: bool = False
    adx_length: int = 14
    dmi: bool = False
    dmi_length: int = 14

    # Momentum indicators
    rsi: bool = False
    rsi_length: int = 14
    macd: bool = False
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    stochastic: bool = False
    stoch_k: int = 14
    stoch_d: int = 3
    stoch_smooth_k: int = 3

    # Volatility indicators
    atr: bool = False
    atr_length: int = 14
    bbands: bool = False
    bb_length: int = 20
    bb_std: float = 2.0
    keltner: bool = False
    kel_length: int = 20
    kel_mult: float = 1.5

    # Volume/Flow indicators
    obv: bool = False
    mfi: bool = False
    mfi_length: int = 14
    vwap: bool = False
    volume_profile: bool = False        # fallback to approximation if Pro not available
    volume_profile_bins: int = 50

    # Market Breadth (index-level)
    advance_decline: bool = False
    percent_above_ma: bool = False
    breadth_ma_length: int = 50

    def to_cache_key(self) -> tuple:
        """Convert config to a hashable tuple for caching"""
        config_dict = asdict(self)
        # Convert lists to tuples for hashability
        if config_dict['sma']:
            config_dict['sma'] = tuple(config_dict['sma'])
        if config_dict['ema']:
            config_dict['ema'] = tuple(config_dict['ema'])

        return tuple(sorted(config_dict.items()))

    @classmethod
    def from_preset(cls, preset_name: str) -> 'IndicatorConfig':
        """Create configuration from preset"""
        presets = {
            'minimal': cls(
                sma=[20, 50],
                rsi=True,
                atr=True
            ),
            'trend_follower': cls(
                ema=[20, 50, 200],
                adx=True,
                macd=True
            ),
            'mean_reversion': cls(
                bbands=True,
                bb_length=20,
                bb_std=2.0,
                stochastic=True,
                stoch_k=14,
                stoch_d=3,
                stoch_smooth_k=3,
                rsi=True,
                rsi_length=14
            ),
            'intraday': cls(
                vwap=True,
                obv=True,
                keltner=True,
                kel_length=20,
                kel_mult=1.5,
                adx=True,
                adx_length=14
            ),
            'comprehensive': cls(
                sma=[20, 50, 200],
                ema=[12, 26],
                rsi=True,
                macd=True,
                bbands=True,
                atr=True,
                obv=True,
                vwap=True
            )
        }

        return presets.get(preset_name, cls())

    def get_active_indicators(self) -> Dict[str, Any]:
        """Get only the active indicators and their parameters"""
        active = {}

        # Trend
        if self.sma:
            active['sma'] = self.sma
        if self.ema:
            active['ema'] = self.ema
        if self.ichimoku:
            active['ichimoku'] = self.ichimoku_params
        if self.adx:
            active['adx'] = self.adx_length
        if self.dmi:
            active['dmi'] = self.dmi_length

        # Momentum
        if self.rsi:
            active['rsi'] = self.rsi_length
        if self.macd:
            active['macd'] = (self.macd_fast, self.macd_slow, self.macd_signal)
        if self.stochastic:
            active['stochastic'] = (self.stoch_k, self.stoch_d, self.stoch_smooth_k)

        # Volatility
        if self.atr:
            active['atr'] = self.atr_length
        if self.bbands:
            active['bbands'] = (self.bb_length, self.bb_std)
        if self.keltner:
            active['keltner'] = (self.kel_length, self.kel_mult)

        # Volume/Flow
        if self.obv:
            active['obv'] = True
        if self.mfi:
            active['mfi'] = self.mfi_length
        if self.vwap:
            active['vwap'] = True
        if self.volume_profile:
            active['volume_profile'] = self.volume_profile_bins

        # Breadth
        if self.advance_decline:
            active['advance_decline'] = True
        if self.percent_above_ma:
            active['percent_above_ma'] = self.breadth_ma_length

        return active


def get_preset_names() -> List[str]:
    """Get list of available preset names"""
    return ['minimal', 'trend_follower', 'mean_reversion', 'intraday', 'comprehensive']


def get_preset_descriptions() -> Dict[str, str]:
    """Get descriptions for each preset"""
    return {
        'minimal': 'SMA 20/50, RSI, ATR - Basic analysis',
        'trend_follower': 'EMA 20/50/200, ADX, MACD - Trend identification',
        'mean_reversion': 'Bollinger Bands, Stochastic, RSI - Reversal signals',
        'intraday': 'VWAP, OBV, Keltner Channels, ADX - Day trading',
        'comprehensive': 'Multiple SMAs/EMAs, RSI, MACD, Bollinger, ATR, OBV, VWAP'
    }