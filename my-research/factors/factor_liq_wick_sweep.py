"""
Factor:     liq_wick_sweep
Hypothesis: A bar that sweeps below a recent low, prints a dominant lower wick,
            recovers, and arrives on elevated volume is a liquidation-wick
            absorption event.
Source:     Extracted from strategies/tv_liq_wick_sweep_eth_4h_long.py after
            the 2026-05-15 expanded alt matrix showed cross-alt usefulness.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Reusable liquidation wick event factor with trigger,
                    strength, and bounded positive score.
"""

# @param sweep_lookback int 20
# @param wick_ratio float 0.65
# @param vol_mult float 1.5

import pandas as pd
import numpy as np

df = df.copy()

sweep_lookback = int(params.get('sweep_lookback', 20))
wick_ratio = float(params.get('wick_ratio', 0.65))
vol_mult = float(params.get('vol_mult', 1.5))

vol_sma = df['volume'].rolling(20).mean()
vol_ratio = (df['volume'] / vol_sma.replace(0, np.nan)).fillna(0)
vol_ok = vol_ratio > vol_mult

prior_low = df['low'].shift(1).rolling(sweep_lookback).min()
sweeps_low = df['low'] < prior_low
recovers = df['close'] > df['close'].shift(1)

bar_range = (df['high'] - df['low']).replace(0, np.nan)
lower_wick = df['close'] - df['low']
wick_pct = (lower_wick / bar_range).fillna(0)
wick_dom = wick_pct > wick_ratio

trigger = (sweeps_low & recovers & wick_dom & vol_ok).fillna(False)

sweep_depth = ((prior_low - df['low']) / prior_low.replace(0, np.nan)).clip(lower=0).fillna(0)
wick_depth = ((wick_pct - wick_ratio) / max(1 - wick_ratio, 1e-12)).clip(lower=0)
vol_depth = ((vol_ratio - vol_mult) / vol_mult).clip(lower=0)
strength = (0.4 * wick_depth + 0.35 * sweep_depth * 10 + 0.25 * vol_depth).clip(0, 3)

df['liq_wick_prior_low'] = prior_low
df['liq_wick_lower_wick_pct'] = wick_pct
df['liq_wick_volume_ratio'] = vol_ratio
df['liq_wick_sweep_trigger'] = trigger.astype(int)
df['liq_wick_sweep_strength'] = np.where(trigger, strength, 0.0)
df['liq_wick_sweep_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor Liq Wick Sweep",
    "plots": [
        {"name": "liq_wick_prior_low", "data": df['liq_wick_prior_low'].fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "liq_wick_lower_wick_pct", "data": df['liq_wick_lower_wick_pct'].tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "liq_wick_sweep_score", "data": df['liq_wick_sweep_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
