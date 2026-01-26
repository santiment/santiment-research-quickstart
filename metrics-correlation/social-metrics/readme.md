# Social Metrics Correlation Analysis

This directory contains analysis comparing different social metrics against price action to identify their unique value and predictive power.

## Overview

Social metrics (such as Social Volume, Social Dominance, and Sentiment) often exhibit different relationships with price. By analyzing these correlations, we can determine:
- Which metrics are leading indicators?
- Which metrics are merely coincident or lagging?
- How "unique" is the signal provided by each metric?

## Methodology

The analysis focuses on **Solana (SOL)** as a case study, examining the correlation between daily changes in social metrics and price returns.

### Analysis Parameters

- **Asset**: Solana (SOL)
- **Start Time**: 2023-05-01 00:00
- **End Time**: 2026-01-21 00:00 
- **Data Granularity**: Hourly (1h)
- **Rolling Window**: 7 days

### Data Transformations

To ensure statistical validity and avoid spurious correlations caused by trends:
1. **Price**: Transformed to **Log Returns** (`log(Pt) - log(Pt-1)`).
2. **Social Metrics**: Transformed to **Log Changes** (`log(1 + Mt) - log(1 + Mt-1)`). This handles the heavy-tailed nature of social data and zero values.

## Key Observations

- **Social Dominance** tends to show a stronger correlation with price changes compared to raw social volume, suggesting that *relative* attention is a more potent signal than absolute attention.
- **Positive Sentiment** is highly correlated with Social Volume, indicating that volume spikes are often driven by positive excitement.
- **Rolling Correlations** reveal that the relationship is not static; there are regimes where social metrics strongly lead price, and others where they decouple.

## Files

- `correlation_matrix_pct_SOL.png`: Visualization of the correlation matrix for the analyzed period.
- `correlation-levels-vs-changes.md`: Theoretical background on why we use changes (returns) instead of raw levels for correlation.
