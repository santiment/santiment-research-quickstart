# Anomaly HAC t-test

## Introduction

This case study focuses on the evaluation of data anomalies using the HAC (Heteroskedasticity and Autocorrelation Consistent) t-test. The analysis aims to rigorously test the statistical significance of detected anomalies within the dataset, ensuring robustness against common time-series data issues.

### Anomaly id with name

| **id** | **name** | **description** | first record time |
| --- | --- | --- | --- |
| anomaly_157_1681 | mvrv_usd_30d_lower_zone (ETH) | mvrv value drop below theshold | 2024-03-19 |
| anomaly_169 | usdc_borrow_apy | avg borrow apy > threshold, on [aave, compound], on Ethereum network | 2024-01-04 |
| anomaly_173 | hyperliquid_avg_funding_rate | hyperliquid avg funding rate > theshold or < theshold | 2024-06-07 |
| anomaly_174 | large_usdc_usdt_mint | Amount of usdc and usdt mint on Ethereum network > threshold, in past 24 hour | 2021-02-03 |

Below is the HAC t-test result table for anomalies, using ETH as the asset for evaluation.

window_hours is the number of hour that after the anomaly happens

`total_return` and `volatility` column means we compare the performance of ETH during `window_hours`, with control groups with the same length of window, chosen randomly.

### How to Read Each Cell

Each cell contains three key statistical indicators:

1. Mean: X vs Y
    - X (First number) : Average value for the Anomaly group.
    - Y (Second number) : Average value for the Control (baseline) group.
    - Example : Mean: 6.10 vs 4.12 means the metric averaged 6.10 during anomalies compared to 4.12 normally.
2. p=... (P-value)
    - Indicates statistical significance (probability that the difference is just luck).
    - p < 0.05 is considered significant (marked with ✅).
3. d=... (Cohen's d Effect Size)
    - Measures how strong the difference is.
    - Positive d : Anomaly group value > Control group value.
    - Negative d : Anomaly group value < Control group value.
    - Scale : ~0.2 is small, ~0.5 is medium, >0.8 is a large effect.

### Metrics Explained

- Total Return : Net percentage profit/loss (directional movement).
- Volatility : Standard deviation of returns (risk/instability).
Summary : Look for rows with ✅ and high d values to identify time windows where anomalies significantly outperform or behave differently than the market baseline.

| anomaly_id | window_hours | total_return | volatility |
| --- | --- | --- | --- |
| anomaly_157_1681 | 24 | Mean: -5.03 vs 1.13   p=0.0000   d=-1.09 ✅ | Mean: 1.02 vs 0.70   p=0.0000   d=0.77 ✅ |
| anomaly_157_1681 | 72 | Mean: -7.00 vs 0.76   p=0.0001   d=-0.83 ✅ | Mean: 1.06 vs 0.77   p=0.0000   d=0.81 ✅ |
| anomaly_157_1681 | 120 | Mean: -10.71 vs 1.37   p=0.0000   d=-1.17 ✅ | Mean: 1.03 vs 0.72   p=0.0000   d=1.07 ✅ |
| anomaly_157_1681 | 240 | Mean: -14.92 vs 2.77   p=0.0000   d=-1.17 ✅ | Mean: 0.94 vs 0.76   p=0.0000   d=0.71 ✅ |
| anomaly_169 | 24 | Mean: 1.15 vs 0.85   p=0.0528   d=0.06 | Mean: 0.59 vs 0.73   p=0.0000   d=-0.44 ✅ |
| anomaly_169 | 72 | Mean: 2.50 vs 0.08   p=0.0847   d=0.25 | Mean: 0.59 vs 0.78   p=0.0000   d=-0.61 ✅ |
| anomaly_169 | 120 | Mean: 4.03 vs 1.12   p=0.0301   d=0.24 ✅ | Mean: 0.58 vs 0.76   p=0.0000   d=-0.68 ✅ |
| anomaly_169 | 240 | Mean: 9.56 vs 1.63   p=0.0009   d=0.46 ✅ | Mean: 0.61 vs 0.79   p=0.0000   d=-0.70 ✅ |
| anomaly_173 | 24 | Mean: 0.99 vs 0.27   p=0.0084   d=0.14 ✅ | Mean: 0.76 vs 0.73   p=0.0000   d=0.08 ✅ |
| anomaly_173 | 72 | Mean: 3.03 vs 1.00   p=0.0000   d=0.22 ✅ | Mean: 0.78 vs 0.76   p=0.0000   d=0.06 ✅ |
| anomaly_173 | 120 | Mean: 5.46 vs 1.63   p=0.0000   d=0.31 ✅ | Mean: 0.79 vs 0.76   p=0.0000   d=0.08 ✅ |
| anomaly_173 | 240 | Mean: 8.19 vs 3.43   p=0.0000   d=0.26 ✅ | Mean: 0.81 vs 0.78   p=0.0000   d=0.12 ✅ |
| anomaly_174 | 24 | Mean: 1.22 vs 0.34   p=0.1378   d=0.14 | Mean: 0.92 vs 0.73   p=0.0000   d=0.38 ✅ |
| anomaly_174 | 72 | Mean: 1.38 vs 1.17   p=0.4748   d=0.02 | Mean: 0.89 vs 0.75   p=0.0000   d=0.31 ✅ |
| anomaly_174 | 120 | Mean: 2.81 vs 2.45   p=0.2565   d=0.02 | Mean: 0.87 vs 0.77   p=0.0000   d=0.26 ✅ |
| anomaly_174 | 240 | Mean: 4.57 vs 3.04   p=0.2090   d=0.07 | Mean: 0.86 vs 0.76 p=0.0000   d=0.28 ✅ |
