# Stockchatu 交易策略抽取

资料来源：

- 人工逐集审计总报告：`/Users/cc/Documents/GitHub/QuantDinger/my-research/log/journals/2026-05-31-stockchatu-manual-audit.md`
- 原始 transcript：`/Users/cc/Documents/GitHub/hello-web-reader/output/stockchatu/transcripts`

目的：从逐集审计中抽取这个 YouTuber 反复使用的交易策略，而不是按视频顺序复述。每个策略都列出：定义、出现样本、真实交易、入场逻辑、出场/复盘、可模拟化、风险。

## 总体结构

他的交易系统不是一个单策略，而是一个多层组合：

1. 底层标的偏好：高度集中在 NVDA，外加 ORCL、ASTS、META、MSTR/BTC、AXTI、太空板块、软件股等主题。
2. 方向判断：宏观事件、AI/财报催化、地缘政治、主题资金、基本面叙事。
3. 期权链判断：open interest、call wall、put wall、max pain、gamma squeeze、做市商杀期权。
4. 表达工具：单腿 call、bull call spread、bull put spread、bear call spread、butterfly、broken-wing butterfly、wheel、risk-off puts。
5. 风控复盘：空仓、止盈、止损、拆腿、3% 期权仓位法、避免 all-in；但实盘挑战里经常违反这些纪律。

可投资化时，必须保留信号层，删除或强约束 all-in 仓位。

## 核心赚钱来源（修正版）

按“真实盈利贡献”看，ASTS 不能放在副线；它是实盘挑战最后一段的大额核心盈利来源之一。

1. NVDA 期权引擎：最反复、最系统的赚钱来源。早期账户从 4000 做到 16000、后续多次靠 NVDA call、vertical spread、butterfly、max pain/OI 结构把账户推高；它是可复用度最高的主策略。
2. ORCL 单腿 call：最大单笔跳跃之一。作者口述近 2000 张 ORCL call，2.23 买入、4.5 卖出，账户从 44 万推到 88 万左右，是高置信错杀反转 + 单腿 call 的大额案例。
3. ASTS 满仓 call：最后阶段最大/并列最大单笔跳跃。作者称在 Q1 财报前后宣布买入 ASTS，最终本周满仓 ASTS call 使账户从 88 万到 135 万，约 +47 万；这不是普通主题研究，而是挑战收官的决定性盈利腿。
4. OI/Gamma/Max-pain 框架：贯穿 NVDA、ORCL、ASTS 的共同边。真正的“方法论核心”不是某一只股票，而是用事件和主题定方向，再用期权链 OI、put/call、关键 strike 和到期路径找杠杆点。

所以如果按赚钱贡献排序，ASTS 应列为核心获利交易；如果按可复制性排序，NVDA + 期权链结构仍排第一。

## 策略 1：催化剂单腿 Call

定义：在强催化剂出现或即将出现时，直接买入近月/短期期权 call，用高 delta/gamma 捕捉快速上涨。

出现样本：

- 第 1 周：NVDA 122 call，3.45 买入，14.55 卖出，账户 4000 到 16000。
- 第 6-8 周：NVDA 146 call、155 call、160 call，多次用 call 捕捉突破。
- 第 18 周/第三季：NVDA 5月1日 180 call，338 张，2.94 买入、4.6 卖出。
- 4月8日尾盘：NVDA 4月15日 180 call，429 张，5.2 买入、7.65 卖出。
- ORCL：近 2000 张 Oracle call，2.23 买入、4.5 卖出。
- ASTS：满仓 ASTS call，账户 88 万到 135 万，约 +47 万；这是挑战收官的核心盈利腿，但缺 strike/到期日/张数/成本。

入场逻辑：

