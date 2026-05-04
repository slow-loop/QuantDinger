# KOL: OHLC Weekly Anchor — 4H Long
# Source factor: emg_027 ohlc_anchor on 4H bars
# Discovery from TF panel: on 4H, OOS IC30=+0.086 (p=0.0001) — strongest OOS signal in
# the entire 8-factor × 3-TF matrix. crypto-kol-quant tested only 1D and missed this.
# IS event hit-rate (long, |score|>0.1, 30-bar fwd): 57.7% on n=1995 triggers.
#
# ARCHIVED 2026-05-04: superseded by kol_ohlc_anchor_4h_long_hysteresis.py.
# Champion failed (IS PF 0.95 / IR -0.02; OOS PF 0.41 / IR -2.68) — too many whipsaw
# trades on a continuous-score factor. Hysteresis variant beat it on every metric.
# See research/experiment_log.csv for full comparison.

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param entry_threshold float 0.1
# @param exit_threshold float 0.0

import pandas as pd
import numpy as np

df = df.copy()

entry_threshold = float(params.get('entry_threshold', 0.1))
exit_threshold = float(params.get('exit_threshold', 0.0))

# Inline replication of factor_ohlc_anchor.
# Sandbox provides df['time'] (datetime64); IC tester provides DatetimeIndex.
if 'time' in df.columns:
    day_of_week = pd.to_datetime(df['time']).dt.dayofweek.values
else:
    day_of_week = df.index.dayofweek
day_of_week = pd.Series(day_of_week, index=df.index)
week_open = df['open'].where(day_of_week == 0).ffill()
pct_diff = (df['close'] - week_open) / week_open
score = (np.tanh(pct_diff * 5) * 0.4).fillna(0.0)

above_thresh = score > entry_threshold
below_exit = score < exit_threshold

raw_buy = above_thresh & ~above_thresh.shift(1).fillna(False)
raw_sell = below_exit & ~below_exit.shift(1).fillna(False)

df['buy'] = raw_buy.fillna(False).astype(bool)
df['sell'] = raw_sell.fillna(False).astype(bool)

output = {
    "name": "KOL OHLC Anchor 4H Long",
    "plots": [
        {"name": "WeeklyOpen", "data": week_open.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
        {"name": "anchor_score", "data": score.tolist(), "color": "#FFD700", "overlay": False},
    ]
}
