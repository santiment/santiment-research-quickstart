import san
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Parameters
ASSET = "solana"
START_DATE = "2025-06-01"
END_DATE = "2025-11-01"
ROLLING_WINDOW = 30  # days

print(f"Fetching data for {ASSET} from {START_DATE} to {END_DATE}...")

try:
    # 1. Fetch Price
    price = san.get(
        "price_usd",
        slug=ASSET,
        from_date=START_DATE,
        to_date=END_DATE,
        interval="1d"
    )
    price.columns = ['price']

    # 2. Fetch Social Metrics
    social_vol = san.get(
        "social_volume_total",
        slug=ASSET,
        from_date=START_DATE,
        to_date=END_DATE,
        interval="1d"
    )
    social_vol.columns = ['social_volume']

    social_dom = san.get(
        "social_dominance_total",
        slug=ASSET,
        from_date=START_DATE,
        to_date=END_DATE,
        interval="1d"
    )
    social_dom.columns = ['social_dominance']
    
    # Sentiment
    sentiment_pos = san.get(
        "sentiment_positive_total",
        slug=ASSET,
        from_date=START_DATE,
        to_date=END_DATE,
        interval="1d"
    )
    sentiment_pos.columns = ['sentiment_pos']
    
    sentiment_neg = san.get(
        "sentiment_negative_total",
        slug=ASSET,
        from_date=START_DATE,
        to_date=END_DATE,
        interval="1d"
    )
    sentiment_neg.columns = ['sentiment_neg']

    # Merge all
    df = pd.concat([price, social_vol, social_dom, sentiment_pos, sentiment_neg], axis=1)
    
    # Drop NaNs
    df = df.dropna()
    
    print(f"Data fetched. Shape: {df.shape}")

    # 3. Transform to Changes (Log returns for price, % change for others or log change)
    # Using simple pct_change for simplicity as per common practice, or log diff
    # correlation-levels-vs-changes.md suggests:
    # Price: log(Pt) - log(Pt-1)
    # Social: log(1+Mt) - log(1+Mt-1)
    
    df_log = pd.DataFrame()
    df_log['price_ret'] = np.log(df['price']).diff()
    df_log['social_vol_chg'] = np.log(1 + df['social_volume']).diff()
    df_log['social_dom_chg'] = np.log(1 + df['social_dominance']).diff()
    df_log['sentiment_pos_chg'] = np.log(1 + df['sentiment_pos']).diff()
    df_log['sentiment_neg_chg'] = np.log(1 + df['sentiment_neg']).diff()
    
    df_log = df_log.dropna()
    
    # 4. Correlation
    # Overall correlation on changes
    corr_matrix = df_log.corr()
    
    print("\nCorrelation Matrix (Changes):")
    print(corr_matrix)
    
    # 5. Rolling Correlation (e.g. Price vs Social Volume)
    # The user asked to mention "rolling window". 
    # Usually this implies we look at how correlation evolves, OR we use a rolling window to smooth the data BEFORE correlation?
    # No, usually "rolling correlation" means corr(x, y) over a sliding window.
    # But "Mention rolling window" in README might refer to the window size used for a specific analysis.
    # I'll calculate one example.
    
    rolling_corr = df_log['price_ret'].rolling(window=ROLLING_WINDOW).corr(df_log['social_vol_chg'])
    
    print(f"\nRolling Correlation (Window={ROLLING_WINDOW}d) calculated. Last value: {rolling_corr.iloc[-1]:.4f}")

except Exception as e:
    print(f"Error: {e}")
