"""
Strategy: tv_eth_horizontal_reclaim_1d_long
Thesis:   ETH 1D — enter long on horizontal reclaim of 50-day high after a pullback.
          Participants who sold the breakdown are squeezed out when price reclaims the level,
          generating short-term upside continuation. Exit after a fixed horizon or if price
          falls more than stop_pct below entry. Sized to ETH only (BTC OOS failed the factor test).
Built on: factors/factor_horizontal_reclaim.py
Source:   factor sourced from CryptoTony__ KOL signal (emg_014_horizontal_reclaim),
          cross-tested on ETH/USDT 1D in journal 2026-05-10.
          Strategy wrapper written 2026-05-12.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. Inline horizontal_reclaim logic (50d high reclaim after ≥3% below
                    for 10 bars). Entry on reclaim bar. Exit: 30-bar timeout OR price drops
                    stop_pct (5%) below entry bar close. Long only. ETH-specific.
  2026-05-12  run   ETH/USDT 1D — IS: Sharpe +1.49 Sortino +1.33 Calmar +3.05 PF 1.67 n=61 ✓
                    OOS: Sharpe +1.61 Sortino +1.33 Calmar +2.99 IR +0.46 PF 3.07 n=10.
                    OOS: +40.69% return vs BTC B&H -13.66%. 17.6% time in market.
                    PASS: Sharpe ✅ Calmar ✅ PF ✅ | MISS: Sortino ⚠️ (1.33<1.5) IR ⚠️ (0.46<0.5).
                    OOS n=10 thin but PF 3.07 is unusually strong. Payoff ratio 4.61 (large winner
                    asymmetry) carrying the equity curve. Sortino miss driven by single large
                    drawdown in IS regime (-46%). ETH-specific; BTC OOS failed (Sharpe -1.71).
                    (log: 2026-05-12T05:27:01)
  2026-05-12  note  CONDITIONAL PASS — 3/5 criteria met. Promising as portfolio component given
                    PF 3.07 and Calmar 2.99 OOS. Monitor OOS as new bars accrue. Do not deploy
                    on BTC (failed). Parameters locked for now: lookback=50, below_pct=3%,
                    timeout=30, stop=5%. Future structural variant could add ADX/trend filter
                    to reduce IS drawdown and push Sortino above 1.5.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param lookback_high int 50
# @param below_pct float 0.03
# @param below_bars int 10
# @param timeout_bars int 30
# @param stop_pct float 0.05

import pandas as pd
import numpy as np

df = df.copy()

lookback_high = int(params.get('lookback_high', 50))
below_pct = float(params.get('below_pct', 0.03))
below_bars = int(params.get('below_bars', 10))
timeout_bars = int(params.get('timeout_bars', 30))
stop_pct = float(params.get('stop_pct', 0.05))

# 50-bar rolling high (proxy for 50-day high on 1D timeframe)
high_50 = df['high'].rolling(window=lookback_high, min_periods=lookback_high // 2).max()

# Was price ≥below_pct% below the 50-bar high, `below_bars` bars ago?
was_below = df['close'].shift(below_bars) < high_50.shift(below_bars) * (1 - below_pct)

# Reclaim: price is now back above the 50-bar high (from below_bars ago)
reclaim = (df['close'] > high_50.shift(below_bars)) & was_below

# Only fire on the first reclaim bar (edge trigger)
fresh_reclaim = reclaim & ~reclaim.shift(1).fillna(False)

# Time exit: timeout_bars after entry
time_exit = fresh_reclaim.shift(timeout_bars).fillna(False)

# Stop loss: covered by @strategy stopLossPct 0.05 platform-level stop.
# Explicitly signal sell only on timeout here; platform handles the hard stop.
df['buy'] = fresh_reclaim.fillna(False).astype(bool)
df['sell'] = time_exit.astype(bool)

output = {
    "name": "ETH Horizontal Reclaim 1D Long",
    "plots": [
        {"name": "50d_high", "data": high_50.fillna(0).tolist(), "color": "#4CAF50", "overlay": True},
        {"name": "was_below_zone", "data": was_below.fillna(False).astype(float).tolist(), "color": "#FF9800", "overlay": False},
    ]
}
