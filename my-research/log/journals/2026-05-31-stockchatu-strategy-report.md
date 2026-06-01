# Stockchatu 逐集交易策略分析报告

> Status: quick draft, not final audit. This first version was produced from
> full file inventory, transcript length checks, keyword/evidence sentence
> extraction, and sampled full reads. It is useful as a rough map, but it should
> not be treated as a careful episode-by-episode reading yet. A proper v2 should
> add per-episode evidence notes extracted from each full transcript before
> rewriting the strategy conclusions.

资料来源：`/Users/cc/Documents/GitHub/hello-web-reader/output/stockchatu/transcripts`

日期：2026-05-31

范围：共 77 个 transcript 文件；其中 73 篇有可分析文本，2 篇为空文本，2 篇为会员视频下载失败。

## 总结

这个 YouTuber 的交易体系不是一个单一量化因子，而是一套高度主观、高集中度、以期权为主要表达工具的交易风格。反复出现的核心可以归纳成五类：

1. **叙事集中**：只盯少数高信仰主题，主要是 Nvidia/AI、Bitcoin/MSTR、META、ASTS/太空、Trump/macro，以及少量小盘事件股。
2. **催化剂择时**：围绕关税、财报、地缘政治、AI capex、OpenAI/Nvidia 合作、太空政策需求、Bitcoin 关键价位、板块轮动交易。
3. **期权链推理**：从 open interest、max pain、大量 call/put strike、到期日 pinning/gamma squeeze 推断做市商可能引导或对冲的价格区间。
4. **高凸性工具**：常用近期期权、call vertical spread、butterfly、cash-secured put、covered call、wheel。公开视频里的挑战型仓位风险极高。
5. **逆人性纪律**：买在无人问津，卖在人声鼎沸；不追 FOMO；没有机会就空仓；亏损后强调复盘、止盈止损和敬畏市场。

可投资版本不能照抄他的「梭哈」行为。真正值得提炼的是：**主题强度 + 催化剂 + 期权链定位 + 价格结构 + 严格仓位控制**。在 QuantDinger 里应该先做 paper-only 策略组，等期权数据、成交假设、风险控制全部验证后，再考虑任何实盘。

## 逐集策略分析

