"""
Strategy: tv_fib_golden_zone_pullback_4h_long_tight_sl
Thesis:   Same Fib golden zone pullback mechanism as tv_fib_golden_zone_pullback_4h_long
          but with structurally-derived exits: SL at 61.8% Fib level invalidation
          (below the zone = structure broken) and TP at 1.618 Fib extension above swing high.
          Tighter SL + wider TP targets a payoff ratio > 1.0 (vs 0.66 in the base version).
Source:   Structural improvement on tv_fib_golden_zone_pullback_4h_long.py
          Concept: ICT OTE (Optimal Trade Entry) zones with extension targets.
          Ref: https://www.tradingview.com/script/ckxO7z13-Confirmed-Fibonacci-BOS-Pullback/
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Structural variant of tv_fib_golden_zone_pullback_4h_long.
                    Key changes vs base:
                    1. SL = just below 61.8% fib level (zone invalidation at 65% retrace)
                       — structural SL, not percentage.
                    2. TP = 1.618 extension above swing high (Fib extension target).
                    3. Entry: same — price in golden zone (50-61.8%) + green candle.
                    Platform stopLossPct is set conservatively (5%) as a hard backstop
                    in case the structural SL can't fire (gap down). The 65% retrace level
                    is the actual intended stop.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param pivot_length int 20
# @param fib_entry_lo float 0.50
# @param fib_entry_hi float 0.618
# @param fib_sl_level float 0.65
# @param fib_tp_ext float 1.618
# @param timeout_bars int 40
# @param min_impulse_pct float 0.05

import pandas as pd
import numpy as np

df = df.copy()

pivot_length    = int(params.get('pivot_length', 20))
fib_entry_lo    = float(params.get('fib_entry_lo', 0.50))
fib_entry_hi    = float(params.get('fib_entry_hi', 0.618))
fib_sl_level    = float(params.get('fib_sl_level', 0.65))   # 65% retrace = structure broken
fib_tp_ext      = float(params.get('fib_tp_ext', 1.618))    # 1.618 extension above swing_high
timeout_bars    = int(params.get('timeout_bars', 40))
min_impulse_pct = float(params.get('min_impulse_pct', 0.05))

# ── Rolling swing high / low (no lookahead) ─────────────────────────────────
df['swing_high'] = df['high'].rolling(pivot_length).max().shift(1)
df['swing_low']  = df['low'].rolling(pivot_length).min().shift(1)

# ── Impulse size filter ──────────────────────────────────────────────────────
swing_range  = df['swing_high'] - df['swing_low']
impulse_size = swing_range / df['swing_low']
is_impulse   = impulse_size >= min_impulse_pct

# ── Fibonacci levels ─────────────────────────────────────────────────────────
# Entry zone: 50% to 61.8% retracement from swing_high
fib_zone_top = df['swing_high'] - fib_entry_lo * swing_range   # 50% retrace
fib_zone_bot = df['swing_high'] - fib_entry_hi * swing_range   # 61.8% retrace

# SL invalidation level: 65% retrace (one step below golden zone)
fib_sl_price = df['swing_high'] - fib_sl_level * swing_range

# TP extension level: 1.618 above swing_high
fib_tp_price = df['swing_high'] + (fib_tp_ext - 1.0) * swing_range

# ── Entry signal ─────────────────────────────────────────────────────────────
price_in_zone = (
    (df['close'] >= fib_zone_bot) &
    (df['close'] <= fib_zone_top)
)

# Bullish close (green candle in zone)
_op = 'open'
green_candle = df['close'] > df[_op]

# In pullback (below swing high)
is_pullback = df['close'] < df['swing_high']

df['buy'] = (
    is_impulse &
    price_in_zone &
    green_candle &
    is_pullback
)

# ── Exit signals ─────────────────────────────────────────────────────────────
# TP: close reaches 1.618 extension
tp_hit = df['close'] >= fib_tp_price

# Structural SL: close breaks below 65% retrace (zone is invalidated)
sl_hit = df['close'] < fib_sl_price

df['sell'] = tp_hit | sl_hit

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
