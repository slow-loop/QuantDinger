"""
Strategy: tv_nr7_compression_breakout_eth_4h_long
Thesis:   Bar with narrowest range among last 7 bars (NR7) signals extreme volatility
          compression → explosive expansion follows. Enter long breakout only when aligned
          with trend (close > EMA50). NR7 is stricter than inside-bar (looks 7 bars back)
          and typically precedes larger-than-average directional moves.
Source:   TradingView NR4/NR7 Volatility Squeeze & Breakouts (TradeTechanalysis)
          https://www.tradingview.com/script/j2K2S9sB-NR4-NR7-Volatility-Squeeze-Breakouts/
          LuxAlgo NR4/NR7 with Breakouts:
          https://www.luxalgo.com/library/indicator/nr4-nr7-with-breakouts/
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   active

History (append-only, newest at bottom):
  2026-05-14  code  init. NR7 = current bar range is minimum of last 7 bars.
                    Entry: NR7 bar + next bar breaks above NR7 high + close > EMA50.
                    Stop: NR7 bar low (structural). TP: 2×ATR from entry or prior swing high.
                    Timeout: 20 bars.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param ema_trend int 50
# @param atr_tp_mult float 2.0
# @param timeout_bars int 20
# @param nr_lookback int 7

import pandas as pd
import numpy as np

df = df.copy()

ema_trend    = int(params.get('ema_trend', 50))
atr_tp_mult  = float(params.get('atr_tp_mult', 2.0))
timeout_bars = int(params.get('timeout_bars', 20))
nr_lookback  = int(params.get('nr_lookback', 7))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- EMA trend gate ---
ema = df['close'].ewm(span=ema_trend, adjust=False).mean()

# --- NR7 detection ---
# NR bar: current bar's range is the smallest among the last nr_lookback bars
bar_range = df['high'] - df['low']
min_range  = bar_range.rolling(nr_lookback).min()
is_nr7     = (bar_range == min_range) & (bar_range > 0)

# Save NR7 bar's high/low for breakout reference (shift to next bar)
nr7_high = df['high'].where(is_nr7).ffill()
nr7_low  = df['low'].where(is_nr7).ffill()

# Breakout bar: close breaks above NR7 bar's high on the NEXT bar
breakout_up = (df['close'] > nr7_high.shift(1)) & ~is_nr7

# Trend gate: close above EMA50
trend_ok = df['close'] > ema

# Entry: breakout bar + trend aligned + NR7 occurred in prev 3 bars (freshness)
nr7_recent = is_nr7.rolling(3).max().shift(1).fillna(0).astype(bool)
df['buy'] = (breakout_up & trend_ok & nr7_recent).fillna(False)

# Exit: timeout
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "NR7 Compression Breakout ETH 4H Long",
    "plots": [
        {"name": "EMA50",     "data": ema.fillna(0).tolist(),        "color": "#2196F3", "overlay": True},
        {"name": "NR7_high",  "data": nr7_high.fillna(0).tolist(),   "color": "#FF9800", "overlay": True},
        {"name": "NR7_low",   "data": nr7_low.fillna(0).tolist(),    "color": "#FF9800", "overlay": True},
        {"name": "ATR",       "data": atr.fillna(0).tolist(),        "color": "#9C27B0", "overlay": False},
    ]
}