| # | Transcript | 本集策略/观点 | 对模拟策略的启发 |
|---:|---|---|---|
| 1 | `-0qjqPRaUpw_回归英伟达_我的最新操作.md` | 回归 Nvidia，但从刺激的 sell put/sell call 体验转向长期投资形态，核心是 wheel strategy。 | 做一个保守 NVDA wheel 模块：只在愿意持有标的时卖 cash-secured put，被指派后卖 covered call。 |
| 2 | `-13Nmto1gfA_美股实盘挑战4千__100万 第17周 已至28万.md` | 第二季终章前的操作，把 Nvidia 投资 OpenAI 视为 AI 需求和未来收益催化剂。 | 大型 AI 合作新闻可做催化剂标签，但必须配合价格确认和仓位上限。 |
| 3 | `-EerUGO-j0k_美股实盘4千__28万 总集篇.md` | 4k 到 28 万的总集，反复使用 NVDA call、vertical spread、butterfly、pinning 和 gamma squeeze 逻辑。 | 这是策略分类的主索引，不应照抄仓位。按 setup 类型拆成规则。 |
| 4 | `-jlDCOj9zBk_中美关税战.md` | 把关税视为先施压后缓和的谈判工具，影响出口、风险偏好和资产价格。 | 做 macro event 标签。政治叙事不能单独开仓，需要市场确认。 |
| 5 | `13gV1I8lefk_I was broke.md` | 回顾 Trump tariff 期间 NVDA 越跌越买，最后没爆掉但暴露弹药打光的风险。 | 加入最大回撤、分批进场和保留现金规则；宏观冲击未结束时不能满仓。 |
| 6 | `2NdCFoZZGQk_美股实盘10万赚100万_88万了.md` | 用 NVDA 看涨垂直价差下注伊朗局势缓和和 AI 趋势延续。 | 事件解决型交易适合用 defined-risk spread，不适合裸买周权。 |
| 7 | `3a50ghrGhIM_Trump Trade.md` | 从股票、债券、美元、黄金、Bitcoin、Tesla 解释 Trump trade。 | 作为宏观 regime overlay，不直接成为单一交易信号。 |
| 8 | `45WE4s40nPE_格林兰事件.md` | 将 Greenland/关税威胁理解为谈判筹码，观察市场是否抛售美国资产或 fade 威胁。 | 可做「政策威胁 fade」情境，但必须考虑波动率和事件日历。 |
| 9 | `46vYLR6qZaQ_美股实盘挑战4千__100万 第13周.md` | 基于做市商杀期权，买 177.5 call、卖两张 180 call、买 182.5 call，赌 NVDA 收敛在 180。 | 实现 max-pain/butterfly paper 策略；只在横盘、低波动、无重大催化剂时使用。 |
| 10 | `4JO7DwX3yzI_How I turned 4k to 1million.md` | 英文长总集，覆盖从初始 NVDA 122 call 到后续 drawdown、squeeze、butterfly、vertical spread。 | 与中文总集去重后用于策略家族抽取。 |
| 11 | `4_hyWzEnFno_美股期权教学.md` | 讲期权基础：long call、long put、covered call、cash-secured put 的收益和风险。 | 转成期权 payoff 模板，供模拟器校验。 |
| 12 | `4aN_3XOCVlE_Trump币的投资逻辑.md` | Trump 币逻辑：注意力、稀缺性、解锁周期、任期事件和投机卖压。 | 只作为 meme/event token 研究；需要专门回测解锁和热度衰退。 |
| 13 | `4xxY0vJ6WP4_Tutorial of predicting stock price from market makers wiping.md` | 会员视频，transcript 下载失败。 | 标记缺失，不能凭标题推断细节。 |
| 14 | `6BwKG7bZcj0_美股实盘10万赚100万_要么百万_要么归零.md` | 在 NVDA 期权链指向 187.5/190 时，选择单腿 call 梭哈，追求最大凸性。 | 只能作为高风险 paper sleeve；真实策略应优先 call spread。 |
| 15 | `92LyxpDx6sk_axti this stock went up 80x last year.md` | AXT/AXTI 事件股，围绕增发、半导体基板叙事和暴涨后的底部交易。 | 做小盘事件过滤：offering selloff + 主题 + 流动性 + rebound 确认。 |
| 16 | `9ev9wiV6eXI_美股实盘挑战4千__100万 第4周.md` | 强调恐慌卖出常常把带血筹码交给做市商。 | 加 anti-panic exit：退出必须预先定义，不能波动后情绪化砍仓。 |
| 17 | `AW51OvD1g0g_美股实盘挑战4千__100万 第3周.md` | 不追高，等 NVDA 财报；基于历史 5 月财报后上涨和主观判断买 call。 | 可以测试财报季节性，但「不会一直输」属于赌徒谬误，不能做信号。 |
| 18 | `DSRAGDRAf4I_CAR史诗级逼空_全网最全解析.md` | 分析 CAR short squeeze：空头回补、swap 对冲、集中持股、内部人获利限制。 | 做 squeeze screen：short interest、borrow stress、float lock、动量、持仓集中度。 |
| 19 | `E4oBNq7hogM_比特币的投资逻辑.md` | Bitcoin 价值来自对法币和机构的不信任，稀缺性本身不足以定价。 | 作为长期 thesis，不是 timing 信号。BTC 仓位应按 regime 配置。 |
| 20 | `EHMVcjiA5_M_从0到1_从人类最基础的需求看投资.md` | 从电、AI、太空等人类基础需求延展投资方向。 | 用作主题发现框架，不直接产生买卖信号。 |
| 21 | `FplFJQ-Tp-c_My Bitcoin Prediction.md` | 英文 Bitcoin thesis，强调金融危机起源、货币信仰和机构采用。 | 与中文 Bitcoin 内容去重，归入叙事分类。 |
| 22 | `GLYtjhCpFX8_美股实盘500美金_赚到曼哈顿大平层 第1周.md` | 空文本。 | 标记不可用。 |
| 23 | `HuB53g_0cV8_Takeaways from trading 4k to 1million.md` | 交易复盘和人生观：多次爆仓、勇气、运气、改变命运。 | 只提取风控/心理课，不形成直接规则。 |
| 24 | `IGxlZJVC4k8_伟大的人生_不需要很多朋友.md` | 人生哲学内容，不是交易策略。 | 排除出策略引擎。 |
| 25 | `JQif0N-yUKU_meta王者归来.md` | META 估值修复：PE 低于其他巨头，602 到 700 的反弹是市场修正误判。 | 做 mega-cap 相对估值筛选，但入场仍需趋势确认。 |
| 26 | `KdhFH6IeBIg_为什么美股财报好股价跌_如何做空波动率_.md` | 解释财报好但股价跌：预期兑现、guidance、财报前已涨、IV crush。 | 做 earnings IV-rank 模块；卖波动率必须 defined-risk。 |
| 27 | `Knve5q0x-xs_美股实盘挑战4千__100万 第10周.md` | butterfly 获利后空仓，认为 NVDA 从看涨变成看横盘。 | 趋势耗尽后从 directional call 切换到 range/pin 策略，或者空仓。 |
| 28 | `LQf5fmykRQg_美股实盘挑战4千__100万 第11周.md` | max pain 在 165、现价 176，期权仓位和市场情绪都极度贪婪，因此做空 NVDA。 | 当现价大幅高于 max pain 且价格过热，可测试 bearish spread。 |
| 29 | `MBXlJXlw9aE_美股实盘挑战4千__100万 第6周.md` | 买 NVDA 7/11 146 call，breakeven 149.6，押注目标价安全。 | 所有 long call 都要记录 breakeven、目标价、剩余时间和 theta 风险。 |
| 30 | `Nom8aoicVdM_美股实盘500美金_赚到劳斯莱斯 第2周.md` | 高波动低确定市场，减少标的：空高估值科技/小盘，做多石油，交易 ETH 突破。 | 小资金模拟要缩小 universe，按 regime 做 long/short basket。 |
| 31 | `OSUcQAxjZl0_为什么你一卖股票就涨.md` | 散户容易在利空和暴跌时同步卖出，常接近局部低点。 | 做 retail capitulation reversal：跳空下跌、放量、reclaim。 |
| 32 | `QBwGO6U9H9w__880k to _1_35M Live Stock Trading.md` | 用 KDJ/J 线识别恐慌释放和反弹弹簧，解释大仓位做多逻辑。 | KDJ 只能作为二级 timing filter，不能单独开仓。 |
| 33 | `QGLMOYzlRsc_Why I invested in Nvidia.md` | Nvidia 长期逻辑：GPU、AI data center、游戏起家、高成长。 | 作为战略 overweight thesis；战术交易仍需估值和价格结构。 |
| 34 | `R2QgAxo6iUs_美股实盘500美金_赚到桑塔纳.md` | 大盘拉高后做避险：空 Russell 2000、做多 LNG/能源、空 AAOI/Micron 等弱标的。 | 建 risk-off basket：空弱小盘/周期，配多能源，需技术确认。 |
| 35 | `RLdwlBtQdvU_Analysis of MSTR.md` | MSTR 是杠杆 Bitcoin exposure，收益和风险都高于直接持有 BTC。 | MSTR 模拟应跟踪 BTC beta、NAV 溢价、融资/稀释风险。 |
| 36 | `Rd30zvqmRvM_英伟达车轮策略第二战_胜率100__.md` | Nvidia wheel 第二战，观察 call/put 分布，也提醒不要因浮盈情绪放弃策略。 | wheel 必须有预设 roll/assignment 规则，不能临场改短期权计划。 |
| 37 | `T31cwleAVMI_美股实盘挑战4千__100万 第15周.md` | NVDA 高开接近 180 后定义为非理性推高，选择逢高做空。 | 做空只在价格拉伸、option pin、反转结构共同出现时测试。 |
| 38 | `Tuq7F6QZeyc_Stock Q_A.md` | Q&A：小资金做大、机器人/新能源趋势、美股过贵、VWAP/均线等技术工具。 | 做交易 checklist：主题、估值热度、VWAP 确认、事前计划。 |
| 39 | `UJsV8AySZKw_美股实盘500美金_赚到曼哈顿大平层.md` | 500 美金账户，做多底部、有故事、有人气的股票，快速止盈，再做小 SPY 隔夜跳空。 | 小账户策略需单独 paper，且建模 cash account 结算限制。 |
| 40 | `VBDdeYS5Bz0_麻省理工天才少年美股4千炒到100万.md` | 讲风险承担、Pi call、止盈止损和活得久。 | 每张交易单强制填写止盈、止损、失效条件。 |
| 41 | `VJfOi2l7tc0_美股选股名单.md` | 股票榜单：Nvidia、TSMC、META 等，依据 AI capex、护城河、业绩和成长性。 | 转成主题 watchlist score：护城河 + capex 受益 + 增长 + 相对估值。 |
| 42 | `VXvai6djs7U_美股实盘挑战4千__100万 第5周.md` | 满仓 NVDA 持有，解释为什么 140-145 横盘、142 附近被 pin。 | 横盘/pin 判断应触发中性结构或等待，不应强行方向交易。 |
| 43 | `X9TWi6_YfMQ_美股实盘挑战4千__100万 第14周.md` | 开 165/170/175 butterfly 赌 NVDA 收在 170，但 AVGO 财报打破平衡。 | pin trade 必须检查相关板块财报和外部催化剂日历。 |
| 44 | `XBYAFgBPEsQ_美股实盘10万赚100万_167梭哈英伟达.md` | 167 附近梭哈 NVDA call，173.5 附近因恐惧落袋。 | 证明凸性可赢，也证明超大仓位会制造情绪化退出。 |
| 45 | `ZLbHFei0lKQ_Stock Q_A.md` | Q&A：潜力股、期权基础、情绪交易、tokenized stocks、交易计划。 | 标准化 trade ticket：thesis、entry、invalidation、target、expiry、max loss。 |
| 46 | `ZPyFOz7d5Cg_美股实盘挑战4千__100万 第9周.md` | 发现 NVDA 170 call OI 最大，预期突破 170 后 gamma squeeze 到 172.5 附近。 | 核心 gamma squeeze 规则：大 OI strike + 突破 + 动量。 |
| 47 | `Za7I-rcxUTM_账户腰斩_曝光我投资生涯的至暗时刻_.md` | tariff 暴跌中半仓/加仓 NVDA，最后子弹打光，靠反弹活下来。 | 强制保留现金，宏观不确定时禁止一次性打满。 |
| 48 | `_OUR0dVOG-8_美股实盘500美金_赚到曼哈顿大平层 Day2.md` | Day 2 预设 113 左右止盈，cash account 卖出后资金需结算，因此收手。 | 小账户回测必须建模资金结算和不可立即再交易。 |
| 49 | `_ebBDP1Dcq8_付费视频_杀期权判断点位的方法.md` | 会员视频，transcript 下载失败。 | 精确「杀期权点位」方法缺失，只能用 max pain/OI 近似。 |
| 50 | `_x0faLWBrFY_人民币对美元汇率会到多少_.md` | 人民币/美元宏观评论，可用交易规则不足。 | 仅作为 FX 背景，除非后续改成明确汇率因子。 |
| 51 | `agrUJLndj34_美股实盘挑战4千__100万 第12周.md` | NVDA 从 180 横盘后跌到 175，使用 170/172.5 bullish vertical spread。 | 回调到支撑后的 bullish spread 可回测，风险/收益明确。 |
| 52 | `bEX1_nQE2uY_My Bitcoin Prediction.md` | Bitcoin 估值模型，讨论 stock-to-flow/减半和华尔街分歧。 | 模型可做情景区间，不能做精准预测。 |
| 53 | `gEFDXAaGokQ_期权进阶_解锁百倍收益的期权投资法 _moomoo.md` | 进阶期权：IV 是期权价格指数，贵时卖、便宜时买。 | 所有期权策略都要加 IV percentile/IV rank 过滤。 |
| 54 | `gjQ3ZaW1rMA_美股实盘挑战4千__100万 第8周.md` | 买 NVDA 7/18 160 call，因 160 call OI 最大，预期突破后 gamma squeeze 到 165。 | 另一个 gamma squeeze 样本，需要 OI 数据和突破确认。 |
| 55 | `grOz0gFGszA_比特币的估值模型.md` | Bitcoin 首破 10 万后的估值模型，引用 Saylor/Wood 对上行空间的乐观观点。 | 长期 valuation dashboard，不是短线入场。 |
| 56 | `h061h_NgCLM_my stock pick.md` | Abao 美股战力榜：Nvidia、TSMC、META 等高成长/护城河公司。 | 建 watchlist score，并与价格动量结合。 |
| 57 | `hM7wbeWPS_w_小资金如何做大_技术指标怎么用_.md` | 小资金三条路：长期复利、高风险期权、技术工具；讲 RSI、量价、假突破。 | 区分财富建设和彩票仓；技术信号必须加 trend/regime filter。 |
| 58 | `iQ1D__3wvCA_比特币概念股微策略MSTR.md` | MSTR 和 BTC 的区别：MSTR 是更高风险的杠杆 BTC proxy。 | 与 MSTR 模块合并：BTC beta、NAV premium、融资和稀释。 |
| 59 | `kL-eqVEWedc_重读利弗莫尔.md` | META 末日期权爆仓后复盘：过度自信、忘记仓位管理、没设止盈止损。 | 硬规则：禁止全仓周权；每笔期权必须有最大账户风险。 |
| 60 | `l6Cidd6Rnrc_一年翻80倍_AXTI还能买吗.md` | AXT/AXTI 暴涨后是否还能买的讨论。 | 80 倍股不能追高，只测试回调/rebase 后入场。 |
| 61 | `lF_sQVMOYVk_美股说唱.md` | 说唱/娱乐内容，无策略。 | 排除。 |
| 62 | `mMxHYN7LuNo_美股实盘挑战4千__100万 第1周.md` | 4000 美金买 NVDA 122 call，受关税缓和和迪拜订单催化，136 附近卖出，周五空仓。 | 经典 pattern：正催化 + AI 龙头 + call 凸性 + 人声鼎沸止盈。 |
| 63 | `mWXoxQtGLeI_打工是不可能打工的.md` | 生活方式/动机内容。 | 排除。 |
| 64 | `mtbDe1kXfkY_美股实盘挑战4千__100万 第7周.md` | 计算 NVDA 到 157.5 的概率，预期突破后 gamma squeeze 到 160。 | 把概率估计、strike OI、突破阈值合并后再开方向期权。 |
| 65 | `nTO9Pvts-hQ_options trading 101.md` | 英文期权基础，与中文教学类似。 | 用于期权 payoff/风险说明模板。 |
| 66 | `pnLj8t4tZzI_美股实盘88__135万.md` | 空文本。 | 标记不可用。 |
| 67 | `qZq5h5kRBH0_2026美股王炸板块太空.md` | 太空板块 thesis：政策需求、商业规模、资本定价、ETF 表现。 | 建太空主题篮子，只交易有流动性和趋势确认的标的。 |
| 68 | `qigOjXQciyA_美股实盘10万赚100万_梭哈英伟达_我破防了.md` | 开 600 组 NVDA 175/180 call spread，因伊朗风险大幅回撤，低于 175 可能归零。 | weekly spread 也可能 100% loss，必须做事件风险压力测试。 |
| 69 | `sV3qSkqh878_英伟达财报策略.md` | 用杀期权原则判断 NVDA 190 put/周五收盘点位。 | 精确方法缺失前，只能用 max pain/put wall 做 paper 近似。 |
| 70 | `u_O0PPT-KxQ_2026_软件股完犊子.md` | 看空软件股：AI 工具冲击 SaaS/软件估值，软件 basket 继续下跌。 | 可做 sector short 候选：AI disruption narrative + 下跌趋势。 |
| 71 | `uk-8FRHJVDc_Why I all in ASTS.md` | ASTS all-in thesis：卫星直连、相控阵天线、专利、200 日均线回踩反弹。 | 主题长线 setup：zero-to-one 主题 + 200DMA pullback + rebound confirmation。 |
| 72 | `vc5p2Rivvqk_如何度过低谷期.md` | 借 Livermore 破产/低谷讲交易心理。 | 不产生信号，作为风控心理笔记。 |
| 73 | `vrTqO9aKR9o_潜力股怎么选_怎么止盈_.md` | 潜力股选择：护城河、技术优势、交易计划、止盈止损、复盘。 | 作为通用交易单和复盘 checklist。 |
| 74 | `ycfh7LFWNWE_why I invested in the space sector.md` | 太空/卫星连接 thesis：Starlink、国防、指挥、情报、政府需求。 | 太空主题 watchlist + 政策/订单催化模型。 |
| 75 | `yhoKiuGFfCA_美股实盘挑战4千__100万 第2周.md` | NVDA 135 附近买 132 末日期权，按 140 call wall 和杀期权逻辑设止盈 137-139，但经历大回撤。 | pin 逻辑即使方向对，过近 expiry 和过大仓位仍会失败。 |
| 76 | `z6ri_AXw1UU_我是如何从4千做到100万的.md` | 中文长总集，重复第 1 周到后续多个阶段：calls、spreads、butterflies、gamma squeeze、风控复盘。 | 作为中文主材料，与英文总集和 28 万总集去重。 |
| 77 | `z_pyHCARzFQ_英伟达的投资逻辑.md` | Nvidia 投资逻辑：AI 时代、GPU/data-center、黄仁勋、高成长。 | 战略 thesis 输入，不等于择时信号。 |

