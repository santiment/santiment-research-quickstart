# 20 Santiment API Demo Ideas

From simple to complex, suitable for showcasing API capabilities to colleagues and clients.

---

## 🟢 Simple Level (1-7) - 5 Minute Demos

### 1. Real-time Price Checker
**Concept**: Simplest "Hello World" demo

```python
import san

# Get latest price
df = san.get("price_usd", slug="bitcoin", from_date="utc_now-1d", to_date="utc_now")
latest_price = df['value'].iloc[-1]
print(f"💰 Bitcoin Latest Price: ${latest_price:,.2f}")
```

**Highlights**: One line of code to get professional data  
**Audience**: Non-technical colleagues, new clients

---

### 2. Multi-Asset Price Comparison Dashboard
**Concept**: Show price trends of multiple major cryptocurrencies simultaneously

```python
import san
import matplotlib.pyplot as plt

assets = ["bitcoin", "ethereum", "solana", "cardano"]
prices = san.get_many("price_usd", slugs=assets, from_date="utc_now-30d", to_date="utc_now")

# Normalize to percentage change
normalized = (prices / prices.iloc[0] - 1) * 100
normalized.plot(figsize=(10, 6), title="30-Day Price Performance Comparison (%)")
```

**Highlights**: Single API call for multi-asset data  
**Visualization**: Multi-line time series chart

---

### 3. Bitcoin Network Activity Monitor
**Concept**: Display on-chain active address count

```python
import san

daa = san.get("daily_active_addresses", slug="bitcoin", from_date="utc_now-90d", to_date="utc_now")
print(f"📊 Average Daily Active Addresses: {daa['value'].mean():,.0f}")
print(f"📈 Peak Daily Active Addresses: {daa['value'].max():,.0f}")
```

**Highlights**: On-chain data vs price data differences  
**Use Case**: Network health baseline metric

---

### 4. Social Media Sentiment Dashboard
**Concept**: Display real-time sentiment of crypto community

```python
import san

sentiment = san.get("sentiment_balance", slug="bitcoin", from_date="utc_now-7d", to_date="utc_now")
social_vol = san.get("social_volume_total", slug="bitcoin", from_date="utc_now-7d", to_date="utc_now")

# Simple sentiment indicator
avg_sentiment = sentiment['value'].mean()
mood = "😊 Positive" if avg_sentiment > 0 else "😟 Negative"
print(f"This Week's Market Sentiment: {mood} (Score: {avg_sentiment:.2f})")
```

**Highlights**: Exclusive social data source  
**Use Case**: Sentiment-driven trading signals

---

### 5. Exchange Fund Flow Monitor
**Concept**: Monitor fund inflow/outflow to exchanges

```python
import san

inflow = san.get("exchange_inflow", slug="ethereum", from_date="utc_now-7d", to_date="utc_now")
outflow = san.get("exchange_outflow", slug="ethereum", from_date="utc_now-7d", to_date="utc_now")

net_flow = outflow['value'].sum() - inflow['value'].sum()
trend = "📤 Outflow" if net_flow > 0 else "📥 Inflow"
print(f"ETH 7-Day Net Flow: {trend} {abs(net_flow):,.0f} ETH")
```

**Highlights**: Predictive indicator (outflow = bullish signal)  
**Use Case**: Short-term price prediction

---

### 6. MVRV Valuation Indicator
**Concept**: Professional-grade valuation metric for market cycle judgment

```python
import san

mvrv = san.get("mvrv_usd", slug="bitcoin", from_date="utc_now-365d", to_date="utc_now")
current = mvrv['value'].iloc[-1]

if current > 3.5:
    signal = "🔴 Overvalued Zone"
elif current < 1.0:
    signal = "🟢 Undervalued Zone"
else:
    signal = "🟡 Fair Zone"

print(f"Current MVRV: {current:.2f} - {signal}")
```

**Highlights**: Institutional-grade analysis metric  
**Use Case**: Long-term portfolio allocation

---

### 7. Development Activity Leaderboard
**Concept**: Track GitHub development activity

```python
import san

# Get development activity for multiple projects
projects = ["ethereum", "bitcoin", "cardano", "polkadot"]
batch = san.AsyncBatch()

for project in projects:
    batch.get("dev_activity", selector={"organization": project}, 
              from_date="utc_now-30d", to_date="utc_now")

results = batch.execute()

for project, activity in zip(projects, results):
    total = activity['value'].sum()
    print(f"{project}: {total:.0f} development activity points")
```

