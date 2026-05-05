# Factor: 200-Week Value Zone
# Source: emg_029_200w_value_zone (LedgerStatus) — IC=+0.178 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:154-161 — outputs score only, no buy/sell.
#
# VALIDATION (2026-05-04, factor_event_tester.py)
#   Best TF:     1D       (4H/1H lose hit rate to ~50%; 1400-bar window != 200 weeks at lower TF)
#   Best regime: late_bear (cycle days 720+ post-halving) — IC=+0.281 in this phase
#   Long hit:    67.5% / avg fwd +7.87% over 30 bars (n=308 IS triggers)
#   OOS:         0 triggers (current phase = distribution; factor correctly not firing)
#   Verdict:     ✅ pass — sparse but strong in target regime; deploy as portfolio component, not standalone
#
# Format note: VALIDATION block is free-text for humans + agents; not parsed by tooling.

# @param zone_pct float 0.08

import pandas as pd
import numpy as np

df = df.copy()

zone_pct = float(params.get('zone_pct', 0.08))

ma_200w = df['close'].rolling(window=1400, min_periods=200).mean()
pct_from_ma_200w = (df['close'] - ma_200w) / ma_200w

df['value_zone_score'] = np.where(np.abs(pct_from_ma_200w) < zone_pct, 0.6, 0.0)

output = {
    "name": "Factor 200W Value Zone",
    "plots": [
        {"name": "MA200W", "data": ma_200w.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "value_zone_score", "data": df['value_zone_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
