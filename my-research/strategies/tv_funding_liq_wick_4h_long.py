"""
Strategy: tv_funding_liq_wick_4h_long
Thesis:   A lower-wick liquidity sweep is more meaningful when perp positioning is
          already crowded short. Negative funding supplies the squeeze fuel; the
          liquidation-style wick confirms sellers were absorbed intrabar.
Source:   2026-05-15 X / Reddit / public-web social scouting notes:
          Funding Extreme + Liq Wick combination for small-cap / altcoin perps.
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. Liq-wick sweep proxy plus funding_z <= -1.0 and funding < 0.
                    Exit uses the existing liq-wick timeout. Built for AVAX/LINK/ARB/OP/DOGE
                    cross-test and comparison against raw liq-wick.
  2026-05-15  run   Cross-test AVAX/LINK/ARB/OP/DOGE 4H. OOS all failed:
                    LINK 1/5, -0.49%, n=4; AVAX 1/5, -0.11%, n=1;
                    DOGE 1/5, -1.45%, n=4; OP 1/5, -3.15%, n=4;
                    ARB 0/5, -9.18%, n=3. Funding gate over-filters the liq-wick
                    signal; raw liq-wick is materially better.
                    (log: 2026-05-15T06:13:56..06:14:46)
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param sweep_lookback int 20
# @param wick_ratio float 0.65
# @param vol_mult float 1.5
# @param funding_z_threshold float -1.0
# @param funding_lookback int 60
# @param timeout_bars int 15

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
timeout_bars = int(params.get('timeout_bars', 15))

tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low'] - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

vol_sma = df['volume'].rolling(20).mean()
vol_ok = df['volume'] > vol_sma * vol_mult

prior_low = df['low'].shift(1).rolling(sweep_lookback).min()
sweeps_low = df['low'] < prior_low
recovers = df['close'] > df['close'].shift(1)

bar_range = (df['high'] - df['low']).replace(0, np.nan)
lower_wick = df['close'] - df['low']
wick_dom = (lower_wick / bar_range) > wick_ratio

funding_mean = df['funding_rate'].rolling(funding_lookback).mean()
funding_std = df['funding_rate'].rolling(funding_lookback).std().replace(0, np.nan)
funding_z = ((df['funding_rate'] - funding_mean) / funding_std).fillna(0)
funding_extreme = (funding_z <= funding_z_threshold) & (df['funding_rate'] < 0)

df['buy'] = (sweeps_low & recovers & wick_dom & vol_ok & funding_extreme).fillna(False)
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy'] = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)

output = {
    "name": "Funding + Liquidation Wick Sweep 4H Long",
    "plots": [
        {"name": "prior_low", "data": prior_low.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "ATR", "data": atr.fillna(0).tolist(), "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20", "data": vol_sma.fillna(0).tolist(), "color": "#9E9E9E", "overlay": False},
        {"name": "funding_z", "data": funding_z.fillna(0).tolist(), "color": "#FF9800", "overlay": False},
    ],
}
