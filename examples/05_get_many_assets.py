import san

# =========================================================
# Example 5: Fetching Data for Multiple Assets (Batching)
# =========================================================

# If you need the same metric for multiple assets, use 'san.get_many'.
# This is more efficient than calling 'san.get' in a loop.

try:
    assets = ["bitcoin", "ethereum", "ripple", "cardano", "solana"]
    
    print(f"Fetching price for: {assets}")
    
    # Fetch price_usd for all specified assets at once
    df = san.get_many(
        "price_usd",
        slugs=assets,
        from_date="2023-10-01",
        to_date="2023-10-05",
        interval="1d"
    )

    print("\nResult DataFrame (Columns are slugs):")
    print(df)
    
    # The resulting DataFrame has one column per asset.
    # This format is perfect for correlation analysis or portfolio backtesting.

except Exception as e:
    print(f"An error occurred: {e}")
