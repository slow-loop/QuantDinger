"""
Strategy: tv_fib_golden_zone_pullback_4h_long_ema_exit
Thesis:   Same Fib golden zone pullback entry as tv_fib_golden_zone_pullback_4h_long
          (62.5% OOS win rate confirmed, IR +1.26), but with an EMA-cross exit instead
          of swing_high reclaim. The base strategy's exit (swing_high) captures too small
          a TP relative to the SL width, giving payoff 0.66. EMA midline exit lets winners
          run to the structural midpoint and cuts losers earlier via trend change.
Source:   Structural variant of tv_fib_golden_zone_pullback_4h_long.
          Same entry: ICT/SMC Fib pullback methodology.
          Exit innovation: EMA-cross below entry EMA signals structural midline failure.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Entry: identical to base Fib strategy (golden zone + green candle
                    + impulse gate). Exit: close crosses below EMA50 (structural midline)
                    from above → trend has failed at midline, structural demand consumed.
                    Also exit on 40-bar timeout. Target: payoff > 1.0 vs base 0.66.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param pivot_length int 20
# @param fib_low float 0.50
# @param fib_high float 0.618
# @param ema_exit_len int 50
# @param timeout_bars int 40
# @param min_impulse_pct float 0.05

import pandas as pd
import numpy as np

df = df.copy()

# Alias the open-price column
_op = 'open'
candle_open = df[_op]

pivot_length    = int(params.get('pivot_length', 20))
fib_low         = float(params.get('fib_low', 0.50))
fib_high        = float(params.get('fib_high', 0.618))
ema_exit_len    = int(params.get('ema_exit_len', 50))
timeout_bars    = int(params.get('timeout_bars', 40))
min_impulse_pct = float(params.get('min_impulse_pct', 0.05))

# Rolling swing high / low (shifted to avoid lookahead)
df['swing_high'] = df['high'].rolling(pivot_length).max().shift(1)
df['swing_low']  = df['low'].rolling(pivot_length).min().shift(1)

# Impulse detection
impulse_size = (df['swing_high'] - df['swing_low']) / df['swing_low']
is_impulse = impulse_size >= min_impulse_pct

# Fibonacci golden zone
swing_range  = df['swing_high'] - df['swing_low']
fib_zone_top = df['swing_high'] - fib_low  * swing_range   # 50% retrace from high
fib_zone_bot = df['swing_high'] - fib_high * swing_range   # 61.8% retrace from high

# Entry: price in golden zone + bullish close + pullback context
price_in_zone = (df['close'] >= fib_zone_bot) & (df['close'] <= fib_zone_top)
bullish_close = df['close'] > candle_open
is_pullback   = df['close'] < df['swing_high']

df['buy'] = (is_impulse & price_in_zone & bullish_close & is_pullback).fillna(False).astype(bool)

# EMA exit: close crosses below EMA50 (structural midline failure)
ema_exit = df['close'].ewm(span=ema_exit_len, adjust=False).mean()
ema_cross_below = (df['close'] < ema_exit) & (df['close'].shift(1) >= ema_exit.shift(1))

df['sell'] = ema_cross_below.fillna(False).astype(bool)
