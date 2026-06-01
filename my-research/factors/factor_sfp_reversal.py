"""
Factor:     sfp_reversal
Hypothesis: A swing failure pattern below a prior swing low marks a stop hunt:
            price sweeps the low, closes back above the swept level, and resolves
            in the upper half of the bar on elevated volume.
Source:     Extracted from strategies/tv_sfp_reversal_eth_4h_long.py.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Reusable SFP event factor for rank/scanner use.
"""

# @param swing_lookback int 10
# @param vol_mult float 1.5

import pandas as pd
import numpy as np

df = df.copy()

swing_lookback = int(params.get('swing_lookback', 10))
vol_mult = float(params.get('vol_mult', 1.5))

prior_swing_low = df['low'].shift(1).rolling(swing_lookback).min()
sweeps_swing_low = df['low'] < prior_swing_low
recovers_above_level = df['close'] > prior_swing_low

bar_range = (df['high'] - df['low']).replace(0, np.nan)
close_pos = ((df['close'] - df['low']) / bar_range).fillna(0)
close_upper = close_pos > 0.5

vol_sma = df['volume'].rolling(20).mean()
vol_ratio = (df['volume'] / vol_sma.replace(0, np.nan)).fillna(0)
vol_ok = vol_ratio > vol_mult

trigger = (sweeps_swing_low & recovers_above_level & close_upper & vol_ok).fillna(False)

sweep_depth = ((prior_swing_low - df['low']) / prior_swing_low.replace(0, np.nan)).clip(lower=0).fillna(0)
reclaim_depth = ((df['close'] - prior_swing_low) / prior_swing_low.replace(0, np.nan)).clip(lower=0).fillna(0)
close_depth = ((close_pos - 0.5) / 0.5).clip(lower=0)
vol_depth = ((vol_ratio - vol_mult) / vol_mult).clip(lower=0)
strength = (0.3 * sweep_depth * 10 + 0.3 * reclaim_depth * 10 + 0.2 * close_depth + 0.2 * vol_depth).clip(0, 3)

df['sfp_prior_swing_low'] = prior_swing_low
df['sfp_close_pos'] = close_pos
df['sfp_volume_ratio'] = vol_ratio
df['sfp_reversal_trigger'] = trigger.astype(int)
df['sfp_reversal_strength'] = np.where(trigger, strength, 0.0)
df['sfp_reversal_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor SFP Reversal",
    "plots": [
        {"name": "sfp_prior_swing_low", "data": df['sfp_prior_swing_low'].fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "sfp_close_pos", "data": df['sfp_close_pos'].tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "sfp_reversal_score", "data": df['sfp_reversal_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
