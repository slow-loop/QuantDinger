# Factor: HTF Reclaim + Retest (weekly MA reclaim with retest confirmation)
# Source: emg_007_htf_reclaim_retest (ColdBloodShill) — IC=+0.053 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:54-63.

import pandas as pd
import numpy as np

df = df.copy()

# 20 weeks = 140 daily bars
ma_20w = df['close'].rolling(window=140, min_periods=50).mean()

above_now = df['close'] > ma_20w
was_below = df['close'].shift(5) < ma_20w.shift(5)
# Retest: today's low touched within 2% of the 20W MA
retest = (df['low'] - ma_20w).abs() / df['close'] < 0.02

trig = above_now & was_below & retest

df['htf_reclaim_score'] = np.where(trig.fillna(False), 0.6, 0.0)

output = {
    "name": "Factor HTF Reclaim Retest",
    "plots": [
        {"name": "MA20W", "data": ma_20w.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "htf_reclaim_score", "data": df['htf_reclaim_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
