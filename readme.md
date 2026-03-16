# Santiment Research Quickstart

This repository is a practical starting point for working with Santiment data in Python. It includes runnable `sanpy` examples, research notes, and an AI skill for agent-based access to Santiment metrics.

## API Key Setup

Both workflows in this repository require a Santiment API key.

1. Get your API key from the [Santiment account page](https://app.santiment.net/account).
2. Copy `env.example` to `.env`.
3. Replace the placeholder value with your key.

```bash
cp env.example .env
```

## Two Ways to Use This Repository

There are two clear workflows in this repo:

### If You Are Using an Agent

Use the included `santiment-api` skill.

This is the preferred path when an AI coding agent is working in the repository. The skill gives the agent a structured way to fetch price, on-chain, social, and development metrics without writing raw `sanpy` code for each request.

Skill location:

- [`skills/santiment-api/`](skills/santiment-api/)

Typical setup:

```bash
git clone https://github.com/santiment/santiment-research-quickstart.git
cd santiment-research-quickstart
```

Simply text "Install the santiment-api skill."

Then ask the agent in natural language, for example:

- "Use the `santiment-api` skill to fetch Bitcoin price data for the last 90 days."
- "Compare daily active addresses for Ethereum and Solana."
- "List available metrics for Chainlink."

### If You Are Accessing Santiment Data Manually

Use the scripts in `examples/` or write your own `sanpy` code directly.

This path is better if you want direct control over the code, prefer working in notebooks, or want to learn the underlying `sanpy` API patterns yourself.

Install dependencies:

```bash
pip install -r requirements.txt
cp env.example .env
```

Example:

```python
import san

df = san.get(
    "price_usd",
    slug="bitcoin",
    from_date="2024-01-01",
    to_date="utc_now",
    interval="1d",
)

print(df.head())
```

## Repository Structure

- `skills/`: Skills for AI agents
- `skills/santiment-api/`: Main skill for querying Santiment data
- `examples/`: Runnable Python examples
- `examples/01_get_price_data.py`: Basic price data retrieval
- `examples/02_get_onchain_metrics.py`: On-chain metrics such as daily active addresses and MVRV
- `examples/03_get_social_metrics.py`: Social volume and sentiment examples
- `examples/04_get_dev_activity.py`: Development activity examples
- `examples/05_get_many_assets.py`: Batch retrieval for multiple assets
- `examples/06_get_available_metrics.py`: Metric discovery for assets
- `examples/07_generate_correlation_matrix.py`: Correlation analysis between price and social metrics
- `examples/notebooks/`: Jupyter notebooks
- `examples/notebooks/client_demo_notebook.ipynb`: Interactive walkthrough
- `case-studies/`: Research reports and analysis notes
- `metrics-correlation/`: Correlation studies and generated outputs

## Notes

- If an agent is operating inside this repository, prefer the `santiment-api` skill instead of writing raw `sanpy` calls.
- If you are working manually, the example scripts are the fastest way to get started.
- This repository is for research and exploration, not production trading systems.

## References

- [SanPy documentation](https://github.com/santiment/sanpy)
- [Santiment metrics catalog](https://academy.santiment.net/metrics/)
