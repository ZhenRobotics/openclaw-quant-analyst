# OpenClaw Quant Examples

This directory contains example scripts demonstrating various features of the OpenClaw Quant system.

## Running Examples

```bash
cd examples
python backtest_ma_cross.py
python optimize_rsi.py
python custom_strategy.py
```

## Examples

### 1. backtest_ma_cross.py
**Moving Average Crossover Strategy**
- Simple two-MA crossover
- Fetches BTC/USDT data
- Displays performance metrics
- Plots equity curve

**Learn:**
- Basic strategy structure
- Data fetching
- Running backtests
- Analyzing results

### 2. optimize_rsi.py
**RSI Strategy with Optimization**
- RSI mean reversion
- Grid search optimization
- Parameter tuning
- Performance comparison

**Learn:**
- Parameter optimization
- Grid search
- Finding best parameters
- Comparing strategies

### 3. custom_strategy.py
**Multi-Indicator Strategy**
- Combines RSI, MACD, Bollinger Bands
- Multiple entry conditions
- Position sizing
- Advanced exit logic

**Learn:**
- Using multiple indicators
- Complex signal logic
- Risk management
- Position sizing

## Quick Start Template

```python
from openclaw_quant import Strategy, Backtest, get_data
from openclaw_quant.indicators import SMA, RSI

class MyStrategy(Strategy):
    # Parameters
    period = 20

    def init(self):
        # Precompute indicators
        self.ma = self.I(SMA, self.data.Close, self.period)

    def next(self):
        # Strategy logic
        if self.data.Close[-1] < self.ma[-1]:
            if not self.position:
                self.buy()
        else:
            if self.position:
                self.sell()

# Fetch data
data = get_data('BTC/USDT', days=365)

# Run backtest
bt = Backtest(MyStrategy, data, cash=10000)
result = bt.run()

# Show results
print(result)
result.plot()
```

## Common Patterns

### Data Fetching

```python
# From exchange
data = get_data('BTC/USDT', exchange='binance', timeframe='1h', days=30)

# From CSV
from openclaw_quant import DataFetcher
data = DataFetcher.from_csv('mydata.csv')
```

### Indicators

```python
# In init()
self.sma = self.I(SMA, self.data.Close, 20)
self.rsi = self.I(RSI, self.data.Close, 14)
macd_df = self.I(MACD, self.data.Close)
self.macd_signal = macd_df['signal']

# In next()
current_value = self.sma[-1]
previous_value = self.sma[-2]
```

### Trading

```python
# Market orders
self.buy()              # Buy with all capital
self.buy(size=0.5)      # Buy with 50% of capital
self.sell()             # Sell entire position

# Limit orders
self.buy(limit=50000)   # Buy if price drops to 50000
```

### Optimization

```python
# Grid search
result = bt.optimize(
    period=range(10, 50, 5),
    threshold=[0.01, 0.02, 0.05],
    maximize='sharpe_ratio'
)

# Bayesian (requires optuna)
result = bt.optimize(
    period=range(10, 100),
    maximize='sharpe_ratio',
    method='optuna',
    max_tries=100
)
```

## Tips

1. **Start Simple**: Begin with basic strategies before adding complexity
2. **Validate Data**: Always check data quality before backtesting
3. **Avoid Overfitting**: Don't optimize on the same data you backtest on
4. **Commission Matters**: Always include realistic commissions
5. **Walk-Forward**: Use out-of-sample testing to validate strategies

## Need Help?

- Read the [API Documentation](../docs/API.md)
- Check [Common Issues](../docs/FAQ.md)
- Visit [GitHub Issues](https://github.com/ZhenRobotics/openclaw-quant-analyst/issues)
