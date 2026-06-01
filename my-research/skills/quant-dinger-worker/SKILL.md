# QuantDinger Research Agent

## [ENVIRONMENT]
- **Role**: Autonomous Quant Developer.
- **Platform**: QuantDinger (Dockerized PostgreSQL + Python Backend + Web UI).
- **Execution Context**: All scripts run inside the `quantdinger-backend` Docker container.
- **Workspace**: `my-research/` is volume-mounted at `/app/my-research/`. Edits take effect immediately.
- **Mount infra**: `docker-compose.override.yml` (gitignored, auto-merged) defines the mount.

## [BOUNDARY — DO NOT TOUCH UPSTREAM]

This repository is downstream of upstream QuantDinger. To keep future
`git pull` merges clean, **all our work lives inside `my-research/` ONLY**.

- ✅ Allowed: anything under `my-research/` (factors, strategies, scripts, log, journals)
- ✅ Allowed: editing `docker-compose.override.yml` (gitignored, our local mount config)
- ❌ Forbidden: editing ANY file under `backend_api_python/`, `frontend/`, or any
  other upstream path — even for "small fixes"
- ❌ Forbidden: modifying upstream `docker-compose.yml`

If you find a bug in upstream code, write a wrapper in `my-research/scripts/` that
works around it. **Do not patch upstream.**

Interaction with upstream services is via:
1. Volume-mounted scripts running in the backend container (current default for research)
2. Agent Gateway REST API (`/api/agent/v1/...`) — for runtime ops like deploy / start strategy
3. MCP server `quantdinger-mcp` — for read/backtest from external AI clients

## [FILE LAYOUT]
```
my-research/
├── AGENT.md                     ← this file
├── factors/                     ← Track A output (validated factors)
│   └── archive/                 ← failed factors (audit trail, don't delete)
├── strategies/                  ← Track B output (active strategies)
│   └── archive/
├── scripts/                     ← research tools (run inside container)
│   ├── strategy_evaluator.py    ← Track B GIPS evaluator (auto-logs)
│   ├── factor_event_tester.py   ← Track A edge validator (hit rate / expectancy)
│   ├── factor_ic_tester.py      ← Track A IC validator (continuous-score factors)
│   ├── backtest_runner.py       ← legacy alpha-vs-B&H runner
│   └── sync_strategies_to_db.py ← push strategies to UI database
└── log/
    ├── experiment_log.csv       ← Track B auto-log (one row per evaluator run)
    ├── journals/YYYY-MM-DD.md   ← per-day handoff narrative
    └── results/
        ├── event/               ← factor_event_tester outputs
        └── ic/                  ← factor_ic_tester outputs
```

## [SCOUTING — 策略來源]

**每次 session 先做 scouting，再進 Track A/B。不管 backlog 有沒有東西。**

### 來源優先序

**1. TradingView Public Scripts（最優先）**

直接 WebFetch 以下分類 URL，每次挑 1 個：

```
https://www.tradingview.com/scripts/strategy/          ← 綜合策略
https://www.tradingview.com/scripts/bollingerbands/
https://www.tradingview.com/scripts/meanreversion/
https://www.tradingview.com/scripts/divergence/?script_type=strategies
https://www.tradingview.com/scripts/ichimoku/
https://www.tradingview.com/scripts/candlestickpatterns/
https://www.tradingview.com/scripts/volume/
```

每頁瀏覽 10–20 個 scripts，列出候選表並按下列標準排序，選排最前面且通過快篩的 1 個。

**候選排序標準**（依重要性）：
1. Open source Pine Script 可讀（hard filter — 無法讀原始碼就跳過）
2. Crypto-native（非 forex / 股票策略移植；timeframe 4H / 1D 優先）
3. Structural / catalyst-based（reclaim、breakout、compression→expansion — 已知有效 pattern）
4. Likes 數（社群驗過；同類型取 likes 高的）
5. 低參數複雜度（參數愈少愈好，overfitting 風險低）

**Dedup（port 前必做）**：
```bash
grep -r "tradingview.com" my-research/strategies/ my-research/strategies/archive/
```
Source URL 已出現過 → 跳過，換下一個。TV script URL 是唯一 key，不用維護額外清單。

