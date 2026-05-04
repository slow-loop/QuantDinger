# @strategy stopLossPct 0.05
# @strategy trailingEnabled true
# @strategy trailingStopPct 0.03
# @strategy trailingActivationPct 0.03
# @strategy tradeDirection long
# @strategy entryPct 0.50

# @param trend_weight float 1.0
# @param vol_weight float 1.0
# @param rev_weight float 0.5

import pandas as pd
import numpy as np

df = df.copy()

# Weights for factors
wt_trend = float(params.get('trend_weight', 1.0))
wt_vol = float(params.get('vol_weight', 1.0))
wt_rev = float(params.get('rev_weight', 0.5))

# 1. Load pure factors
# Factor 1: Trend Momentum
# Returns 'trend_score' (-100 to 100)
df_trend = call_indicator('Factor Trend Momentum', df, {'ma_fast': 10, 'ma_slow': 50, 'rsi_period': 14})
df['f_trend'] = df_trend['trend_score']

# Factor 2: Volatility Squeeze
# Returns 'vol_squeeze_on' (0/1) and 'vol_expansion_dir' (-1/1)
df_vol = call_indicator('Factor Volatility Squeeze', df, {'bb_length': 20, 'kc_length': 20})
df['f_vol_squeeze'] = df_vol['vol_squeeze_on']
df['f_vol_dir'] = df_vol['vol_expansion_dir']

# Factor 3: Mean Reversion
# Returns 'reversion_z_score' (positive=overbought, negative=oversold)
df_rev = call_indicator('Factor Mean Reversion', df, {'lookback': 20})
df['f_reversion'] = df_rev['reversion_z_score']

# 2. Factor Synthesis (Composite Score)
df['buy'] = False
df['sell'] = False

# Synthesizing the buy logic:
buy_condition = (
    # Trend is moderately strong
    (df['f_trend'] > 20) & 
    # Either a volatility expansion to the upside is starting OR we are steadily trending
    (
        ((df['f_vol_squeeze'].shift(1) == 1) & (df['f_vol_squeeze'] == 0) & (df['f_vol_dir'] == 1)) | 
        (df['f_trend'] > 40)
    ) &
    # Not extremely overbought (z-score < 2.5)
    (df['f_reversion'] < 2.5)
)

# Sell Condition (Risk off / Reversion):
sell_condition = (
    # Trend completely breaks down
    (df['f_trend'] < -10) |
    # Extremely overbought, snap back expected
    (df['f_reversion'] > 3.0)
)

df['buy'] = buy_condition
df['sell'] = sell_condition

# Plots for UI
output = {
    "name": "Composite Alpha Strategy",
    "plots": [
        {"name": "Buy Signal", "data": df['buy'].astype(int).tolist(), "type": "scatter", "color": "#00FF00"},
        {"name": "Sell Signal", "data": df['sell'].astype(int).tolist(), "type": "scatter", "color": "#FF0000"}
    ]
}
