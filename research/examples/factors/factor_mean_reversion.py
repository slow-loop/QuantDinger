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