命名前綴：`tv_`。Source 欄填完整 TV 頁面 URL。

**2. GitHub freqtrade community**（TV 找不到或太少）

`https://github.com/freqtrade/freqtrade-strategies` — Python 原生，轉換成本低。
命名前綴：`ft_`。

**3. Twitter / X KOL**（有明確 entry/exit 才處理，純評論跳過）

---

### 快篩（每個候選 30 秒決定）

- 能一句話寫出 Hypothesis？→ 繼續
- 有明確 entry / exit 條件（可 vectorize 成 `df['buy']` / `df['sell']`）？→ 繼續
- Open source Pine Script 可讀？→ 繼續
- 以上任一不行 → 跳過，換下一個

---

### 已知失敗模式（不再 port）

根據 2026-05-12 10 輪實驗：

| 類型 | 失敗原因 |
|---|---|
| EMA/MA crossover | 2025–26 趨勢 regime 差，OOS 崩潰 |
| Z-score / Bollinger stat threshold | Crypto fat tail 使信號延伸而非回歸 |
| RSI divergence（無 macro gate）| 下跌趨勢中 bullish divergence = 接刀子 |
| 任何純統計 threshold（無 structural catalyst）| 通不過 OOS |

**有效的 pattern**：structural event（price reclaims key level / Kumo breakout / structure break after compression）。

---

**沒有 inbox**：找到就 port，backtest 是唯一品質守門員。

## [SOCIAL SCOUTING NOTES — 2026-05-15]

This section records the 2026-05-15 X / Reddit / public-web scouting pass for
small-cap altcoins, memecoins, non-traditional crypto strategies, and emerging
trading ideas. Treat everything here as **candidate research**, not validated
edge. Before promoting anything to Track A/B, convert the idea into a one-line
Hypothesis plus vectorizable entry/exit conditions.

### Highest-priority test candidates

| Priority | Candidate | Testable form | Why it matters for small caps | Source status |
|---|---|---|---|---|
| 1 | Funding / crowding reversal | Extreme `funding_rate` + OI / wick / momentum exhaustion | Small-cap perp funding is noisy but can reveal one-sided leverage | Directly testable if `funding_rate` exists; OI requires external data |
| 2 | Funding Extreme + Liq Wick | Extreme negative funding + large lower wick = long-reversal event | Combines positioning stress with forced-selling candle structure | OHLC + funding, no extra API if funding is in df |
| 3 | OI Surge + Price Compression Breakout | OI z-score up, ATR/range compressed, then price breaks range | Small caps often accumulate leverage before expansion | Needs OI feed; should reject overheated funding |
| 4 | Per-asset walk-forward | Run same mechanism on AVAX/DOGE/ARB/OP/LINK separately | BTC parameters should not be assumed portable to alt perps | Track A/Track B evaluation discipline |
| 5 | Alt regime gate | BTC.D downtrend + ETH/BTC uptrend + TOTAL3/OTHERS.D breakout | Avoids trading alts during false rotation | Requires external regime data |

### Small-cap / altcoin strategies that can map to OHLC-style testing

1. **Funding Rate Extreme Long / Short**
   - Long setup: `funding_rate` is at an extreme negative percentile or z-score,
     ideally with a lower wick / sell climax.
   - Short setup: `funding_rate` is at an extreme positive percentile or z-score,
     OI is elevated, and upside momentum is stalling.
   - Avoid interpreting funding alone as edge. The stronger hypothesis is
     crowding reversal: extreme funding marks one-sided leverage that can unwind.
   - Candidate factor name: `funding_crowding_reversal`.

2. **Funding Extreme + Liquidation Wick**
   - Entry event: extreme negative funding plus a large lower wick.
   - Possible wick definition: `(min(open, close) - low) / close` above rolling
     percentile, with close reclaiming a portion of candle range.
   - Intended improvement over raw liq-wick: funding filters out random wicks
     and keeps only positioning-stress events.
   - Candidate factor name: `funding_liq_wick_reversal`.

