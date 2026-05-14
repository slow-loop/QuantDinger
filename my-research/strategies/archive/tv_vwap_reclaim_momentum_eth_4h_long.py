"""
Strategy: tv_vwap_reclaim_momentum_eth_4h_long
Thesis:   Price consolidates BELOW rolling VWAP, then reclaims it (closes above) with a
          volume surge (2× SMA20 vol). The reclaim flips the "average cost" from above
          to below price — underwater traders become breakeven/profit, momentum follows.
          CRITICAL DISTINCTION: tv_vwap_stretch_reversion (archived) entered when price was
          STRETCHED AWAY from VWAP (counter-trend). This enters when price RECLAIMS VWAP
          (momentum-aligned). Completely opposite logic and regime.
Source:   Snappchart VWAP Momentum Strategy (Reclaim setup):
          https://www.snappchart.app/blog/strategy-playbooks/vwap-momentum-trading-strategy
          TradingView VWAP community scripts.
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-14  code  init. VWAP = rolling volume-weighted price (50-bar window as crypto proxy).
                    Reclaim: close crosses above VWAP from below (was below for ≥3 bars).
                    Volume gate: volume > 2× vol_SMA20.
                    Stop: VWAP level at entry. TP: prior N-bar high or 2×ATR.
                    Timeout: 20 bars.
  2026-05-14  run   BTC 4H IS: Sharpe -1.420, Sortino -0.539, Calmar -1.794, IR -0.975,
                    PF 0.681, Win% 43.8%, payoff 0.875, n=32. FAIL all.
                    BTC 4H OOS: Sharpe -1.529, Sortino -0.559, PF 0.510, Win% 42.9%,
                    payoff 0.679, n=7. FAIL all.
                    Note: first run (15:50:29) had 0 trades due to was_below_enough logic bug
                    (current bar was required both above AND below VWAP simultaneously);
                    fixed by shifting was_below_enough to prior bars only. Fixed run = IS -1.420.
                    (log: 2026-05-14)
  2026-05-14  note  Archive. Negative Sharpe in both IS and OOS — no edge in this mechanism
                    for crypto 4H. VWAP reclaims frequently precede failed breakouts (price
                    touches VWAP then reverses). Rolling 50-bar VWAP is a weak proxy for
                    true session VWAP. The 2× volume gate catches distribution as often as
                    accumulation. Fundamentally different from equity intraday VWAP setups.
"""

# @strategy stopLossPct 0.04
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param vwap_window int 50
# @param vol_mult float 2.0
# @param below_bars_min int 3
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

vwap_window    = int(params.get('vwap_window', 50))
vol_mult       = float(params.get('vol_mult', 2.0))
below_bars_min = int(params.get('below_bars_min', 3))
timeout_bars   = int(params.get('timeout_bars', 20))

# --- Rolling VWAP (crypto-native: no session reset, use rolling window) ---
# VWAP = sum(price * volume) / sum(volume) over rolling window
typical_price = (df['high'] + df['low'] + df['close']) / 3
cumvol  = df['volume'].rolling(vwap_window).sum()
cumpv   = (typical_price * df['volume']).rolling(vwap_window).sum()
vwap    = cumpv / cumvol

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Reclaim detection ---
below_vwap = df['close'] < vwap

# was_below_enough: ALL of the previous below_bars_min bars were below VWAP
# Use shift(1) so we check PAST bars only (not the current bar which may now be above VWAP)
was_below_enough = below_vwap.shift(1).rolling(below_bars_min).sum() >= below_bars_min

# Reclaim bar: current close > VWAP AND previous close < VWAP AND was below for enough bars
reclaim = (df['close'] > vwap) & (df['close'].shift(1) < vwap.shift(1)) & was_below_enough

# Entry: reclaim + volume spike
df['buy'] = (reclaim & vol_ok).fillna(False)

# Exit: timeout
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "VWAP Reclaim Momentum ETH 4H Long",
    "plots": [
        {"name": "VWAP",      "data": vwap.fillna(0).tolist(),       "color": "#FF5722", "overlay": True},
        {"name": "vol_SMA20", "data": vol_sma.fillna(0).tolist(),    "color": "#9E9E9E", "overlay": False},
        {"name": "volume",    "data": df['volume'].tolist(),         "color": "#4CAF50", "overlay": False},
    ]
}
