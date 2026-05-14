"""
Strategy: tv_bar_exhaustion_reversal_eth_4h_long
Thesis:   After N consecutive bearish bars (each closing lower than it opened), directional
          momentum is exhausted. If this exhaustion occurs near a structural support level
          (swing low), the first bullish bar is an entry signal. Based on TradingView's
          "Bar Counter Trend Reversal" (569 likes) adapted with a structural S/R gate
          to avoid catching falling knives in trending bear moves.
Source:   TradingView "Bar Counter Trend Reversal" by various authors (569 likes community):
          https://www.tradingview.com/scripts/
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-14  code  init. Consecutive_bear: rolling count of bars where close < open.
                    S/R gate: price within 2×ATR of rolling N-bar low (structural support).
                    Entry: consecutive_bear >= 5 + S/R gate + current bar is bullish (close > open).
                    Stop: rolling low - 0.5×ATR. Timeout: 15 bars.
  2026-05-14  run   BTC 4H IS: Sharpe +2.119, Sortino +1.692, Calmar +16.15, IR +1.919,
                    PF 1.425, Win% 50.8%, payoff 1.380, n=63. FAIL (PF<1.5).
                    BTC 4H OOS: Sharpe -1.097, Sortino -0.522, PF 0.667, Win% 38.5%,
                    payoff 1.068, n=13. FAIL all.
                    (log: 2026-05-14)
  2026-05-14  note  Archive. IS shows mild edge but OOS collapses hard (Sharpe -1.097,
                    Win% drops from 50.8% to 38.5%). The "5 consecutive bear bars near support"
                    pattern is a falling-knife setup in trending bear markets — exactly the
                    2025-2026 OOS regime. S/R gate (rolling N-bar low) is circular: price is
                    near its own low by construction after 5 down bars. No structural edge
                    beyond momentum continuation risk.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param consec_threshold int 5
# @param sr_lookback int 40
# @param sr_atr_mult float 2.0
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

consec_threshold = int(params.get('consec_threshold', 5))
sr_lookback      = int(params.get('sr_lookback', 40))
sr_atr_mult      = float(params.get('sr_atr_mult', 2.0))
timeout_bars     = int(params.get('timeout_bars', 15))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Consecutive bearish bars ---
is_bearish = (df['close'] < df['open']).astype(int)
consec_bear = is_bearish.rolling(consec_threshold).sum()
enough_bear = consec_bear >= consec_threshold

# --- S/R gate: price near rolling N-bar low ---
swing_low = df['low'].rolling(sr_lookback).min()
near_support = df['low'] <= swing_low + atr * sr_atr_mult

# --- Entry: first bullish bar after exhaustion near support ---
# Current bar is bullish
is_bullish_bar = df['close'] > df['open']

# Exhaustion was in previous bar (consec_bear counts closed bars)
prior_exhaustion = enough_bear.shift(1).fillna(False).astype(bool)

df['buy'] = (prior_exhaustion & near_support & is_bullish_bar).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Bar Exhaustion Reversal ETH 4H Long",
    "plots": [
        {"name": "swing_low",   "data": swing_low.fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "consec_bear", "data": consec_bear.fillna(0).tolist(),"color": "#FF9800", "overlay": False},
        {"name": "ATR",         "data": atr.fillna(0).tolist(),        "color": "#9C27B0", "overlay": False},
    ]
}