3. **OI Surge + Price Flat Breakout**
   - Entry filter: OI surge while price range / ATR is compressed.
   - Trigger: close breaks compression high / low.
   - Safety filter: do not chase if funding is already extremely positive on
     long breakouts or extremely negative on short breakdowns.
   - Small-cap thesis: thin books and noisy OI can still matter during early perp
     listings or when leverage accumulates before a move.
   - Candidate factor name: `oi_compression_breakout`.

4. **Alt/BTC Relative Strength Breakout**
   - Compare target pair against BTC or ETH benchmark.
   - Candidate signal: target/BTC relative line breaks its own range or moving
     average while BTC is not breaking down.
   - Use as a rank / filter first, not a standalone all-in strategy.
   - Candidate factor name: `alt_relative_strength_breakout`.

5. **Funding cost as a backtest penalty**
   - Reddit algo discussions repeatedly warn that crypto perp backtests often
     treat perps like spot and omit funding.
   - Before trusting any perp strategy, estimate:
     `expected_edge > expected_funding_cost + commission + slippage`.
   - This is especially important for multi-day altcoin holds and cash-and-carry
     variants.

### Non-traditional / social strategies to track

1. **BTC.D + ETH/BTC + TOTAL3 / OTHERS.D regime gate**
   - Social framing: altseason confirmation requires more than BTC dominance
     falling. Stronger gate is BTC.D downtrend, ETH/BTC strength, and TOTAL3 or
     OTHERS.D breakout.
   - Use as market regime before enabling alt-beta strategies.
   - Avoid treating BTC.D alone as a precise entry signal.

2. **OTHERS.D small-cap season signal**
   - OTHERS.D tracks the long-tail alt universe better than top-heavy TOTAL.
   - Use as external context for whether small-cap strategies should be active.
   - Candidate implementation: daily/4H regime column merged into df, then gate
     small-cap long strategies only when OTHERS.D is above breakout / trend
     threshold.

3. **Narrative rotation basket**
   - 2026 social/research narratives found in the scan: meme launchpads, ICO
     launchpads, prediction markets, privacy/ZK, perp DEXs, stablecoins /
     stablechains, ETFs / DATcos, RWA, crypto cards, AI infra, DePIN, gaming,
     and meme coins.
   - Treat as sector relative-strength research, not single-symbol magic.
   - Possible workflow: define sector baskets, rank 7d/30d relative strength,
     then only test breakouts in the leading sector.

4. **Memecoin quick-scalp microstructure**
   - Reddit Solana / memecoin discussions frame the current style as DEX /
     terminal / Telegram-bot quick scalping rather than buy-and-hold.
   - Socially mentioned tools and venues include Jupiter, Raydium, Orca, Axiom,
     Trojan, GMGN, Banana Pro, and Pump.fun-style launchpads.
   - Useful features if on-chain data is added later: wallet diversity, trade
     count, holder concentration, new-wallet ratio, bundled buys, liquidity lock
     / burn status, and rapid volume decay after launch.
   - Do not port this directly into OHLC strategies without liquidity and rug
     filters.

5. **Pump.fun realized-profit / exit discipline**
   - CoinGecko reported Pump.fun profitable-wallet share rose in early 2026, but
     much of the realized profit was small and excludes unsold bagholders.
   - Research implication: memecoin edge is more likely in entry/exit speed,
     sizing, and sell discipline than in passive holding.
   - Possible rule idea: force partial exits after velocity spike, reject holds
     after volume decay.

6. **Smart-money / Hyperliquid wallet tracking**
   - Emerging social strategy: track profitable Hyperliquid or on-chain wallets.
   - Do not blindly copy. Filter for 90d+ history, controlled drawdown, stable
     trade frequency, low single-trade concentration, and no obvious market-maker
     / hedging cluster behavior.
   - Better QuantDinger use: convert smart-wallet direction into a weak external
     factor or confirmation label, not a primary signal.

7. **Copy-trading negative filter**
   - High PnL wallets can be luck, incomplete realized PnL, hedged one-leg
     exposure, or category overfit.
   - Useful inverse feature: avoid trades where copied wallet quality is poor,
     deteriorating, or dominated by a single recent win.

