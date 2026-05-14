"""
Strategy: tv_crt_daily_sweep_eth_1d_long
Thesis:   Candle Range Theory (CRT) — each candle is a fractal liquidity range.
          In the FOLLOWING candle, price sweeps one extreme of the prior candle
          (triggering stops at that level), then delivers in the opposite direction.
          For a long setup: current 1D bar sweeps the prior bar's LOW (false breakdown),
          then closes ABOVE the prior bar's low with a bullish body.
          The prior bar's high is the institutional delivery target (liquidity pool above).
          This is an ICT-derived pattern — the "sweep and reverse" is driven by the same
          stop-hunt mechanics as SFP but operates at the single-bar fractal level.
Source:   ICT Candle Range Theory:
          https://innercircletrader.net/tutorials/candle-range-theory-crt/
          writofinance.com CRT explanation:
          https://www.writofinance.com/candle-range-theory-crt/
          Scouted 2026-05-15 (non-orthodox strategy matrix session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-15  code  init. CRT long: current bar's low < prior bar's low (sweep),
                    current bar's close > prior bar's low (recovery),
                    current bar is bullish (close > open).
                    Exit: prior bar's high reached (target) OR invalidation
                    (close < prior bar's low) OR 10-bar timeout.
                    Tested on 1D (fractal is clearest at daily resolution).
  2026-05-15  run   ETH/USDT 1D IS: Sharpe -0.147, Sortino -0.116, PF 0.876, Win% 32.4%,
                    payoff 1.825, n=74. FAIL.
                    ETH/USDT 1D OOS: Sharpe -1.361, Sortino -0.833, PF 0.366, Win% 26.7%,
                    payoff 1.006, n=15. FAIL.
                    (log: 2026-05-15)
  2026-05-15  note  Archive. CRT fires too frequently (n=74 IS = 14.8/yr) on 1D, indicating
                    the pattern is not selective enough. "Sweep prior bar's low + bullish close"
                    is too common a pattern — every pullback candle qualifies. IS Win% 32.4%
                    with good payoff (1.825) but net negative because the mechanism selects
                    for large-range days that often continue lower. The OOS collapse to
                    PF 0.366 confirms no genuine edge. A tighter filter (e.g., sweep must
                    be at a prior significant swing, not just prior bar) would improve selectivity.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param timeout_bars int 10
# @param vol_mult float 1.0

import pandas as pd
import numpy as np

df = df.copy()

timeout_bars = int(params.get('timeout_bars', 10))
vol_mult     = float(params.get('vol_mult', 1.0))

# --- Volume filter (optional, gentle threshold) ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = (df['volume'] > vol_sma * vol_mult) if vol_mult > 0 else pd.Series(True, index=df.index)

# --- CRT Long conditions ---
# (1) Current bar sweeps prior bar's low
sweeps_prior_low = df['low'] < df['low'].shift(1)

# (2) Current bar recovers above prior bar's low (false breakdown)
recovers_above   = df['close'] > df['low'].shift(1)

# (3) Current bar is bullish (institutional delivery upward)
bullish_close    = df['close'] > df['open']

# --- Entry ---
df['buy'] = (sweeps_prior_low & recovers_above & bullish_close & vol_ok).fillna(False)

# --- Exit: close drops below swept level (invalidation) = stop signal ---
# Platform stopLossPct handles the hard stop; this catches structural invalidation
invalidated = df['close'] < df['low'].shift(1)

# Timeout
timed_out = df['buy'].shift(timeout_bars).fillna(False)

df['sell'] = (invalidated | timed_out).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "CRT Daily Sweep ETH 1D Long",
    "plots": [
        {"name": "prior_low",  "data": df['low'].shift(1).fillna(0).tolist(),  "color": "#F44336", "overlay": True},
        {"name": "prior_high", "data": df['high'].shift(1).fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "vol_SMA20",  "data": vol_sma.fillna(0).tolist(),             "color": "#9E9E9E", "overlay": False},
    ]
}