## 统一策略地图

### A. 催化剂方向期权

最常见的大赢家来自 NVDA 方向期权：关税缓和、AI 订单、财报预期、地缘政治缓和、大型 AI 合作。公开视频常用周权或近期期权。

可投资翻译：

- 默认使用 call vertical spread，而不是裸买周权。
- 入场要求：重大催化剂 + 价格站上 VWAP/短均线 + 流动性足够 + IV 没有极端过贵。
- 每笔账户风险先设 0.5%-2% paper，不允许生产规则里出现 all-in。
- 出场：目标价、情绪/成交量高潮、或到期前 time stop。

### B. Gamma Squeeze / Strike Breakout

多集都用大额 open interest strike 推断：突破关键 strike 后，做市商对冲可能推动价格去下一个 strike。

可投资翻译：

- 数据需求：期权链、OI、成交量、IV、delta/gamma 估计。
- 入场：价格放量突破高 OI strike，且市场 regime 支持。
- 出场：下一个高 OI strike、跌回 strike 下方、或到期前动量消失。
- 风险：如果做市商并不是 short gamma，逻辑可能反过来。

### C. Market-Maker Pin / 杀期权

他经常预测周五收盘点位，用 max pain/杀期权逻辑做 butterfly 或短期权结构。

可投资翻译：

