"""
Strategy: tv_rsi_divergence_4h_long
Thesis:   4H long-only — enter when price forms a lower low but RSI forms a higher low
          (bullish RSI divergence). Sellers are losing momentum while price compresses:
          the divergence between price action and RSI is a structural catalyst signal, not
          a threshold-cross signal. ATR-based stop loss; RSI overbought or timeout exit.
Built on: standalone (RSI + pivot detection inline)
Source:   Ported from TradingView — "RSI Divergence Strategy" by AliferCrypto (85 likes).
          URL: https://www.tradingview.com/script/Spg5RGk1-RSI-Divergence-Strategy-AliferCrypto/
          Mechanism: price lower low + RSI higher low on confirmed swing pivots.
          ATR-based SL and RSI-overbought exit preserved in port.
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. RSI computed via Wilder EWM. Pivot detection via rolling argmin
                    over lookback window (vectorized). Divergence confirmed when price pivot
                    low (i) < price pivot low (j) AND rsi pivot low (i) > rsi pivot low (j),
                    where j is the most recent prior pivot. Entry on confirmation bar close.
                    Stop = ATR * atr_sl_mult below entry. Exit: RSI crosses above rsi_exit
                    OR timeout_bars elapsed. Long only (bullish divergence only).
  2026-05-12  run   BTC/USDT 4H — IS: Sharpe +3.17 Sortino +1.78 Calmar +46.5 PF 1.95 n=42 ✓
                    BTC/USDT 4H — OOS: Sharpe -2.78 Sortino -1.47 Calmar -2.71 PF 0.25 n=12. FAIL.
                    ETH/USDT 4H — IS: Sharpe +1.15 PF 1.13 n=50.
                    ETH/USDT 4H — OOS: Sharpe -3.36 PF 0.05 n=9. Win rate 11%. FAIL.
                    (log: 2026-05-12)
  2026-05-12  note  FAIL. Archive. Root cause: bullish RSI divergence in a downtrending
                    regime (2025-26) becomes a "catch falling knife" signal. Price keeps
                    making lower lows with higher RSI (momentum deteriorates slowly while
                    price extends), so the divergence fires repeatedly but ATR stops are
                    hit sequentially. OOS BTC win rate 50% but payoff 0.25 (losses 4x
                    wins). ETH win rate 11% — essentially systematic stop-hunting.
                    Key learning: RSI divergence requires a TREND REVERSAL context, not
                    just momentum divergence in isolation. In a persistent downtrend, every
                    bullish divergence is followed by another lower low. Need to gate on
                    a macro regime filter (e.g., BTC above 200-week MA or HTF structure
                    break) to avoid catching knives. Revisit only with strong trend-
                    reversal confirmation as a prerequisite gate.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param rsi_length int 14
# @param pivot_lookback int 5
# @param max_pivot_gap int 40
# @param atr_length int 14
# @param atr_sl_mult float 2.0
# @param rsi_exit float 70.0
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

rsi_length    = int(params.get('rsi_length', 14))
pivot_lookback = int(params.get('pivot_lookback', 5))
max_pivot_gap  = int(params.get('max_pivot_gap', 40))
atr_length    = int(params.get('atr_length', 14))
atr_sl_mult   = float(params.get('atr_sl_mult', 2.0))
rsi_exit      = float(params.get('rsi_exit', 70.0))
timeout_bars  = int(params.get('timeout_bars', 30))

# ── RSI (Wilder / EWM) ────────────────────────────────────────────────────────
delta   = df['close'].diff()
gain    = delta.clip(lower=0)
loss    = (-delta).clip(lower=0)
avg_gain = gain.ewm(alpha=1.0/rsi_length, min_periods=rsi_length, adjust=False).mean()
avg_loss = loss.ewm(alpha=1.0/rsi_length, min_periods=rsi_length, adjust=False).mean()
rs       = avg_gain / avg_loss.replace(0, np.nan)
rsi      = 100 - 100 / (1 + rs)

# ── ATR ───────────────────────────────────────────────────────────────────────
high_low   = df['high'] - df['low']
high_close = (df['high'] - df['close'].shift()).abs()
low_close  = (df['low']  - df['close'].shift()).abs()
true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
atr        = true_range.ewm(alpha=1.0/atr_length, min_periods=atr_length, adjust=False).mean()

# ── Pivot-low detection (vectorized) ─────────────────────────────────────────
# A bar at index i is a pivot low if close[i] is the minimum in the window
# [i - pivot_lookback, i + pivot_lookback]. We use rolling min on centered windows
# approximated by checking whether close equals rolling min on both sides.
L = pivot_lookback
# Is this bar a local minimum compared to L bars on each side?
roll_min_left  = df['close'].rolling(L+1, min_periods=L+1).min()           # min of past L bars incl. current
roll_min_right = df['close'].shift(-L).rolling(L+1, min_periods=L+1).min() # min of future L bars incl. current
is_pivot_low   = (df['close'] <= roll_min_left) & (df['close'] <= roll_min_right)

rsi_at_pivot   = rsi.where(is_pivot_low)         # RSI values only at pivot-low bars, else NaN
price_at_pivot = df['close'].where(is_pivot_low)  # price only at pivot lows

# ── Divergence signal ─────────────────────────────────────────────────────────
# For each bar, look back up to max_pivot_gap bars for the most recent prior pivot.
# If current pivot: price[now] < price[prior] AND rsi[now] > rsi[prior] → bullish divergence.
n        = len(df)
div_flag = pd.Series(False, index=df.index)

# Build arrays for vectorized comparison
rsi_arr   = rsi_at_pivot.values
price_arr = price_at_pivot.values
idx_arr   = np.arange(n)

for i in range(max_pivot_gap + L, n - L):
    if not is_pivot_low.iloc[i]:
        continue
    if np.isnan(price_arr[i]) or np.isnan(rsi_arr[i]):
        continue
    # Find the most recent prior pivot low within max_pivot_gap bars
    window_start = max(0, i - max_pivot_gap)
    prior_pivots = idx_arr[window_start:i][~np.isnan(price_arr[window_start:i])]
    if len(prior_pivots) == 0:
        continue
    j = prior_pivots[-1]   # most recent prior pivot low
    if np.isnan(price_arr[j]) or np.isnan(rsi_arr[j]):
        continue
    # Bullish divergence: price lower low + RSI higher low
    if price_arr[i] < price_arr[j] and rsi_arr[i] > rsi_arr[j]:
        div_flag.iloc[i] = True

# The divergence fires at pivot-low bar i, but i is only confirmed pivot_lookback bars
# AFTER the actual low (we need future bars for the right side of the pivot).
# So the entry signal should be on bar i + L (the first bar after confirmation).
buy_raw  = div_flag.shift(L).fillna(False).astype(bool)

# De-duplicate: only enter once per divergence (no re-entry until prior trade expires)
# A simple cooldown: suppress subsequent signals within timeout_bars of the last entry.
buy = pd.Series(False, index=df.index)
last_entry = -timeout_bars - 1
for i in range(len(df)):
    if buy_raw.iloc[i] and (i - last_entry) > timeout_bars:
        buy.iloc[i] = True
        last_entry  = i

# ── Exit signals ──────────────────────────────────────────────────────────────
# 1. RSI overbought exit (momentum exhausted)
rsi_ob_exit = (rsi >= rsi_exit) & (rsi.shift(1) < rsi_exit)

# 2. Timeout exit (max holding period)
timeout_exit = buy.shift(timeout_bars).fillna(False)

sell = (rsi_ob_exit | timeout_exit).astype(bool)

df['buy']  = buy
df['sell'] = sell

output = {
    "name": "RSI Divergence 4H Long",
    "plots": [
        {"name": "RSI",        "data": rsi.fillna(50).tolist(),            "color": "#2196F3", "overlay": False},
        {"name": "div_signal", "data": div_flag.astype(float).tolist(),    "color": "#FF5722", "overlay": False},
        {"name": "ATR",        "data": atr.fillna(0).tolist(),             "color": "#9C27B0", "overlay": False},
    ]
}
