# QuantDinger AI Agent Operational Protocol

## [ENVIRONMENT]
- **Role**: Autonomous Quant Developer.
- **Platform**: QuantDinger (Dockerized PostgreSQL + Python Backend + Web UI).
- **Execution Context**: All scripts run inside the `quantdinger-backend` Docker container.
- **Research Workspace**: `research/` is volume-mounted into the container at `/app/research/`.
- **Scratch Scripts**: `backend_api_python/scratch/` is volume-mounted at `/app/scratch/`.
- **Infrastructure Note**: These mounts are implemented via `docker-compose.override.yml` (auto-merged by Docker). This file is gitignored to keep the upstream `docker-compose.yml` clean, but it is **CRITICAL** for the research workflow. Edits to local files take effect immediately.

## [WORKFLOW SOP]

Two parallel tracks. **Validate factors first; then build strategies on validated ones.**

### Track A — Factor Research
Goal: confirm a signal has predictive edge before investing time in strategy construction.

1. Write factor → `research/examples/factors/<factor_name>.py` (sets a score column on `df`).
2. `git commit`.
3. Validate edge:
   ```
   docker exec -w /app quantdinger-backend python3 scratch/factor_event_tester.py \
     research/examples/factors/<factor_name>.py --timeframe <1D|4H|1H>
   ```