- 正催化：关税缓和、Trump 中东行、黄仁勋/迪拜订单、伊朗谈判缓和、AI Day、SpaceX/Starlink 叙事、财报前后错误定价。
- 技术确认：股价站上关键价位、出现看涨吞没、KDJ 低位金叉、放量突破。
- 期权确认：大额 call OI、put/call ratio 极低、关键 strike 可能触发 gamma squeeze。
- 情绪反向：市场恐慌、踏空、评论区悲观、获利筹码极低。

出场/复盘：

- 成功样本通常在情绪高潮或关键价位止盈，例如 NVDA 136、167、173、188.74、ORCL 180。
- 失败样本包括第 2 周 FOMO 买 132 call 后没按 137-139 计划止盈，最终回撤 55%；财报前买 140 call 方向未完全错，但 IV crush 让账户回初始本金。

可模拟化：

- 输入：标的 OHLCV、期权历史价格、到期日、strike、事件日历、OI、put/call ratio、IV。
- 规则：催化剂确认 + 价格突破 + OI 支持时买 call；触及目标价、IV crush 前、或时间价值加速衰减前出场。

主要风险：

- theta 衰减。
- IV crush。
- 隔夜/周末跳空无法止损。
- 若 all-in，方向小错也会账户腰斩。

## 策略 2：Gamma Squeeze / OI Strike Breakout

定义：观察某一到期日 call open interest 最大的 strike；若股价突破该 strike，预期做市商被迫买入正股对冲，形成 gamma squeeze。

出现样本：

- 第 8 周：NVDA 7/18 160 call，成本 2.9；依据 7/11 160 call OI 105000 张，预期突破 160 后冲 165。
- 第 9 周：7/18 170 call OI 约 13 万张，推断突破 170 后目标 172.5。
- 第 6 周：155 call OI 最大，判断突破 157.5。
- 4月8日：NVDA 180、182.5、185、190 call OI 阶梯，买 429 张 180 call。
- 4月13-17：NVDA 185/187.5 call spread，认为 call OI 清一色导致连环 squeeze。
- ASTS：100C/105C 大量 OI，配合 put/call ratio 0.22。

入场逻辑：

- 前几大 OI 集中在 call，而不是 call/put 混杂。
- 现价接近关键 call strike。
- 股价已有上行动能或事件催化。
- 下一个 strike 距离不远，容易连环触发。

出场/复盘：

- 到达下一 OI strike 或接近 squeeze 末端时止盈。
- 他常在股价到 167、188.74、199 附近止盈。

可模拟化：

- 需要 options chain OI by strike/expiry、gamma estimate、stock intraday data。
- 可建立信号：`price crosses high_call_oi_strike AND volume expansion AND call_oi_ladder_above`.

主要风险：

- OI 不等于做市商一定 short gamma。
- 如果 OI 是已对冲或客户卖 call，逻辑可能反过来。
- 临近到期时若未突破，期权迅速归零。

## 策略 3：看涨垂直价差 Bull Call Spread

定义：买低 strike call、卖高 strike call，限制最大亏损和最大收益，用于押注到期前股价高于上方 strike。

出现样本：

- 4月1日：600 组 NVDA 175/180 看涨垂直价差，均价 2.56；卖出总额 27.7 万。
- 4月13-17：1800 组 NVDA 185/187.5 call vertical spread，1.8/1.9 买入，2.45 卖出，账户到 44 万。
- 第 17 周拆腿后转 172.5/175 牛市垂直价差，成本 0.55，吃满。

入场逻辑：

- 方向明确看涨，但希望比单腿 call 更可控。
- 目标价清晰，例如 NVDA 到期大于 180、187.5、175。
- 事件催化明确：伊朗谈判、AI 合作、失业数据后反弹。

出场/复盘：

- 若股价快速越过上方 strike，提前止盈。
- 若到期价高于上方 strike，吃满最大收益。
- 他会在事件落地后按 buy the rumor, sell the news 止盈。

可模拟化：

- payoff 很清楚：最大亏损 = debit；最大收益 = spread width - debit。
- 需要入场价、出场价、到期日、strike、组数。

主要风险：

