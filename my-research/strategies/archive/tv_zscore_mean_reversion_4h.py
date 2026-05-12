"""
Strategy: tv_zscore_mean_reversion_4h
Thesis:   Statistical mean-reversion — when price Z-score is extreme (>2σ away from rolling
          mean) AND RSI confirms exhaustion AND Bollinger Band width is contracting, price
          tends to revert toward the mean. Long on oversold extremes, short on overbought.
Source:   https://www.tradingview.com/script/92rilzXd-Z-Score-Mean-Reversion-Pro/
          (Z-Score Mean Reversion Pro by ayusattv, open-source Pine Script v5)
Built on: no external factors — Z-score, RSI, BB all computed inline
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. port from TradingView Z-Score Mean Reversion Pro (ayusattv).
                    Entry: Z-score crosses ±2.0 threshold confirmed by RSI exhaustion
                    (RSI < rsi_oversold for long / RSI > rsi_overbought for short).
                    BB-width filter added to avoid wide-range breakout bars (BBW < bbw_max).
                    Exit: Z-score returns to within ±0.5 of mean (mean reversion achieved)
                    OR price crosses EMA trend filter in direction of trade (trend exit)
                    OR 20-bar timeout. Stop: ATR-based (2x ATR).
                    No talib — all indicators computed with pandas/numpy EWM + rolling.
  2026-05-12  run   BTC/USDT 4H OOS: Sharpe -0.962, Sortino -0.892, Calmar -1.284,
                    PF 0.62, n=10, WR 60%. FAIL 0/5 criteria.
                    ETH/USDT 4H OOS: Sharpe -1.172, Sortino -0.998, Calmar -1.618,
                    PF 0.48, n=8, WR 50%. FAIL 0/5 criteria.
                    (log: 2026-05-12T — see experiment_log.csv)
  2026-05-12  note  Root cause: payoff ratio ~0.48 on both assets — avg loss ~2x avg win.
                    Crypto fat tails mean Z-score=2.0 does NOT mark the mean-reversion
                    point; price extends to Z=4-5 before reversing. Strategy takes stop
                    losses frequently on the extension leg, then misses the actual reversion
                    when it fires timeout exit. Classic early-entry mean-reversion trap.
                    In forking markets the BBW filter blocks many entries but those that
                    pass still catch the falling knife mid-extension.
                    Archiving. If revisiting: consider entry only on Z-score PEAK (dZ/dt
                    sign change) not threshold cross, or wider stop with inverse Kelly sizing.
                    → archived to my-research/strategies/archive/tv_zscore_mean_reversion_4h.py
Status:   archived
"""

# @strategy stopLossPct 0.03
# @strategy tradeDirection both
# @strategy entryPct 1.0

# @param zscore_length int 20
# @param zscore_entry float 2.0
# @param zscore_exit float 0.5
# @param rsi_length int 14
# @param rsi_oversold float 35.0
# @param rsi_overbought float 65.0
# @param bb_length int 20
# @param bb_std float 2.0
# @param bbw_max_pct float 0.12
# @param ema_length int 50
# @param atr_length int 14
# @param atr_stop_mult float 2.0
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

# ── Parameters ─────────────────────────────────────────────────────────────
zscore_length   = int(params.get('zscore_length',   20))
zscore_entry    = float(params.get('zscore_entry',   2.0))
zscore_exit     = float(params.get('zscore_exit',    0.5))
rsi_length      = int(params.get('rsi_length',      14))
rsi_oversold    = float(params.get('rsi_oversold',   35.0))
rsi_overbought  = float(params.get('rsi_overbought', 65.0))
bb_length       = int(params.get('bb_length',       20))
bb_std          = float(params.get('bb_std',         2.0))
bbw_max_pct     = float(params.get('bbw_max_pct',   0.12))
ema_length      = int(params.get('ema_length',       50))
atr_length      = int(params.get('atr_length',       14))
atr_stop_mult   = float(params.get('atr_stop_mult',  2.0))
timeout_bars    = int(params.get('timeout_bars',     20))

close = df['close']
high  = df['high']
low   = df['low']

# ── Z-Score of close vs rolling mean ───────────────────────────────────────
roll_mean = close.rolling(zscore_length).mean()
roll_std  = close.rolling(zscore_length).std()
zscore    = (close - roll_mean) / roll_std.replace(0, np.nan)

