# @param fast_period int 20 快速均线周期
# @param slow_period int 50 慢速均线周期
# @param rsi_period int 14 RSI 周期

# @strategy stopLossPct 0.02
# @strategy takeProfitPct 0.05

import pandas as pd
import numpy as np

# 数据准备
df = df.copy()
fast_n = int(params.get('fast_period', 20))
slow_n = int(params.get('slow_period', 50))
rsi_n = int(params.get('rsi_period', 14))

# 计算均线
ma_fast = df['close'].rolling(fast_n).mean()
ma_slow = df['close'].rolling(slow_n).mean()

# 计算 RSI
delta = df['close'].diff()
gain = delta.clip(lower=0).rolling(rsi_n).mean()
loss = (-delta).clip(lower=0).rolling(rsi_n).mean()
rs = gain / loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs))
rsi = rsi.fillna(50)

# 生成买卖信号 (向量化处理)
# 金叉 + RSI 过滤
buy_signal = (ma_fast > ma_slow) & (ma_fast.shift(1) <= ma_slow.shift(1)) & (rsi < 70)
# 死叉卖出
sell_signal = (ma_fast < ma_slow) & (ma_fast.shift(1) >= ma_slow.shift(1))

df['buy'] = buy_signal.fillna(False).astype(bool)
df['sell'] = sell_signal.fillna(False).astype(bool)

# 可视化输出
output = {
    "name": "SMA_Cross_RSI_Basic",
    "plots": [
        {"name": f"MA{fast_n}", "data": ma_fast.fillna(0).tolist(), "color": "#1890ff", "overlay": True},
        {"name": f"MA{slow_n}", "data": ma_slow.fillna(0).tolist(), "color": "#ff7a45", "overlay": True}
    ]
}
