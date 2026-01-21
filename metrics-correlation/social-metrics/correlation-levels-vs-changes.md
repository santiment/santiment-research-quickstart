# Correlation for Social Metrics: Levels vs. % Changes

## Executive summary

When correlating **social metrics** (social volume, sentiment, dominance, etc.) with **price**, the “right” choice depends on what you want correlation to mean:

- **If you want a tradable / timing relationship (predictive or contemporaneous)** → correlate **changes** (typically log-differences / returns) and use **lead–lag (cross-)correlation**.
- **If you want a structural / long-run relationship (co-movement of trends)** → levels can be valid **only** after dealing with **non-stationarity** (e.g., cointegration or detrending methods). Otherwise, raw level correlations can be misleading (“spurious correlation”). ([gwern.net](https://gwern.net/doc/economics/1974-granger.pdf?utm_source=chatgpt.com))
- In practice, for a “Social → Price” research pipeline that feeds **anomaly detection**, the best default is a **two-track approach**:
    1. **Short-horizon track:** correlate **changes** + lead–lag
    2. **Long-horizon track:** correlate **detrended levels** or test **cointegration**

---

## 1) Why “levels correlation” often fails in time series

Raw Pearson correlation assumes observations are roughly i.i.d. (or at least not strongly autocorrelated) and that the relationship isn’t dominated by shared trends. Time series like price, social volume, and active addresses often have:

- **trends / regime shifts**
- **strong autocorrelation**
- **time-varying variance**

In those conditions, two unrelated series can show a high correlation simply because both drift over time—classic **spurious regression/correlation**. ([gwern.net](https://gwern.net/doc/economics/1974-granger.pdf?utm_source=chatgpt.com))

**Rule of thumb:** if either series looks like it “wanders” (random-walk-ish), level correlation is suspicious unless you explicitly model the non-stationarity.

---

## 2) Why “% changes correlation” is usually safer (but not always better)

Transforming to **changes** (e.g., Δlog(metric), Δlog(price)) tends to:

- reduce trends (often closer to stationarity)
- reduce spurious correlation risk
- align better with “market timing” questions (does attention *move with* returns?)

This is why finance commonly studies **returns** rather than price levels.

**But changes can throw away signal** when your hypothesis is about *levels*:

- “Sustained attention + sustained price repricing”
- “Adoption trend and valuation trend share a long-run equilibrium”
    
    In those cases, differencing can remove the very relationship you care about.
    

---

## 3) A decision framework (what correlation should mean)

### A. If your goal is **timing / prediction**

Use **changes** and explicitly evaluate **lead–lag**:

**Suggested transforms**

- Price: `r_t = log(P_t) - log(P_{t-1})`
- Social: `s_t = log(1 + M_t) - log(1 + M_{t-1})` (log1p helps with heavy tails / zeros)

**Then compute**

- `corr(s_{t-k}, r_t)` for k in a range (e.g., -48h…+48h) to see whether social tends to lead or lag.
    
    This avoids the trap of only measuring “same-time” correlation when the true relationship is delayed. ([Cross Validated](https://stats.stackexchange.com/questions/133155/how-to-use-pearson-correlation-correctly-with-time-series?utm_source=chatgpt.com))
    

**Why this fits anomaly work**

- You can define anomalies as **unexpected correlation regime shifts**: e.g., “social changes stop leading returns” or “social spikes become unusually predictive.”

### B. If your goal is **structural / long-run co-movement**

Don’t correlate raw levels directly. Use one of:

1. **Cointegration + Error Correction Model (ECM)**
    
    If price and a social metric are both non-stationary but move together in the long run, cointegration formalizes that and yields an interpretable “equilibrium gap” that can itself be a signal/anomaly. ([Users SSC Wisc](https://users.ssc.wisc.edu/~behansen/718/EngleGranger1987.pdf?utm_source=chatgpt.com))
    
2. **Detrended methods (e.g., DCCA)**
    
    Detrended Cross-Correlation Analysis is designed to quantify cross-correlation in **non-stationary** series after removing trends across scales. This is often a practical middle ground when you want “levels-style” relationships without pretending the data is stationary. ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0378437110008800?utm_source=chatgpt.com))
    

**Why this fits anomaly work**

- Long-run “attention–valuation” coupling/decoupling is a narrative-friendly regime feature (good for client-facing insights), while still being statistically defensible.

---

## 4) What we recommend as the default Santiment research setup

### Track 1 (default): Changes + lead–lag correlation

**Use when:** product goal is actionable timing, short/mid-term signals, anomaly alerts.

- Compute transformed changes: `Δlog1p(social_metric)` and `log returns`
- Use rolling windows (e.g., 7d, 30d) and compute:
    - contemporaneous corr
    - max lead corr over a lag grid
    - lag at which corr is maximized (a “lead/lag index”)
- Add significance discipline: autocorrelation reduces effective sample size; naive p-values are too optimistic. ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1746809424002933?utm_source=chatgpt.com))

**Anomaly ideas**

- “Lead flips sign” (social used to lead positively, now leads negatively)
- “Lead collapses” (previously predictive social changes stop mattering)
- “Lag shifts” (market starts reacting faster/slower to social changes)

### Track 2: Detrended levels or cointegration (asset-by-asset)

**Use when:** narrative is about long-run adoption/attention coupling, or when levels are inherently meaningful (e.g., sustained social dominance).

- If you have enough history and stable sampling: test cointegration
- Otherwise: DCCA-style detrended correlation as a robust descriptive metric

**Anomaly ideas**

- “Long-run coupling breaks” (detrended cross-corr drops sharply)
- “Equilibrium gap extremes” (ECM residual unusually large)

---

## 5) Practical notes for social metrics (what usually matters)

Social metrics have quirks that push you toward **robust transforms**:

- heavy tails (viral spikes)
- zeros / discrete jumps (especially for smaller assets)
- platform changes (data-generating process shifts)

**Practical defaults**

- Use `log(1 + x)` before differencing
- Prefer **Spearman** correlation as a robustness check (rank-based), alongside Pearson
- Consider **partial correlation** controlling for market-wide returns (BTC/ETH) when you want “asset-specific social impact”

---

## 6) Clear takeaway

- **For most correlation analysis meant to support tradable signals and anomaly alerts:** use **changes**, and make it **lead–lag** rather than same-time only.
- **For long-run “attention and valuation move together” narratives:** use **cointegration** or **detrended correlation**—not raw level correlation.