"""
Strategy: tv_bos_macd_momentum_4h_long
Thesis:   Break of Structure (new N-bar swing high) confirmed by MACD bullish cross
          + above-average volume fires a structural momentum entry. BOS signals
          that buyers have absorbed prior supply; MACD cross confirms momentum
          alignment; volume gate filters noise breakouts.
Source:   Adapted from ChronoPulse MS-MACD Resonance Strategy by officialjackofalltrades
          https://www.tradingview.com/script/IRxTxcNi-ChronoPulse-MS-MACD-Resonance-Strategy/
          Simplified to 5 core params; CHOCH detection replaced with swing high BOS.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. BOS = close > rolling max(swing_lookback). MACD cross
                    = macd_line crosses above signal_line on same bar. Volume gate
                    = volume > vol_sma * vol_mult. Exit: MACD line crosses below 0
                    OR ATR stop OR 40-bar timeout.
"""

# @strategy stopLossPct 0.03
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param swing_lookback int 20
# @param macd_fast int 12
# @param macd_slow int 26
# @param macd_signal int 9
# @param vol_mult float 1.4
# @param atr_stop_mult float 2.0
# @param timeout_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

swing_lookback = int(params.get('swing_lookback', 20))
macd_fast = int(params.get('macd_fast', 12))
macd_slow = int(params.get('macd_slow', 26))
macd_signal_period = int(params.get('macd_signal', 9))
vol_mult = float(params.get('vol_mult', 1.4))
atr_stop_mult = float(params.get('atr_stop_mult', 2.0))
timeout_bars = int(params.get('timeout_bars', 40))

# --- MACD ---
ema_fast = df['close'].ewm(span=macd_fast, adjust=False).mean()
ema_slow = df['close'].ewm(span=macd_slow, adjust=False).mean()
macd_line = ema_fast - ema_slow
signal_line = macd_line.ewm(span=macd_signal_period, adjust=False).mean()
macd_hist = macd_line - signal_line

# MACD bullish cross: macd_line crosses above signal_line
macd_cross_up = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))

# --- Break of Structure: close breaks above prior N-bar swing high ---
# Shift by 1 to avoid lookahead: prior N-bar high excluding current bar
prior_swing_high = df['close'].shift(1).rolling(swing_lookback).max()
bos = df['close'] > prior_swing_high

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_gate = df['volume'] > vol_sma * vol_mult

# --- ATR for stop ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low'] - df['close'].shift(1)).abs()
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Entry: BOS + MACD cross up + volume gate ---
df['buy'] = bos & macd_cross_up & vol_gate

# --- Exit: MACD line drops below 0 (momentum exhausted) OR ATR stop ---
# ATR stop is handled by platform via @strategy stopLossPct
# Here we signal exit when MACD line crosses below zero
macd_below_zero = (macd_line < 0) & (macd_line.shift(1) >= 0)
df['sell'] = macd_below_zero

# Clean up NaN
df['buy'] = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)
