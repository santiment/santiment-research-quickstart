# Santiment GraphQL API Reference

Santiment API uses GraphQL as the query language. You can execute raw GraphQL queries via `san.graphql.execute_gql()`.

## Basic Usage

### Execute GraphQL Query

```python
import san

result = san.graphql.execute_gql("""
{
  projectBySlug(slug: "bitcoin") {
    slug
    name
    ticker
    priceUsd
    marketcapUsd
  }
}
""")
```

### Process Results

```python
import pandas as pd

# Convert to DataFrame
data = result['projectBySlug']
df = pd.DataFrame([data])
```

---

## Core Query Patterns

### 1. Get Project Information

```python
# Single project
result = san.graphql.execute_gql("""
{
  projectBySlug(slug: "ethereum") {
    slug
    name
    ticker
    infrastructure
    mainContractAddress
    twitterLink
    websiteLink
    githubLink
    marketcapUsd
    priceUsd
    volumeUsd
  }
}
""")
```

### 2. Get Time Series Data (getMetric)

The most commonly used pattern to get time series data for a metric:

```python
# Basic time series query
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      slug: "bitcoin"
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")

# Extract data
data = result['getMetric']['timeseriesData']
df = pd.DataFrame(data)
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
```

### 3. Multi-Asset Batch Query (timeseriesDataPerSlug)

Query the same metric for multiple assets in a single call:

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesDataPerSlug(
      selector: {slugs: ["bitcoin", "ethereum", "solana"]}
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      data {
        slug
        value
      }
    }
  }
}
""")

# Convert to DataFrame
data = result['getMetric']['timeseriesDataPerSlug']
rows = []
for point in data:
    row = {'datetime': point['datetime']}
    for item in point['data']:
        row[item['slug']] = item['value']
    rows.append(row)

df = pd.DataFrame(rows)
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
```

### 4. Advanced Queries Using Selector

Selector allows more flexible asset selection:

```python
# Contract address query
result = san.graphql.execute_gql("""
{
  getMetric(metric: "contract_transactions_count") {
    timeseriesData(
      selector: {
        contractAddress: "0x00000000219ab540356cBB839Cbe05303d7705Fa"
      }
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")

# Organization query (GitHub)
result = san.graphql.execute_gql("""
{
  getMetric(metric: "dev_activity") {
    timeseriesData(
      selector: {
        organization: "ethereum"
      }
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")

# Holder query with parameters
result = san.graphql.execute_gql("""
{
  getMetric(metric: "amount_in_top_holders") {
    timeseriesData(
      selector: {
        slug: "santiment"
        holdersCount: 10
      }
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")
```

### 5. Queries with Labels

```python
# DEX trading data
result = san.graphql.execute_gql("""
{
  getMetric(metric: "total_trade_volume_by_dex") {
    timeseriesData(
      selector: {
        slug: "ethereum"
        label: "decentralized_exchange"
        owner: "UniswapV2"
      }
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")
```

---

## Metadata Queries

### Get Metric Metadata

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "nvt") {
    metadata {
      availableSlugs
      defaultAggregation
      humanReadableName
      isAccessible
      isRestricted
      restrictedFrom
      restrictedTo
      dataType
      unit
    }
  }
}
""")

metadata = result['getMetric']['metadata']
```

### Get Available Metrics List

```python
result = san.graphql.execute_gql("""
{
  query: getAvailableMetrics
}
""")

metrics = result['query']
```

### Check Metric Availability for Asset

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "daily_active_addresses") {
    availableSince(slug: "bitcoin")
  }
}
""")

since = result['getMetric']['availableSince']
```

### Get Available Metrics for Project

```python
result = san.graphql.execute_gql("""
{
  projectBySlug(slug: "ethereum") {
    availableMetrics
  }
}
""")

metrics = result['projectBySlug']['availableMetrics']
```

---

## Project List Queries

### All Projects

```python
result = san.graphql.execute_gql("""
{
  allProjects {
    slug
    name
    ticker
    totalSupply
    marketSegment
    infrastructure
  }
}
""")

projects = result['allProjects']
df = pd.DataFrame(projects)
```

### ERC20 Projects

```python
result = san.graphql.execute_gql("""
{
  allErc20Projects {
    slug
    name
    ticker
    mainContractAddress
  }
}
""")
```

---

## Advanced Queries

### Query with Transform

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      slug: "bitcoin"
      from: "2024-01-01T00:00:00Z"
      to: "2024-03-01T00:00:00Z"
      interval: "1d"
      transform: {type: "moving_average", moving_average_base: 30}
      aggregation: LAST
    ) {
      datetime
      value
    }
  }
}
""")
```

### Include Incomplete Data

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "daily_active_addresses") {
    timeseriesData(
      slug: "bitcoin"
      from: "utc_now-3d"
      to: "utc_now"
      interval: "1d"
      includeIncompleteData: true
    ) {
      datetime
      value
    }
  }
}
""")
```

### Complexity Check

```python
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesDataComplexity(
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    )
  }
}
""")

complexity = result['getMetric']['timeseriesDataComplexity']
# Max complexity: 50000
```

---

## Non-Standard Queries

### OHLCV Data

```python
result = san.graphql.execute_gql("""
{
  ohlc(slug: "bitcoin", from: "2024-01-01T00:00:00Z", to: "2024-02-01T00:00:00Z", interval: "1d") {
    datetime
    openPriceUsd
    highPriceUsd
    lowPriceUsd
    closePriceUsd
    volume
    marketcap
  }
}
""")

df = pd.DataFrame(result['ohlc'])
```

### Historical Balance

```python
result = san.graphql.execute_gql("""
{
  historicalBalance(
    slug: "santiment"
    address: "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2"
    from: "2024-01-01T00:00:00Z"
    to: "2024-02-01T00:00:00Z"
    interval: "1d"
  ) {
    datetime
    balance
  }
}
""")
```

### Large Transactions

```python
# ETH large transactions
result = san.graphql.execute_gql("""
{
  ethTopTransactions(
    slug: "santiment"
    from: "2024-01-01T00:00:00Z"
    to: "2024-02-01T00:00:00Z"
    limit: 10
    transactionType: ALL
  ) {
    datetime
    fromAddress {
      address
      isExchange
    }
    toAddress {
      address
      isExchange
    }
    trxHash
    trxValue
  }
}
""")

# Token large transactions
result = san.graphql.execute_gql("""
{
  tokenTopTransactions(
    slug: "santiment"
    from: "2024-01-01T00:00:00Z"
    to: "2024-02-01T00:00:00Z"
    limit: 10
  ) {
    datetime
    fromAddress {
      address
      isExchange
    }
    toAddress {
      address
      isExchange
    }
    trxHash
    trxValue
  }
}
""")
```

### Trending Words

```python
result = san.graphql.execute_gql("""
{
  getTrendingWords(
    from: "2024-01-01T00:00:00Z"
    to: "2024-01-02T00:00:00Z"
    interval: "1d"
    size: 10
  ) {
    datetime
    topWords {
      word
      score
    }
  }
}
""")
```

---

## Error Handling

```python
from san.error import SanError

try:
    result = san.graphql.execute_gql("""
    {
      projectBySlug(slug: "invalid-slug-xyz") {
        name
      }
    }
    """)
except SanError as e:
    print(f"GraphQL Error: {e}")
    # Handle error: could be invalid slug, rate limit, etc.
```

---

## Query Optimization Tips

### 1. Specify Only Required Fields

Request only needed fields to reduce complexity:

```python
# Good: Only request necessary fields
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesData(slug: "bitcoin", from: "2024-01-01", to: "2024-02-01", interval: "1d") {
      datetime
      value
    }
  }
}
""")
```

### 2. Use Appropriate Intervals

```python
# Use larger intervals for large date ranges
# For 1 year of data use "1d" instead of "1h"
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      slug: "bitcoin"
      from: "2023-01-01T00:00:00Z"
      to: "2024-01-01T00:00:00Z"
      interval: "1d"  # not 1h
    ) {
      datetime
      value
    }
  }
}
""")
```

### 3. Batch vs Single Queries

For multiple assets, use `timeseriesDataPerSlug` instead of multiple individual queries:

```python
# Recommended: Single query for multiple assets
result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesDataPerSlug(
      selector: {slugs: ["bitcoin", "ethereum", "solana"]}
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
    ) {
      datetime
      data {
        slug
        value
      }
    }
  }
}
""")
```

---

## Complete Example: Building Custom Analysis

```python
import san
import pandas as pd

