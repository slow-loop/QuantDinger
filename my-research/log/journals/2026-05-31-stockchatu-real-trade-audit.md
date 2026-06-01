# Stockchatu 逐集真实交易审计

资料来源：`/Users/cc/Documents/GitHub/hello-web-reader/output/stockchatu/transcripts`

生成方式：脚本逐个读取每个 transcript 的正文全文，抽取包含交易、价格、张数、标的、策略、复盘/风险关键词的证据句。没有在 transcript 中出现的字段不补写。

字段说明：

- `标的`：从 transcript 正文命中的 ticker/中文名称抽取。
- `真实交易证据`：保留买入/卖出、开仓/平仓、做多/做空、call/put、价差、wheel 等操作句；含价格、张数、成本、行权价、收益率的句子会被优先排序。
- `策略证据`：保留解释入场逻辑、期权结构、做市商/max pain/gamma/技术指标的句子。
- `回顾证据`：保留复盘、错误、风险、回撤、仓位、计划执行相关句子。
- 空白表示该类证据没有被脚本从该篇正文中可靠抽出，不代表视频绝对没有提到。
- `审计判读`：只依据本集抽出的证据做策略归类；没有交易证据时不会硬补真实交易。

## 总览

- 总文件数：77
- 可用 transcript：73
- 下载失败/会员内容：2
- 空 transcript：2

## 逐集审计

### 01. 回归英伟达_我的最新操作

- 文件：`-0qjqPRaUpw_回归英伟达_我的最新操作.md`
- 状态：`usable`；正文长度：1263
- 标的：NVDA
- 真实交易证据：过去这一年，我经历过sell put和sell call期权，经历过那种一夜之间天堂与地狱的切换，那种感觉很刺激，也很真实，但它更像赌徒，而不是一名投资者。 || 所谓车轮策略其实非常简单，就是围绕一只你愿意长期持有的股票，反复做两件事：sell put和sell covered call。 || 在2月4号周三，英伟达在170多块的位置，我卖出了2月6号到期的185 put option，卖出一张，我能得到的权利金是778美金。 || 先说sell put。 || 卖出put本质上就是你在一个更低的价格买入这只股票，同时收取一笔权利金。 || 于是整个过程就像一个循环：卖put，接股票，卖covered call，股票被行权，再卖put。 || 所以这次回归我的核心策略就只有四个字：车轮战法，the wheel strategy。 || 接下来，我们说covered call。 || 当你已经持有股票的时候，你可以卖出call，相当于告诉市场：如果涨到这个价格，我愿意卖出我的股票。 || 如果股价涨了上去，你可以在一个满意的价格卖出你手上的股票。
- 策略证据：所以这次回归我的核心策略就只有四个字：车轮战法，the wheel strategy。 || 所谓车轮策略其实非常简单，就是围绕一只你愿意长期持有的股票，反复做两件事：sell put和sell covered call。 || 而这个策略一般是在你认为这只股票跌得差不多了，保守看涨的时候，你才会使用的。 || 但如果你看英伟达近半年的股价，170几的价格具有绝对的诱惑性，再加上当周max pain在185，而股价还在180下方。 || 过去的我总在寻找下一次的爆发，现在的我更愿意去建立一个可以重复、可以长期执行、可以穿越周期的策略。
- 回顾证据：所以那一刻我并不是在赌，而是在顺着市场的力往前走，而这也是我在“众人恐慌我贪婪”这句话上的保守性表态。
- 审计判读：wheel/卖权利金；做市商/max pain/pin 推理；方向性 call；put/看跌或卖 put。

### 02. 美股实盘挑战4千__100万 第17周 已至28万

- 文件：`-13Nmto1gfA_美股实盘挑战4千__100万 第17周 已至28万.md`
- 状态：`usable`；正文长度：5531
- 标的：NVDA, META, TSM/TSMC
- 真实交易证据：我首先分析了英伟达本周的期权open interest数据，发现未平仓数量最大的是94000张180扣。 || 也就是说，只要周五收盘英伟达股价在这个区间里，这个蝴蝶策略都为盈利，股价为180时，盈利达到最大值228%。 || 截止周四9点40分，英伟达股价跌到了173.95，而阿宝的蝴蝶策略已经亏损了将近52000元。 || 而这组牛市垂直价差的利润最大收益率为0.55除以2.5减0.5%，也就是28.2%。 || 回顾这波澜壮阔的一天：开盘10分钟，蝴蝶策略亏损5万；接着我把蝴蝶拆腿变call，盈利7万；之后同一天内，我开仓并垂直价差，再次盈利2.6万。 || 时间仅仅剩下一天，只要英伟达接下来的一天跌、横盘或者涨幅低于1.5%，阿宝的垂直价差策略就能获得最大盈利。 || 我构建了175、180、185的蝴蝶策略：买入一张175扣，卖出两张180扣，买入一张185扣，成本1.5，盈利区间为176.5至183.5。 || 这蝴蝶策略一共3条腿，我拆去了其中两条，我平仓了180扣和185扣，留下了175扣，并将平仓后获得的额外资金用于开仓更多的175扣。 || 而随后我平仓了175扣，开仓了172.5、175的牛市垂直价差。 || 那么这一周我一共切换了三个不同的策略：先是周二开180蝴蝶，在周四拆腿变为175扣，周四再平仓变为172.5、175的垂直价差。
- 策略证据：我首先分析了英伟达本周的期权open interest数据，发现未平仓数量最大的是94000张180扣。 || 也就是说，只要周五收盘英伟达股价在这个区间里，这个蝴蝶策略都为盈利，股价为180时，盈利达到最大值228%。 || 截止周四9点40分，英伟达股价跌到了173.95，而阿宝的蝴蝶策略已经亏损了将近52000元。 || 因为做市商对冲的原因，这个价位往往会形成强阻力位，股价很难轻易突破这个墙。 || 时间仅仅剩下一天，只要英伟达接下来的一天跌、横盘或者涨幅低于1.5%，阿宝的垂直价差策略就能获得最大盈利。 || 190的call wall会使得股价难以稳步站上190，而根据做市商杀期权原则，做市商也会将股价压在190之下，杀死绝大多数的看涨期权。
- 回顾证据：周五当日盈利63000，最终实盘账户在第17周来到了28万美金，累计收益率69倍。 || 也就是说，只要周五收盘英伟达股价在这个区间里，这个蝴蝶策略都为盈利，股价为180时，盈利达到最大值228%。 || 面对这份强劲的就业数据，不少人开始恐慌性抛售，纳斯达克指数下跌1.3%，英伟达也跌到了173美元。 || 截止周四9点40分，英伟达股价跌到了173.95，而阿宝的蝴蝶策略已经亏损了将近52000元。 || 而这组牛市垂直价差的利润最大收益率为0.55除以2.5减0.5%，也就是28.2%。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；做市商/max pain/pin 推理；含亏损/回撤复盘。

### 03. 美股实盘4千__28万 总集篇

- 文件：`-EerUGO-j0k_美股实盘4千__28万 总集篇.md`
- 状态：`usable`；正文长度：39973
- 标的：NVDA, META, BTC, TSLA, AVGO, AMD, ORCL
- 真实交易证据：週五英偉達155高開，由於未平倉期權數量最多的是這周5到7的155 call，阿寶根據判斷股價有機率產生一口氣突破157，於是大膽買入了7月18日 155 call。 || 阿寶策略有兩個組成部分：買入一張英偉達7月25號的165 put，賣出一張英偉達7月25號的167.5 put，以一個垂直價差的組合策略為例，整個策略需要鎖定250刀保證金，並獲得78刀的權利金。 || 早上9點50分，我按計劃開倉了180到182.5的熊市垂直價差策略，賣出一張8月1號180 call，買入一張8月1號182.5 call。 || 阿寶週四開倉的蝴蝶策略包括了買入一張177.5 call，賣出兩張180 call，買入一張182.5 call。 || 我分析了這週期權的資料，發現未平倉最高的期權就是7月11日 160 call，一共15000張，這意味著大概率股價會突破160，並且產生Gamma效應，使得股價持續攀升，突破了160就會一口氣衝到165。 || 這個策略總共包含了4個部分，買入一張7月18日 167.5 call，買入一張7月18日 175 call，賣出兩張7月18日 172.5 call，總成本為2.15，所以對應的一手是215刀。 || 如果我們再來看8月1號這一週的期權未平倉倉位，排名第一的是94000張177.5 call，緊接著的是89000張185 call和71000張180 call。 || 熊市垂直價差策略有兩個組成部分，買入一張182.5 call，賣出一張180 call。 || 這組垂直價差包含了賣出172.5 put和買入170 put，只要週五收盤英偉達股價大於172.5，我就能獲得最大盈利27.5%的收益回報率。 || 我根據英偉達的期權open interest判斷， 基於做市商殺期權原則，本週對於期權要多空雙殺，可以看到，在180的股價上，剛好能同時殺死180 call和put以及其他的所有期權。
- 策略证据：我根據英偉達的期權open interest判斷， 基於做市商殺期權原則，本週對於期權要多空雙殺，可以看到，在180的股價上，剛好能同時殺死180 call和put以及其他的所有期權。 || 週五英偉達155高開，由於未平倉期權數量最多的是這周5到7的155 call，阿寶根據判斷股價有機率產生一口氣突破157，於是大膽買入了7月18日 155 call。 || 我分析了這週期權的資料，發現未平倉最高的期權就是7月11日 160 call，一共15000張，這意味著大概率股價會突破160，並且產生Gamma效應，使得股價持續攀升，突破了160就會一口氣衝到165。 || 這個策略總共包含了4個部分，買入一張7月18日 167.5 call，買入一張7月18日 175 call，賣出兩張7月18日 172.5 call，總成本為2.15，所以對應的一手是215刀。 || 阿寶策略有兩個組成部分：買入一張英偉達7月25號的165 put，賣出一張英偉達7月25號的167.5 put，以一個垂直價差的組合策略為例，整個策略需要鎖定250刀保證金，並獲得78刀的權利金。 || 首先盈虧比清晰，你知道最壞的情況，也就是虧172刀，最好的情況是賺78刀；其次，風險可控，不像裸賣put有無限虧損，這種價差組合可以把風險封頂；再者適合震盪偏多的行情， 不需要股價暴漲，只要不跌破關鍵支撐就能賺到錢。
- 回顾证据：最大虧損是250減78等於172刀，最大盈利是78刀，最大收益率是78除以250，也就是31.2%，盈虧平衡點是167.5減0.78等於166.72。 || 首先盈虧比清晰，你知道最壞的情況，也就是虧172刀，最好的情況是賺78刀；其次，風險可控，不像裸賣put有無限虧損，這種價差組合可以把風險封頂；再者適合震盪偏多的行情， 不需要股價暴漲，只要不跌破關鍵支撐就能賺到錢。 || 第二週回撤55%，累計收益1.75倍。 || 最大虧損215刀，最大盈利266.75刀。 || 就是截止下午3點45時間線的截圖，可以看到，如果你只買英偉達167.5的call， 最終收益率會是23%，而阿寶的破譯蝴蝶最終收益率是95%，失之毫厘，謬以千里。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put；含亏损/回撤复盘。

### 04. 中美关税战

- 文件：`-jlDCOj9zBk_中美关税战.md`
- 状态：`usable`；正文长度：1437
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：美國是中國的第一大出口市場，關稅從60%到10%，這種先施壓後緩和的策略，或許是特朗普這隻老狐狸想要先透過強硬的態度迫使對手坐到談判桌前，以關稅為籌碼，然後在談判中逐步釋放緩和的訊號，以此促成談判協議的達成。
- 回顾证据：可為什麼特朗普在上任後並沒有打算執行60%的關稅計劃呢？
- 审计判读：本集偏宏观/主题/估值分析，未抽到明确实盘买卖。

### 05. I was broke

- 文件：`13gV1I8lefk_I was broke.md`
- 状态：`usable`；正文长度：7661
- 标的：NVDA, CAR, ETH
- 真实交易证据：If the stock price drops 5%, your call option could lose 50% of its value just like that. || I I mentioned a method on my show before called the mortal cultivation method, which means you should only use 3% of your portfolio for options trading. || If the stock price drops 10%, your call is basically worthless. || You really have to be aware of this, because in a world of high volatility and high risk, going all in on options is basically dancing on the edge of a knife. || So, whenever there was a pullback, it was basically a chance to buy the dip. || At that time, not only was I heavily invested in Nvidia shares, but I also had a big position in Nvidia calls. || Anyone who trades options knows what the scariest thing about options is, right? || And with options, you can't do anything during after-hours trading because the exchanges are closed, so there's no way to cut your losses. || So, there was really no chance to recover or fix That night, I just turned off the lights and sat in front of my computer, listening. || Like the saying goes, as long as the green hills remain, there will always be wood to burn.
- 策略证据：I I mentioned a method on my show before called the mortal cultivation method, which means you should only use 3% of your portfolio for options trading. || Most people, unless you stayed out of the market most of the time, I don't think you could have avoided it. || Actually, I thought about it more than once because you never know when the drop is going to end. || You really have to be aware of this, because in a world of high volatility and high risk, going all in on options is basically dancing on the edge of a knife. || If you see me going all in with my real trades, that's only because I have just 4,000 as my principal. || Now, the last point might not apply to everyone, but if you think your understanding is deep enough, you can take this as a reference.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put；高集中仓位。

### 06. 美股实盘10万赚100万_88万了

- 文件：`2NdCFoZZGQk_美股实盘10万赚100万_88万了.md`
- 状态：`usable`；正文长度：3837
- 标的：NVDA, ORCL
- 真实交易证据：我分別在1.8和1.9分批次買入的看漲垂直價差策略，最終在2.45賣出止盈，吃滿了最大盈利，收益率33%。 || 我在日內高點止盈，4.5賣出了2.23買入的看漲期權，收益率102%，賬戶來到了88萬，離100萬的目標只剩一步之遙。 || 而4月13號到4月17號這周，我梭哈了所有的28萬美金，買入了1800組週五到期的185和187.5的英偉達看漲垂直價差，下注英偉達週五收盤大於187.5。 || 我在止盈英偉達垂直看漲策略之後，用全部的44萬利潤買入了近2000張Oracle的看漲期權，成本2.23，後路均有。 || 我開倉的第二個原因是我觀察了本週英偉達期權的分佈，和上週簡直一模一樣。 || 未平倉量前六的全都是清一色的看漲期權，從185、187.5、190、195到200。 || 如果你是做市商，在面臨散戶和機構買入如此龐大數字的看漲期權時，而股價又在不斷上行，你會怎麼辦？ || 假設英偉達站上180，180的期權會發生伽瑪擠壓，那麼做市商會被迫買入股票拉高股價。 || 這就是我全部開倉英偉達看漲垂直價差策略的交易邏輯。 || 那麼既然基本面技術面全部利好，我自然就梭哈了28萬美金，全力一擊做多。
- 策略证据：我分別在1.8和1.9分批次買入的看漲垂直價差策略，最終在2.45賣出止盈，吃滿了最大盈利，收益率33%。 || 我在止盈英偉達垂直看漲策略之後，用全部的44萬利潤買入了近2000張Oracle的看漲期權，成本2.23，後路均有。 || 之前英偉達每週的期權基本上前六不可能是清一色的看漲期權，基本上都是看跌看漲參半，而這就會造成殺期權，而不是伽瑪擠壓。 || 可是本週不一樣，持倉量排名前六的期權清一色都是看漲期權，這就讓我判斷會發生伽瑪擠壓。 || 而這就是伽瑪擠壓，有散戶、機構、做市商多方面參與的一場金融戰爭。 || 假設英偉達站上180，180的期權會發生伽瑪擠壓，那麼做市商會被迫買入股票拉高股價。
- 回顾证据：我分別在1.8和1.9分批次買入的看漲垂直價差策略，最終在2.45賣出止盈，吃滿了最大盈利，收益率33%。 || 我在日內高點止盈，4.5賣出了2.23買入的看漲期權，收益率102%，賬戶來到了88萬，離100萬的目標只剩一步之遙。 || 每期影片底下的評論區都有人期待我爆倉，想知道如果我沒贏能活多久。 || 沒錯，你會不得不買入大量的正股來對沖風險，從而推動股價的上漲。 || 如今我是悟道了，可你們不知道的是，我悟道前爆倉過3次，悟道後爆倉過一次，才有了今天的成就。
- 审计判读：defined-risk 垂直价差；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 07. Trump Trade

- 文件：`3a50ghrGhIM_Trump Trade.md`
- 状态：`usable`；正文长度：10905
- 标的：BTC, CAR, TSLA, ETH, LNG/Oil
- 真实交易证据：Shortly after President Trump took office in 2016 with the support of a Republican controlled Congress, the defense budget for the 2017 to 2019 fiscal years was increased by more than $100 billion. || The current short-term rate is 4.75%. || So, in order to achieve higher returns, we'll see a lot of capital from short-term government bonds flowing into long-term government bonds or the stock market. || But in the long run, weakening the regulation of financial institutions could exacerbate systemic risk and that was one of the triggers of the 2008 financial crisis. || And this type of bet is a trading strategy that all of Wall Street's financial institutions are now employing called the Trump trade. || Therefore, a victory for Trump could immediately trigger a sharp short-term rise in oil stocks. || So, a victory for Harris would most likely cause a rapid short-term surge in clean energy related stocks. || Therefore, in the short term, this move will undoubtedly be a major boon for the US financial industry. || Once Trump is elected, a large number of institutions will likely choose to sell the news, which means selling at a high price to lock in their profits. || Short-term US Treasury rates will fall and long-term rates will rise.
- 策略证据：As a major sponsor of the Trump campaign, Musk is giving away $1 million of his own money every day to a random lucky audience member to support Trump's campaign. || And that's why over the past few weeks, the price of Bitcoin has climbed all the way to $72,000, close to its all-time high. || Today, ABA will take you from stocks to bonds, from the US dollar to gold, and then to Bitcoin to give you a comprehensive analysis from the perspective of a Wall Street professional. || Trump's policies favor supporting domestic fossil fuel production in the United States because these policies are designed to reduce regulatory requirements, thereby lowering costs and further promoting the development of oil and natural gas. || But at the same time, Trump's trade policies, which include increased tariffs and restrictions on technology exports, could negatively impact tech companies that rely heavily on global supply chains or have significant business in the Chinese market. || v=3a50ghrGhIM LANG: en TRANSCRIPT: October 27th, 2024, former US President Trump held a massive rally at Madison Square Garden in New York, kicking off the final week of his election campaign.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call。

### 08. 格林兰事件

