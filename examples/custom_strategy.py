"""
Example: Custom Multi-Indicator Strategy

This example demonstrates:
1. Using multiple indicators
2. Combining different signals
3. Position sizing and risk management
"""

import sys
sys.path.insert(0, '../src')

from openclaw_quant import Strategy, Backtest, get_data
from openclaw_quant.indicators import RSI, MACD, BollingerBands


class MultiIndicatorStrategy(Strategy):
    """
    Multi-Indicator Strategy

    Entry Rules:
    - RSI < 40 (oversold)
    - MACD histogram positive
    - Price touches lower Bollinger Band

    Exit Rules:
    - RSI > 60 (overbought)
    - Or price touches upper Bollinger Band
    """

    # Parameters
    rsi_period = 14
    rsi_oversold = 40
    rsi_overbought = 60
    bb_period = 20
    bb_std = 2.0

    def init(self):
        """Initialize indicators"""
        # RSI
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)

        # MACD
        macd_df = self.I(MACD, self.data.Close)
        self.macd_hist = macd_df['histogram']

        # Bollinger Bands
        bb_df = self.I(BollingerBands, self.data.Close, self.bb_period, self.bb_std)
        self.bb_upper = bb_df['upper']
        self.bb_lower = bb_df['lower']

    def next(self):
        """Execute strategy logic"""
        current_price = self.data.Close[-1]
        current_rsi = self.rsi[-1]
        current_macd_hist = self.macd_hist[-1]

        # Entry signal
        if not self.position:
            # Check all conditions
            rsi_oversold = current_rsi < self.rsi_oversold
            macd_positive = current_macd_hist > 0
            at_lower_band = current_price <= self.bb_lower[-1] * 1.01  # 1% tolerance

            if rsi_oversold and macd_positive and at_lower_band:
                self.buy(size=0.95)  # Use 95% of capital

        # Exit signal
        else:
            rsi_overbought = current_rsi > self.rsi_overbought
            at_upper_band = current_price >= self.bb_upper[-1] * 0.99

            if rsi_overbought or at_upper_band:
                self.sell()


def main():
    print("=" * 60)
    print("Multi-Indicator Strategy Backtest")
    print("=" * 60)

    # Fetch data
    print("\n📊 Fetching BTC/USDT data...")
    data = get_data(
        symbol='BTC/USDT',
        exchange='binance',
        timeframe='4h',
        days=90
    )
    print(f"✓ Loaded {len(data)} candles")

    # Run backtest
    print("\n🔄 Running backtest...")
    bt = Backtest(
        MultiIndicatorStrategy,
        data,
        cash=10000,
        commission=0.001
    )
    result = bt.run()

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\n💰 Performance:")
    print(f"  Total Return:     {result.total_return_pct:+.2f}%")
    print(f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}")
    print(f"  Max Drawdown:     {result.max_drawdown_pct:.2f}%")

    print(f"\n📊 Trade Analysis:")
    print(f"  Total Trades:     {result.num_trades}")
    print(f"  Win Rate:         {result.win_rate:.2f}%")
    print(f"  Profit Factor:    {result.profit_factor:.2f}")

    print(f"\n📝 Trade Details:")
    for i, trade in enumerate(result.trades[:10], 1):  # Show first 10 trades
        print(f"  {i}. {trade}")

    # Plot
    result.plot()

    print("\n✓ Done!")


if __name__ == '__main__':
    main()
