# @param fast_period int 20 快速均线周期
# @param slow_period int 50 慢速均线周期
# @param rsi_period int 14 RSI 周期
# @param adx_period int 14 ADX 周期
# @param adx_threshold int 20 降低门槛

import pandas as pd
import numpy as np

# 数据准备
df = df.copy()
fast_n = int(params.get('fast_period', 20))
slow_n = int(params.get('slow_period', 50))
rsi_n = int(params.get('rsi_period', 14))
adx_n = int(params.get('adx_period', 14))
adx_thr = int(params.get('adx_threshold', 20))

# 1. 基础指标
ma_fast = df['close'].rolling(fast_n).mean()
ma_slow = df['close'].rolling(slow_n).mean()

delta = df['close'].diff()
gain = delta.clip(lower=0).rolling(rsi_n).mean()
loss = (-delta).clip(lower=0).rolling(rsi_n).mean()
rs = gain / loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs)).fillna(50)

# 2. ADX
tr = pd.concat([df['high'] - df['low'], (df['high'] - df['close'].shift()).abs(), (df['low'] - df['close'].shift()).abs()], axis=1).max(axis=1)
atr = tr.rolling(adx_n).mean()
plus_dm = df['high'].diff().clip(lower=0)
minus_dm = (df['low'].shift(1) - df['low']).clip(lower=0)
plus_di = 100 * (plus_dm.rolling(adx_n).mean() / atr)
minus_di = 100 * (minus_dm.rolling(adx_n).mean() / atr)
dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
adx = dx.rolling(adx_n).mean()

# === V3.1 核心逻辑 ===
buy_signal = (
    (ma_fast > ma_slow) & (ma_fast.shift(1) <= ma_slow.shift(1)) & 
    (rsi < 70) & (df['close'] > ma_slow) & 
    (adx > adx_thr)
)

sell_signal = (ma_fast < ma_slow) & (ma_fast.shift(1) >= ma_slow.shift(1))

df['buy'] = buy_signal.fillna(False).astype(bool)
df['sell'] = sell_signal.fillna(False).astype(bool)

output = {
    "name": "SMA_Cross_RSI_ADX_Trend_Filter",
    "plots": [
        {"name": "ADX", "data": adx.fillna(0).tolist(), "color": "#eb2f96", "overlay": False}
    ]
}
