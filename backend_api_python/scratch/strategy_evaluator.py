#!/usr/bin/env python3
"""
GIPS-style Strategy Evaluator
==============================
Industry-standard performance evaluation, replacing alpha-vs-B&H pass/fail.

WHY THIS EXISTS:
    backtest_runner.py reports "alpha vs Buy-and-Hold" as the primary criterion.
    For regime-conditional strategies (sparse triggers, mostly-flat exposure), B&H
    comparison is misleading — a strategy can have positive expectancy yet show
    massively negative "alpha" simply by being in cash during a bull run.

    This evaluator implements industry-standard metrics from:
      - GIPS (Global Investment Performance Standards, CFA Institute)
      - Grinold & Kahn, "Active Portfolio Management" (3rd ed., 2019)
      - Carl Bacon, "Practical Portfolio Performance Measurement" (2008)

WHAT IT REPORTS:
    Return metrics:    CAGR, total return
    Risk metrics:      annualized volatility, max drawdown, downside deviation
    Risk-adjusted:     Sharpe, Sortino, Calmar (= MAR ratio)
    Trade quality:     win rate, profit factor, avg win/loss, payoff ratio
    Active mgmt:       β vs BTC, Jensen's α, tracking error, Information Ratio
    Exposure:          % time in market (capacity), in-market vs flat returns

REFERENCES:
    Sharpe (1966): mean excess return / std
    Sortino (1994): mean excess return / downside std
    Calmar (Young 1991): CAGR / |max drawdown|
    Jensen's α (1968): r_p - rf - β(r_m - rf)
    Information Ratio (Goodwin 1998): active_return / tracking_error

USAGE:
    docker exec -w /app quantdinger-backend python3 scratch/strategy_evaluator.py \\
        research/examples/strategies/kol_range_fade_4h_long.py \\
        --symbol BTC/USDT --timeframe 4H --is-days 2200 --oos-days 365

NOTES:
    - Risk-free rate defaults to 0% (crypto convention; can override --rf)
    - Annualization factor inferred from timeframe (1D: 365, 4H: 6×365, 1H: 24×365)
    - Bar-level returns derived from equityCurve; benchmark from BTC close
"""

import os
import sys
import argparse
import csv
import math
import subprocess
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService
from app.data_sources.alt_data import fetch_binance_funding_rate


class AltDataBacktestService(BacktestService):
    """Mirror of backtest_runner's hijack so funding-rate strategies still work."""
    def _fetch_kline_data(self, market, symbol, timeframe, start_date, end_date):
        df = super()._fetch_kline_data(market, symbol, timeframe, start_date, end_date)
        try:
            df_funding = fetch_binance_funding_rate(symbol, start_date, end_date)
            if not df_funding.empty:
                df_funding.set_index('time', inplace=True)
                df = df.join(df_funding, how='left')
                df['funding_rate'] = df['funding_rate'].ffill().fillna(0)
            else:
                df['funding_rate'] = 0
        except Exception:
            if 'funding_rate' not in df.columns:
                df['funding_rate'] = 0
        return df


# ----------------------------------------------------------------------------
# Annualization
# ----------------------------------------------------------------------------

def bars_per_year(timeframe):
    """Annualization factor by timeframe."""
    tf = timeframe.upper()
    if tf == '1D':
        return 365
    if tf == '12H':
        return 365 * 2
    if tf == '8H':
        return 365 * 3
    if tf == '4H':
        return 365 * 6
    if tf == '2H':
        return 365 * 12
    if tf == '1H':
        return 365 * 24
    if tf == '30M':
        return 365 * 48
    if tf == '15M':
        return 365 * 96
    if tf == '5M':
        return 365 * 288
    if tf == '1M':
        return 365 * 1440
    raise ValueError(f"Unknown timeframe: {timeframe}")


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------

def to_returns(equity_series):
    """Bar-to-bar simple returns from an equity curve."""
    return equity_series.pct_change().dropna()


