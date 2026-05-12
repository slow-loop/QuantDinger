"""
Strategy: tv_fib_golden_zone_pullback_4h_long
Thesis:   After a confirmed bullish impulse (price breaks above N-bar high), a pullback
          into the Fibonacci golden zone (50–61.8% retracement) followed by a bullish
          close signals structural demand at a key retracement level. Impulse establishes
          directional bias; Fib zone provides precision entry. This is a structural
          catalyst — not a statistical threshold.
Source:   Adapted from ICT / Smart Money Concepts Fibonacci pullback methodology as
          implemented in TradingView community strategies. See:
          https://www.tradingview.com/script/ckxO7z13-Confirmed-Fibonacci-BOS-Pullback/
          (ukalgorithms, "Confirmed Fibonacci BOS + Pullback" concept)
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Vectorized Fib golden zone pullback strategy.
                    Impulse: close crosses above N-bar (pivot_length=20) highest high.
                    Swing: track the most recent swing_low and swing_high of the impulse.
                    Fib zone: 50% to 61.8% retracement between swing_low and swing_high.
                    Entry: price pulls back into golden zone AND bullish close (close > open).
                    Exit: price reaches 100% extension (prior swing high) OR timeout (30 bars) OR SL.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param pivot_length int 20
# @param fib_low float 0.50
# @param fib_high float 0.618
# @param timeout_bars int 30
# @param min_impulse_pct float 0.05

import pandas as pd
import numpy as np

df = df.copy()

pivot_length   = int(params.get('pivot_length', 20))
fib_low        = float(params.get('fib_low', 0.50))
fib_high       = float(params.get('fib_high', 0.618))
timeout_bars   = int(params.get('timeout_bars', 30))
min_impulse_pct = float(params.get('min_impulse_pct', 0.05))

# ── Rolling swing high / low ────────────────────────────────────────────────
# Swing high: current high is the highest over [pivot_length] bars (shifted to avoid lookahead)
df['swing_high'] = df['high'].rolling(pivot_length).max().shift(1)
df['swing_low']  = df['low'].rolling(pivot_length).min().shift(1)

# ── Impulse detection ────────────────────────────────────────────────────────
# Bullish impulse: current close breaks above prior N-bar high AND
# the move from swing_low to swing_high is > min_impulse_pct
impulse_size = (df['swing_high'] - df['swing_low']) / df['swing_low']
is_impulse = impulse_size >= min_impulse_pct

# ── Fibonacci golden zone ────────────────────────────────────────────────────
# Retracement from impulse high to low
# fib_low_price  = swing_high - fib_high * (swing_high - swing_low)
# fib_high_price = swing_high - fib_low  * (swing_high - swing_low)
swing_range    = df['swing_high'] - df['swing_low']
fib_zone_top   = df['swing_high'] - fib_low  * swing_range  # 50% retrace from high
fib_zone_bot   = df['swing_high'] - fib_high * swing_range  # 61.8% retrace from high

# ── Entry: price in golden zone + bullish close ─────────────────────────────
# Price has pulled back into the fib zone (between 50% and 61.8% from high)
price_in_zone = (
    (df['close'] >= fib_zone_bot) &
    (df['close'] <= fib_zone_top)
)

# Bullish close: close > open (green candle)
bullish_close = df['close'] > df['open']

# Require that price is below the swing high (we're in a pullback, not extending)
is_pullback = df['close'] < df['swing_high']

df['buy'] = (
    is_impulse &
    price_in_zone &
    bullish_close &
    is_pullback
)

# ── Exit: price reclaims swing high (full extension = TP) ───────────────────
# Sell when price reaches or exceeds the prior swing high
df['sell'] = df['close'] >= df['swing_high']

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
