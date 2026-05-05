"""
Strategy: kol_range_fade_4h_long
Thesis:   Range fade long — buy the bottom 15% of the 20-bar range in low-ADX regimes.
          Mean-reversion bet: price recovers to range midpoint.
Built on: factors/factor_range_fade.py
Status:   archived — 2% stop incompatible with daily vol; see note 2026-05-05

History (append-only, newest at bottom):
  2026-05-04  code  init. 4H long-only range fade, stop 5%→2% (kill R:R problem). ADX<20 gate.
  2026-05-04  run   BTC/USDT 4H — IS: -14% Sharpe -0.10 n=90. OOS: -10% Sharpe -1.13. ❌
                    ETH/USDT 4H — IS: -59% Sharpe -2.06. OOS: +0.4% Sharpe 0.22. Mixed.
                    SOL/USDT 4H — IS: -60% Sharpe -1.16. OOS: -25% Sharpe -1.68. ❌
                    BNB/USDT 4H — IS: -58% Sharpe -2.84. OOS: +11% Sharpe 1.70 PF 1.98. ✓ BNB only.
                    (log: 2026-05-04T06:28:xx / 06:29:xx)
  2026-05-05  run   BTC/USDT 1D — IS: -11.6% Sharpe -0.21 n=11 payoff 0.26. OOS: +14% Sharpe 1.34 n=3.
                    BNB/USDT 1D — IS: +17.9% Sharpe 0.48 n=18. OOS: -32.8% Sharpe -1.25 n=3. ❌
                    OOS n=3 on both 1D runs — statistically meaningless.
                    (log: 2026-05-05T14:23:xx)
  2026-05-05  note  Root cause diagnosis: 2% fixed stop is incompatible with daily/4H volatility.
                    Daily ATR for BTC is typically 3-5%, so the stop fires before mean-reversion
                    plays out. Payoff ratio consistently 0.26-0.85 — losers much bigger than winners
                    after commission. Factor event test shows 91.7% OOS hit at 7d horizon (no stop),
                    confirming the FACTOR has edge but the STOP destroys it.
                    If continuing this line: switch to 1x ATR dynamic stop → new file
                    kol_range_fade_1d_long_atr_stop.py. Otherwise archive.
                    Decision: archiving this file. Factor itself is valid; need a new wrapper.
"""

# @strategy stopLossPct 0.02
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param adx_threshold float 20.0
# @param entry_range_pos float 0.15
# @param exit_range_pos float 0.50

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 20.0))
entry_range_pos = float(params.get('entry_range_pos', 0.15))
exit_range_pos = float(params.get('exit_range_pos', 0.50))


def _adx(high, low, close, period=14):
    up = high.diff()
    dn = -low.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=high.index)
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0)


adx14 = _adx(df['high'], df['low'], df['close'], period=14)
high_20 = df['high'].rolling(window=20, min_periods=10).max()
low_20 = df['low'].rolling(window=20, min_periods=10).min()
range_pos = ((df['close'] - low_20) / (high_20 - low_20).replace(0, np.nan)).clip(0, 1)

in_range = adx14 < adx_threshold
long_entry = in_range & (range_pos < entry_range_pos)
mid_range_exit = range_pos > exit_range_pos

raw_buy = long_entry.fillna(False) & ~long_entry.shift(1).fillna(False)
raw_sell = mid_range_exit.fillna(False) & ~mid_range_exit.shift(1).fillna(False)

df['buy'] = raw_buy.astype(bool)
df['sell'] = raw_sell.astype(bool)

output = {
    "name": "KOL Range Fade 4H Long",
    "plots": [
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "range_pos", "data": range_pos.fillna(0.5).tolist(), "color": "#FFD700", "overlay": False},
    ]
}
