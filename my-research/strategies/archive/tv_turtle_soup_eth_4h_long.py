"""
Strategy: tv_turtle_soup_eth_4h_long
Thesis:   Turtle Soup Plus One (Linda Raschke) — when price makes a new 20-bar low
          (the classic Turtle System short entry), retail breakout traders enter short.
          If the NEXT bar ("plus one") opens AND closes above the broken 20-bar low,
          those Turtle shorts are trapped; their stop-loss BUYs at the level creates
          a short-covering squeeze. Enter long on close of the confirmation bar.
          Key difference from liq_wick_sweep / SFP: entry fires on bar N+1 (not bar N itself),
          specifically requiring the follow-through confirmation of the false breakdown.
          The 20-bar lookback matches the Turtle System's original parameter.
Source:   Linda Raschke "Turtle Soup Plus One":
          https://www.cryptodatadownload.com/blog/posts/turtle-soup-trading-strategy-python-cryptocurrency/
          ICT synthesis of Turtle Soup reversal:
          https://innercircletrader.net/tutorials/ict-turtle-soup-pattern/
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-15  code  init. Turtle soup long:
                    Bar N: new 20-bar low (low < rolling 20-bar min).
                    Bar N+1: opens and closes ABOVE the 20-bar low level that was broken on N.
                    (This is the "plus one" confirmation — false breakdown confirmed.)
                    Volume gate on bar N+1: volume > vol_mult × SMA20.
                    Exit: timeout 20 bars. Stop: 5% (platform).
  2026-05-15  run   ETH/USDT 4H IS: Sharpe -0.146, Sortino -0.089, PF 0.938, Win% 54.8%,
                    payoff 0.774, n=73. FAIL.
                    ETH/USDT 4H OOS: Sharpe -1.222, Sortino -0.702, PF 0.676, Win% 47.1%,
                    payoff 0.761, n=17. FAIL.
                    (log: 2026-05-15)
  2026-05-15  note  Archive. Both IS and OOS fail. On 4H, a new 20-bar low followed by
                    next-bar close above the broken level fires 73 IS trades = 14.6/year.
                    This is not a selective pattern — any volatile bar followed by a modest
                    bounce qualifies. Bear market amplifies failure: Turtle shorts are NOT
                    trapped (they're correct), so next-bar recovery is shallow and continued
                    selling resumes. The "Plus One" confirmation adds only one bar of delay
                    but doesn't filter out genuine breakdowns. Needs an additional regime
                    filter (e.g., ranging market gate via ADX < 20) to have real selectivity.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param turtle_lookback int 20
# @param vol_mult float 1.3
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

turtle_lookback = int(params.get('turtle_lookback', 20))
vol_mult        = float(params.get('vol_mult', 1.3))
timeout_bars    = int(params.get('timeout_bars', 20))

# --- Prior N-bar low (no lookahead: shift by 1) ---
rolling_n_low = df['low'].shift(1).rolling(turtle_lookback).min()

# --- Bar N: makes a new N-bar low ---
made_new_low = df['low'] < rolling_n_low

# --- Bar N+1 ("plus one"): confirmation of false breakdown ---
# The level that was broken on bar N = rolling_n_low on bar N = rolling_n_low.shift(1) on bar N+1
broken_level         = rolling_n_low.shift(1)
prev_made_new_low    = made_new_low.shift(1)

# Confirmation: bar N+1 closes above the broken level (false breakdown)
close_above_broken  = df['close'] > broken_level

# Volume gate on the confirmation bar
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- Entry on bar N+1 ---
df['buy'] = (prev_made_new_low & close_above_broken & vol_ok).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Turtle Soup Plus One ETH 4H Long",
    "plots": [
        {"name": "rolling_n_low", "data": rolling_n_low.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "vol_SMA20",     "data": vol_sma.fillna(0).tolist(),       "color": "#9E9E9E", "overlay": False},
    ]
}
