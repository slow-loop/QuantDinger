"""
Strategy: tv_bos_macd_btcd_gate_4h_long
Thesis:   Identical BOS+MACD momentum mechanism as tv_bos_macd_momentum_4h_long
          (ETH 4H conditional pass, Sharpe +1.565 OOS), with an additional BTC Dominance
          proxy regime gate. The gate hypothesis: BOS+MACD entries only have edge when
          altcoins are in "season" (BTC.D < 59.63%). We proxy BTC.D with ETH's own
          golden cross (EMA50 > EMA200), reasoning that ETH outperforms when alts are
          in favour.
          Key test: does the regime gate improve OOS Sortino (was 1.230, threshold 1.5)?
          Or does the bear-market gate eliminate all OOS trades?
Source:   Same as tv_bos_macd_momentum_4h_long.
          BTC.D gate hypothesis:
          https://phemex.com/blogs/bitcoin-dominance-altcoin-season
          https://www.dextools.io/tutorials/what-is-bitcoin-dominance-btc-d-explained-guide-2026
          Scouted 2026-05-15 (second-round non-orthodox report, B2 BTC.D Gate idea).
Status:   archived

History (append-only, newest at bottom):
  2026-05-15  code  init. Adds EMA50 > EMA200 gate (BTC.D proxy) to BOS+MACD.
                    All other logic identical to tv_bos_macd_momentum_4h_long.
                    Hypothesis: gate removes bear-regime entries that cause Sortino miss.
                    Caveat: ETH MA proxy is known to overfit to bull regime (see
                    tv_btcd_proxy_regime_eth_4h_long.py in archive — standalone failed).
                    But as an OVERLAY on an already-passing strategy, effect TBD.
  2026-05-15  run   ETH/USDT 4H IS: Sharpe +3.117, Sortino +2.823, Calmar high, IR +2.316,
                    PF 1.890, Win% 40.6%, payoff 2.762, n=32. Passes all IS.
                    ETH/USDT 4H OOS: Sharpe -2.439, Sortino -0.797, PF 0.0, Win% 0%, n=3.
                    FAIL (IS overfit, OOS collapse). (log: 2026-05-15)
  2026-05-15  note  Archive. Golden cross gate (EMA50 > EMA200) is True throughout the IS
                    bull market (2020-2025), making IS metrics look excellent (+3.117 Sharpe)
                    but masking bull-only bias. In OOS bear market (2025-2026), EMA50 < EMA200
                    almost always → gate eliminates all but 3 OOS trades, all of which lose.
                    Confirms: OHLC-only BTC.D proxies (MA cross) cannot function as altcoin
                    season gates — they ARE the regime they're trying to filter and overfit.
                    True BTC.D gate requires external BTC.D data feed (future AltData work).
"""

# @strategy stopLossPct 0.03
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param swing_lookback int 20
# @param macd_fast int 12
# @param macd_slow int 26
# @param macd_signal int 9
# @param vol_mult float 1.4
# @param ema_fast_btcd int 50
# @param ema_slow_btcd int 200
# @param timeout_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

swing_lookback     = int(params.get('swing_lookback', 20))
macd_fast          = int(params.get('macd_fast', 12))
macd_slow          = int(params.get('macd_slow', 26))
macd_signal_period = int(params.get('macd_signal', 9))
vol_mult           = float(params.get('vol_mult', 1.4))
ema_fast_len       = int(params.get('ema_fast_btcd', 50))
ema_slow_len       = int(params.get('ema_slow_btcd', 200))
timeout_bars       = int(params.get('timeout_bars', 40))

# --- MACD ---
ema_fast_macd  = df['close'].ewm(span=macd_fast, adjust=False).mean()
ema_slow_macd  = df['close'].ewm(span=macd_slow, adjust=False).mean()
macd_line      = ema_fast_macd - ema_slow_macd
signal_line    = macd_line.ewm(span=macd_signal_period, adjust=False).mean()
macd_cross_up  = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))

# --- BOS ---
prior_swing_high = df['close'].shift(1).rolling(swing_lookback).max()
bos              = df['close'] > prior_swing_high

# --- Volume gate ---
vol_sma  = df['volume'].rolling(20).mean()
vol_gate = df['volume'] > vol_sma * vol_mult

# --- BTC.D proxy gate (ETH golden cross) ---
ema_btcd_fast  = df['close'].ewm(span=ema_fast_len, adjust=False).mean()
ema_btcd_slow  = df['close'].ewm(span=ema_slow_len, adjust=False).mean()
btcd_gate      = ema_btcd_fast > ema_btcd_slow   # EMA50 > EMA200 = altcoin season proxy

# --- Entry: BOS + MACD + Volume + BTC.D regime gate ---
df['buy'] = (bos & macd_cross_up & vol_gate & btcd_gate).fillna(False)

# --- Exit: MACD line drops below 0 ---
macd_below_zero = (macd_line < 0) & (macd_line.shift(1) >= 0)
timeout_exit    = df['buy'].shift(timeout_bars).fillna(False)
df['sell']      = (macd_below_zero | timeout_exit).fillna(False).astype(bool)

df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)
