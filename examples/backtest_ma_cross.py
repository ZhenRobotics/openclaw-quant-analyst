"""
Example: Moving Average Crossover Strategy Backtest

This example demonstrates:
1. Defining a simple strategy
2. Fetching historical data
3. Running a backtest
4. Analyzing results
"""

import sys
sys.path.insert(0, '../src')

from openclaw_quant import Strategy, Backtest, get_data
from openclaw_quant.indicators import SMA


class MACrossStrategy(Strategy):
    """Moving Average Crossover Strategy"""

    # Parameters (can be optimized)
    fast_period = 10
    slow_period = 30

    def init(self):
        """Precompute indicators"""
        self.fast_ma = self.I(SMA, self.data.Close, self.fast_period)
        self.slow_ma = self.I(SMA, self.data.Close, self.slow_period)

    def next(self):
        """Execute strategy logic on each bar"""
        # Golden cross: fast MA crosses above slow MA
        if self.fast_ma[-1] > self.slow_ma[-1]:
            if not self.position:
                self.buy()

        # Death cross: fast MA crosses below slow MA
        elif self.fast_ma[-1] < self.slow_ma[-1]:
            if self.position:
                self.sell()


def main():
    print("=" * 60)
    print("Moving Average Crossover Strategy Backtest")
    print("=" * 60)

    # Fetch data
    print("\n📊 Fetching BTC/USDT data (last 365 days)...")
    data = get_data(
        symbol='BTC/USDT',
        exchange='binance',
        timeframe='1d',
        days=365
    )
    print(f"✓ Loaded {len(data)} candles")
    print(f"  Period: {data.index[0]} to {data.index[-1]}")

    # Run backtest
    print("\n🔄 Running backtest...")
    bt = Backtest(
        MACrossStrategy,
        data,
        cash=10000,
        commission=0.001  # 0.1% commission
    )
    result = bt.run()

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\n💰 Returns:")
    print(f"  Initial Capital:  ${result.initial_capital:,.2f}")
    print(f"  Final Capital:    ${result.final_capital:,.2f}")
    print(f"  Total Return:     ${result.total_return:,.2f} ({result.total_return_pct:+.2f}%)")

    print(f"\n📈 Risk Metrics:")
    print(f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio:    {result.sortino_ratio:.2f}")
    print(f"  Max Drawdown:     {result.max_drawdown_pct:.2f}%")

    print(f"\n📊 Trade Statistics:")
    print(f"  Total Trades:     {result.num_trades}")
    print(f"  Winning Trades:   {result.num_winning}")
    print(f"  Losing Trades:    {result.num_losing}")
    print(f"  Win Rate:         {result.win_rate:.2f}%")
    print(f"  Profit Factor:    {result.profit_factor:.2f}")
    print(f"  Avg Trade:        ${result.avg_trade:.2f}")

    # Plot results
    print("\n📉 Plotting equity curve...")
    result.plot()

    print("\n✓ Done!")


if __name__ == '__main__':
    main()
