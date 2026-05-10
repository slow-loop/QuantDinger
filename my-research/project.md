# QuantDinger

## Goal

Agent 自主**蒐集 + port + 驗證 + archive** 加密貨幣交易策略。**核心原則：策略不是自己想，是從 KOL / 網路收集**。Agent 現階段自己原創策略不會比網路上現成的好；直接參考、port 現成的就行。

**入口（agent SOP）：[`AGENT.md`](AGENT.md)**（`my-research/AGENT.md`）— QuantDinger Research Agent 規範。Two-track 工作流（Track A 因子 / Track B 策略），明文支援 KOL / paper / repo / observation 為 source（factor template `Source:` 行 + pass criteria 段「Most KOL-style sparse factors won't pass standalone — they're portfolio components」）。

> 本 `project.md` 跟 `AGENT.md` 同住 `my-research/`：AGENT.md = 怎麼做（SOP），project.md = 在做什麼（intent / scope / phases）。Hello-pm 的 PM 從這份讀。
> 同 pattern 對照：UCAgent 是 `lab/AGENT.md` + `lab/project.md`。

## 工作流程（從 my-research/AGENT.md 抄要）

### Track A — Factor Research

寫 factor → `my-research/factors/<name>.py`（含 docstring 標 Source / Hypothesis / Status / History）→ `factor_event_tester.py` 或 `factor_ic_tester.py` 驗 → 過了更新 docstring；不過搬 archive。

### Track B — Strategy Construction

寫 strategy → `my-research/strategies/<name>.py`（命名前綴 `kol_` 標 KOL 源）→ `strategy_evaluator.py` 跑 GIPS（auto-append 進 `experiment_log.csv`）→ tuning 改同檔、structural 開新檔（**不准 _v2 / _v3**）→ pass criteria：Sharpe>1.0 / Sortino>1.5 / Calmar>0.5 / IR>0.5 / Profit factor>1.5。

### Iteration 規則（重要）

- **Tuning**（同機制改參數）→ 改原檔，append `code` 行
- **Structural**（不同機制）→ 開新檔，cross-reference via `note` 行
- 每次改 code 必 append `code` 行；每次跑 evaluator 必 append `run` 行；想到事但沒做必 append `note` 行

## 工程邊界

QuantDinger 是 downstream of upstream QuantDinger。**所有研究工作只在 `my-research/`**：

- ✅ Allowed：`my-research/` 下任何東西、`docker-compose.override.yml`（gitignored）
- ❌ Forbidden：動 `backend_api_python/` / `frontend/` 等 upstream 路徑（即使小修也不行）
- ❌ Forbidden：動 upstream `docker-compose.yml`

Upstream bug → 寫 wrapper 在 `my-research/scripts/`，**不 patch upstream**。

## Scope

| In scope | Out of scope（無 user 明確批准） |
|---|---|
| 從 KOL / 網路 scout 策略想法 | **自己原創策略 / 因子** |
| port 進 `my-research/strategies/` / `factors/` | 動 upstream（`backend_api_python/` 等） |
| 用 `my-research/scripts/` 工具跑驗證 | 訂閱付費 data source |
| Archive 失敗策略，留 audit trail | 任何實單 / 真錢動作 |
| 在 factor / strategy docstring 標 Source、補 KOL 來源 metadata | 動 已 active 的策略檔（除 archive） |

## Terminology

### Task

一個 task = **一個策略從 KOL idea → port → 跑 GIPS → 進 active 或 archive**。或一個因子從 idea → IC / event test → 進 factor 庫或 archive。

### Checkpoints

- 改 `my-research/AGENT.md` 的 Track 定義 / 邊界規則
- 動已 active 的策略檔（除非 archive）
- 新 scouting source 進入流程（KOL 名單、論壇、paper feed）
- UI sync（promoting strategy to product）需手動跑 `sync_strategies_to_db.py`

### Risk Gates

未經 user 明確批准不執行：

- 任何**實單** / 真錢動作
- 對外 API 收費呼叫
- `git push`、force push、`--no-verify`
- 動 upstream code

## Log（PM 看這邊）

- `my-research/log/journals/<YYYY-MM-DD>.md` — per-day handoff narrative（agent session 結尾寫）
- `my-research/log/experiment_log.csv` — 每跑 strategy_evaluator 自動 append 一行（timestamp / git SHA / GIPS）
- `my-research/log/results/event/`、`my-research/log/results/ic/` — 因子 tester 原始輸出

PM scan 時讀 `my-research/log/journals/` 最新 .md 最後一段 entry。

## 已知策略 / 因子標源現況

`my-research/strategies/`：

- ✅ 標 KOL 源：`kol_200w_value_zone_long.py`、`kol_ohlc_anchor_4h_long_hysteresis.py`
- archive 內 KOL 標源：`kol_range_fade_*`、`kol_ohlc_anchor_4h_long.py`
- ❌ 未標源：`composite_alpha`、`funding_rate_bottom_fisher`、`sma_cross_rsi_basic`、`vol_breakout_4h_long` → **agent 工作項：補 Source 或 archive**

`my-research/factors/`：9 個 active factor，無命名前綴慣例（沿用 docstring `Source:` 行）。

## 已釐清 / 不再混淆

- ❌ `.cursor/skills/quantdinger-agent-workflow/SKILL.md` — Cursor IDE 用的 dev workflow（怎麼在 repo 改 code），**不是這個專案的 skill**
- ❌ `hello-trader-skill/skills-legacy/skill-crypto-trader/`（同份在 `hello-invest/apps/skill-crypto-trader/`）— freqtrade-based 舊 prototype，**已被 my-research/AGENT.md 取代**，不搬、不參考。在 `skills-legacy` 名下也佐證

## Backlog

- 把無 `kol_` 前綴的 4 個 strategies 補 Source（或 archive）
- 寫 scout source 清單（哪些 KOL / 論壇 / paper feed 在追）

## History

- **2026-05-09**：原 `QuantDinger/heartbeat/` 整個刪除（hello-pm template bulk copy 的副產品，跟 my-research/log/journals/ 重複）。project.md 從 `heartbeat/project.md` 搬到 `my-research/project.md`，跟 AGENT.md 同住。PM 從這份讀。
