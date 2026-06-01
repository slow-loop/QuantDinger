# Daily OI Gamma Watchlist Agent Prompt

You are running a daily Stockchatu-style OI Gamma Watchlist scan.

Goal:

Analyze every ticker in the watchlist individually and find high-convexity option setups using:

1. macro/theme/event direction
2. options-chain OI / call walls / put walls / gamma ladder / max pain
3. price trigger confirmation
4. candidate option structure

Do not skip any ticker. If there is no setup, mark `NO_TRADE`. If options data is missing, mark `DATA_MISSING`.

Default watchlist:

```text
NVDA, AMD, AVGO, TSM, ARM, SMCI,
META, MSFT, AMZN, GOOGL, TSLA,
PLTR, COIN, MSTR, HOOD, RDDT,
ASTS, RKLB, LUNR,
ORCL, CRM, SNOW, DDOG, NET,
SPY, QQQ, IWM, SMH
```

For each ticker, collect:

- spot price
- current trend
- relevant catalysts
- nearest weekly expiry and next monthly expiry
- call OI by strike
- put OI by strike
- call/put volume by strike
- max pain if available
- put/call ratio if available
- IV if available
- nearest call wall
- next call wall
- largest call OI strike
- largest put OI strike

Classify each ticker as one of:

- `GAMMA_BREAKOUT`
- `CALL_WALL_REJECTION`
- `MAX_PAIN_PIN`
- `PUT_WALL_SUPPORT`
- `MISPRICED_REVERSAL`
- `NO_SETUP`
- `DATA_MISSING`

Score each ticker:

- Catalyst score 0-3
- Options setup score 0-4
- Price trigger score 0-3
- Total score 0-10

Priority:

- 8-10 = `TRADE_CANDIDATE`
- 5-7 = `WATCH`
- 0-4 = `NO_TRADE`
- critical options fields missing = `DATA_MISSING`

Structure selection:

- bullish breakout: ATM/near-OTM call or bull call spread
- clear next call wall target: bull call spread from current wall to next wall
- high IV bullish: prefer call spread
- support/not-below thesis: bull put spread
- rejection below call wall: bear call spread
- pin/max pain: butterfly centered near target strike
- uncertain long thesis: longer-dated call/call spread only if expiry matches event window

Output format:

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

If working in QuantDinger, save:

```text
my-research/log/results/oi_gamma_watchlist/YYYY-MM-DD-oi-gamma-watchlist.md
```

Optional CSV:

```text
my-research/log/results/oi_gamma_watchlist/YYYY-MM-DD-oi-gamma-watchlist.csv
```

CSV columns:

```text
date,ticker,status,score,setup,spot,expiry,nearest_call_wall,next_call_wall,largest_call_oi_strike,largest_put_oi_strike,max_pain,put_call_ratio,call_volume_signal,catalyst,trigger,target,structure,data_gaps,notes
```
