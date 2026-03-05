"""
Backtest Engine

Fast, vectorized backtesting with event-driven execution.
Balances performance (vectorization) with realism (event loop).
"""

import pandas as pd
import numpy as np
from typing import Type, Optional, Dict, Any
from datetime import datetime
import time

from .strategy import Strategy
from .types import Trade, Position, BacktestResult
from .metrics import calculate_metrics


class _Broker:
    """Internal broker for order execution during backtest"""

    def __init__(self, data: pd.DataFrame, cash: float, commission: float):
        self.data = data
        self.initial_cash = cash
        self.cash = cash
        self.commission = commission

        self.position = Position()
        self.trades: list[Trade] = []
        self.equity_curve = []

        self._i = 0  # Current bar index

    @property
    def equity(self) -> float:
        """Current equity (cash + position value)"""
        if self.position.is_flat:
            return self.cash

        current_price = self.data.Close.iloc[self._i]
        position_value = self.position.size * current_price
        return self.cash + position_value

    def buy(self, size: Optional[float] = None, limit: Optional[float] = None,
            stop: Optional[float] = None, take_profit: Optional[float] = None):
        """Execute buy order"""
        if not self.position.is_flat:
            return  # Already in position

        current_price = self.data.Close.iloc[self._i]
        current_time = self.data.index[self._i]

        # Calculate position size
        if size is None:
            # Use all available cash
            size = (self.cash / current_price) * (1 - self.commission)
        else:
            # Use specified fraction of cash
            size = (self.cash * size / current_price) * (1 - self.commission)

        if size <= 0:
            return

        # Execute trade
        cost = size * current_price
        fee = cost * self.commission

        self.cash -= (cost + fee)
        self.position.size = size
        self.position.entry_price = current_price
        self.position.entry_time = current_time

        # Record trade
        trade = Trade(
            timestamp=current_time,
            price=current_price,
            size=size,
            side='buy',
            fee=fee
        )
        self.trades.append(trade)

    def sell(self, size: Optional[float] = None, limit: Optional[float] = None):
        """Execute sell order"""
        if self.position.is_flat:
            return  # No position to close

        current_price = self.data.Close.iloc[self._i]
        current_time = self.data.index[self._i]

        # Calculate size to sell
        if size is None:
            size = self.position.size  # Close entire position
        else:
            size = min(size, self.position.size)

        if size <= 0:
            return

        # Execute trade
        proceeds = size * current_price
        fee = proceeds * self.commission
        pnl = (current_price - self.position.entry_price) * size - fee

        self.cash += (proceeds - fee)

        # Record trade
        trade = Trade(
            timestamp=current_time,
            price=current_price,
            size=size,
            side='sell',
            fee=fee,
            pnl=pnl
        )
        self.trades.append(trade)

        # Update position
        self.position.size -= size
        if self.position.size < 1e-10:  # Close to zero
            self.position.size = 0.0
            self.position.entry_price = 0.0
            self.position.entry_time = None

    def next(self, i: int):
        """Advance to next bar"""
        self._i = i
        self.equity_curve.append(self.equity)


