# Factor: 200W MA Mechanical Buy
# Source: emg_022_200w_mechanical_buy (IvanOnTech) — IC=+0.158 in crypto-kol-quant
# Faithful port of capabilities/emerged.py:134-141.
# Sibling of emg_029: tighter band (±5% vs ±8%), higher score (0.7 vs 0.6).
#
# ARCHIVED 2026-05-04: redundant with factor_200w_value_zone.py (same indicator,
# triggers are a strict subset). Use factor_200w_value_zone.py with --zone_pct=0.05
# if you specifically want the tighter band.

# @param near_pct float 0.05

import pandas as pd
import numpy as np

df = df.copy()

near_pct = float(params.get('near_pct', 0.05))

ma_200w = df['close'].rolling(window=1400, min_periods=200).mean()
near = (df['close'] - ma_200w).abs() / ma_200w < near_pct

df['mechanical_buy_score'] = np.where(near, 0.7, 0.0)

output = {
    "name": "Factor 200W Mechanical Buy",
    "plots": [
        {"name": "MA200W", "data": ma_200w.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "mechanical_buy_score", "data": df['mechanical_buy_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
