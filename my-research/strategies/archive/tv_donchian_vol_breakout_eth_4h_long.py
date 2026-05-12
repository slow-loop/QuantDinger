"""
Strategy: tv_donchian_vol_breakout_eth_4h_long
Thesis:   Price closes above N-bar Donchian Channel high (new structural high) on
          above-average volume confirms genuine demand absorption — not a noise
          breakout. Volume confirmation filters out false breakouts in choppy regimes.
          The structural event (new N-bar high + volume) is the discrete catalyst.
          Inspired by Turtle Trading on 55-bar high, adapted for ETH 4H with volume gate.
Source:   Adapted from Donchian Breakout Strategy by millerrh (TradingView)
          https://www.tradingview.com/script/hyYvFjux-Donchian-Breakout-Strategy/
          Plus volume filter concept from community breakout strategies.
Status:   active

History (append-only, newest at bottom):
  2026-05-12  code  init. ETH-targeted Donchian breakout with volume confirmation.
                    Entry: close >= rolling N-bar high (shifted 1 for no lookahead) AND
                    volume >= vol_mult * 20-bar rolling avg volume (above-average volume).
                    Exit: close drops below rolling N-bar low (channel midpoint alternative)
                    OR close below EMA(50) as trend end signal OR timeout.
                    SL: platform 5% hard stop as backstop.
  2026-05-12  run   ETH 4H OOS: Sharpe -0.901, PF 0.78, Win% 29.4%, n=17. FAIL 0/5.
                    IS: Sharpe 4.91, Sortino 7.67 — extreme bull-market overfitting.
                    OOS beats B&H by 7pp (-16% vs -23%) but too weak for pass.
                    (log: 2026-05-12)
  2026-05-12  note  55-bar Donchian new high in choppy ETH is a bear trap (brief spike then
                    reversal). Kumo breakout is more selective because the cloud has already
                    tested/rejected price — it requires price to absorb the cloud resistance.
                    Volume gate helps but not enough to overcome the entry selectivity gap.
                    Archived. Do not retry Donchian on 4H without a stronger confluence filter.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param dc_length int 55
# @param vol_length int 20
# @param vol_mult float 1.5
# @param exit_dc_length int 20
# @param ema_exit int 50
# @param timeout_bars int 40

import pandas as pd
import numpy as np

df = df.copy()

dc_length    = int(params.get('dc_length', 55))
vol_length   = int(params.get('vol_length', 20))
vol_mult     = float(params.get('vol_mult', 1.5))
exit_dc_len  = int(params.get('exit_dc_length', 20))
ema_exit_len = int(params.get('ema_exit', 50))
timeout_bars = int(params.get('timeout_bars', 40))

# ── Donchian Channel entry high (shifted 1 to avoid lookahead) ──────────────
dc_high = df['high'].rolling(dc_length).max().shift(1)

# ── Donchian Channel exit low (shorter, for trailing exit) ──────────────────
dc_low_exit = df['low'].rolling(exit_dc_len).min().shift(1)

# ── Volume filter: above-average volume ─────────────────────────────────────
vol_avg = df['volume'].rolling(vol_length).mean()
high_volume = df['volume'] >= vol_mult * vol_avg

# ── EMA exit filter ──────────────────────────────────────────────────────────
ema_exit = df['close'].ewm(span=ema_exit_len, adjust=False).mean()

# ── Entry signal ─────────────────────────────────────────────────────────────
# Breakout: close makes new N-bar high + above-average volume
breakout = df['close'] >= dc_high
df['buy'] = breakout & high_volume

# ── Exit signal ───────────────────────────────────────────────────────────────
# Exit when close drops below the shorter Donchian exit level OR below EMA(50)
dc_exit = df['close'] <= dc_low_exit
ema_exit_signal = df['close'] < ema_exit

df['sell'] = dc_exit | ema_exit_signal

# Ensure boolean
df['buy']  = df['buy'].fillna(False).astype(bool)
df['sell'] = df['sell'].fillna(False).astype(bool)
