# Backtest: Weighted Sentiment Dominance

## Hypothesis

- Sentiment increasing + momentum picking up → Follow the momentum

Why it might work: Trend following strategy would work in general, but often leads to low win rate and quite high drawdowns. In its nature we are betting the trend will be in the right tail of return distribution, then our sentiment data might help with identifying valid breakouts.

## Backtest setup

- Assets: BTC, SOL, ETH, timeframe 1h, 2023-08-01 to 2025-08-10.
- Sentiment source: sentiment ratio * social dominance, time interval 1h

```python
sentiment_soc_dominance = (sentiment_positive / sentiment_negative - 1) * social_dominance
weighted_sentiment_soc_dominance = sentiment_soc_dominance["bitcoin"] * .6 + sentiment_soc_dominance["ethereum"] * .3 + sentiment_soc_dominance["solana"] * .1
```

- Controls: RSI, moving average of sentiment
- Basic cleaning: fill `inf` value with average of 3 previous value


## Strategy sketch

- **Style:** Trend-following
- **Entry:** Go long when RSI > 50 and MA(short term sentiment) > MA(long term sentiment) and current sentiment value > Y
- **Exit:** when 2-day momentum is negative
- **Stop loss**: 20%
- **Take profit**: NA
- **Position sizing:** 33% for each asset
- **Costs:** 0.05% taker fee

## Backtest Results
| Metric | momentum, with current sentiment value > 15 | momentum, with current sentiment value > 18 ✅ | momentum, with current sentiment value > 20 | Only momentum |
| --- | --- | --- | --- | --- |
| Total return | 43.62% | 84.6% | 67.79% | 66.91% |
| CGAR | 19.55% | 35.31% | 29.08% | 28.75% |
| Sharpe | 0.45 | 0.85 | 0.67 | 0.72 |
| Max drawdown | 29.02% | 15.31% | 21.28% | 39.07% |
| Win rate | 34.5% | 37.6% | 37.3% | 26.8% |
| Total trades | 261 | 205 | 177 | 735 |
|  |  |  |  |  |
