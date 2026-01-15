import san

# =========================================================
# Example 4: Fetching Development Activity
# =========================================================

# Development activity tracks the work done in the project's public GitHub repositories.
# Pure 'dev_activity' is often a better indicator than just commit counts.

try:
    print("Fetching Development Activity for Cardano...")
    
    # Cardano is known for high development activity.
    df = san.get(
        "dev_activity",
        slug="cardano",
        from_date="2023-01-01",
        to_date="2023-02-01",
        interval="1d"
    )

    print("\nResult DataFrame:")
    print(df.head())

    # This metric is useful for fundamental analysis to see if the team is building.

except Exception as e:
    print(f"An error occurred: {e}")
