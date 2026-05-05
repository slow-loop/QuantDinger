import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta

# Add app directory to path robustly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from flask import Flask
app = Flask(__name__)

# Import dependencies at the top level
from app.services.backtest import BacktestService
from app.services.indicator_params import StrategyConfigParser
from app.data_sources.alt_data import fetch_binance_funding_rate


def _build_strategy_config(code: str) -> dict:
    """Parse @strategy annotations and convert flat keys to nested config the engine expects.

    Without this, backtest_runner ran with no risk controls — every strategy held positions
    indefinitely regardless of stopLossPct / trailing annotations, making backtests useless
    for risk-managed strategies.
    """
    flat = StrategyConfigParser.parse(code) or {}
    if not flat:
        return {}
    cfg: dict = {}
    risk: dict = {}
    trailing: dict = {}
    if 'stopLossPct' in flat:
        risk['stopLossPct'] = flat['stopLossPct']
    if 'takeProfitPct' in flat:
        risk['takeProfitPct'] = flat['takeProfitPct']
    if 'trailingEnabled' in flat:
        trailing['enabled'] = flat['trailingEnabled']
    if 'trailingStopPct' in flat:
        trailing['pct'] = flat['trailingStopPct']
    if 'trailingActivationPct' in flat:
        trailing['activationPct'] = flat['trailingActivationPct']
    if trailing:
        risk['trailing'] = trailing
    if risk:
        cfg['risk'] = risk
    if 'entryPct' in flat:
        cfg['position'] = {'entryPct': flat['entryPct']}
    if 'tradeDirection' in flat:
        cfg['tradeDirection'] = flat['tradeDirection']
    return cfg

class AltDataBacktestService(BacktestService):
    """
    Inherits from BacktestService to dynamically inject alternative data (e.g., funding rates).
    This allows for sandbox testing without modifying the core engine's source code.
    """
    def _fetch_kline_data(self, market, symbol, timeframe, start_date, end_date):
        # 1. Fetch original K-line data
        df = super()._fetch_kline_data(market, symbol, timeframe, start_date, end_date)
        
        # 2. Inject alternative data
        try:
            df_funding = fetch_binance_funding_rate(symbol, start_date, end_date)
            if not df_funding.empty:
                # df index is DatetimeIndex. df_funding has a 'time' column.
                df_funding.set_index('time', inplace=True)
                df = df.join(df_funding, how='left')
                df['funding_rate'] = df['funding_rate'].ffill().fillna(0)
            else:
                df['funding_rate'] = 0
        except Exception as e:
            print(f"Warning: Alt data fetch failed: {e}")
            if 'funding_rate' not in df.columns:
                df['funding_rate'] = 0
                
        return df


def calculate_bh_return(df):
    """Calculates Buy and Hold return percentage."""
    if df.empty:
        return 0
    start_price = df.iloc[0]['open']
    end_price = df.iloc[-1]['close']
    return (end_price - start_price) / start_price * 100


def run_evaluation(strategy_path, start_date, end_date, args):
    """Runs a backtest evaluation for a given period."""
    if not os.path.exists(strategy_path):
        return {'status': 'error', 'msg': f'Strategy file not found: {strategy_path}'}
        
    with open(strategy_path, 'r', encoding='utf-8') as f:
        code = f.read()

    backtest_service = AltDataBacktestService()
    
    # 1. Fetch benchmark data to calculate Buy & Hold
    try:
        df = backtest_service._fetch_kline_data(
            args.market, args.symbol, args.timeframe, start_date, end_date
        )
        bh_return = calculate_bh_return(df)
    except Exception as e:
        bh_return = 0
        print(f"Warning: Could not fetch benchmark data: {e}")

    # 2. Run Backtest
    strategy_config = _build_strategy_config(code)
    trade_direction = strategy_config.get('tradeDirection', 'long')
    try:
        result = backtest_service.run(
            indicator_code=code,
            market=args.market,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=args.capital,
            leverage=args.leverage,
            commission=args.commission,
            slippage=args.slippage,
            strategy_config=strategy_config,
            trade_direction=trade_direction,
        )
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

    if not result or result.get('status') == 'error':
        return {'status': 'error', 'msg': result.get('error_message', 'Unknown error')}

    # Calculate Alpha
    strategy_return = result.get('totalReturn', 0)
    alpha = strategy_return - bh_return

    return {
        'status': 'success',
        'totalReturn': strategy_return,
        'bhReturn': bh_return,
        'alpha': alpha,
        'maxDrawdown': result.get('maxDrawdown', 0),
        'sharpeRatio': result.get('sharpeRatio', 0),
        'winRate': result.get('winRate', 0),
        'totalTrades': result.get('totalTrades', 0)
    }

