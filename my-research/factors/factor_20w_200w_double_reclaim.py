# Factor: 20W + 200W MA Double Reclaim
# Source: emg_028_20w_200w_double_reclaim (LedgerStatus) — IC=+0.068 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:143-152.
# Triggers when price reclaims BOTH 20W and 200W MAs after being below either.

import pandas as pd
import numpy as np

df = df.copy()

# 20 weeks = 140 daily bars; 200 weeks = 1400 daily bars
ma_20w = df['close'].rolling(window=140, min_periods=50).mean()
ma_200w = df['close'].rolling(window=1400, min_periods=200).mean()

above_both = (df['close'] > ma_20w) & (df['close'] > ma_200w)
was_below_either = (df['close'].shift(3) < ma_20w.shift(3)) | (df['close'].shift(3) < ma_200w.shift(3))
trig = above_both & was_below_either

df['double_reclaim_score'] = np.where(trig.fillna(False), 0.75, 0.0)

output = {
    "name": "Factor 20W+200W Double Reclaim",
    "plots": [
        {"name": "MA20W", "data": ma_20w.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "MA200W", "data": ma_200w.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "double_reclaim_score", "data": df['double_reclaim_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
