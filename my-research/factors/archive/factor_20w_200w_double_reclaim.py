"""
Factor:     double_reclaim_20w_200w
Hypothesis: Simultaneously reclaiming both the 20-week and 200-week MA (after being below either)
            signals a structural bull-market re-entry — the highest-timeframe supply has flipped
            to demand. Expected to produce rare but very high-quality long entries.
Source:     emg_028_20w_200w_double_reclaim (LedgerStatus). IC=+0.068 reported in crypto-kol-quant.
            Port of capabilities/emerged.py:143-152.
Status:     archived

History (append-only, newest at bottom):
  2026-05-06  code  init. Fires when close > MA20W AND close > MA200W AND 3 bars ago was below either.
                    Score = 0.75 on trigger bar, 0 otherwise. Very sparse (few events per cycle).
  2026-05-06  run   BTC/USDT 1D — IS 30d: hit 71.1% n=45 avg +9.50% Sharpe +0.63 ✓
                    OOS 30d: hit 16.7% n=6 avg -10.73% Sharpe -1.09 ❌ REVERSED.
                    (log: 2026-05-06)
  2026-05-06  note  ARCHIVED. Identical failure pattern to htf_reclaim_retest: strong IS in
                    bull-market data (2019-2025) but completely reversed in 2025-26 distribution
                    phase. n=6 OOS all moved against the signal. The 200W MA reclaim concept
                    is a once-per-cycle event that doesn't generalize across regimes.
"""

import pandas as pd
import numpy as np

df = df.copy()

# 20 weeks = 140 daily bars; 200 weeks = 1400 daily bars
ma_20w = df['close'].rolling(window=140, min_periods=50).mean()
ma_200w = df['close'].rolling(window=1400, min_periods=200).mean()

above_both = (df['close'] > ma_20w) & (df['close'] > ma_200w)
was_below_either = (df['close'].shift(3) < ma_20w.shift(3)) | (df['close'].shift(3) < ma_200w.shift(3))
trig = above_both & was_below_either

df['double_reclaim_score'] = np.where(trig.fillna(False), 0.75, 0.0)

output = {
    "name": "Factor 20W+200W Double Reclaim",
    "plots": [
        {"name": "MA20W", "data": ma_20w.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "MA200W", "data": ma_200w.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "double_reclaim_score", "data": df['double_reclaim_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