- 只能先 paper。
- 条件：实现波动率下降、价格靠近 max pain、无财报/板块重大催化剂、预期波动范围窄。
- 工具：defined-risk butterfly 或 iron butterfly；不裸卖期权。
- 退出：价格离开预期区间，或出现相关板块事件。

### D. Wheel Strategy / 收租型覆盖

后期 Nvidia 内容转向 wheel：卖 put、接受指派、卖 covered call。这是素材里最接近可投资的框架。

可投资翻译：

- 只对愿意长期持有的标的做，paper 从 NVDA 开始。
- 在支撑/估值区卖 put；财报周默认回避，除非测试证明可行。
- 被指派后，在成本上方或压力位卖 covered call。
- 限制单一标的 exposure，因为 wheel 的本质风险仍是持股暴跌。

### E. 主题选股

主题很清楚：AI 基建、NVDA/TSMC/META、Bitcoin/MSTR、ASTS/太空、机器人/新能源、AI 冲击下的软件空头。

可投资翻译：

- 维护主题 watchlist，评分维度包括护城河、收入增速、机构需求、催化剂频率、流动性、估值热度。
- 主题分数只用来筛 universe；真正入场仍需价格确认。

### F. 心理和风控

素材里多次提到爆仓、腰斩、后悔、止盈止损。公开挑战里的行为经常和这些教训冲突，所以要把「策略信号」和「娱乐型仓位」分开。