- defined risk 不等于低风险；全仓买 spread 仍可 100% 归零。
- 事件判断错误时，即使亏损有限，也是账户级灾难。

## 策略 4：看涨 Put Credit Spread / Bull Put Spread

定义：卖高 strike put、买低 strike put，收权利金；只要到期股价高于短 put strike，就取得最大收益。

出现样本：

- 第 10 周：NVDA 7/25 165/167.5 put vertical，买 165 put、卖 167.5 put，收 78 美元权利金，保证金 250，最大收益 31.2%。
- 第 10 周周五：切到 170/172.5 put vertical。
- 第 12 周：NVDA 170/172.5 put vertical，成本/权利金口径 0.54，目标收益 27.5%，周五收盘高于 172.5 吃满。

入场逻辑：

- 看涨或横盘偏多，不一定要暴涨。
- 认为关键支撑不会跌破。
- 用时间流逝和股价不跌赚钱。
- 通常配合事件后市场稳定、AI 日、FOMC 预期、max pain 回归。

出场/复盘：

- 如果短 put strike 上方稳定，持有到期吃权利金。
- 他也会在收益接近最大值时平仓并换到更高 strike 继续压榨收益。

可模拟化：

- 非常适合 paper：输入 strike、credit/debit、到期收盘价即可算 payoff。
- 需要保证金占用和 assignment 规则。

主要风险：

- 突发跳空跌破短 put。
- 继续用收到的权利金加仓会提高杠杆。
- 标的集中在 NVDA，单标的尾部风险很高。

## 策略 5：熊市 Call Credit Spread / Bear Call Spread

定义：卖低 strike call、买高 strike call，押注到期股价不会高于短 call strike。

出现样本：

- 第 11 周：NVDA 180/182.5 bear call spread，卖 180 call、买 182.5 call，周五 NVDA 收 173.72，吃满。
- 第 15 周：405 组 NVDA 180/182.5 熊市垂直价差，成本/权利金口径存在矛盾，但策略目标是低于 180。
- 第 17 周：NVDA 190/192.5 熊市垂直价差，卖 190 call、买 192.5 call，最终账户到 28 万。
- 第 14 周：175/177.5 熊市垂直价差。

入场逻辑：

- 股价接近前高或历史阻力。
- 上方 call wall 巨大。
- max pain 明显低于现价。
- 订单流显示上方卖压。
- 月末再平衡、FOMC、关税等事件可能压制上涨。

出场/复盘：

- 到期低于短 call，权利金吃满。
- 如果盘后财报/FOMO 推升股价，会出现极大浮亏。
- 第 11 周盘后 NVDA 曾到 185，后来 H20/关税等消息使其回落，最终成功。

可模拟化：

- 可用 OI/max pain + 价格拉伸信号开仓。
- 需要每笔 credit、组数、到期日和止损规则。

主要风险：

- 裸方向判断错时，即使有保护腿也会最大亏损。
- 盘后事件可能直接越过上方保护区。

## 策略 6：Max Pain / 做市商杀期权 Pin 策略

定义：预测周五到期收盘点位，让最多期权归零；围绕该点位选择卖权利金、价差或 butterfly。

出现样本：

- 第 13 周：判断 NVDA 财报后多空双杀在 180，开 177.5/180/182.5 butterfly。
- 第 17 周：180 为 OI 磁铁，开 175/180/185 butterfly。
- 第 11 周：判断 180 上方难突破，开 bear call spread。
- 车轮第二战：max pain 182.5，卖 182.5 put；下一周计划 sell 190 put。
- 财报策略：卖 2月20日到期 190 put，周五收 189.82。

入场逻辑：

- 期权 OI 明显集中。
- 到期日临近。
- 股价距离 max pain 不远。
- 没有足够强的趋势催化破坏 pin。

出场/复盘：

- 若到期收在目标附近，最大盈利。
- 若突发事件改变平衡，要止损或移动目标点位。
- 第 13 周 Marvell 财报暴雷后，目标从 180 移到 175。

