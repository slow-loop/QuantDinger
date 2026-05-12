"""
Strategy: tv_supertrend_atr_trail_4h_long
Thesis:   Supertrend indicator (ATR-based dynamic support/resistance) flips bullish
          when price breaks above the upper band, signaling a structural regime change
          from bearish to bullish. ATR-based trailing stop exits when trend reverses.
          ATR normalizes for crypto volatility, making the channel self-adjusting.
Source:   Adapted from Supertrend+atr by Darkphi (TradingView)
          https://www.tradingview.com/script/bK7ooPvS/
          Classic Supertrend algorithm (Wilder ATR, upper/lower band flip).
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Supertrend = HL/2 +/- atr_mult * ATR(atr_period). Flip
                    bullish when close > upper_band. Entry on flip bar. Exit when
                    Supertrend flips bearish (close < lower_band after being bullish).
                    ATR trailing: trail_mult * ATR below highest close since entry.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param atr_period int 10
# @param atr_mult float 3.0
# @param trail_mult float 2.0

import pandas as pd
import numpy as np

df = df.copy()

atr_period = int(params.get('atr_period', 10))
atr_mult = float(params.get('atr_mult', 3.0))
trail_mult = float(params.get('trail_mult', 2.0))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low'] - df['close'].shift(1)).abs()
], axis=1).max(axis=1)
atr = tr.ewm(span=atr_period, adjust=False).mean()

# --- Supertrend ---
hl2 = (df['high'] + df['low']) / 2
basic_upper = hl2 + atr_mult * atr
basic_lower = hl2 - atr_mult * atr

# Supertrend bands (vectorized approximation)
# Final upper band: min(basic_upper, prior final_upper) if prior close <= prior final_upper
# Final lower band: max(basic_lower, prior final_lower) if prior close >= prior final_lower
final_upper = basic_upper.copy()
final_lower = basic_lower.copy()

for i in range(1, len(df)):
    if df['close'].iloc[i-1] <= final_upper.iloc[i-1]:
        final_upper.iloc[i] = min(basic_upper.iloc[i], final_upper.iloc[i-1])
    else:
        final_upper.iloc[i] = basic_upper.iloc[i]

    if df['close'].iloc[i-1] >= final_lower.iloc[i-1]:
        final_lower.iloc[i] = max(basic_lower.iloc[i], final_lower.iloc[i-1])
    else:
        final_lower.iloc[i] = basic_lower.iloc[i]

# Supertrend direction: 1 = bullish (close > final_lower), -1 = bearish (close < final_upper)
supertrend = pd.Series(np.nan, index=df.index)
direction = pd.Series(0, index=df.index)

for i in range(1, len(df)):
    if df['close'].iloc[i] > final_upper.iloc[i-1]:
        direction.iloc[i] = 1
    elif df['close'].iloc[i] < final_lower.iloc[i-1]:
        direction.iloc[i] = -1
    else:
        direction.iloc[i] = direction.iloc[i-1]

# Entry: Supertrend flips from bearish to bullish
flip_bull = (direction == 1) & (direction.shift(1) == -1)

# Exit: Supertrend flips from bullish to bearish
flip_bear = (direction == -1) & (direction.shift(1) == 1)

df['buy'] = flip_bull.fillna(False)
df['sell'] = flip_bear.fillna(False)