- 文件：`45WE4s40nPE_格林兰事件.md`
- 状态：`usable`；正文长度：1239
- 标的：未抽取到明确标的
- 真实交易证据：分析師指出，這可能是更大範圍賣出美國資產的開始。
- 策略证据：Brandywine Management說，雖然地緣政治博弈給關稅問題增加了新的變數，但我相信冷靜的頭腦會佔上風，這些關稅威脅更像是一種談判策略，用來爭奪對格陵蘭的控制權。 || 大多數人只會看賬面盈虧，卻不在意背後的原則對錯，要是因為看賬面盈虧而影響了對於原則的判斷，則是以小失大。
- 回顾证据：接下來幾周怎麼發展，決定了一切，所以我們不會恐慌拋售，但會非常謹慎，準備迎接更高波動的到來。 || 而當這些戲劇性事件發生時，正好是投資者對股市最樂觀的時候，美國股票的淨看多倉位處於兩年來的最高水平。 || 大多數人只會看賬面盈虧，卻不在意背後的原則對錯，要是因為看賬面盈虧而影響了對於原則的判斷，則是以小失大。
- 审计判读：含亏损/回撤复盘。

### 09. 美股实盘挑战4千__100万 第13周

- 文件：`46vYLR6qZaQ_美股实盘挑战4千__100万 第13周.md`
- 状态：`usable`；正文长度：1676
- 标的：NVDA, AVGO, AMD
- 真实交易证据：蝴蝶阿寶週四開倉的蝴蝶策略包括了買入一張177.5 call，賣出兩張180 call，買入一張182.5 call。 || 末日蝴蝶買入一張172.5 call，賣出兩張175 call，買入一張177.5 call。 || 基於做市商殺期權原則，本週對於期權要多空雙殺，可以看到，在180的股價上，剛好能同時殺死180 call和put以及其他的所有期權。 || 拿你總資產的97%做正股，3%做期權。 || 因此，在迅速止損180蝴蝶之後，我在須臾之間反手開倉了新的策略。 || 止損的扣一，硬扛扣二，要知道，倘若收盤時股價仍然低於180，那麼180的蝴蝶將血本無歸。 || 我在開盤的幾分鐘內迅速的止損了180蝴蝶。 || 你得學會止盈和止損。 || 英偉達週五4點收盤174.18，阿寶憑藉著末日蝴蝶逆風翻盤，彎道超車，賬戶從早上止損時的10萬來到了16萬。 || 做蝴蝶策略的核心的技巧方法就是先判斷最終收盤的點位，再找最臨近的行權價開倉蝴蝶，蝴蝶的翅膀越窄，最終的收益也就越大。
- 策略证据：基於做市商殺期權原則，本週對於期權要多空雙殺，可以看到，在180的股價上，剛好能同時殺死180 call和put以及其他的所有期權。 || 蝴蝶阿寶週四開倉的蝴蝶策略包括了買入一張177.5 call，賣出兩張180 call，買入一張182.5 call。 || 我判斷因為marvell黑天鵝事件將週四做市商殺期權180的點位移動至了175。 || 我根據英偉達的期權open interest判斷。 || 做蝴蝶策略的核心的技巧方法就是先判斷最終收盤的點位，再找最臨近的行權價開倉蝴蝶，蝴蝶的翅膀越窄，最終的收益也就越大。 || 所以我最終選擇的策略是。
- 回顾证据：截止到13周，我的賬戶已經從12周的136000到了現在的161000，周收益率18.4%，累計收益率3925%。 || 如果3%虧損了，那麼也不傷你根本，再拿3%重新開始繼續提升和完善自己的交易系統。 || 只有一天，最大盈利卻可高達255%。 || 如此一來，如果週五英偉達收盤180，我就能獲得最大盈利。 || 這時候我的賬戶13萬，虧損至10萬。
- 审计判读：butterfly/pin 到期策略；做市商/max pain/pin 推理；方向性 call；put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 10. How I turned 4k to 1million

- 文件：`4JO7DwX3yzI_How I turned 4k to 1million.md`
- 状态：`usable`；正文长度：158994
- 标的：NVDA, META, BTC, ASTS, CAR, TSLA, TSM/TSMC, AVGO, AMD, ETH, ORCL
- 真实交易证据：At the same time, based on the market makers principle of crushing options, predicts that the top three options this week, 177.5, 185 call, and 180 put are very likely to become worthless, meaning the stock price will probably stay below 177.5. || Fans who watched the last video carefully all know that last Friday, which was June 20th, one of the four magical days of the year, I bought the Nvidia 7-Eleven 146 call option right at the close. || I sold one bare call spread from 180 to 182.5, selling one August 1st 180 call and buying one August 1st 182.5 call. || On Thursday, I opened a butterfly position, which involved buying one 177.5 call and selling two 180 calls. || I bought into the vertical call spread strategy in batches at 1.8 and 1.9 and finally sold at 2.45 to take profit, capturing the maximum gain with a 33% return. || After taking profits from my vertical call strategy on Nvidia, I used all 440,000 in profits to buy nearly 2,000 oracle call options at a cost of $2.23 each, entering after the group members. || After the market stabilized, I chose to buy 35 contracts of the 132 strike call option for more recall on Monday, Wednesday, and Friday. || After the market opened on Tuesday, July 8th, a bow bought into the 8160 call option for Nuda Chowo at a cost of 2.9 with your scoring point at 162.9.
- 策略证据：From this chart, you can more intuitively see that ABA's final profit point landed solidly at the position of maximum profit and ABO's 100 million butterfly strategy itself achieved a return rate of 105%. || a round of calls totaling 105,000 contracts, which means there's a high probability the stock price will break through 160 and a gamma squeeze effect will push the price even higher. || On Tuesday, July 15th, Aba analyzed Nvidia's options data for the week and found that the largest open interest position was 130,000 contracts of the July 18th 170 call. || Remember, we just talked about the largest open interest being at the 170 call and that the break even point for both buyers and sellers is at 172.5. || Since this is a strategy involving selling options, when you sell, the return rate will show as 0% at that moment because you've just received the premium and the market price hasn't changed. || If the price closes at max pain on Friday, only 27,000 of the 175 calls will survive.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put；有止盈/出场记录。

### 11. hyWzEnFno_美股期权教学

- 文件：`4_hyWzEnFno_美股期权教学.md`
- 状态：`usable`；正文长度：4198
- 标的：NVDA, TSLA
- 真实交易证据：他在以116.7美金的价格买入10万股英伟达的同时，又卖出了1000张看涨期权，一张看涨期权的期权费为2400美金，所以1000张也就是240万美金。 || 但如果你在3月10号的操作是以220美金的价格买入100股特斯拉股票再卖出期权，那么你最终的收益将是期权费加上上涨带来的2000美金。 || **基础策略四：卖出看跌期权（sell put）** 卖出看跌期权，意思是你愿意在行权价买入股票，并且为了这个承诺，你可以先收取一笔权利金。 || 卖一张covered call是用你100股的股票作为抵押，给别人提供了一个买你股票的机会。 || 期权价格目前处于1.19，在我选择卖出之后，那么我的账户就能立即收到119美元的期权费作为我的收益。 || 如果到了6月20号，英伟达股价没有到达150，那么卖出的期权作废，我可以继续持有我的100股股票。 || 此时，期权买方会行权，而你则需要首先购买100股260元的特斯拉股票，再以240的价格卖出，所以总亏损达到了2000美金。 || 比如英伟达当前股价是110，而你只想买100块钱的英伟达，但是又觉得这个价格很难跌到，那么你就可以选择卖出比如6月20号行权价为100的看跌期权。 || 截止3月28号收盘，这个期权的市场价格是6.7美元。 || 要注意的是，6.7美元所对应的是一股的权利，而一张期权合约捆绑了100股的股票。
- 策略证据：而对于时间价值的崩坏，我们还要小心重大事件后的IV crash，也就是隐含波动率的暴跌。 || IV是隐含波动率的英文，代表市场对未来价格波动的预期。 || 这种不确定性的消失，IV就哗的一下从天上掉了下来，这个现象就叫做IV crash，期权价格也会跟着暴跌，尤其是时间价值的部分，因为希望和赌一把的空间被现实拍扁了。 || 我经常在粉丝群里发布自己最新的期权策略，所以会有很多粉丝朋友想要我科普一下期权的玩法。 || 第一部分我会给大家介绍期权最基础的四种策略。 || 我会用最简单的语言告诉你每个策略是什么，怎么用，能赚多少，同时又有什么风险。
- 回顾证据：如果6月20号股价只到了125，那么我行权后的每股收益就为5美元减去每股6.7的成本，我实际上是每股亏了1.7美元的，其期权的总亏损为170美元。 || 而又因为我已支付了6.7美元每股的期权费，所以真正的净收益是13.3美元。 || 又因为一张期权对应100股，所以总收益为1330美元。 || 但如果最终价格都没有达到120美元，那么你的最大亏损就是你购买期权的成本本金670美元。 || 而又因为我已支付了7.9美元每股的期权费，所以真正的净收益是每股2.1美元，期权总收益为210美元。
- 审计判读：wheel/卖权利金；方向性 call；put/看跌或卖 put；含亏损/回撤复盘。

### 12. 3XOCVlE_Trump币的投资逻辑

- 文件：`4aN_3XOCVlE_Trump币的投资逻辑.md`
- 状态：`usable`；正文长度：1751
- 标的：未抽取到明确标的
- 真实交易证据：英文裡叫buy the rumor, sell the news。 || 特朗普上任後可能會有部分持幣者判斷炒作行情結束，從而拋售創幣，更會有投機者藉機做空。 || 而三個月後，第一批創幣將會被解鎖，允許賣出。
- 策略证据：所以說散戶只是在炒剩下的5%的籌碼，而還有10%用來支撐流動性，剩下的80%全在特朗普手裡。 || 那麼問題來了，創幣暴漲的背後原因有哪些？ || 我認為創幣的暴漲有三個原因。 || 其次，第二點是稀缺性和分发策略。 || 特朗普上任後可能會有部分持幣者判斷炒作行情結束，從而拋售創幣，更會有投機者藉機做空。 || 創幣目前靠的是情緒炒作，沒有技術支撐，也沒有明確的實際應用。
- 回顾证据：第三點則是供給風險。 || 它的高風險和不確定性比大多數傳統投資更誇張。
- 审计判读：有交易证据，但策略类型需人工复核。

### 13. Tutorial of predicting stock price from market makers wiping

- 文件：`4xxY0vJ6WP4_Tutorial of predicting stock price from market makers wiping.md`
- 状态：`download_failed`；正文长度：206
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：v=4xxY0vJ6WP4 All strategies failed: ERROR: [youtube] 4xxY0vJ6WP4: Join this channel to get access to members-only content like this video, and other exclusive perks.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：会员/下载失败内容，不能从正文还原真实交易。

### 14. 美股实盘10万赚100万_要么百万_要么归零

- 文件：`6BwKG7bZcj0_美股实盘10万赚100万_要么百万_要么归零.md`
- 状态：`usable`；正文长度：1720
- 标的：NVDA
- 真实交易证据：於是我說，好了，4月8號尾盤時分，我梭哈了22萬美金，買入了429張4月15號到期的英偉達180看漲期權，價格5.2塊錢。 || 可以看到我成本價5.2買入，7.65賣出，收益率47%，賬戶最終來到了32.8萬。 || 如果你是做市商，在面臨散戶和機構買入如此龐大數字的看漲期權時，而股價又在不斷上行，你會怎麼辦？ || 假設英偉達站上180，180的期權會發生gamma squeeze，那麼做市商會被迫買入股票拉高股價。 || 而當股價拉漲至185，就會發生第三次gamma squeeze，做市商不得不再次買入更多的股票，股價從而繼續拉昇，來到187.5，繼續觸發gamma squeeze。 || 而我就在gamma squeeze後的高點止盈了這張單腿期權。 || 而多頭會接著這個訊息入場推高股價。 || 那麼這麼好的機會，我肯定是順勢而為，只做單腿期權，不做任何組合策略。 || 第二個維度是期權原則。 || 我從期權原則分析，前六的期權全部都是看漲期權，除了190外，其他的都會在一旦股價超過185發生gamma，一口氣來到187.5。
- 策略证据：而當股價拉漲至185，就會發生第三次gamma squeeze，做市商不得不再次買入更多的股票，股價從而繼續拉昇，來到187.5，繼續觸發gamma squeeze。 || 可是本週不一樣，持倉量排名前六的期權清一色都是看漲期權，這就讓我判斷會發生gamma擠壓。 || 而這就是gamma squeeze，有散戶、機構、做市商多方面參與的一場金融戰爭。 || 假設英偉達站上180，180的期權會發生gamma squeeze，那麼做市商會被迫買入股票拉高股價。 || 所以187.5的gamma squeeze就會弱一些，做市商買入的股票就會少一些。 || 我的交易邏輯有兩個維度。
- 回顾证据：可以看到我成本價5.2買入，7.65賣出，收益率47%，賬戶最終來到了32.8萬。 || 沒錯，你會不得不買入大量的正股來對沖風險，從而推動股價的上漲。
- 审计判读：gamma squeeze / OI strike 突破；方向性 call；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 15. axti this stock went up 80x last year

- 文件：`92LyxpDx6sk_axti this stock went up 80x last year.md`
- 状态：`usable`；正文长度：4837
- 标的：AXT/AXTI, CAR, ETH
- 真实交易证据：It had only been [music] 3 short weeks since that bottom fishing move, and the stock price had already reached $115, a 64% return. || When major cloud providers start connecting thousands of GPUs into clusters, the real bottleneck [music] is no longer the GPU chips themselves, but rather the data transmission between GPUs. || As early as the 1950s, aerospace engineers were already using it to describe a material that was theoretically [music] extremely important and had perfect properties, but was almost impossible to actually obtain in reality. || It's called indium phosphide, or InP for short.
- 策略证据：Just a year ago, his stock was trading at less than $2, but all of a sudden, he's holding over $100 million in backlogged orders, >> [music] >> all because the entire wave of AI infrastructure construction is driving demand for this material. || Repricing now isn't just about being aware [music] of the AI boom, it's about aggressively expanding production capacity. || But, at least one thing is certain, the supply bottleneck driving this rally is very real. || But you should look at this 80-fold miracle from a rational perspective.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call。

### 16. 美股实盘挑战4千__100万 第4周

- 文件：`9ev9wiV6eXI_美股实盘挑战4千__100万 第4周.md`
- 状态：`usable`；正文长度：1435
- 标的：NVDA
- 真实交易证据：一列舊賣出，是實打實的韭菜行為，而你以為的止損不過是把帶著血的籌碼親手獻給做市商的腳下。 || 我認為由於上週期權數量過大，會存在做市商周五殺期權這麼一個情況。 || 所以這周理論上，壓制在股價上面的期權壓力消失了。
- 策略证据：我認為由於上週期權數量過大，會存在做市商周五殺期權這麼一個情況。 || 所以這周理論上，壓制在股價上面的期權壓力消失了。 || 一列舊賣出，是實打實的韭菜行為，而你以為的止損不過是把帶著血的籌碼親手獻給做市商的腳下。 || 和幣圈第一大的交易所Coinbase合作，這個IPO一度被認為是2025年最值得期待的IPO。
- 回顾证据：第四周收益67%，累計收益67%。 || 一直跟著阿寶的粉絲應該知道，這周阿寶的倉位一直是英偉達的620140口沒有變過。 || 而這恰恰是最大的錯誤。
- 审计判读：做市商/max pain/pin 推理。

### 17. 美股实盘挑战4千__100万 第3周

- 文件：`AW51OvD1g0g_美股实盘挑战4千__100万 第3周.md`
- 状态：`usable`；正文长度：1392
- 标的：NVDA, BTC, TSLA, AVGO, AMD
- 真实交易证据：这周四个交易日，周二大盘高开，咱踏空了，但这次坚决不追高，所以保持空仓，手头拿着7200刀巨款，等待周三英伟达的财报。 || 而阿宝在周三呢，决定相信哪有赌天天输的逻辑，并且我回测了历史上英伟达财报后的股价表现，我发现5月全部都是大涨，所以这使得我下定决心做多这次5月的财报，在收盘前买入了英伟达620140的call。 || 我在过去一年里满仓做多了4次财报，暴跌了4次，失败了4次，直到今天，我终于对了一次。 || 在周五收盘时，英伟达则止于135，财报后的IBcrash直接把我的期权价格腰斩，挑战本金直接被打回原点。 || 不玩了，退钱，我这个call是620到期，所以一直没有卖。
- 策略证据：而阿宝在周三呢，决定相信哪有赌天天输的逻辑，并且我回测了历史上英伟达财报后的股价表现，我发现5月全部都是大涨，所以这使得我下定决心做多这次5月的财报，在收盘前买入了英伟达620140的call。 || 英伟达的财报说实话有点扑朔迷离，涨跌都有可能，涨的逻辑是之前四次财报，英伟达暴跌了4次，我输了4次，哪有赌天天输啊，所以这次该涨了。 || 那么跌的逻辑呢，之前的4次财报业绩超预期了4次，但暴跌了4次，这个模式还可能延续，总之没法预测，两者都有可能。 || 下周还有博通的财报，我现在判断华尔街比起英伟达更喜欢博通，理由是觉得已经错过了英伟达，认为博通的XPU市场成长率比GPU快。
- 回顾证据：好，让我们来汇总一下美股实盘挑战第三周的战绩，账户回归初始本金4000，周收益率负46%，累计收益率0%。 || 第三周收益回到原点了。 || 英伟达的股性决定了它的持有者大多数都是paperhand，一到财报必定恐慌性抛售股票，这个规律已经在过去的4次财报日全部得到了印证。 || 下周的话，我打算继续扛单，死扛单回本，毕竟只要不卖就不算亏。 || 比特币作为长期投资，而国债作为分散风险的投资。
- 审计判读：方向性 call；含亏损/回撤复盘。

### 18. CAR史诗级逼空_全网最全解析

- 文件：`DSRAGDRAf4I_CAR史诗级逼空_全网最全解析.md`
- 状态：`usable`；正文长度：1231
- 标的：未抽取到明确标的
- 真实交易证据：逼空是空頭最慘的死法，所謂逼空是指股價上漲，迫使做空者回補股票，而這種買盤會進一步推高股票價格。 || 隨著股價上漲，空頭需要回補，Swaps的對手方券商也需要買入股票對沖，而兩個最大的股東SRS和Water持倉不賣，導致了如今的事實級逼空。 || 但是我認為如果Water它的早期建倉時間是在6個月之前，那麼他們可以隨時止盈出售部分的頭寸，大幅獲利。
- 策略证据：未抽取到明确策略句。
- 回顾证据：根據Barance的計算，除開這兩家機構手頭的正股倉位，如果再包括他們手上持有的Equity Swaps，這兩家投資者的合計持股比例達到流通在外總股本的107%。 || 安菲市目前的估值昂貴，如果對應2026年預計每股收益近4美元的市盈率則是超過了150倍。 || 根據彭博社資料，截止3月31號，該股的空頭倉位為900萬股。 || 首先，安菲市可能會利用股價上漲的機會發行新股，公司在2月底提交了檔案，計劃透過華爾街銷售代理的形式，以市場價格最多發行500萬股。 || 其次，最關鍵的問題是股價上漲是否會促使SRS或Water出售部分股份以兌現近期的鉅額收益。
- 审计判读：有止盈/出场记录。

