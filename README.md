# OpenClaw Quant

Professional quantitative trading system for cryptocurrency markets.

## Features

- **Backtesting**: Test strategies on historical data
- **Paper Trading**: Real-time simulation with live data
- **Live Trading**: Automated trading on real exchanges
- **Optimization**: Bayesian parameter optimization
- **50+ Indicators**: MA, RSI, MACD, Bollinger, ATR, etc.
- **Risk Management**: Position sizing, stop-loss, take-profit
- **Multi-Exchange**: Binance, OKX, Bybit, etc. (via ccxt)

## Quick Start

```bash
# Clone repository
git clone https://github.com/ZhenRobotics/openclaw-quant.git
cd openclaw-quant

# Install dependencies
pip install -r requirements.txt

# Run example
python examples/backtest_example.py
```

## Example Strategy

```python
from openclaw_quant import Strategy, Backtest

class MAStrategy(Strategy):
    fast_period = 10
    slow_period = 30

    def init(self):
        self.fast_ma = self.I(SMA, self.data.Close, self.fast_period)
        self.slow_ma = self.I(SMA, self.data.Close, self.slow_period)

    def next(self):
        if self.fast_ma[-1] > self.slow_ma[-1]:
            if not self.position:
                self.buy()
        else:
            if self.position:
                self.sell()

# Backtest
bt = Backtest(MAStrategy, data, cash=10000, commission=0.001)
result = bt.run()
result.plot()
```

## OpenClaw Skill

This project is available as an OpenClaw Skill:

```bash
clawhub install openclaw-quant
```

See [openclaw-skill/SKILL.md](openclaw-skill/SKILL.md) for full documentation.

## Documentation

- [Quick Start](docs/QUICKSTART.md)
- [API Reference](docs/API.md)
- [Strategy Guide](docs/STRATEGIES.md)
- [OpenClaw Skill](openclaw-skill/SKILL.md)

## Requirements

- Python >= 3.9
- pandas >= 2.0.0
- numpy >= 1.24.0
- ccxt >= 4.0.0

See [requirements.txt](requirements.txt) for full list.

## Roadmap

- [x] Project architecture
- [x] OpenClaw Skill definition
- [ ] Core backtesting engine
- [ ] Technical indicators library
- [ ] Paper trading engine
- [ ] Live trading engine
- [ ] Parameter optimization
- [ ] Web dashboard

## Status

**Alpha** - Under active development

## License

MIT

## Links

- **ClawHub**: https://clawhub.ai/ZhenStaff/openclaw-quant
- **GitHub**: https://github.com/ZhenRobotics/openclaw-quant
- **Issues**: https://github.com/ZhenRobotics/openclaw-quant/issues
