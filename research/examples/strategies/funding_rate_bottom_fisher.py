# @strategy stopLossPct 0.08
# @strategy trailingEnabled true
# @strategy trailingStopPct 0.05
# @strategy trailingActivationPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 0.50

# @param funding_threshold float -0.0001
# @param z_score_threshold float -1.5
# @param z_lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

# ==========================================
# 1. 因子准备 (Factor Composition — Data Hijacking 模式)
# ==========================================

# 因子 1: 资金费率
# 由 AltDataBacktestService (Runner) 在 _fetch_kline_data() 阶段
# 自动合并 Binance funding_rate 到 df，已经 ffill + fillna(0)。
# 如果在非 Alt-Data Runner 下执行（如 Web UI），优雅降级为 0。
if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

# 因子 2: 均值回归 Z-Score（内嵌计算，无外部依赖）
z_lookback = int(params.get('z_lookback', 20))
_mean = df['close'].rolling(window=z_lookback).mean()
_std = df['close'].rolling(window=z_lookback).std()
df['z_score'] = ((df['close'] - _mean) / _std).fillna(0)

# ==========================================
# 2. 抄底共振逻辑 (Bottom-Fishing Logic)
# ==========================================
funding_threshold = float(params.get('funding_threshold', -0.0001))
z_score_threshold = float(params.get('z_score_threshold', -1.5))

# 买入条件 (超级共振抄底)：
# 1. Z-Score 极度负值：价格短线发生剧烈暴跌（跌破均线 N 个标准差，带血筹码）
# 2. 资金费率跌破负数：散户群体极度恐慌做空（酝酿了充足的逼空爆仓燃料）
buy_condition = (
    (df['z_score'] < z_score_threshold) & 
    (df['funding_rate'] <= funding_threshold)
)

# 卖出条件：
# 当资金费率重新转为明显正数（散户又开始做多），或者 Z-Score 回到 0（回到均线）
sell_condition = (
    (df['funding_rate'] > abs(funding_threshold) * 1.5) |
    (df['z_score'] > 0)
)

df['buy'] = buy_condition
df['sell'] = sell_condition

# ==========================================
# 3. 可视化输出
# ==========================================
output = {
    "name": "Blood & Squeeze Bottom Fisher",
    "plots": [
        {"name": "Z-Score", "data": df['z_score'].tolist(), "color": "#00FFFF", "overlay": False},
        {"name": "Funding Rate", "data": df['funding_rate'].tolist(), "color": "#FF9900", "overlay": False},
        {"name": "Buy Signal", "data": df['buy'].astype(int).tolist(), "type": "scatter", "color": "#00FF00"},
        {"name": "Sell Signal", "data": df['sell'].astype(int).tolist(), "type": "scatter", "color": "#FF0000"}
    ]
}