### 19. 比特币的投资逻辑

- 文件：`E4oBNq7hogM_比特币的投资逻辑.md`
- 状态：`usable`；正文长度：1611
- 标的：BTC, LNG/Oil
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：首先，纸币作为货币是没有任何内在价值的，因为它没有黄金及其他商品来支撑价值。
- 回顾证据：危机期间，许多大型机构面临破产风险，导致政府不得不实施大规模救助，这暴露了银行中心化控制的弊端和作为经济中心的系统性风险。 || 首先，比特币通过区块链技术实现去中心化，没有任何单一机构比如银行或者政府能够控制比特币的发行或交易，这消除了传统金融体系中对银行的依赖，减少了系统性风险。
- 审计判读：本集偏宏观/主题/估值分析，未抽到明确实盘买卖。

### 20. M_从0到1_从人类最基础的需求看投资

- 文件：`EHMVcjiA5_M_从0到1_从人类最基础的需求看投资.md`
- 状态：`usable`；正文长度：760
- 标的：LNG/Oil
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：未抽取到明确策略句。
- 回顾证据：今天不講股票，不講收益，我們只講一件事：世界是靠很多次從0到1一點一點走到我們面前的。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 21. My Bitcoin Prediction

- 文件：`FplFJQ-Tp-c_My Bitcoin Prediction.md`
- 状态：`usable`；正文长度：6033
- 标的：BTC, CAR, LNG/Oil
- 真实交易证据：First, we need to know that Bitcoin was proposed on October 31st, 2008 by a netzen named Satoshi Nakamoto through a published paper and this was shortly after the outbreak of the financial crisis. || Just like not all rare minerals have collection value and not all limited edition products will be bought by people. || And many people also like to buy gold jewelry to adorn themselves.
- 策略证据：The total supply of Bitcoin is only 21 million, and nearly 20% of the total has been permanently lost. || Although Bitcoin has no intrinsic value and is not backed by governments or central banks, its decentralized mechanism, meaning governments and central banks cannot control its issuance and transactions is the key to giving it value. || So, many people believe that the scarcity brought by the limited total supply gives Bitcoin its value. || You trust that they can effectively formulate policies to manage fiat currency to avoid vicious inflation. || And this trust has reached a consensus among global Bitcoin users, including you, which is what gives Bitcoin its value. || First, we need to know that Bitcoin was proposed on October 31st, 2008 by a netzen named Satoshi Nakamoto through a published paper and this was shortly after the outbreak of the financial crisis.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：有交易证据，但策略类型需人工复核。

### 22. 美股实盘500美金_赚到曼哈顿大平层 第1周

- 文件：`GLYtjhCpFX8_美股实盘500美金_赚到曼哈顿大平层 第1周.md`
- 状态：`empty`；正文长度：0
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：未抽取到明确策略句。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：空 transcript，无法审计。

### 23. 0cV8_Takeaways from trading 4k to 1million

- 文件：`HuB53g_0cV8_Takeaways from trading 4k to 1million.md`
- 状态：`usable`；正文长度：7150
- 标的：CAR, ETH
- 真实交易证据：As for me, I believe my fade is the process of constantly trading options, experiencing repeated wipeouts and comebacks over and over until one day I truly understand and transform fade into luck. || It means calling a bed even when you know there's risk, yet you still choose to go for it with conviction. || If you want to go far on the road of investing, you first have to learn how to survive for the long haul. || But the term I admire even more is hero call. || If you chase perfection too much, you'll end up falling short everywhere.
- 策略证据：All I hope is that someday when chatting with friends over tea or a meal or bragging online, I can smile knowingly and say, "Back in the day, I witnessed a bow's live trading with my own eyes." Because what I cherish most more than any number is this unique memory we created together. || But if you still want to wish me well, then wish that I don't lose my footing on the edge between madness and reason, and that I can still pull the trigger when everyone else thinks I should give up. || If someone can survive by trading, you don't need to ask how smart they are, nor should you envy how much money they've made. || But every time I bounced back and doubled my money, doing even better than before. || We should turn our obsession with not losing in investing into the courage to give it our all to win. || After all, the biggest regret in life is never losing after giving it your all, but not having the courage to start when you could have won.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call。

### 24. 伟大的人生_不需要很多朋友

- 文件：`IGxlZJVC4k8_伟大的人生_不需要很多朋友.md`
- 状态：`usable`；正文长度：1135
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：去年年末、新年開始，我承受了很大很大的壓力。
- 回顾证据：🎼 做交易的時候，你得自己承擔盈虧；做自媒體的時候，你得自己面對質疑和冷清。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 25. meta王者归来

- 文件：`JQif0N-yUKU_meta王者归来.md`
- 状态：`usable`；正文长度：1033
- 标的：NVDA, META, TSLA
- 真实交易证据：自1月26號起，META、特斯拉、英偉達這些M7股票新增了週一、週三到期的末日期權。 || 而且近期美股期權市場還有一個大事情需要我們關注。 || 現在一週三個末日期權，可以預見的是，股價整體的波動將會被進一步的放大。 || 那我們就可以在木木的期權策略這裡選擇。 || 我們認為META將會劇烈震盪，那系統便會給我們推薦買入跨市策略，這是一個很正確的策略。 || 而且目前在木木上買賣美股ETF期權都是零佣金。 || 零佣金和合約費對於我們這種經常做期權的人來說，真的可以省下不少錢了。
- 策略证据：從判斷上看，我確實領先於市場，但節奏錯位，讓我沒能熬過黎明前的最後一段黑暗。 || 說明它的增長勢頭還是保持強勢的，這也是我一直看好它的原因。 || 那我們就可以在木木的期權策略這裡選擇。 || 我們認為META將會劇烈震盪，那系統便會給我們推薦買入跨市策略，這是一個很正確的策略。
- 回顾证据：現在透過我的連結，開戶入金最高還可獲得1000美元的英偉達股票加閒置資金8.1%的收益。 || META的財報馬上要公佈了，我們打開木木，點進META個股頁面，點選公司即可看到META 25年Q4的財報，預測營收584.59億，每股收益是在8.21，同比是上漲的。 || 而且這裡盈利虧損都給你算得明明白白，一鍵就能上車。 || 當一個行業裡水平相同的公司都定價在一個遠比其中一家更高的PE的時候，這就是市場的錯誤定價。 || 那點進財報站裡面還可以看到更多的關鍵資訊，比如META近幾個季度的營業收入、每股收益的走勢等等。
- 审计判读：含亏损/回撤复盘。

### 26. 为什么美股财报好股价跌_如何做空波动率_

- 文件：`KdhFH6IeBIg_为什么美股财报好股价跌_如何做空波动率_.md`
- 状态：`usable`；正文长度：1882
- 标的：NVDA, TSLA, ORCL
- 真实交易证据：做多做空波动率最常用的期权策略包括straddle、strangle、butterfly、iron condor。 || 在理解这些基本的理论之后，IV如果比RV低很多，那说明期权便宜，我就会考虑做多波动率，做期权的买家；IV如果比RV高很多，那说明期权贵，我就会做空波动率，做期权的卖家。 || 长期是buy and hold，买了就不动一直拿着的逻辑，而短线是buy low, sell high，低点买入高点卖出的逻辑。 || 做多和做空隐含波动率的方法有哪些？ || 怎么选择开仓和平仓时机？ || 究竟是做空还是做多波动率，取决于你是卖家还是买家？ || 卖家就是做空，买家就是做多波动率。 || 平仓的时机，因为这类策略，卖家都是吃theta的，时间流逝一般对于做空波动率有利。 || 其中，跨式策略最为稳健，蝴蝶策略收益上限最高。 || 阿宝自己更喜欢蝴蝶，因为我喜欢追求利润的最大化最优解。
- 策略证据：在理解这些基本的理论之后，IV如果比RV低很多，那说明期权便宜，我就会考虑做多波动率，做期权的买家；IV如果比RV高很多，那说明期权贵，我就会做空波动率，做期权的卖家。 || 这其中真正的逻辑是，首先甲骨文爆出的积压订单收入达到惊人的4550亿美元，这样在历史上都极为罕见的数字，实则明牌了未来的营收；再者则是甲骨文在capex资本开支的炸裂式增长，市场理解为公司在加大投资，抢占未来增长，这意味着长期成长空间更大。 || 做多做空波动率最常用的期权策略包括straddle、strangle、butterfly、iron condor。 || 平仓的时机，因为这类策略，卖家都是吃theta的，时间流逝一般对于做空波动率有利。 || IV是隐含波动率，代表了市场对未来会有多么剧烈波动的预期。 || 为什么财报表现与股价反应经常不一致，同样是财报好，有的股票会暴涨，有的却大跌，背后到底是什么逻辑？
- 回顾证据：过去6次英伟达财报我亏了6次，基本上是全亏的，但是财报本身6次都是超预期的。 || 有的哈，我目前正在训练AI研发一个会和我一样思考分析市场数据、制定交易策略、执行交易计划、监测资产组合的机器人阿宝，期待有一天能和大家见面。 || 其中，跨式策略最为稳健，蝴蝶策略收益上限最高。 || 如果IV比RV高很多，那说明市场把未来的风险夸大了，期权定价就比较贵，所以此时卖期权可能更划算。 || 如果IV比RV低很多，那说明市场低估了风险，这时候期权相对便宜，那么这个时候买期权可能更有性价比。
- 审计判读：butterfly/pin 到期策略；含亏损/回撤复盘。

### 27. 美股实盘挑战4千__100万 第10周

- 文件：`Knve5q0x-xs_美股实盘挑战4千__100万 第10周.md`
- 状态：`usable`；正文长度：4052
- 标的：NVDA, AVGO
- 真实交易证据：阿寶的策略有兩個組成部分，買入一張NVIDIA 7月25號的165 put，賣出一張NVIDIA 7月25號的167.5 put。 || 週五一早，我平倉了原來的165至167.5 put的垂直價差，新開了一組170至172.5的put垂直價差。 || 阿寶在這裡解釋一下，因為這是賣出期權的策略，所以當你賣出的那一刻，收益率會顯示為0%，因為權利金剛到手，市場價沒有變化。 || 以一組垂直價差的組合策略為例，整個策略需要鎖定250刀保證金，並獲得78刀的權利金。 || 鑑於宏觀層面相對穩定，且阿寶的垂直價差在週四就已經吃完了95%的最大盈利。 || 第一組的垂直價差，阿寶收益率是37%，第二組的垂直價差，我的收益率是5%，共計43%。 || 不出我所預料的，NVIDIA橫盤在了173.5，而阿寶的170至172.5的垂直價差獲得了最大盈利，策略收益率100%。 || 這週NVIDIA收盤和上週收盤比，股價幾乎沒有變化，但阿寶憑藉著垂直價差獲利43%，而這就是在股價的方寸波動之間，又一次完成了刀尖上的華爾茲，贏得今天收益。 || 所以在上週五橫盤止盈之後，我選擇了空倉蟄伏，避開即將到來的下跌，並等待一個更好的入場時機。 || 股市裡賺錢的道理其實很簡單，在股票漲之前做多，在橫盤之前做空波動率，在下跌之前空倉。
- 策略证据：阿寶的策略有兩個組成部分，買入一張NVIDIA 7月25號的165 put，賣出一張NVIDIA 7月25號的167.5 put。 || 以一組垂直價差的組合策略為例，整個策略需要鎖定250刀保證金，並獲得78刀的權利金。 || 阿寶在這裡解釋一下，因為這是賣出期權的策略，所以當你賣出的那一刻，收益率會顯示為0%，因為權利金剛到手，市場價沒有變化。 || 不出我所預料的，NVIDIA橫盤在了173.5，而阿寶的170至172.5的垂直價差獲得了最大盈利，策略收益率100%。 || 這個時刻，如果我們詳細的分析一下垂直價差策略的勝率，我們會發現NVIDIA的期權隱含波動率IV所計價的價格波動區間在169.69到176.08。 || 阿寶所使用的這一套垂直價差策略是做市商常見的套利方法。
- 回顾证据：最大虧損是250減78，172刀，最大盈利是78刀，最大收益率是78除以250，也就是31.2%。 || 週四正如阿寶所預判的一樣，在週三那麼多明確的利好進場信號之後，大資金開始瘋狂湧入NVIDIA，而NVIDIA股價節節攀升，來到了173，而阿寶的賬戶也隨之來到了8000，收益95%。 || 不出我所預料的，NVIDIA橫盤在了173.5，而阿寶的170至172.5的垂直價差獲得了最大盈利，策略收益率100%。 || 首先，盈虧比清晰，你知道最壞的情況，也就是虧172刀，最好的情況是賺78刀。 || 最後是收益率高，31.2%的收益率在3天內完成是非常高效的交易。
- 审计判读：defined-risk 垂直价差；put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 28. 美股实盘挑战4千__100万 第11周

- 文件：`LQf5fmykRQg_美股实盘挑战4千__100万 第11周.md`
- 状态：`usable`；正文长度：3972
- 标的：NVDA, META
- 真实交易证据：早上9點50分，我按計劃開倉了180到182.5的熊市垂直價差策略：賣出一張8月1號180 call，買入一張8月1號182.5 call。 || 如果我們再來看8月1號這一週的期權未平倉倉位，排名第一的是94000張177.5 call，緊接著的是89000張185 call和71000張180 call。 || 熊市垂直價差策略有兩個組成部分：買入一張182.5 call，賣出一張180 call。 || 與此同時，阿寶根據做市商殺期權原則判斷，這周排名前三的期權177.5、182.5、180 call大機率會直接變成廢紙，也就是說股價會停留在177.5之下。 || 180 call有18.8萬張未平倉，當前夜盤的漲幅是Gamma squeeze和非理性的狂熱情緒造成的。 || 根據做市商殺期權原則和吸引力原則，股價在週五會跌下180，將180 call全部殺死。 || 阿寶的熊市垂直價差策略，在週五獲得了10%的最大盈利，贏取了全部的權利金。 || 不同於你們常見的透過做空正股或者直接購買puts來做跌，阿寶選擇了一個截然不同的方式：垂直價差，也就是熊市垂直價差。 || 急速上漲的市場又有外加空倉，我想大多數人都會感到豐滿和焦慮，畢竟做多是屬於羊群的狂歡，可我終究不適應這樣。 || 它是基於期權市場的未平倉合約計算得出的理論價格，通常反映了市場中期權買家和賣家之間的博弈。
- 策略证据：與此同時，阿寶根據做市商殺期權原則判斷，這周排名前三的期權177.5、182.5、180 call大機率會直接變成廢紙，也就是說股價會停留在177.5之下。 || 根據做市商殺期權原則和吸引力原則，股價在週五會跌下180，將180 call全部殺死。 || 熊市垂直價差策略有兩個組成部分：買入一張182.5 call，賣出一張180 call。 || 早上9點50分，我按計劃開倉了180到182.5的熊市垂直價差策略：賣出一張8月1號180 call，買入一張8月1號182.5 call。 || 180 call有18.8萬張未平倉，當前夜盤的漲幅是Gamma squeeze和非理性的狂熱情緒造成的。 || 阿寶的熊市垂直價差策略，在週五獲得了10%的最大盈利，贏取了全部的權利金。
- 回顾证据：如果我們再來看8月1號這一週的期權未平倉倉位，排名第一的是94000張177.5 call，緊接著的是89000張185 call和71000張180 call。 || 早上9點50分，我按計劃開倉了180到182.5的熊市垂直價差策略：賣出一張8月1號180 call，買入一張8月1號182.5 call。 || 而週五收盤股價有74%的機率低於180，只要低於180，阿寶就可以實現巨大盈利。 || 阿寶的熊市垂直價差策略，在週五獲得了10%的最大盈利，贏取了全部的權利金。 || 至此共計11周的時間，累計收益率2% 625%，算上本金一共翻了27.25倍。
- 审计判读：defined-risk 垂直价差；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put。

### 29. 美股实盘挑战4千__100万 第6周

- 文件：`MBXlJXlw9aE_美股实盘挑战4千__100万 第6周.md`
- 状态：`usable`；正文长度：1901
- 标的：NVDA, TSLA
- 真实交易证据：週四英偉達155高開，由於到期平倉期權數量中最多的是109000張，這周5到7的155 call。 || 6月24號週二SP500漲幅1.1%，那指上漲1.4%，英偉達順勢來到了147.9，而阿寶的賬戶也是搭上了和平順風車來到了9800，這張146 call漲幅40%。 || 而選擇在這裡獲利了結7/11 146 call 3.6的成本，6.75止盈，賬戶從而來到了13000。 || 阿寶根據Gamma原則判斷，週五股價有機率產生Gamma squeeze一口氣突破157，所以大膽買入了7/18 155 call。 || 7/11 146 call阿寶的成本在3.6，這也就意味著7月11號當天149.6會是我的盈虧平衡點。 || 在此之後，阿寶也是分析了英偉達這週期權的資料，發現在147到150區間存在大量的未平倉合約，而股價又站上了147.9，說明了這周很可能會發生Gamma squeeze，股價一口氣衝到149。 || 如果你是做市商，在面臨散戶和機構買入如此龐大資料的看漲期權，而股價又在不斷上行時，你會怎麼辦？ || 而隨著股價上漲，虛值期權變為實值，期權的Gamma陡然增大，做市商需要加速買入更多正股，來維持對沖，形成買入、漲價，更多買入的惡性循環。 || 我曾經在往期的影片中和大家提到過，英偉達的期權很大程度上決定了英偉達股票的價格。 || 在這週五，總共有40萬張看漲期權集中在147到155的價格。
- 策略证据：阿寶根據Gamma原則判斷，週五股價有機率產生Gamma squeeze一口氣突破157，所以大膽買入了7/18 155 call。 || 而這就是Gamma squeeze，有散戶機構、做市商多方面參與的一場金融戰爭，而149也並非這次Gamma squeeze的終點，6月25號週三，股價更是來到了154的歷史新高點。 || 在此之後，阿寶也是分析了英偉達這週期權的資料，發現在147到150區間存在大量的未平倉合約，而股價又站上了147.9，說明了這周很可能會發生Gamma squeeze，股價一口氣衝到149。 || 而隨著股價上漲，虛值期權變為實值，期權的Gamma陡然增大，做市商需要加速買入更多正股，來維持對沖，形成買入、漲價，更多買入的惡性循環。 || 如果你是做市商，在面臨散戶和機構買入如此龐大資料的看漲期權，而股價又在不斷上行時，你會怎麼辦？ || 我們顯然6月27號週五的走勢和預料的一樣，產生了Gamma squeeze。
- 回顾证据：第六隻收益129%，累計收益310%。 || 7/11 146 call阿寶的成本在3.6，這也就意味著7月11號當天149.6會是我的盈虧平衡點。 || 而阿寶牢記眾人恐慌，我貪婪眾人貪婪，我恐慌。 || 在群友們一致貪婪的時候，我聽見了恐慌的聲音。 || 我們又盈利了。
- 审计判读：gamma squeeze / OI strike 突破；方向性 call；有止盈/出场记录；含亏损/回撤复盘。

