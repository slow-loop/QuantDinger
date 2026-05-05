# Factor: Range Fade (mean reversion in low-trend regimes)
# Source: cap_013_range_fade — IC=-0.101 in crypto-kol-quant
# Faithful port of capabilities/patterns.py:123-131.
# NOTE: original IC is NEGATIVE — fading the range loses money.
# Use this factor REVERSED (the score's sign is the *naive* fade direction;
# negative IC means inverting it acts as a trend-follow filter).

import pandas as pd
import numpy as np

df = df.copy()


def _adx(high, low, close, period=14):
    up = high.diff()
    dn = -low.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=high.index)
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0)


adx14 = _adx(df['high'], df['low'], df['close'], period=14)
high_20d = df['high'].rolling(window=20, min_periods=10).max()
low_20d = df['low'].rolling(window=20, min_periods=10).min()

in_range = adx14 < 20
range_pos = ((df['close'] - low_20d) / (high_20d - low_20d).replace(0, np.nan)).clip(0, 1)

# Naive fade: at top of range short, at bottom long.
df['range_fade_score'] = np.where(
    in_range & (range_pos > 0.85), -0.5,
    np.where(in_range & (range_pos < 0.15), 0.5, 0.0)
)

output = {
    "name": "Factor Range Fade",
    "plots": [
        {"name": "High20d", "data": high_20d.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "Low20d", "data": low_20d.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "range_fade_score", "data": df['range_fade_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
