"""
Example: RSI Strategy with Parameter Optimization

This example demonstrates:
1. RSI mean reversion strategy
2. Parameter optimization (grid search)
3. Finding optimal RSI thresholds
"""

import sys
sys.path.insert(0, '../src')

from openclaw_quant import Strategy, Backtest, get_data
from openclaw_quant.indicators import RSI


class RSIStrategy(Strategy):
    """RSI Mean Reversion Strategy"""

    # Parameters to optimize
    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        """Precompute RSI indicator"""
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)

    def next(self):
        """Execute strategy logic"""
        current_rsi = self.rsi[-1]

        # Buy when oversold
        if current_rsi < self.oversold:
            if not self.position:
                self.buy()

        # Sell when overbought
        elif current_rsi > self.overbought:
            if self.position:
                self.sell()


def main():
    print("=" * 60)
    print("RSI Strategy Parameter Optimization")
    print("=" * 60)

    # Fetch data
    print("\n📊 Fetching ETH/USDT data (last 180 days)...")
    data = get_data(
        symbol='ETH/USDT',
        exchange='binance',
        timeframe='4h',
        days=180
    )
    print(f"✓ Loaded {len(data)} candles")

    # Create backtest instance
    bt = Backtest(RSIStrategy, data, cash=10000, commission=0.001)

    # Test default parameters
    print("\n🔄 Testing default parameters...")
    result_default = bt.run()
    print(f"  Default Sharpe Ratio: {result_default.sharpe_ratio:.2f}")

    # Optimize parameters
    print("\n🔍 Optimizing parameters...")
    print("  Testing RSI periods: 10-20")
    print("  Testing oversold levels: 20-40")
    print("  Testing overbought levels: 60-80")

    result_optimized = bt.optimize(
        rsi_period=range(10, 21, 2),
        oversold=range(20, 41, 5),
        overbought=range(60, 81, 5),
        maximize='sharpe_ratio'
    )

    # Display results
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)

    print(f"\n🎯 Best Parameters:")
    print(f"  RSI Period:       {result_optimized._best_params['rsi_period']}")
    print(f"  Oversold:         {result_optimized._best_params['oversold']}")
    print(f"  Overbought:       {result_optimized._best_params['overbought']}")

    print(f"\n📊 Performance Comparison:")
    print(f"  Default Sharpe:   {result_default.sharpe_ratio:.2f}")
    print(f"  Optimized Sharpe: {result_optimized.sharpe_ratio:.2f}")
    print(f"  Improvement:      {(result_optimized.sharpe_ratio - result_default.sharpe_ratio):.2f}")

    print(f"\n💰 Returns:")
    print(f"  Default Return:   {result_default.total_return_pct:+.2f}%")
    print(f"  Optimized Return: {result_optimized.total_return_pct:+.2f}%")

    # Plot optimized strategy
    print("\n📉 Plotting optimized strategy...")
    result_optimized.plot()

    print("\n✓ Optimization complete!")


if __name__ == '__main__':
    main()