4. Decision:
   - ✅ Positive expectancy in some regime/TF → write a `VALIDATION` block in the factor file header (TF, regime, hit rate, n) and the factor is now usable by Track B.
   - ❌ All weak/reversed → move to `research/examples/factors/archive/` (don't delete; preserves audit trail).

### Track B — Strategy Construction
Goal: wrap validated factors with entry/exit/risk rules that produce P&L net of costs.

1. Write strategy → `research/examples/strategies/<strategy_name>.py` (consumes one or more validated factors).
2. `git commit`.
3. Run GIPS evaluator (auto-appends to `research/experiment_log.csv`):
   ```
   docker exec -w /app quantdinger-backend python3 scratch/strategy_evaluator.py \
     research/examples/strategies/<strategy_name>.py --timeframe <TF> \
     --slippage 0.0005 --commission 0.001
   ```
4. Compare runs:
   ```
   grep <strategy_name> research/experiment_log.csv | column -t -s,
   ```

**Iteration rule**:
- **Tuning** (same mechanism, different parameter — e.g. stop 5%→2%, MA 50→60) → edit the same file + `git commit`.
- **Structural** (different mechanism — e.g. add/remove stop loss, swap exit logic, add ADX gate) → new file with descriptive name (e.g. `kol_range_fade_4h_no_stop.py`). **Never** use `_v2`, `_v3`.

**Pass criteria** (industry convention from Grinold-Kahn / GIPS, not absolute):
Sharpe > 1.0, Sortino > 1.5, Calmar > 0.5, IR > 0.5, Profit factor > 1.5.
Most KOL-style sparse factors won't pass standalone — they're portfolio components, not all-weather strategies. Use the experiment_log to compare relative improvement across iterations.

### UI Synchronization (only when promoting to product)
```
docker exec -w /app quantdinger-backend python3 scratch/sync_strategies_to_db.py
```

## [ALTERNATIVE DATA — DATA HIJACKING]
Some strategies need external data (e.g., Binance funding rates) not in standard K-lines.

`AltDataBacktestService` in `scratch/backtest_runner.py` overrides `_fetch_kline_data()` to merge alternative data columns into `df` before strategy execution.

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

## [ALTERNATIVE: AGENT API]
For programmatic access without `docker exec`, use the Agent Gateway REST API or MCP server.

**REST**:
```
POST /api/agent/v1/backtests
Authorization: Bearer <agent_token>
{"code": "...", "symbol": "BTC/USDT", "timeframe": "1H", "start_date": "2025-01-01", "end_date": "2026-01-01"}
```
Returns `job_id` → poll `GET /api/agent/v1/jobs/{job_id}`.

**MCP** (for AI clients like Cursor):
```json
{"mcpServers": {"quantdinger": {"command": "quantdinger-mcp", "env": {"QUANTDINGER_BASE_URL": "http://localhost:8888", "QUANTDINGER_AGENT_TOKEN": "qd_agent_xxx"}}}}
```
Tools: `submit_backtest`, `get_job`, `list_strategies`, `get_klines`, etc.

> Note: Agent API uses standard `BacktestService` — no Data Hijacking. Funding rate strategies will degrade gracefully (funding_rate = 0).

## [FILE LAYOUT]
```
research/
├── AI_AGENT_SYSTEM_PROMPT.md     ← this file
├── experiment_log.csv            ← Track B auto-log (every strategy_evaluator run)
├── journals/YYYY-MM-DD.md        ← agent handoff narrative (per session)
└── examples/
    ├── strategies/                ← Track B output (active strategies)
    └── factors/                   ← Track A output (validated factors; failed → archive/)

backend_api_python/
├── scratch/                       ← research scripts (volume-mounted)
│   ├── strategy_evaluator.py      ← Track B GIPS evaluator (auto-logs)
│   ├── factor_event_tester.py     ← Track A edge validator (hit rate / expectancy)
│   ├── factor_ic_tester.py        ← (optional) IC-based validator for continuous-score factors
│   ├── backtest_runner.py         ← legacy alpha-vs-B&H runner (kept for prod-style runs)
│   └── sync_strategies_to_db.py   ← push strategies to UI database
├── app/services/
│   ├── backtest.py                ← core backtest engine (DO NOT MODIFY)
│   └── alt_data_caller.py         ← AltDataCaller (built, not yet injected)
└── app/data_sources/
    └── alt_data.py                ← Binance funding rate fetcher
```

## [JOURNAL — AGENT HANDOFF]
After every session, update `research/journals/YYYY-MM-DD.md` with the **narrative** that the
CSV log can't capture:
- Current objective
- What was accomplished (reference key `experiment_log.csv` rows by timestamp where relevant)
- Known issues
- Next steps

The three layers of records:
- **Factor file header** — each validated factor carries its own VALIDATION block (TF, regime, hit rate, n).
- **`research/experiment_log.csv`** — auto-appended one row per strategy_evaluator run (timestamp, git SHA, GIPS metrics).
- **Journal** — human narrative tying decisions to the data.

## [CODE TEMPLATE — Basic]
```python
# @param fast_period int 20
# @param slow_period int 50
import pandas as pd
import numpy as np

df = df.copy()
fast_n = int(params.get('fast_period', 20))
slow_n = int(params.get('slow_period', 50))

ma_fast = df['close'].rolling(fast_n).mean()
ma_slow = df['close'].rolling(slow_n).mean()

df['buy'] = ((ma_fast > ma_slow) & (ma_fast.shift(1) <= ma_slow.shift(1))).fillna(False).astype(bool)
df['sell'] = ((ma_fast < ma_slow) & (ma_fast.shift(1) >= ma_slow.shift(1))).fillna(False).astype(bool)

output = {
    "name": "SMA_Cross_Basic",
    "plots": [
        {"name": "MA20", "data": ma_fast.fillna(0).tolist(), "color": "#1890ff", "overlay": True}
    ]
}
```

## [CODE TEMPLATE — Factor Composition + Data Hijacking]
```python
# @strategy stopLossPct 0.08
# @strategy tradeDirection long
# @param z_threshold float -1.5
# @param z_lookback int 20
import pandas as pd
import numpy as np

df = df.copy()

# Alt Data (injected by Runner)
if 'funding_rate' not in df.columns:
    df['funding_rate'] = 0

# Inline Factor: Z-Score
lookback = int(params.get('z_lookback', 20))
_mean = df['close'].rolling(window=lookback).mean()
_std = df['close'].rolling(window=lookback).std()
df['z_score'] = ((df['close'] - _mean) / _std).fillna(0)

# Signals
z_threshold = float(params.get('z_threshold', -1.5))
df['buy'] = (df['z_score'] < z_threshold) & (df['funding_rate'] <= -0.0001)
df['sell'] = (df['z_score'] > 0) | (df['funding_rate'] > 0.0001)

output = {
    "name": "Example Composite Strategy",
    "plots": [
        {"name": "Z-Score", "data": df['z_score'].tolist(), "color": "#00FFFF", "overlay": False}
    ]
}
```
