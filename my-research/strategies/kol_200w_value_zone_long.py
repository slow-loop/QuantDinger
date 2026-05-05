# KOL: 200-Week Value Zone Long
# Source: emg_029_200w_value_zone (LedgerStatus) — IC=+0.178 in crypto-kol-quant
# Hypothesis: BTC price within +/-8% of 200-week MA = long-term value buy zone.

# @strategy stopLossPct 0.15
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param zone_pct float 0.08
# @param exit_above_pct float 0.25

import pandas as pd
import numpy as np

df = df.copy()

zone_pct = float(params.get('zone_pct', 0.08))
exit_above_pct = float(params.get('exit_above_pct', 0.25))

# 200 weeks on daily timeframe = 1400 daily bars.
# min_periods=200 matches crypto-kol-quant feature_engine.py:33 (allows partial-window early values).
ma_200w = df['close'].rolling(window=1400, min_periods=200).mean()
pct_from_ma = (df['close'] - ma_200w) / ma_200w

in_zone = (pct_from_ma.abs() < zone_pct) & ma_200w.notna()
exit_signal = (pct_from_ma > exit_above_pct) & ma_200w.notna()

raw_buy = in_zone & ~in_zone.shift(1).fillna(False)
raw_sell = exit_signal & ~exit_signal.shift(1).fillna(False)

df['buy'] = raw_buy.fillna(False).astype(bool)
df['sell'] = raw_sell.fillna(False).astype(bool)

output = {
    "name": "KOL 200W Value Zone Long",
    "plots": [
        {"name": "MA200W", "data": ma_200w.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "MA200W +8%", "data": (ma_200w * (1 + zone_pct)).fillna(0).tolist(), "color": "#CE93D8", "overlay": True},
        {"name": "MA200W -8%", "data": (ma_200w * (1 - zone_pct)).fillna(0).tolist(), "color": "#CE93D8", "overlay": True},
    ]
}