可模拟化：

- 需要 options OI、max pain、expiration calendar、realized vol、event calendar。
- 可回测 weekly expiry pin probability。

主要风险：

- max pain 是结果描述，不是因果保证。
- 财报、同板块财报、宏观数据会破坏 pin。

## 策略 7：标准 Butterfly

定义：买低 strike call、卖 2 张中间 strike call、买高 strike call，押注到期价格靠近中间 strike。

出现样本：

- 175/180/185 call butterfly，成本 1.5。
- 177.5/180/182.5 call butterfly，成本 0.68。
- 172.5/175/177.5 末日 butterfly。
- 175/177.5/180 0DTE butterfly，成本 1.41。

入场逻辑：

- 已判断某个到期收盘磁吸点。
- 预期波动区间窄。
- 希望用低成本换高赔率。

出场/复盘：

- 成功时收益非常高，例如 0DTE 末日蝴蝶接近最大点。
- 失败时如果价格偏离中间 strike，可能迅速归零。
- 第 14 周 165/170/175 butterfly 因 NVDA 跌破 165 止损，账户腰斩。

可模拟化：

- payoff 明确；最重要是建仓成本、中间 strike、到期收盘。
- 需要记录是否提前平仓，而不是只看到期。

主要风险：

- 窄区间高赔率结构，容错低。
- 方向判断对但区间错，也会亏。

## 策略 8：Broken-Wing Butterfly / 破翼蝴蝶

定义：不对称 butterfly，降低成本并保留某一方向的残余收益；用于押注特定点位，同时避免股价超过目标后完全失效。

出现样本：

- 第 9 周：NVDA 7/18 167.5/172.5/175 broken-wing butterfly，买 167.5 call、卖 2 张 172.5 call、买 175 call，成本 2.15/2.17；4.45/4.52 平仓。

入场逻辑：

- 判断 NVDA 会突破 170，但收盘/流动性点位在 172.5。
- 170 call OI 最大，买卖双方盈亏平衡约 172.5。
- 希望收益集中在目标点，但股价超过 175 后仍保留小收益。

出场/复盘：

- 周五收 172.41，几乎命中目标。
- 该策略被作者用来说明高级期权结构优于裸 call。

可模拟化：

- 高度可模拟。输入三腿结构、成本、平仓价、到期价即可。

主要风险：

- 结构比普通 call 难管理。
- 如果价格过快穿越或未到目标点，盈亏非线性。

## 策略 9：拆腿与临场重构

定义：当原期权组合进入亏损或市场条件变化时，不是整体平仓，而是拆掉部分腿，留下有利腿，再重构新组合。

出现样本：

- 第 17 周：175/180/185 butterfly 亏近 52000；平 180/185 两腿，留下并加仓 175 call；随后平 175 call，转 172.5/175 bull spread。
- 第 13 周：180 butterfly 开局失败后止损，反手开 172.5/175/177.5 末日 butterfly。
- 第 10 周：原 165/167.5 put spread 接近吃满后，换到 170/172.5 put spread。

入场/调整逻辑：

- 原策略 thesis 部分失效，但方向或新目标仍可交易。
- 流动性点位发生移动，例如 180 移到 175。
- 先锁定或释放一部分资金，再开新结构。

出场/复盘：

- 成功样本是亏损转盈利，第 17 周从亏 5 万到赚。
- 失败样本是第 14 周看跌却叠加错误 butterfly，最终腰斩。

可模拟化：

- 需要状态机回测，不是单笔 payoff。
- 每个时间点记录每条腿的价格、delta、theta、保证金。

主要风险：

- 临场重构容易变成加倍下注。
- 没有严格规则会放大主观冲动。

## 策略 10：Wheel Strategy / 车轮策略

定义：围绕愿意长期持有的股票循环卖 cash-secured put、被指派接股、卖 covered call，收取权利金。

出现样本：

