"""
Strategy: tv_pump_fade_eth_4h
Thesis:   A large crash following a prior pump creates an oversold mean-reversion opportunity.
          After a pump >pump_pct% in pump_window bars AND a subsequent crash >crash_pct% from
          peak, oversold conditions (RSI < 30) + price reclaiming EMA9 from below = long entry.
          This exploits the post-CEX-listing dump (avg -52% from peak, -70% from Binance listing)
          where sentiment over-corrects and a technical bounce follows.
          Evaluator limitation: tradeDirection=short not parsed by evaluator script; reframed as
          long entry on the crash recovery bounce instead of shorting the initial dump.
Source:   CEX listing pump-and-dump studies:
          https://bitpinas.com/cryptocurrency/binance-token-listing-dump/
          https://www.cryptopolitan.com/83-cex-listed-tokens-2025-trading-price/
          Scouted 2026-05-14 (non-orthodox altcoin strategy research session).
Status:   archived

History (append-only, newest at bottom):
  2026-05-14  code  init. (v1 was short, evaluator doesn't support; reframed as long bounce.)
                    Pump detection: close is pump_pct% above rolling N-bar low (was pumped).
                    Crash detection: close is crash_pct% below rolling peak (now crashed).
                    Oversold gate: RSI14 < rsi_thresh (oversold).
                    Entry: first bar where close crosses ABOVE EMA9 (bounce confirmation).
                    Long only. Stop: 5%. Timeout: 20 bars.
  2026-05-14  run   BTC 4H IS: 0 trades. BTC 4H OOS: 0 trades. FAIL.
                    Conditions too strict for BTC 4H: pump (+25% in 20 bars) + crash (-20%
                    from peak) + RSI < 35 + EMA9 reclaim rarely all align simultaneously
                    on 4H. The sequence is common in alts but not in BTC/ETH 4H.
                    (log: 2026-05-14)
  2026-05-14  note  Archive. Two blocking issues: (1) evaluator doesn't support short
                    direction (tradeDirection param only parsed by UI, not evaluator script),
                    so original short thesis (CEX listing dump) cannot be backtested via CLI;
                    (2) reframed long bounce version generates 0 trades on BTC/ETH 4H —
                    the strict condition chain never fires on large-cap 4H data.
                    This thesis would require either: UI-based short evaluation, or
                    testing on smaller altcoin data where pump/crash sequences are more common.
"""

# @strategy stopLossPct 0.05
# @strategy tradeDirection long
# @strategy entryPct 1.0

# @param pump_window int 20
# @param pump_pct float 0.25
# @param crash_pct float 0.20
# @param rsi_thresh float 35.0
# @param ema_fast int 9
# @param timeout_bars int 20

import pandas as pd
import numpy as np

df = df.copy()

pump_window  = int(params.get('pump_window', 20))
pump_pct     = float(params.get('pump_pct', 0.25))
crash_pct    = float(params.get('crash_pct', 0.20))
rsi_thresh   = float(params.get('rsi_thresh', 35.0))
ema_fast     = int(params.get('ema_fast', 9))
timeout_bars = int(params.get('timeout_bars', 20))

# --- EMA9 ---
ema9 = df['close'].ewm(span=ema_fast, adjust=False).mean()

# --- RSI14 ---
delta  = df['close'].diff()
gain   = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
loss   = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
rs     = gain / loss.replace(0, np.nan)
rsi14  = 100 - 100 / (1 + rs)

# --- Prior pump: close was pump_pct% above its rolling low in last pump_window bars ---
rolling_low  = df['close'].rolling(pump_window).min().shift(1)
prior_pump   = (df['close'].shift(1) - rolling_low) / rolling_low.replace(0, np.nan) > pump_pct

# --- Current crash: close is crash_pct% below the rolling high (since the pump) ---
rolling_peak  = df['close'].rolling(pump_window).max().shift(1)
current_crash = (rolling_peak - df['close']) / rolling_peak.replace(0, np.nan) > crash_pct

# --- Bounce: close crosses above EMA9 from below ---
above_ema9     = df['close'] > ema9
was_below_ema9 = df['close'].shift(1) <= ema9.shift(1)
ema9_bounce    = above_ema9 & was_below_ema9

# --- Entry: pump occurred + now crashed + oversold + bounce ---
df['buy'] = (prior_pump & current_crash & (rsi14 < rsi_thresh) & ema9_bounce).fillna(False)

# --- Exit: timeout ---
df['sell'] = df['buy'].shift(timeout_bars).fillna(False).astype(bool)

# Clean
df['buy']  = df['buy'].fillna(False)
df['sell'] = df['sell'].fillna(False)

output = {
    "name": "Pump Crash Bounce ETH 4H Long",
    "plots": [
        {"name": "EMA9",         "data": ema9.fillna(0).tolist(),          "color": "#FF5722", "overlay": True},
        {"name": "RSI14",        "data": rsi14.fillna(0).tolist(),         "color": "#2196F3", "overlay": False},
        {"name": "rolling_peak", "data": rolling_peak.fillna(0).tolist(),  "color": "#9C27B0", "overlay": True},
    ]
}
