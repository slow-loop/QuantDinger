# KOL: Range Fade (long-side only) — 4H
# Source factor: cap_013 range_fade on 4H bars
# Discovery from TF panel: on 4H, long-side IS hit 60.6% (n=269), avg fwd +1.30%.
# 1D was 48.5% on n=33 — 4H is the right TF for this thesis (real ranges form here).
# Short side was coin-flip (49.4%), skip it.

# Range-fade is a mean-reversion bet — natural target is +2-3% (range mid). A 5% stop
# means asymmetric R:R (loss > win) which kills expectancy after commission. Tightened
# stop to 2% to keep trades 1:1+ R:R given small win sizes.
# @strategy stopLossPct 0.02
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param adx_threshold float 20.0
# @param entry_range_pos float 0.15
# @param exit_range_pos float 0.50

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 20.0))
entry_range_pos = float(params.get('entry_range_pos', 0.15))
exit_range_pos = float(params.get('exit_range_pos', 0.50))


def _adx(high, low, close, period=14):
    up = high.diff()
    dn = -low.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=high.index)
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0)


adx14 = _adx(df['high'], df['low'], df['close'], period=14)
high_20 = df['high'].rolling(window=20, min_periods=10).max()
low_20 = df['low'].rolling(window=20, min_periods=10).min()
range_pos = ((df['close'] - low_20) / (high_20 - low_20).replace(0, np.nan)).clip(0, 1)

in_range = adx14 < adx_threshold
long_entry = in_range & (range_pos < entry_range_pos)
mid_range_exit = range_pos > exit_range_pos

raw_buy = long_entry.fillna(False) & ~long_entry.shift(1).fillna(False)
raw_sell = mid_range_exit.fillna(False) & ~mid_range_exit.shift(1).fillna(False)

df['buy'] = raw_buy.astype(bool)
df['sell'] = raw_sell.astype(bool)

output = {
    "name": "KOL Range Fade 4H Long",
    "plots": [
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "range_pos", "data": range_pos.fillna(0.5).tolist(), "color": "#FFD700", "overlay": False},
    ]
}
