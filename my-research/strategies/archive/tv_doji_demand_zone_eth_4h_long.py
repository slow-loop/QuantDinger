"""
Strategy: tv_doji_demand_zone_eth_4h_long
Thesis:   A doji candle (open ≈ close, body < 25% of range) forming inside a demand zone
          (prior swing-low area) signals institutional absorption — sellers failed to push
          price lower; indecision resolves upward when in uptrend (price > EMA200).
          Based on TradingView "Twisted Forex's Doji+Area" (217 likes) plus EMA200 macro gate.
Source:   TradingView "Twisted Forex's Doji+Area" strategy (217 likes):
          Candlestick patterns + supply/demand zones page
          https://www.tradingview.com/scripts/candlestickpatterns/?script_type=strategies
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-14  code  init. Doji: |close-open|/(high-low) < 0.25 AND bar range > 0.
                    Demand zone: price within ATR×zone_mult of rolling N-bar low.
                    EMA200 gate: close > EMA200 (macro uptrend only).
                    Entry: doji + in_demand_zone + ema200_gate.
                    Stop: demand zone bottom (swing low - 0.5×ATR). Timeout: 20 bars.
  2026-05-14  run   BTC 4H IS: Sharpe +4.066, Sortino +2.926, Calmar +113.1, IR +3.778,
                    PF 2.037, Win% 56.5%, payoff 1.571, n=62. FAIL (OOS).
                    BTC 4H OOS: Sharpe -2.427, Sortino -0.915, PF 0.220, Win% 16.7%,
                    payoff 1.102, n=6. FAIL all.
                    (log: 2026-05-14)
  2026-05-14  note  Archive. IS looks strong but OOS is catastrophic (PF 0.22, Win% 16.7%,
                    n=6 only). The EMA200 gate restricts OOS to nearly zero entries —
                    bear market kills doji demand zone setups entirely. Same fundamental
                    problem as NR7: EMA200 trend gate over-fits to 2020-2025 bull run.
                    The "doji in demand zone" pattern has no distributional edge beyond
                    being a proxy for low-volatility support touches; resolve direction
                    is random.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param ema_long int 200
# @param zone_lookback int 50
# @param zone_atr_mult float 1.5
# @param doji_body_ratio float 0.25
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

ema_long       = int(params.get('ema_long', 200))
zone_lookback  = int(params.get('zone_lookback', 50))
zone_atr_mult  = float(params.get('zone_atr_mult', 1.5))
doji_body_ratio= float(params.get('doji_body_ratio', 0.25))
timeout_bars   = int(params.get('timeout_bars', 20))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- EMA200 trend gate ---
ema200 = df['close'].ewm(span=ema_long, adjust=False).mean()
trend_ok = df['close'] > ema200

# --- Doji detection ---
bar_range = (df['high'] - df['low']).replace(0, np.nan)
body      = (df['close'] - df['open']).abs()
is_doji   = (body / bar_range) < doji_body_ratio

# --- Demand zone: price near rolling N-bar low (within zone_atr_mult × ATR) ---
demand_low = df['low'].rolling(zone_lookback).min()
in_zone    = df['low'] <= demand_low + atr * zone_atr_mult

# --- Entry ---
df['buy'] = (is_doji & in_zone & trend_ok).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Doji Demand Zone ETH 4H Long",
    "plots": [
        {"name": "EMA200",      "data": ema200.fillna(0).tolist(),       "color": "#FF5722", "overlay": True},
        {"name": "demand_low",  "data": demand_low.fillna(0).tolist(),   "color": "#4CAF50", "overlay": True},
        {"name": "ATR",         "data": atr.fillna(0).tolist(),          "color": "#9C27B0", "overlay": False},
    ]
}