### 30. 美股实盘500美金_赚到劳斯莱斯 第2周

- 文件：`Nom8aoicVdM_美股实盘500美金_赚到劳斯莱斯 第2周.md`
- 状态：`usable`；正文长度：2972
- 标的：SPY, ETH, LNG/Oil
- 真实交易证据：所以我選擇在開盤 9 點 31 分於 22.8 左右買入了行權價 23 塊錢的看漲期權，並於同天下午 3 點 11 分在 23.4 的價格賣出。 || 而這張看跌期權卻因週二繼續高開而止損，並同時我將這張看跌期權換成了 6 月 18 號的 200 put。 || 而最終開花結果，CPU 整個板塊最終於 GTC 情緒過後 3 點鐘準時開始跳水，並在隔天於 88 塊錢低開之後，我選擇獲利了結這張看跌期權。 || 我在這裡簡單解釋一下：6 月 18 號 200 put 所帶來的一個典型的 convex payoff，也就是凸性收益。 || 如今這個市場因為戰爭而導致的黑天鵝事件層出不窮，買這個看跌期權的費用不高，但是黑天鵝導致的市場暴跌卻能讓這個 put 的收益成指數性上漲，而且因為時間夠久，離到期 6 月 18 號還好幾個月，theta 衰減得很慢，又因為黑天鵝發生時間點難以預測，所以也同時給了我很多時間等待事件的發生。 || 我在週四開盤之後買入了兩張 venture global 的看漲期權，只買兩張顯得稍微有些保守，是因為我覺得入場時的價格太高，波動太大。 || 在某一特定的板塊，我只會做多或者做空特定的標的，這樣也能讓我減少不必要的交易，從而可以把精力和注意力更有效地利用起來。 || 在這裡給大家稍微提醒一下我在第一週所提到的避險交易做法：做空高估值科技股，做空小盤股，做多石油股。 || 由於 ETH 以太坊自 3 月 9 號就開始了底部的反彈行情，3 月 13 號週五比滿成交量放大，走出了之前的震盪箱體，所以可以說，只要在突破或回落時買入，就有機會吃上這一波的向上趨勢。 || 所以這無疑是增加了賣壓，也是空頭入場做空的底層原因。
- 策略证据：其實空這家公司還有另外一個原因，也是讓我下定決心去空它的底層邏輯，那就是 3 月 12 號盤後 applied upto 宣佈了 2.5 可以市值的股票散發計劃，並會以 ed money 的形式在盤中出售其股票。 || 由於 ETH 以太坊自 3 月 9 號就開始了底部的反彈行情，3 月 13 號週五比滿成交量放大，走出了之前的震盪箱體，所以可以說，只要在突破或回落時買入，就有機會吃上這一波的向上趨勢。 || 大家好啊，最近因為身體的原因，所以推遲了第二週影片的錄製，在這裡還是希望大家能夠在忙碌的生活中注意健康。 || 所以這種市場有幾個非常典型的特徵：沒有持續的趨勢，高波動但低確定性，情緒驅動大於基本面，頻繁假突破和假跌破。 || 盤中，我看到 CPU 板塊的 apply upto 有大量資金獲利了結，半小時線不僅一直被 VWAP 壓制，並且在接近中午的時間跌破了周線。 || 所以這無疑是增加了賣壓，也是空頭入場做空的底層原因。
- 回顾证据：我在這裡簡單解釋一下：6 月 18 號 200 put 所帶來的一個典型的 convex payoff，也就是凸性收益。 || 其實空這家公司還有另外一個原因，也是讓我下定決心去空它的底層邏輯，那就是 3 月 12 號盤後 applied upto 宣佈了 2.5 可以市值的股票散發計劃，並會以 ed money 的形式在盤中出售其股票。 || 我自己也曾提醒自己，老是想著吃完所有盈利，只會害了自己，可是人呢，總是在貪婪面前顯得那麼不堪一擊。 || 如今這個市場因為戰爭而導致的黑天鵝事件層出不窮，買這個看跌期權的費用不高，但是黑天鵝導致的市場暴跌卻能讓這個 put 的收益成指數性上漲，而且因為時間夠久，離到期 6 月 18 號還好幾個月，theta 衰減得很慢，又因為黑天鵝發生時間點難以預測，所以也同時給了我很多時間等待事件的發生。 || 我低估了 2026 年 OFC AI Infrastructure 會議給光摩快速帶來的 buff 加成，最終吞下了貪婪的苦果。
- 审计判读：方向性 call；put/看跌或卖 put；有止盈/出场记录。

### 31. 为什么你一卖股票就涨

- 文件：`OSUcQAxjZl0_为什么你一卖股票就涨.md`
- 状态：`usable`；正文长度：1018
- 标的：NVDA
- 真实交易证据：好，首先啊我們仔細想一想，咱們小韭菜什麼時候最容易賣出？ || 利空的新聞出現了大盤暴跌，沒估完了，這個時候小散戶最容易把手上的股票賣出去。 || 而當很多人在同一時間賣出時，市場就會發生一些很有意思的事情。 || 比如說對沖基金long show hedge fund。 || 那些更關注公司基本面，忽略短期噪音的大玩家們，也會開始慢慢買入建倉。
- 策略证据：未抽取到明确策略句。
- 回顾证据：恐慌的時候，對不對？ || 當買盤大於賣盤價格往上，當賣盤大於買盤，價格往下，所恐慌的時候是什麼？ || 這就是為什麼股票會在恐慌時快速的下跌。 || 所以大家一定要意識到，對於一家好的公司，市場其實從來都不會缺買家，只是在恐慌的時候，買家只願意用更低的價格去買。
- 审计判读：有交易证据，但策略类型需人工复核。

### 32. _880k to _1_35M Live Stock Trading

- 文件：`QBwGO6U9H9w__880k to _1_35M Live Stock Trading.md`
- 状态：`usable`；正文长度：13850
- 标的：META, AMD, ETH, LNG/Oil
- 真实交易证据：After analyzing the macro option structure, I also found from the micro option structure that the 105 calls and the 100 calls are overwhelmingly dominant, each with over 10,000 open interest contracts. || Looking at the macro structure options, I noticed that AS's options trading volume has surged, ranking 12th among all US stocks, right alongside Amazon, Microsoft, and AMD. || And along with this news, there was also unusual activity in the capital flows with a large amount of money pouring into the space sector getting in early to take positions. || And if we look at the put call ratio, we'll see that among the top 13 stocks with the lowest ratios, the put call ratios are all between 0.3 and 0.9. || I believe the recent drop stems from short-term negative sentiment and unfavorable trading mechanisms. || When it comes to using KDJ, you really just need to remember four words, oversold and golden cross. || Next, let's look at a real example with focus your attention on the chart, specifically the period from early May to midMay. || In technical analysis, this area is called the oversold zone. || In technical analysis, this move is called a bullish crossover at a different position. || And you have to realize AS is just a small cap company, yet its options volume is on par with these giants.
- 策略证据：After analyzing the macro option structure, I also found from the micro option structure that the 105 calls and the 100 calls are overwhelmingly dominant, each with over 10,000 open interest contracts. || v=QBwGO6U9H9w TITLE: $880k to $1.35M Live Stock Trading TRANSCRIPT: Life is like a play, and I want to try to become the main character in my own story. || We'll divide the $3.7 trillion projected market cap by this diluted 1 billion share total. || So, let's be a bit more conservative and set it at 75%. || 3.7 trillion market cap divided by 1 billion shares equals $3,700 per share. || The indicator I'm using, let me first give a quick explanation for those who aren't familiar with it is the KDJ.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put。

### 33. Why I invested in Nvidia

- 文件：`QGLMOYzlRsc_Why I invested in Nvidia.md`
- 状态：`usable`；正文长度：15706
- 标的：NVDA, META, CAR, TSLA, AMD, ETH
- 真实交易证据：Today, data center operations have long become [music] Nvidia's largest source of revenue, accounting for nearly 80% and its market share [music] has reached an impressive 90%. || The essence of the stock market is the monetization of your understanding of the market, and the process of accumulating this knowledge is both arduous and lengthy, but when you finally break out of your cocoon and become a butterfly, all the patience you've enjoyed will eventually have its day to erupt. || This tiny little thing dramatically boosted the graphics quality of computer games. || Gamers were so moved, they were practically in tears because they had never played such realistic computer [music] games in their lives. || All the effort, hardships, and failures you experience along the way, once you reflect seriously and persist, will ultimately become your assets [music] and help propel you towards success. || So today, I'm putting on a leather jacket and channeling Jensen Huang to talk with you all about him and Nvidia. || At first, Jensen Huang had rather narrow market positioning for Nvidia, planning to just make graphics cards and sell them to gaming companies. || Jensen Huang realized that CPUs could not only handle [music] graphics rendering, but could also excel in big data and AI computing. || So, Nvidia began a major transformation introducing GPUs into the field of artificial intelligence computing.
- 策略证据：Today, data center operations have long become [music] Nvidia's largest source of revenue, accounting for nearly 80% and its market share [music] has reached an impressive 90%. || In the face of adversity, however, Jensen Huang decisively changed the business strategy, carried [music] out sweeping reforms of the company's operations, and boldly made strong statements to the market. || [music] He said that since Nvidia was able to survive the brutal competition of the past, it would surely be able to seize its share in the markets of the [music] future. || Whether it's autonomous driving, medical imaging, or scientific research, many fields have started using Nvidia's GPUs, [music] and the company's market value has skyrocketed as a result. || Nvidia's Drive system [music] not only calculates routes, but can also recognize obstacles and automatically avoid pedestrians. || As we come to the end of this video, I too feel a bit envious and would like to offer some words to all the retail investors still striving in the stock market.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：butterfly/pin 到期策略；方向性 call；put/看跌或卖 put。

### 34. 美股实盘500美金_赚到桑塔纳

- 文件：`R2QgAxo6iUs_美股实盘500美金_赚到桑塔纳.md`
- 状态：`usable`；正文长度：1286
- 标的：MU, Russell 2000, LNG/Oil
- 真实交易证据：所以我在週三大盤拉高之後，就開始了這周的避險交易，包括空小盤股羅素2000、買LNG標的，以及做空CPU中的Applied Optoelectronics。 || 前兩者是在看到伊朗和設施被炸的消息之後，大盤跳水並重新拉高之後買入的。 || 而今天3月16號，Applied Optoelectronics開盤即跳水5個點，我則是果斷了結了手裡的看跌期權。 || 兩層的負面訊號疊加，是我做空頭的底層邏輯。 || 美光的日線布林帶下軌在354，所以在價格下穿354之後，我就選擇了止盈。
- 策略证据：Applied Optoelectronics是看到CPU龍頭Lumentum在週三資金獲利了結，卻沒有承接盤之後所做出的判斷。 || 兩層的負面訊號疊加，是我做空頭的底層邏輯。
- 回顾证据：他在和談時所擺出的傲慢態度，所提供的15點談判條件，在這期間甚至計劃派出路面部隊，並同時依舊源源不斷地進行轟炸，讓參與市場的我們沒有辦法做到不交易。 || 如果動了貪心，則會被教訓到體無完膚。 || 整個板塊的資金都在撤離，加上大盤的恐慌情緒拋售。 || 所以在我浮虧的時候，我也能夠拿得住。 || 那麼你們可以看到，我今天賺了500，而其中有一部分收益是未實現收益。
- 审计判读：put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 35. Analysis of MSTR

- 文件：`RLdwlBtQdvU_Analysis of MSTR.md`
- 状态：`usable`；正文长度：10977
- 标的：MSTR, BTC, ETH
- 真实交易证据：And on the other hand, from a debt perspective, MSTR in the past five years issued a total of nearly $7.3 billion of convertible bonds to buy Bitcoin. || Long after MSTR rose to 500, I, Bao, advised my followers to take profits at the $500 mark. || Quantum [music] computing can greatly accelerate the cracking of the encryption algorithms that Bitcoin security relies on and subvert the mining process and the constitution [music] of the Bitcoin protocol, thereby threatening Bitcoin security. || But in fact, according to what I've heard from a colleague at MIT, a PhD student specializing in quantum computing, the practical application of quantum computing is still a long way off, at least 10 years or more. || To reverse the impending bankruptcy, [music] company executives led by CEO Michael Saylor decided to throw in all the cash to buy Bitcoin as a hedge against inflation and as a means of capital appreciation. || They used all the company's cash to buy Bitcoin and then use some of the Bitcoins as collateral, mortgage to the bank so continue to lend to banks, go buy more Bitcoins. || Buying Bitcoin or buying shares in MSTR, basically they are optimistic about the rise of Bitcoin. || It's a financial instrument that combines a bond with a call option on the company stock. || This method is also highly unlikely to be feasible when Bitcoin falls sharply because if Bitcoin's price drops, the stock price will follow and investors won't buy MSTR's convertible bonds.
- 策略证据：v=RLdwlBtQdvU LANG: en TRANSCRIPT: As Bitcoin's price breaks through $100,000, listed [music] companies that focus on investing in Bitcoin and MicroStrategy MSTR in particular have also become the focus of much attention. || And on the other hand, from a debt perspective, MSTR in the past five years issued a total of nearly $7.3 billion of convertible bonds to buy Bitcoin. || [music] The price of Bitcoin fell from an all-time high of $60,000 to $30,000 by the end of May. || Bitcoin from $100 to $100,000, >> [music] >> MSTR from obscurity to a hot topic, these are all myths of getting rich. || To reverse the impending bankruptcy, [music] company executives led by CEO Michael Saylor decided to throw in all the cash to buy Bitcoin as a hedge against inflation and as a means of capital appreciation. || And because its market value is mainly derived from the value of its Bitcoin holdings, we can use MSTR's [music] market value and the amount of Bitcoin held to back calculate the price of Bitcoin.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put；有止盈/出场记录。

### 36. 英伟达车轮策略第二战_胜率100__

- 文件：`Rd30zvqmRvM_英伟达车轮策略第二战_胜率100__.md`
- 状态：`usable`；正文长度：1297
- 标的：NVDA
- 真实交易证据：在2月17號到2月20號這一個短週，阿寶判斷2月20號週五，英偉達將收在190附近，sell 190 put就是我的選擇。 || 首先我們看到2月3號到期的期權當中，排名前列的put基本上都是處於深度價外。 || 這個行權價為182.5的call是看漲期權中數量最大的，最容易成為市場集中的博弈點位。 || 所以我們就可以合理推斷出，2月13號週五，英偉達股價將大機率收在182.5，而隨後的操作也就是很自然地賣出了182.5的put。 || 這類期權到期歸零的機率極高，所以我們基本可以忽略不計。 || 真正值得關注的是call這一側。 || 根據做市商殺期權原則，在週五2月13號，股價會向182.5靠近，以此殺死182.5及其以上的所有看漲期權。 || 而我們再結合2月3號的max pain來看，max pain處於182.5，也就是說做市商會傾向於在到期日將股價控制在最大痛點的位置，讓儘可能多的期權失效。
- 策略证据：在2月17號到2月20號這一個短週，阿寶判斷2月20號週五，英偉達將收在190附近，sell 190 put就是我的選擇。 || 2月9號到2月13號這一週，我們在週一依舊是透過做市商殺氣權原則配合著，來判斷英偉達13號週五的點位。 || 對於做市商殺氣權原則或者max pain不太瞭解的新朋友們，你們有兩個選擇，一是重溫阿寶4000到100萬的挑戰第一季和第二季，這些都是免費的。 || 當英偉達的股價如此強勢時，基於基本面與市場情緒的雙重支撐，的確容易讓人產生還能繼續的慣性判斷。 || 根據做市商殺期權原則，在週五2月13號，股價會向182.5靠近，以此殺死182.5及其以上的所有看漲期權。 || 而我們再結合2月3號的max pain來看，max pain處於182.5，也就是說做市商會傾向於在到期日將股價控制在最大痛點的位置，讓儘可能多的期權失效。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：wheel/卖权利金；做市商/max pain/pin 推理；方向性 call；put/看跌或卖 put；含亏损/回撤复盘。

### 37. 美股实盘挑战4千__100万 第15周

- 文件：`T31cwleAVMI_美股实盘挑战4千__100万 第15周.md`
- 状态：`usable`；正文长度：2974
- 标的：NVDA, ORCL
- 真实交易证据：阿寶的末日蝴蝶加看跌垂直價差這兩套策略一共取得了100%的收益。 || 我一共建倉了405組180和182.5的熊市垂直價差，成本0.25。 || 在英偉達股價178的時候，阿寶開倉了做空策略——熊市垂直價差。 || 如果此時再來分析新的期權未平倉數據，根據做市商殺期權原則，182.5、185、180的call肯定是要殺的。 || 我從週一便開始空倉等風起，等不到我想要的風，我絕不開倉，繼續保持蟄伏。 || 支撐我做出這一交易決策的數據，是英偉達未平倉的期權數據。 || 可以看到，未平倉數量最大的正是11萬張175的call。 || 根據吸引力原則，哪裡期權未平倉數最大，哪裡就是磁鐵，會把股價吸向這個價格。 || 所以，根據本週期權未平倉數據，我做出判斷：英偉達週五收盤股價會收斂於175，低於180。 || 隨之，根據做市商殺期權原則判斷出來的殺期權點位，我再一次使用了蝴蝶。
- 策略证据：阿寶的末日蝴蝶加看跌垂直價差這兩套策略一共取得了100%的收益。 || 隨之，根據做市商殺期權原則判斷出來的殺期權點位，我再一次使用了蝴蝶。 || 之所以選擇177.5，是因為我根據之前說過的期權未平倉數據判斷，177.5是做市商殺期權會退而求其次所選擇的次優解。 || 如果此時再來分析新的期權未平倉數據，根據做市商殺期權原則，182.5、185、180的call肯定是要殺的。 || 這也是為什麼我選擇把策略的下腿放在180，而不是177.5或者175去做空的原因。 || 在英偉達股價178的時候，阿寶開倉了做空策略——熊市垂直價差。
- 回顾证据：歡迎來到阿寶美股實盤挑戰的第15周，周收益率100%，累計收益率3%900。 || 阿寶的末日蝴蝶加看跌垂直價差這兩套策略一共取得了100%的收益。 || 這是一個非常經典的警示訊號，提醒我們要收起貪婪、注意風險。 || 也就是說，180.52是我的盈虧分界線，低於這個數字則盈利，否則為虧損。 || 倘若週五收盤英偉達低於180，我將收取最大盈利。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；做市商/max pain/pin 推理；put/看跌或卖 put；含亏损/回撤复盘。

