# Factor: OHLC Anchor Framework (weekly open as structural anchor)
# Source: emg_027_ohlc_anchor_framework (KillaXBT) — IC=+0.109 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:165-178.
# Continuous tanh score of price-vs-weekly-open distance.

import pandas as pd
import numpy as np

df = df.copy()

# Derive day_of_week (0 = Monday). Sandbox uses df['time']; IC tester uses DatetimeIndex.
if 'time' in df.columns:
    day_of_week = pd.to_datetime(df['time']).dt.dayofweek.values
else:
    day_of_week = df.index.dayofweek
day_of_week = pd.Series(day_of_week, index=df.index)

# Weekly open: forward-fill the open from each Monday across the week.
week_open = df['open'].where(day_of_week == 0).ffill()

pct_diff = (df['close'] - week_open) / week_open
# Smoothed tanh score in [-0.4, +0.4]
df['anchor_score'] = (np.tanh(pct_diff * 5) * 0.4).fillna(0.0)

output = {
    "name": "Factor OHLC Anchor",
    "plots": [
        {"name": "WeeklyOpen", "data": week_open.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
        {"name": "anchor_score", "data": df['anchor_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