8. **Prediction-market wallet / event arbitrage**
   - Polymarket / Kalshi style discussions center on specialist-wallet tracking,
     market mispricing, and cross-market arb.
   - This is not OHLC-portable, but the research pattern is useful: build a
     mispricing scanner rather than blindly following high-PnL wallets.

9. **Equity / commodity perpetuals**
   - 2026 discussions highlight crypto venues listing 24/7 equity / commodity
     perps, including stock perps and pre-IPO style markets.
   - Possible edge classes: off-hours basis dislocation, funding imbalance,
     oracle / underlying-market closed-hour risk, crypto risk-on spillover.
   - Risk: multi-week holds can be dominated by funding costs.

### Symbols worth cross-testing first

```
AVAX/USDT, LINK/USDT, ARB/USDT, OP/USDT, DOGE/USDT
```

Suggested mechanism-symbol pairs:
- **Vol Climax / Liq Wick x AVAX**: high beta, thinner book, cascade-prone.
- **SFP / Stop Hunt x DOGE**: retail stop clusters and meme liquidity.
- **Funding Extreme x ARB/OP**: L2 tokens can show exaggerated perp funding.
- **Relative Strength x LINK/AVAX**: better candidates for sector/quality alt
  rotation than pure memecoin behavior.

### Source notes from the 2026-05-15 scan

Use these as source breadcrumbs when turning an idea into a factor/strategy:

- Reddit / algo: discussions warned that perp backtests often miss funding
  costs and that one BTC config does not reliably port to ETH/SOL/alt perps.
- Reddit / CryptoMarkets: recent threads discuss abnormal small-cap funding
  spikes and BTC dominance interpretation.
- Reddit / Solana and memecoin communities: current memecoin trading is mostly
  DEX / terminal / Telegram-bot quick scalping, with high rug/liquidity risk.
- CoinGecko: 2026 narrative reports covered meme launchpads, prediction
  markets, privacy/ZK, perp DEXs, RWA, stablecoin/stablechain themes, and
  Pump.fun profitable-wallet statistics.
- Trading / exchange research posts: funding + open interest are commonly
  framed as crowding / leverage indicators, not standalone directional signals.
- Hyperliquid / on-chain articles and Reddit threads: smart-money copy trading
  is popular, but wallet-quality filters are the real research surface.
- Public X-indexed material: BTC.D, ETH/BTC, TOTAL3, OTHERS.D, funding, OI,
  perp basis, stock perps, and Hyperliquid wallet tracking are recurring themes.

Concrete URLs captured during the scan:
- https://blofin.com/academy/education/funding-and-open-interest-signals
- https://www.walletfinder.ai/blog/crypto-funding-rates
- https://www.coingecko.com/research/publications/pump-fun-traders-are-making-a-comeback
- https://www.coingecko.com/learn/crypto-narratives
- https://www.coingecko.com/research/publications/rwa-report-2026
- https://crypto.com/us/research/equity-commodity-perps-jan-2026
- https://arx.trade/blog/why-copy-trade-smart-money-hyperliquid/
- https://coincub.com/blog/altcoin-rotation-when-to-move/
- https://www.kucoin.com/th/news/flash/others-d-aligns-with-qt-end-suggesting-2026-alt-season-pattern
- https://doc.methodalgo.com/docs/indicator/redeye-raven/start/

---

## [WORKFLOW SOP]

Two parallel tracks. **Validate factors first; then build strategies on validated ones.**

### Track A — Factor Research
Goal: confirm a signal has predictive edge before investing time in strategy construction.

1. Write factor → `my-research/factors/<factor_name>.py` (sets a score column on `df`).
2. `git commit`.
3. Validate edge:
   ```
   docker exec -w /app quantdinger-backend python3 my-research/scripts/factor_event_tester.py \
     my-research/factors/<factor_name>.py --timeframe <1D|4H|1H>
   ```
4. Decision:
   - ✅ Positive expectancy in some regime/TF → update the docstring (TF, regime, hit rate, n in History as a `run` line). Factor is now usable by Track B.
   - ❌ All weak/reversed → move to `my-research/factors/archive/` and add a final `note` line with the reason.

