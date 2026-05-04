# Factor: Horizontal Level Reclaim
# Source: emg_014_horizontal_reclaim (CryptoTony__) — IC=+0.084 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:113-120.
# Triggers when price reclaims a previously-lost 50-day high.

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