可投资翻译：

- 每笔 paper trade 必须写 thesis、entry、invalidation、target、time stop、max loss、review。
- 如果一个策略必须靠全仓才有意义，直接拒绝。
- 先验证信号，再谈放大；不能先放大再靠运气验证。

## QuantDinger 落地方案

### Phase 1: 建结构化研究表

先把 transcript 转成结构化数据：

- `episode_id`
- `title`
- `date`
- `ticker`
- `asset_class`
- `strategy_family`
- `instrument`
- `direction`
- `entry_logic`
- `exit_logic`
- `risk_lesson`
- `data_needed`
- `simulation_ready`

这样能把口语内容变成候选规则，同时避免把每一句观点都误当成可回测信号。

### Phase 2: 先做三个 paper 策略

1. **NVDA wheel paper strategy**
   - 数据：日线 OHLCV、支撑/压力、财报日历。
   - 动作：支撑下方卖 cash-secured put；被指派后卖 covered call。
   - 优先级最高，因为最好控风险，也最接近真实可投资策略。

2. **NVDA options-chain squeeze strategy**
   - 数据：期权 OI/volume by strike、IV、股票 OHLCV。
   - 动作：价格放量突破 dominant call wall 后买 call spread。
   - 这是挑战中重复出现最多的赢家，但强依赖期权数据。

