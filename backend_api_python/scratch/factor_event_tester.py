#!/usr/bin/env python3
"""
Factor Event Tester
=====================
Evaluates a factor as a series of discrete trigger events, NOT as a continuous predictor.

WHY THIS EXISTS:
    The IC framework (factor_ic_tester.py) measures Spearman correlation between
    factor score and forward returns across ALL bars. For sparse / discrete event
    factors (e.g., emg_028 fires 45 times in 6 years), most bars have score=0 and
    end up as tied ranks. This crushes IC even when the few non-zero events are
    highly predictive.

    Event Tester instead asks: "When this factor FIRES, what happens next?"
    It treats each trigger as an independent trade event and reports per-trade
    statistics — the right framework for KOL-style discrete decisions.

WHAT IT REPORTS (per direction × per horizon × IS/OOS split):
    - N triggers (event count)
    - Hit rate (% of triggers where direction was correct)
    - Avg forward return per trigger
    - Std of forward returns per trigger
    - Per-trade Sharpe = mean/std (NOT annualized — see notes)

USAGE:
    docker exec -w /app quantdinger-backend python3 scratch/factor_event_tester.py \\
        research/examples/factors/factor_200w_value_zone.py \\
        --symbol BTC/USDT --timeframe 1D --is-days 2200 --oos-days 365 \\
        --threshold 0.1

NOTES ON SHARPE:
    Per-trade Sharpe (mean/std of trigger-conditional fwd returns) is NOT annualized.
    To convert to annualized strategy Sharpe you'd need:
        - trigger frequency (events / year)
        - whether positions overlap (they often do for 30d horizon + frequent triggers)
        - capital allocation per trigger
    These depend on strategy construction; we report the cleaner per-trade metric and
    let downstream strategy code annualize. A per-trade Sharpe > 0.5 is considered
    strong; > 1.0 is exceptional.

LEVEL 3 EXTENSIONS (future work):
    [ ] Equity curve simulation: actually open positions on each trigger, hold N days,
        track equity. Handles overlapping positions correctly.
    [ ] Trigger clustering: detect when multiple triggers cluster in time (regime),
        deduplicate or weight down redundant signals.
    [ ] Bootstrap CIs on hit rate and avg return — small N (e.g., 39 triggers for
        emg_007) makes point estimates very uncertain.
    [ ] Combine with regime-conditional analysis (see ic_tester.py for cycle-phase split)
        to identify which regime each event factor works in.
    [ ] Trade-level transaction cost: subtract slippage + commission from each event's
        fwd return to see net edge.
    [ ] Compare with bar-shuffle null distribution: shuffle factor scores 1000x,
        compute hit rate distribution, see if observed hit rate is in top 5%.
"""

import os
import sys
import argparse
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService


def execute_factor(factor_path, df, params=None):
    """Execute a factor file in a controlled namespace, return df + new score columns."""
    params = params or {}
    df_input = df.copy()
    cols_before = set(df_input.columns)
    with open(factor_path, 'r', encoding='utf-8') as f:
        code = f.read()
    namespace = {'df': df_input, 'params': params, 'pd': pd, 'np': np}
    exec(code, namespace)
    df_out = namespace['df']
    new_cols = [c for c in df_out.columns if c not in cols_before]
    new_numeric = [c for c in new_cols if pd.api.types.is_numeric_dtype(df_out[c])]
    return df_out, new_numeric


def fetch_data(symbol, timeframe, total_days):
    svc = BacktestService()
    end = datetime.utcnow()
    start = end - timedelta(days=total_days + 1400)  # 1400d warmup for 200W MA
    df = svc._fetch_kline_data('Crypto', symbol, timeframe, start, end)
    if df is None or len(df) == 0:
        raise RuntimeError(f'No data fetched for {symbol} {timeframe}')
    return df


