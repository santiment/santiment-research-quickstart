---
name: santiment-api
description: Fetch Santiment crypto metrics with stable defaults. Prefer san.get and san.get_many. Use GraphQL only for metadata inspection, custom selectors, or custom response shapes.
---

# Santiment API

Use this skill when you need Santiment market, on-chain, social, or development data in Python.

## Preconditions

- The repository must already be installed with `pip install -r requirements.txt`.
- The Santiment API key must be available via `SAN_API_KEY`.
- Reuse the repository bootstrap helper in `scripts/bootstrap_sanpy.py` instead of redefining API auth in each script.

## Decision Order

1. Prefer `san.get(...)` for ordinary single-series retrieval.
2. Prefer `san.get_many(...)` for one metric across many slugs.
3. Prefer `san.get(..., version="2.0")` for versioned timeseries when the default output is enough.
4. Use GraphQL only for metadata inspection, custom selectors, or custom response shapes.
5. Use SQL only when explicitly required.

## Routing Rules

### Rule 1

Single metric + single asset + ordinary timeseries -> `san.get(...)`

### Rule 2

Single metric + many assets -> `san.get_many(...)`

### Rule 3

If the request explicitly asks for `2.0` and still wants the normal timeseries result -> `san.get(..., version="2.0")`

Do not jump to GraphQL just because the request mentions `2.0`.

### Rule 4

Only use GraphQL when at least one of these is true:

- you need `metadata.availableVersions`
- you need a custom response shape
- the selector is more complex than a plain `slug=...`
- you need GraphQL-only fields

### Rule 5

Only use `san.execute_sql(...)` when the user explicitly asks for SQL or the task clearly requires ClickHouse-style querying.

## Defaults

- Use `slug` unless the task clearly requires a selector.
- Default to `interval="1d"` unless the task explicitly needs intraday data.
- Use relative dates like `utc_now-30d` for exploratory requests.
- Before writing new code, inspect the closest example in `examples/`.
- Prefer adapting an existing example over inventing a new pattern.

## Example Selection

- Ordinary single-asset series -> start from `examples/01_get_price_data.py`
- On-chain single-asset series -> start from `examples/02_get_onchain_metrics.py`
- Social single-asset series -> start from `examples/03_get_social_metrics.py`
- Multi-asset single metric -> start from `examples/05_get_many_assets.py`
- Metric discovery -> start from `examples/06_get_available_metrics.py`

Only move to raw GraphQL or SQL when the examples and routing rules say the normal path is not enough.

## Minimal Patterns

### Standard Timeseries

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

df = san.get(
    "daily_active_addresses",
    slug="ethereum",
    from_date="utc_now-30d",
    to_date="utc_now",
    interval="1d",
)
```

### Many Assets

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

df = san.get_many(
    "price_usd",
    slugs=["bitcoin", "ethereum", "solana"],
    from_date="utc_now-30d",
    to_date="utc_now",
    interval="1d",
)
```

### Versioned Standard Timeseries

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

df = san.get(
    "social_volume_total",
    slug="bitcoin",
    from_date="utc_now-30d",
    to_date="utc_now",
    interval="1d",
    version="2.0",
)
```

### GraphQL Metadata Inspection

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

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
```

### GraphQL Custom Selector

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesData(
      selector: {slugs: ["bitcoin", "ethereum", "solana"]}
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

### SQL Only When Explicitly Needed

```python
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.bootstrap_sanpy import configure_san
import san

configure_san()

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

## Common Helpers

```python
import san

all_metrics = san.available_metrics()
btc_metrics = san.available_metrics_for_slug("bitcoin")
since = san.available_metric_for_slug_since("daily_active_addresses", "bitcoin")
```

## Do Not

- Do not mix multiple auth styles inside generated code.
- Do not default to raw GraphQL for simple timeseries.
- Do not default to GraphQL just because the request mentions `2.0`.
- Do not use SQL unless the task explicitly needs it.

## References

- [references/graphql-versioned-metrics.md](references/graphql-versioned-metrics.md): when version inspection or custom versioned GraphQL is actually needed
- [references/versioned-metrics-2.0-inventory.md](references/versioned-metrics-2.0-inventory.md): live-verified inventory of metric names exposing `2.0`
- [references/graphql.md](references/graphql.md): GraphQL-only patterns
- [references/exploration.md](references/exploration.md): metric discovery workflow
- [references/demo-ideas.md](references/demo-ideas.md): reusable analysis ideas
