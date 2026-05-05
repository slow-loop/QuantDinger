# KOL: Range Fade (long-side) — 4H, NO stop loss + time-based exit
# Challenger to: kol_range_fade_4h_long.py (champion, with 2% stop loss)
#
# @hypothesis: champion has 67% win rate but payoff 0.48 → tight stops cut would-be
# winners on a mean-reversion thesis. Removing stop + adding 30-bar forced exit
# should let payoff ratio approach the event_tester's underlying +1.30%/30-bar reading,
# raising profit factor above 1.0 even at the cost of larger individual losses.
#
# ARCHIVED 2026-05-04: hypothesis falsified.
# Result: IS PF 0.85 (worse than champion's 0.97), payoff barely changed (0.48→0.49).
# Diagnosis: bottleneck is exit_range_pos > 0.5 (mid-range target = small profit),
# NOT the stop loss. Fix should target exit logic next, not risk control.
# See research/experiment_log.csv for full comparison.

# @strategy tradeDirection long
# @strategy entryPct 1.0
# (No stopLossPct — exits driven entirely by mid-range fill or 30-bar timeout)

# @param adx_threshold float 20.0
# @param entry_range_pos float 0.15
# @param exit_range_pos float 0.50
# @param max_hold_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 20.0))
entry_range_pos = float(params.get('entry_range_pos', 0.15))
exit_range_pos = float(params.get('exit_range_pos', 0.50))
max_hold_bars = int(params.get('max_hold_bars', 30))


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

# Time-based forced exit: N bars after each entry, mark forced sell.
time_forced_sell = raw_buy.shift(max_hold_bars).fillna(False)
combined_sell_signal = mid_range_exit.fillna(False) | time_forced_sell
raw_sell = combined_sell_signal & ~combined_sell_signal.shift(1).fillna(False)

df['buy'] = raw_buy.astype(bool)
df['sell'] = raw_sell.astype(bool)

output = {
    "name": "KOL Range Fade 4H Long (no stop, time exit)",
    "plots": [
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "range_pos", "data": range_pos.fillna(0.5).tolist(), "color": "#FFD700", "overlay": False},
    ]
}
