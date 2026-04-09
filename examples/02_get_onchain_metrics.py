import san

# =========================================================
# Example 2: Fetching On-Chain Metrics
# =========================================================

# Santiment specializes in on-chain data. 
# This example fetches 'daily_active_addresses', a key metric for network usage.

try:
    # Fetch Daily Active Addresses for Ethereum
    print("Fetching Ethereum Daily Active Addresses...")
    
    # Note: Some on-chain metrics might require a paid API plan for real-time data,
    # but historical data is often available for free with a lag.
    df = san.get(
        "daily_active_addresses",
        slug="ethereum",
        from_date="2023-06-01",
        to_date="2023-06-07",
        interval="1d"
    )

    print("\nResult DataFrame:")
    print(df)
    
    # Other useful on-chain metrics:
    # - "network_growth" (New addresses created)
    # - "transaction_volume"
    # - "mvrv_usd" (Market Value to Realized Value)

except Exception as e:
    print(f"An error occurred: {e}")