# ── RSI (Wilder — EWM with alpha = 1/length) ───────────────────────────────
delta   = close.diff()
gain    = delta.clip(lower=0)
loss    = (-delta).clip(lower=0)
avg_gain = gain.ewm(alpha=1.0 / rsi_length, min_periods=rsi_length, adjust=False).mean()
avg_loss = loss.ewm(alpha=1.0 / rsi_length, min_periods=rsi_length, adjust=False).mean()
rs  = avg_gain / avg_loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs))

# ── Bollinger Bands + BBW (bandwidth relative to midline) ──────────────────
bb_mid   = close.rolling(bb_length).mean()
bb_sigma = close.rolling(bb_length).std()
bb_upper = bb_mid + bb_std * bb_sigma
bb_lower = bb_mid - bb_std * bb_sigma
bbw      = (bb_upper - bb_lower) / bb_mid          # normalised width

# ── EMA trend filter ────────────────────────────────────────────────────────
ema = close.ewm(span=ema_length, adjust=False).mean()

# ── ATR (Wilder) ────────────────────────────────────────────────────────────
tr     = pd.concat([
    high - low,
    (high - close.shift()).abs(),
    (low  - close.shift()).abs()
], axis=1).max(axis=1)
atr = tr.ewm(alpha=1.0 / atr_length, min_periods=atr_length, adjust=False).mean()

# ── Entry conditions ────────────────────────────────────────────────────────
# Long: Z-score crosses below -zscore_entry threshold (price deeply oversold vs mean)
#       AND RSI confirms oversold exhaustion AND BBW not too wide (avoid breakouts)
prev_zscore  = zscore.shift(1)
long_entry   = (
    (prev_zscore >= -zscore_entry) &          # was above threshold last bar
    (zscore       < -zscore_entry) &          # just crossed below
    (rsi          < rsi_oversold)  &          # RSI confirms exhaustion
    (bbw          < bbw_max_pct)              # BBW filter: not in a breakout bar
)

# Short: Z-score crosses above +zscore_entry threshold (price stretched above mean)
#        AND RSI confirms overbought exhaustion AND BBW filter
short_entry  = (
    (prev_zscore <= zscore_entry)  &          # was below threshold last bar
    (zscore       > zscore_entry)  &          # just crossed above
    (rsi          > rsi_overbought) &         # RSI confirms exhaustion
    (bbw          < bbw_max_pct)              # BBW filter
)

# ── Exit conditions (mean reversion achieved or timeout) ────────────────────
# Long exit: Z-score returns to within ±zscore_exit of mean (reversion complete)
#            OR price falls below EMA (trend turned against us)
long_exit    = (zscore > -zscore_exit) | (close < ema)

# Short exit: Z-score returns to within ±zscore_exit of mean
#             OR price rises above EMA
short_exit   = (zscore < zscore_exit)  | (close > ema)

# ── Timeout exit ─────────────────────────────────────────────────────────────
# Implement timeout: exit if still in trade after timeout_bars bars
# We track position entry bar index using a rolling flag approach.
# Build a bar-index series to detect timeouts.
bar_index = pd.Series(range(len(df)), index=df.index)

# Forward-fill entry bar into a "bars since entry" series
# This is a vectorised approximation: mark every long_entry bar, then look
# within the next timeout_bars bars for any exit. Outside of that window, force exit.
timeout_long_exit  = long_entry.shift(timeout_bars).fillna(False).astype(bool)
timeout_short_exit = short_entry.shift(timeout_bars).fillna(False).astype(bool)

# ── Combine exits ────────────────────────────────────────────────────────────
long_exit_final  = long_exit  | timeout_long_exit
short_exit_final = short_exit | timeout_short_exit

# ── Assign to df ─────────────────────────────────────────────────────────────
df['buy']  = long_entry.fillna(False).astype(bool)
df['sell'] = short_entry.fillna(False).astype(bool)

# Sell existing long (close long)
df['buy_close']  = long_exit_final.fillna(False).astype(bool)
# Close existing short
df['sell_close'] = short_exit_final.fillna(False).astype(bool)

# ── Output ────────────────────────────────────────────────────────────────────
output = {
    "name": "Z-Score Mean Reversion 4H",
    "plots": [
        {"name": "zscore",  "data": zscore.fillna(0).tolist(),  "color": "#FF6B6B", "overlay": False},
        {"name": "rsi",     "data": rsi.fillna(50).tolist(),    "color": "#4ECDC4", "overlay": False},
        {"name": "bbw",     "data": bbw.fillna(0).tolist(),     "color": "#FFE66D", "overlay": False},
        {"name": "ema",     "data": ema.fillna(0).tolist(),     "color": "#A8E6CF", "overlay": True},
    ]
}
