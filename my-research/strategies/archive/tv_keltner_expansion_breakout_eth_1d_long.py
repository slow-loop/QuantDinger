"""
Strategy: tv_keltner_expansion_breakout_eth_1d_long
Thesis:   Same Keltner compression→expansion mechanism as tv_keltner_expansion_breakout_eth_4h_long
          (active, IR +1.15, +20pp alpha OOS), now on 1D timeframe. Daily timeframe produces
          larger per-trade moves (better payoff ratio) and reduces fee drag (fewer trades).
          The 4H version had win rate 33.3% + payoff 2.01 = breakeven PF. 1D should produce
          higher payoff per winning trade, pushing PF and Sharpe above thresholds.
Source:   Structural variant of tv_keltner_expansion_breakout_eth_4h_long.
          Same mechanism; timeframe change is structural (different trade duration, regime).
          Keltner Channel Breakout concept — ETH 1D application.
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. Identical Keltner logic to 4H version. Adjusted compression
                    to compress_bars=5 over look_back=10 daily bars (5 weeks compression).
                    EMA20 midline, ATR14, mult=2.0. Exit: close below EMA midline OR 20-bar
                    timeout (20 trading days). Testing 1D vs 4H payoff improvement hypothesis.
  2026-05-12  run   ETH 1D OOS: Sharpe -0.514, PF 0.65, Win% 28.6%, n=7. FAIL 0/5. Archived.
  2026-05-12  note  1D too sparse (n=7 OOS). Win rate collapsed vs 4H (28.6% vs 33.3%).
                    1D Keltner bands are too wide — compression inside 2x ATR on daily is
                    harder to break convincingly. The 4H version remains the better timeframe.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param ema_len int 20
# @param atr_len int 14
# @param atr_mult float 2.0
# @param compress_bars int 5
# @param look_back int 10
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

ema_len       = int(params.get('ema_len', 20))
atr_len       = int(params.get('atr_len', 14))
atr_mult      = float(params.get('atr_mult', 2.0))
compress_bars = int(params.get('compress_bars', 5))
look_back     = int(params.get('look_back', 10))
timeout_bars  = int(params.get('timeout_bars', 20))

# EMA midline
ema = df['close'].ewm(span=ema_len, adjust=False).mean()

# ATR (Wilder)
high_low = df['high'] - df['low']
high_pc  = (df['high'] - df['close'].shift(1)).abs()
low_pc   = (df['low']  - df['close'].shift(1)).abs()
tr       = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
atr      = tr.ewm(alpha=1/atr_len, adjust=False).mean()

# Keltner bands
upper_band = ema + atr_mult * atr
lower_band = ema - atr_mult * atr

# Compression detection (shifted to avoid lookahead)
inside_channel = (df['close'] <= upper_band) & (df['close'] >= lower_band)
bars_inside_recent = inside_channel.shift(1).rolling(look_back).sum()
was_compressed = bars_inside_recent >= compress_bars

# Entry: breakout above upper band after compression
above_upper = df['close'] > upper_band.shift(1)
df['buy'] = (above_upper & was_compressed).fillna(False).astype(bool)

# Exit: close below EMA midline (structural midline rejection)
df['sell'] = (df['close'] < ema.shift(1)).fillna(False).astype(bool)
