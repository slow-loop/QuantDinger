"""
Factor:     htf_reclaim_retest
Hypothesis: Reclaiming the 20-week MA then retesting it as support (within 2%) confirms trend
            resumption — the MA transitions from resistance to support and represents a
            high-conviction re-entry for macro trend followers.
Source:     emg_007_htf_reclaim_retest (ColdBloodShill). IC=+0.053 reported in crypto-kol-quant.
            Port of capabilities/emerged.py:54-63.
Status:     archived

History (append-only, newest at bottom):
  2026-05-05  code  init. faithful port. fires when: above 20W MA now + was below 5 bars ago
                    + today's low within 2% of 20W MA.
  2026-05-06  run   BTC/USDT 1D — IS 30d: hit 69.2% n=39 avg +7.95% Sharpe +0.46 ✓
                    OOS 30d: hit 0.0% n=4 avg -14.26% Sharpe -1.53 ❌ REVERSED
                    OOS 7d: hit 40% n=5. All 4 OOS 30d triggers were losers.
                    (log: 2026-05-06)
  2026-05-06  note  ARCHIVED. OOS completely reversed at 30d horizon — 0% hit, n=4 all losers.
                    Factor likely encoded a 2019-2024 bull-market reclaim dynamic that doesn't
                    hold in 2025-26. The 20W MA retest confirmation is too slow for current
                    volatility. Archived.
"""

import pandas as pd
import numpy as np

df = df.copy()

# 20 weeks = 140 daily bars
ma_20w = df['close'].rolling(window=140, min_periods=50).mean()

above_now = df['close'] > ma_20w
was_below = df['close'].shift(5) < ma_20w.shift(5)
# Retest: today's low touched within 2% of the 20W MA
retest = (df['low'] - ma_20w).abs() / df['close'] < 0.02

trig = above_now & was_below & retest

df['htf_reclaim_score'] = np.where(trig.fillna(False), 0.6, 0.0)

output = {
    "name": "Factor HTF Reclaim Retest",
    "plots": [
        {"name": "MA20W", "data": ma_20w.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "htf_reclaim_score", "data": df['htf_reclaim_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
