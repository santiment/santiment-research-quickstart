---
name: santiment-api
description: Query and fetch cryptocurrency and blockchain data using Santiment GraphQL API via sanpy library. Use when you need price, on-chain, social, development, or other crypto metrics. Supports single metrics, multi-asset queries, batching, SQL, raw GraphQL, and versioned metrics such as social v2.0.
---

# Santiment API

Use this skill when you need Santiment market, on-chain, social, or development data in Python.

## Setup

Install:

```bash
pip install sanpy==0.12.3
```

Configure an API key before querying:

```python
import san

# Repo-local convention
# .env -> SAN_API_KEY=...

# sanpy environment variable
# export SANPY_APIKEY="your_api_key"

# Fallback
san.ApiConfig.api_key = "your_api_key"
```

Get an API key from [Santiment Account](https://app.santiment.net/account).

## Choose the Right Access Pattern

- Use `san.get(...)` for one metric on one asset.
- Use `san.get_many(...)` for one metric across multiple assets.
- Use `AsyncBatch` for multiple independent queries.
- Use `san.graphql.execute_gql(...)` for versioned metrics, custom selectors, or custom shapes.
- Use `san.execute_sql(...)` only when you explicitly need ClickHouse-style SQL access.

## Core Patterns

### 1. Single Metric

```python
import san

df = san.get(
    "daily_active_addresses",
    slug="ethereum",
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d",
)
```

### 2. Multiple Assets

```python
df = san.get_many(
    "price_usd",
    slugs=["bitcoin", "ethereum", "solana"],
    from_date="2024-01-01",
    to_date="2024-02-01",
    interval="1d",
)
```

### 3. Batch Queries

```python
from san import AsyncBatch

batch = AsyncBatch()
batch.get("price_usd", slug="bitcoin", from_date="2024-01-01", to_date="2024-02-01")
batch.get("daily_active_addresses", slug="ethereum", from_date="2024-01-01", to_date="2024-02-01")

btc_price, eth_daa = batch.execute(max_workers=10)
```

### 4. Raw GraphQL

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

### 5. Versioned Metrics (Use This for v2)

If the task explicitly asks for `version="2.0"` data, use GraphQL.

```python
import san

meta = san.graphql.execute_gql("""
{
  getMetric(metric: "social_volume_total") {
    metadata {
      availableVersions { version }
      internalMetric
    }
  }
}
""")

print(meta["getMetric"]["metadata"])
```

```python
import san

social_volume_v2 = san.graphql.execute_gql("""
{
  getMetric(metric: "social_volume_total", version: "2.0") {
    timeseriesData(
      slug: "bitcoin"
      from: "utc_now-30d"
      to: "utc_now"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")

social_dominance_v2 = san.graphql.execute_gql("""
{
  getMetric(metric: "social_dominance_total", version: "2.0") {
    timeseriesData(
      slug: "bitcoin"
      from: "utc_now-30d"
      to: "utc_now"
      interval: "1d"
    ) {
      datetime
      value
    }
  }
}
""")
```

Rules for versioned metrics:

- Use client-facing names like `social_volume_total` and `social_dominance_total`.
- Put `version: "2.0"` on `getMetric(...)`, not on `timeseriesData(...)`.
- Prefer `san.graphql.execute_gql(...)` over `san.get(..., version="2.0")`.
- Validate `availableVersions` first when versioning matters.

### 6. SQL Access

```python
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
        metric_id = get_metric_id({{metric}})
    GROUP BY dt, metric_id, asset_id
    ORDER BY dt ASC
    """,
    parameters={"slug": "bitcoin", "metric": "daily_active_addresses"},
    set_index="dt",
)
```

## Common Discovery Helpers

```python
import san

all_metrics = san.available_metrics()
btc_metrics = san.available_metrics_for_slug("bitcoin")
since = san.available_metric_for_slug_since("daily_active_addresses", "bitcoin")
```

## Practical Defaults

- Use `slug` for normal asset queries.
- Use `selector` only when the metric needs a contract, organization, label, or other custom target.
- Use `interval="1d"` unless the task explicitly needs higher frequency.
- Use relative dates like `utc_now-30d` for quick exploratory queries.
- Keep the main skill lightweight; use the references for long-tail patterns.

## References

- [references/graphql-versioned-metrics.md](references/graphql-versioned-metrics.md): versioned metrics such as social v2.0
- [references/versioned-metrics-2.0-recommended.md](references/versioned-metrics-2.0-recommended.md): recommended client-facing metric names with `2.0`
- [references/versioned-metrics-2.0-inventory.md](references/versioned-metrics-2.0-inventory.md): live-verified inventory of metric names exposing `2.0`
- [references/graphql.md](references/graphql.md): general GraphQL patterns, selectors, and metadata
- [references/exploration.md](references/exploration.md): metric discovery and exploration workflow
- [references/demo-ideas.md](references/demo-ideas.md): reusable analysis ideas
- [Santiment Academy](https://academy.santiment.net/)
