# Santiment Data Anomalies as Conditional Market-State Features

This folder archives the June 2026 data anomaly event-study package.

See the case-study disclaimer in [../README.md](../../README.md). This material is for research and education only. It is not financial advice, not a trading recommendation, and not evidence of a standalone trading strategy.

## Scope

- Data anomalies: `social_dev_score`, `eth_whale_dump`, `price_network_activity_divergence`, `project_in_trends`
- Asset universe: mapped Binance spot USDT markets
- Source window: 2023-01-01 through 2026-05-28
- Evaluated sample: 1,211 unique anomaly events across 34 assets
- Design: event study with same-asset, hour-of-week matched controls

## Main Files

- `data_anomaly_event_study.pdf`: reviewed paper.
- `data_anomaly_event_study.tex`: LaTeX source for the reviewed paper.
- `manifest.json`: publication manifest for the archived run.
- `figures/`: paper figures and diagnostics.
- `tables/`: primary and sensitivity result tables.
- `data/`: event, control, raw event, study-event, and hourly Binance price datasets used by the paper.
- `reproducibility/`: original generation scripts from the `anomaly_evaluation` workflow.

## Reader Notes

The final review pass reused the existing CSVs, tables, figures, and manifest; it did not refetch market or production data. The archived reproducibility scripts were copied for provenance and expect the broader Santiment research workspace, including the `anomaly_evaluation` package and ClickHouse access, if rerun from scratch.

The strongest evidence in this run is for Price/Network Activity Divergence as a volatility and conditional market-state marker. Directional return evidence is anomaly-specific and should not be described as alpha without transaction-cost-aware portfolio testing.
