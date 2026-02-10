# API Exploration Guide

How to discover Santiment API capabilities and build correct GraphQL queries.

---

## 1. Discover Available Metrics

### Get All Metrics

```python
import san

# Get all available metrics (global list)
all_metrics = san.available_metrics()
print(f"Total metrics: {len(all_metrics)}")

# Search for specific keywords
price_metrics = [m for m in all_metrics if 'price' in m.lower()]
social_metrics = [m for m in all_metrics if 'social' in m.lower()]
```

### Get Metrics for Specific Asset

```python
import san

# Get all metrics supported by BTC
btc_metrics = san.available_metrics_for_slug("bitcoin")
print(f"Bitcoin supports {len(btc_metrics)} metrics")

# Print first 20
for m in btc_metrics[:20]:
    print(f"  - {m}")
```

### Check Metric Availability

```python
import san

# Check when a metric became available for an asset
since = san.available_metric_for_slug_since("daily_active_addresses", "bitcoin")
print(f"daily_active_addresses for BTC available since: {since}")
```

---

## 2. Get Metric Metadata

Understand detailed information about a metric, including restrictions, aggregation methods, etc:

```python
import san

meta = san.metadata(
    "nvt",
    arr=[
        "humanReadableName",      # Human readable name
        "availableSlugs",         # List of supported assets (can be large)
        "defaultAggregation",     # Default aggregation (AVG, SUM, etc.)
        "dataType",               # Data type
        "unit",                   # Unit
        "isAccessible",           # Accessible with current API key
        "isRestricted",           # Whether restricted
        "restrictedFrom",         # Restriction start time
        "restrictedTo",           # Restriction end time
        "minInterval",            # Minimum available interval
    ]
)

print(meta)
```

Example output:
```python
{
    'humanReadableName': 'NVT (Using Circulation)',
    'availableSlugs': ['bitcoin', 'ethereum', ...],
    'defaultAggregation': 'AVG',
    'dataType': 'FLOAT',
    'unit': 'RATIO',
    'isAccessible': True,
    'isRestricted': True,
    'restrictedFrom': '2020-03-21T08:44:14Z',
    'restrictedTo': '2020-06-17T08:44:14Z',
    'minInterval': '1d'
}
```

---

## 3. Explore Using GraphQL Playground

Santiment provides a GraphQL Playground for interactive API exploration:

**URL**: https://api.santiment.net/graphiql

### Playground Features:

1. **Autocomplete**: Press `Ctrl+Space` to see available fields
2. **Documentation Panel**: Click "Docs" on the right to see full Schema
3. **Query Validation**: Real-time query syntax checking

### Exploration Steps:

```graphql
# 1. First check available queries
{
  __schema {
    queryType {
      fields {
        name
        description
      }
    }
  }
}

# 2. Check getMetric parameters
{
  __type(name: "Query") {
    fields {
      name
      args {
        name
        type {
          name
        }
      }
    }
  }
}
```

---

## 4. Common Exploration Patterns

### Pattern A: Get Asset List

```python
import san
import pandas as pd

# Get all projects
projects = san.get("projects/all")
print(projects[['name', 'slug', 'ticker']].head(20))

# Search for specific projects
eth_projects = projects[projects['slug'].str.contains('eth', case=False)]
print(eth_projects[['name', 'slug']])
```

### Pattern B: Test Metric Availability

```python
import san
from san.error import SanError

def test_metric(metric, slug="bitcoin"):
    """Test if metric is available"""
    try:
        df = san.get(metric, slug=slug, from_date="utc_now-7d", to_date="utc_now")
        print(f"✅ {metric}: Available, recent data: {len(df)} rows")
        return True
    except SanError as e:
        print(f"❌ {metric}: {e}")
        return False

# Test multiple metrics
test_metrics = ['price_usd', 'daily_active_addresses', 'nvt', 'mvrv_ratio']
for m in test_metrics:
    test_metric(m)
```

### Pattern C: Explore Data Range

```python
import san

# Check metric data time range
metric = "price_usd"
slug = "bitcoin"

since = san.available_metric_for_slug_since(metric, slug)
print(f"{metric} for {slug} has data from {since}")

# Get latest data point
df = san.get(metric, slug=slug, from_date="utc_now-1d", to_date="utc_now")
print(f"Latest data: {df.index[-1]} = {df['value'].iloc[-1]}")
```

---

## 5. Explore Schema from Python

### Get All Query Types

```python
import san

# Get available query list
result = san.graphql.execute_gql("""
{
  __schema {
    queryType {
      fields {
        name
        description
        type {
          name
        }
      }
    }
  }
}
""")

queries = result['__schema']['queryType']['fields']
for q in queries[:10]:
    print(f"{q['name']}: {q['description'][:80] if q['description'] else 'N/A'}...")
```

### Get Metric Type Details

```python
import san

result = san.graphql.execute_gql("""
{
  __type(name: "Metric") {
    fields {
      name
      type {
        name
      }
      description
    }
  }
}
""")

fields = result['__type']['fields']
for f in fields:
    print(f"  {f['name']}: {f.get('description', 'N/A')[:60]}...")
```

