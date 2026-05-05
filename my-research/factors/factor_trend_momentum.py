"""
Factor:     trend_momentum
Hypothesis: MA crossover (fast/slow) combined with RSI relative to 50 produces a continuous
            score that captures directional momentum strength. High positive = strong uptrend;
            high negative = strong downtrend.
Source:     own composition. MA-RSI composite is a standard quant building block.
Status:     active

History (append-only, newest at bottom):
  2026-05-06  code  init. trend_score = clip(MA%diff*500, -50, 50) + (RSI - 50). Range -100 to +100.
  2026-05-06  run   BTC/USDT 4H IC — IS 30d: IC +0.001. OOS 30d: IC +0.001 (p=0.96). Near zero.
                    (log: 2026-05-06)
  2026-05-06  note  No predictive edge at any horizon. IC ~0 IS and OOS. The MA+RSI composite
                    is not informative for 30d BTC returns. Keeping active as it may be useful
                    as a regime overlay in composite strategies, but useless standalone.
"""

# @param ma_fast int 10
# @param ma_slow int 50
# @param rsi_period int 14

import pandas as pd
import numpy as np

df = df.copy()

fast_len = int(params.get('ma_fast', 10))
slow_len = int(params.get('ma_slow', 50))
rsi_period = int(params.get('rsi_period', 14))

# Moving Averages
ma_fast = df['close'].rolling(window=fast_len).mean()
ma_slow = df['close'].rolling(window=slow_len).mean()

# MA Score (-50 to +50)
ma_diff = (ma_fast - ma_slow) / ma_slow * 100
ma_score = np.clip(ma_diff * 5, -50, 50)

# RSI Score (-50 to +50)
delta = df['close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
rsi_score = rsi - 50

# Total Trend Score (-100 to +100)
df['trend_score'] = ma_score + rsi_score

# Output for visualization
output = {
    "name": "Factor Trend Momentum",
    "plots": [
        {"name": "Trend_Score", "data": df['trend_score'].fillna(0).tolist(), "color": "#1890ff", "overlay": False}
    ]
}
