"""
Technical Indicators Library

Provides common technical analysis indicators using pandas/numpy.
Optimized for vectorized operations.
"""

import numpy as np
import pandas as pd
from typing import Union


def SMA(series: Union[pd.Series, np.ndarray], period: int) -> pd.Series:
    """Simple Moving Average"""
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
    return series.rolling(window=period).mean()


def EMA(series: Union[pd.Series, np.ndarray], period: int) -> pd.Series:
    """Exponential Moving Average"""
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
    return series.ewm(span=period, adjust=False).mean()


def RSI(series: Union[pd.Series, np.ndarray], period: int = 14) -> pd.Series:
    """
    Relative Strength Index

    Args:
        series: Price series
        period: RSI period (default: 14)

    Returns:
        RSI values (0-100)
    """
    if isinstance(series, np.ndarray):
        series = pd.Series(series)

    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def MACD(series: Union[pd.Series, np.ndarray],
         fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Moving Average Convergence Divergence

    Returns:
        DataFrame with 'macd', 'signal', and 'histogram' columns
    """
    if isinstance(series, np.ndarray):
        series = pd.Series(series)

    ema_fast = EMA(series, fast)
    ema_slow = EMA(series, slow)

    macd_line = ema_fast - ema_slow
    signal_line = EMA(macd_line, signal)
    histogram = macd_line - signal_line

    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })


def BollingerBands(series: Union[pd.Series, np.ndarray],
                   period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Bollinger Bands

    Returns:
        DataFrame with 'upper', 'middle', and 'lower' columns
    """
    if isinstance(series, np.ndarray):
        series = pd.Series(series)

    middle = SMA(series, period)
    std = series.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return pd.DataFrame({
        'upper': upper,
        'middle': middle,
        'lower': lower
    })


def ATR(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Average True Range

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period

    Returns:
        ATR values
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    return atr


def Stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
               period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> pd.DataFrame:
    """
    Stochastic Oscillator

    Returns:
        DataFrame with '%K' and '%D' columns
    """
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()

    k_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    k = k_raw.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()

    return pd.DataFrame({
        '%K': k,
        '%D': d
    })


def ADX(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average Directional Index"""
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr = ATR(high, low, close, 1)

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return adx


def OBV(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume"""
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def VWAP(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Volume Weighted Average Price"""
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap


def ROC(series: Union[pd.Series, np.ndarray], period: int = 12) -> pd.Series:
    """Rate of Change"""
    if isinstance(series, np.ndarray):
        series = pd.Series(series)

    roc = ((series - series.shift(period)) / series.shift(period)) * 100
    return roc


def CCI(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """Commodity Channel Index"""
    typical_price = (high + low + close) / 3
    sma_tp = typical_price.rolling(window=period).mean()
    mean_deviation = typical_price.rolling(window=period).apply(
        lambda x: np.abs(x - x.mean()).mean()
    )

    cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
    return cci


def WilliamsR(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Williams %R"""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
    return williams_r


# Convenience functions for strategy use
def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Detect crossover (series1 crosses above series2)"""
    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Detect crossunder (series1 crosses below series2)"""
    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))


__all__ = [
    'SMA', 'EMA', 'RSI', 'MACD', 'BollingerBands',
    'ATR', 'Stochastic', 'ADX', 'OBV', 'VWAP',
    'ROC', 'CCI', 'WilliamsR',
    'crossover', 'crossunder'
]