### 38. Stock Q_A

- 文件：`Tuq7F6QZeyc_Stock Q_A.md`
- 状态：`usable`；正文长度：6923
- 标的：NVDA, META, CAR, ETH
- 真实交易证据：If you invest 1 million in US stocks, buying shares and steadily earning 20% per year over 20 years, the compounding effect will bring your total return to 3,700%. || The max pain price is the price at expiration where the most option buyers lose money and the most sellers make money. || For example, if you had bought Nvidia or invested in Meta stock 10 years ago, your returns would have been dozens or even hundreds of times your original investment. || But the problem is most people don't fail because they can't spot these opportunities, but because they can't hold on, they get shaken out by volatility along the way. || With short-term trading, you can chase quick profits, but it requires extremely strong discipline and risk control. || The option strategies that Abao demonstrates in his real money trading challenges fall into this category. || I started with a principle of 4,000 and in 11 weeks using the leverage of options, I grew it to 107,000, a 26-fold increase. || Wages are rising rapidly and business owners are constantly complaining about labor shortages. || In other words, they can solve society's biggest pain points, labor shortages, and high costs. || Things like electric vehicles, photovoltaics, and energy storage aren't optional.
- 策略证据：In previous live trading videos, ABA has explained that a traffic light turns from green to yellow to red and the stock market goes from rising to moving sideways to falling. || If the stock price is below the VWAP, it means most people are losing money and the trend is relatively weak. || Many times, as expiration approaches, the stock price is drawn toward the max pain point. || Have you noticed that labor has become more and more expensive in the past couple of years? || In other words, they can solve society's biggest pain points, labor shortages, and high costs. || Industrial robots combined with service robots are the twin engines driving industrial upgrades.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：做市商/max pain/pin 推理；高集中仓位。

### 39. 美股实盘500美金_赚到曼哈顿大平层

- 文件：`UJsV8AySZKw_美股实盘500美金_赚到曼哈顿大平层.md`
- 状态：`usable`；正文长度：2086
- 标的：SPY
- 真实交易证据：我的賬戶裡一共542美金，其中376美金買入了回升星的看漲期權。 || 對於一個從500美金起步的交易計劃來說，這幾乎就是最理想的做多標的。 || 可惜在當時賬戶裡只剩下50美金，所以我只能買兩張680的末日期權。 || 一旦一家公司進入標普500，就意味著所有被動指數資金、ETF、指數基金、養老金配置都必須被動買入這些股票來完成指數跟蹤，這就會帶來以下幾件事情：穩定而持續的被動資金流入、更高的交易流動性、機構覆蓋度和市場關注度的提升。 || 指數像被突然點燃一樣開始往上衝，而我幾乎是在同一時間做出了反應，買入SPY末日期權。 || 我持有了大約10分鐘，然後把它們賣出，接著又開了隔天到期的686 SPY期權，賭一把第二天大盤高開跳空。 || 在真正開盤之前，我給今天的交易設定了一個大致的框架：做多回升星或CPU板塊。 || 很多人死在這裡，不是因為市場不好，而是因為一開始就想著梭哈改變命運。 || 但在我看來，小資金真正能活下來的方式，反而是最樸素的一種：在底部做多一隻能漲、有人氣、有故事的股票，慢慢的去積累原始籌碼，再讓復利一點點開始滾動。 || 當然了，交易計劃只是框架，真正的入場時機永遠要交給盤面。
- 策略证据：原因其實也很簡單：上週標普500下跌了2%，而AppLovin卻在同一周裡逆勢上漲了16%。 || 因為Coherent和Lumentum入選標普500的訊息，讓整個板塊都出現了資金搶籌，這反而讓我在第一時間就放棄了CPU，原因很簡單：如果大家都在搶，那麼風險就已經開始慢慢變大。 || 這很像是一種典型的盤面行為：短線資金建倉出貨，空頭釋放壓力。
- 回顾证据：而今天我也想做一件看起來有點瘋狂的事情：用500美金開始一場交易實驗，沒有固定的收益目標，取而代之的是用收益去實現那些現實世界中的夢想——賺到一張回國的機票，換一輛新車，再往後是全世界旅居的費用，直到有一天在曼哈頓買下一套屬於自己的大平層。 || 對於一個從500美金起步的交易計劃來說，這幾乎就是最理想的做多標的。 || 而更重要的是，回升星在年初衝高之後一路回撤，目前處於低位區域；而Coherent和Lument這兩隻CPU核心標的，則在過去一個月裡隨著市場整體回撥，從高點在短短几天內跌掉了將近一個月的漲幅。 || 因為Coherent和Lumentum入選標普500的訊息，讓整個板塊都出現了資金搶籌，這反而讓我在第一時間就放棄了CPU，原因很簡單：如果大家都在搶，那麼風險就已經開始慢慢變大。 || 曼哈頓計劃的第一筆真正的倉位就這樣落下。
- 审计判读：方向性 call；高集中仓位；含亏损/回撤复盘。

### 40. 麻省理工天才少年美股4千炒到100万

- 文件：`VBDdeYS5Bz0_麻省理工天才少年美股4千炒到100万.md`
- 状态：`usable`；正文长度：1680
- 标的：未抽取到明确标的
- 真实交易证据：想在投資的這條路上走得遠，就得先學會活得久，你得學會止盈和止損。 || 而我更欣賞的是另外一個詞，Pi call，就是明知有風險，卻依然堅定選擇的跟注。 || 什麼叫止盈？ || 什麼叫止損？ || 而我認為我的命就是在不斷的做期權這個過程當中，經歷反覆歸零和東山再起，循環往復。
- 策略证据：被萬一失敗的想象動搖自己的內心，最終失去理性的判斷，輸給自己的膽怯。
- 回顾证据：在股市裡，只有冒風險，才有機會獲得超額收益。 || 你們不必羨慕我賺了這麼多，如今我是悟道了，可你們不知道的是，我悟道前爆倉過3次，悟道後爆倉過一次，才有了今天的成就。 || 而我更欣賞的是另外一個詞，Pi call，就是明知有風險，卻依然堅定選擇的跟注。 || 怕輸時，注意力全在規避風險上，如履薄冰，戰戰兢兢。 || 最大的風險就是不敢承擔任何風險。
- 审计判读：方向性 call；有止盈/出场记录；含亏损/回撤复盘。

### 41. 美股选股名单

- 文件：`VJfOi2l7tc0_美股选股名单.md`
- 状态：`usable`；正文长度：6557
- 标的：NVDA, META, TSLA, TSM/TSMC, AVGO, AMD, LNG/Oil
- 真实交易证据：阿寶1月28號在粉絲群裡提過說SOUN是一個潛在好公司，但是當前股價過高，應該把買入點放在9塊錢附近。 || 在南希·佩洛西最新的公開持倉中，她買入了50份VST的看漲期權。 || TSM現在股價200，我會選擇把開倉點位放在180。 || 作為投資者而言，Meta現在在一個高位，需要等一個回撥再入場或許更合適。
- 策略证据：我給BBAI打6分3顆星，原因在於，雖然它在政府合同和資料分析領域具備一定優勢，但相較於市場巨頭，其市值和市場滲透率尚需提升，未來成長存在較大不確定性，因此打分保持在6分。 || 臺積電的邏輯其實和英偉達一樣，他們本身也是合作伙伴，一榮俱榮，一損俱損。 || 雖然處於早期商業化階段，但其顛覆性技術一旦突破，核電所帶來的產量和收益將徹底顛覆現有的電力格局。 || 但因為作為ETF需要持倉各種半導體公司的原因，SMH裡面也有一些我不太看好的弱勢公司，因此我給他打了7分。
- 回顾证据：但同時需要謹慎控制風險，畢竟跌起來你虧的也是3倍。 || 我給TQQQ打7分，是因為雖然它很好地追蹤了大盤3倍收益，但因為槓桿的本質風險和損耗也很大，所以只有7分。 || 佩洛西的成績大家有目共睹，在2024年期間，投資組合實現了70.9%的盈利率，遠遠超過了巴菲特長期以來所取得的平均20%的年化回報率。 || FTEC一共推出了10年，收益累計637%。 || FTEC是阿寶做過無數研究之後，精挑細選得出的天下第一大追蹤ETF，納斯達克指數增強版，歷史收益穩定跑贏大家更熟悉的VOO和QQQ，而且它的ETF費率非常低，遠低於QQQ和VOO。
- 审计判读：方向性 call；含亏损/回撤复盘。

### 42. 美股实盘挑战4千__100万 第5周

- 文件：`VXvai6djs7U_美股实盘挑战4千__100万 第5周.md`
- 状态：`usable`；正文长度：2730
- 标的：NVDA
- 真实交易证据：到了6月20号周五盘前，阿宝也是买入了英伟达7/11 146 call市价3.6，再次杀入市场，让我们敬请期待。 || 而如果你看过阿宝之前的美股期权入门视频，你就会知道美股期权对应了100股的股票。 || 所以期权就像一个100倍的放大器，期权市场的总仓位变化很大程度决定了英伟达的正股股价变化。 || Citadel卖出了79000股英伟达，持仓成本108，而高盛最大卖出的仓位也是英伟达，近期卖出了42000股。 || 英伟达是一个被期权价值带动的股票，有太多投资者通过持有英伟达期权来做多做空对冲正股。 || 而这里你看8万张150的call，7万张145的call和7万张146的call，6万张137的put，6万张155的call，在周五最终收盘价142的情况下，全部都会归零，都是废纸。 || 我们可以通过观察市场上的订单流，分析买方卖方强弱，判断哪里有大单买入卖出，从而提前一步抢占先机。 || 我们这里可以看到，按照open interest从高到低排列，排名前九的只有一个put，8个都是call。 || 而按照strike排列，144往上的call的数量全部远大于put。 || 143成为了主力的出货和止盈点位，散户的套牢最高点。
- 策略证据：第一个视角：支撑位和阻力位。 || 所以阿宝认为，这使得143存在巨大阻力，被套牢的人想抛售离场，抄底的主力为获利了结，卖的人一多，股价自然难以突破143。 || 第三个是RSI，这个指标是专门用来判断一个股票是否处于超卖或者超买的区间的。 || 第一原则是做市商杀期权原则。 || 这就是做市商杀期权原则，基本上持仓最大的期权都是韭菜，最后股价会变化到使得这些期权都归零。 || 在周五，美股因为伊朗和以色列冲突跌了的情况下，我做出判断，错的不是我，错的是这个市场。
- 回顾证据：第五周收益10.5%，累计收益78.5%。 || 所以期权就像一个100倍的放大器，期权市场的总仓位变化很大程度决定了英伟达的正股股价变化。 || Citadel卖出了79000股英伟达，持仓成本108，而高盛最大卖出的仓位也是英伟达，近期卖出了42000股。 || 在复盘之前，我们先插播一条快讯，在录这个视频的6月23号，约时间傍晚6点钟，特朗普在自己的社交平台单方面向全世界宣布伊朗和以色列停火。 || 第五个视角：对冲基金、机构仓位变化。
- 审计判读：做市商/max pain/pin 推理；方向性 call；put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 43. YfMQ_美股实盘挑战4千__100万 第14周

- 文件：`X9TWi6_YfMQ_美股实盘挑战4千__100万 第14周.md`
- 状态：`usable`；正文长度：1430
- 标的：NVDA, AVGO, AMD
- 真实交易证据：9月3號，英偉達橫盤在170，阿寶建倉開了一手175/177.5的熊市垂直價差。 || 我選擇開了一組165/170/175的蝴蝶，之所以選擇寬的蝴蝶，是因為5塊錢的長度的翅膀是為了更大的容錯，但整體策略是在下注週五英偉達股價會收斂在170。 || 雖然尾盤英偉達又漲回了167，但理論上，如果不止損會回本90%。 || 不知道你是否還記得在第11週中，阿寶預先看跌垂直價差，從182的歷史大頂做空英偉達。 || 倘若只是等待週五期權到期，我的垂直價差一共可以獲得2萬的盈利，而我卻更加貪婪。 || 週五，英偉達一口氣跌下了165，阿寶在165附近選擇止損離場，最終本金腰斬。 || 但既然已經決定了止損走人，那就徹底離場。 || 想在投資的這條路上走得遠，就得先學會活得久，你得學會止盈和止損。 || 這是因為我判斷英偉達本週大概率會跌，且透過期權的open interest，發現排名前六的都是高於170的。 || 根據做市商殺期權原則，我判斷週五會收盤在170附近殺死這些期權。
- 策略证据：我選擇開了一組165/170/175的蝴蝶，之所以選擇寬的蝴蝶，是因為5塊錢的長度的翅膀是為了更大的容錯，但整體策略是在下注週五英偉達股價會收斂在170。 || 根據做市商殺期權原則，我判斷週五會收盤在170附近殺死這些期權。 || 這是因為我判斷英偉達本週大概率會跌，且透過期權的open interest，發現排名前六的都是高於170的。 || 看跌卻選擇了小範圍橫盤策略，這是這筆交易失敗的根本原因。 || 而週四英偉達更是在169至170的範圍內波動一天，所有的一切都符合我的判斷，讓我確信本週五英偉達會收盤在170。 || 覆盤來看，我的大趨勢判斷是跌。
- 回顾证据：截止到第14週，我的賬戶從第13週的161000回撤到了現在的8萬，週收益率-50%，累計收益率1906%。 || 倘若只是等待週五期權到期，我的垂直價差一共可以獲得2萬的盈利，而我卻更加貪婪。 || 成本2.25，這意味著只要股價在167.25到172.25的區間之內，我就是盈利的，否則會虧損。 || 在股市裡只有冒風險，才有機會獲得超額收益，不妨再勇敢一些，放下顧慮，畢竟人只活一次，何不活得轟轟烈烈一些呢？ || 於是，在貪婪的驅使下，阿寶親手開啟了命運的潘多拉魔盒。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；做市商/max pain/pin 推理；put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 44. 美股实盘10万赚100万_167梭哈英伟达

- 文件：`XBYAFgBPEsQ_美股实盘10万赚100万_167梭哈英伟达.md`
- 状态：`usable`；正文长度：1702
- 标的：NVDA
- 真实交易证据：週一，我開倉買入了10萬塊的5月1號到期、行權價180的英偉達看漲期權，一共338張。 || 2.94買入的338張call，我在4.6的價格全部賣出，整波操作獲利50%。 || 而另一方面，我的內心也有些恐慌，因為我的倉位並非股票，167到163看似只跌了4美金，而對於我的call來說卻是一筆重大的損失。 || 結果所有的股票都應聲暴漲，英偉達則是隨漲了3%，我的期權賬戶直接盈利4萬，不僅補回來了昨天虧損的1.6萬，還淨賺了2.4萬。 || 我在173的價位將期權全部賣出止盈。 || 我是在167附近開倉的英偉達call。 || 第三，看put call ratio。 || 開張數錢，我曾在Matter的那一場梭哈中一無所有。 || 於英偉達167時梭哈了手裡的全部10萬美金，並在今天3月30號週二17:30選擇落袋為安。 || 開倉邏輯是我認為市場錯殺了英偉達，而英偉達遲早會把這段跌幅收回來。
- 策略证据：開倉邏輯是我認為市場錯殺了英偉達，而英偉達遲早會把這段跌幅收回來。 || 當VIX指數飆升直接突破30大關的時候，這意味著什麼？
- 回顾证据：而另一方面，我的內心也有些恐慌，因為我的倉位並非股票，167到163看似只跌了4美金，而對於我的call來說卻是一筆重大的損失。 || 結果所有的股票都應聲暴漲，英偉達則是隨漲了3%，我的期權賬戶直接盈利4萬，不僅補回來了昨天虧損的1.6萬，還淨賺了2.4萬。 || 收益率55%。 || 這意味著在這個價位，市場上99%以上的流通盤都是被套牢的，或者是割肉虧損的狀態。 || 當戰爭的陰影籠罩美股市場，哀嚎遍野，恐慌在暴跌中蔓延時，我選擇了在恐懼中貪婪。
- 审计判读：方向性 call；put/看跌或卖 put；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 45. Stock Q_A

- 文件：`ZLbHFei0lKQ_Stock Q_A.md`
- 状态：`usable`；正文长度：17127
- 标的：NVDA, META, CAR, TSLA, ETH, ORCL
- 真实交易证据：If you're trading the underlying stock and can't use option strategies to short volatility, then the best approach is to buy at the lows and sell at the highs within the consolidation range. || Whether the stock hasn't dropped or it has dropped and you bought the stock, you can use the shares you hold to sell a call option, which allows you to collect another premium. || Once the stock price rises to the strike price, your shares will be called away and sold, but you still make a profit on the sale plus you receive the option premium. || The third step, after your shares are sold, start selling cash secured put options. || Use 97% of your total assets for stocks and 3% for options. || I'm not talking about the fan who submitted this question specifically, but Aba has noticed that there are always a few gamblers who go allin on expiring options. || The second step, after you get the stock, sell a covered call option. || Because you originally wanted to own this stock and sell it when the price is high, you don't have to worry about selling at the wrong time since the option premium plus the stock's price increase provide a safety net. || My favorite and most commonly used take-profit method is the wheel strategy in options and its logic is especially simple. || Step one, sell cash secured put options.
- 策略证据：Everyone says this company is a meme stock, but Jane Street holds 5.9% of the total shares, and the new CEO's equity incentives are unlocked incrementally as the stock price rises from 9 to 33 UN. || Once the stock price rises to the strike price, your shares will be called away and sold, but you still make a profit on the sale plus you receive the option premium. || Whether there are people hyping it up and driving the momentum is extremely important. || For more advanced ways to play with options, you can check out the first season of my US stock live trading challenge series, which spans 11 weeks. || But no matter how many instructional videos you watch, nothing is as effective as real trading experience. || Every time I place a trade and lose, I just don't know if what I'm doing is right.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：wheel/卖权利金；方向性 call；put/看跌或卖 put。

### 46. 美股实盘挑战4千__100万 第9周

