# Factor: Regime — Strong Downtrend
# Source: cap_045_regime_trending_down — IC=+0.098 in crypto-kol-quant
# Faithful port of capabilities/regime.py:13-17.
# Triggers when price < MA200 AND MA50 < MA200 AND ADX > 25 (strong, confirmed downtrend).
# Outputs negative score (short bias).

# @param adx_threshold float 25.0

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 25.0))


def _adx(high, low, close, period=14):
    """Wilder's ADX. Returns the ADX series."""
    up = high.diff()
    dn = -low.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    plus_dm = pd.Series(plus_dm, index=high.index)
    minus_dm = pd.Series(minus_dm, index=high.index)

    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)

    # Wilder smoothing ≈ EMA with alpha = 1/period
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx.fillna(0)


ma50 = df['close'].rolling(window=50, min_periods=20).mean()
ma200 = df['close'].rolling(window=200, min_periods=50).mean()
adx14 = _adx(df['high'], df['low'], df['close'], period=14)

trig = (df['close'] < ma200) & (ma50 < ma200) & (adx14 > adx_threshold)

df['regime_down_score'] = np.where(trig.fillna(False), -1.0, 0.0)

output = {
    "name": "Factor Regime Trending Down",
    "plots": [
        {"name": "MA200", "data": ma200.fillna(0).tolist(), "color": "#9C27B0", "overlay": True},
        {"name": "MA50", "data": ma50.fillna(0).tolist(), "color": "#03A9F4", "overlay": True},
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "regime_down_score", "data": df['regime_down_score'].tolist(), "color": "#FF1744", "overlay": False},
    ]
}
