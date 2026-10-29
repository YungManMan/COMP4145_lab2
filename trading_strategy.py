import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import yfinance as yf
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    yf = None

# Download 5 years of MSFT data
def get_stock_data(ticker, period="5y"):
    if yf is None:
        raise ModuleNotFoundError(
            "yfinance is required. Install it with: pip install yfinance"
        )
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Calculate moving averages
def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

# Identify golden cross (buy signals)
def identify_golden_cross(data):
    data['Signal'] = 0  # Initialize signal column with 0
    # Golden Cross occurs when MA50 crosses above MA200
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    return data

# Implement trading strategy
def implement_strategy(data):
    positions = []

    # Need at least 200 days to calculate the 200-day MA
    data = data.iloc[200:].copy()

    buy_dates = data[data['GoldenCross'] == True].index.tolist()

    for buy_date in buy_dates:
        # Get buy price
        buy_price = data.loc[buy_date, 'Close']

        # Calculate target sell price (15% profit)
        target_price = buy_price * 1.15

        # Set maximum holding period
        max_sell_date = buy_date + pd.Timedelta(days=60)

        # Get data slice for potential sell period
        sell_period = data.loc[buy_date:max_sell_date].copy()

        # Check if target price is reached during the period
        target_reached = sell_period[sell_period['Close'] >= target_price]

        if not target_reached.empty:
            # Sell at first date target is reached
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            sell_reason = "Target reached"
        else:
            # Sell at end of maximum holding period
            sell_date_candidates = sell_period.index.tolist()
            if sell_date_candidates:
                sell_date = sell_date_candidates[-1]
                sell_price = data.loc[sell_date, 'Close']
                sell_reason = "Max holding period"
            else:
                # Skip if no valid sell date (should not happen in practice)
                continue

        # Calculate holding period in calendar days
        holding_days = (sell_date - buy_date).days

        # Calculate profit
        profit_pct = (sell_price / buy_price - 1) * 100

        positions.append({
            'BuyDate': buy_date,
            'BuyPrice': buy_price,
            'SellDate': sell_date,
            'SellPrice': sell_price,
            'HoldingDays': holding_days,
            'ProfitPct': profit_pct,
            'SellReason': sell_reason
        })

    return pd.DataFrame(positions)

# Analyze the results
def analyze_results(positions):
    if positions.empty:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'average_profit': 0,
            'average_holding_days': 0,
            'target_reached': 0,
            'max_period': 0,
            'message': 'No trading signals detected'
        }

    total_trades = len(positions)
    win_trades = len(positions[positions['ProfitPct'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
    avg_profit = positions['ProfitPct'].mean()
    avg_holding = positions['HoldingDays'].mean()
    target_reached = len(positions[positions['SellReason'] == 'Target reached'])
    max_period = len(positions[positions['SellReason'] == 'Max holding period'])

    return {
        'total_trades': total_trades,
        'winning_trades': win_trades,
        'losing_trades': loss_trades,
        'win_rate': round(win_rate, 2),
        'average_profit': round(avg_profit, 2),
        'average_holding_days': round(avg_holding, 2),
        'target_reached': target_reached,
        'max_period': max_period,
        'message': 'Strategy analysis completed successfully'
    }

# Main function
def main():
    # Get stock data
    data = get_stock_data("MSFT")

    # Calculate moving averages
    data = calculate_moving_averages(data)

    # Identify golden cross
    data = identify_golden_cross(data)

    # Implement strategy
    positions = implement_strategy(data)

    # Analyze results
    summary = analyze_results(positions)

    print("\n===== Trading Strategy Results (Golden Cross)=====")
    for key, value in summary.items():
        if key == 'message':
            continue
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\nDetailed Trades:")
    print(positions.to_string())

    return positions


if __name__ == "__main__":
    main()