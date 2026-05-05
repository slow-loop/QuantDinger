#!/usr/bin/env python3
"""
Factor IC Tester (Level 2: walk-forward IC analysis)
=====================================================

Evaluates a QuantDinger factor file's signal quality via Information Coefficient
(Spearman rank correlation between factor score and forward returns).

WHY THIS EXISTS:
    backtest_runner.py answers "does this strategy make money?" (Sharpe/MDD/alpha).
    This tool answers "does this factor's score predict future returns?" (IC).
    The two are independent — a factor with high IC may still lose money under bad
    risk control, and a profitable strategy may rely on a factor with weak IC.

WHAT IT DOES (Level 2):
    1. Executes a factor file in a controlled namespace, captures the score column(s) it adds to df.
    2. Computes Spearman IC vs forward returns at multiple horizons (1d/7d/30d).
    3. Splits IS / OOS using same convention as backtest_runner.py.
    4. Computes rolling IC (90-bar window) to detect regime breaks.
    5. Computes hit rate when |score| > threshold.
    6. Writes CSV alongside printing console summary.

USAGE:
    docker exec -w /app quantdinger-backend python3 my-research/scripts/factor_ic_tester.py \\
        my-research/factors/factor_200w_value_zone.py \\
        --symbol BTC/USDT --timeframe 1D --is-days 2200 --oos-days 365

LEVEL 3 — NOT YET IMPLEMENTED (future work, in priority order):
    [ ] Multiple-testing correction (Bonferroni / Benjamini-Hochberg FDR) when scoring
        many factors at once — the current IC tester reports raw p-values, which
        overstate significance under multiple comparisons. With ~12 factors and α=0.05
        you'd expect ~0.6 false positives by chance; with corrections this drops to <0.05.
    [ ] Factor correlation matrix — compute pairwise Spearman correlation across factor
        score columns, identify clusters of redundant factors. Critical before ensemble
        weighting; weighting two correlated factors equally double-counts the same alpha.
    [ ] Bootstrap confidence intervals for IC — resample (with replacement) factor/return
        pairs N=1000 times, report 5th/95th percentile of IC distribution. Tells you
        whether IC=+0.18 is "definitely positive" or "+0.18 ± 0.20".
    [ ] Plot output (PNG/HTML) — IC time series, IC heatmap by horizon, quantile portfolio
        equity curves. Currently text-only.
    [ ] Multi-symbol panel — compute IC across BTC + ETH + SOL pooled, more samples
        and a check whether the factor generalizes beyond BTC.
    [ ] IC decay curve — compute IC at horizons 1, 2, 3, ..., 60 days, plot decay rate.
        Tells you the natural holding period for the factor.
    [ ] Quantile portfolio analysis — sort bars into quintiles by score, compute mean
        forward return per quintile. Linear monotonic = clean factor; flat/U-shaped = noisy.
    [ ] Walk-forward weight optimization — instead of one IS/OOS split, slide a rolling
        window: at each rebalance, fit weights on past N days, measure on next M days.
        Eliminates the single-split lottery effect.
    [ ] Regime-conditional IC — partition bars by regime (trending/ranging/high-vol)
        and compute IC per regime. Reveals factors that only work in specific regimes.
    [ ] Transaction cost simulation — apply realistic slippage/commission to the
        quantile portfolio returns to see what survives net of costs.
"""

import os
import sys
import argparse
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def spearmanr(x, y):
    """Spearman rank correlation + two-sided p-value.

    scipy-free implementation. p-value uses normal approximation to the
    t-distribution (accurate for n ≥ 30; this tool requires min_n=30 anyway).
    Returns (correlation, p_value).
    """
    sx = pd.Series(x).reset_index(drop=True)
    sy = pd.Series(y).reset_index(drop=True)
    n = len(sx)
    if n < 3:
        return float('nan'), float('nan')
    rx = sx.rank()
    ry = sy.rank()
    r = float(rx.corr(ry))
    if math.isnan(r) or abs(r) >= 1.0:
        return r, 0.0
    t = r * math.sqrt((n - 2) / (1 - r * r))
    p = math.erfc(abs(t) / math.sqrt(2))
    return r, p

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService


# ----------------------------------------------------------------------------
# Factor execution
# ----------------------------------------------------------------------------

