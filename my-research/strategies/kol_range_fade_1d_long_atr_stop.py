"""
Strategy: kol_range_fade_1d_long_atr_stop
Thesis:   Daily range fade long — buy the bottom 15% of the 20-day range in low-ADX regimes,
          with a 6% stop loss (~1.5x typical BTC daily ATR of ~4%) giving mean-reversion room
          to play out over the 7-day horizon the factor event test validated.
Built on: factors/factor_range_fade.py
Status:   active

History (append-only, newest at bottom):
  2026-05-05  code  init. structural change from kol_range_fade_4h_long.py (archived).
                    Root cause of old strategy's failure: 2% stop fires before 7d reversion completes.
                    Factor event test (1D OOS) showed 91.7% 7d hit, 100% 30d hit (n=12).
                    New design: same entry logic (ADX<20 + bottom 15% of 20d range),
                    stop widened to 6% (≈1.5x daily ATR) + 15-bar time exit.
                    Timeframe: 1D. Target: enter at range bottom, exit at range midpoint.
  2026-05-05  run   BTC/USDT 1D — IS: +4.93% Sharpe 0.27 n=11 payoff 0.76 PF 1.32.
                    OOS: +10.74% Sharpe 1.09 n=3 payoff 3.51 PF 7.03.
                    6% stop improved payoff ratio (was 0.26 with 2% stop → now 0.76 IS).
                    BNB/USDT 1D — IS: +31.1% Sharpe 0.75 n=19 payoff 1.28 PF 1.76.
                    OOS: -33.1% Sharpe -1.61 n=3 payoff 0.03. BNB OOS catastrophic (bear regime).
                    (log: 2026-05-05T14:3x:xx)
  2026-05-05  note  BTC OOS (n=3) is too sparse to conclude. IS Sharpe 0.27 is weak — only 11 trades
                    in 5 years (ADX<20 is rarely met on BTC 1D in trending markets). 6% stop is an
                    improvement over 2% but payoff ratio (0.76) is still slightly inverted.
                    BNB OOS failure is a regime issue — range fade long is not a bear-market strategy.
                    Next: widen ADX threshold to 25 to increase IS n, or accept this as portfolio-
                    component only. Current evidence is inconclusive — needs more OOS cycles.
"""

# @strategy stopLossPct 0.06
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param adx_threshold float 20.0
# @param entry_range_pos float 0.15
# @param exit_range_pos float 0.50
# @param timeout_bars int 15

import pandas as pd
import numpy as np

df = df.copy()

adx_threshold = float(params.get('adx_threshold', 20.0))
entry_range_pos = float(params.get('entry_range_pos', 0.15))
exit_range_pos = float(params.get('exit_range_pos', 0.50))
timeout_bars = int(params.get('timeout_bars', 15))


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
natural_sell = mid_range_exit.fillna(False) & ~mid_range_exit.shift(1).fillna(False)
time_forced_sell = raw_buy.shift(timeout_bars).fillna(False)

df['buy'] = raw_buy.astype(bool)
df['sell'] = (natural_sell.fillna(False) | time_forced_sell).astype(bool)

output = {
    "name": "KOL Range Fade 1D Long (ATR stop)",
    "plots": [
        {"name": "ADX14", "data": adx14.tolist(), "color": "#FF5722", "overlay": False},
        {"name": "range_pos", "data": range_pos.fillna(0.5).tolist(), "color": "#FFD700", "overlay": False},
    ]
}
