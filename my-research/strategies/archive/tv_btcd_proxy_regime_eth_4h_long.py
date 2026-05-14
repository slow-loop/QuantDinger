"""
Strategy: tv_btcd_proxy_regime_eth_4h_long
Thesis:   BTC Dominance (BTC.D) < 59.63% = capital rotating from BTC into alts (altseason).
          Since BTC.D is unavailable as OHLC data in our framework, we proxy it with two
          internal signals: (1) ETH golden cross (EMA50 > EMA200) and (2) ETH showing
          relative strength by holding above its 200-bar EMA in a pullback structure.
          When BOTH signals align, altcoin-season dynamics are active and structural
          long entries have historically higher success rates.
          The strategy itself is a BOS (Break of Structure): close above N-bar swing high.
          The BTC.D proxy is the regime gate that filters out bear-regime false signals.
Source:   BTC Dominance altseason signals:
          https://phemex.com/blogs/bitcoin-dominance-altcoin-season
          DEXTools BTC.D guide 2026:
          https://www.dextools.io/tutorials/what-is-bitcoin-dominance-btc-d-explained-guide-2026
          Altcoin sector rotation:
          https://www.spotedcrypto.com/altcoin-sector-rotation-2026-depin-ai-rwa-gaming/
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-14  code  init. BTC.D proxy gate: EMA50 > EMA200 (golden cross, altcoin regime)
                    + close > EMA200 (ETH holding macro uptrend).
                    Core entry: BOS = close > prior N-bar swing high.
                    Volume confirmation: volume > 1.3× vol_SMA20.
                    Stop: EMA50 break. Timeout: 30 bars.
  2026-05-14  run   BTC 4H IS: Sharpe +6.446, Sortino +8.267, Calmar +10478, IR +6.314,
                    PF 2.110, Win% 47.8%, payoff 2.302, n=138, exposure 38.6%. FAIL (OOS).
                    BTC 4H OOS: Sharpe -1.190, Sortino -0.985, PF 0.770, Win% 28.0%,
                    payoff 1.980, n=25. FAIL all.
                    (log: 2026-05-14)
  2026-05-14  note  Archive. Extreme IS overfit (Sharpe 6.446, Calmar 10478) driven by the
                    golden-cross gate selecting only 2020-2024 bull-market bars where BOS
                    trades naturally profit. OOS (2025-2026 bear) golden cross gone → entries
                    fire at random structure breaks → Win% crashes to 28% with no regime
                    support. The EMA50 > EMA200 proxy for BTC.D is a lagging, circular
                    condition — by the time the golden cross fires, altseason alpha is already
                    priced in. The BTC.D regime idea is conceptually sound but requires
                    real BTC.D data, not an ETH internal MA proxy.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param ema_fast int 50
# @param ema_slow int 200
# @param bos_lookback int 20
# @param vol_mult float 1.3
# @param timeout_bars int 30

import pandas as pd
import numpy as np

df = df.copy()

ema_fast     = int(params.get('ema_fast', 50))
ema_slow     = int(params.get('ema_slow', 200))
bos_lookback = int(params.get('bos_lookback', 20))
vol_mult     = float(params.get('vol_mult', 1.3))
timeout_bars = int(params.get('timeout_bars', 30))

# --- EMAs ---
ema50  = df['close'].ewm(span=ema_fast, adjust=False).mean()
ema200 = df['close'].ewm(span=ema_slow, adjust=False).mean()

# --- BTC.D proxy: altcoin regime gate ---
# Golden cross + price above EMA200 = ETH in structural uptrend = altcoin dynamics
golden_cross = ema50 > ema200
above_ema200 = df['close'] > ema200
altcoin_regime = golden_cross & above_ema200

# --- Break of Structure ---
prior_swing_high = df['close'].shift(1).rolling(bos_lookback).max()
bos = df['close'] > prior_swing_high

# --- Volume gate ---
vol_sma = df['volume'].rolling(20).mean()
vol_ok  = df['volume'] > vol_sma * vol_mult

# --- Entry: BOS + regime gate + volume ---
df['buy'] = (bos & altcoin_regime & vol_ok).fillna(False)

# --- Exit: timeout or EMA50 breaks ---
ema50_break = df['close'] < ema50
df['sell'] = (df['buy'].shift(timeout_bars).fillna(False) | ema50_break).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "BTC.D Proxy Regime BOS ETH 4H Long",
    "plots": [
        {"name": "EMA50",  "data": ema50.fillna(0).tolist(),  "color": "#FF9800", "overlay": True},
        {"name": "EMA200", "data": ema200.fillna(0).tolist(), "color": "#F44336", "overlay": True},
    ]
}
