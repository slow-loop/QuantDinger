"""
Strategy: tv_vol_climax_bottom_eth_4h_long
Thesis:   Selling climax — after a decline, a bar with extreme volume (3×+ SMA20)
          AND large range (>1.5×ATR) AND close in the upper half of the bar signals
          that sellers have exhausted themselves. The massive volume absorbed by buyers
          prevents continuation; smart money has fully covered their short inventory.
          Crypto-specific: leverage cascades and liquidation waterfalls amplify volume
          spikes at capitulation lows, making this signal more reliable than in equities.
          Distinct from tv_liq_wick_sweep: no wick dominance ratio, no sweep of N-bar low.
          Climax is an exhaustion signal (large absolute volume), not a structural sweep.
Source:   TradingView "Volume Climax Reversal (VCR)" by Rendon1 and zeiierman:
          https://www.tradingview.com/script/AxKt5f9c-Volume-Climax-Reversal-VCR-Catch-Exhaustion-Tops-Bottoms/
          Finveroo Volume Climax strategy guide
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. Selling climax (long setup):
                    (1) volume > vol_mult × vol_SMA20 (extreme volume spike).
                    (2) bar_range > atr_mult × ATR14 (large actual move, not a doji).
                    (3) close in upper close_pos_min% of bar (buyers recovered intrabar).
                    (4) price was declining: close[-1] < SMA(close, decline_bars) context.
                    Exit: 15-bar timeout. Stop: 5% (platform).
  2026-05-15  run   ETH/USDT 4H IS: Sharpe +1.173, Sortino +0.503, Calmar +3.649, IR +0.287,
                    PF 1.252, Win% 59.5%, payoff 0.854, n=37. FAIL (PF<1.5).
                    ETH/USDT 4H OOS: Sharpe +0.020, Sortino +0.012, PF 1.089, Win% 40%,
                    payoff 1.633, n=5. FAIL (n too small, metrics flat).
                    SOL/USDT 4H IS: Sharpe +1.770, Sortino +1.136, Calmar +7.104, IR +0.608,
                    PF 1.228, Win% 51.5%, payoff 1.156, n=33. FAIL (PF<1.5).
                    SOL/USDT 4H OOS: Sharpe +2.167✅, Sortino +1.006⚠️, Calmar +9.993✅,
                    IR +1.080✅, PF 3.214✅, Win% 62.5%, payoff 1.928, n=8. PASS 4/5.
                    Sortino misses (1.006 vs 1.5). n=8 OOS too small for high confidence.
                    (log: 2026-05-15)
  2026-05-15  note  SOL shows strong OOS (PF 3.214, Sharpe 2.167) but n=8 is statistically
                    weak. Volume climax mechanism is more dramatic on SOL — high-beta asset
                    has more extreme selling cascades that snap back cleanly. Binding constraint
                    is the `decline_bars` + large_bar combination, not vol_mult.
                    Keep active — mechanism is sound on SOL, needs more OOS data.
                    ETH OOS too small (n=5) + flat metrics — ETH version essentially inconclusive.
  2026-05-15  run   BTC/USDT 4H IS: Sharpe -0.006, n=26. OOS: Sharpe -0.745, PF 0.60, n=6.
                    FAIL. BTC too liquid for selling cascades — deep order book absorbs without
                    sharp reversal. Vol Climax is SOL-specific; BTC has no edge.
                    Cross-asset: SOL >> ETH > BTC for this mechanism.
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

# --- Context: price was declining (selling climax requires prior selling pressure) ---
close_sma_decline    = df['close'].shift(1).rolling(decline_bars).mean()
price_was_declining  = df['close'].shift(1) < close_sma_decline

# --- Entry ---
df['buy'] = (vol_spike & large_bar & upper_half & price_was_declining).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Volume Climax Bottom ETH 4H Long",
    "plots": [
        {"name": "ATR",           "data": atr.fillna(0).tolist(),       "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20",     "data": vol_sma.fillna(0).tolist(),   "color": "#9E9E9E", "overlay": False},
        {"name": "close_sma",     "data": close_sma_decline.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
    ]
}
