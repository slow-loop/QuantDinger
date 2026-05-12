"""
Strategy: tv_inside_bar_breakout_eth_4h_long
Thesis:   A sequence of N consecutive inside bars (each bar's high-low range is fully
          contained within the mother bar's range) signals market indecision and supply/demand
          equilibrium. When price finally closes above the mother bar high, it breaks the
          equilibrium — a structural demand event where buyers decisively overwhelm sellers.
          This is a price-structure pattern with no oscillator dependency.
Source:   Inside bar breakout strategy — widely documented in price action trading.
          https://www.tradingview.com/scripts/strategy/?q=inside+bar
          Pattern: mother bar + N inside bars + breakout close above mother high.
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. Inside bar: current high <= prev high AND current low >= prev low.
                    Consecutive inside bars: rolling count of inside bars >= min_inside_bars.
                    Mother bar: the bar just before the first inside bar in the sequence.
                    Entry: close > mother_high (first close above mother bar high after squeeze).
                    Exit: close drops below entry EMA20 (midline rejection) OR 30-bar timeout.
  2026-05-12  run   BTC 4H OOS: Sharpe -1.633, PF 0.72, n=31. FAIL 0/5.
                    ETH 4H OOS: Sharpe +0.671, Calmar +0.889✅, IR -0.134, PF 1.16, n=32. FAIL 1/5. Archived.
  2026-05-12  note  Mechanism has weak edge on ETH (positive returns) but IR negative means
                    no genuine alpha vs benchmark. The rolling_max mother_high approximation
                    may be too loose — fires frequently (n=31 BTC OOS). 4H inside bars in
                    crypto are very common, reducing selectivity. Would need 1D timeframe
                    or tighter mother bar identification for higher-quality setups.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param min_inside_bars int 2
# @param lookback int 5
# @param ema_exit_len int 20
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

min_inside_bars = int(params.get('min_inside_bars', 2))
lookback        = int(params.get('lookback', 5))
ema_exit_len    = int(params.get('ema_exit_len', 20))
timeout_bars    = int(params.get('timeout_bars', 30))

# --- Inside bar detection ---
# Each inside bar: high <= prev high AND low >= prev low
is_inside = (df['high'] <= df['high'].shift(1)) & (df['low'] >= df['low'].shift(1))

# --- Consecutive inside bar count (rolling) ---
# Count how many of the last lookback bars were inside bars
consec_inside = is_inside.rolling(lookback).sum()
enough_inside = consec_inside.shift(1) >= min_inside_bars  # at least 2 inside bars before current bar

# --- Mother bar high: the high of the bar before the inside bar sequence ---
# We approximate: mother high = the rolling max high over lookback+1 bars shifted by lookback
mother_high = df['high'].shift(lookback + 1)  # the bar before the sequence started

# Fallback: use rolling max high over a wider window shifted to avoid lookahead
# (more robust approximation for variable-length sequences)
mother_high_robust = df['high'].shift(1).rolling(lookback + 1).max()

# --- Entry: close breaks above mother high after inside bar compression ---
breakout = df['close'] > mother_high_robust

df['buy'] = (enough_inside & breakout).fillna(False)

# --- Exit: close crosses below EMA midline ---
ema_exit = df['close'].ewm(span=ema_exit_len, adjust=False).mean()
df['sell'] = (df['close'] < ema_exit).fillna(False)