**Highlights**: Use selector to query non-asset data  
**Use Case**: Fundamental analysis, project health

---

## 🟡 Intermediate Level (8-14) - 15 Minute Demos

### 8. On-Chain vs Price Correlation Analysis
**Concept**: Explore relationship between active addresses and price

```python
import san
import pandas as pd
import seaborn as sns

# Get data
batch = san.AsyncBatch()
batch.get("price_usd", slug="bitcoin", from_date="2023-01-01", to_date="2024-01-01")
batch.get("daily_active_addresses", slug="bitcoin", from_date="2023-01-01", to_date="2024-01-01")
batch.get("transaction_volume", slug="bitcoin", from_date="2023-01-01", to_date="2024-01-01")

price, daa, volume = batch.execute()

# Merge and calculate correlation
df = pd.concat([price['value'], daa['value'], volume['value']], axis=1)
df.columns = ['Price', 'Active_Addresses', 'Volume']

correlation = df.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm')
```

**Highlights**: Multi-dimensional data analysis  
**Visualization**: Correlation heatmap

---

### 9. Whale Activity Alert System
**Concept**: Monitor large transactions and correlate with price movements

```python
import san

# Get whale transaction count and price
batch = san.AsyncBatch()
batch.get("whale_transaction_count_1m_usd_to_inf", slug="bitcoin", 
          from_date="utc_now-30d", to_date="utc_now")
batch.get("price_usd", slug="bitcoin", from_date="utc_now-30d", to_date="utc_now")

whales, price = batch.execute()

# Find days with high whale activity
high_whale_days = whales[whales['value'] > whales['value'].quantile(0.9)]
print(f"🐋 {len(high_whale_days)} days with abnormal whale activity in past 30 days")

# Analyze next-day price change
for date in high_whale_days.index[:3]:
    print(f"  {date.strftime('%Y-%m-%d')}: Whale transactions {high_whale_days.loc[date, 'value']:.0f}")
```

**Highlights**: Predictive analysis  
**Use Case**: Trading timing selection

---

### 10. Comprehensive Market Health Score
**Concept**: Multi-indicator comprehensive scoring system

```python
import san
import numpy as np

def calculate_health_score(slug):
    # Get multiple indicators
    batch = san.AsyncBatch()
    batch.get("mvrv_usd", slug=slug, from_date="utc_now-1d", to_date="utc_now")
    batch.get("nvt", slug=slug, from_date="utc_now-1d", to_date="utc_now")
    batch.get("exchange_inflow", slug=slug, from_date="utc_now-7d", to_date="utc_now")
    
    mvrv, nvt, inflow = batch.execute()
    
    # Calculate score (0-100)
    score = 50
    if mvrv['value'].iloc[-1] < 2: score += 20  # Undervalued bonus
    if nvt['value'].iloc[-1] < 50: score += 15  # Low NVT bonus
    if inflow['value'].mean() < inflow['value'].rolling(30).mean().iloc[-1]: score += 15  # Reduced inflow bonus
    
    return min(100, max(0, score))

score = calculate_health_score("bitcoin")
print(f"🎯 BTC Market Health Score: {score}/100")
```

**Highlights**: Custom composite indicator  
**Use Case**: Portfolio management tool

---

### 11. Asset Correlation Heatmap
**Concept**: Analyze price correlation between multiple assets

```python
import san
import seaborn as sns
import matplotlib.pyplot as plt

assets = ["bitcoin", "ethereum", "solana", "cardano", "polkadot", "avalanche"]
prices = san.get_many("price_usd", slugs=assets, from_date="2023-01-01", to_date="2024-01-01")

# Calculate daily returns
daily_returns = prices.pct_change()

# Correlation matrix
correlation_matrix = daily_returns.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', center=0,
            square=True, fmt='.2f')
plt.title("Crypto Asset Price Correlation Matrix")
```

**Highlights**: Portfolio optimization  
**Visualization**: Professional-grade heatmap

---

### 12. Social Sentiment-Price Divergence Detection
**Concept**: Discover inconsistencies between sentiment and price (potential opportunities)

