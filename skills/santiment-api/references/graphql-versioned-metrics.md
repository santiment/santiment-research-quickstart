# Santiment GraphQL Versioned Metrics

Use this reference when a task explicitly requires metric versions such as `version: "2.0"`.

## Preferred Decision Order

1. Try `san.get(..., version="2.0")` first when you only need the default timeseries output.
2. Use GraphQL metadata when you need to confirm which versions exist.
3. Use GraphQL timeseries queries only when you need a custom selector or a custom response shape.

## When to Use

Use GraphQL versioned queries when:

- the metric has multiple available versions
- you need to confirm which version is exposed before fetching data
- you need a custom GraphQL response shape beyond the default `san.get(...)` timeseries output
- you need a selector that does not fit the standard `slug=...` path

Do not switch to GraphQL just because the user mentioned `2.0`.

`san.get(..., version="2.0")` is supported in `sanpy 0.13.0`. Use GraphQL when you need metadata inspection or a custom query shape.

## Core Rule

Put `version: "2.0"` on `getMetric(...)`, not on `timeseriesData(...)`.

```python
import san

result = san.graphql.execute_gql("""
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

## Check Available Versions First

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

Typical response shape:

```python
{
    "availableVersions": [{"version": "1.0"}, {"version": "2.0"}],
    "internalMetric": "social_volume"
}
```

## Social Metrics v2.0 Examples

### Social Volume Total v2

```python
import san

result = san.graphql.execute_gql("""
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
```

### Social Dominance Total v2

```python
import san

result = san.graphql.execute_gql("""
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

## Naming Rules

- Use client-facing metric names like `social_volume_total` and `social_dominance_total`.
- Do not use internal names like `social_dominance_v2` in `getMetric(...)`.
- Do not use slash-style names like `social_dominance_v2/2.0`.

Common mapping:

- `social_dominance_total` -> internal `social_dominance_v2`
- `social_dominance_total_1h_moving_average` -> internal `social_dominance_1h`
- `social_dominance_total_24h_moving_average` -> internal `social_dominance_24h`

## Practical Notes

- Validate `availableVersions` when version separation matters.
- `san.get(metric, ..., version="2.0")` is the simplest manual path when you just need the default timeseries result.
- Some custom text-query paths can still produce similar v1 and v2 results; verify if the distinction is important to the task.
- Use `interval="1d"` by default unless the task explicitly needs intraday data.
