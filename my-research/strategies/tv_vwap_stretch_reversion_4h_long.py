"""
Strategy: tv_vwap_stretch_reversion_4h_long
Thesis:   Price overshoots the lower VWAP deviation band (2σ), then closes BACK
          inside the band — this return-to-mean bar signals exhaustion of the sell
          side. Unlike Z-score threshold cross (which fires INTO the extension),
          the re-entry signal fires AFTER the stretch, avoiding the knife-catch trap.
          Volume filter: entry bar must NOT have extreme volume (no panic selling).
Source:   Adapted from VWAP Mean Reversion Strategy by ayusattv / community concept.
          https://www.tradingview.com/script/9SEB7IHb-VWAP-Mean-Reversion-Strategy-Range-Bound-Forex-RSI-Volume/
          Key innovation: entry on band re-entry (not on stretch), avoids extension trap.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Rolling VWAP = cumulative VPWA over lookback. Bands at
                    +/- band_mult * rolling_std(close). Entry: close < lower_band
                    previous bar AND close > lower_band current bar (return to mean).
                    Volume filter: volume < vol_extreme_mult * vol_sma (no extreme vol).
                    Exit: close crosses above VWAP midline OR 30-bar timeout.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param lookback int 20
# @param band_mult float 2.0
# @param vol_extreme_mult float 3.0
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

lookback = int(params.get('lookback', 20))
band_mult = float(params.get('band_mult', 2.0))
vol_extreme_mult = float(params.get('vol_extreme_mult', 3.0))
timeout_bars = int(params.get('timeout_bars', 30))

# --- Rolling VWAP (volume-weighted average price over lookback) ---
typical_price = (df['high'] + df['low'] + df['close']) / 3
vwap = (typical_price * df['volume']).rolling(lookback).sum() / df['volume'].rolling(lookback).sum()

# --- Deviation bands ---
rolling_std = df['close'].rolling(lookback).std()
upper_band = vwap + band_mult * rolling_std
lower_band = vwap - band_mult * rolling_std

# --- Volume filter: avoid extreme volume bars (panic sell / capitulation) ---
vol_sma = df['volume'].rolling(20).mean()
no_extreme_vol = df['volume'] < vol_sma * vol_extreme_mult

# --- Entry: price was below lower band last bar AND is back above it now ---
# (return-to-mean signal, not threshold-cross signal)
was_below = df['close'].shift(1) < lower_band.shift(1)
now_above = df['close'] > lower_band
return_to_band = was_below & now_above

df['buy'] = (return_to_band & no_extreme_vol).fillna(False)

# --- Exit: close crosses above VWAP midline (mean-reversion target reached) ---
crossed_above_vwap = (df['close'] > vwap) & (df['close'].shift(1) <= vwap.shift(1))
df['sell'] = crossed_above_vwap.fillna(False)
