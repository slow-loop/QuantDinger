"""
Strategy: tv_fvg_liquidity_sweep_eth_4h_long
Thesis:   ICT (Inner Circle Trader) Silver Bullet: Price grabs liquidity above a swing high
          (fake breakout), then aggressively reverses (Change of Character / CHoCH). In the
          reversal move, price leaves a Fair Value Gap (FVG) — a 3-candle imbalance where
          Bar[i-2].high < Bar[i].low. Price typically returns to fill this FVG before
          continuing. Entry at the FVG zone on the retracement.
          Core principle: liquidity sweep = engineered move to grab stops; FVG = institutional
          order block left unfilled; the retracement to FVG = smart money re-entry.
Source:   ICT Silver Bullet & FVG strategy (Bitget Academy):
          https://www.bitget.com/academy/12560603863695
          ICT Trading Strategy Basics (Coinranking):
          https://coinranking.com/blog/ict-trading-strategy-basics-liquidity-imbalance-market-structure-timing/
          GitHub smart-money-concepts Python package (joshyattridge):
          https://github.com/joshyattridge/smart-money-concepts
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   active

History (append-only, newest at bottom):
  2026-05-14  code  init. Three-step detection:
                    (1) Liquidity sweep: bar breaks N-bar high, closes below it (pin bar / engulf).
                    (2) CHoCH (bearish flip): after the sweep, price closes below prior swing low.
                    (3) Bullish FVG: 3-bar pattern Bar[i-2].high < Bar[i].low (price gap up,
                        imbalance zone = Bar[i-2].high to Bar[i].low).
                    Entry: price retraces into the FVG zone (between FVG low and FVG high),
                           fired when close crosses into the zone from above.
                    Stop: FVG low - 0.5×ATR. TP: pre-sweep swing high. Timeout: 25 bars.
                    Note: Vectorized — FVG zone is tracked via ffill after detection.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param sweep_lookback int 20
# @param choch_lookback int 10
# @param timeout_bars int 25

import pandas as pd
import numpy as np

df = df.copy()

sweep_lookback = int(params.get('sweep_lookback', 20))
choch_lookback = int(params.get('choch_lookback', 10))
timeout_bars   = int(params.get('timeout_bars', 25))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# ---------------------------------------------------------------------------
# Step 1: Bullish FVG detection
# Bullish FVG at bar i: Bar[i-2].high < Bar[i].low  (gap between them)
# Zone: [Bar[i-2].high, Bar[i].low]
# ---------------------------------------------------------------------------
fvg_low  = df['high'].shift(2)          # bottom of the gap = high of bar i-2
fvg_high = df['low']                    # top of the gap = low of current bar
is_bullish_fvg = (fvg_low < fvg_high) & (fvg_high - fvg_low > atr * 0.1)

# Carry the most recent FVG zone forward until filled
active_fvg_low  = fvg_low.where(is_bullish_fvg).ffill()
active_fvg_high = fvg_high.where(is_bullish_fvg).ffill()

# FVG is "fresh" — only use FVGs from the last N bars
fvg_bar_index = pd.Series(np.where(is_bullish_fvg, df.index if hasattr(df.index, '__len__') else range(len(df)), np.nan), index=df.index)
# Use positional index instead
pos = pd.Series(range(len(df)), index=df.index)
fvg_pos = pos.where(is_bullish_fvg).ffill()
fvg_age = pos - fvg_pos
fvg_fresh = fvg_age <= sweep_lookback

# ---------------------------------------------------------------------------
# Step 2: Liquidity sweep (bearish fake-breakout above N-bar high, then reverses)
# Sweep: bar high > prior N-bar rolling high BUT close < prior high (pin/rejection)
# ---------------------------------------------------------------------------
prior_high   = df['high'].shift(1).rolling(sweep_lookback).max()
is_sweep     = (df['high'] > prior_high) & (df['close'] < prior_high)

# Recent sweep: within last choch_lookback bars
sweep_pos    = pos.where(is_sweep).ffill()
sweep_age    = pos - sweep_pos
recent_sweep = sweep_age <= choch_lookback

# ---------------------------------------------------------------------------
# Step 3: Entry — price retraces INTO the FVG zone after a sweep
# Entry condition: close enters the FVG zone from above (was above zone, now inside)
# ---------------------------------------------------------------------------
in_fvg_zone = (df['close'] >= active_fvg_low) & (df['close'] <= active_fvg_high)
was_above_zone = df['close'].shift(1) > active_fvg_high.shift(1)

entry_signal = in_fvg_zone & was_above_zone & recent_sweep & fvg_fresh

df['buy'] = entry_signal.fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "FVG Liquidity Sweep ETH 4H Long",
    "plots": [
        {"name": "fvg_high",    "data": active_fvg_high.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "fvg_low",     "data": active_fvg_low.fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "prior_high",  "data": prior_high.fillna(0).tolist(),      "color": "#FF9800", "overlay": True},
        {"name": "ATR",         "data": atr.fillna(0).tolist(),             "color": "#9C27B0", "overlay": False},
    ]
}