- 文件：`ZPyFOz7d5Cg_美股实盘挑战4千__100万 第9周.md`
- 状态：`usable`；正文长度：3752
- 标的：NVDA
- 真实交易证据：這個策略總共包含了4個部分：買入一張718167.5 call，買入一張718175 call，賣出兩張718172.5 call，總成本為2.15，所以對應的一手是215刀。 || 而阿寶的破譯蝴蝶策略的收益率達到了105%，我成本2.17買入的破譯蝴蝶組合，最終分別在4.45和4.52平倉。 || 7月15號週二，阿寶分析了英偉達本週的期權資料，發現英偉達期權open interest最大的持倉是13萬張的718170 call。 || 而每張170 call市價大約在2.5美元。 || 還記得我們剛才說到最大open interest 170 call買賣雙方的盈虧平衡點在172.5嗎？ || 週四，英偉達收盤價173，阿寶的破譯蝴蝶策略盈利57%，賬戶來到了51000。 || 這意味著我有16.6%的機率在區間裡贏得破譯蝴蝶的最大化收益。 || 這是截止下午3點45時間線的截圖，可以看到，如果你只買英偉達167.5的call，最終收益率會是23%。 || 而阿寶的破譯蝴蝶最終收益率是95%，失之毫釐，謬以千里。 || 我們可以來對比一下買入call和阿寶的破譯蝴蝶策略在這一週的收益情況。
- 策略证据：這個策略總共包含了4個部分：買入一張718167.5 call，買入一張718175 call，賣出兩張718172.5 call，總成本為2.15，所以對應的一手是215刀。 || 7月15號週二，阿寶分析了英偉達本週的期權資料，發現英偉達期權open interest最大的持倉是13萬張的718170 call。 || 還記得我們剛才說到最大open interest 170 call買賣雙方的盈虧平衡點在172.5嗎？ || 如果週五收盤價是172.5，那我的策略就可以漲到5塊。 || 週四，英偉達收盤價173，阿寶的破譯蝴蝶策略盈利57%，賬戶來到了51000。 || 而阿寶的破譯蝴蝶策略的收益率達到了105%，我成本2.17買入的破譯蝴蝶組合，最終分別在4.45和4.52平倉。
- 回顾证据：最大虧損215刀，最大盈利266.75刀。 || 當股價來到172.5時，達到理論最大收益117%。 || 直到股價大於175，阿寶的收益率會鎖定在10.13%。 || 還記得我們剛才說到最大open interest 170 call買賣雙方的盈虧平衡點在172.5嗎？ || 週四，英偉達收盤價173，阿寶的破譯蝴蝶策略盈利57%，賬戶來到了51000。
- 审计判读：butterfly/pin 到期策略；方向性 call；含亏损/回撤复盘。

### 47. 账户腰斩_曝光我投资生涯的至暗时刻_

- 文件：`Za7I-rcxUTM_账户腰斩_曝光我投资生涯的至暗时刻_.md`
- 状态：`usable`；正文长度：1907
- 标的：NVDA
- 真实交易证据：如果股價跌了5%，你的call可能就直接跌沒了50%；股價如果跌了10%，你的call也就基本上歸零了。 || 我之前在我的節目裡有提到過一個方法，叫做反人修仙法，就是隻拿你的3%的倉位來做期權，期權千萬不能熬運。 || 所以那天晚上我就盯著股價在夜盤跳水，然後期權在夜盤也沒有辦法交易，所以就根本沒有辦法止損，腦子裡面是一片空白的。 || 今年Trump tariff，我記得整個market大概連跌了大概有兩個月，大多數人除非你大多數時間保持空倉，不然我想一般很難逃過這一劫。 || 但雖然最後我沒有在低點被虧損擊垮，沒有離場，但我真的明白，如果當時NVIDIA不是在83反彈，而是比如說跌到了50甚至更低，我可能也撐不過去。 || 當時我不僅重倉了NVIDIA的正股，我還重倉了NVIDIA的call。 || 做期權的應該都知道期權最可怕的是什麼？ || 然後我們應該明白期權是把雙刃劍，一定要意識到這點。 || 因為在高波動和高風險事件面前，你重倉期權真的就是刀尖舔血。 || 再者一定要學會接受失敗，及時止損。
- 策略证据：首先我們要學會敬畏市場，因為再硬的個股邏輯，你也幹不過市場的趨勢轉變。
- 回顾证据：我之前在我的節目裡有提到過一個方法，叫做反人修仙法，就是隻拿你的3%的倉位來做期權，期權千萬不能熬運。 || 無非就是虧了太多次，已經有些麻木了。 || 那個倉位大概是什麼樣的？ || 但雖然最後我沒有在低點被虧損擊垮，沒有離場，但我真的明白，如果當時NVIDIA不是在83反彈，而是比如說跌到了50甚至更低，我可能也撐不過去。 || 有沒有什麼經驗教訓可以和觀眾分享的呢？
- 审计判读：方向性 call；含亏损/回撤复盘。

### 48. OUR0dVOG-8_美股实盘500美金_赚到曼哈顿大平层 Day2

- 文件：`_OUR0dVOG-8_美股实盘500美金_赚到曼哈顿大平层 Day2.md`
- 状态：`usable`；正文长度：1112
- 标的：SPY, LNG/Oil
- 真实交易证据：所以我在盤前就有了一個大致的計劃，這個計劃也很簡單：如果回升新能源漲到113左右，我就會試著止盈離場。 || 再加上我使用的是cash account，賣出之後資金需要結算，短時間內也無法再進行新的交易，於是我打算賣掉然後收手。 || 所以在11點21分，我做出了決定，在111左右的位置平掉了手裡的兩張看漲期權，同時也把前一天開的那兩張彩票一起賣掉。
- 策略证据：這種交易邏輯在過去一年中已經出現過很多次。
- 回顾证据：3月10號，曼哈頓計劃第二天。 || 所以我在盤前就有了一個大致的計劃，這個計劃也很簡單：如果回升新能源漲到113左右，我就會試著止盈離場。 || 這就是曼哈頓計劃day two的全部操作，沒有什麼驚心動魄的劇情，也沒有華麗的交易。
- 审计判读：方向性 call；有止盈/出场记录。

### 49. ebBDP1Dcq8_付费视频_杀期权判断点位的方法

- 文件：`_ebBDP1Dcq8_付费视频_杀期权判断点位的方法.md`
- 状态：`download_failed`；正文长度：206
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：v=_ebBDP1Dcq8 All strategies failed: ERROR: [youtube] _ebBDP1Dcq8: Join this channel to get access to members-only content like this video, and other exclusive perks.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：会员/下载失败内容，不能从正文还原真实交易。

### 50. x0faLWBrFY_人民币对美元汇率会到多少_

- 文件：`_x0faLWBrFY_人民币对美元汇率会到多少_.md`
- 状态：`usable`；正文长度：1525
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：而且大家要記住的是，我們央媽有足夠的外匯儲備，以保證其在合理的區間以內，畢竟貶值過多也會帶來進口成本上升，以及通脹壓力的增加，這對於我們老百姓來說也是很大的負擔。 || 那麼問題來了，人民幣兌美元貶值的底層邏輯是什麼？
- 回顾证据：進入2025年以來，10年期國債收益率跌至到了1.6%到1.7%的史上最低區間。 || 而當投資者對於經濟增長的前景感到擔憂時，他們往往會選擇購買國債這種低風險的避險資產。 || 債券的收益率走低，往往是因為市場對於債券的需求增高，從而推動債券價格上升，而又因為收益率等於票息除以債券價格，所以導致了收益率的降低。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 51. 美股实盘挑战4千__100万 第12周

- 文件：`agrUJLndj34_美股实盘挑战4千__100万 第12周.md`
- 状态：`usable`；正文长度：2232
- 标的：NVDA
- 真实交易证据：這組垂直價差包含了賣出172.5 put和買入170 put。 || 梭哈了170/172.5的垂直價差，成本0.54，目標收益率27.5%。 || NVIDIA最終收盤179.6，阿寶的170/172.5的垂直價差，以及穩穩的可以獲得最大盈利，剩下的只需靜待時間流逝即可。 || 一旦週五收盤在max pain，只有2.7萬張175 call能夠倖免於難，其他全部out of money最終為零。 || 隨後啊我就使用了兩袖信蛇中的看漲垂直價差策略。 || 我從7月末空倉蛰伏至今，不動則已，動則集中火力，重倉猛幹。 || 如果落地鷹派超預期，那麼避險就升級為趨勢性賣出，跌幅會加深並持續。 || 你或許會覺得期權風險太大，並且在這次交易當中沒有買在最低點，從而使得風險提升。 || 根據做市商殺期權原則，我判斷價格可能在週五收盤會接近177.5，收在max pain的位置，殺掉最多的期權。 || 而這就是做市商殺期權原則，也是max pain的正確使用方法。
- 策略证据：根據做市商殺期權原則，我判斷價格可能在週五收盤會接近177.5，收在max pain的位置，殺掉最多的期權。 || 一旦週五收盤在max pain，只有2.7萬張175 call能夠倖免於難，其他全部out of money最終為零。 || 而這就是做市商殺期權原則，也是max pain的正確使用方法。 || 隨後啊我就使用了兩袖信蛇中的看漲垂直價差策略。 || 而我做出判斷，今天的下跌是由資金避險FOMC會議紀要以及週五鮑威爾的Jackson Hole演講導致的。 || 對於美聯儲的態度，阿寶當時自己的判斷是鴿派，9月會降息，所以我認為避險事件結束，資金肯定會迴流。
- 回顾证据：只要週五收盤，NVIDIA股價大於172.5，我就能獲得最大盈利27.5%的收益回報率。 || 截止到目前，我的賬戶已經從最初的4000抵達了現在的136000，周收益率27%，累計收益率3296%。 || 梭哈了170/172.5的垂直價差，成本0.54，目標收益率27.5%。 || NVIDIA最終收盤179.6，阿寶的170/172.5的垂直價差，以及穩穩的可以獲得最大盈利，剩下的只需靜待時間流逝即可。 || 阿寶的賬戶來到了136000，周收益率27%。
- 审计判读：defined-risk 垂直价差；做市商/max pain/pin 推理；put/看跌或卖 put；高集中仓位。

### 52. nQE2uY_My Bitcoin Prediction

- 文件：`bEX1_nQE2uY_My Bitcoin Prediction.md`
- 状态：`usable`；正文长度：5670
- 标的：BTC, CAR
- 真实交易证据：At such a historically significant moment, we might as well consider a question. || So, the Bitcoin valuation model we are proposing today is actually a model used to value scarce natural resources called the stock toflow model. || The stockflow model specifically for Bitcoin was a concept proposed in 2019 by a former institutional investor named Plan B. || Instead, it assumes that as more bitcoins are mined, the number of people who want to buy Bitcoin will also increase. || And many people now buy Bitcoin not for its intrinsic functions, but to speculate for profit. || The reduced output makes the resources scarce, increasing their market value.
- 策略证据：v=bEX1_nQE2uY LANG: en TRANSCRIPT: On December 5th, 2024, the price of Bitcoin broke the $100,000 mark for the first time. || By running the Bitcoin open- source software, after the Genesis block, which is the first block in the Bitcoin blockchain, is created, a new block is generated approximately every 10 minutes, and Bitcoin is the reward that miners receive after successfully mining a block. || New York time, 1989 million bitcoins have been generated, accounting for 94.7% of the total supply. || For example, after the Bitcoin reward h havinging in May of 2020, the price of Bitcoin was around $9,000, while the model's predicted price was $55,000. || Although the predicted price seemed absurd at the time, the price of Bitcoin actually reached $55,000 in February of 2021. || Is $100,000 the ceiling for Bitcoin?
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put。

### 53. 期权进阶_解锁百倍收益的期权投资法 _moomoo

- 文件：`gEFDXAaGokQ_期权进阶_解锁百倍收益的期权投资法 _moomoo.md`
- 状态：`usable`；正文长度：3136
- 标的：NVDA, META
- 真实交易证据：阿寶追求的是極致的收益，所以符合我預期收益的策略只有2個：670 call，或者是710/740看漲垂直價差。 || 而這意味著假如我買了一張META call，股價每漲1塊錢，我會賺34塊錢；股價每跌1塊錢，我就會虧損34塊錢。 || 咱們還是以這個META call舉例，Theta是-0.4，意味著每過一天我會因為時間價值流逝而虧損40塊。 || 期權的本質是雙刃劍，用得好，10倍百倍也可以做到；用不好，結局就是歸零。 || 在這張圖中，我們可以看到每個點位上的put和call未平倉資料。 || 這就是最方便的期權策略構建功能，而且生成以後就可以直達下單頁面，還能把止盈止損都一口氣設定好。 || 如圖中所示，阿寶這裡選取了META的一買一賣兩筆期權形成組合，我們可以看到組合後的Delta、Gamma和Theta分別是多少，從而衡量整個組合作為整體的指標和風險情況。 || Open interest中文是未平倉量，則代表了有多少人持有這個期權未平倉。 || 阿寶在這裡演示一下木木的open interest功能，我們可以將選中日期的open interest分為call和put視覺化顯示。 || 像垂直價差、蝴蝶、破譯蝴蝶，這些都是阿寶常用的策略。
- 策略证据：阿寶追求的是極致的收益，所以符合我預期收益的策略只有2個：670 call，或者是710/740看漲垂直價差。 || 在理解了這些之後，你就能理解為什麼阿寶說IV是判斷策略的基礎。 || 你可以看當前IV是否處於歷史高位，判斷是不是賣方策略比買方策略更加划算。 || 而對於open interest的高階用法，你們可以參考阿寶油管或者B站的教學影片「殺期權判斷點位的方法教學與實操」。 || 第一部分：隱含波動率（IV），期權的價格指數。 || IV的作用往往是新手做期權賠錢的最大原因。
- 回顾证据：而這意味著假如我買了一張META call，股價每漲1塊錢，我會賺34塊錢；股價每跌1塊錢，我就會虧損34塊錢。 || 咱們還是以這個META call舉例，Theta是-0.4，意味著每過一天我會因為時間價值流逝而虧損40塊。 || 阿寶追求的是極致的收益，所以符合我預期收益的策略只有2個：670 call，或者是710/740看漲垂直價差。 || 如圖中所示，阿寶這裡選取了META的一買一賣兩筆期權形成組合，我們可以看到組合後的Delta、Gamma和Theta分別是多少，從而衡量整個組合作為整體的指標和風險情況。 || 每個策略下方會顯示策略的收益率、最大虧損和勝率。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put；有止盈/出场记录；含亏损/回撤复盘。

### 54. 美股实盘挑战4千__100万 第8周

- 文件：`gjQ3ZaW1rMA_美股实盘挑战4千__100万 第8周.md`
- 状态：`usable`；正文长度：2478
- 标的：NVDA, TSLA
- 真实交易证据：我分析了這週期權的資料，發現未平倉最高的期權就是7/11 160 call，一共105000張，這意味著很大機率股價會突破160，並且產生gamma squeeze效應，使得股價持續攀升，突破了160就會一口氣衝到165。 || 7月8號週二開盤後，阿寶埋入了NVIDIA 7/18 160 call，成本2.9，盈虧平衡點在162.9。 || 最終的結果是收盤價為164.92，把165這個未平倉最大的call全部絞殺，這也印證了阿寶先前影片裡講過的做市商殺期權原則。 || 當時他在160開的120 covered call，這樣的操作，與其說是穩健，不如說有點捧著金碗要飯的意思。 || 因為165存在的大量未平倉期權，就像一塊磁鐵，牢牢地把價格吸引在了這裡。 || 所以阿寶的原計劃為按兵不動，保持空倉。 || 對於很多很心急，一天不操作都渾身難受的朋友，阿寶在這裡送你們一句話：滿倉衝鋒的可以是勇士，但懂得空倉的才是將軍。 || 7月10號週四一早，英偉達開盤前就來到了164，我分析了期權資料，發現排名前三的期權全部in the money。 || 我判斷這周做市商可能得買入無數正股來保證被行權時有足夠多的股票交割。 || 而165的call也帶來了潛在的gamma squeeze的可能，形勢一片大好。
- 策略证据：我分析了這週期權的資料，發現未平倉最高的期權就是7/11 160 call，一共105000張，這意味著很大機率股價會突破160，並且產生gamma squeeze效應，使得股價持續攀升，突破了160就會一口氣衝到165。 || 從流動性原則上來說，我判斷股價一定會突破160，讓做市商去吃掉這些賣單。 || 我判斷這周做市商可能得買入無數正股來保證被行權時有足夠多的股票交割。 || 根據期權吸引力法的判斷，哪裡open interest最大，哪裡就是磁鐵，價格就會靠近。 || 最終的結果是收盤價為164.92，把165這個未平倉最大的call全部絞殺，這也印證了阿寶先前影片裡講過的做市商殺期權原則。 || 對於我這個決定，除了上述所說的市場情緒面的理解以外，最關鍵的是我認為NVIDIA 160突破在即，160以下的時間不多了。
- 回顾证据：7月8號週二開盤後，阿寶埋入了NVIDIA 7/18 160 call，成本2.9，盈虧平衡點在162.9。 || 所以阿寶的原計劃為按兵不動，保持空倉。 || 演算法交易要降低滑點，機構要排兵布陣，能成交能盈利的才是主戰場。
- 审计判读：wheel/卖权利金；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；方向性 call；含亏损/回撤复盘。

### 55. 比特币的估值模型

- 文件：`grOz0gFGszA_比特币的估值模型.md`
- 状态：`usable`；正文长度：1672
- 标的：MSTR, BTC
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：2024年12月5號，比特幣的價格首次突破10萬美元大關。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：本集偏宏观/主题/估值分析，未抽到明确实盘买卖。

### 56. NgCLM_my stock pick

- 文件：`h061h_NgCLM_my stock pick.md`
- 状态：`usable`；正文长度：25671
- 标的：NVDA, META, ASTS, CAR, TSLA, TSM/TSMC, AVGO, AMD, ORCL
- 真实交易证据：In her latest publicly disclosed holdings, Nancy Pelosi bought 50 call options on VST. || On January 28th, Abacus mentioned in the fan group that SoundHound is a potentially [music] good company, but its current stock price is too high and the buying point should be set around $9. || On February 15th, due to Nvidia's withdrawal of investment, the stock price plummeted and [music] closed at $10.97, which is close to the $9 buying point I mentioned. || In my opinion, a stock price in the $200 to $220 range presents a very good buying opportunity. || Her portfolio achieved a 70.9% [music] profit rate, far surpassing Warren Buffett's long-term average annual return of much more. || Just a few days ago, after Google released its financial [music] report, I bought also posted a short video analysis in which he mentioned that Google's investment in AI has greatly increased. || As a company with a long history and strong cash flow and dividend capabilities, VST has become a blue-chip benchmark in the market amid the rapid development of global data centers and AI technology, which has led to a significant [music] increase in electricity demand. || As the world moves toward intelligence and [music] digitalization, AI and high-performance computing are now the main drivers of transformation across industries.
- 策略证据：On January 28th, Abacus mentioned in the fan group that SoundHound is a potentially [music] good company, but its current stock price is too high and the buying point should be set around $9. || On February 15th, due to Nvidia's withdrawal of investment, the stock price plummeted and [music] closed at $10.97, which is close to the $9 buying point I mentioned. || As a GPU designer, Nvidia holds about 90% market share with products in gaming, data centers, autonomous driving, and more. || For investors, [music] this kind of diversified and forward-looking strategy not only spreads out risk, but also creates possibilities for various future dividends. || Besides the search engine, it also includes online [music] advertising, the Android operating system, cloud computing, autonomous driving, and other cutting-edge technologies. || In my opinion, around $180 is a very good entry point.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put。

