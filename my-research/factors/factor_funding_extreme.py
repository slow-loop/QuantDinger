"""
Factor:     funding_extreme
Hypothesis: Extremely negative funding plus downside price stretch marks crowded
            short positioning and forced-positioning exhaustion in alt perps.
Source:     Extracted from strategies/tv_funding_extreme_long_4h.py after the
            2026-05-15 expanded alt matrix showed broad OOS usefulness.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Reusable factor layer for funding z-score crowding
                    plus price z-score stretch. Emits trigger, strength, score.
"""

# @param funding_z_threshold float -1.5
# @param price_z_threshold float -1.0
# @param funding_lookback int 60
# @param price_lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

funding_z_threshold = float(params.get('funding_z_threshold', -1.5))
price_z_threshold = float(params.get('price_z_threshold', -1.0))
funding_lookback = int(params.get('funding_lookback', 60))
price_lookback = int(params.get('price_lookback', 20))

funding_mean = df['funding_rate'].rolling(funding_lookback).mean()
funding_std = df['funding_rate'].rolling(funding_lookback).std().replace(0, np.nan)
funding_z = ((df['funding_rate'] - funding_mean) / funding_std).fillna(0)

price_mean = df['close'].rolling(price_lookback).mean()
price_std = df['close'].rolling(price_lookback).std().replace(0, np.nan)
price_z = ((df['close'] - price_mean) / price_std).fillna(0)

funding_extreme = (funding_z <= funding_z_threshold) & (df['funding_rate'] < 0)
price_stretched = price_z <= price_z_threshold
trigger = (funding_extreme & price_stretched).fillna(False)

funding_depth = ((funding_z_threshold - funding_z) / abs(funding_z_threshold)).clip(lower=0)
price_depth = ((price_z_threshold - price_z) / abs(price_z_threshold)).clip(lower=0)
strength = (0.6 * funding_depth + 0.4 * price_depth).clip(0, 3)

df['funding_z'] = funding_z
df['price_z'] = price_z
df['funding_extreme_trigger'] = trigger.astype(int)
df['funding_extreme_strength'] = np.where(trigger, strength, 0.0)
df['funding_extreme_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor Funding Extreme",
    "plots": [
        {"name": "funding_z", "data": df['funding_z'].tolist(), "color": "#FF9800", "overlay": False},
        {"name": "price_z", "data": df['price_z'].tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "funding_extreme_score", "data": df['funding_extreme_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
