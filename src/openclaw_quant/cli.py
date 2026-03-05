"""
Command Line Interface for OpenClaw Quant
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw Quant - Professional Quantitative Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest
  openclaw-quant backtest --strategy ma_cross --symbol BTCUSDT --days 365

  # Optimize parameters
  openclaw-quant optimize --strategy rsi --metric sharpe_ratio

  # Show help
  openclaw-quant --help

For more information: https://github.com/ZhenRobotics/openclaw-quant-analyst
        """
    )

    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run strategy backtest')
    backtest_parser.add_argument('--strategy', required=True, help='Strategy name')
    backtest_parser.add_argument('--symbol', default='BTC/USDT', help='Trading pair')
    backtest_parser.add_argument('--exchange', default='binance', help='Exchange name')
    backtest_parser.add_argument('--timeframe', default='1d', help='Candle timeframe')
    backtest_parser.add_argument('--days', type=int, default=365, help='Days of history')
    backtest_parser.add_argument('--cash', type=float, default=10000, help='Initial capital')
    backtest_parser.add_argument('--commission', type=float, default=0.001, help='Commission rate')

    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize strategy parameters')
    optimize_parser.add_argument('--strategy', required=True, help='Strategy name')
    optimize_parser.add_argument('--symbol', default='BTC/USDT', help='Trading pair')
    optimize_parser.add_argument('--metric', default='sharpe_ratio', help='Metric to optimize')
    optimize_parser.add_argument('--method', default='grid', choices=['grid', 'optuna'], help='Optimization method')

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute command
    if args.command == 'backtest':
        run_backtest(args)
    elif args.command == 'optimize':
        run_optimization(args)
    else:
        parser.print_help()


def run_backtest(args):
    """Run backtest command"""
    print("=" * 60)
    print("OpenClaw Quant - Backtest")
    print("=" * 60)

    # Import here to avoid slow startup
    from .strategy import SMAStrategy
    from .backtest import Backtest
    from .data import get_data

    # Fetch data
    print(f"\n📊 Fetching {args.symbol} data...")
    data = get_data(
        symbol=args.symbol,
        exchange=args.exchange,
        timeframe=args.timeframe,
        days=args.days
    )
    print(f"✓ Loaded {len(data)} candles")

    # Run backtest
    print(f"\n🔄 Running backtest...")
    bt = Backtest(
        SMAStrategy,
        data,
        cash=args.cash,
        commission=args.commission
    )
    result = bt.run()

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\n💰 Returns:")
    print(f"  Total Return:     {result.total_return_pct:+.2f}%")
    print(f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}")
    print(f"  Max Drawdown:     {result.max_drawdown_pct:.2f}%")

    print(f"\n📊 Trades:")
    print(f"  Total:            {result.num_trades}")
    print(f"  Win Rate:         {result.win_rate:.2f}%")

    print("\n✓ Done!")


def run_optimization(args):
    """Run optimization command"""
    print("=" * 60)
    print("OpenClaw Quant - Optimization")
    print("=" * 60)
    print("\n🔍 Optimizing strategy parameters...")
    print("  This may take a while...")

    # TODO: Implement optimization
    print("\n⚠️  Optimization not yet implemented")
    print("  Use the Python API for now:")
    print("    from openclaw_quant import Backtest")
    print("    bt.optimize(...)")


if __name__ == '__main__':
    main()
