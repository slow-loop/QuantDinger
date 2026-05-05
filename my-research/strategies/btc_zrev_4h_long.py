"""
Strategy: btc_zrev_4h_long
Thesis:   Buy BTC when 4H close drops ≥2 std below its 20-bar mean (z < -2, fresh oversold),
          exit when price reverts toward mean (z > -0.5) or timeout. IC tester confirmed the
          1-day (6-bar) predictive edge: IC_OOS = -0.043, p = 0.04 — statistically significant.
Built on: factors/factor_mean_reversion.py
Status:   active

History (append-only, newest at bottom):
  2026-05-06  code  init. Entry: z-score crosses below -2 (first bar in oversold zone).
                    Exit: z rises above -0.5 OR 10-bar time stop. No stop loss — tight timeout
                    provides downside containment. Long only; no filter (first-pass test).
"""

# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param z_entry float -2.0
# @param z_exit float -0.5
# @param timeout_bars int 10
# @param lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

lookback = int(params.get('lookback', 20))
z_entry = float(params.get('z_entry', -2.0))
z_exit = float(params.get('z_exit', -0.5))
timeout_bars = int(params.get('timeout_bars', 10))

mean = df['close'].rolling(window=lookback, min_periods=lookback // 2).mean()
std = df['close'].rolling(window=lookback, min_periods=lookback // 2).std()
z = ((df['close'] - mean) / std.replace(0, np.nan)).fillna(0)

# Enter on first bar crossing into oversold zone
fresh_oversold = (z < z_entry) & (z.shift(1) >= z_entry)

# Exit when z recovers toward mean, OR time-based forced exit
z_recovered = (z > z_exit) & (z.shift(1) <= z_exit)
time_exit = fresh_oversold.shift(timeout_bars).fillna(False)

df['buy'] = fresh_oversold.fillna(False).astype(bool)
df['sell'] = (z_recovered.fillna(False) | time_exit).astype(bool)

output = {
    "name": "BTC Z-Rev 4H Long",
    "plots": [
        {"name": "z_score", "data": z.tolist(), "color": "#1890ff", "overlay": False},
        {"name": "ma20", "data": mean.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
    ]
}
