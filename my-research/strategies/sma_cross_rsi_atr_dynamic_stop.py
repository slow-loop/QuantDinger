# @param fast_period int 20 快速均线周期
# @param slow_period int 50 慢速均线周期
# @param rsi_period int 14 RSI 周期
# @param atr_period int 14 ATR 周期
# @param atr_multiplier float 2.5 ATR 止损倍数

# @strategy stopLossPct 0.0  # 我们在代码中动态处理止损
# @strategy takeProfitPct 0.08
# @strategy trailingEnabled true

import pandas as pd
import numpy as np

# 数据准备
df = df.copy()
fast_n = int(params.get('fast_period', 20))
slow_n = int(params.get('slow_period', 50))
rsi_n = int(params.get('rsi_period', 14))
atr_n = int(params.get('atr_period', 14))
atr_mult = float(params.get('atr_multiplier', 2.5))

# 计算均线
ma_fast = df['close'].rolling(fast_n).mean()
ma_slow = df['close'].rolling(slow_n).mean()

# 计算 RSI
delta = df['close'].diff()
gain = delta.clip(lower=0).rolling(rsi_n).mean()
loss = (-delta).clip(lower=0).rolling(rsi_n).mean()
rs = gain / loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs)).fillna(50)

# 计算 ATR (真实波幅)
high_low = df['high'] - df['low']
high_close = (df['high'] - df['close'].shift()).abs()
low_close = (df['low'] - df['close'].shift()).abs()
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
atr = tr.rolling(atr_n).mean()

# === V2 核心逻辑：入场过滤与动态止损线 ===
# 入场条件：金叉 + RSI < 70 + 价格在长线均线之上 (趋势确认)
buy_signal = (ma_fast > ma_slow) & (ma_fast.shift(1) <= ma_slow.shift(1)) & (rsi < 70) & (df['close'] > ma_slow)

# 出场条件：死叉
sell_signal = (ma_fast < ma_slow) & (ma_fast.shift(1) >= ma_slow.shift(1))

df['buy'] = buy_signal.fillna(False).astype(bool)
df['sell'] = sell_signal.fillna(False).astype(bool)

# 计算动态止损位（用于图表展示）
df['stop_price'] = df['close'] - (atr * atr_mult)

# 可视化输出
output = {
    "name": "SMA_Cross_RSI_ATR_Dynamic_Stop",
    "plots": [
        {"name": "MA20", "data": ma_fast.fillna(0).tolist(), "color": "#1890ff", "overlay": True},
        {"name": "MA50", "data": ma_slow.fillna(0).tolist(), "color": "#ff7a45", "overlay": True},
        {"name": "ATR_Stop", "data": df['stop_price'].fillna(0).tolist(), "color": "#ff4d4f", "overlay": True}
    ]
}
