"""
Strategy: tv_pwl_sweep_eth_4h_long
Thesis:   Previous Week Low (PWL) liquidity sweep — institutional algorithms target
          stop-loss clusters resting below prior-week lows. When price sweeps below
          the PWL then closes back inside the prior week's range, the stop-run is
          complete and the reversal is imminent. PWL levels carry more weight than
          daily lows because orders accumulate over a full 5-day session.
          This is a weekly-fractal version of the SFP mechanism.
Source:   ICT PWH/PWL key levels framework:
          https://tradingfinder.com/education/forex/pwh-pwl/
          GhostTraders PDH/PDL/PWH/PWL institutional levels
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-15  code  init. Weekly level computation:
                    - Primary: datetime-index resample('W') for true weekly OHLC.
                    - Fallback: rolling 42 bars (7d × 6 bars/day on 4H) approximation.
                    PWL sweep long: 4H bar low < prev_week_low AND close > prev_week_low.
                    Volume gate: volume > vol_mult × SMA20.
                    Bullish close confirmation: close > open.
                    Exit: 20-bar timeout. Stop: 5% platform.
  2026-05-15  run   ETH/USDT 4H IS: Sharpe -1.020, Sortino -0.525, PF 0.750, Win% 54.8%,
                    payoff 0.620, n=42. FAIL.
                    ETH/USDT 4H OOS: Sharpe +0.287, Sortino +0.149, PF 1.042, Win% 61.5%,
                    payoff 0.651, n=13. FAIL (metrics too weak).
                    Note: df.index confirmed DatetimeIndex → resample('W') path executed.
                    (log: 2026-05-15)
  2026-05-15  note  Archive. IS fails strongly (Sharpe -1.020). OOS is marginally positive
                    (Sharpe +0.287) but below all thresholds. Bearish regime in OOS means
                    weekly lows are hit regularly in downtrends — the mechanism fires on
                    real breakdowns (not stop-hunts) as often as genuine reversals. PWL
                    in a bear market is more likely a continuation signal than a reversal.
                    SFP with 10-bar lookback is a superior implementation of the same idea
                    (shorter lookback = more local/relevant swing low, better selectivity).
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param vol_mult float 1.5
# @param timeout_bars int 20
# @param fallback_bars int 42

import pandas as pd
import numpy as np

df = df.copy()

vol_mult      = float(params.get('vol_mult', 1.5))
timeout_bars  = int(params.get('timeout_bars', 20))
fallback_bars = int(params.get('fallback_bars', 42))

# --- Previous week low (with datetime-index detection) ---
try:
    if isinstance(df.index, pd.DatetimeIndex):
        weekly_low  = df['low'].resample('W').min()
        prev_wk_low = weekly_low.shift(1).reindex(df.index, method='ffill')
        weekly_high = df['high'].resample('W').max()
        prev_wk_high = weekly_high.shift(1).reindex(df.index, method='ffill')
    else:
        raise TypeError("non-datetime index")
except Exception:
    prev_wk_low  = df['low'].shift(1).rolling(fallback_bars).min()
    prev_wk_high = df['high'].shift(1).rolling(fallback_bars).max()

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- PWL sweep long: sweeps below prior week low, recovers above it ---
sweeps_pwl  = df['low'] < prev_wk_low
recovers    = df['close'] > prev_wk_low
bull_close  = df['close'] > df['open']

# --- Entry ---
df['buy'] = (sweeps_pwl & recovers & bull_close & vol_ok).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "PWL Weekly Level Sweep ETH 4H Long",
    "plots": [
        {"name": "prev_wk_low",  "data": prev_wk_low.fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "prev_wk_high", "data": prev_wk_high.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "vol_SMA20",    "data": vol_sma.fillna(0).tolist(),      "color": "#9E9E9E", "overlay": False},
    ]
}
