"""
Factor:     funding_liq_wick
Hypothesis: A liquidation-wick sweep is higher conviction when funding already
            shows crowded short positioning. This is intentionally stricter than
            raw liq_wick_sweep and should be treated as sparse confirmation.
Source:     Extracted from strategies/tv_funding_liq_wick_4h_long.py.
Status:     active

History (append-only, newest at bottom):
  2026-05-18  code  init. Combined funding-z plus liq wick confirmation factor.
"""

# @param sweep_lookback int 20
# @param wick_ratio float 0.65
# @param vol_mult float 1.5
# @param funding_z_threshold float -1.0
# @param funding_lookback int 60

import pandas as pd
import numpy as np

df = df.copy()

if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

sweep_lookback = int(params.get('sweep_lookback', 20))
wick_ratio = float(params.get('wick_ratio', 0.65))
vol_mult = float(params.get('vol_mult', 1.5))
funding_z_threshold = float(params.get('funding_z_threshold', -1.0))
funding_lookback = int(params.get('funding_lookback', 60))

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

funding_mean = df['funding_rate'].rolling(funding_lookback).mean()
funding_std = df['funding_rate'].rolling(funding_lookback).std().replace(0, np.nan)
funding_z = ((df['funding_rate'] - funding_mean) / funding_std).fillna(0)
funding_extreme = (funding_z <= funding_z_threshold) & (df['funding_rate'] < 0)

trigger = (sweeps_low & recovers & wick_dom & vol_ok & funding_extreme).fillna(False)

sweep_depth = ((prior_low - df['low']) / prior_low.replace(0, np.nan)).clip(lower=0).fillna(0)
wick_depth = ((wick_pct - wick_ratio) / max(1 - wick_ratio, 1e-12)).clip(lower=0)
vol_depth = ((vol_ratio - vol_mult) / vol_mult).clip(lower=0)
funding_depth = ((funding_z_threshold - funding_z) / abs(funding_z_threshold)).clip(lower=0)
strength = (0.3 * funding_depth + 0.3 * wick_depth + 0.25 * sweep_depth * 10 + 0.15 * vol_depth).clip(0, 3)

df['funding_liq_wick_funding_z'] = funding_z
df['funding_liq_wick_lower_wick_pct'] = wick_pct
df['funding_liq_wick_volume_ratio'] = vol_ratio
df['funding_liq_wick_trigger'] = trigger.astype(int)
df['funding_liq_wick_strength'] = np.where(trigger, strength, 0.0)
df['funding_liq_wick_score'] = np.where(trigger, np.tanh(strength / 2.0), 0.0)

output = {
    "name": "Factor Funding Liq Wick",
    "plots": [
        {"name": "funding_liq_wick_funding_z", "data": df['funding_liq_wick_funding_z'].tolist(), "color": "#FF9800", "overlay": False},
        {"name": "funding_liq_wick_lower_wick_pct", "data": df['funding_liq_wick_lower_wick_pct'].tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "funding_liq_wick_score", "data": df['funding_liq_wick_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
