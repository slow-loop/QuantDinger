# Options Data Sources for OI Gamma Watchlist

目标：

为 `stockchatu-oi-gamma-watchlist` 每日扫描取得美股期权链数据，包括：

- option chain
- strike / expiration
- call/put
- bid / ask / last
- volume
- open interest
- IV
- Greeks
- underlying spot

## 需要的数据字段

每日 watchlist 至少需要：

```text
date
ticker
spot
expiration
strike
option_type
bid
ask
last
volume
open_interest
implied_volatility
delta
gamma
theta
vega
```

可由这些字段计算：

- nearest call wall
- next call wall
- largest call OI strike
- largest put OI strike
- put/call ratio
- max pain
- simple gamma ladder
- candidate spread strikes

## 推荐路径

### Path A：Polygon.io，最适合先做 watchlist scanner

适合：

- 需要快速开发 watchlist monitor。
- 需要 REST API。
- 需要 chain snapshot、OI、IV、Greeks、quote/trade。
- 不想先接券商交易系统。

优点：

- API 结构清楚。
- options snapshot 可拿 open interest、IV、Greeks、latest quote/trade。
- 适合按 ticker 扫描整条 chain。

缺点：

- 需要付费方案。
- 实时/历史权限取决于 plan。

用途：

- 第一版每日 OI Gamma Watchlist 推荐用 Polygon。

### Path B：Tradier，轻量级 chain API

适合：

- 需要简单拉某个 symbol + expiration 的 options chain。
- 需要 open interest 和 Greeks。
- 可接受按 expiration 循环请求。

优点：

- `/v1/markets/options/chains` 可直接按 symbol/expiration 拿 chain。
- `greeks=true` 时可包含 Greeks/IV。
- response 内含 open_interest。

缺点：

- 需要逐个 expiration 拉。
- 数据深度和历史覆盖不如专业 vendor。

用途：

- 适合 MVP 或低成本版本。

### Path C：IBKR TWS API，适合有券商账户且可能要下单

适合：

- 已经使用 Interactive Brokers。
- 希望数据和交易执行在同一券商体系。
- 能接受 TWS/Gateway 常驻和 market data subscription。

优点：

- 可拿 option chain contract definitions。
- 可拿实时/延迟 market data，取决于订阅。
- 后续可扩展到交易执行。

缺点：

- 工程复杂度较高。
- 需要 TWS 或 IB Gateway。
- 市场数据权限、节流、盘中可用性都要处理。

用途：

- 第二阶段可接，尤其是想 paper/live execution 时。

### Path D：Databento / OPRA，专业原始数据

适合：

- 需要 OPRA consolidated trades / NBBO。
- 需要历史研究、tick/quote 级别。
- 愿意自己计算衍生指标。

优点：

- 专业级 OPRA 数据。
- 覆盖美国期权交易所的 trades / NBBO。

缺点：

- 对我们当前 watchlist scanner 可能过重。
- OI、Greeks、max pain 等往往仍要自己整理或另外取得。

用途：

- 后续做严肃历史回测时考虑。

### Path E：Yahoo/yfinance 等免费源，不建议作为正式信号

适合：

- 手动探索。
- 快速 sanity check。

问题：

- 非官方、稳定性不保证。
- OI/volume 延迟与缺失常见。
- Greeks/IV 不完整或需自己算。

用途：

- 只能做临时观察，不作为 production scanner。

## 第一版建议

建议先用：

1. Polygon.io，如果可付费/已有 key。
2. Tradier，如果想更轻量。
3. IBKR，如果用户本来就有 IBKR 且想后续交易执行。

第一版目标不是 tick 级精确，而是每天生成：

```text
ticker, spot, expiry, strike, call_oi, put_oi, call_volume, put_volume, iv, delta, gamma
```

然后计算：

```text
call_wall = max call OI strike near/above spot
next_call_wall = next major call OI strike above call_wall
put_wall = max put OI strike near/below spot
put_call_ratio = total_put_volume / total_call_volume
max_pain = strike with minimum total option-holder payout
gamma_ladder = gamma * open_interest * 100 by strike
```

## Max Pain 简化算法

对某个 expiry：

```text
for candidate_price in all_strikes:
    call_payout = sum(max(candidate_price - strike, 0) * call_oi * 100)
    put_payout = sum(max(strike - candidate_price, 0) * put_oi * 100)
    total_payout = call_payout + put_payout
max_pain = candidate_price with minimum total_payout
```

## Gamma Ladder 简化算法

若有 contract gamma：

```text
gamma_exposure_by_strike = gamma * open_interest * 100 * spot * spot
```

第一版可以先不估 dealer sign，只用它判断哪些 strike 的 gamma 敏感度最大。更严谨版本再区分 dealer long/short gamma。

## 每日 agent 缺数据处理规则

如果没有 options chain：

- ticker status = `DATA_MISSING`
- 不得给 candidate structure
- 可只写 catalyst / price context

如果有 chain 但无 Greeks：

- 可计算 OI wall、volume、put/call、max pain
- gamma ladder 标 `DATA_MISSING`

如果有 OI 但无 volume：

- 可判断静态 wall
- 不得声称 call volume surge

如果有 volume 但无 OI：

- 可判断当日 flow
- 不得声称 call wall / max pain