def cagr(equity_series, periods_per_year):
    if len(equity_series) < 2:
        return 0.0
    total_return = equity_series.iloc[-1] / equity_series.iloc[0] - 1
    years = len(equity_series) / periods_per_year
    if years <= 0:
        return 0.0
    return (1 + total_return) ** (1 / years) - 1


def annualized_vol(returns, periods_per_year):
    return float(returns.std() * math.sqrt(periods_per_year))


def downside_deviation(returns, mar=0.0, periods_per_year=365):
    """Sortino's denominator: std of negative excess returns vs MAR (minimum acceptable return)."""
    excess = returns - mar / periods_per_year
    downside = excess[excess < 0]
    if len(downside) < 2:
        return float('nan')
    return float(downside.std() * math.sqrt(periods_per_year))


def sharpe_ratio(returns, rf, periods_per_year):
    if len(returns) < 2 or returns.std() == 0:
        return float('nan')
    excess = returns - rf / periods_per_year
    return float(excess.mean() / returns.std() * math.sqrt(periods_per_year))


def sortino_ratio(returns, rf, periods_per_year):
    excess_mean = returns.mean() - rf / periods_per_year
    dd = downside_deviation(returns, mar=rf, periods_per_year=periods_per_year)
    if dd == 0 or math.isnan(dd):
        return float('nan')
    return float(excess_mean * periods_per_year / dd)


def max_drawdown(equity_series):
    if len(equity_series) == 0:
        return 0.0
    cummax = equity_series.cummax()
    dd = (equity_series / cummax - 1.0)
    return float(dd.min())


def calmar_ratio(equity_series, periods_per_year):
    """CAGR / |MDD|. Also called MAR ratio."""
    cg = cagr(equity_series, periods_per_year)
    mdd = max_drawdown(equity_series)
    if mdd == 0:
        return float('nan')
    return float(cg / abs(mdd))


def beta_alpha_ir(strategy_returns, benchmark_returns, rf, periods_per_year):
    """CAPM-style β + Jensen's α + Information Ratio.

    Returns dict with: beta, alpha_annual, tracking_error, information_ratio.
    """
    aligned = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner').dropna()
    aligned.columns = ['s', 'b']
    if len(aligned) < 30:
        return {'beta': float('nan'), 'alpha_annual': float('nan'),
                'tracking_error': float('nan'), 'information_ratio': float('nan')}

    var_b = aligned['b'].var()
    if var_b == 0:
        beta = float('nan')
    else:
        cov_sb = ((aligned['s'] - aligned['s'].mean()) * (aligned['b'] - aligned['b'].mean())).mean()
        beta = float(cov_sb / var_b)

    rf_per = rf / periods_per_year
    # Jensen's alpha (annualized)
    alpha_per_bar = aligned['s'].mean() - rf_per - beta * (aligned['b'].mean() - rf_per)
    alpha_annual = float(alpha_per_bar * periods_per_year)

    # Active return = strategy - benchmark; tracking error = std of active return
    active = aligned['s'] - aligned['b']
    te = float(active.std() * math.sqrt(periods_per_year))
    if te == 0:
        ir = float('nan')
    else:
        ir = float(active.mean() / active.std() * math.sqrt(periods_per_year))

    return {'beta': beta, 'alpha_annual': alpha_annual,
            'tracking_error': te, 'information_ratio': ir}


def trade_stats(trades):
    """Profit factor, payoff ratio, avg win, avg loss, etc."""
    closing = [t for t in trades if t.get('profit', 0) != 0]
    wins = [t['profit'] for t in closing if t['profit'] > 0]
    losses = [t['profit'] for t in closing if t['profit'] < 0]
    n = len(closing)
    if n == 0:
        return {'n_trades': 0, 'win_rate': float('nan'), 'avg_win': float('nan'),
                'avg_loss': float('nan'), 'payoff_ratio': float('nan'),
                'profit_factor': float('nan'), 'gross_win': 0, 'gross_loss': 0}
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    avg_win = float(np.mean(wins)) if wins else float('nan')
    avg_loss = float(np.mean(losses)) if losses else float('nan')
    payoff = avg_win / abs(avg_loss) if (losses and avg_loss != 0) else float('nan')
    pf = gross_win / gross_loss if gross_loss > 0 else (gross_win if gross_win > 0 else 0)
    return {
        'n_trades': n,
        'win_rate': len(wins) / n,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'payoff_ratio': payoff,
        'profit_factor': pf,
        'gross_win': gross_win,
        'gross_loss': gross_loss,
    }


