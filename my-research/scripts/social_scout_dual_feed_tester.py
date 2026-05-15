#!/usr/bin/env python3
"""
Dual-feed event tester for social-scout candidates.

This lives in my-research because QuantDinger strategy execution receives one df
per run. The script tests research ideas that need BTC + alt feeds without
patching upstream:

- alt/BTC relative-strength breakout
- BTC impulse followed by alt lag
- ETH/BTC 250D regime as a market gate
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

from app.services.backtest import BacktestService


def fetch(symbol, timeframe, days):
    svc = BacktestService()
    end = datetime.now(timezone.utc).replace(tzinfo=None)
    start = end - timedelta(days=days + 400)
    df = svc._fetch_kline_data('Crypto', symbol, timeframe, start, end)
    if df is None or len(df) == 0:
        raise RuntimeError(f'No data for {symbol} {timeframe}')
    df = df.copy()
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time').set_index('time')
    else:
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
    return df[['open', 'high', 'low', 'close', 'volume']].astype(float)


def event_stats(close, triggers, horizons, sign=1):
    rows = []
    for h in horizons:
        fwd = close.pct_change(h).shift(-h)
        rets = fwd[triggers & fwd.notna()]
        n = int(len(rets))
        if n == 0:
            rows.append({'horizon_bars': h, 'n': 0, 'hit_rate': np.nan, 'avg_ret': np.nan, 'sharpe': np.nan})
            continue
        directional = rets * sign
        rows.append({
            'horizon_bars': h,
            'n': n,
            'hit_rate': float((directional > 0).mean()),
            'avg_ret': float(rets.mean()),
            'sharpe': float(directional.mean() / directional.std()) if directional.std() > 0 else np.nan,
        })
    return rows


def split_mask(index, oos_days):
    oos_start = index.max() - pd.Timedelta(days=oos_days)
    return {
        'IS': index < oos_start,
        'OOS': index >= oos_start,
        'full': pd.Series(True, index=index),
    }


def test_alt_btc_rs(alt_symbol, alt, btc, args):
    df = pd.concat([
        alt['close'].rename('alt_close'),
        btc['close'].rename('btc_close'),
    ], axis=1, join='inner').dropna()
    ratio = df['alt_close'] / df['btc_close']
    prior_high = ratio.shift(1).rolling(args.rs_lookback).max()
    triggers = ratio > prior_high
    rows = []
    for period, mask in split_mask(df.index, args.oos_days).items():
        mask = pd.Series(mask, index=df.index) if not isinstance(mask, pd.Series) else mask
        for row in event_stats(df['alt_close'], triggers & mask, args.horizons):
            rows.append({'test': 'alt_btc_rs_breakout', 'symbol': alt_symbol, 'period': period, **row})
    return rows


def test_btc_impulse_alt_lag(alt_symbol, alt, btc, args):
    df = pd.concat([
        alt['close'].rename('alt_close'),
        btc['close'].rename('btc_close'),
    ], axis=1, join='inner').dropna()
    btc_ret = df['btc_close'].pct_change()
    alt_ret = df['alt_close'].pct_change()
    triggers = (btc_ret >= args.btc_impulse) & (alt_ret <= args.alt_lag_max)
    rows = []
    for period, mask in split_mask(df.index, args.oos_days).items():
        mask = pd.Series(mask, index=df.index) if not isinstance(mask, pd.Series) else mask
        for row in event_stats(df['alt_close'], triggers & mask, args.lag_horizons):
            rows.append({'test': 'btc_impulse_alt_lag', 'symbol': alt_symbol, 'period': period, **row})
    return rows


def test_eth_btc_regime(alt_symbol, alt_4h, eth_d, btc_d, args):
    daily = pd.concat([
        eth_d['close'].rename('eth_close'),
        btc_d['close'].rename('btc_close'),
    ], axis=1, join='inner').dropna()
    ratio = daily['eth_close'] / daily['btc_close']
    ma = ratio.rolling(args.ethbtc_ma).mean()
    regime_daily = ratio > ma
    regime_4h = regime_daily.reindex(alt_4h.index, method='ffill').fillna(False)

    rows = []
    fwd = alt_4h['close'].pct_change(args.regime_horizon).shift(-args.regime_horizon)
    for period, mask in split_mask(alt_4h.index, args.oos_days).items():
        mask = pd.Series(mask, index=alt_4h.index) if not isinstance(mask, pd.Series) else mask
        for label, regime_mask in [('ethbtc_above_ma', regime_4h), ('ethbtc_below_ma', ~regime_4h)]:
            rets = fwd[mask & regime_mask & fwd.notna()]
            n = int(len(rets))
            rows.append({
                'test': label,
                'symbol': alt_symbol,
                'period': period,
                'horizon_bars': args.regime_horizon,
                'n': n,
                'hit_rate': float((rets > 0).mean()) if n else np.nan,
                'avg_ret': float(rets.mean()) if n else np.nan,
                'sharpe': float(rets.mean() / rets.std()) if n and rets.std() > 0 else np.nan,
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbols', default='AVAX/USDT,LINK/USDT,ARB/USDT,OP/USDT,DOGE/USDT')
    parser.add_argument('--days', type=int, default=2600)
    parser.add_argument('--oos-days', type=int, default=365)
    parser.add_argument('--timeframe', default='4H')
    parser.add_argument('--horizons', type=lambda s: [int(x) for x in s.split(',')], default='6,18,42')
    parser.add_argument('--lag-horizons', type=lambda s: [int(x) for x in s.split(',')], default='1,3,6')
    parser.add_argument('--rs-lookback', type=int, default=60)
    parser.add_argument('--btc-impulse', type=float, default=0.02)
    parser.add_argument('--alt-lag-max', type=float, default=0.01)
    parser.add_argument('--ethbtc-ma', type=int, default=250)
    parser.add_argument('--regime-horizon', type=int, default=42)
    parser.add_argument('--out', default='my-research/log/results/social_scout_dual_feed_2026-05-15.csv')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',') if s.strip()]
    rows = []
    with app.app_context():
        btc_4h = fetch('BTC/USDT', args.timeframe, args.days)
        btc_d = fetch('BTC/USDT', '1D', args.days)
        eth_d = fetch('ETH/USDT', '1D', args.days)
        for sym in symbols:
            alt_4h = fetch(sym, args.timeframe, args.days)
            rows.extend(test_alt_btc_rs(sym, alt_4h, btc_4h, args))
            rows.extend(test_btc_impulse_alt_lag(sym, alt_4h, btc_4h, args))
            rows.extend(test_eth_btc_regime(sym, alt_4h, eth_d, btc_d, args))

    out_path = os.path.join(PROJECT_ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f'CSV: {args.out}')
    df = pd.DataFrame(rows)
    oos = df[df['period'] == 'OOS'].copy()
    oos = oos.sort_values(['test', 'avg_ret'], ascending=[True, False])
    print(oos.to_string(index=False, formatters={
        'hit_rate': lambda x: '-' if pd.isna(x) else f'{x:.1%}',
        'avg_ret': lambda x: '-' if pd.isna(x) else f'{x:+.2%}',
        'sharpe': lambda x: '-' if pd.isna(x) else f'{x:+.3f}',
    }))


if __name__ == '__main__':
    main()
