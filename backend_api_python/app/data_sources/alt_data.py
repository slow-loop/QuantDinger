import requests
import pandas as pd
from datetime import datetime, timezone
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

def fetch_binance_funding_rate(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetch historical funding rate from Binance USD-M Futures.
    
    Args:
        symbol: e.g., 'BTC/USDT'
        start_date: Backtest start date
        end_date: Backtest end date
        
    Returns:
        DataFrame with columns ['time', 'funding_rate']
    """
    if not symbol:
        return pd.DataFrame()
        
    api_symbol = symbol.replace('/', '').replace('-', '').upper()
    
    # Ensure start_date and end_date are timezone aware
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
        
    start_ts = int(start_date.timestamp() * 1000)
    end_ts = int(end_date.timestamp() * 1000)
    
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    all_data = []
    
    current_start = start_ts
    limit = 1000
    
    try:
        while current_start < end_ts:
            params = {
                "symbol": api_symbol,
                "startTime": current_start,
                "endTime": end_ts,
                "limit": limit
            }
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            if not data:
                break
                
            all_data.extend(data)
            last_time = data[-1]['fundingTime']
            
            if current_start >= last_time + 1:
                break
                
            current_start = last_time + 1
            time.sleep(0.1) # Basic rate limit protection
    except Exception as e:
        logger.error(f"Failed to fetch Binance funding rate for {api_symbol}: {e}")
            
    if not all_data:
        logger.warning(f"No funding rate data returned for {api_symbol}")
        # Return empty DF with expected columns
        return pd.DataFrame(columns=['time', 'funding_rate'])
        
    df = pd.DataFrame(all_data)
    
    # Binance returns 'fundingTime' and 'fundingRate'
    if 'fundingTime' not in df.columns or 'fundingRate' not in df.columns:
        return pd.DataFrame(columns=['time', 'funding_rate'])
        
    df['time'] = pd.to_datetime(df['fundingTime'], unit='ms')
    df['funding_rate'] = df['fundingRate'].astype(float)
    
    # Select only the needed columns
    df = df[['time', 'funding_rate']]
    
    # Sort by time just in case
    df = df.sort_values('time').reset_index(drop=True)
    
    logger.info(f"Fetched {len(df)} funding rate records for {api_symbol}")
    return df
