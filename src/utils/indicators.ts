/**
 * Technical Indicators Library
 * Common technical analysis indicators for trading strategies
 */

import { Candle } from '../types';

export class Indicators {
  /**
   * Simple Moving Average (SMA)
   */
  static sma(values: number[], period: number): number[] {
    const result: number[] = [];

    for (let i = 0; i < values.length; i++) {
      if (i < period - 1) {
        result.push(NaN);
        continue;
      }

      const sum = values.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }

    return result;
  }

  /**
   * Exponential Moving Average (EMA)
   */
  static ema(values: number[], period: number): number[] {
    const result: number[] = [];
    const multiplier = 2 / (period + 1);

    let ema = values.slice(0, period).reduce((a, b) => a + b, 0) / period;

    for (let i = 0; i < values.length; i++) {
      if (i < period - 1) {
        result.push(NaN);
      } else if (i === period - 1) {
        result.push(ema);
      } else {
        ema = (values[i] - ema) * multiplier + ema;
        result.push(ema);
      }
    }

    return result;
  }

  /**
   * Relative Strength Index (RSI)
   */
  static rsi(values: number[], period: number = 14): number[] {
    const result: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];

    for (let i = 1; i < values.length; i++) {
      const change = values[i] - values[i - 1];
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? -change : 0);
    }

    const avgGains = this.ema(gains, period);
    const avgLosses = this.ema(losses, period);

    result.push(NaN); // First value is always NaN

    for (let i = 0; i < avgGains.length; i++) {
      if (isNaN(avgGains[i]) || isNaN(avgLosses[i])) {
        result.push(NaN);
        continue;
      }

      const rs = avgGains[i] / avgLosses[i];
      const rsi = 100 - (100 / (1 + rs));
      result.push(rsi);
    }

    return result;
  }

  /**
   * Bollinger Bands
   */
  static bollingerBands(
    values: number[],
    period: number = 20,
    stdDev: number = 2
  ): { upper: number[]; middle: number[]; lower: number[] } {
    const middle = this.sma(values, period);
    const upper: number[] = [];
    const lower: number[] = [];

    for (let i = 0; i < values.length; i++) {
      if (i < period - 1) {
        upper.push(NaN);
        lower.push(NaN);
        continue;
      }

      const slice = values.slice(i - period + 1, i + 1);
      const mean = middle[i];
      const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
      const std = Math.sqrt(variance);

      upper.push(mean + std * stdDev);
      lower.push(mean - std * stdDev);
    }

    return { upper, middle, lower };
  }

  /**
   * Moving Average Convergence Divergence (MACD)
   */
  static macd(
    values: number[],
    fastPeriod: number = 12,
    slowPeriod: number = 26,
    signalPeriod: number = 9
  ): { macd: number[]; signal: number[]; histogram: number[] } {
    const fastEma = this.ema(values, fastPeriod);
    const slowEma = this.ema(values, slowPeriod);

    const macd = fastEma.map((fast, i) => fast - slowEma[i]);
    const signal = this.ema(macd.filter(v => !isNaN(v)), signalPeriod);

    // Pad signal array to match length
    const paddedSignal = new Array(macd.length - signal.length).fill(NaN).concat(signal);
    const histogram = macd.map((m, i) => m - paddedSignal[i]);

    return { macd, signal: paddedSignal, histogram };
  }

  /**
   * Average True Range (ATR)
   */
  static atr(candles: Candle[], period: number = 14): number[] {
    const trueRanges: number[] = [];

    for (let i = 1; i < candles.length; i++) {
      const high = candles[i].high;
      const low = candles[i].low;
      const prevClose = candles[i - 1].close;

      const tr = Math.max(
        high - low,
        Math.abs(high - prevClose),
        Math.abs(low - prevClose)
      );

      trueRanges.push(tr);
    }

    const atr = this.ema(trueRanges, period);
    return [NaN, ...atr]; // Add NaN for first candle
  }

  /**
   * Stochastic Oscillator
   */
  static stochastic(
    candles: Candle[],
    period: number = 14,
    kSmooth: number = 3,
    dSmooth: number = 3
  ): { k: number[]; d: number[] } {
    const k: number[] = [];

    for (let i = 0; i < candles.length; i++) {
      if (i < period - 1) {
        k.push(NaN);
        continue;
      }

      const slice = candles.slice(i - period + 1, i + 1);
      const high = Math.max(...slice.map(c => c.high));
      const low = Math.min(...slice.map(c => c.low));
      const close = candles[i].close;

      const stoch = ((close - low) / (high - low)) * 100;
      k.push(stoch);
    }

    const kSmoothed = this.sma(k.filter(v => !isNaN(v)), kSmooth);
    const d = this.sma(kSmoothed.filter(v => !isNaN(v)), dSmooth);

    // Pad arrays
    const paddedK = new Array(candles.length - kSmoothed.length).fill(NaN).concat(kSmoothed);
    const paddedD = new Array(candles.length - d.length).fill(NaN).concat(d);

    return { k: paddedK, d: paddedD };
  }

  /**
   * Volume Weighted Average Price (VWAP)
   */
  static vwap(candles: Candle[]): number[] {
    const result: number[] = [];
    let cumulativeTPV = 0;
    let cumulativeVolume = 0;

    for (const candle of candles) {
      const typicalPrice = (candle.high + candle.low + candle.close) / 3;
      cumulativeTPV += typicalPrice * candle.volume;
      cumulativeVolume += candle.volume;

      result.push(cumulativeTPV / cumulativeVolume);
    }

    return result;
  }

  /**
   * On-Balance Volume (OBV)
   */
  static obv(candles: Candle[]): number[] {
    const result: number[] = [0];

    for (let i = 1; i < candles.length; i++) {
      const prev = result[i - 1];
      const change = candles[i].close > candles[i - 1].close ? candles[i].volume :
                    candles[i].close < candles[i - 1].close ? -candles[i].volume : 0;
      result.push(prev + change);
    }

    return result;
  }

  /**
   * Helper: Get closes from candles
   */
  static getCloses(candles: Candle[]): number[] {
    return candles.map(c => c.close);
  }

  /**
   * Helper: Get highs from candles
   */
  static getHighs(candles: Candle[]): number[] {
    return candles.map(c => c.high);
  }

  /**
   * Helper: Get lows from candles
   */
  static getLows(candles: Candle[]): number[] {
    return candles.map(c => c.low);
  }

  /**
   * Helper: Get volumes from candles
   */
  static getVolumes(candles: Candle[]): number[] {
    return candles.map(c => c.volume);
  }
}
