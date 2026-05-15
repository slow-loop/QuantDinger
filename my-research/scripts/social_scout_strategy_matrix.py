#!/usr/bin/env python3
"""
Run and summarize a broad social-scout strategy matrix.

This is a thin batch runner around strategy_evaluator.py. It keeps the existing
experiment_log.csv as the primary durable log, and writes a separate ranked
summary for the run so the research can be audited without rereading stdout.
"""

import argparse
import csv
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_STRATEGIES = [
    'my-research/strategies/tv_funding_extreme_long_4h.py',
    'my-research/strategies/funding_rate_bottom_fisher.py',
    'my-research/strategies/tv_liq_wick_sweep_eth_4h_long.py',
    'my-research/strategies/tv_vol_climax_bottom_eth_4h_long.py',
    'my-research/strategies/tv_sfp_reversal_eth_4h_long.py',
    'my-research/strategies/tv_funding_liq_wick_4h_long.py',
]


def parse_float(value):
    try:
        return float(value)
    except Exception:
        return float('nan')


def pass_count(row):
    return sum([
        parse_float(row['sharpe']) > 1.0,
        parse_float(row['sortino']) > 1.5,
        parse_float(row['calmar']) > 0.5,
        parse_float(row['information_ratio']) > 0.5,
        parse_float(row['profit_factor']) > 1.5,
    ])


def load_log_rows(log_path):
    with open(log_path, newline='') as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbols', required=True)
    parser.add_argument('--strategies', default=','.join(DEFAULT_STRATEGIES))
    parser.add_argument('--timeframe', default='4H')
    parser.add_argument('--is-days', type=int, default=2200)
    parser.add_argument('--oos-days', type=int, default=365)
    parser.add_argument('--slippage', type=float, default=0.0005)
    parser.add_argument('--commission', type=float, default=0.001)
    parser.add_argument('--log', default='my-research/log/experiment_log.csv')
    parser.add_argument('--out-prefix', default='my-research/log/results/social_scout_expanded_2026-05-15')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',') if s.strip()]
    strategies = [s.strip() for s in args.strategies.split(',') if s.strip()]
    started_at = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')

    log_path = PROJECT_ROOT / args.log
    before_count = len(load_log_rows(log_path)) if log_path.exists() else 0

    stdout_path = PROJECT_ROOT / f'{args.out_prefix}.log'
    stdout_path.parent.mkdir(parents=True, exist_ok=True)

    failures = []
    with stdout_path.open('w') as stdout:
        stdout.write(f'started_at={started_at}\n')
        stdout.write(f'symbols={symbols}\nstrategies={strategies}\n\n')
        for strategy in strategies:
            for symbol in symbols:
                header = f'===== {strategy} :: {symbol} =====\n'
                print(header.strip(), flush=True)
                stdout.write('\n' + header)
                cmd = [
                    sys.executable,
                    'my-research/scripts/strategy_evaluator.py',
                    strategy,
                    '--symbol', symbol,
                    '--timeframe', args.timeframe,
                    '--is-days', str(args.is_days),
                    '--oos-days', str(args.oos_days),
                    '--slippage', str(args.slippage),
                    '--commission', str(args.commission),
                    '--log', args.log,
                ]
                proc = subprocess.run(cmd, cwd=PROJECT_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout.write(proc.stdout)
                stdout.write(f'\nEXIT={proc.returncode}\n')
                if proc.returncode != 0:
                    failures.append({'strategy': strategy, 'symbol': symbol, 'exit': proc.returncode})

    rows = load_log_rows(log_path)
    new_rows = rows[before_count:]
    expected_rows = len(symbols) * len(strategies) * 2
    if len(new_rows) != expected_rows:
        print(f'WARN: expected {expected_rows} new log rows, got {len(new_rows)}')

    new_csv = PROJECT_ROOT / f'{args.out_prefix}_experiment_rows.csv'
    with new_csv.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(new_rows)

    oos = [r for r in new_rows if r['period'] == 'OOS']
    for row in oos:
        row['_pass_count'] = pass_count(row)
    ranked = sorted(oos, key=lambda r: (r['_pass_count'], parse_float(r['sharpe']), parse_float(r['profit_factor'])), reverse=True)

    summary_md = PROJECT_ROOT / f'{args.out_prefix}_summary.md'
    with summary_md.open('w') as f:
        f.write('# Expanded Social Scout Strategy Matrix — 2026-05-15\n\n')
        f.write(f'Started at UTC: `{started_at}`\n\n')
        f.write(f'Symbols tested: `{", ".join(symbols)}`\n\n')
        f.write(f'Strategies tested: `{", ".join(Path(s).name for s in strategies)}`\n\n')
        f.write(f'Failures: `{len(failures)}`\n\n')
        f.write('| Strategy | Symbol | OOS pass | Return | Sharpe | Sortino | Calmar | IR | PF | Win | N |\n')
        f.write('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n')
        for r in ranked:
            win = parse_float(r['win_rate'])
            n = parse_float(r['n_trades'])
            f.write(
                f"| {Path(r['strategy_file']).name} | {r['symbol']} | {r['_pass_count']}/5 | "
                f"{parse_float(r['total_return'])*100:+.2f}% | {parse_float(r['sharpe']):+.3f} | "
                f"{parse_float(r['sortino']):+.3f} | {parse_float(r['calmar']):+.3f} | "
                f"{parse_float(r['information_ratio']):+.3f} | {parse_float(r['profit_factor']):.3f} | "
                f"{win*100:.1f}% | {int(n) if not math.isnan(n) else 0} |\n"
            )

    print(f'Rows: {len(new_rows)}')
    print(f'CSV: {new_csv.relative_to(PROJECT_ROOT)}')
    print(f'Summary: {summary_md.relative_to(PROJECT_ROOT)}')
    print(f'Stdout log: {stdout_path.relative_to(PROJECT_ROOT)}')
    if failures:
        print('Failures:')
        for failure in failures:
            print(failure)


if __name__ == '__main__':
    main()
