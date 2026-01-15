import san

# =========================================================
# Example 6: Fetching Available Metrics
# =========================================================

# It's often useful to know what metrics are available in general 
# or for a specific asset before querying.

try:
    print("Fetching all available metrics...")
    
    # 1. Get a list of ALL available metrics in the Santiment API
    all_metrics = san.available_metrics()
    print(f"Total number of metrics: {len(all_metrics)}")
    print("First 10 metrics:", all_metrics[:10])
    
    print("-" * 50)
    
    # 2. Get available metrics for a specific asset (e.g., Bitcoin)
    # Not all metrics are calculated for all assets (e.g., ERC-20 metrics aren't for Bitcoin).
    slug = "bitcoin"
    print(f"Fetching available metrics for {slug}...")
    
    btc_metrics = san.available_metrics_for_slug(slug)
    print(f"Number of metrics available for {slug}: {len(btc_metrics)}")
    print(f"First 10 metrics for {slug}:", btc_metrics[:10])

    # 3. Check if a specific metric is available for an asset
    metric_to_check = "daily_active_addresses"
    if metric_to_check in btc_metrics:
        print(f"\n'{metric_to_check}' is available for {slug}.")
    else:
        print(f"\n'{metric_to_check}' is NOT available for {slug}.")

except Exception as e:
    print(f"An error occurred: {e}")