### Track B — Strategy Construction
Goal: wrap validated factors with entry/exit/risk rules that produce P&L net of costs.

1. Write strategy → `my-research/strategies/<strategy_name>.py` (consumes one or more validated factors).
2. `git commit`.
3. Run GIPS evaluator (auto-appends to `my-research/log/experiment_log.csv`):
   ```
   docker exec -w /app quantdinger-backend python3 my-research/scripts/strategy_evaluator.py \
     my-research/strategies/<strategy_name>.py --timeframe <TF> \
     --slippage 0.0005 --commission 0.001
   ```
4. Compare runs:
   ```
   grep <strategy_name> my-research/log/experiment_log.csv | column -t -s,
   ```

**Iteration rule**:
- **Tuning** (same mechanism, different parameter — e.g. stop 5%→2%, MA 50→60) → edit the same file, append a `code` line in History + `git commit`.
- **Structural** (different mechanism — e.g. add/remove stop loss, swap exit logic, add ADX gate) → new file with descriptive name (e.g. `kol_range_fade_4h_no_stop.py`). **Never** use `_v2`, `_v3`. Cross-reference between files via `note` lines.

**Pass criteria** (industry convention from Grinold-Kahn / GIPS, not absolute):
Sharpe > 1.0, Sortino > 1.5, Calmar > 0.5, IR > 0.5, Profit factor > 1.5.
Most KOL-style sparse factors won't pass standalone — they're portfolio components, not all-weather strategies. Use the experiment_log to compare relative improvement across iterations.

### UI Synchronization (only when promoting to product)
```
docker exec -w /app quantdinger-backend python3 my-research/scripts/sync_strategies_to_db.py
```

## [FACTOR FILE TEMPLATE]

Every factor file starts with a docstring (narrative) followed by `#` directives. Read the example, copy the structure, fill in your own.

```python
"""
Factor:     funding_rate_zscore                # filename without .py
Hypothesis: 資金費率極端值預示 mean-reversion    # one line — the mechanism. Can't write this = idea isn't clear yet, don't write the file.
Source:     ported from arxiv 2401.xxxxx       # paper / repo / observation / own idea
Status:     active                             # active | archived | superseded-by:<file>

History (append-only, newest at bottom):
  2026-05-05  code  init. funding rate 標準化 + 20-bar z-score.
  2026-05-05  run   IC=0.08 on 4H BTC, hit 54% n=412 ✓ marginal but positive.
                    (log: 2026-05-05T09:12:44)
  2026-05-06  note  4H IC > 1H — 短 TF 噪音太大。下一步只跑 4H/1D。
"""

# @param lookback int 20

import pandas as pd
import numpy as np

df = df.copy()

if 'funding_rate' not in df.columns:                # graceful degrade outside Alt-Data Runner
    df['funding_rate'] = 0

lookback = int(params.get('lookback', 20))
mean = df['funding_rate'].rolling(lookback).mean()
std = df['funding_rate'].rolling(lookback).std()
df['funding_z'] = ((df['funding_rate'] - mean) / std).fillna(0)
```

## [STRATEGY FILE TEMPLATE]

```python
"""
Strategy: kol_range_fade_4h_long
Thesis:   4H range-fade — 在低 ADX 區間 + range 底部進 long
Built on: factors/factor_range_fade.py
Status:   active

History (append-only, newest at bottom):
  2026-04-12  code  init. port from cap_013 range_fade. stop=5%.
  2026-04-12  run   Sharpe 0.4, hit 58% n=271. R:R asymmetric — win avg +1.3%.
                    (log: 2026-04-12T22:10:33)
  2026-04-13  note  5% 太寬，平均 win 只 +1.3% — kill expectancy after fees. 試 2%。
  2026-04-13  code  stop 5%→2%.
  2026-04-14  run   Sharpe 0.7, Sortino 1.1, hit 60.6% n=269 ✓
                    (log: 2026-04-14T15:23:01)
  2026-04-20  note  在 trending regime 死。試加 ADX gate
                    → 開新檔 kol_range_fade_4h_long_adx.py 測（structural change）
  2026-04-25  note  新檔結果中性。原因可能是 ADX threshold 抓的 regime 太粗。先擱置。
"""

# @strategy stopLossPct 0.02
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param adx_threshold float 20.0
# @param entry_range_pos float 0.15
# @param exit_range_pos float 0.50

import pandas as pd
import numpy as np

df = df.copy()
# ... (strategy logic)
```

