"""
Factor:     funding_bottom_fisher
Hypothesis: Short-term price capitulation plus negative funding marks a bottom
            fishing setup where crowded shorts can be squeezed.
Source:     Extracted from strategies/funding_rate_bottom_fisher.py, retained as
            the simple threshold baseline against funding-z variants.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Emits price z-score, threshold trigger, strength, score.
"""

# @param funding_threshold float -0.0001
# @param z_score_threshold float -1.5
# @param z_lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

funding_threshold = float(params.get('funding_threshold', -0.0001))
z_score_threshold = float(params.get('z_score_threshold', -1.5))
z_lookback = int(params.get('z_lookback', 20))

mean = df['close'].rolling(window=z_lookback).mean()
std = df['close'].rolling(window=z_lookback).std().replace(0, np.nan)
price_z = ((df['close'] - mean) / std).fillna(0)

trigger = ((price_z < z_score_threshold) & (df['funding_rate'] <= funding_threshold)).fillna(False)

price_depth = ((z_score_threshold - price_z) / abs(z_score_threshold)).clip(lower=0)
funding_depth = ((funding_threshold - df['funding_rate']) / max(abs(funding_threshold), 1e-12)).clip(lower=0)
strength = (0.55 * price_depth + 0.45 * funding_depth).clip(0, 3)

df['funding_bottom_price_z'] = price_z
df['funding_bottom_trigger'] = trigger.astype(int)
df['funding_bottom_strength'] = np.where(trigger, strength, 0.0)
df['funding_bottom_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor Funding Bottom Fisher",
    "plots": [
        {"name": "funding_bottom_price_z", "data": df['funding_bottom_price_z'].tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "funding_bottom_score", "data": df['funding_bottom_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
