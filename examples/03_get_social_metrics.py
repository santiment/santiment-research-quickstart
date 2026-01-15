import san

# =========================================================
# Example 3: Fetching Social Metrics
# =========================================================

# Santiment tracks social media discussion (Telegram, Reddit, Twitter, etc.).
# 'social_volume_total' shows the total number of mentions for an asset.

try:
    print("Fetching Social Volume for Solana...")
    
    # Fetch Social Volume Total for Solana
    df = san.get(
        "social_volume_total",
        slug="solana",
        from_date="2023-09-01",
        to_date="2023-09-10",
        interval="1d"
    )

    print("\nResult DataFrame:")
    print(df)

    # Social metrics are great for sentiment analysis.
    # Other metrics:
    # - "social_dominance_total" (% of total social volume)
    # - "sentiment_positive_total"
    # - "sentiment_negative_total"

except Exception as e:
    print(f"An error occurred: {e}")
