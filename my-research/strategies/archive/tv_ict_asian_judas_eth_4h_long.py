"""
Strategy: tv_ict_asian_judas_eth_4h_long
Thesis:   ICT Asian Range + Judas Swing — the Asian session (00:00-08:00 UTC) sets a
          low-volatility accumulation range. During the London session start [08:00 UTC bar],
          price makes a FALSE breakout below the Asian low (the "Judas Swing" / manipulation
          leg), triggering retail stop-losses and breakout shorts. The manipulation leg
          is engineered to fill institutional buy orders at retail stop levels.
          When London bar sweeps Asian low but CLOSES BACK ABOVE it, the first NY bar
          (12:00 UTC) is the entry — price is now in distribution/expansion phase upward.
          Uses df['time'] column (datetime64) for UTC session structure of 4H bars.
Source:   ICT Inner Circle Trader Asian Range strategy:
          https://tradingfinder.com/education/forex/ict-asian-range-trading-strategy/
          ICT Power of 3 (AMD = Accumulate, Manipulate, Distribute):
          https://fxopen.com/blog/en/what-is-ict-po3-and-how-do-traders-use-it/
          quantifiedstrategies.com London breakout backtest (regime-filtered version)
          Scouted 2026-05-15 (non-orthodox strategy matrix, session-based strategies).
Status:   archived

History (append-only, newest at bottom):
  2026-05-15  code  init. Session structure (UTC 4H bars):
                    Asian range: bars at 00:00, 04:00 UTC per day → daily high/low.
                    Judas Swing long: 08:00 bar LOW sweeps below Asian low, CLOSES above it.
                    Compression filter: Asian range width < compression_mult × ATR14 (ensures
                    the manipulation is meaningful relative to volatility).
                    Entry: 12:00 UTC bar (first NY session bar) on a Judas Down day.
                    Exit: 15-bar timeout. Stop: 5% platform.
                    Volume gate: volume > vol_mult × SMA20 on London bar.
                    Uses df['time'] column for UTC session hour extraction (RangeIndex env).
  2026-05-15  run   ETH/USDT 4H IS: Sharpe +1.832, Sortino +0.555, Calmar +8.018, IR +0.241,
                    PF 1.606, Win% 58.8%, payoff 1.124, n=17. FAIL (Sortino miss, IR miss, n small).
                    ETH/USDT 4H OOS: 0 trades. FAIL.
                    (log: 2026-05-15)
  2026-05-15  note  Archive. IS produces 17 signals (Sharpe +1.832, PF 1.606) but Sortino
                    misses badly (+0.555 vs 1.5 threshold) and n=17 is too small.
                    OOS: 0 trades — compression filter too strict in bear-regime volatility,
                    or London Judas Down pattern (fake sweep + recovery) simply doesn't occur
                    in 2025-2026 downtrend (real breakdowns, not stop-hunts).
                    Key bug found: framework uses RangeIndex, not DatetimeIndex — session
                    partitioning requires df['time'].dt.hour, not df.index.hour.
                    Mechanism is conceptually sound but needs looser compression threshold or
                    separate OOS validation period with a neutral regime.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param compression_mult float 1.2
# @param vol_mult float 1.3
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

compression_mult = float(params.get('compression_mult', 1.2))
vol_mult         = float(params.get('vol_mult', 1.3))
timeout_bars     = int(params.get('timeout_bars', 15))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Session partitioning via df['time'] column ---
ts = pd.to_datetime(df['time'])
df['_hour']     = ts.dt.hour
df['_date_key'] = ts.dt.date

# Asian session bars: 00:00 and 04:00 UTC
asian_mask     = df['_hour'].isin([0, 4])
asian_high_day = df.loc[asian_mask].groupby('_date_key')['high'].max()
asian_low_day  = df.loc[asian_mask].groupby('_date_key')['low'].min()

# Map back to all bars (same day)
df['asian_high'] = df['_date_key'].map(asian_high_day)
df['asian_low']  = df['_date_key'].map(asian_low_day)
df['asian_rng']  = df['asian_high'] - df['asian_low']

# --- Compression filter: Asian range < compression_mult × ATR ---
compression_ok = df['asian_rng'] < atr * compression_mult

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- Judas Down on London bar (08:00 UTC) ---
is_london_bar = df['_hour'] == 8
judas_down = (
    is_london_bar
    & (df['low'] < df['asian_low'])        # sweeps Asian low
    & (df['close'] > df['asian_low'])      # closes back above Asian low
    & compression_ok                        # Asian range was compressed
    & vol_ok                                # volume confirms stop-out
)

# --- Entry: first NY bar (12:00 UTC) on a Judas Down day ---
is_first_ny = df['_hour'] == 12

# shift(1): the bar immediately before 12:00 is the London 08:00 bar on same day
df['buy'] = (is_first_ny & judas_down.shift(1)).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Cleanup temp columns
df.drop(columns=['_hour', '_date_key'], inplace=True)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "ICT Asian Range Judas Swing ETH 4H Long",
    "plots": [
        {"name": "asian_high", "data": df['asian_high'].fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "asian_low",  "data": df['asian_low'].fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "ATR",        "data": atr.fillna(0).tolist(),              "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20",  "data": vol_sma.fillna(0).tolist(),          "color": "#9E9E9E", "overlay": False},
    ]
}
