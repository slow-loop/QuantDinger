#!/usr/bin/env python3
"""
IBKR options OI/gamma watchlist scanner.

This script is intentionally local-first: it connects to a running TWS or IB
Gateway through ib_insync, fetches a filtered options chain for a watchlist, and
writes the Stockchatu-style daily OI/gamma report artifacts.
"""

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_OUTPUT_DIR = "my-research/log/results/oi_gamma_watchlist"
DEFAULT_WATCHLIST = [
    "NVDA", "AMD", "AVGO", "TSM", "ARM", "SMCI",
    "META", "MSFT", "AMZN", "GOOGL", "TSLA",
    "PLTR", "COIN", "MSTR", "HOOD", "RDDT",
    "ASTS", "RKLB", "LUNR",
    "ORCL", "CRM", "SNOW", "DDOG", "NET",
    "SPY", "QQQ", "IWM", "SMH",
]


@dataclass(frozen=True)
class OptionQuote:
    ticker: str
    expiration: str
    strike: float
    right: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    volume: Optional[float] = None
    open_interest: Optional[float] = None
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None


@dataclass(frozen=True)
class TickerScan:
    ticker: str
    status: str
    score: int
    setup: str
    spot: Optional[float]
    expiry: Optional[str]
    nearest_call_wall: Optional[float]
    next_call_wall: Optional[float]
    largest_call_oi_strike: Optional[float]
    largest_put_oi_strike: Optional[float]
    max_pain: Optional[float]
    put_call_ratio: Optional[float]
    call_volume_signal: str
    trigger: str
    target: str
    structure: str
    data_gaps: str
    notes: str


def parse_watchlist(raw: str) -> List[str]:
    if not raw:
        return DEFAULT_WATCHLIST[:]
    return [item.strip().upper() for item in raw.split(",") if item.strip()]


def safe_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number) or number <= 0:
        return None
    return number


def safe_number(value) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def expiry_to_date(expiration: str) -> date:
    return datetime.strptime(expiration, "%Y%m%d").date()


def is_third_friday(expiration: str) -> bool:
    day = expiry_to_date(expiration)
    return day.weekday() == 4 and 15 <= day.day <= 21


def select_expirations(expirations: Sequence[str], today: Optional[date] = None) -> List[str]:
    today = today or date.today()
    future = sorted(exp for exp in expirations if expiry_to_date(exp) >= today)
    if not future:
        return []
    nearest = future[0]
    monthly = next((exp for exp in future if exp != nearest and is_third_friday(exp)), None)
    selected = [nearest]
    if monthly:
        selected.append(monthly)
    elif len(future) > 1:
        selected.append(future[1])
    return selected


def select_strikes(
    strikes: Sequence[float],
    spot: float,
    pct_window: float = 0.15,
    max_each_side: int = 20,
) -> List[float]:
    clean = sorted({float(strike) for strike in strikes if safe_float(strike)})
    if not clean or spot <= 0:
        return []
    lower = spot * (1 - pct_window)
    upper = spot * (1 + pct_window)
    in_window = [strike for strike in clean if lower <= strike <= upper]
    below = [strike for strike in clean if strike < spot][-max_each_side:]
    above = [strike for strike in clean if strike >= spot][:max_each_side]
    return sorted(set(in_window + below + above))


def mid_or_last(bid: Optional[float], ask: Optional[float], last: Optional[float]) -> Optional[float]:
    if bid and ask:
        return (bid + ask) / 2
    return last or bid or ask


def option_price(quote: OptionQuote) -> float:
    return mid_or_last(quote.bid, quote.ask, quote.last) or 0.0


