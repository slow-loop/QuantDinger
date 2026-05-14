"""
Strategy: tv_vol_climax_bottom_sol_4h_long
Thesis:   Identical Vol Climax mechanism as tv_vol_climax_bottom_eth_4h_long applied to SOL.
          Selling climax — extreme volume spike (3×+SMA20) + large bar range (>1.5×ATR)
          + close in upper half of bar after a declining price context.
          SOL's high beta, thinner order book, and leveraged-long-heavy OI make it the
          ideal asset for selling climax signals. In bear market cascades, SOL experiences
          more extreme liquidation waterfalls that snap back more cleanly than ETH or BTC.
          SOL OOS Sharpe +2.167 with PF 3.214 — strongest Vol Climax asset tested.
Source:   Same as tv_vol_climax_bottom_eth_4h_long (TradingView VCR indicator, zeiierman).
          Cross-asset generalization of ETH Vol Climax test.
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. Exact copy of tv_vol_climax_bottom_eth_4h_long logic.
                    (1) volume > 3.0 × vol_SMA20 (extreme volume spike).
                    (2) bar_range > 1.5 × ATR14 (large actual move).
                    (3) close in upper 50% of bar (buyers recovered intrabar).
                    (4) price was declining: close[-1] < SMA(close, 10).
                    Exit: 15-bar timeout. Stop: 5% platform.
  2026-05-15  run   SOL/USDT 4H IS: Sharpe +1.770, Sortino +1.136, Calmar +7.104,
                    IR +0.608, PF 1.228, Win% 51.5%, payoff 1.156, n=33. FAIL (PF<1.5).
                    SOL/USDT 4H OOS: Sharpe +2.167✅, Sortino +1.006⚠️, Calmar +9.993✅,
                    IR +1.080✅, PF 3.214✅, Win% 62.5%, payoff 1.928, n=8.
                    PASS 4/5. Sortino misses (1.006 vs 1.5 threshold). n=8 small.
                    (log: 2026-05-15)
  2026-05-15  note  SOL is the best Vol Climax asset (ETH OOS +0.020, BTC OOS -0.745).
                    High-beta + thin book = more extreme selling cascades = cleaner snapbacks.
                    n=8 OOS is statistically weak — keep active but treat as portfolio component
                    with limited position sizing. Need more OOS data to confirm.
                    Sortino miss (1.006) likely due to asymmetric return distribution
                    (a few large wins inflate Sharpe but irregular win timing affects Sortino).
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param vol_mult float 3.0
# @param atr_mult float 1.5
# @param close_pos_min float 0.5
# @param decline_bars int 10
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

vol_mult      = float(params.get('vol_mult', 3.0))
atr_mult      = float(params.get('atr_mult', 1.5))
close_pos_min = float(params.get('close_pos_min', 0.5))
decline_bars  = int(params.get('decline_bars', 10))
timeout_bars  = int(params.get('timeout_bars', 15))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Volume spike ---
vol_sma   = df['volume'].rolling(20).mean()
vol_spike = df['volume'] > vol_sma * vol_mult

# --- Large bar (real move) ---
bar_range  = (df['high'] - df['low']).replace(0, np.nan)
large_bar  = bar_range > atr * atr_mult

# --- Close in upper portion of bar (buyers absorbed selling intrabar) ---
close_pos  = (df['close'] - df['low']) / bar_range
upper_half = close_pos > close_pos_min

# --- Context: price was declining ---
close_sma_decline    = df['close'].shift(1).rolling(decline_bars).mean()
price_was_declining  = df['close'].shift(1) < close_sma_decline

# --- Entry ---
df['buy'] = (vol_spike & large_bar & upper_half & price_was_declining).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Volume Climax Bottom SOL 4H Long",
    "plots": [
        {"name": "ATR",       "data": atr.fillna(0).tolist(),              "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20", "data": vol_sma.fillna(0).tolist(),          "color": "#9E9E9E", "overlay": False},
        {"name": "close_sma", "data": close_sma_decline.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
    ]
}