def execute_factor(factor_path, df, params=None):
    """Execute a factor file in a controlled namespace.

    Returns the df with new columns added by the factor, plus a list of new
    numeric column names (the factor's score outputs).
    """
    params = params or {}
    df_input = df.copy()
    cols_before = set(df_input.columns)

    with open(factor_path, 'r', encoding='utf-8') as f:
        code = f.read()

    namespace = {
        'df': df_input,
        'params': params,
        'pd': pd,
        'np': np,
    }
    exec(code, namespace)
    df_out = namespace['df']

    new_cols = [c for c in df_out.columns if c not in cols_before]
    new_numeric = [c for c in new_cols if pd.api.types.is_numeric_dtype(df_out[c])]
    return df_out, new_numeric


# ----------------------------------------------------------------------------
# IC computation
# ----------------------------------------------------------------------------

def compute_ic(score, fwd_ret, min_n=30):
    """Spearman rank IC between factor score and forward returns."""
    valid = score.notna() & fwd_ret.notna()
    if valid.sum() < min_n:
        return None
    if score[valid].nunique() < 2:
        return None
    ic, pval = spearmanr(score[valid], fwd_ret[valid])
    return {'ic': float(ic), 'pval': float(pval), 'n': int(valid.sum())}


def compute_hit_rate(score, fwd_ret, threshold=0.1):
    """When |score| > threshold, what fraction of forward returns were directionally correct?"""
    long_mask = (score > threshold) & fwd_ret.notna()
    short_mask = (score < -threshold) & fwd_ret.notna()
    n_long = int(long_mask.sum())
    n_short = int(short_mask.sum())
    hit_long = float((fwd_ret[long_mask] > 0).mean()) if n_long > 0 else None
    hit_short = float((fwd_ret[short_mask] < 0).mean()) if n_short > 0 else None
    avg_long = float(fwd_ret[long_mask].mean()) if n_long > 0 else None
    avg_short = float(fwd_ret[short_mask].mean()) if n_short > 0 else None
    return {
        'n_long': n_long, 'n_short': n_short,
        'hit_long': hit_long, 'hit_short': hit_short,
        'avg_ret_long': avg_long, 'avg_ret_short': avg_short,
    }


# 4-year cycle phase boundaries — mirror capabilities/cycle.py logic from crypto-kol-quant.
# Phases derived from days-since-last-halving; bull/bear behavior of these phases is itself
# the subject of cap_037/cap_038, so this binning IS our regime hypothesis under test.
HALVINGS = [
    pd.Timestamp('2012-11-28'),
    pd.Timestamp('2016-07-09'),
    pd.Timestamp('2020-05-11'),
    pd.Timestamp('2024-04-19'),
]
PHASE_ORDER = ['accumulation', 'parabolic', 'distribution', 'bear', 'late_bear']


def cycle_phase(date):
    """Return phase label based on days since the most recent BTC halving."""
    last = None
    for h in HALVINGS:
        if h <= date:
            last = h
    if last is None:
        return 'pre_halving'
    days = (date - last).days
    if days < 180:
        return 'accumulation'
    elif days < 540:
        return 'parabolic'
    elif days < 720:
        return 'distribution'
    elif days < 1080:
        return 'bear'
    else:
        return 'late_bear'


def regime_conditional_ic(score, fwd_ret, dates, min_n=20):
    """Compute Spearman IC separately for each 4-year cycle phase.

    Returns a dict of {phase_label: {'ic', 'pval', 'n'}}. A factor that's
    universally weak but appears strong only because it fires during a single
    favorable phase will reveal that here.
    """
    phases = pd.Series([cycle_phase(d) for d in dates], index=dates)
    out = {}
    for phase in PHASE_ORDER:
        mask = (phases == phase)
        if mask.sum() < min_n:
            continue
        s = score[mask]
        f = fwd_ret[mask]
        valid = s.notna() & f.notna()
        if valid.sum() < min_n or s[valid].nunique() < 2:
            continue
        ic, pval = spearmanr(s[valid], f[valid])
        out[phase] = {'ic': float(ic), 'pval': float(pval), 'n': int(valid.sum())}
    return out