def compute_max_pain(quotes: Sequence[OptionQuote]) -> Optional[float]:
    strikes = sorted({q.strike for q in quotes})
    if not strikes:
        return None
    oi_quotes = [q for q in quotes if q.open_interest is not None]
    if not oi_quotes:
        return None

    payouts: List[Tuple[float, float]] = []
    for candidate in strikes:
        total = 0.0
        for quote in oi_quotes:
            oi = quote.open_interest or 0.0
            if quote.right == "C":
                total += max(candidate - quote.strike, 0.0) * oi * 100
            elif quote.right == "P":
                total += max(quote.strike - candidate, 0.0) * oi * 100
        payouts.append((candidate, total))
    return min(payouts, key=lambda row: row[1])[0]


def largest_oi_strike(quotes: Sequence[OptionQuote], right: str) -> Optional[float]:
    rows = [q for q in quotes if q.right == right and q.open_interest is not None]
    if not rows:
        return None
    return max(rows, key=lambda q: q.open_interest or 0).strike


def nearest_call_walls(quotes: Sequence[OptionQuote], spot: float) -> Tuple[Optional[float], Optional[float]]:
    calls = [q for q in quotes if q.right == "C" and q.strike >= spot and q.open_interest is not None]
    by_strike: Dict[float, float] = {}
    for quote in calls:
        by_strike[quote.strike] = by_strike.get(quote.strike, 0.0) + (quote.open_interest or 0.0)
    ranked = sorted(by_strike.items(), key=lambda row: (-row[1], row[0]))
    if not ranked:
        return None, None
    first = ranked[0][0]
    next_above = next((strike for strike, _ in ranked if strike > first), None)
    return first, next_above


def put_call_volume_ratio(quotes: Sequence[OptionQuote]) -> Optional[float]:
    call_volume = sum(q.volume or 0 for q in quotes if q.right == "C")
    put_volume = sum(q.volume or 0 for q in quotes if q.right == "P")
    if call_volume <= 0:
        return None
    return put_volume / call_volume


def has_gamma(quotes: Sequence[OptionQuote]) -> bool:
    return any(q.gamma is not None for q in quotes)


def scan_ticker_from_quotes(ticker: str, spot: Optional[float], quotes: Sequence[OptionQuote], error: str = "") -> TickerScan:
    if error:
        return TickerScan(
            ticker=ticker,
            status="DATA_MISSING",
            score=0,
            setup="DATA_MISSING",
            spot=spot,
            expiry=None,
            nearest_call_wall=None,
            next_call_wall=None,
            largest_call_oi_strike=None,
            largest_put_oi_strike=None,
            max_pain=None,
            put_call_ratio=None,
            call_volume_signal="DATA_MISSING",
            trigger="DATA_MISSING",
            target="DATA_MISSING",
            structure="",
            data_gaps=error,
            notes="IBKR data fetch failed.",
        )
    if spot is None:
        return scan_ticker_from_quotes(ticker, None, [], "missing underlying spot")
    if not quotes:
        return scan_ticker_from_quotes(ticker, spot, [], "missing options chain")

    expiries = sorted({q.expiration for q in quotes})
    expiry = expiries[0] if expiries else None
    nearest_quotes = [q for q in quotes if q.expiration == expiry] if expiry else list(quotes)
    oi_available = any(q.open_interest is not None for q in nearest_quotes)
    volume_available = any(q.volume is not None for q in nearest_quotes)

    if not oi_available:
        return TickerScan(
            ticker=ticker,
            status="DATA_MISSING",
            score=0,
            setup="DATA_MISSING",
            spot=spot,
            expiry=expiry,
            nearest_call_wall=None,
            next_call_wall=None,
            largest_call_oi_strike=None,
            largest_put_oi_strike=None,
            max_pain=None,
            put_call_ratio=put_call_volume_ratio(nearest_quotes) if volume_available else None,
            call_volume_signal="volume available" if volume_available else "DATA_MISSING",
            trigger="DATA_MISSING",
            target="DATA_MISSING",
            structure="",
            data_gaps="missing option open interest",
            notes="Cannot compute call walls or max pain without OI.",
        )

    nearest_wall, next_wall = nearest_call_walls(nearest_quotes, spot)
    largest_call = largest_oi_strike(nearest_quotes, "C")
    largest_put = largest_oi_strike(nearest_quotes, "P")
    pain = compute_max_pain(nearest_quotes)
    pcr = put_call_volume_ratio(nearest_quotes) if volume_available else None

    gaps = []
    if not volume_available:
        gaps.append("missing option volume")
    if not has_gamma(nearest_quotes):
        gaps.append("missing option Greeks/gamma")

    score = 0
    setup = "NO_SETUP"
    status = "NO_TRADE"
    trigger = ""
    target = ""
    structure = ""
    notes = "OI chain available; no actionable trigger without catalyst/price confirmation."
    if nearest_wall:
        distance = abs(nearest_wall - spot) / spot
        if distance <= 0.015:
            score += 2
            setup = "GAMMA_BREAKOUT" if has_gamma(nearest_quotes) else "WATCH_CALL_WALL"
            status = "WATCH"
            trigger = f"break and hold above {nearest_wall:g}"
            target = f"{next_wall:g}" if next_wall else ""
            structure = "consider bull call spread after catalyst confirmation" if next_wall else ""
            notes = f"Spot is within {distance:.1%} of the nearest call wall."
        elif distance <= 0.04:
            score += 1
            status = "WATCH"
            setup = "CALL_WALL_APPROACH"
            trigger = f"move toward {nearest_wall:g}"
            target = f"{nearest_wall:g}"
            notes = f"Nearest call wall is {distance:.1%} above spot."

    return TickerScan(
        ticker=ticker,
        status=status,
        score=score,
        setup=setup,
        spot=spot,
        expiry=expiry,
        nearest_call_wall=nearest_wall,
        next_call_wall=next_wall,
        largest_call_oi_strike=largest_call,
        largest_put_oi_strike=largest_put,
        max_pain=pain,
        put_call_ratio=pcr,
        call_volume_signal="available" if volume_available else "DATA_MISSING",
        trigger=trigger,
        target=target,
        structure=structure,
        data_gaps=", ".join(gaps),
        notes=notes,
    )


