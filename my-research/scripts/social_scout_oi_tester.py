#!/usr/bin/env python3
"""
Recent OI surge + price compression tester.

Binance only exposes a limited recent futures OI history through the public
endpoint, so this is a recent-window event study, not a full IS/OOS strategy
evaluation. It covers the social-scout idea:

    OI surge + price compression -> breakout / breakdown follow-through
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService


def binance_symbol(symbol):
    return symbol.replace('/', '')


def fetch_oi(symbol, period='4h', limit=500):
    url = 'https://fapi.binance.com/futures/data/openInterestHist'
    r = requests.get(url, params={'symbol': binance_symbol(symbol), 'period': period, 'limit': limit}, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise RuntimeError('empty OI response')
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
    df['time'] = df['time'].astype('datetime64[ns]')
    df['oi_value'] = df['sumOpenInterestValue'].astype(float)
    return df[['time', 'oi_value']].sort_values('time')


def fetch_price(symbol, timeframe, days):
    svc = BacktestService()
    end = datetime.now(timezone.utc).replace(tzinfo=None)
    start = end - timedelta(days=days)
    df = svc._fetch_kline_data('Crypto', symbol, timeframe, start, end)
    if df is None or len(df) == 0:
        raise RuntimeError('empty price response')
    df = df.copy()
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
    else:
        df['time'] = pd.to_datetime(df.index)
    df['time'] = df['time'].astype('datetime64[ns]')
    df = df.reset_index(drop=True)
    return df[['time', 'open', 'high', 'low', 'close', 'volume']].sort_values('time')


def zscore(s, lookback):
    mean = s.rolling(lookback).mean()
    std = s.rolling(lookback).std().replace(0, np.nan)
    return ((s - mean) / std).fillna(0)


def event_rows(symbol, args):
    price = fetch_price(symbol, args.timeframe, args.days)
    oi = fetch_oi(symbol, period=args.oi_period, limit=args.oi_limit)
    df = pd.merge_asof(price.sort_values('time'), oi.sort_values('time'), on='time', direction='nearest', tolerance=pd.Timedelta(args.timeframe.lower()))
    df = df.dropna(subset=['oi_value']).reset_index(drop=True)
    if len(df) < args.min_rows:
        raise RuntimeError(f'insufficient merged rows: {len(df)}')

    oi_ret = df['oi_value'].pct_change(args.oi_change_bars)
    oi_z = zscore(oi_ret, args.oi_z_lookback)

    range_ratio = (df['high'].rolling(args.range_bars).max() - df['low'].rolling(args.range_bars).min()) / df['close']
    compression_threshold = range_ratio.rolling(args.compression_rank_lookback).quantile(args.compression_quantile)
    compressed = range_ratio <= compression_threshold
    oi_surge = oi_z >= args.oi_z_threshold
    setup = (oi_surge & compressed).rolling(args.setup_lookback).max().fillna(0).astype(bool)

    prior_high = df['close'].shift(1).rolling(args.breakout_bars).max()
    prior_low = df['close'].shift(1).rolling(args.breakout_bars).min()
    long_trigger = setup & (df['close'] > prior_high)
    short_trigger = setup & (df['close'] < prior_low)

    rows = []
    for direction, trigger, sign in [('long', long_trigger, 1), ('short', short_trigger, -1)]:
        for h in args.horizons:
            fwd = df['close'].pct_change(h).shift(-h)
            rets = fwd[trigger & fwd.notna()]
            directional = rets * sign
            n = int(len(rets))
            rows.append({
                'symbol': symbol,
                'direction': direction,
                'horizon_bars': h,
                'n': n,
                'hit_rate': float((directional > 0).mean()) if n else np.nan,
                'avg_ret': float(rets.mean()) if n else np.nan,
                'directional_avg': float(directional.mean()) if n else np.nan,
                'sharpe': float(directional.mean() / directional.std()) if n and directional.std() > 0 else np.nan,
                'rows': len(df),
                'first': str(df['time'].iloc[0]),
                'last': str(df['time'].iloc[-1]),
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbols', required=True)
    parser.add_argument('--timeframe', default='4H')
    parser.add_argument('--days', type=int, default=260)
    parser.add_argument('--oi-period', default='4h')
    parser.add_argument('--oi-limit', type=int, default=500)
    parser.add_argument('--min-rows', type=int, default=150)
    parser.add_argument('--oi-change-bars', type=int, default=3)
    parser.add_argument('--oi-z-lookback', type=int, default=60)
    parser.add_argument('--oi-z-threshold', type=float, default=1.5)
    parser.add_argument('--range-bars', type=int, default=20)
    parser.add_argument('--compression-rank-lookback', type=int, default=120)
    parser.add_argument('--compression-quantile', type=float, default=0.35)
    parser.add_argument('--setup-lookback', type=int, default=6)
    parser.add_argument('--breakout-bars', type=int, default=20)
    parser.add_argument('--horizons', type=lambda s: [int(x) for x in s.split(',')], default='6,18,42')
    parser.add_argument('--out', default='my-research/log/results/social_scout_oi_2026-05-15.csv')
    args = parser.parse_args()

    rows = []
    errors = []
    with app.app_context():
        for symbol in [s.strip() for s in args.symbols.split(',') if s.strip()]:
            try:
                rows.extend(event_rows(symbol, args))
            except Exception as exc:
                errors.append({'symbol': symbol, 'error': str(exc).replace('\n', ' ')[:300]})

    out_path = os.path.join(PROJECT_ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    if errors:
        pd.DataFrame(errors).to_csv(out_path.replace('.csv', '_errors.csv'), index=False)
    print(f'CSV: {args.out}')
    if errors:
        print(f'Errors: {len(errors)}')
    if not df.empty:
        view = df.sort_values(['sharpe', 'directional_avg'], ascending=[False, False]).head(50)
        print(view.to_string(index=False, formatters={
            'hit_rate': lambda x: '-' if pd.isna(x) else f'{x:.1%}',
            'avg_ret': lambda x: '-' if pd.isna(x) else f'{x:+.2%}',
            'directional_avg': lambda x: '-' if pd.isna(x) else f'{x:+.2%}',
            'sharpe': lambda x: '-' if pd.isna(x) else f'{x:+.3f}',
        }))


if __name__ == '__main__':
    main()