```python
import san
import numpy as np

# Get data
sentiment = san.get("sentiment_balance", slug="bitcoin", from_date="utc_now-30d", to_date="utc_now")
price = san.get("price_usd", slug="bitcoin", from_date="utc_now-30d", to_date="utc_now")

# Normalize to 0-1 range
sentiment_norm = (sentiment['value'] - sentiment['value'].min()) / (sentiment['value'].max() - sentiment['value'].min())
price_norm = (price['value'] - price['value'].min()) / (price['value'].max() - price['value'].min())

# Calculate divergence
divergence = sentiment_norm - price_norm
latest_divergence = divergence.iloc[-1]

if abs(latest_divergence) > 0.3:
    direction = "Sentiment above price" if latest_divergence > 0 else "Price above sentiment"
    print(f"⚠️ Divergence signal detected: {direction} (Divergence: {latest_divergence:.2f})")
```

**Highlights**: Contrarian trading signal  
**Use Case**: Identify market overreactions

---

### 13. Exchange Balance Change Alert
**Concept**: Monitor exchange total balance change trends

```python
import san
import pandas as pd

def exchange_alert(slug, threshold=0.05):
    """Alert when exchange balance change exceeds threshold"""
    balance = san.get("exchange_balance", slug=slug, from_date="utc_now-30d", to_date="utc_now")
    
    current = balance['value'].iloc[-1]
    avg_30d = balance['value'].mean()
    change = (current - avg_30d) / avg_30d
    
    if abs(change) > threshold:
        direction = "Decreased" if change < 0 else "Increased"
        emoji = "🚨" if change < 0 else "⚠️"  # Decrease is usually bullish
        print(f"{emoji} {slug} Exchange Balance {direction}: {abs(change)*100:.1f}%")
        return True
    return False

exchange_alert("ethereum", threshold=0.03)
```

**Highlights**: Automated monitoring  
**Use Case**: Risk alert system

---

### 14. NVT Ratio Historical Analysis
**Concept**: Long-term analysis of Network Value to Transactions ratio

```python
import san
import matplotlib.pyplot as plt

# Get multi-year NVT data
nvt = san.get("nvt", slug="bitcoin", from_date="2020-01-01", to_date="2024-01-01")

# Calculate historical percentiles
p10 = nvt['value'].quantile(0.10)
p90 = nvt['value'].quantile(0.90)
current = nvt['value'].iloc[-1]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(nvt.index, nvt['value'], label='NVT Ratio')
ax.axhline(y=p10, color='green', linestyle='--', label=f'10th percentile ({p10:.1f})')
ax.axhline(y=p90, color='red', linestyle='--', label=f'90th percentile ({p90:.1f})')
ax.axhline(y=current, color='blue', linestyle='-', label=f'Current ({current:.1f})')
ax.legend()
ax.set_title("Bitcoin NVT Ratio Historical Analysis")
```

**Highlights**: Long-term valuation model  
**Visualization**: Trend chart with historical percentiles

---

## 🔴 Advanced Level (15-20) - 30 Minute Demos

### 15. Simple Strategy Backtesting Framework
**Concept**: Backtest investment strategies based on API data

```python
import san
import pandas as pd
import numpy as np

def backtest_mvrv_strategy(slug, start_date, end_date):
    """
    MVRV Strategy: Buy when MVRV < 1, Sell when MVRV > 3.5
    """
    # Get data
    mvrv = san.get("mvrv_usd", slug=slug, from_date=start_date, to_date=end_date)
    price = san.get("price_usd", slug=slug, from_date=start_date, to_date=end_date)
    
    df = pd.concat([mvrv['value'], price['value']], axis=1)
    df.columns = ['MVRV', 'Price']
    
    position = 0  # 0 = No position, 1 = Full position
    trades = []
    
    for date, row in df.iterrows():
        if row['MVRV'] < 1.0 and position == 0:
            position = 1
            trades.append({'date': date, 'action': 'BUY', 'price': row['Price']})
        elif row['MVRV'] > 3.5 and position == 1:
            position = 0
            trades.append({'date': date, 'action': 'SELL', 'price': row['Price']})
    
    # Calculate returns
    returns = []
    for i in range(0, len(trades)-1, 2):
        if trades[i]['action'] == 'BUY' and trades[i+1]['action'] == 'SELL':
            ret = (trades[i+1]['price'] - trades[i]['price']) / trades[i]['price']
            returns.append(ret)
    
    return trades, returns

trades, returns = backtest_mvrv_strategy("bitcoin", "2020-01-01", "2024-01-01")
print(f"Strategy executed {len(trades)} trades")
print(f"Average return: {np.mean(returns)*100:.1f}%")
```

