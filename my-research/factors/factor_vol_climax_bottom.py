"""
Factor:     vol_climax_bottom
Hypothesis: After a decline, an extreme volume spike plus large bar range and
            upper-half close marks seller exhaustion and buyer absorption.
Source:     Extracted from strategies/tv_vol_climax_bottom_eth_4h_long.py.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Reusable selling-climax bottom factor.
"""

# @param vol_mult float 3.0
# @param atr_mult float 1.5
# @param close_pos_min float 0.5
# @param decline_bars int 10

import pandas as pd
import numpy as np

df = df.copy()

vol_mult = float(params.get('vol_mult', 3.0))
atr_mult = float(params.get('atr_mult', 1.5))
close_pos_min = float(params.get('close_pos_min', 0.5))
decline_bars = int(params.get('decline_bars', 10))

tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low'] - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

vol_sma = df['volume'].rolling(20).mean()
vol_ratio = (df['volume'] / vol_sma.replace(0, np.nan)).fillna(0)
vol_spike = vol_ratio > vol_mult

bar_range = (df['high'] - df['low']).replace(0, np.nan)
range_ratio = (bar_range / atr.replace(0, np.nan)).fillna(0)
large_bar = range_ratio > atr_mult

close_pos = ((df['close'] - df['low']) / bar_range).fillna(0)
upper_half = close_pos > close_pos_min

close_sma_decline = df['close'].shift(1).rolling(decline_bars).mean()
price_was_declining = df['close'].shift(1) < close_sma_decline

trigger = (vol_spike & large_bar & upper_half & price_was_declining).fillna(False)

vol_depth = ((vol_ratio - vol_mult) / vol_mult).clip(lower=0)
range_depth = ((range_ratio - atr_mult) / atr_mult).clip(lower=0)
close_depth = ((close_pos - close_pos_min) / max(1 - close_pos_min, 1e-12)).clip(lower=0)
strength = (0.4 * vol_depth + 0.35 * range_depth + 0.25 * close_depth).clip(0, 3)

df['vol_climax_volume_ratio'] = vol_ratio
df['vol_climax_range_ratio'] = range_ratio
df['vol_climax_close_pos'] = close_pos
df['vol_climax_bottom_trigger'] = trigger.astype(int)
df['vol_climax_bottom_strength'] = np.where(trigger, strength, 0.0)
df['vol_climax_bottom_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor Vol Climax Bottom",
    "plots": [
        {"name": "vol_climax_volume_ratio", "data": df['vol_climax_volume_ratio'].tolist(), "color": "#9E9E9E", "overlay": False},
        {"name": "vol_climax_range_ratio", "data": df['vol_climax_range_ratio'].tolist(), "color": "#9C27B0", "overlay": False},
        {"name": "vol_climax_bottom_score", "data": df['vol_climax_bottom_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