def event_stats(score, fwd_ret, mask, threshold, direction):
    """Compute event statistics for one direction.

    direction='long': triggers when score > +threshold, expects fwd_ret > 0
    direction='short': triggers when score < -threshold, expects fwd_ret < 0
    """
    if direction == 'long':
        trig = (score > threshold) & mask & fwd_ret.notna()
        sign = 1
    else:
        trig = (score < -threshold) & mask & fwd_ret.notna()
        sign = -1

    n = int(trig.sum())
    if n == 0:
        return {'n': 0, 'hit_rate': None, 'avg_ret': None, 'std_ret': None,
                'sharpe': None, 'directional_avg': None}

    rets = fwd_ret[trig]
    hit_rate = float((rets * sign > 0).mean())
    avg_ret = float(rets.mean())
    std_ret = float(rets.std())
    # Sharpe: positive when direction matches expected return sign
    directional_avg = float((rets * sign).mean())  # sign-corrected mean
    directional_std = float((rets * sign).std())
    sharpe = directional_avg / directional_std if directional_std > 0 else None

    return {
        'n': n, 'hit_rate': hit_rate, 'avg_ret': avg_ret, 'std_ret': std_ret,
        'sharpe': sharpe, 'directional_avg': directional_avg,
    }


def analyze_factor(factor_path, args):
    df = fetch_data(args.symbol, args.timeframe, args.is_days + args.oos_days)
    print(f"Data: {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

    df_with_score, score_cols = execute_factor(factor_path, df)
    if not score_cols:
        raise RuntimeError('Factor produced no new numeric columns.')
    print(f"Score columns detected: {score_cols}")

    horizons = [int(h) for h in args.horizons.split(',')]
    threshold = args.threshold

    now = df_with_score.index[-1]
    oos_start = now - pd.Timedelta(days=args.oos_days)
    is_start = oos_start - pd.Timedelta(days=args.is_days)

    is_mask = (df_with_score.index >= is_start) & (df_with_score.index < oos_start)
    oos_mask = (df_with_score.index >= oos_start) & (df_with_score.index <= now)
    full_mask = pd.Series(True, index=df_with_score.index)

    print(f"\nIS:    {is_start.date()} → {oos_start.date()}  ({int(is_mask.sum())} bars)")
    print(f"OOS:   {oos_start.date()} → {now.date()}  ({int(oos_mask.sum())} bars)")
    print(f"Trigger threshold: |score| > {threshold}")

    rows = []
    for col in score_cols:
        score = df_with_score[col]
        for h in horizons:
            fwd = df_with_score['close'].pct_change(h).shift(-h)
            for label, mask in [('IS', is_mask), ('OOS', oos_mask), ('full', full_mask)]:
                mask_series = pd.Series(mask, index=df_with_score.index) if not isinstance(mask, pd.Series) else mask
                for direction in ['long', 'short']:
                    stats = event_stats(score, fwd, mask_series, threshold, direction)
                    rows.append({
                        'score_col': col, 'horizon_d': h, 'period': label,
                        'direction': direction, **stats,
                    })

    return pd.DataFrame(rows), df_with_score, score_cols


def print_report(df_results, score_cols, args):
    print("\n" + "=" * 80)
    print(f"🎯 EVENT-BASED FACTOR ANALYSIS")
    print(f"Factor:    {args.factor_file}")
    print(f"Symbol:    {args.symbol}   Timeframe: {args.timeframe}")
    print(f"Threshold: |score| > {args.threshold}")
    print("=" * 80)

    horizons = sorted(df_results['horizon_d'].unique())

    for col in score_cols:
        sub = df_results[df_results['score_col'] == col]
        print(f"\n📊 Score column: {col}")

        for direction in ['long', 'short']:
            dir_data = sub[sub['direction'] == direction]
            # Skip if direction never fires anywhere
            if (dir_data['n'].sum() == 0):
                continue

            print(f"\n  [{direction.upper()} triggers]")
            print(f"  {'Period':<8} {'Horizon':>8} {'N':>6} {'HitRate':>10} {'AvgRet':>10} {'StdRet':>10} {'Sharpe':>10}")
            print(f"  {'-'*72}")
            for period in ['IS', 'OOS', 'full']:
                for h in horizons:
                    row = dir_data[(dir_data['period'] == period) & (dir_data['horizon_d'] == h)]
                    if len(row) == 0:
                        continue
                    r = row.iloc[0]
                    if r['n'] == 0:
                        print(f"  {period:<8} {int(h):>7}d {0:>6}  {'-':>9} {'-':>9} {'-':>9} {'-':>9}")
                    else:
                        hit_str = f"{r['hit_rate']:.1%}" if r['hit_rate'] is not None else '-'
                        avg_str = f"{r['avg_ret']:+.2%}" if r['avg_ret'] is not None else '-'
                        std_str = f"{r['std_ret']:.2%}" if r['std_ret'] is not None else '-'
                        sharpe_str = f"{r['sharpe']:+.3f}" if r['sharpe'] is not None else '-'
                        print(f"  {period:<8} {int(h):>7}d {int(r['n']):>6} {hit_str:>10} {avg_str:>10} {std_str:>10} {sharpe_str:>10}")

        # Verdict per direction at 30d horizon
        print(f"\n  📋 Verdict (30d horizon, IS vs OOS):")
        for direction in ['long', 'short']:
            is_row = sub[(sub['direction']==direction) & (sub['period']=='IS') & (sub['horizon_d']==30)]
            oos_row = sub[(sub['direction']==direction) & (sub['period']=='OOS') & (sub['horizon_d']==30)]
            if len(is_row) == 0 or is_row.iloc[0]['n'] == 0:
                continue
            is_r = is_row.iloc[0]
            oos_r = oos_row.iloc[0] if len(oos_row) > 0 else None

            verdict = ''
            if oos_r is None or oos_r['n'] == 0:
                verdict = '⚠️  no OOS triggers (sparse factor in current regime)'
            elif oos_r['hit_rate'] is not None and is_r['hit_rate'] is not None:
                if oos_r['hit_rate'] >= 0.55 and is_r['hit_rate'] >= 0.55:
                    verdict = '✅ stable (hit rate maintained)'
                elif oos_r['hit_rate'] < 0.45:
                    verdict = '🔄 reversed (hit rate flipped to < 45%)'
                elif oos_r['hit_rate'] < 0.50:
                    verdict = '⚠️  decayed (hit rate dropped below 50%)'
                else:
                    verdict = '✅ stable-ish'
            print(f"    {direction:<6} IS hit={is_r['hit_rate']:.1%} (n={int(is_r['n'])}) → "
                  f"OOS hit={'-' if oos_r is None or oos_r['n']==0 else f'{oos_r['hit_rate']:.1%}'} "
                  f"({0 if oos_r is None else int(oos_r['n'])})   {verdict}")


def write_csv(df_results, factor_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(factor_path))[0]
    out_path = os.path.join(out_dir, f'event_{base}.csv')
    df_results.to_csv(out_path, index=False)
    print(f"\n💾 CSV: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Factor Event Tester")
    parser.add_argument("factor_file")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1D")
    parser.add_argument("--is-days", type=int, default=2200)
    parser.add_argument("--oos-days", type=int, default=365)
    parser.add_argument("--horizons", default="1,7,30")
    parser.add_argument("--threshold", type=float, default=0.1, help="Trigger threshold; |score|>threshold counts as event")
    parser.add_argument("--out-dir", default="research/event_results")
    args = parser.parse_args()

    factor_path = os.path.join(PROJECT_ROOT, args.factor_file)
    if not os.path.exists(factor_path):
        print(f"❌ Factor file not found: {factor_path}")
        sys.exit(1)

    with app.app_context():
        df_results, df_data, score_cols = analyze_factor(factor_path, args)
        print_report(df_results, score_cols, args)
        write_csv(df_results, factor_path, os.path.join(PROJECT_ROOT, args.out_dir))


if __name__ == '__main__':
    main()