def rolling_ic(score, fwd_ret, window=90, min_n=30):
    """Rolling IC over a sliding window. Returns a Series of IC values."""
    paired = pd.DataFrame({'s': score, 'r': fwd_ret}).dropna()
    if len(paired) < window:
        return pd.Series(dtype=float)
    out = []
    idx = []
    for i in range(window, len(paired) + 1):
        chunk = paired.iloc[i - window:i]
        if chunk['s'].nunique() < 2:
            out.append(np.nan)
        else:
            ic, _ = spearmanr(chunk['s'], chunk['r'])
            out.append(ic)
        idx.append(paired.index[i - 1])
    return pd.Series(out, index=idx)


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------

def fetch_data(symbol, timeframe, total_days):
    """Fetch enough OHLCV history to cover IS + OOS + factor warmup."""
    svc = BacktestService()
    end = datetime.utcnow()
    # Add 200-week warmup buffer for long-MA factors (1400 daily bars).
    start = end - timedelta(days=total_days + 1400)
    df = svc._fetch_kline_data('Crypto', symbol, timeframe, start, end)
    if df is None or len(df) == 0:
        raise RuntimeError(f'No data fetched for {symbol} {timeframe}')
    return df


def analyze_factor(factor_path, args):
    df = fetch_data(args.symbol, args.timeframe, args.is_days + args.oos_days)
    print(f"Data: {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

    df_with_score, score_cols = execute_factor(factor_path, df)
    if not score_cols:
        raise RuntimeError(f'Factor produced no new numeric columns. Check the factor file.')
    print(f"Score columns detected: {score_cols}")

    horizons = [int(h) for h in args.horizons.split(',')]

    # IS/OOS boundaries (mirror backtest_runner.py)
    now = df_with_score.index[-1]
    oos_start = now - pd.Timedelta(days=args.oos_days)
    is_start = oos_start - pd.Timedelta(days=args.is_days)

    is_mask = (df_with_score.index >= is_start) & (df_with_score.index < oos_start)
    oos_mask = (df_with_score.index >= oos_start) & (df_with_score.index <= now)

    print(f"\nIS:    {is_start.date()} → {oos_start.date()}  ({int(is_mask.sum())} bars)")
    print(f"OOS:   {oos_start.date()} → {now.date()}  ({int(oos_mask.sum())} bars)")

    rows = []
    for col in score_cols:
        score = df_with_score[col]
        for h in horizons:
            fwd = df_with_score['close'].pct_change(h).shift(-h)
            row = {'score_col': col, 'horizon_d': h}
            for label, mask in [('full', slice(None)), ('IS', is_mask), ('OOS', oos_mask)]:
                ic_res = compute_ic(score[mask], fwd[mask])
                if ic_res:
                    row[f'ic_{label}'] = ic_res['ic']
                    row[f'pval_{label}'] = ic_res['pval']
                    row[f'n_{label}'] = ic_res['n']
                else:
                    row[f'ic_{label}'] = np.nan
                    row[f'pval_{label}'] = np.nan
                    row[f'n_{label}'] = 0
            hit = compute_hit_rate(score[is_mask], fwd[is_mask])
            row.update({f'IS_{k}': v for k, v in hit.items()})
            rows.append(row)

    return pd.DataFrame(rows), df_with_score, score_cols


def print_report(df_results, df_data, score_cols, args):
    print("\n" + "=" * 72)
    print(f"🧪 FACTOR IC ANALYSIS")
    print(f"Factor:    {args.factor_file}")
    print(f"Symbol:    {args.symbol}   Timeframe: {args.timeframe}")
    print("=" * 72)

    for col in score_cols:
        sub = df_results[df_results['score_col'] == col]
        print(f"\n📊 Score column: {col}")
        print(f"{'Horizon':>8} {'IC_full':>10} {'IC_IS':>10} {'IC_OOS':>10} {'p_OOS':>10} {'n_OOS':>8}  decay")
        print("-" * 72)
        for _, r in sub.iterrows():
            decay = ''
            if not pd.isna(r['ic_IS']) and not pd.isna(r['ic_OOS']) and abs(r['ic_IS']) > 0.01:
                ratio = r['ic_OOS'] / r['ic_IS']
                if ratio > 0.7:
                    decay = '✅ stable'
                elif ratio > 0.3:
                    decay = '⚠️  decayed'
                elif ratio > -0.3:
                    decay = '❌ ~zero'
                else:
                    decay = '🔄 reversed'
            print(f"{int(r['horizon_d']):>7}d {r['ic_full']:>+10.4f} {r['ic_IS']:>+10.4f} {r['ic_OOS']:>+10.4f} {r['pval_OOS']:>10.4f} {int(r['n_OOS']):>8}  {decay}")

        # IS hit rate detail (use 30d horizon row)
        h30 = sub[sub['horizon_d'] == 30].iloc[0] if (sub['horizon_d'] == 30).any() else sub.iloc[0]
        print(f"\n  IS hit-rate (|score|>0.1, horizon={int(h30['horizon_d'])}d):")
        if h30.get('IS_n_long', 0):
            print(f"    long signals:  {int(h30['IS_n_long']):>5}  hit={h30['IS_hit_long']:.1%}  avg_fwd={h30['IS_avg_ret_long']:+.2%}")
        else:
            print(f"    long signals:  none")
        if h30.get('IS_n_short', 0):
            print(f"    short signals: {int(h30['IS_n_short']):>5}  hit={h30['IS_hit_short']:.1%}  avg_fwd={h30['IS_avg_ret_short']:+.2%}")
        else:
            print(f"    short signals: none")

        # Rolling IC (30d horizon, default window)
        score = df_data[col]
        fwd_30d = df_data['close'].pct_change(30).shift(-30)
        roll = rolling_ic(score, fwd_30d, window=args.rolling_window)
        if len(roll.dropna()) > 0:
            valid = roll.dropna()
            print(f"\n  Rolling IC (window={args.rolling_window} bars, horizon=30d, n_windows={len(valid)}):")
            print(f"    mean: {valid.mean():+.4f}   std: {valid.std():.4f}")
            print(f"    min:  {valid.min():+.4f}   max: {valid.max():+.4f}")
            print(f"    %positive: {(valid > 0).mean():.1%}    %|IC|>0.1: {(valid.abs() > 0.1).mean():.1%}")

        # Regime-conditional IC (4-year cycle phase, 30d horizon)
        regime_ic = regime_conditional_ic(score, fwd_30d, df_data.index)
        if regime_ic:
            print(f"\n  Regime-conditional IC (4-year cycle phase, horizon=30d):")
            print(f"    {'Phase':<14} {'IC':>10} {'p-value':>10} {'n_bars':>8}  flag")
            print(f"    " + "-" * 60)
            for phase in PHASE_ORDER:
                if phase not in regime_ic:
                    continue
                r = regime_ic[phase]
                flag = ''
                if r['pval'] < 0.05:
                    if r['ic'] > 0.1:
                        flag = '⭐ strong+ (significant)'
                    elif r['ic'] > 0:
                        flag = '✓ weak+ (significant)'
                    elif r['ic'] < -0.1:
                        flag = '🔄 strong- (reversed, significant)'
                    else:
                        flag = '🔄 weak- (reversed, significant)'
                else:
                    flag = '· not significant'
                print(f"    {phase:<14} {r['ic']:>+10.4f} {r['pval']:>10.4f} {r['n']:>8}  {flag}")


def write_csv(df_results, factor_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(factor_path))[0]
    out_path = os.path.join(out_dir, f'ic_{base}.csv')
    df_results.to_csv(out_path, index=False)
    print(f"\n💾 CSV: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Factor IC Tester (Level 2)")
    parser.add_argument("factor_file", help="Path to factor file relative to project root")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1D")
    parser.add_argument("--is-days", type=int, default=2200, help="In-sample window (default 6yr to fit 200W MA + signal)")
    parser.add_argument("--oos-days", type=int, default=365)
    parser.add_argument("--horizons", default="1,7,30", help="Comma-separated forward-return horizons in bars")
    parser.add_argument("--rolling-window", type=int, default=90, help="Rolling IC window in bars")
    parser.add_argument("--out-dir", default="my-research/log/results/ic")
    args = parser.parse_args()

    factor_path = os.path.join(PROJECT_ROOT, args.factor_file)
    if not os.path.exists(factor_path):
        print(f"❌ Factor file not found: {factor_path}")
        sys.exit(1)

    with app.app_context():
        df_results, df_data, score_cols = analyze_factor(factor_path, args)
        print_report(df_results, df_data, score_cols, args)
        write_csv(df_results, factor_path, os.path.join(PROJECT_ROOT, args.out_dir))


if __name__ == '__main__':
    main()
