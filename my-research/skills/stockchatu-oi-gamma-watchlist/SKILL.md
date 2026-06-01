---
name: stockchatu-oi-gamma-watchlist
description: Use when running a daily Stockchatu-style options watchlist scan that analyzes every ticker for macro/theme/event direction, options open interest, call walls, put walls, gamma breakout, max pain/pin risk, and candidate option structures. Use for daily monitoring, paper-trade candidate generation, or producing a structured watchlist report.
---

# Stockchatu OI Gamma Watchlist

## Purpose

Run a daily watchlist scan modeled on Stockchatu's core profit engine:

> macro/theme/event direction + options chain OI/gamma/max pain levels + high-convexity option structure.

The agent must analyze **every ticker in the watchlist individually**. Do not skip tickers because they look boring. Mark them `NO_TRADE` if no setup exists.

## Hard Rules

- Use current market/options data when running a live daily scan. If current data is unavailable, say exactly which fields are missing.
- Never invent option OI, volume, max pain, IV, prices, strikes, or catalysts.
- Separate facts from interpretation.
- Separate `TRADE_CANDIDATE`, `WATCH`, `NO_TRADE`, and `DATA_MISSING`.
- Do not give generic bullish/bearish commentary without tying it to event + price + options-chain evidence.
- Do not limit the scan to NVDA. NVDA is only one ticker in the universe.

## Default Watchlist

Use this default list unless the user provides a custom list:

```text
NVDA, AMD, AVGO, TSM, ARM, SMCI,
META, MSFT, AMZN, GOOGL, TSLA,
PLTR, COIN, MSTR, HOOD, RDDT,
ASTS, RKLB, LUNR,
ORCL, CRM, SNOW, DDOG, NET,
SPY, QQQ, IWM, SMH
```

## Required Inputs Per Ticker

For each ticker, collect or mark missing:

- Spot price.
- Daily and intraday trend if available.
- Upcoming catalysts: earnings, macro event, product/order news, regulatory/news catalyst, sector theme.
- Nearest weekly expiry and next monthly expiry.
- Options chain by strike for at least the nearest relevant expiry:
  - call OI
  - put OI
  - call volume
  - put volume
  - bid/ask or mid price
  - IV if available
- Put/call ratio if available.
- Max pain if available or computable.
- Notable call walls and put walls.

## Data Sources

Preferred source order:

1. Polygon.io options snapshots: best first implementation for watchlist scanning because snapshots can include open interest, IV, Greeks, quotes, trades, and underlying spot.
2. Tradier options chains: good lightweight API for symbol + expiration chain pulls; use `greeks=true` when available.
3. IBKR TWS / Gateway API: use when the user already has IBKR market data subscriptions or wants the same stack for execution.
4. Databento / OPRA: use for professional raw OPRA trades/NBBO or historical research; expect to compute more derived fields yourself.
5. Free/unofficial sources: allowed only for manual sanity checks; do not treat as production signals.

If data source details are needed, read:

```text
my-research/log/journals/2026-05-31-options-data-sources.md
```

Data-gap rules:

- No options chain: mark ticker `DATA_MISSING`; do not propose a structure.
- Chain but no Greeks: OI walls and max pain are allowed; gamma ladder is `DATA_MISSING`.
- OI but no volume: static walls are allowed; do not claim volume surge.
- Volume but no OI: flow commentary is allowed; do not claim call wall or max pain.

## Analysis Workflow

### 1. Direction Layer

Classify the directional thesis:

- `BULLISH_BREAKOUT`: positive catalyst + price near/above call wall.
- `BEARISH_REJECTION`: price near resistance/call wall and likely to fail.
- `PIN_OR_MAX_PAIN`: likely to close near a strike/max pain level.
- `MISPRICED_REVERSAL`: selloff appears disconnected from thesis and reversal evidence exists.
- `NO_DIRECTION`: no clear directional edge.

Record the catalyst:

```text
macro:
sector/theme:
company:
technical:
sentiment:
```

### 2. Options Chain Map

Identify:

- Nearest call wall above spot.
- Current/nearest strike being tested.
- Next call wall above that.
- Largest call OI strike.
- Largest put OI strike.
- Put wall below spot.
- Max pain.
- Whether call OI forms a ladder above spot.
- Whether put OI creates downside support or downside magnet.