**Highlights**: Complete investment strategy validation  
**Use Case**: Quantitative research team

---

### 16. Real-time Anomaly Detection System
**Concept**: Detect abnormal patterns in on-chain data

```python
import san
import numpy as np
from scipy import stats

def detect_anomalies(slug, metric, window=30):
    """Detect outliers using Z-score"""
    data = san.get(metric, slug=slug, from_date=f"utc_now-{window}d", to_date="utc_now")
    
    # Calculate Z-score
    z_scores = np.abs(stats.zscore(data['value']))
    anomalies = data[z_scores > 2.5]  # Z-score > 2.5 considered anomaly
    
    if len(anomalies) > 0:
        latest_anomaly = anomalies.iloc[-1]
        latest_z = z_scores[z_scores > 2.5][-1]
        print(f"🔴 Anomaly detected!")
        print(f"   Time: {latest_anomaly.name}")
        print(f"   Value: {latest_anomaly['value']:,.0f}")
        print(f"   Z-Score: {latest_z:.2f}")
        return True
    return False

detect_anomalies("bitcoin", "daily_active_addresses")
```

**Highlights**: Real-time monitoring system  
**Use Case**: Risk monitoring, trading signals

---

### 17. Machine Learning Feature Engineering
**Concept**: Prepare rich feature sets for ML models

```python
import san
import pandas as pd
import numpy as np

def build_feature_set(slug, start_date, end_date):
    """Build feature dataset for ML"""
    
    # Batch fetch multiple features
    metrics = [
        "price_usd", "daily_active_addresses", "transaction_volume",
        "exchange_inflow", "exchange_outflow", "mvrv_usd", "nvt",
        "sentiment_balance", "social_volume_total", "dev_activity"
    ]
    
    batch = san.AsyncBatch()
    for metric in metrics:
        try:
            batch.get(metric, slug=slug, from_date=start_date, to_date=end_date)
        except:
            pass
    
    results = batch.execute()
    
    # Merge all features
    feature_df = pd.concat([r['value'] for r in results], axis=1)
    feature_df.columns = metrics[:len(results)]
    
    # Add technical indicator features
    feature_df['price_ma7'] = feature_df['price_usd'].rolling(7).mean()
    feature_df['price_ma30'] = feature_df['price_usd'].rolling(30).mean()
    feature_df['price_volatility'] = feature_df['price_usd'].rolling(7).std()
    
    # Add on-chain features
    feature_df['net_exchange_flow'] = feature_df['exchange_outflow'] - feature_df['exchange_inflow']
    feature_df['nvt_normalized'] = (feature_df['nvt'] - feature_df['nvt'].mean()) / feature_df['nvt'].std()
    
    # Target variable: 7-day future price change
    feature_df['target'] = feature_df['price_usd'].shift(-7) / feature_df['price_usd'] - 1
    
    return feature_df.dropna()

features = build_feature_set("bitcoin", "2023-01-01", "2024-01-01")
print(f"Feature matrix shape: {features.shape}")
print(f"Feature list: {list(features.columns)}")
```

**Highlights**: Data science workflow  
**Use Case**: Predictive models, quantitative strategies

---

### 18. Cross-Asset Fund Flow Analysis
**Concept**: Track fund flow between different assets

```python
import san
import pandas as pd

def cross_asset_flow_analysis(assets, window_days=7):
    """
    Analyze exchange net flow for multiple assets
    Identify which assets funds are flowing out from and into
    """
    results = []
    
    for asset in assets:
        inflow = san.get("exchange_inflow", slug=asset, 
                        from_date=f"utc_now-{window_days}d", to_date="utc_now")
        outflow = san.get("exchange_outflow", slug=asset,
                         from_date=f"utc_now-{window_days}d", to_date="utc_now")
        
        net_flow = (outflow['value'] - inflow['value']).sum()
        results.append({
            'asset': asset,
            'net_flow': net_flow,
            'status': 'Outflow' if net_flow > 0 else 'Inflow'
        })
    
    df = pd.DataFrame(results).sort_values('net_flow', ascending=False)
    
    print(f"📊 {window_days}-Day Cross-Asset Fund Flow Analysis:")
    print("=" * 50)
    for _, row in df.iterrows():
        emoji = "🟢" if row['net_flow'] > 0 else "🔴"
        print(f"{emoji} {row['asset']}: {row['status']} {abs(row['net_flow']):,.0f}")
    
    return df

assets = ["bitcoin", "ethereum", "solana", "cardano"]
flow_analysis = cross_asset_flow_analysis(assets)
```

