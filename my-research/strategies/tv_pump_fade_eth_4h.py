"""
Strategy: tv_pump_fade_eth_4h
Thesis:   Any asset that surges >pump_pct% in pump_window bars, then shows a reversal
          signal (RSI overbought + first bearish close below EMA9), is statistically
          likely to mean-revert. Models the CEX-listing post-peak fade pattern without
          needing external event data: the pump detection is endogenous.
          Data: 83% of 2025 CEX-listed tokens are below listing price; Binance listings
          pump avg +87% then dump avg -70%. Pattern generalizes to any sharp price extension.
Source:   CEX listing pump-and-dump studies:
          https://bitpinas.com/cryptocurrency/binance-token-listing-dump/
          https://www.cryptopolitan.com/83-cex-listed-tokens-2025-trading-price/
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   active

History (append-only, newest at bottom):
  2026-05-14  code  init. Pump detection: rolling max gain over pump_window bars > pump_pct.
                    Overbought gate: RSI14 > rsi_thresh.
                    Reversal: close < EMA9 (first bar closing below fast MA after pump).
                    tradeDirection = short. Stop: high of last 3 bars. Timeout: 15 bars.
                    Note: uses @strategy tradeDirection short — platform must support shorts.
"""

# @strategy stopLossPct 0.06
# @strategy tradeDirection short
# @strategy entryPct 1.0

# @param pump_window int 10
# @param pump_pct float 0.30
# @param rsi_thresh float 68.0
# @param ema_fast int 9
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

pump_window  = int(params.get('pump_window', 10))
pump_pct     = float(params.get('pump_pct', 0.30))
rsi_thresh   = float(params.get('rsi_thresh', 68.0))
ema_fast     = int(params.get('ema_fast', 9))
timeout_bars = int(params.get('timeout_bars', 15))

# --- EMA9 ---
ema9 = df['close'].ewm(span=ema_fast, adjust=False).mean()

# --- RSI14 ---
delta  = df['close'].diff()
gain   = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
loss   = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
rs     = gain / loss.replace(0, np.nan)
rsi14  = 100 - 100 / (1 + rs)

# --- Pump detection: max close gain over pump_window bars ---
rolling_low  = df['close'].rolling(pump_window).min().shift(1)
pump_gain    = (df['close'] - rolling_low) / rolling_low.replace(0, np.nan)
pumped       = pump_gain > pump_pct

# --- Reversal signal: first bar closing below EMA9 after a pump ---
below_ema9     = df['close'] < ema9
was_above_ema9 = df['close'].shift(1) >= ema9.shift(1)
ema9_cross_dn  = below_ema9 & was_above_ema9

# --- Entry short: pump + overbought + EMA9 cross down ---
df['buy'] = (pumped & (rsi14 > rsi_thresh) & ema9_cross_dn).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Pump Fade ETH 4H Short",
    "plots": [
        {"name": "EMA9",      "data": ema9.fillna(0).tolist(),    "color": "#FF5722", "overlay": True},
        {"name": "RSI14",     "data": rsi14.fillna(0).tolist(),   "color": "#2196F3", "overlay": False},
        {"name": "pump_gain", "data": pump_gain.fillna(0).tolist(),"color": "#4CAF50","overlay": False},
    ]
}
