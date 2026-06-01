# Stockchatu 交易策略全景与评估

资料基础：

- 逐集人工审计：`/Users/cc/Documents/GitHub/QuantDinger/my-research/log/journals/2026-05-31-stockchatu-manual-audit.md`
- 去重账户曲线：`/Users/cc/Documents/GitHub/QuantDinger/my-research/log/journals/2026-05-31-stockchatu-account-vs-trades.md`
- 主要交易明细：`/Users/cc/Documents/GitHub/QuantDinger/my-research/log/journals/2026-05-31-stockchatu-trade-ledger-detailed.md`
- 原始 transcript：`/Users/cc/Documents/GitHub/hello-web-reader/output/stockchatu/transcripts`

## 一句话总结

他的核心不是单纯看好 NVDA、ORCL 或 ASTS，而是：

> 用宏观/主题/事件找方向，用期权链 OI、gamma、max pain 找点位，再用高杠杆期权结构放大账户。

真正让账户大幅跳跃的部分，大多来自高信心、高杠杆、接近 all-in 或 all-in 的期权交易；这和他口头上强调的风控并不一致。

## 策略全景

### 1. 催化剂单腿 Call

代表交易：

- NVDA 122C：3.45 买、14.55 卖，账户 4,000 -> 16,000。
- NVDA 5/1 180C：338 张，2.94 买、4.6 卖。
- NVDA 4/15 180C：429 张，5.2 买、7.65 卖。
- ORCL call：近 2,000 张，2.23 买、4.5 卖，账户 440,000 -> 880,000。
- ASTS call：满仓单腿 call，账户 880,000 -> 1,350,000。

策略本质：

- 事件或主题催化出现后，用单腿 call 捕捉方向和 gamma。
- 对方向和时机要求很高，收益弹性最大。
- 失败时会因为 theta、IV crush 或方向小错造成巨大损失。

评估：

- 这是他最大获利来源之一，但不可直接复制。
- 若要策略化，应优先改成 call spread 或小仓位 call，而不是 all-in 单腿 call。

### 2. Gamma Squeeze / OI Strike Breakout

代表交易：

- NVDA 160C：根据 160 call OI、160 卖单和突破预期，买 7/18 160C。
- NVDA 170/172.5 区域：用 170C OI 和盈亏平衡推导 172.5。
- NVDA 180/185/187.5 阶梯：用 call OI 阶梯推演连环 squeeze。
- ASTS 100C/105C：put/call ratio 0.22，100C/105C 各 1 万多张 OI。

策略本质：

- 观察某个到期日的 call OI 是否集中在关键 strike。
- 若股价接近并突破该 strike，预期做市商买正股对冲，形成 gamma squeeze。
- 下一个 OI strike 可能成为下一段目标。

评估：

- 这是他最有研究价值的核心 edge。
- 但 OI 不等于做市商一定 short gamma；如果 OI 方向、持有人结构或对冲状态判断错，结论会反过来。
- 真正系统化需要 options chain、OI by strike、volume、IV、dealer gamma proxy。

### 3. Max Pain / 做市商杀期权

代表交易：

- NVDA 180/182.5 bear call spread。
- NVDA 190/192.5 bear call spread。
- NVDA 177.5 附近 0DTE butterfly。

策略本质：

- 如果某些热门 call strike 难以突破，股价可能被压在该 strike 下方，让大量 call 到期归零。
- 用 bear call spread 或 butterfly 表达“不会超过某价位”或“会收敛到某点位”。

评估：

- 这是他从单纯买 call 进化到结构化期权的重要部分。
- 可模拟性比 all-in call 更高。
- 但它高度依赖到期周路径，隔夜事件会造成大幅逆风。

### 4. Vertical Spread

代表交易：

- NVDA 175/180 bull call spread：600 组，2.56 买，卖出总额 277,000。
- NVDA 185/187.5 bull call spread：1,800 组，1.8/1.9 买，2.45 卖，账户 280,000 -> 440,000。
- NVDA 170/172.5 put vertical：成本/权利金口径 0.54，账户到 136,000。
- NVDA 180/182.5、190/192.5 bear call spread。

策略本质：

- 用价差限制最大亏损和最大收益。
- 看涨时用 bull call spread 或 bull put spread。
- 看跌/上方受限时用 bear call spread。

评估：

- 这是最适合被我们转成 paper/backtest 的部分。
- payoff 清楚，风控边界比单腿 call 好。
- 但他实盘中仍常用过大仓位，导致定义风险不等于账户风险小。

### 5. Butterfly / Broken-Wing Butterfly

代表交易：

- NVDA 167.5/172.5/175 broken-wing butterfly：成本 2.15/2.17，4.45/4.52 平仓。
- NVDA 177.5/180/182.5 财报后 butterfly。
- NVDA 165/170/175 butterfly：第 14 周导致账户 161,000 -> 80,000。
- NVDA 175/180/185 butterfly：拆腿后转 175C，再转 172.5/175 bull spread。

策略本质：

- 押注到期时正股收在某个精确点位。
- 成功时收益率高；偏离目标点过多时亏损很快。
- Broken-wing 用来改变上下行风险形状。

评估：