Use plain language:

```text
Spot 159.3 is testing the 160 call wall.
Next call wall is 165.
Call OI ladder exists at 160 -> 165 -> 170.
```

### 3. Setup Classification

Classify one setup per ticker:

- `GAMMA_BREAKOUT`
- `CALL_WALL_REJECTION`
- `MAX_PAIN_PIN`
- `PUT_WALL_SUPPORT`
- `MISPRICED_REVERSAL`
- `NO_SETUP`
- `DATA_MISSING`

### 4. Scoring

Score each ticker from 0 to 10.

Catalyst score, 0-3:

- 0 = no catalyst
- 1 = weak/general news
- 2 = sector momentum or clear technical setup
- 3 = major macro/company/theme catalyst

Options setup score, 0-4:

- +1 nearest call wall close to spot
- +1 call OI ladder above spot
- +1 call volume surge or low put/call ratio
- +1 max pain / OI structure supports thesis

Price trigger score, 0-3:

- 0 = far from trigger
- 1 = near trigger
- 2 = testing trigger
- 3 = broke trigger with confirmation

Total:

```text
score = catalyst + options_setup + price_trigger
```

Priority:

- 8-10: `TRADE_CANDIDATE`
- 5-7: `WATCH`
- 0-4: `NO_TRADE`
- missing critical options data: `DATA_MISSING`

## Structure Selection

Select a candidate structure only for `TRADE_CANDIDATE` or strong `WATCH`.

Use:

- Strong bullish breakout: ATM/near-OTM call or bull call spread.
- Clear next call wall target: bull call spread from current strike to next call wall.
- High IV but bullish: bull call spread instead of naked call.
- Support / not below strike thesis: bull put spread.
- Rejection below call wall: bear call spread.
- Pin/max pain target: butterfly centered near target strike.
- Long thesis with uncertain timing: longer-dated call or call spread only if expiry supports the thesis window.

Do not recommend a structure if strike/expiry/option prices are missing. Instead say what structure would be considered once data is available.

## Required Daily Output

Write the report with these sections:

```markdown
# Daily OI Gamma Watchlist - YYYY-MM-DD

## Market Context
- Index regime:
- Volatility/VIX:
- Macro events today/this week:
- Sector themes:

## High Priority
| ticker | score | setup | spot | trigger | target | structure | key reason |

## Watch
| ticker | score | setup | spot | trigger | target | structure | key reason |

## No Trade / Data Missing
| ticker | status | reason |

## Per-Ticker Notes
### TICKER
- Status:
- Direction:
- Catalyst:
- Spot / trend:
- Options chain:
  - nearest call wall:
  - next call wall:
  - largest call OI:
  - largest put OI:
  - max pain:
  - put/call:
  - call volume:
- Setup:
- Candidate structure:
- Invalidation / reason to skip:
- Data gaps:

## Paper Trade Candidates
| ticker | thesis | trigger | structure | target | data needed |

## Review Questions
- Did any ticker break a call wall?
- Did any ticker pin to max pain?
- Did call volume confirm or fade?
- Which candidates should be reviewed after close?
```

## Save Artifacts

If working inside QuantDinger, save the daily scan under:

```text
my-research/log/results/oi_gamma_watchlist/YYYY-MM-DD-oi-gamma-watchlist.md
```

If producing machine-readable output, also save:

```text
my-research/log/results/oi_gamma_watchlist/YYYY-MM-DD-oi-gamma-watchlist.csv
```

CSV columns:

```text
date,ticker,status,score,setup,spot,expiry,nearest_call_wall,next_call_wall,largest_call_oi_strike,largest_put_oi_strike,max_pain,put_call_ratio,call_volume_signal,catalyst,trigger,target,structure,data_gaps,notes
```

## Quality Bar

The output is only acceptable if:

- Every watchlist ticker appears exactly once in the report.
- Missing data is explicit.
- At least one sentence explains why each `TRADE_CANDIDATE` is actionable.
- `NO_TRADE` entries are concise but not omitted.
- No trade is proposed from narrative alone without options-chain evidence.
