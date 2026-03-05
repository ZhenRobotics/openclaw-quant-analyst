"""
Performance Metrics Calculation

Calculate comprehensive trading performance metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from .types import Trade


def calculate_metrics(
    trades: List[Trade],
    equity_curve: pd.Series,
    initial_capital: float
) -> Dict[str, float]:
    """
    Calculate comprehensive performance metrics.

    Args:
        trades: List of executed trades
        equity_curve: Equity over time
        initial_capital: Starting capital

    Returns:
        Dictionary of metrics
    """
    if len(trades) == 0 or len(equity_curve) == 0:
        return _empty_metrics()

    final_capital = equity_curve.iloc[-1]

    # Basic metrics
    total_return = final_capital - initial_capital
    total_return_pct = (total_return / initial_capital) * 100

    # Trade statistics
    buy_trades = [t for t in trades if t.side == 'buy']
    sell_trades = [t for t in trades if t.side == 'sell']

    # Match buy/sell pairs to calculate PnL
    trade_pnls = []
    for i in range(min(len(buy_trades), len(sell_trades))):
        buy = buy_trades[i]
        sell = sell_trades[i]
        pnl = (sell.price - buy.price) * buy.size - buy.fee - sell.fee
        trade_pnls.append(pnl)

    num_trades = len(trade_pnls)
    num_winning = sum(1 for pnl in trade_pnls if pnl > 0)
    num_losing = sum(1 for pnl in trade_pnls if pnl < 0)
    win_rate = (num_winning / num_trades * 100) if num_trades > 0 else 0.0

    # Win/Loss statistics
    winning_trades = [pnl for pnl in trade_pnls if pnl > 0]
    losing_trades = [pnl for pnl in trade_pnls if pnl < 0]

    avg_win = np.mean(winning_trades) if winning_trades else 0.0
    avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0.0
    avg_trade = np.mean(trade_pnls) if trade_pnls else 0.0

    # Profit factor
    gross_profit = sum(winning_trades) if winning_trades else 0.0
    gross_loss = abs(sum(losing_trades)) if losing_trades else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0

    # Drawdown metrics
    max_drawdown, max_drawdown_pct = calculate_max_drawdown(equity_curve)

    # Risk-adjusted metrics
    sharpe_ratio = calculate_sharpe_ratio(equity_curve)
    sortino_ratio = calculate_sortino_ratio(equity_curve)

    return {
        'initial_capital': initial_capital,
        'final_capital': final_capital,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'num_trades': num_trades,
        'num_winning': num_winning,
        'num_losing': num_losing,
        'win_rate': win_rate,
        'avg_trade': avg_trade,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown_pct,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
    }


def calculate_max_drawdown(equity: pd.Series) -> tuple[float, float]:
    """
    Calculate maximum drawdown.

    Returns:
        (absolute_drawdown, percentage_drawdown)
    """
    if len(equity) == 0:
        return 0.0, 0.0

    cummax = equity.cummax()
    drawdown = equity - cummax
    drawdown_pct = (drawdown / cummax) * 100

    max_dd = abs(drawdown.min())
    max_dd_pct = abs(drawdown_pct.min())

    return max_dd, max_dd_pct


def calculate_sharpe_ratio(equity: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        equity: Equity curve
        risk_free_rate: Risk-free rate (annual)

    Returns:
        Sharpe ratio
    """
    if len(equity) < 2:
        return 0.0

    # Calculate returns
    returns = equity.pct_change().dropna()

    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    # Annualize (assume daily data)
    mean_return = returns.mean() * 252  # Annualized
    std_return = returns.std() * np.sqrt(252)  # Annualized

    sharpe = (mean_return - risk_free_rate) / std_return

    return sharpe


def calculate_sortino_ratio(equity: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sortino ratio (only penalize downside volatility).

    Args:
        equity: Equity curve
        risk_free_rate: Risk-free rate (annual)

    Returns:
        Sortino ratio
    """
    if len(equity) < 2:
        return 0.0

    # Calculate returns
    returns = equity.pct_change().dropna()

    if len(returns) == 0:
        return 0.0

    # Downside returns only
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    # Annualize
    mean_return = returns.mean() * 252
    downside_std = downside_returns.std() * np.sqrt(252)

    sortino = (mean_return - risk_free_rate) / downside_std

    return sortino


def calculate_calmar_ratio(total_return: float, max_drawdown_pct: float) -> float:
    """
    Calculate Calmar ratio (return / max drawdown).

    Returns:
        Calmar ratio
    """
    if max_drawdown_pct == 0:
        return 0.0

    return total_return / max_drawdown_pct


def _empty_metrics() -> Dict[str, float]:
    """Return empty metrics dict"""
    return {
        'initial_capital': 0.0,
        'final_capital': 0.0,
        'total_return': 0.0,
        'total_return_pct': 0.0,
        'num_trades': 0,
        'num_winning': 0,
        'num_losing': 0,
        'win_rate': 0.0,
        'avg_trade': 0.0,
        'avg_win': 0.0,
        'avg_loss': 0.0,
        'profit_factor': 0.0,
        'max_drawdown': 0.0,
        'max_drawdown_pct': 0.0,
        'sharpe_ratio': 0.0,
        'sortino_ratio': 0.0,
    }


def format_metrics(metrics: Dict[str, float]) -> str:
    """Format metrics for display"""
    return f"""
Performance Metrics
==================
Total Return:     ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)
Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}
Sortino Ratio:    {metrics['sortino_ratio']:.2f}
Max Drawdown:     {metrics['max_drawdown_pct']:.2f}%

Trade Statistics
================
Total Trades:     {metrics['num_trades']}
Winning:          {metrics['num_winning']} ({metrics['win_rate']:.1f}%)
Losing:           {metrics['num_losing']}
Profit Factor:    {metrics['profit_factor']:.2f}
Avg Trade:        ${metrics['avg_trade']:.2f}
Avg Win:          ${metrics['avg_win']:.2f}
Avg Loss:         ${metrics['avg_loss']:.2f}
"""
