"""
Strategy: tv_liq_wick_sweep_sol_4h_long
Thesis:   Identical Liq Wick Sweep mechanism as tv_liq_wick_sweep_eth_4h_long on SOL.
          Large lower wick sweeping the N-bar low + close recovery = proxy for a leveraged-
          long liquidation cascade. Forced market-sell liquidations push price briefly below
          structural support, then snap back once selling is absorbed.
          SOL has higher beta and heavier leveraged-long OI than ETH, making liquidation
          cascades more extreme and the recovery more pronounced in bear-regime markets.
          ETH version: IS elite (IR +2.102) but OOS fails. SOL version flips this —
          IS weak (Sharpe +0.233) but OOS strong (Sharpe +1.920, IR +1.144).
Source:   Same as tv_liq_wick_sweep_eth_4h_long (CoinGlass, Glassnode liq research).
          Cross-asset generalization of ETH Liq Wick test.
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. Exact copy of tv_liq_wick_sweep_eth_4h_long logic.
                    (1) bar sweeps N-bar low: low < rolling_min_low(20).
                    (2) recovery: close > previous close.
                    (3) wick dominance: (close-low)/(high-low) > 0.65.
                    (4) volume spike: volume > 1.5× vol_SMA20.
                    Stop: 5% platform. Timeout: 15 bars.
  2026-05-15  run   SOL/USDT 4H IS: Sharpe +0.233, Sortino +0.160, Calmar -1.117,
                    IR -0.527, PF 0.911, Win% 50.0%, payoff 0.911, n=62. FAIL.
                    SOL/USDT 4H OOS: Sharpe +1.920✅, Sortino +0.924⚠️, Calmar +5.666✅,
                    IR +1.144✅, PF 2.010✅, Win% 63.6%, payoff 1.148, n=11.
                    PASS 4/5. Sortino misses (0.924 vs 1.5 threshold).
                    (log: 2026-05-15)
  2026-05-15  note  SOL Liq Wick shows OOS > IS pattern (same as SFP and Vol Climax on SOL).
                    All three reversal/stop-hunt mechanisms on SOL show weak IS (bull market
                    sweeps often continue) but strong OOS (bear market sweeps snap back).
                    Consistent SOL reversal theme: high beta + bear regime = strong reversal alpha.
                    BTC Liq Wick tested: OOS Sharpe +1.552 but IR +0.304 only (3/5) — SOL superior.
                    ETH Liq Wick: IS IR +2.102 (elite) but OOS -0.438 — different regime bias.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param sweep_lookback int 20
# @param wick_ratio float 0.65
# @param vol_mult float 1.5
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

sweep_lookback = int(params.get('sweep_lookback', 20))
wick_ratio     = float(params.get('wick_ratio', 0.65))
vol_mult       = float(params.get('vol_mult', 1.5))
timeout_bars   = int(params.get('timeout_bars', 15))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- Sweep: bar low breaks N-bar rolling low (shift 1 to avoid lookahead) ---
prior_low  = df['low'].shift(1).rolling(sweep_lookback).min()
sweeps_low = df['low'] < prior_low

# --- Recovery: close recovers above previous close ---
recovers = df['close'] > df['close'].shift(1)

# --- Wick dominance: lower wick is large relative to full range ---
bar_range  = (df['high'] - df['low']).replace(0, np.nan)
lower_wick = df['close'] - df['low']
wick_dom   = (lower_wick / bar_range) > wick_ratio

# --- Entry: all conditions ---
df['buy'] = (sweeps_low & recovers & wick_dom & vol_ok).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Liquidation Wick Sweep Proxy SOL 4H Long",
    "plots": [
        {"name": "prior_low", "data": prior_low.fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "ATR",       "data": atr.fillna(0).tolist(),        "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20", "data": vol_sma.fillna(0).tolist(),    "color": "#9E9E9E", "overlay": False},
    ]
}
