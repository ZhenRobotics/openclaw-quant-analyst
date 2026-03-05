/**
 * OpenClaw Quant - Core Type Definitions
 * Quantitative trading system with backtesting, paper trading, and live trading
 */

export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Position {
  symbol: string;
  side: 'long' | 'short';
  entryPrice: number;
  quantity: number;
  entryTime: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  price?: number;
  quantity: number;
  timestamp: number;
  status: 'pending' | 'filled' | 'cancelled';
  filledPrice?: number;
  filledQuantity?: number;
}

export interface Trade {
  orderId: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  quantity: number;
  fee: number;
  timestamp: number;
}

export interface Signal {
  type: 'buy' | 'sell' | 'close';
  symbol: string;
  timestamp: number;
  price: number;
  quantity?: number;
  reason?: string;
  confidence?: number; // 0-1
}

export interface StrategyConfig {
  symbol: string;
  interval: string; // '1m', '5m', '15m', '1h', '4h', '1d'
  capital: number;
  positionSize: number; // Percentage of capital per trade (0-1)
  maxPositions: number;
  fees: number; // Trading fee percentage
  slippage: number; // Expected slippage percentage
  stopLoss?: number; // Stop loss percentage
  takeProfit?: number; // Take profit percentage
}

export interface BacktestResult {
  symbol: string;
  startTime: number;
  endTime: number;
  initialCapital: number;
  finalCapital: number;
  totalReturn: number; // Percentage
  totalReturnValue: number; // Absolute value
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number; // Percentage
  averageWin: number;
  averageLoss: number;
  profitFactor: number; // Gross profit / Gross loss
  sharpeRatio: number;
  maxDrawdown: number; // Percentage
  maxDrawdownValue: number; // Absolute value
  trades: Trade[];
  equity: { timestamp: number; value: number }[];
  metrics: Record<string, number>;
}

export interface PerformanceMetrics {
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  calmarRatio: number;
  recoveryFactor: number;
  averageWin: number;
  averageLoss: number;
  largestWin: number;
  largestLoss: number;
  averageTradeDuration: number; // in hours
  expectancy: number; // Expected value per trade
}

export interface OptimizationConfig {
  parameters: {
    name: string;
    min: number;
    max: number;
    step: number;
  }[];
  metric: keyof PerformanceMetrics; // Metric to optimize
  direction: 'maximize' | 'minimize';
  method: 'grid' | 'genetic' | 'random';
  maxIterations?: number;
  populationSize?: number; // For genetic algorithm
}

export interface OptimizationResult {
  bestParameters: Record<string, number>;
  bestScore: number;
  results: {
    parameters: Record<string, number>;
    score: number;
    metrics: PerformanceMetrics;
  }[];
  totalRuns: number;
  duration: number; // milliseconds
}

export interface DataSource {
  name: string;
  getCandles(
    symbol: string,
    interval: string,
    startTime: number,
    endTime?: number,
    limit?: number
  ): Promise<Candle[]>;
  subscribeCandles?(
    symbol: string,
    interval: string,
    callback: (candle: Candle) => void
  ): () => void;
}

export interface ExchangeConnector extends DataSource {
  placeOrder(order: Omit<Order, 'id' | 'status' | 'timestamp'>): Promise<Order>;
  cancelOrder(orderId: string): Promise<void>;
  getBalance(asset: string): Promise<number>;
  getPosition(symbol: string): Promise<Position | null>;
}

export interface Strategy {
  name: string;
  config: StrategyConfig;
  parameters: Record<string, number>;

  initialize(candles: Candle[]): void;
  onCandle(candle: Candle, candles: Candle[]): Signal | null;
  onTrade?(trade: Trade): void;
  cleanup?(): void;
}

export interface TradingContext {
  getCurrentPrice(symbol: string): number;
  getCandles(symbol: string, limit: number): Candle[];
  getBalance(asset: string): number;
  getPosition(symbol: string): Position | null;
  getPositions(): Position[];
  placeOrder(order: Omit<Order, 'id' | 'status' | 'timestamp'>): Promise<Order>;
  closePosition(symbol: string): Promise<void>;
}
