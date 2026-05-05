"""
Strategy: btc_monthly_open_4h_long
Thesis:   Monthly open as structural anchor on 4H BTC — enter when price breaks >8% above
          monthly open with strong momentum, exit when it fades back to ~2.5% above.
          Hypothesis: monthly open is an institutional reference level (CME futures monthly
          settlement, monthly options expiration, end-of-month rebalancing all reset on the
          1st), creating a structural anchor analogous to BNB's weekly open.
          Hysteresis + time cap mirror the champion strategy architecture exactly.
Built on: factors/factor_ohlc_anchor.py (concept adapted to monthly timeframe)
Status:   archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Adapts kol_ohlc_anchor_4h_long_hysteresis.py from weekly to monthly open.
                    Hysteresis: entry 0.15 (~8% above monthly open), exit 0.05 (~2.5% above).
                    Monthly open = first 4H bar of each calendar month. 40-bar timeout (1 week).
                    Tested on BTC (institutional futures/options calendar). Direct champion analog.
  2026-05-06  run   BTC 4H IS: n=1737 ❌ OOS Sharpe -8.70. ETH IS: n=2069 ❌ OOS -5.38.
                    BNB 4H IS: n=1806 ❌ OOS -5.49. All three catastrophically bad.
                    (log: 2026-05-06)
  2026-05-06  note  ABANDONED. Root cause: monthly open anchor + 40-bar timeout generates
                    churn — when price stays >8% above monthly open (common across a full month
                    of bull market), every time exit immediately re-enters. n=1737 IS on 5 years
                    means ~29 trades/month. The weekly anchor avoids this because weekly moves
                    rarely sustain 8% above weekly open for the full 30-bar hold. Monthly dynamics
                    are fundamentally different. The institutional monthly cycle hypothesis is
                    wrong — monthly open is not a watched structural level the way BNB's weekly
                    open is. Strategy line closed.
"""

# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param entry_threshold float 0.15
# @param exit_threshold float 0.05
# @param max_hold_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

entry_threshold = float(params.get('entry_threshold', 0.15))
exit_threshold = float(params.get('exit_threshold', 0.05))
max_hold_bars = int(params.get('max_hold_bars', 40))

# Monthly open: first bar of each calendar month
if 'time' in df.columns:
    dt = pd.to_datetime(df['time'])
    month_period = dt.dt.to_period('M')
else:
    dt = df.index
    month_period = dt.to_period('M')

month_period = pd.Series(month_period.astype(str), index=df.index)
is_month_start = month_period != month_period.shift(1).fillna(month_period.iloc[0])

monthly_open = df['open'].where(is_month_start).ffill()
pct_diff = (df['close'] - monthly_open) / monthly_open.replace(0, np.nan)
score = (np.tanh(pct_diff * 5) * 0.4).fillna(0.0)

# Hysteresis: same logic as champion
above_entry = score > entry_threshold
below_exit = score < exit_threshold

raw_buy = above_entry & ~above_entry.shift(1).fillna(False)
natural_sell = below_exit & ~below_exit.shift(1).fillna(False)
time_forced_sell = raw_buy.shift(max_hold_bars).fillna(False)

df['buy'] = raw_buy.fillna(False).astype(bool)
df['sell'] = (natural_sell.fillna(False) | time_forced_sell).astype(bool)

output = {
    "name": "BTC Monthly Open Anchor 4H Long",
    "plots": [
        {"name": "MonthlyOpen", "data": monthly_open.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
        {"name": "anchor_score", "data": score.tolist(), "color": "#FFD700", "overlay": False},
    ]
}
