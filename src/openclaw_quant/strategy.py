"""
Strategy Base Class

Provides a simple, elegant API for strategy development.
Inspired by backtesting.py but with enhanced functionality.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
import pandas as pd
import numpy as np


class Strategy(ABC):
    """
    Base class for trading strategies.

    Usage:
        class MyStrategy(Strategy):
            # Define parameters (can be optimized)
            period = 20

            def init(self):
                # Precompute indicators (vectorized)
                self.ma = self.I(SMA, self.data.Close, self.period)

            def next(self):
                # Event-driven logic for each bar
                if self.ma[-1] > self.data.Close[-1]:
                    if not self.position:
                        self.buy()
                else:
                    if self.position:
                        self.sell()
    """

    def __init__(self):
        self._data: Optional[pd.DataFrame] = None
        self._indicators: Dict[str, pd.Series] = {}
        self._i: int = 0  # Current bar index

    @property
    def data(self) -> pd.DataFrame:
        """Access to OHLCV data"""
        return self._data

    @property
    def position(self) -> 'Position':
        """Current position (set by backtest engine)"""
        return self._broker.position

    @property
    def equity(self) -> float:
        """Current equity (set by backtest engine)"""
        return self._broker.equity

    def I(self, func: Callable, *args, **kwargs) -> pd.Series:
        """
        Register an indicator for vectorized computation.

        Args:
            func: Indicator function (e.g., SMA, RSI)
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments

        Returns:
            Indicator series (can be accessed with [-1] for current value)

        Example:
            self.ma = self.I(SMA, self.data.Close, 20)
            current_ma = self.ma[-1]
        """
        # Compute indicator once for entire dataset
        indicator = func(*args, **kwargs)

        # Convert to SeriesAccessor for easy access
        accessor = _SeriesAccessor(indicator, self)
        return accessor

    @abstractmethod
    def init(self):
        """
        Initialize strategy: precompute indicators.

        Called once before backtesting starts.
        Use self.I() to register indicators.
        """
        pass

    @abstractmethod
    def next(self):
        """
        Main strategy logic executed on each bar.

        Access data with:
        - self.data.Close[-1]  # Current close
        - self.data.Close[-2]  # Previous close
        - self.ma[-1]          # Current indicator value

        Execute trades with:
        - self.buy()           # Open long position
        - self.sell()          # Close long position
        - self.buy(size=0.5)   # Buy 50% of capital
        """
        pass

    def buy(self, size: Optional[float] = None, limit: Optional[float] = None,
            stop: Optional[float] = None, take_profit: Optional[float] = None):
        """
        Place a buy order.

        Args:
            size: Position size (None = all available capital)
            limit: Limit price (None = market order)
            stop: Stop loss price
            take_profit: Take profit price
        """
        self._broker.buy(size, limit, stop, take_profit)

    def sell(self, size: Optional[float] = None, limit: Optional[float] = None):
        """
        Place a sell order.

        Args:
            size: Position size (None = close entire position)
            limit: Limit price (None = market order)
        """
        self._broker.sell(size, limit)

    def _set_broker(self, broker):
        """Internal: set broker instance"""
        self._broker = broker

    def _set_data(self, data: pd.DataFrame):
        """Internal: set data"""
        self._data = data

    def _set_index(self, i: int):
        """Internal: set current bar index"""
        self._i = i


class _SeriesAccessor:
    """
    Wrapper for indicator series to allow array-like access.

    Allows accessing future bars during backtesting by tracking current index.
    """

    def __init__(self, series: pd.Series, strategy: Strategy):
        self._series = series
        self._strategy = strategy

    def __getitem__(self, key):
        """
        Array-like access to indicator values.

        -1 returns current bar, -2 returns previous bar, etc.
        """
        if isinstance(key, int):
            if key < 0:
                # Negative indexing: -1 = current, -2 = previous
                idx = self._strategy._i + key + 1
            else:
                # Positive indexing (absolute)
                idx = key

            if 0 <= idx < len(self._series):
                return self._series.iloc[idx]
            else:
                return np.nan
        else:
            # Slice or other key types
            return self._series[key]

    def __len__(self):
        return len(self._series)

    def __repr__(self):
        return f"Indicator({self._series.name})"

    @property
    def series(self) -> pd.Series:
        """Access underlying pandas Series"""
        return self._series


# Example strategies for reference
class BuyAndHold(Strategy):
    """Simple buy and hold strategy"""

    def init(self):
        pass

    def next(self):
        if not self.position:
            self.buy()


class SMAStrategy(Strategy):
    """Simple moving average crossover"""

    fast_period = 10
    slow_period = 30

    def init(self):
        from .indicators import SMA
        self.fast_ma = self.I(SMA, self.data.Close, self.fast_period)
        self.slow_ma = self.I(SMA, self.data.Close, self.slow_period)

    def next(self):
        if self.fast_ma[-1] > self.slow_ma[-1]:
            if not self.position:
                self.buy()
        elif self.fast_ma[-1] < self.slow_ma[-1]:
            if self.position:
                self.sell()
