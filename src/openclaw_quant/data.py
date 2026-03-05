"""
Data Fetching Module

Fetch historical and real-time market data from exchanges.
"""

import pandas as pd
import ccxt
from typing import Optional, List
from datetime import datetime, timedelta


class DataFetcher:
    """
    Fetch market data from cryptocurrency exchanges.

    Supports 100+ exchanges via ccxt library.
    """

    def __init__(self, exchange: str = 'binance', config: Optional[dict] = None):
        """
        Initialize data fetcher.

        Args:
            exchange: Exchange name (e.g., 'binance', 'okx', 'bybit')
            config: Exchange configuration (API keys, etc.)
        """
        self.exchange_name = exchange
        self.config = config or {}

        # Initialize exchange
        exchange_class = getattr(ccxt, exchange)
        self.exchange = exchange_class(self.config)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        since: Optional[datetime] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            since: Start date (None = last `limit` candles)
            limit: Number of candles to fetch

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        # Convert since to timestamp
        since_ts = None
        if since:
            since_ts = int(since.timestamp() * 1000)

        # Fetch data
        ohlcv = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since_ts,
            limit=limit
        )

        # Convert to DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        )

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')

        return df

    def fetch_historical(
        self,
        symbol: str,
        timeframe: str = '1h',
        days: int = 30
    ) -> pd.DataFrame:
        """
        Fetch historical data for a period.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            days: Number of days of history

        Returns:
            DataFrame with OHLCV data
        """
        all_data = []
        since = datetime.now() - timedelta(days=days)

        while True:
            # Fetch batch
            data = self.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=1000
            )

            if len(data) == 0:
                break

            all_data.append(data)

            # Update since to last timestamp
            last_timestamp = data.index[-1]
            since = last_timestamp + timedelta(milliseconds=1)

            # Stop if we've reached current time
            if since >= datetime.now():
                break

        # Concatenate all data
        if all_data:
            df = pd.concat(all_data)
            df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
            df = df.sort_index()
            return df
        else:
            return pd.DataFrame()

    def fetch_latest(self, symbol: str, timeframe: str = '1h') -> pd.DataFrame:
        """
        Fetch latest candle.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe

        Returns:
            DataFrame with single row
        """
        return self.fetch_ohlcv(symbol, timeframe, limit=1)

    @staticmethod
    def from_csv(file_path: str) -> pd.DataFrame:
        """
        Load data from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame with OHLCV data

        CSV format:
            timestamp,open,high,low,close,volume
            2024-01-01 00:00:00,45000,46000,44000,45500,1000
        """
        df = pd.read_csv(file_path)

        # Standardize column names
        column_mapping = {
            col.lower(): col.capitalize()
            for col in ['open', 'high', 'low', 'close', 'volume']
        }

        df = df.rename(columns=column_mapping)

        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

        return df

    @staticmethod
    def to_csv(data: pd.DataFrame, file_path: str):
        """
        Save data to CSV file.

        Args:
            data: OHLCV DataFrame
            file_path: Output file path
        """
        data.to_csv(file_path)

    def list_symbols(self) -> List[str]:
        """
        List all available trading pairs.

        Returns:
            List of symbol strings (e.g., ['BTC/USDT', 'ETH/USDT'])
        """
        markets = self.exchange.load_markets()
        return list(markets.keys())

    def list_timeframes(self) -> List[str]:
        """
        List supported timeframes.

        Returns:
            List of timeframe strings (e.g., ['1m', '5m', '1h'])
        """
        return list(self.exchange.timeframes.keys())


# Convenience function
def get_data(
    symbol: str = 'BTC/USDT',
    exchange: str = 'binance',
    timeframe: str = '1h',
    days: int = 30
) -> pd.DataFrame:
    """
    Quick helper to fetch data.

    Args:
        symbol: Trading pair
        exchange: Exchange name
        timeframe: Candle timeframe
        days: Days of history

    Returns:
        OHLCV DataFrame

    Example:
        data = get_data('BTC/USDT', days=365)
        bt = Backtest(MyStrategy, data)
    """
    fetcher = DataFetcher(exchange)
    return fetcher.fetch_historical(symbol, timeframe, days)
