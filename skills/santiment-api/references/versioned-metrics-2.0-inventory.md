# Metrics With `2.0` Available

This document lists metric names whose GraphQL metadata exposed `availableVersions` including `2.0` when checked against the live Santiment API on **March 16, 2026**.

Scope:

- Source: live GraphQL metadata scan
- Check: `getMetric(metric: "...") { metadata { availableVersions { version } } }`
- Result: **132 metric names** with `2.0` available

Notes:

- This inventory can change over time as the API evolves.
- Some names are aliases of the same internal metric.
- Some metrics expose additional labels such as `Experimental (Weighted Age)` alongside `1.0` and `2.0`.

## How To Verify

```python
import san

meta = san.graphql.execute_gql("""
{
  getMetric(metric: "social_volume_total") {
    metadata {
      availableVersions { version }
      internalMetric
    }
  }
}
""")

print(meta["getMetric"]["metadata"])
```

## Community Social Volume

Count: 2

- `community_social_volume_reddit`
- `community_social_volume_telegram`

## Sentiment Balance

Count: 15

- `sentiment_balance_4chan`
- `sentiment_balance_4chan_v2`
- `sentiment_balance_bitcointalk`
- `sentiment_balance_bitcointalk_v2`
- `sentiment_balance_farcaster`
- `sentiment_balance_reddit`
- `sentiment_balance_reddit_v2`
- `sentiment_balance_telegram`
- `sentiment_balance_telegram_v2`
- `sentiment_balance_total`
- `sentiment_balance_total_v2`
- `sentiment_balance_twitter`
- `sentiment_balance_twitter_v2`
- `sentiment_balance_youtube_videos`
- `sentiment_balance_youtube_videos_v2`

## Sentiment Negative

Count: 8

- `sentiment_negative_4chan`
- `sentiment_negative_bitcointalk`
- `sentiment_negative_farcaster`
- `sentiment_negative_reddit`
- `sentiment_negative_telegram`
- `sentiment_negative_total`
- `sentiment_negative_twitter`
- `sentiment_negative_youtube_videos`

## Sentiment Positive

Count: 8

- `sentiment_positive_4chan`
- `sentiment_positive_bitcointalk`
- `sentiment_positive_farcaster`
- `sentiment_positive_reddit`
- `sentiment_positive_telegram`
- `sentiment_positive_total`
- `sentiment_positive_twitter`
- `sentiment_positive_youtube_videos`

## Sentiment Volume Consumed

Count: 7

- `sentiment_volume_consumed_4chan`
- `sentiment_volume_consumed_bitcointalk`
- `sentiment_volume_consumed_reddit`
- `sentiment_volume_consumed_telegram`
- `sentiment_volume_consumed_total`
- `sentiment_volume_consumed_twitter`
- `sentiment_volume_consumed_youtube_videos`

## Sentiment Weighted

Count: 45

- `sentiment_weighted_4chan`
- `sentiment_weighted_4chan_1d`
- `sentiment_weighted_4chan_1d_v2`
- `sentiment_weighted_4chan_1h`
- `sentiment_weighted_4chan_1h_v2`
- `sentiment_weighted_4chan_v2`
- `sentiment_weighted_bitcointalk`
- `sentiment_weighted_bitcointalk_1d`
- `sentiment_weighted_bitcointalk_1d_v2`
- `sentiment_weighted_bitcointalk_1h`
- `sentiment_weighted_bitcointalk_1h_v2`
- `sentiment_weighted_bitcointalk_v2`
- `sentiment_weighted_farcaster`
- `sentiment_weighted_farcaster_1d`
- `sentiment_weighted_farcaster_1h`
- `sentiment_weighted_reddit`
- `sentiment_weighted_reddit_1d`
- `sentiment_weighted_reddit_1d_v2`
- `sentiment_weighted_reddit_1h`
- `sentiment_weighted_reddit_1h_v2`
- `sentiment_weighted_reddit_v2`
- `sentiment_weighted_telegram`
- `sentiment_weighted_telegram_1d`
- `sentiment_weighted_telegram_1d_v2`
- `sentiment_weighted_telegram_1h`
- `sentiment_weighted_telegram_1h_v2`
- `sentiment_weighted_telegram_v2`
- `sentiment_weighted_total`
- `sentiment_weighted_total_1d`
- `sentiment_weighted_total_1d_v2`
- `sentiment_weighted_total_1h`
- `sentiment_weighted_total_1h_v2`
- `sentiment_weighted_total_v2`
- `sentiment_weighted_twitter`
- `sentiment_weighted_twitter_1d`
- `sentiment_weighted_twitter_1d_v2`
- `sentiment_weighted_twitter_1h`
- `sentiment_weighted_twitter_1h_v2`
- `sentiment_weighted_twitter_v2`
- `sentiment_weighted_youtube_videos`
- `sentiment_weighted_youtube_videos_1d`
- `sentiment_weighted_youtube_videos_1d_v2`
- `sentiment_weighted_youtube_videos_1h`
- `sentiment_weighted_youtube_videos_1h_v2`
- `sentiment_weighted_youtube_videos_v2`

## Social Dominance

Count: 24

- `social_dominance_4chan`
- `social_dominance_4chan_1h_moving_average`
- `social_dominance_4chan_24h_moving_average`
- `social_dominance_bitcointalk`
- `social_dominance_bitcointalk_1h_moving_average`
- `social_dominance_bitcointalk_24h_moving_average`
- `social_dominance_farcaster`
- `social_dominance_farcaster_1h_moving_average`
- `social_dominance_farcaster_24h_moving_average`
- `social_dominance_reddit`
- `social_dominance_reddit_1h_moving_average`
- `social_dominance_reddit_24h_moving_average`
- `social_dominance_telegram`
- `social_dominance_telegram_1h_moving_average`
- `social_dominance_telegram_24h_moving_average`
- `social_dominance_total`
- `social_dominance_total_1h_moving_average`
- `social_dominance_total_24h_moving_average`
- `social_dominance_twitter`
- `social_dominance_twitter_1h_moving_average`
- `social_dominance_twitter_24h_moving_average`
- `social_dominance_youtube_videos`
- `social_dominance_youtube_videos_1h_moving_average`
- `social_dominance_youtube_videos_24h_moving_average`

## Social Volume

Count: 8

- `social_volume_4chan`
- `social_volume_bitcointalk`
- `social_volume_farcaster`
- `social_volume_reddit`
- `social_volume_telegram`
- `social_volume_total`
- `social_volume_twitter`
- `social_volume_youtube_videos`

## Unique Social Volume

Count: 15

- `unique_social_volume_4chan_1d`
- `unique_social_volume_4chan_5m`
- `unique_social_volume_bitcointalk_1d`
- `unique_social_volume_bitcointalk_5m`
- `unique_social_volume_farcaster_1d`
- `unique_social_volume_farcaster_5m`
- `unique_social_volume_reddit_1d`
- `unique_social_volume_reddit_5m`
- `unique_social_volume_telegram_1d`
- `unique_social_volume_telegram_5m`
- `unique_social_volume_total_1d`
- `unique_social_volume_total_1h`
- `unique_social_volume_total_5m`
- `unique_social_volume_twitter_1d`
- `unique_social_volume_twitter_5m`

## Summary

- Total metric names with `2.0` available: `132`
- Main families: social volume, social dominance, unique social volume, sentiment balance, sentiment positive/negative, sentiment consumed, and sentiment weighted
- Recommended client-facing examples: `social_volume_total`, `social_dominance_total`
