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

## Choose a Workflow

There are two clear workflows in this repo:

### If You Are Using an Agent

Use the included `santiment-api` skill.

This is the preferred path when an AI coding agent is working in the repository. The skill selects the appropriate API access pattern for each request.

Skill location:

- [`skills/santiment-api/`](skills/santiment-api/)

Typical setup:

```bash
git clone https://github.com/santiment/santiment-research-quickstart.git
cd santiment-research-quickstart
```

Tell the agent to use the `santiment-api` skill, then ask for data in natural language. For example:

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

- `skills/santiment-api/`: Agent skill for querying Santiment data
- `examples/`: Runnable Python examples and an interactive notebook
- `case-studies/`: Research reports and analysis notes
- `metrics-correlation/`: Correlation studies and generated outputs

## Notes

- If an agent is operating inside this repository, prefer the `santiment-api` skill instead of writing raw `sanpy` calls.
- If you are working manually, start from the closest script in `examples/` before inventing a new pattern.
- This repository is for research and exploration, not production trading systems.

## References

- [SanPy documentation](https://github.com/santiment/sanpy)
- [Santiment metrics catalog](https://academy.santiment.net/metrics/)
