# Fisher Z–Normalized Rolling Correlation for Social–Price Anomaly Signals

**Version:** v0.9 (WIP)

**Author:** Larry (Signals / Data Anomaly)

**Date:** 2026-01-07

---

## 1) Executive Summary

We are developing an anomaly signal that detects structural changes in the relationship between social attention and price movement.

Method: compute rolling correlation between social volume dynamics and price returns; transform correlation using Fisher Z (arctanh); standardize the transformed series into an anomaly score (z-score) against a historical baseline.

This approach is:

- Statistically grounded (correlation is bounded and heteroskedastic)
- Operationally robust (handles spikes, regime shifts, overlapping windows)
- Client-legible (outputs raw correlation + actionable anomaly score)

## 2) Motivation and Client Value

Social activity often reflects attention rotation, narrative acceleration, coordination effects, and information diffusion. Price responds with time-varying lag.

A dynamic “rolling correlation + anomaly” signal helps:

- detect unusual coupling/decoupling
- identify early narrative momentum
- monitor regime changes where attention stops moving price

## 3) Core Methodology

### 3.1 Data inputs (proposed)

We use changes (not levels) to reduce spurious correlation.

Price:

- r_t = log(P_t) - log(P_{t-1}) (log return)

Social:

- s_t = log(SV_t + c) - log(SV_{t-1} + c)
    
    where SV_t is social volume, c is a small constant to avoid log(0)
    

Optional preprocessing:

- winsorize / clip extreme s_t (spikes are common)
- explicit missing data handling (avoid naive forward-fill for counts)

### 3.2 Rolling correlation

For rolling window W:

- rho_t = corr( r_{t-W+1:t}, s_{t-W+1:t} )

We output rho_t for interpretability, but correlation is bounded in [-1, 1] and its variance is not constant.

### 3.3 Fisher Z transformation

We map correlation into a more stable scale:

- z_t = arctanh(rho_t)
- equivalently: z_t = 0.5 * ln((1 + rho_t) / (1 - rho_t))

Implementation note:

- clamp rho_t into (-1 + eps, 1 - eps) to avoid infinities

### 3.4 Anomaly scoring

Standardize z_t against a baseline window B:

- A_t = (z_t - mean_B) / std_B

Robust option (recommended in noisy markets):

- mean_B -> median_B
- std_B -> 1.4826 * MAD_B

Interpretation:

- A_t >> 0: unusually strong correlation vs recent history
- A_t << 0: unusually weak / inverted correlation vs recent history

## 4) Lags (Lead–Lag Effects)

Same-time correlation is often not maximal. We compute a lag family:

For lag k in {0..K}:

- rho_{t,k} = corr( r_{t-W+1:t}, s_{t-k-W+1:t-k} )
    
    Then compute:
    
- z_{t,k} = arctanh(rho_{t,k})
- A_{t,k} = zscore(z_{t,k} vs baseline)

We can also output:

- best_lag = argmax_k |rho_{t,k}| (or argmax_k |A_{t,k}|)

## 5) Why Fisher Z Improves Reliability

Raw correlation rho is bounded [-1,1], skewed near boundaries, and variance depends on the true correlation + sample size. Fisher Z makes changes more linear and stabilizes variance, making z-scoring more meaningful and reducing geometry-driven false alerts.

## 6) Failure Modes & Mitigations

1. Overlapping windows -> strong autocorrelation in rho_t
    - use robust baseline, set thresholds empirically, optional downsampling
2. Social spikes dominate correlation
    - winsorize/clamp social changes, optional Spearman variant
3. Regime shifts break fixed baselines
    - rolling baseline, dual baseline (short + long), add regime context
4. Shared volatility confounds correlation
    - add volatility companion features; advanced: partial out vol effects

## 7) Validation Plan

- Statistical sanity: distribution stability of rho vs z, sensitivity to W/B, missing data robustness
- Event-based backtests: triggers when |A_t| exceeds threshold; evaluate forward returns, vol expansion, attention persistence
- Case studies: curated episodes showing coupling/decoupling and lag behavior

## 8) Production Considerations

- Additive metrics family (no production impact)
- WIP behind feature flag / optional endpoint
- Outputs: corr_r, corr_z, corr_anom (+ lag variants)

## 9) Conclusion

Using Fisher Z–normalized rolling correlation is a principled way to transform a bounded, heteroskedastic statistic (correlation) into a form suitable for anomaly detection. The methodology is transparent, testable, and easy to operationalize.

Most importantly, we treat this as a living research track: we are implementing it carefully, measuring failure modes explicitly, and planning iterative improvements grounded in validation rather than intuition.

---

## Appendix A: Key Formulas

**Fisher Z:**

$z=\operatorname{arctanh}(r)=\frac12\ln\left(\frac{1+r}{1-r}\right)$

**Inverse:**

$r=\tanh(z)=\frac{e^{2z}-1}{e^{2z}+1}$

**Anomaly score:**

$A_t = \frac{z_t-\mu_{t,B}}{\sigma_{t,B}}$

[Related Work & Rationale](https://www.notion.so/Related-Work-Rationale-2e12a82d136180079598dc04755c56d9?pvs=21)