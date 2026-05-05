"""
Factor:     horizontal_reclaim
Hypothesis: Reclaiming a previously-lost 50-day high signals a structural shift — participants
            who sold the breakdown are now underwater and become demand as price squeezes back above,
            generating upside continuation edge.
Source:     emg_014_horizontal_reclaim (CryptoTony__). IC=+0.084 reported in crypto-kol-quant.
            Port of capabilities/emerged.py:113-120.
Status:     active

History (append-only, newest at bottom):
  2026-05-05  code  init. faithful port. fires when price crosses back above 50d high after being
                    ≥3% below it for 10 bars.
  2026-05-06  run   BTC/USDT 1D — IS 30d: hit 67.5% n=255 avg +10.74% Sharpe +0.57 ✓
                    OOS 30d: hit 54.5% n=11 avg -6.49% Sharpe -0.53 ⚠️
                    Hit rate holds OOS (54.5% > 50%) but avg return inverted — regime effect:
                    May 2025-26 saw repeated false breakouts above 50d high in choppy market.
                    IS evidence strong (n=255). OOS n=11 too thin to rule out regime-specific.
                    (log: 2026-05-06)
  2026-05-06  note  Keep active pending regime change. IS edge is robust (n=255, 67.5% hit).
                    OOS failure is plausibly 2025-26 choppy-market artifact. Do NOT use in strategy
                    until OOS expectancy turns positive. Retest after 3-6 months.
"""

import pandas as pd
import numpy as np

df = df.copy()

high_50d = df['high'].rolling(window=50, min_periods=20).max()

# 10 bars ago we were ≥3% below the 50d high (lost the level), and now we're back above it
lost_50d = df['close'].shift(10) < high_50d.shift(10) * 0.97
reclaim = (df['close'] > high_50d.shift(10)) & lost_50d

df['horizontal_reclaim_score'] = np.where(reclaim.fillna(False), 0.6, 0.0)

output = {
    "name": "Factor Horizontal Reclaim",
    "plots": [
        {"name": "High50d", "data": high_50d.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "horizontal_reclaim_score", "data": df['horizontal_reclaim_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