3. **NVDA max-pain butterfly strategy**
   - 数据：期权链、max pain、实现波动率、催化剂日历。
   - 动作：围绕预期周五 pin 位开 defined-risk butterfly。
   - 这是「杀期权」逻辑的直接版本，但模型风险高。

### Phase 3: 建主题篮子，不急着交易

- AI infra：NVDA、TSM、AVGO、AMD、META、AMZN、MSFT、GOOGL。
- Bitcoin proxy：BTC、MSTR、相关 miner/ETF。
- Space/connectivity：ASTS、RKLB、LUNR、太空 ETF 成分。
- AI-disrupted software shorts：高估值且下跌趋势的软件股。
- Small-cap events：AXT/AXTI 类 offering、squeeze、放量反弹候选。

### Phase 4: 回测和 paper gate

最低通过标准：

- 能拿到数据的策略至少 2 年回测；2025-2026 事件用 event replay。
- 期权必须计入 premium、bid/ask spread、commission、slippage、assignment、expiry。
- 报告 hit rate、expectancy、max drawdown、average loss、largest loss、time in market。
- 如果 realistic spread/slippage 后 edge 消失，策略淘汰。
- paper-only 跑 30-60 个交易日后，才讨论 live。

## 立即下一步

1. 把这些 transcript 生成 Phase 1 的 CSV。
2. 在 `my-research/strategies/` 新增 `stockchatu_nvda_wheel_paper.py`。
3. 决定期权数据源：Polygon、Tradier、IBKR、ORATS 或其他供应商。
4. 先回测股票代理版：NVDA 支撑/reclaim + cash/covered-call 近似。
5. 等期权链数据可靠后，再做 gamma squeeze 和 butterfly。

## 风险提示

- 这批素材适合挖 idea，不适合复制交易。
- 公开挑战常常依赖极端集中、近期期权和幸存者叙事。
- 我们要保留他的观察力，移除 all-in 仓位。
- 没有期权链数据时，所有「做市商杀期权」都只是叙事近似，不能当成真实模型。
