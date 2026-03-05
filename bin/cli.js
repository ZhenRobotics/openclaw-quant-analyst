#!/usr/bin/env node

/**
 * OpenClaw Quant Analyst - npm CLI Wrapper
 *
 * This is a Node.js wrapper that calls the Python backend.
 * Users can install via npm and use immediately.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkPython() {
  // Check if Python 3 is installed
  const pythonCommands = ['python3', 'python'];

  for (const cmd of pythonCommands) {
    try {
      const result = spawn(cmd, ['--version'], { stdio: 'pipe' });
      result.on('close', (code) => {
        if (code === 0) {
          return cmd;
        }
      });
    } catch (err) {
      continue;
    }
  }

  return null;
}

function showHelp() {
  console.log(`
${colors.cyan}OpenClaw Quant Analyst${colors.reset} - Professional Quantitative Trading System

${colors.yellow}Usage:${colors.reset}
  openclaw-quant-analyst <command> [options]

${colors.yellow}Commands:${colors.reset}
  backtest              Run strategy backtest
  optimize              Optimize strategy parameters
  help                  Show this help message
  install-python        Install Python dependencies

${colors.yellow}Examples:${colors.reset}
  openclaw-quant-analyst backtest --strategy ma_cross --symbol BTCUSDT
  openclaw-quant-analyst optimize --strategy rsi --metric sharpe_ratio
  openclaw-quant-analyst install-python

${colors.yellow}Python API:${colors.reset}
  This is a Node.js wrapper. For full functionality, use the Python API:

  ${colors.green}from openclaw_quant import Strategy, Backtest, get_data
  from openclaw_quant.indicators import SMA, RSI

  class MyStrategy(Strategy):
      def init(self):
          self.ma = self.I(SMA, self.data.Close, 20)

      def next(self):
          if self.data.Close[-1] > self.ma[-1]:
              if not self.position:
                  self.buy()

  data = get_data('BTC/USDT', days=365)
  bt = Backtest(MyStrategy, data, cash=10000)
  result = bt.run()
  result.plot()${colors.reset}

${colors.yellow}Documentation:${colors.reset}
  GitHub: https://github.com/ZhenRobotics/openclaw-quant-analyst
  ClawHub: https://clawhub.ai/ZhenStaff/quant-analyst

${colors.yellow}Installation:${colors.reset}
  npm install -g openclaw-quant-analyst
  pip install openclaw-quant-analyst
`);
}

function installPythonDeps() {
  log('\n📦 Installing Python dependencies...', 'cyan');

  const pythonCmd = checkPython();
  if (!pythonCmd) {
    log('❌ Error: Python 3 is not installed', 'red');
    log('Please install Python 3.9 or higher: https://www.python.org/downloads/', 'yellow');
    process.exit(1);
  }

  log(`✓ Found Python: ${pythonCmd}`, 'green');
  log('Installing openclaw-quant-analyst...', 'cyan');

  const pip = spawn(pythonCmd, ['-m', 'pip', 'install', 'openclaw-quant-analyst'], {
    stdio: 'inherit'
  });

  pip.on('close', (code) => {
    if (code === 0) {
      log('\n✓ Python dependencies installed successfully!', 'green');
      log('\nYou can now use:', 'cyan');
      log('  openclaw-quant-analyst backtest --strategy ma_cross', 'yellow');
    } else {
      log('\n❌ Failed to install Python dependencies', 'red');
      process.exit(code);
    }
  });
}

function runPythonCLI(args) {
  const pythonCmd = checkPython();

  if (!pythonCmd) {
    log('❌ Error: Python 3 is not installed', 'red');
    log('Please install Python 3.9 or higher: https://www.python.org/downloads/', 'yellow');
    log('\nOr use: openclaw-quant-analyst install-python', 'cyan');
    process.exit(1);
  }

  // Try to run the Python CLI
  const cli = spawn(pythonCmd, ['-m', 'openclaw_quant.cli', ...args], {
    stdio: 'inherit'
  });

  cli.on('error', (err) => {
    log('❌ Error: openclaw_quant Python package not found', 'red');
    log('\nPlease install it first:', 'yellow');
    log('  npm run install-python', 'cyan');
    log('  or', 'yellow');
    log('  pip install openclaw-quant-analyst', 'cyan');
    process.exit(1);
  });

  cli.on('close', (code) => {
    process.exit(code);
  });
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === 'help' || args[0] === '--help' || args[0] === '-h') {
  showHelp();
  process.exit(0);
}

if (args[0] === 'install-python') {
  installPythonDeps();
} else {
  runPythonCLI(args);
}
