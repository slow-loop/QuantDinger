"""
Strategy: tv_stochrsi_support_bounce_4h_long
Thesis:   Stochastic RSI crosses up from deep oversold (<20) while price is near
          a significant structural low (within proximity_pct of the rolling 60-bar low).
          The structural low proximity acts as the catalyst (demand zone), while Stoch RSI
          exhaustion confirms momentum reversal. This avoids the pure-oscillator knife-catch
          by requiring price to be at a structurally significant level.
Source:   Community implementation of Stochastic RSI strategy concept.
          https://www.tradingview.com/scripts/strategy/
          Structural low proximity gate: original innovation (avoids extension trap).
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. Stoch RSI = stochastic of RSI(rsi_len) over stoch_len bars.
                    Signal: stoch_k crosses above stoch_d + stoch_k < 20 (oversold zone).
                    Structural gate: close within proximity_pct of rolling low_lookback bar low.
                    Exit: Stoch RSI crosses above 80 (overbought) OR 30-bar timeout.
  2026-05-12  run   BTC 4H IS: Sharpe -2.694. IS negative → skip ETH. FAIL 0/5. Archived.
  2026-05-12  note  Structural low proximity (5% band) does not fix the knife-catch problem.
                    55% win rate but payoff 0.55 — same R:R inversion as RSI divergence (S4).
                    Downtrend extends through ATR stop before bounce completes. The near-low
                    gate is too loose (5% proximity covers many non-significant lows).
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param rsi_len int 14
# @param stoch_len int 14
# @param stoch_smooth int 3
# @param low_lookback int 60
# @param proximity_pct float 0.05
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

rsi_len = int(params.get('rsi_len', 14))
stoch_len = int(params.get('stoch_len', 14))
stoch_smooth = int(params.get('stoch_smooth', 3))
low_lookback = int(params.get('low_lookback', 60))
proximity_pct = float(params.get('proximity_pct', 0.05))
timeout_bars = int(params.get('timeout_bars', 30))

# --- RSI (Wilder EWM) ---
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = (-delta).clip(lower=0)
avg_gain = gain.ewm(com=rsi_len - 1, min_periods=rsi_len, adjust=False).mean()
avg_loss = loss.ewm(com=rsi_len - 1, min_periods=rsi_len, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs))

# --- Stochastic RSI ---
rsi_min = rsi.rolling(stoch_len).min()
rsi_max = rsi.rolling(stoch_len).max()
stoch_k_raw = 100 * (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan)
stoch_k = stoch_k_raw.rolling(stoch_smooth).mean()
stoch_d = stoch_k.rolling(stoch_smooth).mean()

# --- Structural low proximity gate ---
rolling_low = df['low'].rolling(low_lookback).min()
near_low = df['close'] <= rolling_low * (1 + proximity_pct)

# --- Stoch RSI cross up from oversold ---
stoch_cross_up = (stoch_k > stoch_d) & (stoch_k.shift(1) <= stoch_d.shift(1))
stoch_oversold = stoch_k < 20

# --- Entry: Stoch RSI cross from oversold + near structural low ---
df['buy'] = (stoch_cross_up & stoch_oversold & near_low).fillna(False)

# --- Exit: Stoch RSI reaches overbought ---
stoch_overbought_cross = (stoch_k > 80) & (stoch_k.shift(1) <= 80)
df['sell'] = stoch_overbought_cross.fillna(False)
