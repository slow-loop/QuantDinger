"""
Strategy: tv_keltner_expansion_breakout_eth_4h_long
Thesis:   After a period of price compression inside the Keltner Channel (ATR-based),
          a breakout above the upper band signals volatility expansion — sellers have
          been absorbed and buyers are in control. The compression period (N bars inside
          channel) acts as a coiled spring; the expansion breakout is the structural
          demand event. Keltner uses ATR (not std-dev), making it robust to crypto fat tails.
Source:   Keltner Channel Breakout concept, adapted for ETH 4H.
          See TV community: Keltner Channel strategies with compression filter.
          URL: https://www.tradingview.com/scripts/keltnerchannels/ (community strategies)
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. ETH Keltner expansion breakout.
                    Channel: EMA(ema_len) ± atr_mult * ATR(atr_len).
                    Compression: price inside channel for at least compress_bars recent bars
                    (rolling sum of inside-channel bars >= compress_bars).
                    Entry: close > upper_band AND compression was present in last look_back bars.
                    Exit: close < EMA (midline of channel) — price rejects back to center.
                    OR timeout (30 bars). Platform SL as backstop.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param ema_len int 20
# @param atr_len int 14
# @param atr_mult float 2.0
# @param compress_bars int 5
# @param look_back int 10
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

ema_len       = int(params.get('ema_len', 20))
atr_len       = int(params.get('atr_len', 14))
atr_mult      = float(params.get('atr_mult', 2.0))
compress_bars = int(params.get('compress_bars', 5))
look_back     = int(params.get('look_back', 10))
timeout_bars  = int(params.get('timeout_bars', 30))

# ── EMA (Keltner midline) ────────────────────────────────────────────────────
ema = df['close'].ewm(span=ema_len, adjust=False).mean()

# ── ATR (Wilder smoothing) ────────────────────────────────────────────────────
high_low = df['high'] - df['low']
high_pc  = (df['high'] - df['close'].shift(1)).abs()
low_pc   = (df['low']  - df['close'].shift(1)).abs()
tr       = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
atr      = tr.ewm(alpha=1/atr_len, adjust=False).mean()

# ── Keltner Bands ─────────────────────────────────────────────────────────────
upper_band = ema + atr_mult * atr
lower_band = ema - atr_mult * atr

# ── Compression: price inside channel ────────────────────────────────────────
inside_channel = (df['close'] <= upper_band) & (df['close'] >= lower_band)

# Count bars inside channel over the last look_back bars
# Use rolling sum shifted by 1 (no lookahead)
bars_inside_recent = inside_channel.shift(1).rolling(look_back).sum()
was_compressed = bars_inside_recent >= compress_bars

# ── Entry: breakout above upper band after compression ──────────────────────
above_upper = df['close'] > upper_band.shift(1)   # compare to prior bar's band (no lookahead)

df['buy'] = above_upper & was_compressed

# ── Exit: close below EMA (midline rejection) ────────────────────────────────
df['sell'] = df['close'] < ema.shift(1)

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
