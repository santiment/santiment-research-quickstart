# Santiment Research Quickstart

Welcome to the **Santiment Research Quickstart**. This repository provides concise examples and best practices for using `sanpy`, the official Python client for Santiment's comprehensive crypto financial, social, and on-chain data.

## Installation

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

Or install manually (including visualization libraries):

```bash
pip install sanpy pandas matplotlib seaborn
```

## Configuration

To access full historical data and advanced metrics, a Santiment API key is required.
[Get your API Key here](https://app.santiment.net/account).

Configure your API key in your script:

```python
import san
san.ApiConfig.api_key = "YOUR_API_KEY_HERE"
```

## Quick Start

Fetch the daily price of Bitcoin:

```python
import san

# Get daily price in USD for Bitcoin
df = san.get("price_usd", slug="bitcoin", from_date="2024-01-01", to_date="utc_now", interval="1d")

print(df.head())
```

## Repository Structure

*   **`examples/`**: Scripts demonstrating key data fetching capabilities.
    *   `01_get_price_data.py`: Basic OHLCV price data fetching.
    *   `02_get_onchain_metrics.py`: On-chain metrics like MVRV and Daily Active Addresses.
    *   `03_get_social_metrics.py`: Social data including Social Volume and Sentiment.
    *   `04_get_dev_activity.py`: Tracking project development activity.
    *   `05_get_many_assets.py`: Efficient batch processing for multiple assets.
    *   `06_get_available_metrics.py`: Discovery of available metrics for specific assets.
*   **`examples/notebooks/`**: Interactive Jupyter Notebooks.
    *   `client_demo_notebook.ipynb`: Comprehensive walkthrough from data validation to alpha discovery.

## Documentation

*   [Official SanPy Documentation](https://github.com/santiment/sanpy)
*   [Available Metrics Catalog](https://api.santiment.net/)