### 57. w_小资金如何做大_技术指标怎么用_

- 文件：`hM7wbeWPS_w_小资金如何做大_技术指标怎么用_.md`
- 状态：`usable`；正文长度：1566
- 标的：NVDA, META, TSLA, LNG/Oil
- 真实交易证据：我從400本金開始，11周的時間，靠著期權的槓桿屬性做到了107000，本金增長26倍。 || 阿寶在自己的實盤挑戰裡演示的期權策略，正是屬於這一類。 || 最後就是阿寶的獨門秘籍：max pain最大痛點，這就是阿寶用來分析期權市場的秘密武器。 || max pain的價格是到期時能讓最多期權買家虧錢、最多賣家賺錢的那個價格。
- 策略证据：橫盤本身就意味著趨勢的減弱和反轉，這就是為什麼阿寶判斷年底有機率出現重大回調的原因。 || 阿寶在自己的實盤挑戰裡演示的期權策略，正是屬於這一類。 || 所以總結一句，小資金做大的核心邏輯是，第一種最穩，但也最慢，第二種靠眼光和運氣，第三種靠能力和心態。 || 回調或許會遲到，但永遠不會缺席。 || 年底左右，阿寶認為美股會有機率出現重大回調，大的就要來了。 || 除此以外，首先VWAP是一個很好的指標，反映了市場平均買股票的成本。
- 回顾证据：靠槓桿，你可以放大收益，但同樣放大虧損。 || 舉個例子，如果你在10年前就買了英偉達、特斯拉、Meta的股票，你的收益率會是幾十倍上百倍。 || 這是最快的方式，也是最難的方式，而且是風險最大的方式。 || 但事實是，一將功成萬骨枯，很多人資金沒有做大，反而是交易越多，虧的越多。 || 股價在VWAP之上，說明市場整體賺錢趨勢偏強；股價在VWAP之下，說明大多數人是虧的，趨勢偏弱。
- 审计判读：做市商/max pain/pin 推理；含亏损/回撤复盘。

### 58. _3wvCA_比特币概念股微策略MSTR

- 文件：`iQ1D__3wvCA_比特币概念股微策略MSTR.md`
- 状态：`usable`；正文长度：3105
- 标的：MSTR, BTC, ETH
- 真实交易证据：對於無論如何都想要繼續做多比特幣的朋友，如果你想要接著讓利潤跑，比起止盈，掛個高於成本價的止損或許會更好。 || Plan B是適合堅定看漲比特幣的朋友，掛個10萬的止損，繼續持有手頭的做多頭寸，不要加倉，不要滾倉，不要上槓杆。 || 可轉債是一種結合了債券和股票看漲期權這兩個部分的金融工具。 || 而波動性大能推高可轉債中期權部分的價格，從而讓MSTR在債券發行當中募集到更多的資金。 || 阿寶早在MSTR漲上500之後，就提示大家在500的價位止盈。 || 在MSTR和比特幣上已經賺了錢的朋友們可以考慮在這裡止盈了。 || Plan A是適合已經在這波行情大賺一波的朋友，分批次止盈，將手上的倉位分成3到4份，在103121這個點位只盈其中一份，只止盈不加倉。
- 策略证据：隨著比特幣價格突破10萬美元大關，專注於投資比特幣的上市公司微策略MSTR這隻股票也成為了萬眾矚目的焦點。 || 但在2020年，由於眾所周知的原因，全球進入低利率和量化寬鬆的貨幣環境，美元開始貶值。 || 而MSTR為什麼這麼執著於發可轉債也是有原因的。 || 因為如果比特幣回調帶來的反向擠壓是血崩性的，這不代表比特幣短期不能繼續上漲，而是作為一名合格的投資者，不是什麼錢你都要賺。
- 回顾证据：在此期間，比特幣挖礦算力驟降，比特幣價格從6萬美元的歷史高點下降至5月底的3萬美元，一個月的跌幅就接近50%，這也導致市場恐慌性拋售，進一步加劇了價格的下跌。 || 當時MSTR的資料分析主營業務盈利能力差，從2000年至今已持續虧損14億美元。 || 因為在過去四年16個季度裡面，只有2020年第三季度這一個季度公司的盈利收入是正數，其餘皆是虧損。 || 但是，由於槓桿的因素，兩者的核心區別在於風險層級。 || 也就是說，MSTR這隻股票是比比特幣風險更高的存在。
- 审计判读：方向性 call；有止盈/出场记录；含亏损/回撤复盘。

### 59. 重读利弗莫尔

- 文件：`kL-eqVEWedc_重读利弗莫尔.md`
- 状态：`usable`；正文长度：2450
- 标的：NVDA, META, TSLA
- 真实交易证据：比如這裡我們的跟蹤止損設定到2%，當衝高回落2%就會賣出，鎖住利潤，沒有觸發，則一直放大收益。 || 比如啊期權交易波動大的時候，那我們在買入之後就可以透過高階訂單功能設定一個跟蹤止損性價單。 || 最近我經歷了一次爆倉，因為我太賭性，對於META的判斷上頭了，忘記了倉位管理，一次性梭哈的末日期權輸了個精光。 || 我反思了一下，我當時就應該提前設定止盈和止損單的。 || 當期權價格衝高回落，一定的百分比便會自動賣出。 || 一上頭，倉位沒有控制住，直接梭哈，結果市場反手就給了我一句響亮的耳光。 || 我覆盤了一下我此次的交易，除了倉位管理，還有一個錯誤，就是在交易過程當中沒有嚴格執行止損。 || 保險起見，我們還可以設定一個限價止損單來防範風險。 || 總之原則就是嚴格執行止損策略。 || 此外，我們做期權一定要選擇勝率高的方向，尤其是財報記的期權。
- 策略证据：比如這裡設定虧損最多在3%到4%左右，保證整個策略虧損有限的同時，收益也能放大。 || 最近我經歷了一次爆倉，因為我太賭性，對於META的判斷上頭了，忘記了倉位管理，一次性梭哈的末日期權輸了個精光。 || 這次我對META的判斷太篤定了，篤定到我完全忘了什麼是敬畏。 || 總之原則就是嚴格執行止損策略。 || 下單前要思考情況，後面就透過工具來嚴格執行我們的交易策略。 || 現在回過頭想想，如果當時我有一個冷靜的助手，像mo木這樣幫我堅決執行交易前制定的策略，減少情緒化交易，那可能損失就不會這麼慘重。
- 回顾证据：比如這裡設定虧損最多在3%到4%左右，保證整個策略虧損有限的同時，收益也能放大。 || 比如這裡我們的跟蹤止損設定到2%，當衝高回落2%就會賣出，鎖住利潤，沒有觸發，則一直放大收益。 || 現在透過我的連結，開戶入金最高還可獲得1000美元的英伟达股票加閒置資金8.1%的收益。 || 現在透過我的連結開戶入金，最高還可獲得1000美元的英偉達股票，加閒置資金8.1%的收益。 || 最近我經歷了一次爆倉，因為我太賭性，對於META的判斷上頭了，忘記了倉位管理，一次性梭哈的末日期權輸了個精光。
- 审计判读：高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 60. 一年翻80倍_AXTI还能买吗

- 文件：`l6Cidd6Rnrc_一年翻80倍_AXTI还能买吗.md`
- 状态：`usable`；正文长度：1272
- 标的：AXT/AXTI
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：這種事情通常只會發生在分析師原本研究的投資邏輯被現實的發展速度徹底超車的時候，而這也引出了我們影片開頭的那個詞「unobtainium」——無法獲得之物。
- 回顾证据：直到我做這個影片的5月14號，距離那場抄底不過短短的三週，股價居然已經來到了115美元，收益率64%。 || 公司在4月底完成了一筆6.3億美元的股票增發，用來支援擴產計劃。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 61. sQVMOYVk_美股说唱

- 文件：`lF_sQVMOYVk_美股说唱.md`
- 状态：`usable`；正文长度：199
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：未抽取到明确策略句。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 62. 美股实盘挑战4千__100万 第1周

- 文件：`mMxHYN7LuNo_美股实盘挑战4千__100万 第1周.md`
- 状态：`usable`；正文长度：1300
- 标的：NVDA
- 真实交易证据：實盤的交割單我就放這裡，獲利主要來源於這張NVDA 122的call 3.45買進14.55賣出。 || 關稅降低到10%，我尋思著肯定力挺英偉達，我就用這4000刀在週一買了英偉達122的call，買的時候股價在120。 || 所以說借Call賺錢就像喝水割草，咱在美股的三天就翻了3倍。 || 而我選擇在人聲鼎沸時賣出獲利了結，資產也是來到了16000，提前結束這一週，週五保持空倉。 || 週三市場情緒特別好，很多人踏空fomo了追漲買入。 || 阿寶接下來一週的交易策略暫時是打算週一接著空倉，原因是英偉達這幾天連續沒有突破136，現在盤後又跌到了131。 || 我的判斷是沒有買方力量，下週一估計會回調，打算低於130之後再考慮買入。 || 如果出現特大回調，就上車英偉達，如果沒有就繼續保持空倉。 || 我知道有一些粉絲朋友們很急，空倉一天就渾身難受，但是你先別急，我們要有耐心，儘量做到宝刀出鞘時，便是我們大殺四方日。
- 策略证据：阿寶接下來一週的交易策略暫時是打算週一接著空倉，原因是英偉達這幾天連續沒有突破136，現在盤後又跌到了131。 || 我的判斷是沒有買方力量，下週一估計會回調，打算低於130之後再考慮買入。 || 如果出現特大回調，就上車英偉達，如果沒有就繼續保持空倉。
- 回顾证据：第一週收益40倍。 || 5月16號這一週4000美金翻倍至16000，收益率400%，100萬的目標已完成進度1.6%。 || 記住這句話，買在無人問津處，賣在人聲鼎沸時，其中的道理和巴菲特所說的眾人恐慌我貪婪，眾人貪婪我恐慌是一樣的道理。 || 在那裡我會實時更新我的實盤倉位。
- 审计判读：方向性 call；有止盈/出场记录。

### 63. 打工是不可能打工的

- 文件：`mWXoxQtGLeI_打工是不可能打工的.md`
- 状态：`usable`；正文长度：986
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：未抽取到明确策略句。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：未抽到明确实盘买卖；只保留策略或复盘证据。

### 64. 美股实盘挑战4千__100万 第7周

- 文件：`mtbDe1kXfkY_美股实盘挑战4千__100万 第7周.md`
- 状态：`usable`；正文长度：1860
- 标的：NVDA, TSLA
- 真实交易证据：而阿寶在這裡選擇了止盈，我6.2買入6.85賣出賺了0.65的差價，賬戶也隨之來到了金高10800，以我們4000到100萬的挑戰，百尺竿頭，更進一步，我週四選擇全部止盈有三個理由。 || 所以阿寶在週一一早就買入了NVIDIA 7月18號的Call，成本6.2，這意味著7月18號時，我的盈虧平衡點為161.2。 || 期權推算出股價的隱藏波動範圍在152至157.5。 || 由於期權的槓桿屬性，看著賬戶的浮虧，覺得這次跌幅是瀑布，恐慌情緒蔓延。 || 在這裡，阿寶還是要說一點，作為期權的持有者，那就應該要做好或有巨大浮動盈虧的心理準備。 || 其次，距離這張Call到期日718還有將近三週的時間，是什麼讓你覺得一隻股票今天跌了，那往後就會一直跌呢？ || 做市商大量買入了更多股票推高股價。 || 首先，Gamma squeeze來到了160並不會長久，很可能日內或者下週出現回撥，所以在100有這麼一個高點止盈，我覺得很合適。 || 所以我提前離場，避免了時間損耗。
- 策略证据：而一旦突破了157.5就會產生Gamma squeeze，從而繼續推動股價上漲。 || 且一旦突破了157.5，藉助Gamma擠壓效應，股價可能會逼近160。 || 基於這些資料，我做出判斷，這週四NVIDIA收盤大機率會收在157.5之上。 || 我看到NVIDIA的邏輯是，我認為NVIDIA股價在過去的一年裡一直被低估。 || 而這一次，隨著NVIDIA突破新高，我認為過去一年市場對NVIDIA股價的低估是時候被清算了。 || 你應該從理性的角度去分析下跌，而不是盯著自己的賬戶，在出現浮虧時做出感性的判斷。
- 回顾证据：兩個月前，阿寶在96的位置帶領全體群眾說哈抄底，如今股價已經到159，正股收益65%，一朝踏碎星河去，我命其中天作地。 || 由於期權的槓桿屬性，看著賬戶的浮虧，覺得這次跌幅是瀑布，恐慌情緒蔓延。 || 所以阿寶在週一一早就買入了NVIDIA 7月18號的Call，成本6.2，這意味著7月18號時，我的盈虧平衡點為161.2。 || 在這裡，阿寶還是要說一點，作為期權的持有者，那就應該要做好或有巨大浮動盈虧的心理準備。 || 你應該從理性的角度去分析下跌，而不是盯著自己的賬戶，在出現浮虧時做出感性的判斷。
- 审计判读：gamma squeeze / OI strike 突破；方向性 call；有止盈/出场记录；含亏损/回撤复盘。

### 65. options trading 101

- 文件：`nTO9Pvts-hQ_options trading 101.md`
- 状态：`usable`；正文长度：13052
- 标的：NVDA, CAR, TSLA, ETH
- 真实交易证据：For example, if Nvidia's current stock price is $110 and you only want to buy $100 worth of Nvidia stock, but you think that price is unlikely to fall further, then you can choose to sell, for example, a put option with a strike price of $100 on June 20th. || The option buyer will exercise the option, and you'll need to first buy a 100 shares of Tesla stock at $260 each and then sell them at $240 each, resulting in a total loss of $2,000. || However, if you had bought a 100 shares of Tesla stock at $220 each on March 10th and then sold the option, your final profit would have been the option premium plus the $2,000 profit from the price increase. || Selling one cover call applies to 100 shares of stock as collateral, providing someone else with an opportunity to buy your stock. || For example, if I own a 100 shares of Nvidia stock and I think it's unlikely that Nvidia will reach a price of $150 in the near future, then I can choose to sell a cover call expiring on June 20th. || If Nvidia's stock price doesn't reach 150 by June 20th, if the option expires and I can continue to hold my 100 shares, then if Nvidia's stock price exceeds 150, my 100 Nvidia shares will be sold at the exercise price of 150. || While buying 100,000 shares of Nvidia at $11670, it simultaneously sold 1,000 cover calls. || For example, you might buy a call option on a stock with a strike price of $100.
- 策略证据：On June 20th, if the stock price is below $15, such as 95, then I can exercise my right to sell Nvidia stock at $105 per share, which is equivalent to making $10 per share. || So in today's video, I will divide it into two parts to explain my understanding and thoughts on options. || And the break even point for a put option is the strike price minus the option premium, which is 105 - 7.9 equals 97.1. || If I choose to sell, my account will immediately receive the 119 option premium as my profit. || But if you want to trade options, then you at least need to understand every point I'm about to make. || We should also be careful about the IV crash after major events, which is the crash of implied volatility.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：方向性 call；put/看跌或卖 put。

### 66. 美股实盘88__135万

- 文件：`pnLj8t4tZzI_美股实盘88__135万.md`
- 状态：`empty`；正文长度：0
- 标的：未抽取到明确标的
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：未抽取到明确策略句。
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：空 transcript，无法审计。

### 67. 2026美股王炸板块太空

- 文件：`qZq5h5kRBH0_2026美股王炸板块太空.md`
- 状态：`usable`；正文长度：1877
- 标的：LNG/Oil
- 真实交易证据：金融時報就引用Morningstar的研究指出，多數主題ETF在過去幾年裡跑輸基準，且存在追高買入時機不佳的問題。
- 策略证据：太空板塊這波行情核心不是一個原因，是三股力量的疊加：政策把需求鎖死，商業把規模做大，資本把估值鉚定。 || 只要國家安全邏輯成立，訂單就會持續滾動。 || 任何一個環節的推遲都會導致估值回調。
- 回顾证据：但我必須要提醒你，主題型板塊很容易在最熱的時候吸引資金，也很容易在情緒退潮時回撤。 || 太空板塊同樣有這個風險，當趨勢太滿，估值會掀飛，業績可能跟不上。
- 审计判读：含亏损/回撤复盘。

### 68. 美股实盘10万赚100万_梭哈英伟达_我破防了

- 文件：`qigOjXQciyA_美股实盘10万赚100万_梭哈英伟达_我破防了.md`
- 状态：`usable`；正文长度：1159
- 标的：NVDA, AVGO, AMD
- 真实交易证据：4月1号周三，英伟达股价175附近，我开仓了600组175180的垂直价差策略，押注英伟达截止下周五收盘会大于180，我的策略平均价格在2.56左右，而理论最大收益是5块，只要下周英伟达大于180，我就可以取得接近翻倍的收益。 || 🎼我在周三一早卖出了全部600组垂直价差，共计27.7万于最顶点止盈。 || 我知道buy the rumor, sell the news，当消息落地的那一刻，利好出尽，也就是我落袋为安之时。 || 在市场极度恐慌的情况下，我的看涨垂直价差策略也大幅回撤。 || 而我认为我的命就是在不断的做期权这过程当中，经历反复归零和东山再起，循环往复。 || 🎼因此，我坚定做多，丝毫不慌。
- 策略证据：4月1号周三，英伟达股价175附近，我开仓了600组175180的垂直价差策略，押注英伟达截止下周五收盘会大于180，我的策略平均价格在2.56左右，而理论最大收益是5块，只要下周英伟达大于180，我就可以取得接近翻倍的收益。 || 🎼因为你是基于情绪三的判断在赌，而我从来只会根据逻辑做出自己的判断。 || 我根据三点事实逻辑判断出周二伊朗和美国的和谈必将成功。 || 在市场极度恐慌的情况下，我的看涨垂直价差策略也大幅回撤。 || 🎼我判断去年关税日4月7号成为熊牛转变日，今年的谈判日也是4月7号，这也将会是一样的剧本。 || 你或许会问，那万一我判断错了呢？
- 回顾证据：4月1号周三，英伟达股价175附近，我开仓了600组175180的垂直价差策略，押注英伟达截止下周五收盘会大于180，我的策略平均价格在2.56左右，而理论最大收益是5块，只要下周英伟达大于180，我就可以取得接近翻倍的收益。 || 在市场极度恐慌的情况下，我的看涨垂直价差策略也大幅回撤。 || 如果换作是你，你会不会害怕到恐慌割肉，又或者是坚持纵容恐慌，我贪婪，无论你回答我哪个答案，都是错的。 || 4月6号周一，美国给伊朗定下来最后期限，周二如果不打，在海峡就会将波斯夷为平地，市场随之恐慌，英伟达暴跌至174。 || 如果周五英伟达股价低于175，比如和现在的174当前股价一样，我会彻底归零爆仓。
- 审计判读：defined-risk 垂直价差；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 69. 英伟达财报策略

