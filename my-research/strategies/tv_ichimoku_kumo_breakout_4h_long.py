"""
Strategy: tv_ichimoku_kumo_breakout_4h_long
Thesis:   Price breaking above the Ichimoku Kumo (cloud) after being inside or below it
          signals a structural regime change — buyers have absorbed sellers across the
          entire cloud zone. The Kumo is a dynamic demand/supply zone, not a simple MA.
          Breakout above both Senkou spans is a discrete structural event with squeeze
          mechanics (shorts covering as price clears resistance).
Source:   Adapted from Ichimoku Kinko Hyo Cloud (no-offset, no-repaint) by KryptoNight
          https://www.tradingview.com/scripts/ichimokuclouds/ (1.8K likes)
          Crypto-optimized settings: 20/60/120/30 (vs standard 9/26/52/26 forex)
          See also: Ichimoku Cloud Back test by Yo_adriiiiaan (1K likes, simple kumo cross)
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Kumo breakout strategy, crypto-optimized Ichimoku settings.
                    Tenkan=20, Kijun=60, Senkou B=120, displacement=30 (crypto-native).
                    Entry: close crosses above BOTH Senkou A and B (above cloud top).
                    Must be entering from below (prior close was below cloud OR in cloud).
                    Additional filter: Tenkan > Kijun (short-term momentum aligns with breakout).
                    Exit: close drops below cloud bottom (Senkou B or A, whichever is lower) OR
                    30-bar timeout. Platform SL handles hard stop.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param tenkan int 20
# @param kijun int 60
# @param senkou_b int 120
# @param displacement int 30
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

tenkan_len   = int(params.get('tenkan', 20))
kijun_len    = int(params.get('kijun', 60))
senkou_b_len = int(params.get('senkou_b', 120))
displace     = int(params.get('displacement', 30))
timeout_bars = int(params.get('timeout_bars', 30))

# ── Ichimoku components ──────────────────────────────────────────────────────

# Tenkan-sen (conversion line): midpoint of N-bar high-low range
tenkan = (df['high'].rolling(tenkan_len).max() + df['low'].rolling(tenkan_len).min()) / 2

# Kijun-sen (base line): midpoint of M-bar high-low range
kijun = (df['high'].rolling(kijun_len).max() + df['low'].rolling(kijun_len).min()) / 2

# Senkou Span A: midpoint of Tenkan and Kijun, shifted forward by displacement
# For non-repaint evaluation, we shift back (i.e., use values from [displace] bars ago)
senkou_a = ((tenkan + kijun) / 2).shift(displace)

# Senkou Span B: midpoint of senkou_b_len range, shifted forward by displacement
senkou_b = ((df['high'].rolling(senkou_b_len).max() + df['low'].rolling(senkou_b_len).min()) / 2).shift(displace)

# Cloud top and bottom (current cloud — shifted to align with current price)
cloud_top = pd.concat([senkou_a, senkou_b], axis=1).max(axis=1)
cloud_bot = pd.concat([senkou_a, senkou_b], axis=1).min(axis=1)

# ── Breakout detection ────────────────────────────────────────────────────────
# Current close is above the cloud
above_cloud = df['close'] > cloud_top

# Prior close was NOT above cloud (entering from below or inside)
# Use shift(1) to get prior bar state
prior_in_or_below = df['close'].shift(1) <= cloud_top.shift(1)

# Tenkan > Kijun (short-term momentum aligned with breakout direction)
tenkan_above_kijun = tenkan > kijun

# ── Entry signal ─────────────────────────────────────────────────────────────
df['buy'] = (
    above_cloud &
    prior_in_or_below &
    tenkan_above_kijun
)

# ── Exit signal ───────────────────────────────────────────────────────────────
# Exit when close drops below cloud bottom (structure reclaimed then lost)
df['sell'] = df['close'] < cloud_bot

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
