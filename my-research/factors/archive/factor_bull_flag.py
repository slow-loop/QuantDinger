"""
Factor:     bull_flag
Hypothesis: A bull flag forms when a sharp impulse (flagpole: 5D return > 10%) is followed by
            tight consolidation (next 5D return < 3%, ADX < 20 = low momentum), then a range
            breakout (close > 3-bar high). The pattern identifies institutional accumulation after
            a momentum surge — the breakout bar is the high-probability long entry.
            Score fires 0.7 on the breakout bar, 0.0 otherwise.
Source:     cap_003_bull_flag. IC=+0.70 in crypto-kol-quant.
            Faithful port of capabilities/patterns.py:cap_003 logic.
Status:     archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Flagpole: 5D ret 5 bars ago > 10%. Consolidation: |5D ret| < 3% +
                    ADX < 20. Breakout: close > 3-bar high shifted 1. Score 0.7 on trigger.
                    Source: cap_003 from crypto-kol-quant (IC 0.70).
  2026-05-06  run   BTC 1D: 0 triggers. BTC 4H: 0 triggers. ETH 1D: n=3 IS, 0 OOS, negative returns.
  2026-05-06  note  ARCHIVED. ADX < 20 post-10%-impulse structurally impossible on majors — ADX lags
                    and stays elevated after strong moves. Triple conjunction never fires. IC 0.70 is a
                    cross-sectional altcoin score. Pattern does not work on BTC/ETH.
"""

# @param flagpole_bars int 5
# @param flagpole_threshold float 0.10
# @param consolidation_threshold float 0.03
# @param adx_max float 20.0
# @param breakout_bars int 3
# @param adx_period int 14

import pandas as pd
import numpy as np

df = df.copy()

flagpole_bars = int(params.get('flagpole_bars', 5))
flagpole_threshold = float(params.get('flagpole_threshold', 0.10))
consolidation_threshold = float(params.get('consolidation_threshold', 0.03))
adx_max = float(params.get('adx_max', 20.0))
breakout_bars = int(params.get('breakout_bars', 3))
adx_period = int(params.get('adx_period', 14))

# 5D return (rolling)
ret_5d = df['close'].pct_change(flagpole_bars)

# Flagpole: strong prior move (5D return 5 bars ago > threshold)
flagpole = ret_5d.shift(flagpole_bars) > flagpole_threshold

# Consolidation: tight range AND weak trend
consolidation_ret = ret_5d.abs() < consolidation_threshold

# ADX (Wilder's)
high = df['high']
low = df['low']
close = df['close']
prev_close = close.shift(1)
tr = pd.concat([
    high - low,
    (high - prev_close).abs(),
    (low - prev_close).abs()
], axis=1).max(axis=1)
plus_dm = (high - high.shift(1)).clip(lower=0)
minus_dm = (low.shift(1) - low).clip(lower=0)
plus_dm = plus_dm.where(plus_dm > minus_dm, 0.0)
minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)
atr = tr.ewm(alpha=1 / adx_period, adjust=False).mean()
plus_di = 100 * plus_dm.ewm(alpha=1 / adx_period, adjust=False).mean() / atr.replace(0, np.nan)
minus_di = 100 * minus_dm.ewm(alpha=1 / adx_period, adjust=False).mean() / atr.replace(0, np.nan)
dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
adx = dx.ewm(alpha=1 / adx_period, adjust=False).mean()

low_momentum = adx < adx_max
consolidation = consolidation_ret & low_momentum

# Breakout: close > recent high (3-bar, shifted 1 to avoid lookahead)
recent_high = df['close'].rolling(window=breakout_bars, min_periods=1).max().shift(1)
breakout = df['close'] > recent_high

# Trigger: flagpole + consolidation (1 bar ago) + breakout now
trig = flagpole & consolidation.shift(1).fillna(False) & breakout

df['bull_flag_score'] = np.where(trig, 0.7, 0.0)

output = {
    "name": "Factor Bull Flag",
    "plots": [
        {"name": "recent_high", "data": recent_high.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "ret_5d", "data": ret_5d.fillna(0).tolist(), "color": "#FFD700", "overlay": False},
        {"name": "adx", "data": adx.fillna(0).tolist(), "color": "#FF9800", "overlay": False},
        {"name": "bull_flag_score", "data": df['bull_flag_score'].tolist(), "color": "#00BCD4", "overlay": False},
    ]
}
