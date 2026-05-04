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
# True Range
tr1 = df['high'] - df['low']
tr2 = abs(df['high'] - df['close'].shift(1))
tr3 = abs(df['low'] - df['close'].shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

atr = tr.rolling(window=kc_length).mean()
upper_kc = ma + (kc_mult * atr)
lower_kc = ma - (kc_mult * atr)

# Squeeze Condition (BB completely inside KC)
squeeze_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
df['vol_squeeze_on'] = squeeze_on.astype(int)

# Expansion Direction (simple momentum proxy: current close vs N periods ago)
momentum = df['close'] - df['close'].shift(bb_length)
df['vol_expansion_dir'] = np.where(momentum > 0, 1, -1)

# Output for visualization
output = {
    "name": "Factor Volatility Squeeze",
    "plots": [
        {"name": "Squeeze_On", "data": df['vol_squeeze_on'].tolist(), "color": "#FF5252", "overlay": False}
    ]
}
