# KOL: OHLC Weekly Anchor — 4H Long, hysteresis entry/exit + time-based forced exit
# Challenger to: kol_ohlc_anchor_4h_long.py
#   Champion: entry 0.1, exit 0.0, 5% stop loss → 122 trades, PF 0.95, win 46% (eaten by whipsaw + cost)
#
# @hypothesis: 122 trades on a continuous-score factor = whipsaw. Solution:
#   1. Hysteresis — enter at stronger threshold (0.15 = price ~8% above weekly open),
#      exit only on much weaker (0.05 = drops back to ~2.5%). Filters weak signals.
#   2. Remove stop — fixed 5% stop fired on intra-week dips that would have recovered.
#   3. Time exit at 30 bars — caps holding period at 5 days (matches event_tester window).
# Expected: fewer trades, larger avg win, higher PF.

# @strategy tradeDirection long
# @strategy entryPct 1.0
# (No stopLossPct — exits via score crossing exit threshold or 30-bar timeout)

# @param entry_threshold float 0.15
# @param exit_threshold float 0.05
# @param max_hold_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

entry_threshold = float(params.get('entry_threshold', 0.15))
exit_threshold = float(params.get('exit_threshold', 0.05))
max_hold_bars = int(params.get('max_hold_bars', 30))

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

# Hysteresis: enter on stronger signal, exit only on much weaker
above_entry = score > entry_threshold
below_exit = score < exit_threshold

raw_buy = above_entry & ~above_entry.shift(1).fillna(False)
natural_sell = below_exit & ~below_exit.shift(1).fillna(False)

# Time-based forced exit: 30 bars after each entry
time_forced_sell = raw_buy.shift(max_hold_bars).fillna(False)

# OR — engine treats "sell while flat" as no-op
raw_sell = (natural_sell.fillna(False) | time_forced_sell).astype(bool)
df['buy'] = raw_buy.fillna(False).astype(bool)
df['sell'] = raw_sell

output = {
    "name": "KOL OHLC Anchor 4H Long (hysteresis + time exit)",
    "plots": [
        {"name": "WeeklyOpen", "data": week_open.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
        {"name": "anchor_score", "data": score.tolist(), "color": "#FFD700", "overlay": False},
    ]
}
