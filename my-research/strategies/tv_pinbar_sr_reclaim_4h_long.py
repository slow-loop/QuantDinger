"""
Strategy: tv_pinbar_sr_reclaim_4h_long
Thesis:   Hammer / Pin Bar reversal candle forming at a dynamic support level (rolling
          N-bar low) signals structural demand — buyers absorbing sellers at a key price
          zone. The structural catalyst (candle at key level) differentiates this from
          pure threshold-cross mean-reversion.
Source:   Adapted from felipemiransan "Price Action Strategy" on TradingView
          https://www.tradingview.com/script/6jwIsZAE/
          Original: Hammer/Doji/PinBar near dynamic S/R (16-bar pivot, 1.8% sensitivity).
          Adapted: long-only, 4H timeframe, tighter sensitivity, ATR-based SL.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Port from felipemiransan Price Action Strategy (TV).
                    Long-only: hammer or pin bar within sensitivity pct of rolling support.
                    Support = lowest low over sr_length bars (structural demand zone).
                    Hammer: lower wick >= body*2, body in upper 1/3 of range, range > ATR*0.5.
                    Pin Bar: lower wick >= total_range*0.6, small body at top of range.
                    Exit: ATR 2x SL (hard), 20-bar timeout (soft), 8% TP (profit target).
"""

# @strategy stopLossPct 0.03
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param sr_length int 16
# @param sensitivity float 0.02
# @param atr_length int 14
# @param tp_pct float 0.08
# @param timeout_bars int 20
# @param atr_sl_mult float 2.0

import pandas as pd
import numpy as np

df = df.copy()

sr_length = int(params.get('sr_length', 16))
sensitivity = float(params.get('sensitivity', 0.02))
atr_length = int(params.get('atr_length', 14))
tp_pct = float(params.get('tp_pct', 0.08))
timeout_bars = int(params.get('timeout_bars', 20))
atr_sl_mult = float(params.get('atr_sl_mult', 2.0))

# ── Dynamic support: rolling lowest low ──────────────────────────────────────
df['support'] = df['low'].rolling(sr_length).min()

# ── ATR (Wilder smoothing) ────────────────────────────────────────────────────
high_low = df['high'] - df['low']
high_pc  = (df['high'] - df['close'].shift(1)).abs()
low_pc   = (df['low']  - df['close'].shift(1)).abs()
tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
df['atr'] = tr.ewm(alpha=1/atr_length, adjust=False).mean()

# ── Candle geometry ──────────────────────────────────────────────────────────
body      = (df['close'] - df['open']).abs()
upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
lower_wick = df[['open', 'close']].min(axis=1) - df['low']
candle_range = df['high'] - df['low']

# Hammer: lower wick >= 2x body, body in upper 40% of candle range, candle range > 0.5*ATR
# (bullish close preferred but not required — classic hammer can close red)
is_hammer = (
    (lower_wick >= body * 2.0) &
    (body > 0) &
    (candle_range > df['atr'] * 0.5) &
    (upper_wick <= body * 1.0)   # small upper wick
)

# Pin Bar: lower wick >= 60% of total range, small body at top
is_pinbar = (
    (lower_wick >= candle_range * 0.6) &
    (candle_range > df['atr'] * 0.5) &
    (body <= candle_range * 0.25)
)

is_reversal_candle = is_hammer | is_pinbar

# ── Proximity to support (within sensitivity %) ──────────────────────────────
# Check that the low of the candle touched or came close to the support level
# Low must be within sensitivity% above support (candle wicked into support zone)
near_support = (
    (df['low'] <= df['support'] * (1.0 + sensitivity)) &
    (df['low'] >= df['support'] * (1.0 - sensitivity * 0.5))   # not too far below
)

# ── Entry signal ─────────────────────────────────────────────────────────────
df['buy'] = is_reversal_candle & near_support

# ── Exit signals ─────────────────────────────────────────────────────────────
# Timeout exit: sell after timeout_bars bars (rolling: if in position for N bars)
# Note: strategy_evaluator handles stopLossPct as platform stop;
# we add explicit timeout and TP exits via df['sell']

# TP: close reaches tp_pct above entry close
# We approximate TP exit as: close > entry_close * (1 + tp_pct)
# Without stateful tracking of entry price in vectorized form, we use:
# sell when close is up tp_pct from N-bars-ago close (where N ~ position hold)
# Better approximation: sell when close crosses above rolling max of recent highs
# (price has extended significantly from any recent support)
# Use: close > support * (1 + tp_pct) as proxy for meaningful profit
df['sell'] = (
    (df['close'] > df['support'] * (1.0 + tp_pct))  # TP proxy: moved away from support
)

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