**Highlights**: Market microstructure analysis  
**Use Case**: Asset allocation, rotation strategies

---

### 19. Market Sentiment Composite Index
**Concept**: Build a fear/greed index combining multiple factors

```python
import san
import numpy as np

def calculate_fear_greed_index(slug="bitcoin"):
    """
    Custom Fear/Greed Index (0-100)
    Combines: MVRV, NVT, Social Sentiment, Exchange Flow, Whale Activity
    """
    batch = san.AsyncBatch()
    batch.get("mvrv_usd", slug=slug, from_date="utc_now-30d", to_date="utc_now")
    batch.get("nvt", slug=slug, from_date="utc_now-30d", to_date="utc_now")
    batch.get("sentiment_balance", slug=slug, from_date="utc_now-7d", to_date="utc_now")
    batch.get("exchange_balance", slug=slug, from_date="utc_now-30d", to_date="utc_now")
    batch.get("whale_transaction_count_100k_usd_to_inf", slug=slug, from_date="utc_now-7d", to_date="utc_now")
    
    mvrv, nvt, sentiment, ex_balance, whales = batch.execute()
    
    # Calculate factor scores (0-20 points each)
    scores = {}
    
    # MVRV score (Low MVRV = Fear = Low score, High MVRV = Greed = High score)
    mvrv_current = mvrv['value'].iloc[-1]
    scores['mvrv'] = min(20, max(0, (mvrv_current / 5) * 20))
    
    # NVT score (High NVT = Fear = Low score)
    nvt_percentile = (nvt['value'].iloc[-1] - nvt['value'].min()) / (nvt['value'].max() - nvt['value'].min())
    scores['nvt'] = (1 - nvt_percentile) * 20
    
    # Sentiment score
    sent_norm = (sentiment['value'].mean() + 1) / 2  # Assume range -1 to 1
    scores['sentiment'] = sent_norm * 20
    
    # Exchange balance change (Outflow = Less fear = High score)
    balance_change = (ex_balance['value'].iloc[-1] - ex_balance['value'].iloc[0]) / ex_balance['value'].iloc[0]
    scores['exchange'] = (1 - balance_change) * 20 if balance_change < 0 else max(0, (1 - balance_change) * 20)
    
    # Whale activity (High activity = Greed = High score)
    whale_avg = whales['value'].mean()
    scores['whales'] = min(20, whale_avg / 10)
    
    # Total score
    total_score = sum(scores.values())
    
    # Sentiment label
    if total_score < 25:
        sentiment_label = "Extreme Fear"
    elif total_score < 40:
        sentiment_label = "Fear"
    elif total_score < 60:
        sentiment_label = "Neutral"
    elif total_score < 75:
        sentiment_label = "Greed"
    else:
        sentiment_label = "Extreme Greed"
    
    print(f"🎯 {slug.upper()} Fear/Greed Index")
    print(f"Total Score: {total_score:.0f}/100 - {sentiment_label}")
    print("-" * 30)
    for factor, score in scores.items():
        print(f"  {factor}: {score:.1f}/20")
    
    return total_score, scores

score, details = calculate_fear_greed_index("bitcoin")
```

**Highlights**: Custom market sentiment indicator  
**Use Case**: Market sentiment monitoring, contrarian indicator

---

### 20. Automated Trading Signal Generator
**Concept**: Multi-factor trading signal system that can be integrated into trading systems

