"""
Factor:     volatility_squeeze
Hypothesis: When Bollinger Bands compress inside Keltner Channels (volatility squeeze), a
            breakout in the direction of momentum marks the start of an impulsive expansion.
            The squeeze_breakout_score fires only on the release bar, biasing long if momentum
            is positive and short if momentum is negative.
Source:     John Carter / LazyBear TTM Squeeze concept; standard algo-trading setup.
            vol_squeeze_on and vol_expansion_dir are raw components; squeeze_breakout_score
            is the composite event signal used by the event tester and strategies.
Status:     active

History (append-only, newest at bottom):
  2026-05-06  code  init. BB(20,2) inside KC(20,1.5). Composite squeeze_breakout_score fires on
                    squeeze release bar: +0.7 if momentum > 0 (long), -0.7 if momentum < 0 (short).
"""

# @param bb_length int 20
# @param bb_mult float 2.0
# @param kc_length int 20
# @param kc_mult float 1.5

import pandas as pd
import numpy as np

df = df.copy()

bb_length = int(params.get('bb_length', 20))
bb_mult = float(params.get('bb_mult', 2.0))
kc_length = int(params.get('kc_length', 20))
kc_mult = float(params.get('kc_mult', 1.5))

# Bollinger Bands
basis = df['close'].rolling(window=bb_length).mean()
dev = bb_mult * df['close'].rolling(window=bb_length).std()
upper_bb = basis + dev
lower_bb = basis - dev

# Keltner Channels
ma = df['close'].rolling(window=kc_length).mean()
tr1 = df['high'] - df['low']
tr2 = (df['high'] - df['close'].shift(1)).abs()
tr3 = (df['low'] - df['close'].shift(1)).abs()
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
atr = tr.rolling(window=kc_length).mean()
upper_kc = ma + (kc_mult * atr)
lower_kc = ma - (kc_mult * atr)

# Squeeze: BB completely inside KC
squeeze_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
df['vol_squeeze_on'] = squeeze_on.astype(int)

# Momentum direction
momentum = df['close'] - df['close'].shift(bb_length)
df['vol_expansion_dir'] = np.where(momentum > 0, 1, -1)

# Composite event: fires only on squeeze-release bar
squeeze_release = squeeze_on.shift(1).fillna(False).astype(bool) & ~squeeze_on.fillna(False).astype(bool)
df['squeeze_breakout_score'] = np.where(
    squeeze_release & (momentum > 0),  0.7,
    np.where(
    squeeze_release & (momentum < 0), -0.7, 0.0)
)

output = {
    "name": "Factor Volatility Squeeze",
    "plots": [
        {"name": "Squeeze_On", "data": df['vol_squeeze_on'].tolist(), "color": "#FF5252", "overlay": False},
        {"name": "squeeze_breakout_score", "data": df['squeeze_breakout_score'].tolist(), "color": "#FFD700", "overlay": False},
    ]
}
