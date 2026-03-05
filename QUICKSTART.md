# Quick Start Guide

Get started with OpenClaw Quant in 5 minutes!

## Installation

### 1. Install via ClawHub (Recommended)

```bash
clawhub install quant-analyst
```

### 2. Install from GitHub

```bash
# Clone repository
git clone https://github.com/ZhenRobotics/openclaw-quant-analyst.git
cd openclaw-quant-analyst

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Your First Backtest (3 minutes)

Create a file `my_first_backtest.py`:

```python
from openclaw_quant import Strategy, Backtest, get_data
from openclaw_quant.indicators import SMA

class SimpleStrategy(Strategy):
    """Buy when price crosses above MA, sell when crosses below"""

    def init(self):
        self.ma = self.I(SMA, self.data.Close, 20)

    def next(self):
        if self.data.Close[-1] > self.ma[-1]:
            if not self.position:
                self.buy()
        else:
            if self.position:
                self.sell()

# Fetch data
data = get_data('BTC/USDT', days=365)

# Run backtest
bt = Backtest(SimpleStrategy, data, cash=10000, commission=0.001)
result = bt.run()

# Show results
print(result)
result.plot()
```

Run it:

```bash
python my_first_backtest.py
```

## Next Steps

1. **Run Examples**:
   ```bash
   cd examples
   python backtest_ma_cross.py
   ```

2. **Read Documentation**: Check [README.md](README.md)

3. **Join Community**: [GitHub](https://github.com/ZhenRobotics/openclaw-quant-analyst)

Happy Trading! 🚀