- 文件：`sV3qSkqh878_英伟达财报策略.md`
- 状态：`usable`；正文长度：1018
- 标的：NVDA
- 真实交易证据：我們在上期影片的最後和大家說了，阿寶在上週賣了2月20號到期的190 put，而190也是根據做市商殺期權原則所判斷出來的。 || 而由於上週賣了190 put成功卡在189.8結股，如此一來，阿寶目前就是全倉NVIDIA正股。 || 那麼對於很多粉絲在群裡問我為什麼不買call，我的解釋是買call做NVIDIA是自殺行為，因為做市商殺期權會導致股價下跌，而伴隨著IV crash會讓你虧得褲衩都不剩。 || 190後擁有最大未平倉看漲期權數量，所以190這個點位會像磁鐵一般在週五將股價吸過去，最終週五收盤189.82。 || 而對於做市商殺期權原則還不太清楚的朋友，可以光顧我的主頁購買我所製作的做市商殺期權課程。 || 如果我們看本週的open interest分佈，有太多賭徒開了195和200的call，總共12萬張，1200萬股，可以撬動22.8億美元的資金。 || 而這麼大的期權數量是有機率在財報之後發生gamma squeeze的。 || 我吃過買期權賭財報的虧，所以這是我以身試法之後所總結出來的經驗教訓，我希望你們能聽得進去。
- 策略证据：我們在上期影片的最後和大家說了，阿寶在上週賣了2月20號到期的190 put，而190也是根據做市商殺期權原則所判斷出來的。 || 那麼對於很多粉絲在群裡問我為什麼不買call，我的解釋是買call做NVIDIA是自殺行為，因為做市商殺期權會導致股價下跌，而伴隨著IV crash會讓你虧得褲衩都不剩。 || 而對於做市商殺期權原則還不太清楚的朋友，可以光顧我的主頁購買我所製作的做市商殺期權課程。 || 我之後會在群裡持續更新我對NVIDIA點位的判斷。 || 如果我們看本週的open interest分佈，有太多賭徒開了195和200的call，總共12萬張，1200萬股，可以撬動22.8億美元的資金。 || 而這麼大的期權數量是有機率在財報之後發生gamma squeeze的。
- 回顾证据：那麼對於很多粉絲在群裡問我為什麼不買call，我的解釋是買call做NVIDIA是自殺行為，因為做市商殺期權會導致股價下跌，而伴隨著IV crash會讓你虧得褲衩都不剩。 || 我吃過買期權賭財報的虧，所以這是我以身試法之後所總結出來的經驗教訓，我希望你們能聽得進去。 || 而對於大家最最最關心的2月25號週三盤後的NVIDIA財報，阿寶的計劃是全倉正股過財報，不上任何的槓桿。
- 审计判读：gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；方向性 call；put/看跌或卖 put；高集中仓位；含亏损/回撤复盘。

### 70. O0PPT-KxQ_2026_软件股完犊子

- 文件：`u_O0PPT-KxQ_2026_软件股完犊子.md`
- 状态：`usable`；正文长度：1730
- 标的：NVDA, META
- 真实交易证据：18倍的市盈率创纪录的便宜，但便宜从来不是买入的理由，尤其是当增长前景变得模糊不清的时候。
- 策略证据：首先，我们要搞清楚的一点是，在过去这么多年，是什么一直在支撑着软件股的估值。 || 问题之一在于，大多数软件公司在自家AI产品上的表现并没有显示出太多实质性的突破。 || 不过，这些被压低的估值也是促使华尔街部分人士开始对板块反弹持乐观态度的原因之一。
- 回顾证据：根据彭博行业研究的资料，标普500中，软件和服務公司的盈利增长预计在2026年将放缓至14%，低于2025年约19%的预期增长。
- 审计判读：有交易证据，但策略类型需人工复核。

### 71. Why I all in ASTS

- 文件：`uk-8FRHJVDc_Why I all in ASTS.md`
- 状态：`usable`；正文长度：3796
- 标的：NVDA, BTC, ASTS
- 真实交易证据：On top of that, there are 48 million shares sold short with a short interest of 20.74%. || That means out of every 100 shares, 21 are being shorted, pushing short positions to an all-time high. || First, Bezos's Blue Origin put AST satellite into the wrong orbit, causing the stock price to plummet. || Then, the largest shareholder, Rakuten from Japan, went on a selling spree, dumping shares onto the market at any cost just to solve its own financial crisis. || Looking at the news, I observe that the biggest whale, Loda, has finished unloading all their shares, a total of 15 million sold.
- 策略证据：It'll build a massive base station in outer space above Earth, so even if you're out on the waves of the Pacific or in the wilderness of a no man's land, the sky above you can deliver full bar 5G coverage. || v=uk-8FRHJVDc LANG: en TRANSCRIPT: This will be the most important investment of my life, and I'm going to bet everything on it. || My life motto is to seek out those sparks of civilization that go from zero to one. || [music] For the era of space-based stations, 2026 will be a dividing line, and the name standing on that line is AST SpaceMobile. || I believe that after ASTS pulls back to the 200-day moving average, it'll bottom out and rebound, ushering in a new wave of gains. || Bitcoin is the answer for one era, and Nvidia is the answer for another.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：put/看跌或卖 put；高集中仓位。

### 72. 如何度过低谷期

- 文件：`vc5p2Rivvqk_如何度过低谷期.md`
- 状态：`usable`；正文长度：1110
- 标的：未抽取到明确标的
- 真实交易证据：很多人記得他的高光是1929年做空市場封神一樣的時刻，但很少有人記得他也曾幾次破產，獨自坐在紐約公園的長椅上，沒有電報機，沒有隨從，只有一份報紙。
- 策略证据：如果你現在也正在經歷失敗、壓力或者一種說不出口的疲憊，我想跟你說，不用急著站起來，我們先站穩。
- 回顾证据：熟悉我的朋友應該都知道，在做電臺這檔節目之前，我一直都是做的美股實盤，直到最後一次試盤爆倉。
- 审计判读：含亏损/回撤复盘。

### 73. 潜力股怎么选_怎么止盈_

- 文件：`vrTqO9aKR9o_潜力股怎么选_怎么止盈_.md`
- 状态：`usable`；正文长度：4562
- 标的：NVDA, META, TSLA, ORCL, LNG/Oil
- 真实交易证据：拿你總資產的97%做正股，3%做期權。 || 這裡阿寶舉個例子你就明白了：假設你開了25倍合約做多NVIDIA，那麼就相當於用25倍槓桿去做多NVIDIA的股票。 || 所以抄底的第一步，現在先空倉，滿手的現金倉位可以放在國債ETF賺取一定的利息，年化利率約4%。 || 我最喜歡最常用的止盈方式就是期權裡的車輪策略。 || 所以我的建議是，首先事先制定交易計劃，把要做的策略、買點、賣點、止盈、止損都先給定下來。 || 那麼第二點，每週覆盤記錄自己本週的交易，包括買入邏輯、止損位、預期目標和最終結果。 || 而合約則是你可以選擇一個槓桿的倍數進行做多或者做空。 || 在下面這裡選擇做多或者做空。 || 我並沒有在說這位投稿的粉絲啊，但是阿寶發現總有個別賭狗滿倉梭哈玩期權，然後跑過來說波動太大了、承受不住怎麼辦？ || 如果你是做正股的，自然你沒有辦法用期權策略做空波動率，那麼最好的策略就是在震盪區間的低點買、高點賣，做波段行情。
- 策略证据：如果你去華爾街的對沖基金看一看，他們策略的勝率大多就是在55%至60%，然後賺的時候多賺一些，虧的時候少虧一些。 || 假設你能心理健康承受的波動是一天3%，而一隻股票的波動率是9%，那你就用三分之一倉位來做這個股票，這樣你的預期波動就在3%，在自己的心理承受範圍之內。 || 所以對應的最合適的策略，我認為是做空波動率。 || 如果你是做正股的，自然你沒有辦法用期權策略做空波動率，那麼最好的策略就是在震盪區間的低點買、高點賣，做波段行情。 || 假設美股在未來的一兩個月內有一個比較大的回調，有什麼收益大且比較安全的抄底策略呢？ || 邏輯也特別簡單，車輪策略一共有三步，像車輪一樣不斷循環。
- 回顾证据：假如你的盈利概率是55%，每次盈利1.5%，虧損概率是45%，每次虧損時虧損1%，在很長的時間裡你去重複博弈，你會發現你的收益率整體會慢慢達到一個非常驚人的數字，這就是正期望交易。 || 假如NVIDIA漲1%，你盈利25%；反之，假如NVIDIA跌1%，你虧損25%。 || 如果3%做大了，甚至可能超過97%；而如果3%虧沒了，也完全不傷害根基，再拿3%重新來過就好。 || 如果你去華爾街的對沖基金看一看，他們策略的勝率大多就是在55%至60%，然後賺的時候多賺一些，虧的時候少虧一些。 || 假設你能心理健康承受的波動是一天3%，而一隻股票的波動率是9%，那你就用三分之一倉位來做這個股票，這樣你的預期波動就在3%，在自己的心理承受範圍之內。
- 审计判读：wheel/卖权利金；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 74. why I invested in the space sector

- 文件：`ycfh7LFWNWE_why I invested in the space sector.md`
- 状态：`usable`；正文长度：7021
- 标的：CAR, ETH
- 真实交易证据：And this is also why governments around the world take it seriously, why the military is willing to procure it long-term, and why the capital markets give it a national security premium. || From a capital perspective, in the short term, SpaceX's launch business can provide stable cash flow. || You buy a terminal, pay a monthly subscription fee, and you can get online in the desert, on snowy plains, on remote islands, or even in an RV. || On December 19th, 2025, the SDA put their money right on the table. || As long as the logic of national security holds, the orders will keep coming. || But in the long run, Starlink is truly the ceiling for SpaceX's valuation. || First, we need to understand that Starlink isn't selling satellites. || It's selling connectivity. || It doesn't make money by selling satellites. || It makes money by selling one simple promise.
- 策略证据：When the market is focused on SpaceX's potential $ 1.5 trillion IPO in 2026, the secondary market will instinctively come up with one question. || And this is also why governments around the world take it seriously, why the military is willing to procure it long-term, and why the capital markets give it a national security premium. || This drives the space sector strong data, benefiting from both national security and communications infrastructure premiums, as well as the valuation premium unique to this sector. || Directtode device satellite connectivity is definitely a trend, but there are a lot of hurdles it still needs to overcome, like spectrum interference regulations, settlement models with telecom operators, satellite capacity, and costs. || By 2026, space won't just be a distant dream, but a strategic arena for major powers and a new infrastructure era emerging as the backbone for global connectivity. || Space used to be for the elite, limited to powerful nations and massive satellites.
- 回顾证据：未抽取到明确复盘/风险句。
- 审计判读：put/看跌或卖 put。

### 75. 美股实盘挑战4千__100万 第2周

- 文件：`yhoKiuGFfCA_美股实盘挑战4千__100万 第2周.md`
- 状态：`usable`；正文长度：1318
- 标的：NVDA
- 真实交易证据：在大盤穩定下來之後，我選擇在 NVIDIA 135 時買入35張132的末日期權。 || 但依然我選擇在135 call 入場。 || 週一132拉到135的這根大陽線，讓我當時認為上漲趨勢強勁，而又因為不能帶上軌在139，且本週有94000張140 call。 || 本著做市商殺期權原則，我認定 call 在139，止盈區間定在137至139，而選擇132。 || call 則是為了保險起見，只要股價高於136.5，那麼我就可以實現盈利。 || 我說的是：我認為英偉達這週會有回調的可能，我會考慮在130以下入場。 || 如果沒有出現回調，則保持空倉。 || 我在週一看到 NVIDIA 從132拉到135後，其實有所降低入場條件，從130提高到了132。 || 我沒有遵循原定的計劃，貿然入場，是失去了對市場的敬畏之心。 || 那個時候的我其實已經認輸了，腦子裡面只有止損二字。
- 策略证据：本著做市商殺期權原則，我認定 call 在139，止盈區間定在137至139，而選擇132。 || 我說的是：我認為英偉達這週會有回調的可能，我會考慮在130以下入場。 || 如果沒有出現回調，則保持空倉。 || 那麼第二個問題是你為什麼炒股這麼厲害，還要來做自媒體，原因也很簡單啊，因為我就是單純分享慾比較旺盛，而且如果萬一調整。
- 回顾证据：試盤第二週回撤55%，累計收益1.75倍。 || 我犯了哪些錯誤，導致虧損，以及在未來我將如何避免。 || 這個錯誤與我來說是傲慢之罪。 || 高收益的同時也會有更高的風險。 || call 則是為了保險起見，只要股價高於136.5，那麼我就可以實現盈利。
- 审计判读：做市商/max pain/pin 推理；方向性 call；有止盈/出场记录；含亏损/回撤复盘。

### 76. AXw1UU_我是如何从4千做到100万的

- 文件：`z6ri_AXw1UU_我是如何从4千做到100万的.md`
- 状态：`usable`；正文长度：48990
- 标的：NVDA, META, BTC, TSLA, AVGO, AMD, ORCL
- 真实交易证据：週四NVIDIA 155高開，由於未平倉期權數量中最多的是100張這週五到期的155 call，阿寶根據判斷，周股價有機率產生一口氣突破157，於是大膽買入了718 155 call。 || 早上9點50分，我按計劃開倉了180到182.5的熊市垂直價差策略，賣出一張8月1號180 call，買入一張8月1號182.5 call。 || 阿寶週四開倉的蝴蝶策略包括了買入一張177.5 call，賣出兩張180 call，買入一張182.5 call。 || 我在173的價位將期權全部賣出止盈，2.94買入的338張call，我在4.6的價格全部賣出，整波操作獲利5%。 || 阿寶策略有兩個組成部分：買入一張NVIDIA 7月25號的165 put，賣出一張NVIDIA 7月25號的167.5 put，以一組垂直價差的組合策略為例。 || 如果我們再來看8月1號這一週的期權未平倉倉位，排名第一的是94000張177.5 call，緊接著的是89000張185 call和71000張180 call。 || 熊市垂直價差策略有兩個組成部分：買入一張182.5 call，賣出一張180 call。 || 這組垂直價差包含了賣出172.5 put和買入170 put，只要週五收盤NVIDIA股價大於172.5，我就能獲得最大盈利27.5%的收益率。 || 我構建了175、180、185的蝴蝶策略，買入一張175 call，賣出兩張180 call，買入一張185 call，成本1.5。 || 而隨後我平倉了175 call，開倉了172.5 175的牛市垂直價差。
- 策略证据：週四NVIDIA 155高開，由於未平倉期權數量中最多的是100張這週五到期的155 call，阿寶根據判斷，周股價有機率產生一口氣突破157，於是大膽買入了718 155 call。 || 與此同時，阿寶根據做市商殺期權原則判斷，這周排名前三的期權177.5、182.5、180 call大概率會直接變成廢紙。 || 根據做市商殺期權原則和吸引力原則，股價在週五會跌下180，將180 call全部殺死。 || 如果此時再來分析新的期權未平倉資料，根據做市商殺期權原則，182.5、185、180 call肯定是要殺的。 || 我看見了做市商殺期權要殺光190 call 11萬張。 || 我從殺期權原則分析，前流的期權全部都是看漲期權，除了190 call，其他的都會在一旦股價超過185時發生gamma squeeze，一口氣來到187.5。
- 回顾证据：當戰爭的陰影籠罩美股市場，哀鴻遍野，恐慌在暴跌中蔓延時，我選擇了在恐懼中貪婪，於NVIDIA 1670梭哈了手裡的全部10萬美金，並在今天3月301號週二1730選擇落袋為安，收益率55%。 || 最大虧損是250減78，即172刀；最大盈利是78刀；最大收益率是78除以250，即31.2%；盈虧平衡點是167.5減0.78，即166.72。 || 第二週回撤55%，累計收益1.75倍。 || 最大虧損215刀，最大盈利266.75刀。 || 而一旦股價繼續上升，我的收益會有所下降，但是整體還是保持盈利，直到股價大於175，阿寶的收益率會鎖定在10.13%。
- 审计判读：defined-risk 垂直价差；butterfly/pin 到期策略；gamma squeeze / OI strike 突破；做市商/max pain/pin 推理；put/看跌或卖 put；高集中仓位；有止盈/出场记录；含亏损/回撤复盘。

### 77. pyHCARzFQ_英伟达的投资逻辑

- 文件：`z_pyHCARzFQ_英伟达的投资逻辑.md`
- 状态：`usable`；正文长度：4401
- 标的：NVDA, META, TSLA, AMD
- 真实交易证据：未抽取到明确实盘交易句。
- 策略证据：而面對困境，黃仁勳則是果斷改變商業策略，對公司業務進行了大刀闊斧的改革，並高調地向市場放下狠話，說NVIDIA既然能在過去的廝殺中生存下來，也必然將在未來的市場中搶到肉吃。 || 馬斯克更是一擲千金，把特斯拉的車載晶片全部換成了NVIDIA的，而原因也很簡單，因為NVIDIA的Drive系統不僅能計算路線，還能識別障礙，自動避讓行人。 || NVIDIA在很多領域都進行了佈局，而在自動駕駛這個領域，NVIDIA的Drive平台可以說是汽車廠商的金牌夥伴。 || 而這背後其實有一個非常簡單的原因，就是因為他們的現任CEO都是公司最初的創始人。
- 回顾证据：一開始，老黃對NVIDIA的市場定位是比較狹小的，計劃就做顯示卡，然後賣給遊戲公司。 || 我們再來說說NVIDIA的核心業務和盈利模式。
- 审计判读：本集偏宏观/主题/估值分析，未抽到明确实盘买卖。
