# @param scale_factor float 1.0

import pandas as pd

df = df.copy()

# Since we gracefully injected the alternative data via ProBacktestService (Data Hijacking),
# the 'funding_rate' column is already beautifully merged and forward-filled in our raw `df`.

if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

scale = float(params.get('scale_factor', 1.0))
df['factor_funding'] = df['funding_rate'] * scale