# ----------------------------------------------------------------------------
# Experiment log (auto-appended on every run)
# ----------------------------------------------------------------------------

LOG_FIELDS = [
    'timestamp', 'strategy_file', 'git_sha', 'symbol', 'timeframe', 'period',
    'total_return', 'cagr', 'max_drawdown',
    'sharpe', 'sortino', 'calmar',
    'beta', 'jensen_alpha', 'tracking_error', 'information_ratio',
    'profit_factor', 'win_rate', 'payoff_ratio',
    'n_trades', 'avg_win', 'avg_loss',
    'pct_in_market',
]


def get_git_sha(file_path):
    """Best-effort git SHA for the file's repo. Returns 'nogit' if unavailable
    (e.g. running inside a Docker container where .git isn't mounted)."""
    try:
        d = os.path.dirname(file_path) or '.'
        result = subprocess.run(
            ['git', '-C', d, 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return 'nogit'
        sha = result.stdout.strip()
        dirty = subprocess.run(
            ['git', '-C', d, 'status', '--porcelain', file_path],
            capture_output=True, text=True, timeout=5,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            sha += '-dirty'
        return sha
    except Exception:
        return 'nogit'


def append_log(log_path, row):
    is_new = not os.path.exists(log_path)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS, extrasaction='ignore')
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def exposure_stats(equity_series):
    """Capacity = fraction of bars where equity moved (i.e., position was open)."""
    rets = to_returns(equity_series)
    in_position = (rets.abs() > 1e-9)
    return {
        'pct_in_market': float(in_position.mean()),
        'in_market_avg_return': float(rets[in_position].mean()) if in_position.any() else float('nan'),
        'flat_avg_return': float(rets[~in_position].mean()) if (~in_position).any() else float('nan'),
    }


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------

def run_backtest(strategy_path, symbol, timeframe, start, end, args):
    svc = AltDataBacktestService()
    with open(strategy_path, 'r', encoding='utf-8') as f:
        code = f.read()
    result = svc.run(
        indicator_code=code,
        market=args.market,
        symbol=symbol,
        timeframe=timeframe,
        start_date=start,
        end_date=end,
        initial_capital=args.capital,
        leverage=args.leverage,
        commission=args.commission,
        slippage=args.slippage,
    )
    return result


def benchmark_returns(symbol, timeframe, start, end, args):
    """BTC bar-level returns (passive long benchmark)."""
    svc = AltDataBacktestService()
    df = svc._fetch_kline_data(args.market, symbol, timeframe, start, end)
    if df is None or len(df) == 0:
        return pd.Series(dtype=float)
    closes = df['close'].astype(float)
    return closes.pct_change().dropna()


def equity_to_returns(equity_curve):
    """equityCurve = [{'time': ..., 'value': ...}, ...] → Series indexed by time."""
    if not equity_curve:
        return pd.Series(dtype=float)
    df = pd.DataFrame(equity_curve)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').sort_index()
    return df['value'].astype(float)


def evaluate_period(strategy_path, label, start, end, args):
    print(f"\n{'─' * 76}")
    print(f"  {label}: {start.date()} → {end.date()}")
    print(f"{'─' * 76}")

    result = run_backtest(strategy_path, args.symbol, args.timeframe, start, end, args)
    if not result or result.get('error'):
        print(f"  ❌ Backtest failed: {result.get('error') if result else 'no result'}")
        return None

    equity = equity_to_returns(result.get('equityCurve') or [])
    if len(equity) < 2:
        print(f"  ❌ Equity curve empty or too short")
        return None

    rets = to_returns(equity)
    bench = benchmark_returns(args.symbol, args.timeframe, start, end, args)
    # Re-align benchmark to strategy's bar timeline
    bench = bench.reindex(rets.index, method='nearest').dropna()

    ppy = bars_per_year(args.timeframe)
    rf = args.rf

    cg = cagr(equity, ppy)
    vol = annualized_vol(rets, ppy)
    mdd = max_drawdown(equity)
    sharpe = sharpe_ratio(rets, rf, ppy)
    sortino = sortino_ratio(rets, rf, ppy)
    calmar = calmar_ratio(equity, ppy)
    capm = beta_alpha_ir(rets, bench, rf, ppy)
    trades = trade_stats(result.get('trades') or [])
    expos = exposure_stats(equity)

    bh_total = float(equity.iloc[-1] / equity.iloc[0] - 1) * 0  # placeholder; we'll compute B&H below
    bench_total = float((1 + bench).prod() - 1) if len(bench) > 0 else 0.0

    print(f"\n  📊 RETURN")
    print(f"    Total return:          {(equity.iloc[-1]/equity.iloc[0]-1)*100:+.2f}%   (CAGR: {cg*100:+.2f}%)")
    print(f"    BTC B&H total:         {bench_total*100:+.2f}%   (reference, not pass/fail)")

    print(f"\n  📉 RISK")
    print(f"    Annualized volatility: {vol*100:.2f}%")
    print(f"    Maximum drawdown:      {mdd*100:.2f}%")

    print(f"\n  ⚖️  RISK-ADJUSTED")
    print(f"    Sharpe ratio:          {sharpe:+.3f}")
    print(f"    Sortino ratio:         {sortino:+.3f}")
    print(f"    Calmar ratio (MAR):    {calmar:+.3f}")

    print(f"\n  🎯 ACTIVE MANAGEMENT (vs BTC B&H)")
    print(f"    β (beta to BTC):       {capm['beta']:+.3f}")
    print(f"    α (Jensen, annual):    {capm['alpha_annual']*100:+.2f}%")
    print(f"    Tracking error:        {capm['tracking_error']*100:.2f}%")
    print(f"    Information Ratio:     {capm['information_ratio']:+.3f}    {_ir_verdict(capm['information_ratio'])}")

    print(f"\n  💼 TRADE QUALITY")
    print(f"    Trades:                {trades['n_trades']}")
    if trades['n_trades'] > 0:
        print(f"    Win rate:              {trades['win_rate']*100:.1f}%")
        print(f"    Avg win:               +${trades['avg_win']:.2f}    Avg loss: ${trades['avg_loss']:.2f}")
        print(f"    Payoff ratio:          {trades['payoff_ratio']:.2f}")
        print(f"    Profit factor:         {trades['profit_factor']:.2f}    {_pf_verdict(trades['profit_factor'])}")

    print(f"\n  ⏱️  EXPOSURE")
    print(f"    % time in market:      {expos['pct_in_market']*100:.1f}%")
    if not math.isnan(expos['in_market_avg_return']):
        print(f"    Avg bar return (in):   {expos['in_market_avg_return']*100:+.4f}%")

    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1)

    return {
        'label': label,
        'total_return': total_return,
        'cagr': cg,
        'max_drawdown': mdd,
        'sharpe': sharpe,
        'sortino': sortino,
        'calmar': calmar,
        'beta': capm['beta'],
        'jensen_alpha': capm['alpha_annual'],
        'tracking_error': capm['tracking_error'],
        'information_ratio': capm['information_ratio'],
        'profit_factor': trades['profit_factor'],
        'win_rate': trades['win_rate'],
        'payoff_ratio': trades['payoff_ratio'],
        'n_trades': trades['n_trades'],
        'avg_win': trades['avg_win'],
        'avg_loss': trades['avg_loss'],
        'pct_in_market': expos['pct_in_market'],
    }


def _ir_verdict(ir):
    if math.isnan(ir):
        return ''
    if ir >= 2.0:
        return '🏆 elite (>=2.0)'
    if ir >= 1.0:
        return '⭐ strong (>=1.0)'
    if ir >= 0.5:
        return '✓ acceptable (>=0.5)'
    if ir >= 0.0:
        return '⚠️ weak (>=0)'
    return '❌ negative (loses to benchmark)'


def _pf_verdict(pf):
    if math.isnan(pf):
        return ''
    if pf >= 2.0:
        return '🏆 strong'
    if pf >= 1.5:
        return '⭐ good'
    if pf >= 1.2:
        return '✓ acceptable'
    if pf >= 1.0:
        return '⚠️ marginal (covers nothing)'
    return '❌ losing system'


def main():
    parser = argparse.ArgumentParser(description="GIPS-style Strategy Evaluator")
    parser.add_argument("strategy_file")
    parser.add_argument("--market", default="Crypto")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1D")
    parser.add_argument("--capital", type=float, default=10000.0)
    parser.add_argument("--leverage", type=int, default=1)
    parser.add_argument("--commission", type=float, default=0.001)
    parser.add_argument("--slippage", type=float, default=0.0005)
    parser.add_argument("--rf", type=float, default=0.0, help="Annualized risk-free rate (0 = crypto convention)")
    parser.add_argument("--is-days", type=int, default=2200)
    parser.add_argument("--oos-days", type=int, default=365)
    parser.add_argument("--log", default="research/experiment_log.csv",
                        help="Auto-append log path (relative to project root). Empty string to disable.")
    args = parser.parse_args()

    strategy_path = os.path.join(PROJECT_ROOT, args.strategy_file)
    if not os.path.exists(strategy_path):
        print(f"❌ Strategy file not found: {strategy_path}")
        sys.exit(1)

    now = datetime.utcnow()
    is_start = now - timedelta(days=args.is_days)
    is_end = now - timedelta(days=args.oos_days)
    oos_start = is_end
    oos_end = now

    print("=" * 76)
    print(f"  📈 GIPS-STYLE STRATEGY EVALUATION")
    print(f"  Strategy:  {args.strategy_file}")
    print(f"  Symbol:    {args.symbol}   Timeframe: {args.timeframe}")
    print(f"  Costs:     slippage {args.slippage*100}%   commission {args.commission*100}%")
    print(f"  Risk-free: {args.rf*100}% (annualized)")
    print("=" * 76)

    git_sha = get_git_sha(strategy_path)
    log_path = os.path.join(PROJECT_ROOT, args.log) if args.log else None
    timestamp = datetime.utcnow().isoformat(timespec='seconds')

    def log_period(period_label, metrics):
        if metrics is None or log_path is None:
            return
        row = {
            'timestamp': timestamp,
            'strategy_file': args.strategy_file,
            'git_sha': git_sha,
            'symbol': args.symbol,
            'timeframe': args.timeframe,
            'period': period_label,
            **{k: v for k, v in metrics.items() if k in LOG_FIELDS},
        }
        append_log(log_path, row)

    with app.app_context():
        is_metrics = evaluate_period(strategy_path, "IN-SAMPLE", is_start, is_end, args)
        log_period('IS', is_metrics)
        oos_metrics = evaluate_period(strategy_path, "OUT-OF-SAMPLE", oos_start, oos_end, args)
        log_period('OOS', oos_metrics)

    if log_path:
        print(f"\n  📝 Auto-logged to: {os.path.relpath(log_path, PROJECT_ROOT)}  (git: {git_sha})")

    print("\n" + "=" * 76)
    print("  Pass criteria (industry convention, not absolute):")
    print("    Sharpe > 1.0    Sortino > 1.5    Calmar > 0.5    IR > 0.5    Profit factor > 1.5")
    print("    Most KOL-style sparse factors won't pass these standalone — that's expected.")
    print("    Use this as a portfolio-component evaluator, not a standalone strategy filter.")
    print("=" * 76)


if __name__ == '__main__':
    main()
