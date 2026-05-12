"""
Strategy: tv_obv_price_breakout_4h_long
Thesis:   Price and OBV simultaneously break to new N-bar highs, confirming institutional
          accumulation behind the price breakout. OBV new high = volume is net-positive
          across the breakout window, meaning buyers are absorbing supply persistently.
          Price-only breakout without OBV confirmation is often a false breakout (distribution).
          Combined signal is a structural event with volume catalyst.
Source:   OBV (On Balance Volume) breakout concept, widely documented in volume analysis.
          https://www.tradingview.com/scripts/volume/
          Original OBV: Joseph Granville (1963). Breakout variant: community implementation.
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. OBV = cumulative sum(volume * sign(close change)).
                    Price BOS: close > rolling_max(close, lookback).shift(1).
                    OBV BOS: obv > rolling_max(obv, lookback).shift(1).
                    Entry: both break simultaneously (same bar).
                    Exit: OBV drops below its 20-bar moving average (volume trend reversal)
                    OR 40-bar timeout. Platform SL handles hard stop.
  2026-05-12  run   BTC 4H OOS: Sharpe -5.035, PF 0.38, n=47. FAIL 0/5.
                    ETH 4H OOS: Sharpe -1.258, PF 0.81, n=45. FAIL 0/5. Archived.
  2026-05-12  note  65% time-in-market — not selective enough. OBV and price at new highs
                    simultaneously is too common in trending sub-periods. OBV MA exit also
                    triggers frequently. Result: heavy fee drag + frequent false breakouts.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param lookback int 20
# @param obv_ma_len int 20
# @param timeout_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

lookback    = int(params.get('lookback', 20))
obv_ma_len  = int(params.get('obv_ma_len', 20))
timeout_bars = int(params.get('timeout_bars', 40))

# --- OBV calculation ---
close_change = df['close'].diff()
direction = np.sign(close_change).fillna(0)
obv = (direction * df['volume']).cumsum()

# --- Price and OBV breakout ---
price_high = df['close'].shift(1).rolling(lookback).max()
obv_high   = obv.shift(1).rolling(lookback).max()

price_bos = df['close'] > price_high
obv_bos   = obv > obv_high

# --- Entry: both price and OBV at new N-bar high simultaneously ---
df['buy'] = (price_bos & obv_bos).fillna(False)

# --- Exit: OBV drops below its moving average (accumulation ends) ---
obv_ma = obv.rolling(obv_ma_len).mean()
obv_below_ma = (obv < obv_ma) & (obv.shift(1) >= obv_ma.shift(1))

df['sell'] = obv_below_ma.fillna(False)
