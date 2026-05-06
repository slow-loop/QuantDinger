"""
Factor:     liquidity_grab
Hypothesis: A liquidity grab (stop hunt) occurs when price spikes beyond a 10-bar extreme to
            trigger clustered stop orders, then reverses and closes in the opposite direction.
            Lower wick grab (spike below 10-bar low, close > open): bullish reversal signal.
            Upper wick grab (spike above 10-bar high, close < open): bearish reversal signal.
            The wick must comprise > 50% of the bar's total range to confirm the hunt.
            Long score: +0.65 (lower wick grab). Short score: -0.65 (upper wick grab).
Source:     cap_052_liquidity_grab. IC=+0.65 in crypto-kol-quant.
            Faithful port of capabilities/patterns.py:cap_052 logic.
Status:     archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Lower wick grab: low < 10-bar min low + lower_wick_pct > 0.5 + close > open.
                    Upper wick grab: high > 10-bar max high + upper_wick_pct > 0.5 + close < open.
                    Score: +0.65 (bull), -0.65 (bear). Source: cap_052 (IC 0.65).
  2026-05-06  run   BTC 1D: IS long n=33 30d hit=45.5%, short n=35 30d hit=54.3%. Avg returns ≈ 0.
                    BTC 4H: IS long n=213 30d Sharpe +0.056; short n=211 anti-predicted (upper wick
                    bullish on BTC 57% of the time).
  2026-05-06  note  ARCHIVED. Hit rate stable (58% long on 4H) but avg returns negligible — no P&L
                    net of costs. Upper wick grab is anti-predicted: bearish signal is actually bullish
                    on BTC. IC 0.65 was cross-sectional altcoin score; no edge on BTC/ETH.
"""

# @param lookback int 10
# @param wick_threshold float 0.5

import pandas as pd
import numpy as np

df = df.copy()

lookback = int(params.get('lookback', 10))
wick_threshold = float(params.get('wick_threshold', 0.5))

bar_range = (df['high'] - df['low']).replace(0, np.nan)

upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
lower_wick = df[['open', 'close']].min(axis=1) - df['low']

upper_wick_pct = (upper_wick / bar_range).fillna(0)
lower_wick_pct = (lower_wick / bar_range).fillna(0)

# 10-bar rolling extremes (shifted to avoid lookahead)
rolling_high = df['high'].rolling(window=lookback, min_periods=lookback // 2).max().shift(1)
rolling_low = df['low'].rolling(window=lookback, min_periods=lookback // 2).min().shift(1)

# Bullish: spike below 10-bar low, large lower wick, close above open (rejection)
wick_dn = (
    (df['low'] < rolling_low) &
    (lower_wick_pct > wick_threshold) &
    (df['close'] > df['open'])
)

# Bearish: spike above 10-bar high, large upper wick, close below open (rejection)
wick_up = (
    (df['high'] > rolling_high) &
    (upper_wick_pct > wick_threshold) &
    (df['close'] < df['open'])
)

df['liquidity_grab_score'] = np.where(wick_dn, 0.65, np.where(wick_up, -0.65, 0.0))

output = {
    "name": "Factor Liquidity Grab",
    "plots": [
        {"name": "rolling_high", "data": rolling_high.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "rolling_low", "data": rolling_low.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "lower_wick_pct", "data": lower_wick_pct.fillna(0).tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "liquidity_grab_score", "data": df['liquidity_grab_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
