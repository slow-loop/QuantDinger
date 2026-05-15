#!/usr/bin/env python3
"""
Summarize expanded social-scout matrix by sector / narrative bucket.

This does not create new backtest results. It groups the already logged strategy
matrix so we can see whether the edge is isolated to a few hand-picked symbols
or appears across narrative buckets.
"""

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


SECTOR = {
    'SOL/USDT': 'L1/high-beta', 'AVAX/USDT': 'L1/high-beta', 'NEAR/USDT': 'L1/high-beta',
    'APT/USDT': 'L1/high-beta', 'SUI/USDT': 'L1/high-beta', 'SEI/USDT': 'L1/high-beta',
    'TIA/USDT': 'L1/high-beta', 'INJ/USDT': 'L1/high-beta', 'ATOM/USDT': 'L1/high-beta',
    'ARB/USDT': 'L2', 'OP/USDT': 'L2',
    'DOGE/USDT': 'meme', 'PEPE/USDT': 'meme', 'SHIB/USDT': 'meme', 'WIF/USDT': 'meme',
    'FLOKI/USDT': 'meme', 'BONK/USDT': 'meme',
    'FET/USDT': 'AI', 'RENDER/USDT': 'AI', 'TAO/USDT': 'AI', 'WLD/USDT': 'AI',
    'JUP/USDT': 'perp-dex/defi', 'DYDX/USDT': 'perp-dex/defi', 'GMX/USDT': 'perp-dex/defi',
    'UNI/USDT': 'perp-dex/defi', 'AAVE/USDT': 'perp-dex/defi', 'LDO/USDT': 'perp-dex/defi',
    'PENDLE/USDT': 'perp-dex/defi',
    'ONDO/USDT': 'RWA', 'LINK/USDT': 'infra/oracle', 'FIL/USDT': 'infra/oracle',
    'XRP/USDT': 'large-cap', 'BNB/USDT': 'large-cap', 'ADA/USDT': 'large-cap', 'DOT/USDT': 'large-cap',
}


def f(value):
    try:
        return float(value)
    except Exception:
        return float('nan')


def pass_count(row):
    return sum([
        f(row['sharpe']) > 1.0,
        f(row['sortino']) > 1.5,
        f(row['calmar']) > 0.5,
        f(row['information_ratio']) > 0.5,
        f(row['profit_factor']) > 1.5,
    ])


def fmt(value):
    if math.isnan(value):
        return '-'
    return f'{value:.3f}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrix', default='my-research/log/results/social_scout_expanded_2026-05-15_experiment_rows.csv')
    parser.add_argument('--out', default='my-research/log/results/social_scout_sector_summary_2026-05-15.md')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = [r for r in csv.DictReader((root / args.matrix).open()) if r['period'] == 'OOS']
    for r in rows:
        r['pass_count'] = pass_count(r)
        r['sector'] = SECTOR.get(r['symbol'], 'other')

    by_sector = defaultdict(list)
    by_strategy = defaultdict(list)
    by_pair = []
    for r in rows:
        by_sector[r['sector']].append(r)
        by_strategy[Path(r['strategy_file']).name].append(r)
        if r['pass_count'] >= 5:
            by_pair.append(r)

    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w') as fp:
        fp.write('# Social Scout Sector Summary — 2026-05-15\n\n')
        fp.write('Based on expanded OOS matrix only.\n\n')
        fp.write('## Sector Coverage\n\n')
        fp.write('| Sector | Symbols | Tests | 5/5 | 4/5+ | Median Sharpe | Median PF |\n')
        fp.write('|---|---:|---:|---:|---:|---:|---:|\n')
        for sector, sector_rows in sorted(by_sector.items()):
            symbols = len({r['symbol'] for r in sector_rows})
            sharpes = sorted(f(r['sharpe']) for r in sector_rows if not math.isnan(f(r['sharpe'])))
            pfs = sorted(f(r['profit_factor']) for r in sector_rows if not math.isnan(f(r['profit_factor'])))
            median_sharpe = sharpes[len(sharpes)//2] if sharpes else float('nan')
            median_pf = pfs[len(pfs)//2] if pfs else float('nan')
            fp.write(f"| {sector} | {symbols} | {len(sector_rows)} | {sum(r['pass_count']==5 for r in sector_rows)} | {sum(r['pass_count']>=4 for r in sector_rows)} | {fmt(median_sharpe)} | {fmt(median_pf)} |\n")

        fp.write('\n## Strategy Breadth\n\n')
        fp.write('| Strategy | 5/5 | 4/5+ | Symbols 4/5+ |\n')
        fp.write('|---|---:|---:|---|\n')
        for strategy, strategy_rows in sorted(by_strategy.items()):
            good = [r['symbol'] for r in strategy_rows if r['pass_count'] >= 4]
            fp.write(f"| {strategy} | {sum(r['pass_count']==5 for r in strategy_rows)} | {len(good)} | {', '.join(good)} |\n")

        fp.write('\n## 5/5 OOS Pairs\n\n')
        fp.write('| Strategy | Symbol | Sector | Return | Sharpe | PF | N |\n')
        fp.write('|---|---|---|---:|---:|---:|---:|\n')
        for r in sorted(by_pair, key=lambda x: (f(x['sharpe']), f(x['profit_factor'])), reverse=True):
            fp.write(f"| {Path(r['strategy_file']).name} | {r['symbol']} | {r['sector']} | {f(r['total_return'])*100:+.2f}% | {f(r['sharpe']):+.3f} | {f(r['profit_factor']):.3f} | {int(f(r['n_trades'])) if not math.isnan(f(r['n_trades'])) else 0} |\n")

    print(f'MD: {args.out}')


if __name__ == '__main__':
    main()
