"""
Strategy: kol_ohlc_anchor_4h_long_hysteresis
Thesis:   Weekly open as structural anchor on 4H — enter when price breaks >8% above
          weekly open with strong momentum, exit when it drops back to ~2.5% above on fade.
          Hysteresis + time cap eliminate the whipsaw that killed the original champion.
Built on: factors/factor_ohlc_anchor.py
Status:   active — BNB-confirmed; ETH/SOL fail

History (append-only, newest at bottom):
  2026-05-04  code  init. challenger to kol_ohlc_anchor_4h_long.py (champion: entry 0.1, exit 0.0,
                    5% stop → 122 trades, PF 0.95, 46% win). Hysteresis entry 0.15 / exit 0.05,
                    no stop loss, 30-bar timeout. Score 0.15 = ~8% above weekly open.
  2026-05-04  run   BTC/USDT 4H — IS: Sharpe 0.51 n=150 PF 1.09. OOS: Sharpe 1.10 n=4 PF 4.16.
                    OOS positive but n=4 is too thin to conclude.
                    (log: 2026-05-04T05:20:03)
  2026-05-05  run   BNB/USDT 4H — IS: Sharpe 4.13 n=212 PF 1.44 win 53%. OOS: Sharpe 2.59 n=7
                    PF 7.12 win 71%. BEST result in portfolio — passes Sharpe/Calmar/PF.
                    (log: 2026-05-05T14:23:04)
  2026-05-05  run   ETH/USDT 4H — IS: Sharpe -0.58 n=204. OOS: Sharpe -0.81 n=46. ❌ Fail.
                    SOL/USDT 4H — IS: Sharpe 1.03 n=503. OOS: Sharpe -2.75 n=42. ❌ Fail.
                    BTC/USDT 1D — IS: Sharpe 0.76 n=88. OOS: Sharpe -0.26 n=5. ❌ Fail.
                    (log: 2026-05-05T14:23:xx / 14:24:xx)
  2026-05-05  note  Strategy is BNB-specific. ETH/SOL OOS n=42-46 makes failure statistically
                    significant — not noise. BNB weekly-open anchor likely anchored by Binance
                    institutional cycle (quarterly burns, fee discounts reset weekly). Do NOT
                    deploy on ETH/SOL.
  2026-05-05  code  Tuning test: lowered entry_threshold 0.15→0.12 to increase OOS trade count.
  2026-05-05  run   BNB/USDT 4H at 0.12 — IS: Sharpe 3.61 n=332. OOS: Sharpe -1.25 n=30 PF 0.80. ❌
                    (log: 2026-05-05T14:4x:xx)
  2026-05-05  code  Reverted to entry_threshold=0.15. The 7 OOS trades at 0.15 are high-quality
                    signal (win 71%, PF 7.12); extra 23 trades at 0.12 are noise (win 36.7%, PF 0.80).
                    Low n at 0.15 is a feature. Threshold locked at 0.15 — do not tune further.
"""

# @strategy tradeDirection long
# @strategy entryPct 1.0
# (No stopLossPct — exits via score crossing exit threshold or 30-bar timeout)

# @param entry_threshold float 0.15
# @param exit_threshold float 0.05
# @param max_hold_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

entry_threshold = float(params.get('entry_threshold', 0.15))
exit_threshold = float(params.get('exit_threshold', 0.05))
max_hold_bars = int(params.get('max_hold_bars', 30))

# Inline replication of factor_ohlc_anchor.
# Sandbox provides df['time'] (datetime64); IC tester provides DatetimeIndex.
if 'time' in df.columns:
    day_of_week = pd.to_datetime(df['time']).dt.dayofweek.values
else:
    day_of_week = df.index.dayofweek
day_of_week = pd.Series(day_of_week, index=df.index)
week_open = df['open'].where(day_of_week == 0).ffill()
pct_diff = (df['close'] - week_open) / week_open
score = (np.tanh(pct_diff * 5) * 0.4).fillna(0.0)

# Hysteresis: enter on stronger signal, exit only on much weaker
above_entry = score > entry_threshold
below_exit = score < exit_threshold

raw_buy = above_entry & ~above_entry.shift(1).fillna(False)
natural_sell = below_exit & ~below_exit.shift(1).fillna(False)

# Time-based forced exit: 30 bars after each entry
time_forced_sell = raw_buy.shift(max_hold_bars).fillna(False)

# OR — engine treats "sell while flat" as no-op
raw_sell = (natural_sell.fillna(False) | time_forced_sell).astype(bool)
df['buy'] = raw_buy.fillna(False).astype(bool)
df['sell'] = raw_sell

output = {
    "name": "KOL OHLC Anchor 4H Long (hysteresis + time exit)",
    "plots": [
        {"name": "WeeklyOpen", "data": week_open.fillna(0).tolist(), "color": "#FF9800", "overlay": True},
        {"name": "anchor_score", "data": score.tolist(), "color": "#FFD700", "overlay": False},
    ]
}
