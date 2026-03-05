"""
Core type definitions for OpenClaw Quant
"""

from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class Trade:
    """Represents a completed trade"""
    timestamp: datetime
    price: float
    size: float
    side: str  # 'buy' or 'sell'
    fee: float = 0.0
    pnl: float = 0.0

    def __repr__(self):
        return f"Trade({self.side.upper()} {self.size:.4f} @ {self.price:.2f})"


@dataclass
class Position:
    """Current position state"""
    size: float = 0.0
    entry_price: float = 0.0
    entry_time: Optional[datetime] = None

    @property
    def is_long(self) -> bool:
        return self.size > 0

    @property
    def is_short(self) -> bool:
        return self.size < 0

    @property
    def is_flat(self) -> bool:
        return self.size == 0

    def pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL"""
        if self.is_flat:
            return 0.0
        return (current_price - self.entry_price) * self.size


@dataclass
class Order:
    """Order to be executed"""
    size: float  # positive for buy, negative for sell
    limit: Optional[float] = None  # None for market order
    stop: Optional[float] = None   # stop loss
    take_profit: Optional[float] = None

    @property
    def is_buy(self) -> bool:
        return self.size > 0

    @property
    def is_sell(self) -> bool:
        return self.size < 0


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    trades: List[Trade]
    equity_curve: pd.Series
    metrics: Dict[str, float]

    # Performance metrics
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float

    # Trade statistics
    num_trades: int
    num_winning: int
    num_losing: int
    win_rate: float

    # Risk metrics
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float

    # Additional metrics
    profit_factor: float
    avg_trade: float
    avg_win: float
    avg_loss: float

    def __repr__(self):
        return (
            f"BacktestResult(\n"
            f"  Total Return: {self.total_return_pct:.2f}%\n"
            f"  Sharpe Ratio: {self.sharpe_ratio:.2f}\n"
            f"  Max Drawdown: {self.max_drawdown_pct:.2f}%\n"
            f"  Win Rate: {self.win_rate:.2f}%\n"
            f"  Trades: {self.num_trades}\n"
            f")"
        )

    def plot(self, show: bool = True):
        """Plot equity curve and drawdown"""
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Equity curve
        self.equity_curve.plot(ax=ax1, label='Equity')
        ax1.set_ylabel('Equity ($)')
        ax1.set_title('Backtest Results')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Drawdown
        drawdown = (self.equity_curve / self.equity_curve.cummax() - 1) * 100
        drawdown.plot(ax=ax2, color='red', label='Drawdown')
        ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        if show:
            plt.show()

        return fig


@dataclass
class OptimizationResult:
    """Results from parameter optimization"""
    best_params: Dict[str, Any]
    best_value: float
    all_results: pd.DataFrame
    optimization_time: float

    def __repr__(self):
        return (
            f"OptimizationResult(\n"
            f"  Best Value: {self.best_value:.4f}\n"
            f"  Best Params: {self.best_params}\n"
            f"  Total Trials: {len(self.all_results)}\n"
            f"  Time: {self.optimization_time:.2f}s\n"
            f")"
        )
