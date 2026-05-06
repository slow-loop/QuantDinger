"""
Factor:     regime_trending_up
Hypothesis: A golden cross (MA50 > MA200) combined with strong trend strength (ADX > 25) defines
            a trending-up regime. When both conditions are met, the market is structurally bullish
            with directional momentum — a high-probability long environment. Score is binary: 1.0
            when regime is active, 0.0 otherwise.
Source:     cap_044_regime_trending_up. IC=+0.70 in crypto-kol-quant.
            Faithful port of capabilities/patterns.py:cap_044 logic.
Status:     archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Golden cross (MA50 > MA200) + ADX > 25. Binary score 1.0 / 0.0.
                    Source: cap_044 from crypto-kol-quant (IC 0.70).
  2026-05-06  run   BTC 1D event test: IS 30d hit=58.8% n=839 → OOS 30d hit=5.4% n=56. Reversed.
  2026-05-06  note  ARCHIVED. Golden cross + ADX regime is long-lived (839 IS triggers = always on in
                    bull market). OOS period (2025-26) was corrective/ranging — regime signal stayed
                    active but price fell. IC 0.70 was cross-sectional altcoin score; fails on BTC.
"""

# @param ma_fast int 50
# @param ma_slow int 200
# @param adx_period int 14
# @param adx_threshold float 25.0

import pandas as pd
import numpy as np

df = df.copy()

ma_fast = int(params.get('ma_fast', 50))
ma_slow = int(params.get('ma_slow', 200))
adx_period = int(params.get('adx_period', 14))
adx_threshold = float(params.get('adx_threshold', 25.0))

# Moving averages
ma_f = df['close'].rolling(window=ma_fast, min_periods=ma_fast // 2).mean()
ma_s = df['close'].rolling(window=ma_slow, min_periods=ma_slow // 2).mean()

golden_cross = ma_f > ma_s

# ADX calculation (Wilder's method)
high = df['high']
low = df['low']
close = df['close']

prev_close = close.shift(1)
tr = pd.concat([
    high - low,
    (high - prev_close).abs(),
    (low - prev_close).abs()
], axis=1).max(axis=1)

plus_dm = (high - high.shift(1)).clip(lower=0)
minus_dm = (low.shift(1) - low).clip(lower=0)
plus_dm = plus_dm.where(plus_dm > minus_dm, 0.0)
minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)

atr = tr.ewm(alpha=1 / adx_period, adjust=False).mean()
plus_di = 100 * plus_dm.ewm(alpha=1 / adx_period, adjust=False).mean() / atr.replace(0, np.nan)
minus_di = 100 * minus_dm.ewm(alpha=1 / adx_period, adjust=False).mean() / atr.replace(0, np.nan)

dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
adx = dx.ewm(alpha=1 / adx_period, adjust=False).mean()

strong_trend = adx > adx_threshold

regime_active = golden_cross & strong_trend
df['regime_trending_up_score'] = np.where(regime_active, 1.0, 0.0)

output = {
    "name": "Factor Regime Trending Up",
    "plots": [
        {"name": "ma_fast", "data": ma_f.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "ma_slow", "data": ma_s.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "adx", "data": adx.fillna(0).tolist(), "color": "#FFD700", "overlay": False},
        {"name": "regime_trending_up_score", "data": df['regime_trending_up_score'].tolist(), "color": "#00BCD4", "overlay": False},
    ]
}
