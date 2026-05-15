#!/usr/bin/env python3
"""
Check which social-scout symbols are usable in QuantDinger's current data source.

The goal is not to define a permanent trading universe. It records which requested
small-cap / alt / narrative symbols have enough 4H history to run the existing
single-symbol evaluator today.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService


DEFAULT_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT',
    'AVAX/USDT', 'LINK/USDT', 'ARB/USDT', 'OP/USDT', 'DOGE/USDT',
    'XRP/USDT', 'BNB/USDT', 'ADA/USDT', 'DOT/USDT', 'ATOM/USDT',
    'NEAR/USDT', 'INJ/USDT', 'APT/USDT', 'SUI/USDT', 'SEI/USDT', 'TIA/USDT',
    'WLD/USDT', 'FET/USDT', 'RENDER/USDT', 'RNDR/USDT', 'TAO/USDT',
    'JUP/USDT', 'DYDX/USDT', 'GMX/USDT', 'UNI/USDT', 'AAVE/USDT', 'LDO/USDT',
    'PENDLE/USDT', 'ONDO/USDT', 'FIL/USDT', 'PEPE/USDT', 'SHIB/USDT',
    'WIF/USDT', 'FLOKI/USDT', 'BONK/USDT',
]


def latest_timestamp(df):
    if 'time' in df.columns:
        return pd.to_datetime(df['time']).max()
    return pd.to_datetime(df.index).max()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbols', default=','.join(DEFAULT_SYMBOLS))
    parser.add_argument('--timeframe', default='4H')
    parser.add_argument('--days', type=int, default=2600)
    parser.add_argument('--min-bars', type=int, default=1200)
    parser.add_argument('--out', default='my-research/log/results/social_scout_universe_2026-05-15.csv')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',') if s.strip()]
    end = datetime.now(timezone.utc).replace(tzinfo=None)
    start = end - timedelta(days=args.days)

    rows = []
    with app.app_context():
        svc = BacktestService()
        for sym in symbols:
            try:
                df = svc._fetch_kline_data('Crypto', sym, args.timeframe, start, end)
                if df is None or len(df) == 0:
                    raise RuntimeError('no rows')
                latest = latest_timestamp(df)
                rows.append({
                    'symbol': sym,
                    'status': 'ok' if len(df) >= args.min_bars else 'short',
                    'rows': len(df),
                    'earliest': str(pd.to_datetime(df['time']).min() if 'time' in df.columns else pd.to_datetime(df.index).min()),
                    'latest': str(latest),
                    'error': '',
                })
            except Exception as exc:
                rows.append({
                    'symbol': sym,
                    'status': 'error',
                    'rows': 0,
                    'earliest': '',
                    'latest': '',
                    'error': str(exc).replace('\n', ' ')[:300],
                })

    out_path = os.path.join(PROJECT_ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df_out = pd.DataFrame(rows)
    df_out.to_csv(out_path, index=False)
    print(f'CSV: {args.out}')
    print(df_out.to_string(index=False))


if __name__ == '__main__':
    main()
