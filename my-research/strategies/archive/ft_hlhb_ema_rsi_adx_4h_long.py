"""
Strategy: ft_hlhb_ema_rsi_adx_4h_long
Thesis:   HLHB system adapted for crypto 4H — enter long when EMA5 crosses above EMA10
          AND RSI(10, HL2) crosses above 50 AND ADX > 25. The triple confirmation
          (trend direction, momentum, trend strength) squeezes out low-conviction signals
          and targets established short-term trends. Exit on reverse crossover.
Built on: (inline indicators — no external factor dependency)
Source:   https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/hlhb.py
          Original concept: https://www.babypips.com/trading/forex-hlhb-system-explained
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. Port from freqtrade/hlhb.py. EMA5/EMA10 crossover + RSI(10,HL2) > 50
                    + ADX > 25. Exit: EMA5 crosses below EMA10 AND RSI < 50. Stop 4%.
                    Timeout 40 bars (10 days). Long only. BTC/USDT 4H.
  2026-05-12  run   BTC/USDT 4H IS: Sharpe +2.005, Sortino +2.132, Calmar +11.08, PF 1.32, n=62.
                    OOS: Sharpe -2.184, Sortino -1.237, Calmar -2.170, IR -0.299, PF 0.51, n=15. ❌
                    (log: 2026-05-12)
  2026-05-12  note  ARCHIVED. Severe IS/OOS mismatch. IS (2020-2025 bull cycle) misleading —
                    strategy learned crypto uptrend regime. OOS (2025-2026 choppy/bear) collapses:
                    Sharpe -2.18, PF 0.51, win rate 33%. The simultaneous EMA+RSI dual-crossover
                    requirement makes entries too sparse (n=15 OOS) and too late into moves.
                    The original forex HLHB system does not translate to crypto 4H OOS regime.
"""

# @strategy tradeDirection long
# @strategy stopLossPct 0.04
# @strategy entryPct 1.0

# @param ema_fast int 5
# @param ema_slow int 10
# @param rsi_period int 10
# @param adx_period int 14
# @param adx_threshold float 25.0
# @param timeout_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

ema_fast = int(params.get('ema_fast', 5))
ema_slow = int(params.get('ema_slow', 10))
rsi_period = int(params.get('rsi_period', 10))
adx_period = int(params.get('adx_period', 14))
adx_threshold = float(params.get('adx_threshold', 25.0))
timeout_bars = int(params.get('timeout_bars', 40))

# HL2 price for RSI (matches HLHB original)
hl2 = (df['high'] + df['low']) / 2

# EMA indicators
ema_f = hl2.ewm(span=ema_fast, adjust=False).mean()
ema_s = hl2.ewm(span=ema_slow, adjust=False).mean()

# RSI on HL2
delta = hl2.diff()
gain = delta.clip(lower=0)
loss = (-delta).clip(lower=0)
avg_gain = gain.ewm(alpha=1.0 / rsi_period, adjust=False).mean()
avg_loss = loss.ewm(alpha=1.0 / rsi_period, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
rsi = (100 - 100 / (1 + rs)).fillna(50)

# ADX
high_s = df['high']
low_s = df['low']
close_s = df['close']
prev_close = close_s.shift(1)

tr = pd.concat([
    high_s - low_s,
    (high_s - prev_close).abs(),
    (low_s - prev_close).abs()
], axis=1).max(axis=1)

dm_plus = (high_s - high_s.shift(1)).clip(lower=0)
dm_minus = (low_s.shift(1) - low_s).clip(lower=0)
# DM+ only valid when DM+ > DM-
dm_plus = dm_plus.where(dm_plus > dm_minus, 0.0)
dm_minus = dm_minus.where(dm_minus > dm_plus.where(dm_plus > dm_minus, 0.0), 0.0)
# re-zero when tied
tie = (high_s - high_s.shift(1)) == (low_s.shift(1) - low_s)
dm_plus = dm_plus.where(~tie, 0.0)
dm_minus = dm_minus.where(~tie, 0.0)

atr = tr.ewm(alpha=1.0 / adx_period, adjust=False).mean()
di_plus = 100 * (dm_plus.ewm(alpha=1.0 / adx_period, adjust=False).mean() / atr.replace(0, np.nan))
di_minus = 100 * (dm_minus.ewm(alpha=1.0 / adx_period, adjust=False).mean() / atr.replace(0, np.nan))
dx = (100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, np.nan)).fillna(0)
adx = dx.ewm(alpha=1.0 / adx_period, adjust=False).mean()

# Crossover helpers
ema_cross_up = (ema_f > ema_s) & (ema_f.shift(1) <= ema_s.shift(1))
ema_cross_dn = (ema_f < ema_s) & (ema_f.shift(1) >= ema_s.shift(1))
rsi_cross_up = (rsi > 50) & (rsi.shift(1) <= 50)
rsi_cross_dn = (rsi < 50) & (rsi.shift(1) >= 50)

# Entry: EMA crossover up AND RSI crosses above 50 on same bar AND ADX > threshold
entry = ema_cross_up & rsi_cross_up & (adx > adx_threshold)

# Exit: EMA crosses down AND RSI crosses below 50 (dual confirmation exit)
cross_exit = ema_cross_dn & rsi_cross_dn

# Timeout exit
time_exit = entry.shift(timeout_bars).fillna(False)

df['buy'] = entry.fillna(False).astype(bool)
df['sell'] = (cross_exit.fillna(False) | time_exit).astype(bool)

output = {
    "name": "HLHB EMA/RSI/ADX 4H Long",
    "plots": [
        {"name": "ema_fast", "data": ema_f.fillna(0).tolist(), "color": "#26C6DA", "overlay": True},
        {"name": "ema_slow", "data": ema_s.fillna(0).tolist(), "color": "#FF7043", "overlay": True},
        {"name": "rsi", "data": rsi.fillna(50).tolist(), "color": "#AB47BC", "overlay": False},
        {"name": "adx", "data": adx.fillna(0).tolist(), "color": "#66BB6A", "overlay": False},
    ]
}
