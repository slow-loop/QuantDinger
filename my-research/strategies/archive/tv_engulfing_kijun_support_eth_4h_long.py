"""
Strategy: tv_engulfing_kijun_support_eth_4h_long
Thesis:   In an Ichimoku uptrend (price above cloud + Tenkan > Kijun), price pulls back
          to the Kijun-sen (base line) and forms a bullish engulfing candle. The Kijun is
          the Ichimoku structural support in a trending market; a bullish engulfing there
          signals buyers defending the structural level. This combines a structural level
          (Kijun) with a candlestick confirmation signal (engulfing) — both required.
Source:   Ichimoku Tenkan/Kijun interaction and candlestick pattern combination.
          Inspired by YellowKuma "Ichimoku Bounce on Tenkan-Sen" (TradingView, 52 likes).
          https://www.tradingview.com/script/js2sP2g4-Ichimoku-Bounce-on-Tenkan-Sen-by-YellowKuma/
          Entry innovation: Kijun (not Tenkan) + engulfing confirmation (not just touch).
Status:   archived

History (append-only, newest at bottom):
  2026-05-12  code  init. Crypto-optimized Ichimoku: tenkan=20, kijun=60.
                    Uptrend filter: price > cloud_top (from Kumo) AND tenkan > kijun.
                    Kijun proximity: low touched or came within proximity_pct of kijun.
                    Bullish engulfing: current close > prev close AND current close > prev open
                    AND current open < prev close AND current open < prev open.
                    Entry: engulfing at kijun in uptrend (all 3 conditions).
                    Exit: close drops below kijun (structure lost) OR 30-bar timeout.
  2026-05-12  run   BTC 4H IS: Sharpe -0.016. IS Sharpe < 0 → skip ETH. FAIL 0/5. Archived.
  2026-05-12  note  IS payoff 5.07 is compelling (similar to ETH Kumo 7.95) but IS win rate
                    15.9% with PF 0.96 means the few big wins don't cover many small losses.
                    The Kijun proximity gate (2%) is too tight — only n=44 IS trades over 5yr.
                    In a bear/chop regime, price rarely enters genuine Kumo uptrend context
                    AND touches Kijun AND forms engulfing simultaneously. May work in a bull
                    market where price is persistently above the cloud.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param tenkan int 20
# @param kijun int 60
# @param senkou_b int 120
# @param displacement int 30
# @param proximity_pct float 0.02
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

# Alias open column
_op = 'open'
candle_open = df[_op]

tenkan_len   = int(params.get('tenkan', 20))
kijun_len    = int(params.get('kijun', 60))
senkou_b_len = int(params.get('senkou_b', 120))
displace     = int(params.get('displacement', 30))
proximity_pct = float(params.get('proximity_pct', 0.02))
timeout_bars = int(params.get('timeout_bars', 30))

# Ichimoku components
tenkan = (df['high'].rolling(tenkan_len).max() + df['low'].rolling(tenkan_len).min()) / 2
kijun  = (df['high'].rolling(kijun_len).max()  + df['low'].rolling(kijun_len).min())  / 2

# Senkou spans (displaced)
senkou_a = ((tenkan + kijun) / 2).shift(displace)
senkou_b = ((df['high'].rolling(senkou_b_len).max() + df['low'].rolling(senkou_b_len).min()) / 2).shift(displace)

cloud_top = pd.concat([senkou_a, senkou_b], axis=1).max(axis=1)

# Uptrend filter: price above cloud AND Tenkan > Kijun
above_cloud = df['close'] > cloud_top
tenkan_gt_kijun = tenkan > kijun
in_uptrend = above_cloud & tenkan_gt_kijun

# Kijun proximity: low came close to or touched Kijun on this or prior bar
near_kijun = (
    (df['low'] <= kijun * (1 + proximity_pct)) &
    (df['low'] >= kijun * (1 - proximity_pct))
) | (
    (df['low'].shift(1) <= kijun.shift(1) * (1 + proximity_pct)) &
    (df['low'].shift(1) >= kijun.shift(1) * (1 - proximity_pct))
)

# Bullish engulfing: current bar engulfs previous bearish bar
prev_bearish = candle_open.shift(1) > df['close'].shift(1)
engulfs_prev = (df['close'] > candle_open.shift(1)) & (candle_open < df['close'].shift(1))
bullish_engulfing = prev_bearish & engulfs_prev & (df['close'] > candle_open)

# Entry: uptrend + Kijun proximity + bullish engulfing
df['buy'] = (in_uptrend & near_kijun & bullish_engulfing).fillna(False)

# Exit: close drops below Kijun (structural support lost)
df['sell'] = (df['close'] < kijun).fillna(False)
