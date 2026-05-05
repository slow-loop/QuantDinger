"""
Strategy: btc_regime_short_1d
Thesis:   Enter short at the START of each confirmed downtrend episode (price < MA200,
          MA50 < MA200, ADX > 25), exit when regime dissolves. Event tester showed
          OOS 30d hit 53%, avg -3.53% (profit for short), n=100 daily bars (2025-26).
          IS was weaker (36% hit) due to violent 2022 bear bounces — trading episodes
          rather than individual bars should reduce bounce exposure.
Built on: factors/factor_regime_trending_down.py (inlined)
Status:   archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Enter SHORT at first bar of each regime episode (regime turns on).
                    Exit when regime ends (any condition flips) OR 30-bar time stop.
                    No fixed stop loss — regime provides the structural filter.
  2026-05-06  run   BTC/USDT 1D — IS: Sharpe +0.274 n=83 PF 1.10 win 56.6% payoff 0.84.
                    OOS: Sharpe -1.236 n=55 PF 0.53 win 41.8%. ❌ OOS failure.
                    (log: 2026-05-06)
  2026-05-06  note  ABANDONED. Root cause: ADX oscillates around 25, generating frequent
                    episode_start triggers (OOS 55 trades/year = 4-5 per month). Each "episode
                    start" enters short after a recent drop — high bounce risk. IS decent because
                    2022 bear was more sustained. OOS choppy. The regime concept is valid but
                    episode_start timing is the wrong entry. A persistence filter (require regime
                    active ≥ 5 days before counting as true episode start) could be explored, but
                    the underlying short-side structural edge may not be strong enough for crypto.
"""

# @strategy tradeDirection short
# @strategy entryPct 1.0

# @param adx_threshold float 25.0
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 25.0))
timeout_bars = int(params.get('timeout_bars', 30))


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


ma50 = df['close'].rolling(window=50, min_periods=20).mean()
ma200 = df['close'].rolling(window=200, min_periods=50).mean()
adx14 = _adx(df['high'], df['low'], df['close'], period=14)

regime_on = (df['close'] < ma200) & (ma50 < ma200) & (adx14 > adx_threshold)

# Enter only at the FIRST bar of each episode (regime turns from off to on)
episode_start = regime_on.fillna(False) & ~regime_on.shift(1).fillna(False)

# Exit when regime ends (any condition flips) or time stop
regime_off = ~regime_on.fillna(False) & regime_on.shift(1).fillna(False)
time_exit = episode_start.shift(timeout_bars).fillna(False)

# For short strategy: buy = enter short, sell = cover
df['buy'] = episode_start.astype(bool)
df['sell'] = (regime_off.fillna(False) | time_exit).astype(bool)

output = {
    "name": "BTC Regime Short 1D",
    "plots": [
        {"name": "MA200", "data": ma200.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "MA50", "data": ma50.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "regime_on", "data": regime_on.astype(float).tolist(), "color": "#FF1744", "overlay": False},
    ]
}
