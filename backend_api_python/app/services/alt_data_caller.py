import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from app.data_sources.alt_data import fetch_binance_funding_rate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AltDataCaller:
    """
    Caller for alternative data sources.
    Matches the design pattern of IndicatorCaller. It gets injected into the strategy sandbox
    so that strategies can pull alternative data elegantly.
    """
    def __init__(self, context_params: Dict[str, Any]):
        """
        Initialize with the current backtest context.
        context_params should contain: market, symbol, start_date, end_date, timeframe
        """
        self.market = context_params.get('market', '')
        self.symbol = context_params.get('symbol', '')
        self.start_date = context_params.get('start_date')
        self.end_date = context_params.get('end_date')
        
    def call_alt_data(self, data_type: str, df: pd.DataFrame, kwargs: dict = None) -> pd.DataFrame:
        """
        Fetch alternative data and return it.
        
        Args:
            data_type: The type of alternative data (e.g., 'binance_funding_rate')
            df: The primary K-line dataframe.
            kwargs: Any extra parameters (e.g. overriding symbol).
        
        Returns:
            A DataFrame containing the alternative data, ready to be merged.
        """
        if kwargs is None:
            kwargs = {}
            
        target_symbol = kwargs.get('symbol', self.symbol)
        
        if data_type == 'binance_funding_rate':
            # Ensure we have valid dates
            start_dt = self.start_date
            end_dt = self.end_date
            
            # Fallback to deriving from df if context dates are missing
            if not start_dt or not end_dt:
                if not df.empty and 'time' in df.columns:
                    start_dt = df['time'].min()
                    end_dt = df['time'].max()
                else:
                    logger.warning("No date range provided for alt data fetch.")
                    return pd.DataFrame()
                
            alt_df = fetch_binance_funding_rate(target_symbol, start_dt, end_dt)
            return alt_df
            
        else:
            logger.warning(f"Unsupported alternative data type: {data_type}")
            return pd.DataFrame()