class IBKROptionsProvider:
    def __init__(
        self,
        host: str,
        port: int,
        client_id: int,
        readonly: bool = True,
        snapshot: bool = False,
        sleep_seconds: float = 3.0,
        request_pause: float = 0.05,
        market_data_batch_size: int = 40,
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.readonly = readonly
        self.snapshot = snapshot
        self.sleep_seconds = sleep_seconds
        self.request_pause = request_pause
        self.market_data_batch_size = market_data_batch_size
        self.ib = None
        self.ib_mod = None

    def connect(self) -> None:
        try:
            import ib_insync as ib_mod
        except ImportError as exc:
            raise RuntimeError("ib_insync is not installed; install backend_api_python/requirements.txt") from exc
        self.ib_mod = ib_mod
        self.ib = ib_mod.IB()
        self.ib.connect(self.host, self.port, clientId=self.client_id, readonly=self.readonly, timeout=10)

    def disconnect(self) -> None:
        if self.ib is not None and self.ib.isConnected():
            self.ib.disconnect()

    def _stock_contract(self, ticker: str):
        contract = self.ib_mod.Stock(ticker, "SMART", "USD")
        qualified = self.ib.qualifyContracts(contract)
        if not qualified:
            raise RuntimeError(f"IBKR could not qualify underlying contract for {ticker}")
        return qualified[0]

    def get_spot(self, ticker: str) -> Tuple[float, object]:
        contract = self._stock_contract(ticker)
        market = self.ib.reqMktData(contract, "", self.snapshot, False)
        self.ib.sleep(self.sleep_seconds)
        spot = (
            safe_float(getattr(market, "marketPrice", lambda: None)())
            or safe_float(getattr(market, "last", None))
            or safe_float(getattr(market, "close", None))
            or mid_or_last(safe_float(getattr(market, "bid", None)), safe_float(getattr(market, "ask", None)), None)
        )
        self.ib.cancelMktData(contract)
        if spot is None:
            raise RuntimeError(f"missing spot quote for {ticker}; check underlying market data subscription")
        return spot, contract

    def get_option_quotes(
        self,
        ticker: str,
        spot: float,
        underlying_contract,
        pct_window: float,
        max_each_side: int,
    ) -> List[OptionQuote]:
        chains = self.ib.reqSecDefOptParams(
            underlyingSymbol=ticker,
            futFopExchange="",
            underlyingSecType="STK",
            underlyingConId=underlying_contract.conId,
        )
        chain = next((row for row in chains if row.exchange == "SMART" and row.tradingClass == ticker), None)
        if chain is None and chains:
            chain = chains[0]
        if chain is None:
            raise RuntimeError(f"missing option security definition parameters for {ticker}")

        expirations = select_expirations(list(chain.expirations))
        strikes = select_strikes(list(chain.strikes), spot, pct_window=pct_window, max_each_side=max_each_side)
        if not expirations or not strikes:
            raise RuntimeError(f"empty filtered option universe for {ticker}")

        contracts = []
        for expiration in expirations:
            for strike in strikes:
                for right in ("C", "P"):
                    contracts.append(self.ib_mod.Option(ticker, expiration, strike, right, "SMART", currency="USD", multiplier="100"))

        qualified = []
        chunk_size = 40
        for idx in range(0, len(contracts), chunk_size):
            qualified.extend(self.ib.qualifyContracts(*contracts[idx:idx + chunk_size]))
            self.ib.sleep(self.request_pause)

        quotes = []
        generic_ticks = "100,101,106"
        for idx in range(0, len(qualified), self.market_data_batch_size):
            batch = qualified[idx:idx + self.market_data_batch_size]
            tickers = []
            for contract in batch:
                tickers.append(self.ib.reqMktData(contract, generic_ticks, self.snapshot, False))
                self.ib.sleep(self.request_pause)
            self.ib.sleep(self.sleep_seconds)
            quotes.extend(self._ticker_to_quote(ticker, market) for market in tickers)
            for contract in batch:
                self.ib.cancelMktData(contract)
            self.ib.sleep(self.request_pause)
        return quotes

    def _ticker_to_quote(self, requested_ticker: str, market) -> OptionQuote:
        contract = market.contract
        right = contract.right
        greeks = getattr(market, "modelGreeks", None) or getattr(market, "bidGreeks", None) or getattr(market, "askGreeks", None)
        oi_attr = "callOpenInterest" if right == "C" else "putOpenInterest"
        volume_attr = "callVolume" if right == "C" else "putVolume"
        return OptionQuote(
            ticker=requested_ticker,
            expiration=str(contract.lastTradeDateOrContractMonth),
            strike=float(contract.strike),
            right=right,
            bid=safe_float(getattr(market, "bid", None)),
            ask=safe_float(getattr(market, "ask", None)),
            last=safe_float(getattr(market, "last", None)),
            volume=safe_float(getattr(market, volume_attr, None)) or safe_float(getattr(market, "volume", None)),
            open_interest=safe_float(getattr(market, oi_attr, None)),
            implied_volatility=safe_float(getattr(greeks, "impliedVol", None)) if greeks else None,
            delta=safe_number(getattr(greeks, "delta", None)) if greeks else None,
            gamma=safe_number(getattr(greeks, "gamma", None)) if greeks else None,
            theta=safe_number(getattr(greeks, "theta", None)) if greeks else None,
            vega=safe_number(getattr(greeks, "vega", None)) if greeks else None,
        )


def scan_watchlist(provider: IBKROptionsProvider, watchlist: Sequence[str], pct_window: float, max_each_side: int) -> List[TickerScan]:
    scans: List[TickerScan] = []
    for ticker in watchlist:
        try:
            spot, underlying = provider.get_spot(ticker)
            quotes = provider.get_option_quotes(ticker, spot, underlying, pct_window, max_each_side)
            scans.append(scan_ticker_from_quotes(ticker, spot, quotes))
        except Exception as exc:
            scans.append(scan_ticker_from_quotes(ticker, None, [], str(exc)))
    return scans


def fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def write_csv(path: str, scan_date: date, scans: Sequence[TickerScan]) -> None:
    columns = [
        "date", "ticker", "status", "score", "setup", "spot", "expiry",
        "nearest_call_wall", "next_call_wall", "largest_call_oi_strike",
        "largest_put_oi_strike", "max_pain", "put_call_ratio",
        "call_volume_signal", "catalyst", "trigger", "target", "structure",
        "data_gaps", "notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in scans:
            writer.writerow({
                "date": scan_date.isoformat(),
                "ticker": row.ticker,
                "status": row.status,
                "score": row.score,
                "setup": row.setup,
                "spot": fmt(row.spot),
                "expiry": row.expiry or "",
                "nearest_call_wall": fmt(row.nearest_call_wall),
                "next_call_wall": fmt(row.next_call_wall),
                "largest_call_oi_strike": fmt(row.largest_call_oi_strike),
                "largest_put_oi_strike": fmt(row.largest_put_oi_strike),
                "max_pain": fmt(row.max_pain),
                "put_call_ratio": fmt(row.put_call_ratio),
                "call_volume_signal": row.call_volume_signal,
                "catalyst": "",
                "trigger": row.trigger,
                "target": row.target,
                "structure": row.structure,
                "data_gaps": row.data_gaps,
                "notes": row.notes,
            })


def table_rows(scans: Iterable[TickerScan], statuses: Sequence[str]) -> List[TickerScan]:
    return [row for row in scans if row.status in statuses]


def write_markdown(path: str, scan_date: date, scans: Sequence[TickerScan]) -> None:
    high = [row for row in scans if row.status == "TRADE_CANDIDATE"]
    watch = table_rows(scans, ["WATCH"])
    skipped = table_rows(scans, ["NO_TRADE", "DATA_MISSING"])

    lines = [
        f"# Daily OI Gamma Watchlist - {scan_date.isoformat()}",
        "",
        "## Market Context",
        "- Index regime: DATA_MISSING",
        "- Volatility/VIX: DATA_MISSING",
        "- Macro events today/this week: DATA_MISSING",
        "- Sector themes: DATA_MISSING",
        "",
        "## High Priority",
        "| ticker | score | setup | spot | trigger | target | structure | key reason |",
        "|---|---:|---|---:|---|---|---|---|",
    ]
    for row in high:
        lines.append(f"| {row.ticker} | {row.score} | {row.setup} | {fmt(row.spot)} | {row.trigger} | {row.target} | {row.structure} | {row.notes} |")
    if not high:
        lines.append("| - | - | - | - | - | - | - | No trade candidates from IBKR-only chain scan. |")

    lines.extend([
        "",
        "## Watch",
        "| ticker | score | setup | spot | trigger | target | structure | key reason |",
        "|---|---:|---|---:|---|---|---|---|",
    ])
    for row in watch:
        lines.append(f"| {row.ticker} | {row.score} | {row.setup} | {fmt(row.spot)} | {row.trigger} | {row.target} | {row.structure} | {row.notes} |")
    if not watch:
        lines.append("| - | - | - | - | - | - | - | No watch setups from IBKR-only chain scan. |")

    lines.extend([
        "",
        "## No Trade / Data Missing",
        "| ticker | status | reason |",
        "|---|---|---|",
    ])
    for row in skipped:
        reason = row.data_gaps or row.notes
        lines.append(f"| {row.ticker} | {row.status} | {reason} |")

    lines.extend(["", "## Per-Ticker Notes"])
    for row in scans:
        lines.extend([
            f"### {row.ticker}",
            f"- Status: {row.status}",
            "- Direction: NO_DIRECTION",
            "- Catalyst:",
            f"- Spot / trend: {fmt(row.spot)} / DATA_MISSING",
            "- Options chain:",
            f"  - nearest call wall: {fmt(row.nearest_call_wall)}",
            f"  - next call wall: {fmt(row.next_call_wall)}",
            f"  - largest call OI: {fmt(row.largest_call_oi_strike)}",
            f"  - largest put OI: {fmt(row.largest_put_oi_strike)}",
            f"  - max pain: {fmt(row.max_pain)}",
            f"  - put/call: {fmt(row.put_call_ratio)}",
            f"  - call volume: {row.call_volume_signal}",
            f"- Setup: {row.setup}",
            f"- Candidate structure: {row.structure}",
            f"- Invalidation / reason to skip: {row.notes}",
            f"- Data gaps: {row.data_gaps}",
            "",
        ])

    lines.extend([
        "## Paper Trade Candidates",
        "| ticker | thesis | trigger | structure | target | data needed |",
        "|---|---|---|---|---|---|",
        "| - | - | - | - | - | Need catalyst/price confirmation before candidate generation. |",
        "",
        "## Review Questions",
        "- Did any ticker break a call wall?",
        "- Did any ticker pin to max pain?",
        "- Did call volume confirm or fade?",
        "- Which candidates should be reviewed after close?",
        "",
    ])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def output_paths(output_dir: str, scan_date: date) -> Tuple[str, str]:
    abs_dir = output_dir if os.path.isabs(output_dir) else os.path.join(PROJECT_ROOT, output_dir)
    os.makedirs(abs_dir, exist_ok=True)
    stem = f"{scan_date.isoformat()}-oi-gamma-watchlist"
    return os.path.join(abs_dir, f"{stem}.md"), os.path.join(abs_dir, f"{stem}.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run IBKR OI/gamma watchlist scanner.")
    parser.add_argument("--watchlist", default=",".join(DEFAULT_WATCHLIST), help="Comma-separated tickers.")
    parser.add_argument("--host", default=os.getenv("IBKR_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("IBKR_PORT", "4002")), help="Gateway paper default 4002.")
    parser.add_argument("--client-id", type=int, default=int(os.getenv("IBKR_CLIENT_ID", "19")))
    parser.add_argument("--pct-window", type=float, default=0.15)
    parser.add_argument("--max-each-side", type=int, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=3.0)
    parser.add_argument("--request-pause", type=float, default=0.05)
    parser.add_argument("--market-data-batch-size", type=int, default=40)
    parser.add_argument("--snapshot", action="store_true", help="Request snapshot market data instead of streaming samples.")
    parser.add_argument("--connect-only", action="store_true", help="Only verify IBKR connection.")
    parser.add_argument("--out-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--date", default=date.today().isoformat())
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    scan_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    provider = IBKROptionsProvider(
        host=args.host,
        port=args.port,
        client_id=args.client_id,
        readonly=True,
        snapshot=args.snapshot,
        sleep_seconds=args.sleep_seconds,
        request_pause=args.request_pause,
        market_data_batch_size=args.market_data_batch_size,
    )
    try:
        provider.connect()
        if args.connect_only:
            print(f"Connected to IBKR at {args.host}:{args.port} clientId={args.client_id}")
            return 0
        scans = scan_watchlist(provider, parse_watchlist(args.watchlist), args.pct_window, args.max_each_side)
    finally:
        provider.disconnect()

    md_path, csv_path = output_paths(args.out_dir, scan_date)
    write_markdown(md_path, scan_date, scans)
    write_csv(csv_path, scan_date, scans)
    print(f"Markdown: {os.path.relpath(md_path, PROJECT_ROOT)}")
    print(f"CSV: {os.path.relpath(csv_path, PROJECT_ROOT)}")
    missing = [row for row in scans if row.status == "DATA_MISSING"]
    if missing:
        print(f"DATA_MISSING: {len(missing)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