- 回归 NVDA：卖 1 张 2月6日到期 NVDA 185 put，权利金 778，保证金 18500。
- 车轮第二战：卖 182.5 put，到期 NVDA 收 182.81，接近安全；下一周计划卖 190 put。
- Q&A 中明确把 wheel 作为止盈/收租方式。

入场逻辑：

- 标的是愿意长期持有的好公司。
- 股价跌到吸引区间。
- max pain 或 OI 显示股价可能回归目标 strike。
- 不是追求一夜暴富，而是现金流和成本管理。

出场/复盘：

- 如果未跌破 strike，收权利金。
- 如果被指派，持有正股，再卖 covered call。
- covered call 被行权则卖股并重新卖 put。

可模拟化：

- 很适合先做 paper。
- 需要期权链、assignment、保证金、正股持仓、covered call 出场规则。

主要风险：

- 本质是长期持股风险，暴跌时会接到下跌中的股票。
- covered call 可能卖飞大涨。
- 集中在 NVDA 时，单标的风险高。

## 策略 11：财报 / IV Crush / 波动率交易

定义：围绕财报前后 implied volatility 与 realized volatility 的差，选择买波动或卖波动；也包括避免用 call 赌财报。

出现样本：

- 第 3 周：NVDA 6/20 140 call，财报后 IV crush，账户回到初始。
- 财报教学：过去 6 次 NVDA 财报亏 6 次。
- META 王者归来：若预期 META 财报剧烈震荡，可用 straddle 做多波动。
- 英伟达财报策略：不买 call，改为全仓正股过财报，避免 IV crush。
- 期权进阶：IV 低买期权，IV 高卖期权。

入场逻辑：

- 买波动：预期实际波动大于 IV 定价。
- 卖波动：IV 显著高于 RV，且预期消息落地后波动收缩。
- 财报方向交易必须考虑预期是否已兑现。

出场/复盘：

- 财报后 IV collapse 是核心风险。
- 单纯猜对方向仍可能亏钱。

可模拟化：

- 需要 earnings calendar、IV rank、RV、option chain、财报前涨幅、guidance surprise。

主要风险：

- 财报后的方向和波动同时难预测。
- 买期权可能方向对但 IV crush 亏。
- 卖波动遇到跳空会亏大。

## 策略 12：Risk-Off Basket / 避险空头篮子

定义：在宏观和地缘风险升温、市场猴市/风险偏好下降时，用 put 做空高估值科技、小盘股、财报高开后弱势股，同时做多能源/LNG。

出现样本：

- 500 美金挑战：SPY 670 put、Oracle put、IWM put、AOI put、Sable/oil、SanDisk put。
- 桑塔纳篇：空 Russell 2000、买 LNG、做空 AOI、做空 MU；MU 价格下穿 354 后止盈。
- Day2：SPY 681 lower high 后开空，收 677。

入场逻辑：

- 地缘风险：伊朗、海峡、油价、Trump 新闻。
- 大盘高位 lower high。
- 财报高开但上方套牢盘重。
- 龙头回撤，小票逆势缩量上涨。
- 小盘股融资压力大。

出场/复盘：

- 快速获利了结。
- 失败样本来自追油股、贪婪不止盈，SanDisk put 从 2 到 5.5 没卖最后归零。

可模拟化：

- 可用 SPY/IWM/VIX/oil/news event + sector relative weakness。
- 但很多订单缺 strike、到期日、权利金。

主要风险：

- 反弹和 short squeeze。
- 0DTE put 归零快。
- 新闻反转频繁。

## 策略 13：小账户 Lottery / 0DTE 快速交易

定义：用几百美元账户买极短期期权，靠单日事件、新闻和快速波动放大账户。

出现样本：

- 500 美金曼哈顿计划：回升星 calls、AppLovin 彩票、SPY 680 末日期权、隔日 686 SPY。
- Day2：回升新能源 2 张 call + 2 张彩票，111 附近平仓；SPY 681 lower high 开空。
- 500 美金劳斯莱斯：多笔短线 put/call。

