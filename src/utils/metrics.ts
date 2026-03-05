/**
 * Performance Metrics Calculator
 * Calculate trading strategy performance metrics
 */

import { Trade, PerformanceMetrics } from '../types';

export class Metrics {
  /**
   * Calculate comprehensive performance metrics
   */
  static calculateMetrics(
    trades: Trade[],
    equity: { timestamp: number; value: number }[],
    initialCapital: number
  ): PerformanceMetrics {
    if (trades.length === 0 || equity.length === 0) {
      return this.getEmptyMetrics();
    }

    const finalCapital = equity[equity.length - 1].value;
    const totalReturn = (finalCapital - initialCapital) / initialCapital;

    // Calculate returns for each equity point
    const returns = equity.slice(1).map((point, i) =>
      (point.value - equity[i].value) / equity[i].value
    );

    // Separate winning and losing trades
    const { wins, losses } = this.separateTrades(trades);

    // Calculate time-based metrics
    const durationDays = (equity[equity.length - 1].timestamp - equity[0].timestamp) / (1000 * 60 * 60 * 24);
    const annualizedReturn = durationDays > 0 ?
      Math.pow(1 + totalReturn, 365 / durationDays) - 1 : 0;

    return {
      totalReturn: totalReturn * 100,
      annualizedReturn: annualizedReturn * 100,
      sharpeRatio: this.calculateSharpeRatio(returns, annualizedReturn),
      sortinoRatio: this.calculateSortinoRatio(returns, annualizedReturn),
      maxDrawdown: this.calculateMaxDrawdown(equity) * 100,
      winRate: this.calculateWinRate(trades) * 100,
      profitFactor: this.calculateProfitFactor(wins, losses),
      calmarRatio: this.calculateCalmarRatio(annualizedReturn, this.calculateMaxDrawdown(equity)),
      recoveryFactor: this.calculateRecoveryFactor(totalReturn, this.calculateMaxDrawdown(equity)),
      averageWin: this.calculateAverageWin(wins),
      averageLoss: this.calculateAverageLoss(losses),
      largestWin: this.calculateLargestWin(wins),
      largestLoss: this.calculateLargestLoss(losses),
      averageTradeDuration: this.calculateAverageTradeDuration(trades),
      expectancy: this.calculateExpectancy(wins, losses, trades.length),
    };
  }

  private static getEmptyMetrics(): PerformanceMetrics {
    return {
      totalReturn: 0,
      annualizedReturn: 0,
      sharpeRatio: 0,
      sortinoRatio: 0,
      maxDrawdown: 0,
      winRate: 0,
      profitFactor: 0,
      calmarRatio: 0,
      recoveryFactor: 0,
      averageWin: 0,
      averageLoss: 0,
      largestWin: 0,
      largestLoss: 0,
      averageTradeDuration: 0,
      expectancy: 0,
    };
  }

  private static separateTrades(trades: Trade[]): { wins: Trade[]; losses: Trade[] } {
    const wins: Trade[] = [];
    const losses: Trade[] = [];

    // Group trades into buy-sell pairs
    const pairs: [Trade, Trade][] = [];
    for (let i = 0; i < trades.length - 1; i += 2) {
      if (trades[i].side === 'buy' && trades[i + 1].side === 'sell') {
        pairs.push([trades[i], trades[i + 1]]);
      }
    }

    pairs.forEach(([buy, sell]) => {
      const pnl = (sell.price - buy.price) * buy.quantity - buy.fee - sell.fee;
      if (pnl > 0) {
        wins.push(sell);
      } else {
        losses.push(sell);
      }
    });

    return { wins, losses };
  }

  private static calculateWinRate(trades: Trade[]): number {
    if (trades.length < 2) return 0;

    const { wins } = this.separateTrades(trades);
    const totalPairs = Math.floor(trades.length / 2);

    return totalPairs > 0 ? wins.length / totalPairs : 0;
  }

  private static calculateProfitFactor(wins: Trade[], losses: Trade[]): number {
    if (losses.length === 0) return wins.length > 0 ? Infinity : 0;

    const grossProfit = wins.reduce((sum, trade) => sum + (trade.price * trade.quantity), 0);
    const grossLoss = losses.reduce((sum, trade) => sum + (trade.price * trade.quantity), 0);

    return grossLoss > 0 ? grossProfit / grossLoss : 0;
  }

  private static calculateSharpeRatio(returns: number[], annualizedReturn: number): number {
    if (returns.length === 0) return 0;

    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);

    // Annualize the standard deviation
    const annualizedStdDev = stdDev * Math.sqrt(252); // 252 trading days

