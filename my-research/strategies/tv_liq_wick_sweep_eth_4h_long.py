"""
Strategy: tv_liq_wick_sweep_eth_4h_long
Thesis:   A candle with a large lower wick that sweeps below the recent N-bar low and
          immediately recovers (close well above the low) is a proxy for a leveraged-long
          liquidation cascade. Forced market-sell liquidations push price briefly below
          structural support, then snap back once selling is absorbed. Enter on the close
          of the recovery candle.
Source:   CoinGlass liquidation heatmap analysis:
          https://quadcode.com/blog/bitcoin-liquidation-heatmap-and-how-to-use-it-for-profitable-trading
          Glassnode liquidation research:
          https://insights.glassnode.com/liquidation-heatmaps/
          Strategy: K-line proxy (no external liq data needed).
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   active

History (append-only, newest at bottom):
  2026-05-14  run   ETH 4H IS: Sharpe +1.566, Sortino +0.846, Calmar +4.955, IR +2.102 (elite),
                    PF 1.26, Win% 53.7%, payoff 1.09, n=54, exposure 17.8%. FAIL (PF<1.5).
                    ETH 4H OOS: Sharpe -0.438, PF 0.82, Win% 50.0%, payoff 0.82, n=18. FAIL.
                    IS structure is strong (IR 2.102), OOS collapses. Small OOS n=18 is noisy.
                    EMA gate variant tested (tv_liq_wick_sweep_eth_4h_long_ema_gate.py) → worse.
                    (log: 2026-05-14)
  2026-05-14  note  IS/OOS split driven by bear market 2025-2026 OOS period. Win rate 53.7%→50%,
                    payoff 1.09→0.82. Liq sweep mechanism exists in both bull/bear but bear
                    recoveries weaker. NOT archiving — IR 2.102 IS warrants further iteration
                    (vol_mult tuning, or multi-symbol diversification across BTC+SOL).
                    Next: test on BTC/USDT 4H to check if IS alpha generalizes cross-asset.
  2026-05-14  code  init. Wick proxy conditions:
                    (1) bar sweeps N-bar low: low < rolling_min_low (new low)
                    (2) recovery: close > previous close (recovered)
                    (3) wick dominance: (close-low)/(high-low) > 0.65 (lower wick large)
                    (4) volume spike: volume > 1.5× vol_SMA20 (liquidation volume)
                    Stop: bar low - 0.5×ATR. Timeout: 15 bars.
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
prior_low = df['low'].shift(1).rolling(sweep_lookback).min()
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

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Liquidation Wick Sweep Proxy ETH 4H Long",
    "plots": [
        {"name": "prior_low", "data": prior_low.fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "ATR",       "data": atr.fillna(0).tolist(),        "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20", "data": vol_sma.fillna(0).tolist(),    "color": "#9E9E9E", "overlay": False},
    ]
}
