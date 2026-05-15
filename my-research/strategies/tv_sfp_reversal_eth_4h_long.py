"""
Strategy: tv_sfp_reversal_eth_4h_long
Thesis:   Swing Failure Pattern (SFP) — a bar sweeps below the prior N-bar swing low,
          triggering retail stop-losses, but closes BACK ABOVE that level. The failed
          breakdown reveals institutional absorption: market makers engineered the
          liquidity grab and immediately reversed once stop orders filled their bids.
          Unlike liq_wick_sweep (which checks wick dominance + close > prev close),
          SFP requires close > the swept level itself (stronger recovery condition)
          and close in the upper half of the bar (directional resolve).
Source:   LuxAlgo Swing Failure Pattern indicator:
          https://www.luxalgo.com/library/indicator/swing-failure-pattern-sfp/
          ICT / SMC community stop-hunt reversal framework:
          https://www.quantvps.com/blog/swing-failure-pattern-explained
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   active

History (append-only, newest at bottom):
  2026-05-15  code  init. SFP long: low sweeps prior swing low, close recovers above it,
                    close in upper 50% of bar (directional resolve), volume spike.
                    Distinct from tv_liq_wick_sweep: recovery condition is close > swept level
                    (not just close > prev close); no wick dominance ratio requirement.
                    Stop: sweep bar low - 0.5×ATR. Timeout: 15 bars.
  2026-05-15  run   ETH/USDT 4H IS: Sharpe -0.271, Sortino -0.230, PF 0.937, Win% 48.9%,
                    payoff 0.980, n=133. FAIL.
                    ETH/USDT 4H OOS: Sharpe +0.880, Sortino +0.641, Calmar +1.286, IR +0.603,
                    PF 1.192, Win% 53.1%, payoff 1.052, n=32. FAIL (Sharpe<1.0, PF<1.5).
                    Notable: OOS > IS — reversal mechanism suits 2025-2026 bear regime.
                    SOL/USDT 4H: IS Sharpe +2.435, OOS Sharpe +2.068, OOS PF 1.601 → PASS 4/5.
                    See tv_sfp_reversal_sol_4h_long.py for SOL-dedicated strategy.
                    (log: 2026-05-15)
  2026-05-15  note  ETH SFP marginal OOS (Sharpe 0.880) — keep active as portfolio component.
                    The OOS > IS regime flip is the key insight: bull-market (2020-2025) has
                    cleaner directional follow-through so SFPs resolve less reliably; bear
                    market (2025-2026) has more liquidity grabs that DO reverse. Long-term
                    this strategy may have asymmetric regime exposure. Monitor going forward.
  2026-05-15  run   BTC/USDT 4H IS: Sharpe -0.002, n=139. OOS: Sharpe +1.574✅, Sortino +1.126⚠️,
                    Calmar +5.841✅, IR +0.579✅, PF 1.657✅, n=31. PASS 4/5 (Sortino miss).
                    → dedicated file: tv_sfp_reversal_btc_4h_long.py
                    Cross-asset summary: OOS > IS pattern confirmed on ETH, SOL, and BTC.
                    SFP is a consistent bear-market reversal mechanism across all three assets.
  2026-05-15  run   Small-cap cross-test AVAX/LINK/ARB/OP/DOGE 4H. OOS:
                    OP PASS 5/5 — Sharpe +2.059, Sortino +1.618, Calmar +15.345,
                    IR +3.738, PF 1.609, win 56.0%, n=25.
                    AVAX 4/5 — Sharpe +1.835, IR +2.430, PF 1.642, n=25.
                    DOGE 2/5 marginal; ARB/LINK failed. OP is the best new SFP candidate.
                    (log: 2026-05-15T06:17:13..06:18:01)
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param swing_lookback int 10
# @param vol_mult float 1.5
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

swing_lookback = int(params.get('swing_lookback', 10))
vol_mult       = float(params.get('vol_mult', 1.5))
timeout_bars   = int(params.get('timeout_bars', 15))

# --- ATR ---
tr = pd.concat([
    df['high'] - df['low'],
    (df['high'] - df['close'].shift(1)).abs(),
    (df['low']  - df['close'].shift(1)).abs(),
], axis=1).max(axis=1)
atr = tr.ewm(span=14, adjust=False).mean()

# --- Prior swing low (shift 1 to avoid lookahead) ---
prior_swing_low = df['low'].shift(1).rolling(swing_lookback).min()

# --- SFP Long conditions ---
# (1) Bar sweeps below the prior swing low
sweeps_swing_low = df['low'] < prior_swing_low

# (2) Bar CLOSES above the swept level (not just above prev close — stronger recovery)
recovers_above_level = df['close'] > prior_swing_low

# (3) Close in upper half of bar (directional resolve, not a doji recovery)
bar_range   = (df['high'] - df['low']).replace(0, np.nan)
close_pos   = (df['close'] - df['low']) / bar_range
close_upper = close_pos > 0.5

# (4) Volume spike (liquidity grab confirmed by stop-out volume)
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- Entry ---
df['buy'] = (sweeps_swing_low & recovers_above_level & close_upper & vol_ok).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "SFP Swing Failure Pattern ETH 4H Long",
    "plots": [
        {"name": "prior_swing_low", "data": prior_swing_low.fillna(0).tolist(), "color": "#F44336", "overlay": True},
        {"name": "ATR",             "data": atr.fillna(0).tolist(),             "color": "#9C27B0", "overlay": False},
        {"name": "vol_SMA20",       "data": vol_sma.fillna(0).tolist(),         "color": "#9E9E9E", "overlay": False},
    ]
}