    return annualizedStdDev !== 0 ? annualizedReturn / annualizedStdDev : 0;
  }

  private static calculateSortinoRatio(returns: number[], annualizedReturn: number): number {
    if (returns.length === 0) return 0;

    const negativeReturns = returns.filter(r => r < 0);
    if (negativeReturns.length === 0) return annualizedReturn > 0 ? Infinity : 0;

    const avgNegReturn = negativeReturns.reduce((a, b) => a + b, 0) / negativeReturns.length;
    const downVariance = negativeReturns.reduce((sum, r) => sum + Math.pow(r - avgNegReturn, 2), 0) / negativeReturns.length;
    const downStdDev = Math.sqrt(downVariance);

    const annualizedDownStdDev = downStdDev * Math.sqrt(252);

    return annualizedDownStdDev !== 0 ? annualizedReturn / annualizedDownStdDev : 0;
  }

  private static calculateMaxDrawdown(equity: { timestamp: number; value: number }[]): number {
    let maxDrawdown = 0;
    let peak = equity[0].value;

    for (const point of equity) {
      if (point.value > peak) {
        peak = point.value;
      }

      const drawdown = (peak - point.value) / peak;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    }

    return maxDrawdown;
  }

  private static calculateCalmarRatio(annualizedReturn: number, maxDrawdown: number): number {
    return maxDrawdown !== 0 ? annualizedReturn / maxDrawdown : 0;
  }

  private static calculateRecoveryFactor(totalReturn: number, maxDrawdown: number): number {
    return maxDrawdown !== 0 ? totalReturn / maxDrawdown : 0;
  }

  private static calculateAverageWin(wins: Trade[]): number {
    if (wins.length === 0) return 0;
    return wins.reduce((sum, trade) => sum + (trade.price * trade.quantity - trade.fee), 0) / wins.length;
  }

  private static calculateAverageLoss(losses: Trade[]): number {
    if (losses.length === 0) return 0;
    return losses.reduce((sum, trade) => sum + (trade.price * trade.quantity + trade.fee), 0) / losses.length;
  }

  private static calculateLargestWin(wins: Trade[]): number {
    if (wins.length === 0) return 0;
    return Math.max(...wins.map(trade => trade.price * trade.quantity - trade.fee));
  }

  private static calculateLargestLoss(losses: Trade[]): number {
    if (losses.length === 0) return 0;
    return Math.min(...losses.map(trade => -(trade.price * trade.quantity + trade.fee)));
  }

  private static calculateAverageTradeDuration(trades: Trade[]): number {
    if (trades.length < 2) return 0;

    let totalDuration = 0;
    let count = 0;

    for (let i = 0; i < trades.length - 1; i += 2) {
      if (trades[i].side === 'buy' && trades[i + 1].side === 'sell') {
        totalDuration += (trades[i + 1].timestamp - trades[i].timestamp);
        count++;
      }
    }

    // Return in hours
    return count > 0 ? totalDuration / count / (1000 * 60 * 60) : 0;
  }

  private static calculateExpectancy(wins: Trade[], losses: Trade[], totalTrades: number): number {
    if (totalTrades === 0) return 0;

    const winRate = wins.length / totalTrades;
    const lossRate = losses.length / totalTrades;

    const avgWin = this.calculateAverageWin(wins);
    const avgLoss = Math.abs(this.calculateAverageLoss(losses));

    return (winRate * avgWin) - (lossRate * avgLoss);
  }

  /**
   * Format metrics for display
   */
  static formatMetrics(metrics: PerformanceMetrics): Record<string, string> {
    return {
      'Total Return': `${metrics.totalReturn.toFixed(2)}%`,
      'Annualized Return': `${metrics.annualizedReturn.toFixed(2)}%`,
      'Sharpe Ratio': metrics.sharpeRatio.toFixed(2),
      'Sortino Ratio': metrics.sortinoRatio.toFixed(2),
      'Max Drawdown': `${metrics.maxDrawdown.toFixed(2)}%`,
      'Win Rate': `${metrics.winRate.toFixed(2)}%`,
      'Profit Factor': metrics.profitFactor.toFixed(2),
      'Calmar Ratio': metrics.calmarRatio.toFixed(2),
      'Recovery Factor': metrics.recoveryFactor.toFixed(2),
      'Average Win': `$${metrics.averageWin.toFixed(2)}`,
      'Average Loss': `$${metrics.averageLoss.toFixed(2)}`,
      'Largest Win': `$${metrics.largestWin.toFixed(2)}`,
      'Largest Loss': `$${metrics.largestLoss.toFixed(2)}`,
      'Avg Trade Duration': `${metrics.averageTradeDuration.toFixed(2)}h`,
      'Expectancy': `$${metrics.expectancy.toFixed(2)}`,
    };
  }
}