入场逻辑：

- 小资金只能用高 convexity 工具。
- 新闻/推文/盘中 lower high/快速拉升。
- 账户现金限制和 cash account settlement 影响交易频率。

出场/复盘：

- 快进快出，10 分钟级别。
- 但作者也承认会因贪婪错过止盈。

可模拟化：

- 需要分钟级 OHLC、期权分钟数据、新闻时间戳、cash account settlement。

主要风险：

- 极高归零率。
- 交易细节缺失，难还原。
- 更像实验/内容型挑战，不适合作为生产策略。

## 策略 14：基本面主题选股 / 长线 Thesis

定义：从行业大趋势和公司护城河选择候选标的，作为后续期权/正股策略的 universe。

主题和样本：

- NVDA：AI 算力、GPU、CUDA、数据中心、创始人 CEO。
- TSM/AVGO/META/AMZN/GOOGL：AI capex 和 mega-cap 成长。
- ASTS/太空：卫星直连、SpaceX IPO proxy、国防合同、政策预算。
- BTC/MSTR：去中心化共识、stock-to-flow、MSTR 杠杆 BTC proxy。
- AXTI：AI 光互联材料、增发后抄底、订单/产能重估。
- 软件股：AI agent 冲击 SaaS 护城河，半导体相对更有收入可见度。

入场逻辑：

- 行业 TAM 扩大。
- 供给瓶颈或技术护城河。
- 机构资金/政策资金进入。
- 估值低于同业或因事件错杀。
- 回调到技术支撑，例如 ASTS 200 日均线、AXTI 跌破 70。

出场/复盘：

- 主题股容易在热度最高时追高。
- MSTR/BTC 提倡分批止盈，不加仓不上杠杆。
- ASTS/太空叙事在第 66 集已经转成真实大额盈利交易：满仓 ASTS call 使账户从 88 万到 135 万；但 strike、到期日、张数、入场/出场权利金缺失，不能精确复盘。

可模拟化：

- 可做 watchlist scoring：主题、收入增长、估值、订单、政策、short interest、技术位置。
- 不能直接当买卖信号，必须加价格确认。

主要风险：

- 叙事正确但时机错误。
- 估值过高。
- 主题 ETF/概念股容易回撤。

## 策略 15：宏观事件驱动

定义：用关税、FOMC、美债拍卖、伊朗谈判、就业数据、财报、SpaceX IPO、Trump Trade 等事件决定方向。

出现样本：

- 关税缓和 → NVDA call。
- 美债拍卖需求疲软 → 第 2 周 NVDA call 跳水。
- 伊朗谈判 → NVDA 175/180 spread、185/187.5 spread。
- FOMC/Jackson Hole → 170/172.5 put spread。
- 就业数据 → 第 17 周 butterfly 拆腿。
- Trump Trade → 能源、金融、国防、BTC、黄金、美元。
- Greenland/关税威胁 → 风险资产波动上升。

入场逻辑：

- 市场对事件预期与作者判断不同。
- 事件落地可能触发 risk-on/risk-off。
- 删除帖、延迟期限、谈判措辞等被用作主观信号。

出场/复盘：

- 常用 buy the rumor, sell the news。
- 事件落地后立刻止盈，不恋战。

可模拟化：

- 结构化事件日历 + 情绪/价格反应。
- 主观判断部分难量化，需要先转成明确条件。

主要风险：

- 事件推理高度主观。
- 误判会导致期权归零。

## 策略 16：技术指标辅助层

定义：不单独构成策略，而是辅助入场/出场。

指标：

- VWAP：判断价格在平均成本上方/下方。
- RSI：70 超买，30 超卖。
- 成交量：判断突破/下跌真假。
- KDJ/J 线：恐慌释放、超卖后反弹。
- Bollinger：第 2 周用上轨 139 定止盈区。
- lower high：SPY 681 开空。
- 200 日均线：ASTS 65 附近底部 thesis。
- 订单流：145/180 上方卖盘。