---

## 6. Query Building Workflow

### Step 1: Determine Data Type

```python
# First determine what type of data you need:
# - Time series data → Use getMetric + timeseriesData
# - Project information → Use projectBySlug
# - Multiple asset comparison → Use timeseriesDataPerSlug
# - List data → Use allProjects
```

### Step 2: Validate Metric Name

```python
import san

# Method 1: Check available list
available = san.available_metrics_for_slug("bitcoin")
if "price_usd" in available:
    print("✅ price_usd available")

# Method 2: Try to get metadata
try:
    meta = san.metadata("price_usd", arr=["humanReadableName"])
    print(f"✅ {meta}")
except:
    print("❌ Metric doesn't exist or not accessible")
```

### Step 3: Build and Test Query

```python
import san
from san.error import SanError

# Start with small range for testing
query = """
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      slug: "bitcoin"
      from: "utc_now-3d"
      to: "utc_now"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
"""

try:
    result = san.graphql.execute_gql(query)
    data = result['getMetric']['timeseriesData']
    print(f"✅ Query successful, got {len(data)} rows")
    print(f"Example: {data[0]}")
except SanError as e:
    print(f"❌ Error: {e}")
```

### Step 4: Expand Query

```python
# After successful test, expand date range or add parameters
query = """
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      slug: "bitcoin"
      from: "2024-01-01T00:00:00Z"
      to: "2024-02-01T00:00:00Z"
      interval: "1d"
      transform: {type: "moving_average", moving_average_base: 7}
    ) {
      datetime
      value
    }
  }
}
"""
```

---

## 7. Utility Functions

```python
import san
import pandas as pd
from san.error import SanError

class SantimentExplorer:
    """Santiment API Exploration Tool"""
    
    @staticmethod
    def find_metrics(pattern, slug="bitcoin"):
        """Search for matching metrics"""
        metrics = san.available_metrics_for_slug(slug)
        matches = [m for m in metrics if pattern.lower() in m.lower()]
        return sorted(matches)
    
    @staticmethod
    def compare_metrics(metrics, slug="bitcoin", days=7):
        """Compare availability of multiple metrics"""
        results = []
        for metric in metrics:
            try:
                meta = san.metadata(metric, arr=["humanReadableName", "isAccessible"])
                since = san.available_metric_for_slug_since(metric, slug)
                results.append({
                    'metric': metric,
                    'name': meta.get('humanReadableName', 'N/A'),
                    'accessible': meta.get('isAccessible', False),
                    'available_since': since
                })
            except Exception as e:
                results.append({
                    'metric': metric,
                    'name': 'ERROR',
                    'accessible': False,
                    'error': str(e)
                })
        return pd.DataFrame(results)
    
    @staticmethod
    def get_metric_info(metric):
        """Get complete information about a metric"""
        try:
            meta = san.metadata(
                metric,
                arr=["humanReadableName", "dataType", "unit", 
                     "defaultAggregation", "minInterval",
                     "isAccessible", "isRestricted"]
            )
            return meta
        except Exception as e:
            return {'error': str(e)}

# Usage examples
explorer = SantimentExplorer()

# Find all price-related metrics
price_metrics = explorer.find_metrics("price", "bitcoin")
print(f"Found {len(price_metrics)} price-related metrics")

# Get detailed metric info
info = explorer.get_metric_info("mvrv_ratio")
print(info)

# Compare multiple metrics
comparison = explorer.compare_metrics(
    ['price_usd', 'nvt', 'mvrv_ratio', 'daily_active_addresses'],
    slug='bitcoin'
)
print(comparison)
```

---

## 8. Troubleshooting Common Issues

### Issue: Metric Not Found

```python
# Error: Unknown metric
# Solution: Check spelling, use available_metrics_for_slug to verify

metrics = san.available_metrics_for_slug("bitcoin")
similar = [m for m in metrics if 'active' in m.lower()]
print(f"Similar metrics: {similar[:10]}")
```

### Issue: Empty Data

```python
# Possible reasons:
# 1. Date range too early (metric didn't have data then)
# 2. Asset doesn't support this metric
# 3. Need higher permission API key

# Check available time
since = san.available_metric_for_slug_since("some_metric", "bitcoin")
print(f"Data available from {since}")

# Check if restricted
meta = san.metadata("some_metric", arr=["isAccessible", "isRestricted"])
print(meta)
```

### Issue: Complexity Too High

```python
# Error: Complexity limit exceeded
# Solution: Reduce date range or increase interval

# Check complexity
complexity = san.metric_complexity(
    metric="price_usd",
    from_date="2020-01-01",
    to_date="2024-01-01",
    interval="1h"  # Might be too high
)
print(f"Complexity: {complexity} (limit: 50000)")

# Use larger interval
complexity = san.metric_complexity(
    metric="price_usd",
    from_date="2020-01-01",
    to_date="2024-01-01",
    interval="1d"  # More reasonable
)
```
