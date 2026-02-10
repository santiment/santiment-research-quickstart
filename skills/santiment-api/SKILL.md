---
name: santiment-api
description: Query and fetch cryptocurrency and blockchain data using Santiment GraphQL API via sanpy library. Use when you need to fetch on-chain metrics, price data, social metrics, or any crypto market analytics for analysis, visualization, or reporting. Supports single metrics (get), multiple assets (get_many), batching (AsyncBatch), SQL queries (execute_sql), and raw GraphQL.
---

# Santiment API

Python client (`sanpy`) for accessing cryptocurrency data from [Santiment API](https://api.santiment.net/).

## Quick Start

### Installation

```bash
pip install sanpy==0.12.3
```

### Configuration

```python
import san

# Option 1: Environment variable (recommended)
# export SANPY_APIKEY="your_api_key"

# Option 2: Manual configuration
san.ApiConfig.api_key = "your_api_key"
```

Get API key from [Santiment Account](https://app.santiment.net/account).

---

## Core Functions

### 1. Fetch Single Metric (`san.get`)

Fetch timeseries data for a single metric/asset pair.

```python
import san

# Basic usage - default: last 365 days, daily interval
df = san.get("price_usd", slug="bitcoin")

# With date range
df = san.get(
    "daily_active_addresses",
    slug="ethereum",
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d"
)

# Using selector for flexible targeting
df = san.get(
    "dev_activity",
    selector={"organization": "ethereum"},
    from_date="2024-01-01",
    to_date="2024-02-01"
)

# Contract address metrics
df = san.get(
    "contract_transactions_count",
    selector={"contractAddress": "0x00000000219ab540356cBB839Cbe05303d7705Fa"},
    from_date="2024-01-01",
    to_date="2024-02-01"
)

# With transformation
df = san.get(
    "price_usd",
    slug="bitcoin",
    from_date="2024-01-01",
    to_date="2024-03-01",
    transform={"type": "moving_average", "moving_average_base": 7}
)
```

### 2. Fetch Multiple Assets (`san.get_many`)

Fetch one metric for multiple assets in a single API call.

```python
df = san.get_many(
    "price_usd",
    slugs=["bitcoin", "ethereum", "tether"],
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d"
)
# Returns DataFrame with datetime index, columns: bitcoin, ethereum, tether
```

### 3. Batch Queries (`AsyncBatch` - Recommended)

Execute multiple queries concurrently.

```python
from san import AsyncBatch

batch = AsyncBatch()

batch.get("price_usd", slug="bitcoin", from_date="2024-01-01", to_date="2024-02-01")
batch.get("daily_active_addresses", slug="ethereum", from_date="2024-01-01", to_date="2024-02-01")
batch.get_many("price_usd", slugs=["bitcoin", "ethereum"], from_date="2024-01-01", to_date="2024-02-01")

results = batch.execute(max_workers=10)
# Returns list of DataFrames in order added
btc_price, eth_daa, multi_price = results
```

Legacy `Batch` class (single HTTP request, for lightweight queries):

```python
from san import Batch

batch = Batch()
batch.get("price_usd", slug="bitcoin")
batch.get("transaction_volume", slug="bitcoin")
results = batch.execute()
```

### 4. Execute SQL (`san.execute_sql`)

Query ClickHouse database directly with SQL.

```python
# Simple query
df = san.execute_sql(query="SELECT * FROM daily_metrics_v2 LIMIT 5")

# With parameters
df = san.execute_sql(
    query="""
    SELECT
        get_metric_name(metric_id) AS metric,
        get_asset_name(asset_id) AS asset,
        dt,
        argMax(value, computed_at)
    FROM daily_metrics_v2
    WHERE
        asset_id = get_asset_id({{slug}}) AND
        metric_id = get_metric_id({{metric}}) AND
        dt >= now() - INTERVAL {{last_n_days}} DAY
    GROUP BY dt, metric_id, asset_id
    ORDER BY dt ASC
    """,
    parameters={'slug': 'bitcoin', 'metric': 'daily_active_addresses', 'last_n_days': 7},
    set_index="dt"
)
```

### 5. Raw GraphQL

For custom queries not covered by helper functions.

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

**See [references/graphql.md](references/graphql.md) for comprehensive GraphQL documentation including:**
- Complete query patterns (timeseriesData, timeseriesDataPerSlug)
- Advanced selector usage (contracts, organizations, labels)
- Metadata and project queries
- OHLCV, historical balance, top transactions
- Query optimization techniques

---

## Common Metrics

```python
import san

# List all available metrics
metrics = san.available_metrics()

# List metrics for specific asset
metrics = san.available_metrics_for_slug("bitcoin")
```

**Popular Metrics:**
| Category | Metrics |
|----------|---------|
| Market | `price_usd`, `volume_usd`, `marketcap_usd` |
| On-Chain | `daily_active_addresses`, `transaction_volume`, `network_growth` |
| Exchange | `exchange_inflow`, `exchange_outflow`, `exchange_balance` |
| Valuation | `mvrv_ratio`, `nvt` |
| Social | `sentiment_balance`, `social_volume_total` |
| Development | `dev_activity` |

---

## Parameters Reference

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `slug` | str | required | Asset identifier (e.g., "bitcoin", "ethereum") |
| `slugs` | list | required (get_many) | List of asset identifiers |
| `from_date` | str/datetime | utc_now-365d | Start date (ISO8601 or datetime) |
| `to_date` | str/datetime | utc_now | End date (ISO8601 or datetime) |
| `interval` | str | "1d" | Data interval: "1h", "1d", "1w", "toStartOfDay", etc. |

### Special Date Formats

```python
# Relative dates
from_date="utc_now-30d"
from_date="utc_now-7d"
from_date="utc_now-1h"

# Absolute dates
from_date="2024-01-01"
from_date="2024-01-01T00:00:00Z"
```

### Transformations

```python
transform={"type": "moving_average", "moving_average_base": 100}
transform={"type": "consecutive_differences"}
transform={"type": "percent_change"}
```

---

## Utility Functions

### Available Metrics

```python
# List all available metrics
metrics = san.available_metrics()

# List metrics for specific asset
metrics = san.available_metrics_for_slug("bitcoin")

# When metric became available for asset
since = san.available_metric_for_slug_since("daily_active_addresses", "bitcoin")
```

### Metric Metadata

```python
meta = san.metadata(
    "nvt",
    arr=["availableSlugs", "defaultAggregation", "humanReadableName", 
         "isAccessible", "isRestricted", "restrictedFrom", "restrictedTo"]
)
```

### Rate Limit Management

```python
import time

try:
    df = san.get("price_usd", slug="bitcoin")
except Exception as e:
    if san.is_rate_limit_exception(e):
        seconds = san.rate_limit_time_left(e)
        time.sleep(seconds)

# Check remaining calls
calls_remaining = san.api_calls_remaining()
# Returns: {'month_remaining': '...', 'hour_remaining': '...', 'minute_remaining': '...'}

calls_made = san.api_calls_made()  # List of (datetime, count) tuples
```

### Metric Complexity

```python
complexity = san.metric_complexity(
    metric="price_usd",
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d"
)
# Max complexity: 50000. If exceeded, break request into smaller chunks.
```

---

## Non-Standard Queries

### OHLCV Data

```python
df = san.get(
    "ohlcv/bitcoin",
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d"
)
```

### Historical Balance

```python
df = san.get(
    "historical_balance",
    slug="santiment",
    address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
    from_date="2024-01-01",
    to_date="2024-02-01"
)
```

### Top Transactions

```python
# ETH transactions
df = san.get(
    "eth_top_transactions",
    slug="santiment",
    from_date="2024-01-01",
    to_date="2024-02-01",
    limit=10,
    transaction_type="ALL"  # "ALL", "IN", "OUT"
)

# Token transfers
df = san.get(
    "token_top_transactions",
    slug="santiment",
    from_date="2024-01-01",
    to_date="2024-02-01",
    limit=10
)

# Top transfers
df = san.get(
    "top_transfers",
    slug="santiment",
    address="0x...",
    transaction_type="ALL",
    from_date="utc_now-30d",
    to_date="utc_now"
)
```

### Project Information

```python
# All projects
projects = san.get("projects/all")

# Specific project
project = san.get("project/santiment")
```

### Emerging Trends

```python
df = san.get(
    "emerging_trends",
    from_date="2024-01-01",
    to_date="2024-01-02",
    interval="1d",
    size=10
)
```

---

## Error Handling

```python
from san.error import SanError

try:
    df = san.get("price_usd", slug="invalid-slug")
except SanError as e:
    print(f"API Error: {e}")
```

---

## References

- [references/graphql.md](references/graphql.md) - GraphQL API patterns and examples
- [references/exploration.md](references/exploration.md) - How to discover metrics and build queries
- [references/demo-ideas.md](references/demo-ideas.md) - **20 demo ideas from simple to complex**

For detailed API documentation, see [Santiment Academy](https://academy.santiment.net/).
