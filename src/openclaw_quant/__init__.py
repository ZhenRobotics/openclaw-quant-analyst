"""
OpenClaw Quant - Professional Quantitative Trading System

A professional quantitative trading system for cryptocurrency markets.
Features backtesting, paper trading, live trading, and strategy optimization.
"""

__version__ = "0.1.0"
__author__ = "ZhenStaff"
__license__ = "MIT"

from .strategy import Strategy
from .backtest import Backtest
from .data import DataFetcher, get_data
from .types import Trade, Position, BacktestResult

# Import all indicators
from .indicators import (
    SMA, EMA, RSI, MACD, BollingerBands,
    ATR, Stochastic, ADX, OBV, VWAP,
    ROC, CCI, WilliamsR,
    crossover, crossunder
)

__all__ = [
    # Core classes
    "Strategy",
    "Backtest",
    "DataFetcher",
    "get_data",

    # Types
    "Trade",
    "Position",
    "BacktestResult",

    # Indicators
    "SMA", "EMA", "RSI", "MACD", "BollingerBands",
    "ATR", "Stochastic", "ADX", "OBV", "VWAP",
    "ROC", "CCI", "WilliamsR",
    "crossover", "crossunder",
]