```python
import san
from datetime import datetime

class TradingSignalGenerator:
    """Multi-factor trading signal generator"""
    
    def __init__(self, slug):
        self.slug = slug
        self.signals = []
    
    def fetch_data(self):
        """Fetch required data"""
        batch = san.AsyncBatch()
        batch.get("price_usd", slug=self.slug, from_date="utc_now-30d", to_date="utc_now")
        batch.get("mvrv_usd", slug=self.slug, from_date="utc_now-30d", to_date="utc_now")
        batch.get("exchange_inflow", slug=self.slug, from_date="utc_now-7d", to_date="utc_now")
        batch.get("sentiment_balance", slug=self.slug, from_date="utc_now-7d", to_date="utc_now")
        batch.get("whale_transaction_count_1m_usd_to_inf", slug=self.slug, from_date="utc_now-7d", to_date="utc_now")
        
        self.price, self.mvrv, self.inflow, self.sentiment, self.whales = batch.execute()
    
    def generate_signals(self):
        """Generate trading signals"""
        self.fetch_data()
        signals = []
        
        # Signal 1: MVRV oversold/overbought
        mvrv_current = self.mvrv['value'].iloc[-1]
        if mvrv_current < 1.0:
            signals.append(('MVRV', 'BUY', f'MVRV = {mvrv_current:.2f} (Oversold)', 0.25))
        elif mvrv_current > 3.5:
            signals.append(('MVRV', 'SELL', f'MVRV = {mvrv_current:.2f} (Overbought)', 0.25))
        
        # Signal 2: Large exchange inflow (bearish)
        inflow_avg = self.inflow['value'].mean()
        inflow_current = self.inflow['value'].iloc[-1]
        if inflow_current > inflow_avg * 2:
            signals.append(('Exchange Flow', 'SELL', f'Abnormally high inflow ({inflow_current/inflow_avg:.1f}x average)', 0.20))
        
        # Signal 3: Extremely negative sentiment (contrarian buy)
        sent_avg = self.sentiment['value'].mean()
        if sent_avg < -0.5:
            signals.append(('Sentiment', 'BUY', f'Extremely negative sentiment ({sent_avg:.2f}), contrarian signal', 0.15))
        
        # Signal 4: Whale activity surge
        whale_current = self.whales['value'].iloc[-1]
        whale_avg = self.whales['value'].mean()
        if whale_current > whale_avg * 3:
            signals.append(('Whales', 'CAUTION', f'Whale activity surge ({whale_current:.0f} transactions)', 0.20))
        
        self.signals = signals
        return signals
    
    def get_recommendation(self):
        """Comprehensive recommendation"""
        signals = self.generate_signals()
        
        if not signals:
            return "HOLD", 0, "No clear signals"
        
        # Weighted calculation
        buy_score = sum(s[3] for s in signals if s[1] == 'BUY')
        sell_score = sum(s[3] for s in signals if s[1] == 'SELL')
        
        if buy_score > sell_score and buy_score > 0.3:
            return "BUY", buy_score, signals
        elif sell_score > buy_score and sell_score > 0.3:
            return "SELL", sell_score, signals
        else:
            return "HOLD", max(buy_score, sell_score), signals
    
    def report(self):
        """Generate report"""
        action, confidence, details = self.get_recommendation()
        
        print(f"📈 {self.slug.upper()} Trading Signal Report")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Recommendation: {'🟢' if action == 'BUY' else '🔴' if action == 'SELL' else '⚪'} {action}")
        print(f"Confidence: {confidence:.0%}")
        print("-" * 40)
        
        if isinstance(details, list):
            print("Detailed Signals:")
            for source, signal, reason, weight in details:
                print(f"  • {source}: {signal} (Weight: {weight:.0%})")
                print(f"    Reason: {reason}")
        else:
            print(details)

# Usage
generator = TradingSignalGenerator("bitcoin")
generator.report()
```

**Highlights**: Production-grade trading system component  
**Use Case**: Quantitative funds, automated trading systems

---

## Demo Recommendations

| Scenario | Recommended Demos | Duration |
|----------|------------------|----------|
| Sales Demo (Non-technical Clients) | 1, 2, 5, 6, 10 | 15 minutes |
| Technical Integration Meeting | 2, 7, 8, 11, 17 | 30 minutes |
| Quant Team Roadshow | 10, 15, 17, 19, 20 | 45 minutes |
| Full Product Demo | All in order | 90 minutes |

## Technical Preparation Checklist

- [ ] API Key configuration
- [ ] Jupyter Notebook environment
- [ ] matplotlib/seaborn visualization
- [ ] Sample data cache (prevent demo network issues)
- [ ] Pre-generated charts as backup
