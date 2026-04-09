import san

# =========================================================
# Example 1: Fetching Historical Price Data (OHLCV)
# =========================================================

# This example demonstrates how to fetch historical price data for a specific asset.
# 'price_usd' is one of the most common metrics.

try:
    # Fetch daily price (USD) for Bitcoin
    # Parameters:
    # - metric: "price_usd" (you can also use "price_btc", "volume_usd", etc.)
    # - slug: "bitcoin" (the identifier for the asset)
    # - from_date: Start date (ISO format or datetime object)
    # - to_date: End date (ISO format or datetime object)
    # - interval: "1d" (daily data). You can use "1h", "5m", etc.
    
    print("Fetching Bitcoin price data...")
    df = san.get(
        "price_usd",
        slug="bitcoin",
        from_date="2023-01-01",
        to_date="2023-01-31",
        interval="1d"
    )

    # The result is a pandas DataFrame
    print("\nResult DataFrame Head:")
    print(df.head())

    # You can easily access the values
    print(f"\nNumber of data points: {len(df)}")
    
except Exception as e:
    print(f"An error occurred: {e}")