class Backtest:
    """
    Backtest engine for strategy evaluation.

    Usage:
        bt = Backtest(MyStrategy, data, cash=10000, commission=0.001)
        result = bt.run()
        result.plot()

        # Optimize parameters
        best = bt.optimize(
            period=range(10, 50, 5),
            maximize='sharpe_ratio'
        )
    """

    def __init__(
        self,
        strategy: Type[Strategy],
        data: pd.DataFrame,
        cash: float = 10000.0,
        commission: float = 0.001,
        exclusive_orders: bool = True
    ):
        """
        Initialize backtest.

        Args:
            strategy: Strategy class (not instance)
            data: OHLCV DataFrame with DatetimeIndex
            cash: Initial capital
            commission: Commission rate (0.001 = 0.1%)
            exclusive_orders: If True, only one position at a time
        """
        self._strategy_class = strategy
        self._data = self._prepare_data(data)
        self._cash = cash
        self._commission = commission
        self._exclusive_orders = exclusive_orders

    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare and validate data"""
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        # Check for required columns (case-insensitive)
        data_columns = {col.lower(): col for col in data.columns}
        missing = [col for col in required_columns if col.lower() not in data_columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Standardize column names
        data = data.rename(columns={
            data_columns[col.lower()]: col for col in required_columns
        })

        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            if 'timestamp' in data.columns:
                data = data.set_index('timestamp')
                data.index = pd.to_datetime(data.index)
            elif 'date' in data.columns:
                data = data.set_index('date')
                data.index = pd.to_datetime(data.index)
            else:
                raise ValueError("Data must have DatetimeIndex or 'timestamp'/'date' column")

        # Sort by time
        data = data.sort_index()

        return data[required_columns]

    def run(self) -> BacktestResult:
        """
        Run backtest and return results.

        Returns:
            BacktestResult with trades, equity curve, and metrics
        """
        # Initialize broker
        broker = _Broker(self._data, self._cash, self._commission)

        # Initialize strategy
        strategy = self._strategy_class()
        strategy._set_broker(broker)
        strategy._set_data(self._data)

        # Precompute indicators
        strategy.init()

        # Event loop: iterate through each bar
        for i in range(len(self._data)):
            strategy._set_index(i)
            broker.next(i)

            # Execute strategy logic
            strategy.next()

        # Calculate final equity
        broker.next(len(self._data) - 1)

        # Create equity curve
        equity_series = pd.Series(broker.equity_curve, index=self._data.index)

        # Calculate metrics
        metrics = calculate_metrics(
            trades=broker.trades,
            equity_curve=equity_series,
            initial_capital=self._cash
        )

        # Create result
        result = BacktestResult(
            trades=broker.trades,
            equity_curve=equity_series,
            metrics=metrics,
            **metrics
        )

        return result

    def optimize(
        self,
        maximize: str = 'sharpe_ratio',
        method: str = 'grid',
        max_tries: int = None,
        **param_ranges
    ) -> BacktestResult:
        """
        Optimize strategy parameters.

        Args:
            maximize: Metric to optimize ('sharpe_ratio', 'total_return', etc.)
            method: Optimization method ('grid' or 'optuna')
            max_tries: Maximum iterations (for non-grid methods)
            **param_ranges: Parameter ranges (e.g., period=range(10, 50))

        Returns:
            BacktestResult with best parameters

        Example:
            best = bt.optimize(
                period=range(10, 50, 5),
                threshold=[0.01, 0.02, 0.05],
                maximize='sharpe_ratio'
            )
        """
        if method == 'grid':
            return self._optimize_grid(maximize, param_ranges)
        elif method == 'optuna':
            return self._optimize_optuna(maximize, max_tries, param_ranges)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _optimize_grid(self, maximize: str, param_ranges: Dict) -> BacktestResult:
        """Grid search optimization"""
        from itertools import product

        # Generate all combinations
        param_names = list(param_ranges.keys())
        param_values = [param_ranges[name] for name in param_names]
        combinations = list(product(*param_values))

        best_result = None
        best_value = -np.inf

        print(f"Testing {len(combinations)} combinations...")

        for i, params in enumerate(combinations):
            # Set parameters
            for name, value in zip(param_names, params):
                setattr(self._strategy_class, name, value)

            # Run backtest
            try:
                result = self.run()
                value = result.metrics.get(maximize, -np.inf)

                if value > best_value:
                    best_value = value
                    best_result = result
                    best_result._best_params = dict(zip(param_names, params))

                if (i + 1) % max(1, len(combinations) // 10) == 0:
                    print(f"Progress: {i+1}/{len(combinations)}")

            except Exception as e:
                print(f"Error with params {dict(zip(param_names, params))}: {e}")
                continue

        print(f"Best {maximize}: {best_value:.4f}")
        print(f"Best params: {best_result._best_params}")

        return best_result

    def _optimize_optuna(self, maximize: str, max_tries: int, param_ranges: Dict):
        """Bayesian optimization using Optuna"""
        try:
            import optuna
        except ImportError:
            raise ImportError("optuna not installed. Run: pip install optuna")

        def objective(trial):
            # Sample parameters
            params = {}
            for name, values in param_ranges.items():
                if isinstance(values, range):
                    params[name] = trial.suggest_int(name, min(values), max(values))
                elif isinstance(values, (list, tuple)):
                    params[name] = trial.suggest_categorical(name, values)
                else:
                    raise ValueError(f"Invalid parameter range for {name}")

            # Set parameters
            for name, value in params.items():
                setattr(self._strategy_class, name, value)

            # Run backtest
            result = self.run()
            return result.metrics.get(maximize, -np.inf)

        # Run optimization
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=max_tries or 100, show_progress_bar=True)

        # Get best result
        best_params = study.best_params
        for name, value in best_params.items():
            setattr(self._strategy_class, name, value)

        best_result = self.run()
        best_result._best_params = best_params

        print(f"Best {maximize}: {study.best_value:.4f}")
        print(f"Best params: {best_params}")

        return best_result
