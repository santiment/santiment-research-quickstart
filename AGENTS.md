# AGENTS.md - Santiment Research Quickstart

This document provides essential context for AI coding agents working on this repository.

---

## Project Overview

This is a **Python research repository** demonstrating how to use `sanpy`, the official Python client for [Santiment's](https://santiment.net/) cryptocurrency financial, social, and on-chain data API.

**Purpose:**
- Provide concise, working examples for fetching crypto data via Santiment API
- Demonstrate best practices for data analysis with crypto metrics
- Serve as a reference for quantitative research and anomaly detection studies

**Primary Language:** Python (3.x)

---

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| `sanpy` | 0.12.3 | Official Santiment Python API client |
| `pandas` | 2.0.3 | Data manipulation and analysis |
| `numpy` | 1.24.3 | Numerical computing |
| `matplotlib` | 3.7.2 | Data visualization |
| `seaborn` | 0.13.2 | Statistical visualization |

---

## Project Structure

```
santiment-research-quickstart/
├── examples/                     # Runnable example scripts
│   ├── 01_get_price_data.py      # Basic OHLCV price fetching
│   ├── 02_get_onchain_metrics.py # On-chain metrics (DAA, MVRV, etc.)
│   ├── 03_get_social_metrics.py  # Social data (volume, sentiment)
│   ├── 04_get_dev_activity.py    # GitHub development activity
│   ├── 05_get_many_assets.py     # Batch processing multiple assets
│   ├── 06_get_available_metrics.py # Discover available metrics
│   ├── 07_generate_correlation_matrix.py # Correlation analysis
│   └── notebooks/                # Jupyter notebooks
│       └── client_demo_notebook.ipynb  # Interactive walkthrough
├── case-studies/                 # Research reports and analyses
│   ├── research_reports.md       # Index of external research
│   ├── backtest_weighted_sentiment_dominance.md  # Trading strategy backtest
│   ├── data-anomaly-evaluation/  # Anomaly detection studies
│   │   └── anomaly-t-test.md
│   └── README.md                 # Disclaimer for case studies
├── metrics-correlation/          # Correlation analysis outputs
│   └── social-metrics/
│       ├── correlation-levels-vs-changes.md  # Methodology doc
│       ├── readme.md             # Analysis summary
│       └── *.png                 # Generated visualizations
├── skills/                       # Skills for AI agents
│   └── santiment-api/            # Santiment API interaction skill
├── requirements.txt              # Python dependencies
├── .env                          # API key storage (gitignored)
└── readme.md                     # Project documentation
```

---

## Configuration & Environment

### API Key Setup

The project requires a Santiment API key for full data access. The key is configured via environment variables or directly in code:

**Method 1: Environment Variable (Recommended)**
```bash
# Set in .env file (already present, do NOT commit)
SAN_API_KEY=your_api_key_here
```

**Method 2: Inline Configuration**
```python
import san
san.ApiConfig.api_key = "YOUR_API_KEY_HERE"
```

**Important:** The `.env` file is already gitignored. Never commit API keys.

---

## Running Code

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running Examples

```bash
# Run any example script directly
python examples/01_get_price_data.py
python examples/07_generate_correlation_matrix.py
```

### Jupyter Notebooks

```bash
# Start Jupyter to run notebooks
jupyter notebook examples/notebooks/
```

---

## Code Conventions

### Data Access

**Important:** When you need to fetch data from the Santiment API, **DO NOT** write raw `sanpy` code or scripts. Instead, use the provided **skills** (e.g., `santiment-api`).

- **Skill Usage:** Invoke the `santiment-api` skill to fetch price, social metrics, on-chain data, etc.
- **Reference:** See `skills/santiment-api/` for implementation details (but simply call the skill).

### Common Metrics Reference

| Category | Metric Name | Description |
|----------|-------------|-------------|
| Price | `price_usd`, `price_btc` | Asset price |
| Price | `volume_usd` | Trading volume |
| On-chain | `daily_active_addresses` | Unique active addresses |
| On-chain | `transaction_volume` | On-chain transaction volume |
| On-chain | `network_growth` | New addresses created |
| On-chain | `mvrv_usd` | Market Value to Realized Value |
| Social | `social_volume_total` | Total social mentions |
| Social | `social_dominance_total` | % of total crypto social volume |
| Social | `sentiment_positive_total` | Positive sentiment count |
| Social | `sentiment_negative_total` | Negative sentiment count |
| Development | `dev_activity` | GitHub development activity |

### Data Transformations Best Practice

When analyzing correlations between price and social metrics, use these transformations:

```python
# Price: Log returns
price_returns = np.log(df['price']).diff()

# Social metrics: Log changes (handles zeros and heavy tails)
social_changes = np.log(1 + df['social_volume']).diff()
```

See `metrics-correlation/social-metrics/correlation-levels-vs-changes.md` for detailed methodology.

---

## Testing Strategy

**This project does not have a formal test suite.** The examples serve as:
- Integration tests against the live Santiment API
- Documentation that must remain runnable
- Validation of API patterns

When modifying code:
1. Run affected example scripts to verify they still work
2. Check that API responses return expected data
3. Verify data transformations produce valid results

---

## Documentation Standards

### Markdown Files

- Research reports and case studies use Markdown format
- Include clear hypothesis, methodology, and results sections
- Reference external resources with full URLs
- **External Content Access:** Some research files serve as indices or summaries. You MUST visit the links within these files to access the full content, data, or external reports.

### Code Comments

- Use block comments for section headers
- Explain "why" not just "what"
- Document API limitations or requirements in comments

---

## Security Considerations

1. **API Keys:** The `.env` file contains sensitive credentials. Never commit it.
2. **Data Validation:** Ensure data integrity by cross-referencing with known sources when possible.
3. **No Production Code:** This is a research repository; examples are not production-ready trading systems.

---

## External Resources

- [SanPy Official Documentation](https://github.com/santiment/sanpy)
- [Santiment Metrics Catalog](https://api.santiment.net/)
- [Get API Key](https://app.santiment.net/account)

---

## Common Tasks

### Adding a New Example Script

1. Follow the naming convention: `NN_description.py` where NN is sequence number
2. Include header comment with description
3. Use try-except for error handling
4. Add reference in `readme.md` repository structure section

### Adding a New Research Case Study

1. Create markdown file in `case-studies/`
2. Include disclaimer notice (refer to `case-studies/README.md`)
3. Document methodology, data sources, and limitations
4. Add entry to `research_reports.md` if linking to external resources

### Updating Dependencies

1. Modify `requirements.txt`
2. Test all example scripts
3. Document any breaking changes in commit message
