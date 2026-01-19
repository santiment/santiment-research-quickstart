# Santiment Research Kit (SanPy)

Welcome to the **Santiment Research Kit**. This repository contains examples and best practices for using `sanpy`, the official Python client for Santiment's on-chain, social, and financial crypto data.

## 🚀 Installation

```bash
pip install sanpy pandas matplotlib seaborn
```

## 🔑 Configuration

To access the full historical data and advanced metrics, you need a Santiment API key.
[Get your API Key here](https://app.santiment.net/account).

```python
import san
san.ApiConfig.api_key = "YOUR_API_KEY_HERE"
```

## ⚡ Quick Start: Hello World

Fetch the daily price of Bitcoin in 3 lines of code:

```python
import san

# Get daily price in USD for Bitcoin
df = san.get("price_usd", slug="bitcoin", from_date="2024-01-01", to_date="utc_now", interval="1d")

print(df.head())
```

## 📂 Repository Structure

*   **`examples/`**: Python scripts for common data fetching tasks.
    *   `01_get_price_data.py`: Basic OHLCV fetching.
    *   `02_get_onchain_metrics.py`: Fetching MVRV, Daily Active Addresses, etc.
    *   `03_get_social_metrics.py`: Social Volume and Sentiment.
    *   `05_get_many_assets.py`: Batch processing for multiple assets.
*   **`examples/notebooks/`**: Jupyter Notebooks for interactive exploration.
    *   `client_demo_notebook.ipynb`: A complete walkthrough from validation to alpha discovery.

## 📚 Documentation

*   [Official SanPy Documentation](https://github.com/santiment/sanpy)
*   [Available Metrics Catalog](https://api.santiment.net/)
