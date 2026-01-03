# create_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_data(num_trades=50, account_balance=10000):
    """Create realistic sample trading data"""
    
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'XAUUSD', 'TSLA', 'AAPL']
    
    trades = []
    current_balance = account_balance
    
    for i in range(1, num_trades + 1):
        symbol = np.random.choice(symbols)
        
        # Generate realistic prices based on symbol
        if symbol in ['EURUSD', 'GBPUSD', 'USDJPY']:
            base_price = np.random.uniform(1.0, 1.5) if 'USD' in symbol else np.random.uniform(100, 150)
        elif symbol == 'BTCUSD':
            base_price = np.random.uniform(30000, 50000)
        elif symbol == 'XAUUSD':
            base_price = np.random.uniform(1800, 2100)
        else:  # Stocks
            base_price = np.random.uniform(100, 300)
        
        entry_price = base_price
        exit_price = entry_price * np.random.uniform(0.97, 1.03)  # +/- 3%
        
        # Determine if profit or loss
        if np.random.random() > 0.4:  # 60% win rate
            profit_loss = np.random.uniform(10, 100)
        else:
            profit_loss = -np.random.uniform(10, 100)
        
        # Adjust exit price based on P&L
        exit_price = entry_price * (1 + profit_loss / (entry_price * 0.1))
        
        # Generate times
        start_date = datetime.now() - timedelta(days=30)
        random_days = np.random.randint(0, 30)
        random_hours = np.random.randint(0, 23)
        
        entry_time = start_date + timedelta(days=random_days, hours=random_hours)
        exit_time = entry_time + timedelta(hours=np.random.randint(1, 48))
        
        # Stop loss and take profit
        stop_loss = entry_price * (0.98 if profit_loss > 0 else 1.02)  # 2% SL
        take_profit = entry_price * (1.02 if profit_loss > 0 else 0.98)  # 2% TP
        
        trades.append({
            'trade_id': i,
            'symbol': symbol,
            'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'trade_type': np.random.choice(['BUY', 'SELL']),
            'lot_size': np.random.uniform(0.01, 0.5),
            'entry_price': round(entry_price, 4),
            'exit_price': round(exit_price, 4),
            'stop_loss': round(stop_loss, 4),
            'take_profit': round(take_profit, 4),
            'profit_loss': round(profit_loss, 2),
            'account_balance_before': round(current_balance, 2)
        })
        
        current_balance += profit_loss
    
    return pd.DataFrame(trades)

# Save sample data
df = create_sample_data(100)
df.to_csv('data/sample_trades.csv', index=False)
print("Sample data created: data/sample_trades.csv")
print(f"Created {len(df)} sample trades")