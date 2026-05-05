"""
Factor:     mean_reversion
Hypothesis: Price deviation from its 20-bar rolling mean (z-score) predicts short-term reversal.
            Extreme negative z-score = oversold (long signal); extreme positive = overbought (short).
Source:     own composition. Z-score mean reversion is a fundamental statistical arbitrage concept.
Status:     active

History (append-only, newest at bottom):
  2026-05-06  code  init. reversion_z_score = (close - rolling_mean) / rolling_std, window=20.
  2026-05-06  run   BTC/USDT 4H IC — 1d: IC_IS -0.019 / IC_OOS -0.043 p=0.04 ✅ (stable, significant)
                    7d: IC ~-0.002 (not significant). 30d: IC ~+0.006 (reversed sign, ignore).
                    Edge decays rapidly past 1-day horizon.
                    (log: 2026-05-06)
  2026-05-06  note  Clear 1d edge (6 4H bars forward). High z-score → lower next-day return (mean reverts).
                    Build strategy: buy when z < -2 (fresh oversold), exit when z > -0.5 or 10-bar timeout.
"""

# @param lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

lookback = int(params.get('lookback', 20))

mean = df['close'].rolling(window=lookback).mean()
std = df['close'].rolling(window=lookback).std()

# Z-Score (how many standard deviations away from the mean)
z_score = (df['close'] - mean) / std

# Score: Positive means overbought (reversion risk), Negative means oversold (bounce potential)
df['reversion_z_score'] = z_score

output = {
    "name": "Factor Mean Reversion",
    "plots": [
        {"name": "Z_Score", "data": df['reversion_z_score'].fillna(0).tolist(), "color": "#faad14", "overlay": False}
    ]
}