使用方式：

- 技术指标很少单独触发交易，通常配合期权链和事件。
- 例：KDJ + ASTS OI + SpaceX IPO；lower high + 地缘风险开空 SPY。

可模拟化：

- 技术指标可直接编码。
- 但需要防止成为过拟合的后验解释。

## 策略 17：仓位与心理风控

定义：从失败复盘中提炼出来的风险控制原则。

核心规则：

- 97% 正股，3% 期权。
- 小资金可以高风险，但大资金不能 all-in options。
- 事前写买点、卖点、止盈、止损。
- 每周复盘，判断操作是否合理，不只看赚亏。
- 空仓是策略。
- 到达计划止盈区必须执行。
- 财报和周末隔夜风险要主动降杠杆。
- 亏损到一定程度要撤退，不要用“长期看对”扛末日期权。

失败样本：

- 第 2 周：原计划 130 以下买，实际 135 FOMO 买；到 137 不止盈，最终回撤 55%。
- 财报 call：方向未必错，但 IV crush 让账户回初始。
- META 末日期权：判断上头、梭哈、未设止盈止损，输光。
- SanDisk put：2 到 5.5 不止盈，最终归零。
- Tariff/DeepSeek：重仓 NVDA shares + calls 遇周末跳空。

可模拟化：

- 建议作为所有策略的 wrapper：
  - 每笔最大亏损。
  - 单一标的风险上限。
  - 期权仓位比例。
  - 事件日前降仓。
  - 到达目标自动减仓。

## 策略组合优先级

如果要在 QuantDinger 里做 paper/backtest，优先级如下：

1. NVDA wheel：最稳、规则清楚、最适合 paper。
2. Bull/bear vertical spread：defined-risk，payoff 清楚，数据需求可控。
3. Gamma/OI breakout：他最核心的盈利来源之一，但依赖期权链数据。
4. Max pain butterfly：能模拟，但对事件过滤要求高。
5. Risk-off basket：可做股票/ETF 代理版本，期权版以后再做。
6. 主题 watchlist scoring：先做筛选，不直接交易。
7. 0DTE lottery/all-in：只保留为研究样本，不作为生产策略。

注意：上面的优先级是“适合系统化研究/模拟交易”的排序，不等于原作者实盘赚钱贡献排序。实盘赚钱贡献里，ASTS 满仓 call 和 ORCL call 是最大单笔跳跃，NVDA 是最反复、最可复用的收益引擎。

## 最小可执行研究路线

1. 先做 `stockchatu_strategy_events.csv`：逐笔拆出 NVDA call、vertical spread、butterfly、wheel、risk-off put。
2. 对 NVDA 建三套 paper：
   - `stockchatu_nvda_wheel`
   - `stockchatu_nvda_oi_breakout_call_spread`
   - `stockchatu_nvda_max_pain_butterfly`
3. 用股票数据先做代理回测：关键 strike 附近突破、收盘点位、事件日回测。
4. 接入 options chain 后再做真实 payoff。
5. 所有策略统一套风控 wrapper：不允许 all-in，期权仓位上限 3%-10%，单笔最大亏损固定。

## 结论

他的可复用核心不是“梭哈英伟达”，而是：

- 用宏观/主题找方向；
- 用期权链找点位；
- 用期权结构表达赔率；
- 用拆腿/价差/butterfly 管理到期路径；
- 用复盘承认错误，但公开视频中经常用极端仓位放大叙事。

如果要做成投资策略，应保留前四点，严格压制最后的 all-in 行为。

但如果问题是“他主要靠哪些交易赚到钱”，结论要改成：NVDA 是反复赚钱的主引擎，ORCL 和 ASTS 是账户级别跳跃的关键单笔交易；其中 ASTS 从 88 万到 135 万，是必须单独列为核心的收官盈利腿。