**History tags**:
- `code` — 改了程式（含 init）
- `run`  — 跑了 evaluator，附主要指標 + log timestamp（可跳回 csv 看完整數據）
- `note` — 想了什麼、決定什麼、放棄什麼，沒動 code

每次改 code 必 append `code` 行；每次跑 evaluator 必 append `run` 行；想到事情但沒做必 append `note` — 否則思路斷在 context 裡，下一棒撿不起來。

寫不出 Hypothesis / Thesis 就不要寫這個檔。

## [ALTERNATIVE DATA — DATA HIJACKING]
Some strategies need external data (e.g., Binance funding rates) not in standard K-lines.

`AltDataBacktestService` in `my-research/scripts/backtest_runner.py` overrides `_fetch_kline_data()` to merge alternative data columns into `df` before strategy execution.

**Strategy-side**:
```python
# Runner injects 'funding_rate' into df. Degrade gracefully outside Alt-Data Runner:
if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0
```

> `call_indicator()` is for platform-registered indicators only. Never use it for alternative data.

## [FACTOR COMPOSITION]
1. **Simple factors** (Z-Score, RSI) → inline in strategy. No external dependency.
2. **Registered factors** → `call_indicator('Factor Name', df, {'param': value})`.
3. **Alternative data** → Data Hijacking (see above).

## [CONSTRAINTS]
- **Vectorization ONLY**: Engine requires `df['buy']` / `df['sell']` boolean columns.
- **No File IO/Plotting**: Use `output['plots']` dict only. Frontend ECharts handles rendering.
- **Sandbox**: No bypassing `safe_exec.py`. Only `pandas` and `numpy`.
- **Realistic Costs**: Enforce slippage ≥ 0.05%, commission ≥ 0.1%. Zero-cost backtests are invalid.

## [JOURNAL — AGENT HANDOFF]
After every session, update `my-research/log/journals/YYYY-MM-DD.md` with the **narrative** that the CSV log and per-file history can't capture:
- Current objective
- What was accomplished (reference `experiment_log.csv` rows by timestamp where relevant)
- Known issues
- Next steps

The four layers of records:
- **File docstring** — each factor / strategy carries its own thesis + per-file history (code/run/note).
- **`log/experiment_log.csv`** — auto-appended one row per `strategy_evaluator` run (timestamp, git SHA, GIPS metrics).
- **`log/results/`** — raw CSV outputs from event / IC testers.
- **`log/journals/`** — per-day human narrative tying decisions to the data.

## [ALTERNATIVE: AGENT API]
For programmatic access without `docker exec`, use the Agent Gateway REST API or MCP server.

**REST**:
```
POST /api/agent/v1/backtests
Authorization: Bearer <agent_token>
{"code": "...", "symbol": "BTC/USDT", "timeframe": "1H", "start_date": "2025-01-01", "end_date": "2026-01-01"}
```
Returns `job_id` → poll `GET /api/agent/v1/jobs/{job_id}`.

For deploying a strategy to paper trading on testnet:
- `POST /api/agent/v1/strategies` (W scope) → create with status=stopped
- `PATCH /api/agent/v1/strategies/{id}` (W + T scope) → set status=running
- Credentials must have `enable_demo_trading: true` to route orders to exchange testnet.

**MCP** (for AI clients like Cursor):
```json
{"mcpServers": {"quantdinger": {"command": "quantdinger-mcp", "env": {"QUANTDINGER_BASE_URL": "http://localhost:8888", "QUANTDINGER_AGENT_TOKEN": "qd_agent_xxx"}}}}
```
Tools: `submit_backtest`, `get_job`, `list_strategies`, `get_klines`, etc. (read + backtest only — deploy/start go via REST.)

> Note: Agent API uses standard `BacktestService` — no Data Hijacking. Funding rate strategies will degrade gracefully (funding_rate = 0).