- 技术含量高，但容错低。
- 第 14 周失败说明：如果方向是看跌，却使用窄区间横盘 butterfly，跌太多也会亏。
- 如果要系统化，只适合作为小仓位事件策略，不适合作为主仓位。

### 6. 基本面 / 主题 Thesis

代表主题：

- NVDA：AI 算力、GPU、CUDA、数据中心。
- ORCL：OCI、RPO、AI 数据中心资本开支被市场错杀。
- ASTS：卫星直连手机、SpaceX/Starlink IPO proxy、太空板块资金流。
- MSTR/BTC、AXTI、太空板块、软件股等。

策略本质：

- 用主题和基本面筛选标的。
- 真正交易时仍需叠加技术面、期权链和事件。

评估：

- 主题研究提供 universe，不直接等于交易信号。
- ASTS 和 ORCL 是主题 thesis 成功转成实盘获利的例子。
- AXTI、太空 ETF、MSTR 等多数内容是研究/建议，不能计入作者账户收益。

### 7. 风控与心理

他口头原则：

- 97% 正股，3% 期权。
- 小资金可以高风险，大资金不能 all-in options。
- 事前设定止盈、止损。
- 空仓也是策略。
- 财报和周末隔夜风险要主动降杠杆。

实际行为：

- 多次全仓或接近全仓期权。
- META 末日期权 all-in 输光。
- ASTS all-in call 收官大赚。
- ORCL、NVDA 高额段都带明显 all-in 风格。

评估：

- 他知道正确风控，但实盘挑战经常为了账户跃迁和内容张力违反纪律。
- 这是最不能复制的部分。

## 真正赚钱的核心来源

按实际账户贡献：

1. NVDA 是反复赚钱的主引擎：从 4,000 到 280,000 的主体收益来自 NVDA call、spread、butterfly。
2. ORCL 是最大单笔跳跃之一：440,000 -> 880,000。
3. ASTS 是收官核心大赚：880,000 -> 1,350,000。
4. OI / gamma / max pain 是贯穿 NVDA、ORCL、ASTS 的共同框架。

所以核心不是某一只股票，而是：

> 事件方向 + 期权链点位 + 高杠杆期权表达。

## 最大失败案例

1. META 末日期权 all-in：明确爆仓/输光，但缺金额、strike、张数、成本。
2. NVDA 第 14 周 butterfly：账户 161,000 -> 80,000。
3. NVDA 第 2 周 132C FOMO：16,000 -> 约 7,200。
4. NVDA 财报 140C：约 7,200 -> 4,000，方向一度对但 IV crush。
5. DeepSeek / tariff 阶段重仓 NVDA shares + calls：真实风险经历，但金额不可审计。

共同问题：

- 仓位太大。
- 期限太短。
- 方向和工具不匹配。
- 把长期 thesis 用短期期权表达。
- 没有机械止损。

## 我的总体评估

有价值的部分：

- 他会等待事件催化，不是每天乱交易。
- 他会用 options chain 找关键价位，而不是只看 K 线。
- 他会根据情境切换工具：call、spread、butterfly、sell put。
- 他能把市场情绪、散户 FOMO、恐慌、做市商对冲结合起来。

危险的部分：

- 大量收益来自 all-in / 接近 all-in，不是稳健 edge。
- 许多大交易缺完整合约字段，不能独立复核。
- 叙事后验成分高，尤其是赚钱后的解释很完整，亏损时归因于人性和上头。
- 最大风险是期限错配：META 就是方向可能长期对，但末日期权活不到长期。

结论：

> 他的策略有研究价值，但原始做法不能直接复制。应保留事件、期权链、结构化表达，删除 all-in、末日期权梭哈、靠信念扛单。

## 如果要在 QuantDinger 转成策略

### Signal Layer

保留以下信号：

- 事件催化：财报、政策、地缘、IPO、订单、行业资金流。
- 正股位置：趋势、支撑阻力、VWAP、KDJ、RSI、Bollinger。
- 期权链：OI by strike、call wall、put wall、put/call ratio、volume、IV。
- 市场状态：VIX、恐慌成交量、获利筹码比例、订单流。

### Structure Layer

不同情境用不同结构：

- 高信心趋势：优先 call spread，而不是 all-in call。
- 接近关键 gamma strike：小仓位 call 或 call spread。
- 判断上方受限：bear call spread。
- 判断下方支撑：bull put spread。
- 判断到期点位收敛：小仓位 butterfly。
- 长期主题：正股或 LEAPS，不用末日期权。

### Risk Wrapper

必须加的限制：

- 单笔最大亏损固定。
- 期权仓位上限 3%-10%。
- 禁止全仓末日期权。
- 财报前后单独处理 IV crush。
- 到达目标点强制减仓/止盈。
- 事件未落地前限制隔夜仓位。

## 推荐研究优先级

1. NVDA OI / gamma breakout + call spread。
2. NVDA max pain / bear call spread。
3. NVDA bull put spread / wheel-like income。
4. NVDA butterfly 点位收敛，小仓位研究。
5. ORCL / ASTS 事件型单腿 call 改造成 defined-risk call spread。
6. META 爆仓案例做成风控反例，不作为策略。

