"""
Strategy: tv_funding_extreme_long_4h
Thesis:   Extremely negative funding means perp traders are crowded short. If price
          is also stretched below its recent mean, the setup is a short-squeeze /
          mean-reversion candidate. This is intentionally funding-first and generic
          across liquid alt perps; validate per symbol before reuse.
Source:   2026-05-15 X / Reddit / public-web social scouting notes:
          funding-rate extreme contrarian long for small-cap / altcoin perps.
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. Funding z-score <= -1.5, funding < 0, close z-score <= -1.0.
                    Exit when funding normalizes, close reverts to mean, or timeout fires.
                    Built for AVAX/LINK/ARB/OP/DOGE cross-test.
  2026-05-15  run   Cross-test AVAX/LINK/ARB/OP/DOGE 4H. OOS:
                    AVAX PASS 5/5 — Sharpe +3.807, Sortino +2.403, Calmar +39.031,
                    IR +3.258, PF 2.479, win 70.4%, n=27.
                    DOGE PASS 5/5 — Sharpe +3.805, Sortino +2.181, Calmar +30.096,
                    IR +2.918, PF 2.678, win 62.1%, n=29.
                    LINK PASS 4/5 — Sharpe +2.364, Sortino +1.252, IR +1.716,
                    PF 1.702, n=27. ARB weak 1/5; OP failed with -20.86% OOS.
                    Best current small-cap funding candidate: AVAX/DOGE.
                    (log: 2026-05-15T06:11:37..06:12:26)
"""

# @strategy stopLossPct 0.08
# @strategy trailingEnabled true
# @strategy trailingStopPct 0.05
# @strategy trailingActivationPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 0.50

# @param funding_z_threshold float -1.5
# @param price_z_threshold float -1.0
# @param funding_lookback int 60
# @param price_lookback int 20
# @param timeout_bars int 18

import pandas as pd
import numpy as np

df = df.copy()

if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

funding_z_threshold = float(params.get('funding_z_threshold', -1.5))
price_z_threshold = float(params.get('price_z_threshold', -1.0))
funding_lookback = int(params.get('funding_lookback', 60))
price_lookback = int(params.get('price_lookback', 20))
timeout_bars = int(params.get('timeout_bars', 18))

funding_mean = df['funding_rate'].rolling(funding_lookback).mean()
funding_std = df['funding_rate'].rolling(funding_lookback).std().replace(0, np.nan)
funding_z = ((df['funding_rate'] - funding_mean) / funding_std).fillna(0)

price_mean = df['close'].rolling(price_lookback).mean()
price_std = df['close'].rolling(price_lookback).std().replace(0, np.nan)
price_z = ((df['close'] - price_mean) / price_std).fillna(0)

funding_extreme = (funding_z <= funding_z_threshold) & (df['funding_rate'] < 0)
price_stretched = price_z <= price_z_threshold

df['buy'] = (funding_extreme & price_stretched).fillna(False)

funding_normalized = funding_z > 0
price_reverted = price_z > 0
timeout_exit = df['buy'].shift(timeout_bars).fillna(False)
df['sell'] = (funding_normalized | price_reverted | timeout_exit).fillna(False)

df['buy'] = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)

output = {
    "name": "Funding Extreme Contrarian Long 4H",
    "plots": [
        {"name": "funding_z", "data": funding_z.fillna(0).tolist(), "color": "#FF9800", "overlay": False},
        {"name": "price_z", "data": price_z.fillna(0).tolist(), "color": "#00BCD4", "overlay": False},
        {"name": "funding_rate", "data": df['funding_rate'].fillna(0).tolist(), "color": "#9C27B0", "overlay": False},
    ],
}
