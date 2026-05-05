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