def fetch_multi_metric_comparison(slug, metrics, from_date, to_date):
    """
    Fetch multiple metrics for comparison analysis
    """
    # Build single GraphQL query to get multiple metrics
    queries = []
    for i, metric in enumerate(metrics):
        queries.append(f"""
    metric{i}: getMetric(metric: "{metric}") {{
      timeseriesData(
        slug: "{slug}"
        from: "{from_date}"
        to: "{to_date}"
        interval: "1d"
      ) {{
        datetime
        value
      }}
    }}
    """)
    
    full_query = "{\n" + "\n".join(queries) + "\n}"
    
    result = san.graphql.execute_gql(full_query)
    
    # Convert to DataFrame
    data_frames = {}
    for i, metric in enumerate(metrics):
        metric_data = result[f'metric{i}']['timeseriesData']
        df = pd.DataFrame(metric_data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.rename(columns={'value': metric}, inplace=True)
        data_frames[metric] = df
    
    # Merge all metrics
    combined = pd.concat(data_frames.values(), axis=1)
    return combined

# Usage
metrics = ['price_usd', 'daily_active_addresses', 'transaction_volume']
df = fetch_multi_metric_comparison(
    slug='bitcoin',
    metrics=metrics,
    from_date='2024-01-01T00:00:00Z',
    to_date='2024-02-01T00:00:00Z'
)
print(df.head())
```