def print_report(phase_name, res):
    """Prints the evaluation report for a given phase."""
    print(f"--- {phase_name} ---")
    if res['status'] == 'error':
        print(f"❌ Error: {res['msg']}")
        return False
    
    print(f"Strategy Return: {res['totalReturn']:.2f}% | B&H Return: {res['bhReturn']:.2f}%")
    
    alpha = res['alpha']
    alpha_str = f"+{alpha:.2f}%" if alpha > 0 else f"{alpha:.2f}%"
    print(f"Alpha (Excess):  {alpha_str}")
    print(f"Max Drawdown:    {res['maxDrawdown']:.2f}%")
    print(f"Sharpe Ratio:    {res['sharpeRatio']:.2f}")
    print(f"Win Rate:        {res['winRate']:.2f}% ({res['totalTrades']} trades)")
    print("")
    return True

def main():
    parser = argparse.ArgumentParser(description="Backtest Runner for In-Sample & Out-Of-Sample Evaluation")
    parser.add_argument("strategy_file", help="Path to strategy file relative to project root")
    parser.add_argument("--market", default="Crypto", help="Market type")
    parser.add_argument("--symbol", default="BTC/USDT", help="Trading symbol")
    parser.add_argument("--timeframe", default="1H", help="Timeframe (e.g., 1H, 1D)")
    parser.add_argument("--capital", type=float, default=10000.0, help="Initial capital")
    parser.add_argument("--leverage", type=int, default=1, help="Leverage multiplier")
    parser.add_argument("--commission", type=float, default=0.001, help="Commission rate")
    parser.add_argument("--slippage", type=float, default=0.0005, help="Slippage rate")
    parser.add_argument("--is-days", type=int, default=360, help="Number of days for In-Sample")
    parser.add_argument("--oos-days", type=int, default=90, help="Number of days for Out-Of-Sample")
    
    args = parser.parse_args()
    
    # Resolve strategy path
    strategy_path = os.path.join(PROJECT_ROOT, args.strategy_file)
    
    # Calculate dates
    now = datetime.now()
    is_start = now - timedelta(days=args.is_days)
    is_end = now - timedelta(days=args.oos_days)
    
    oos_start = is_end
    oos_end = now

    with app.app_context():
        print("="*60)
        print(f"🚀 BACKTEST REPORT")
        print(f"Strategy: {args.strategy_file}")
        print(f"Slippage Enforced: {args.slippage * 100}%")
        print(f"Commission Enforced: {args.commission * 100}%")
        print("="*60)
        
        # Run In-Sample
        res_is = run_evaluation(strategy_path, is_start, is_end, args)
        success_is = print_report(f"IN-SAMPLE (IS): {is_start.strftime('%Y-%m-%d')} to {is_end.strftime('%Y-%m-%d')}", res_is)
        
        # Run Out-Of-Sample
        res_oos = run_evaluation(strategy_path, oos_start, oos_end, args)
        success_oos = print_report(f"OUT-OF-SAMPLE (OOS): {oos_start.strftime('%Y-%m-%d')} to {oos_end.strftime('%Y-%m-%d')}", res_oos)

        print("="*60)
        if success_is and success_oos:
            if res_is['alpha'] > 0 and res_oos['alpha'] > 0:
                print("✅ PASSED: Positive Alpha in both IS and OOS.")
            else:
                print("⚠️ WARNING: Negative Alpha detected. Strategy underperforms Buy & Hold.")
        print("="*60)

if __name__ == "__main__":
    main()
