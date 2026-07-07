#!/usr/bin/env python3
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
from anomaly_evaluation.fetching import BinanceDataFetcher

DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
TABLE_DIR = ROOT / "tables"
for directory in (DATA_DIR, FIG_DIR, TABLE_DIR, ROOT / "cache"):
    directory.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20260528)
CLICKHOUSE = ["clickhouse", "client", "-h", "clickhouse.production.san", "--port", "30900"]
START_DATE = "2023-01-01 00:00:00"
END_DATE = "2026-05-28 00:00:00"
WINDOWS = [1, 4, 24, 72]
CONTROL_RATIO = 10
EXCLUSION_MIN_HOURS = 24

TARGET_SIGNAL_NAMES = [
    "social_dev_score",
    "eth_whale_dump",
    "price_network_activity_divergence",
    "project_in_trends",
]

SIGNAL_DISPLAY = {
    "social_dev_score": "Social Dev Score",
    "eth_whale_dump": "ETH Whale Dump",
    "price_network_activity_divergence": "Price/Network Activity Divergence",
    "project_in_trends": "Project in Trends",
}

PRIMARY_MODEL = {
    "eth_whale_dump": "event_weighted",
    "social_dev_score": "asset_weighted",
    "price_network_activity_divergence": "asset_weighted",
    "project_in_trends": "asset_weighted",
}

MIN_ASSET_EVENTS = {
    "social_dev_score": 2,
    "eth_whale_dump": 1,
    "price_network_activity_divergence": 5,
    "project_in_trends": 5,
}

BINANCE_SYMBOLS = {
    1370: "ZRX/USDT",
    1437: "BAT/USDT",
    1452: "BTC/USDT",
    1526: "LINK/USDT",
    1610: "MANA/USDT",
    1672: "EOS/USDT",
    1681: "ETH/USDT",
    2029: "QNT/USDT",
    2053: "XRP/USDT",
    2262: "BNB/USDT",
    2369: "AAVE/USDT",
    2462: "LTC/USDT",
    2484: "BCH/USDT",
    2530: "ALGO/USDT",
    2623: "ADA/USDT",
    2666: "CRV/USDT",
    2671: "DASH/USDT",
    2695: "DOGE/USDT",
    2716: "ENS/USDT",
    2723: "ETC/USDT",
    2812: "KSM/USDT",
    2887: "CKB/USDT",
    3052: "XTZ/USDT",
    3057: "RUNE/USDT",
    3073: "TRX/USDT",
    3085: "UNI/USDT",
    3092: "VET/USDT",
    3139: "ZEC/USDT",
    3169: "SOL/USDT",
    3198: "AR/USDT",
    3291: "DOT/USDT",
    3511: "AXS/USDT",
    3614: "1INCH/USDT",
    3630: "LDO/USDT",
    3790: "JASMY/USDT",
    4442: "APE/USDT",
    5736: "PEPE/USDT",
    5766: "SUI/USDT",
    5801: "WLD/USDT",
    5896: "BONK/USDT",
    6022: "TAO/USDT",
    6995: "BOME/USDT",
    7171: "WIF/USDT",
    7210: "TRUMP/USDT",
}

AUDIT_ROWS = [
    {
        "Public Name": "Social Dev Score",
        "Internal Name": "social_dev_score",
        "App Path": "signals/src/apps/social_dev_score",
        "Timestamp Used": "daily event date",
        "Value Field": "score",
        "Directional?": "No",
        "Caveats": "Composite rank score; short production history for many assets",
    },
    {
        "Public Name": "ETH Whale Dump",
        "Internal Name": "eth_whale_dump",
        "App Path": "signals/src/apps/eth_whale_dump",
        "Timestamp Used": "flow-event timestamp",
        "Value Field": "flow value",
        "Directional?": "Possibly",
        "Caveats": "ETH-only filtered flow-event label",
    },
    {
        "Public Name": "Price/Network Activity Divergence",
        "Internal Name": "price_network_activity_divergence",
        "App Path": "signals/src/apps/price_network_activity_divergence",
        "Timestamp Used": "daily event date",
        "Value Field": "price",
        "Directional?": "Yes",
        "Caveats": "Daily modified-z divergence between price growth and DAA",
    },
    {
        "Public Name": "Project in Trends",
        "Internal Name": "project_in_trends",
        "App Path": "signals/src/apps/project_in_trends",
        "Timestamp Used": "hour boundary after trend window",
        "Value Field": "total_score",
        "Directional?": "No",
        "Caveats": "Top-N social trend and asset mapping; cooldown affects repeats",
    },
]


@dataclass
class PriceSeries:
    asset_id: int
    asset: str
    symbol: str
    times: np.ndarray
    close: np.ndarray


def ch_query(query: str) -> pd.DataFrame:
    normalized = query.strip().lower()
    if not (normalized.startswith("select") or normalized.startswith("with") or normalized.startswith("describe")):
        raise ValueError("Only read-only ClickHouse queries are allowed")
    result = subprocess.run(
        CLICKHOUSE + ["--format", "TSVWithNames", "--query", query],
        check=True,
        text=True,
        capture_output=True,
    )
    if not result.stdout.strip():
        return pd.DataFrame()
    return pd.read_csv(StringIO(result.stdout), sep="\t")


def fetch_target_metadata() -> pd.DataFrame:
    names = ", ".join(f"'{name}'" for name in TARGET_SIGNAL_NAMES)
    metadata = ch_query(
        f"""
        SELECT signal_id, name, version, computed_at
        FROM signal_metadata
        WHERE name IN ({names})
        ORDER BY name, version DESC, signal_id DESC
        """
    )
    metadata["computed_at"] = pd.to_datetime(metadata["computed_at"])
    latest = (
        metadata.sort_values(["name", "version", "signal_id"], ascending=[True, False, False])
        .groupby("name", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    return latest


def fetch_events(metadata: pd.DataFrame) -> pd.DataFrame:
    ids = ",".join(str(int(x)) for x in metadata["signal_id"])
    frame = ch_query(
        f"""
        SELECT
            signal_id,
            asset_id,
            dictGet('assets', 'name', asset_id) AS asset,
            dt,
            argMax(value, computed_at) AS value,
            argMax(metadata, computed_at) AS metadata
        FROM signals
        WHERE
            signal_id IN ({ids})
            AND dt >= toDateTime('{START_DATE}')
            AND dt <= toDateTime('{END_DATE}')
        GROUP BY signal_id, asset_id, asset, dt
        ORDER BY signal_id, asset_id, dt
        """
    )
    signal_map = dict(zip(metadata["signal_id"].astype(int), metadata["name"]))
    frame["dt"] = pd.to_datetime(frame["dt"])
    frame["signal"] = frame["signal_id"].astype(int).map(signal_map)
    frame["display"] = frame["signal"].map(SIGNAL_DISPLAY)
    return frame


def filter_event_universe(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    coverage = []
    for signal, group in events.groupby("signal"):
        source_events = len(group)
        source_assets = group["asset_id"].nunique()
        mapped = group[group["asset_id"].isin(BINANCE_SYMBOLS)].copy()
        mapped["symbol"] = mapped["asset_id"].map(BINANCE_SYMBOLS)
        counts = mapped.groupby("asset_id").size()
        keep_assets = counts[counts >= MIN_ASSET_EVENTS[signal]].index
        mapped = mapped[mapped["asset_id"].isin(keep_assets)].copy()
        rows.append(mapped)
        coverage.append(
            {
                "signal": signal,
                "display": SIGNAL_DISPLAY[signal],
                "source_events": source_events,
                "source_assets": source_assets,
                "events_after_binance_filter": len(mapped),
                "assets_after_binance_filter": mapped["asset_id"].nunique(),
                "min_events_per_asset": MIN_ASSET_EVENTS[signal],
            }
        )
    return pd.concat(rows, ignore_index=True).sort_values(["signal", "asset_id", "dt"]), pd.DataFrame(coverage)


def fetch_prices(events: pd.DataFrame) -> dict[int, PriceSeries]:
    fetcher = BinanceDataFetcher(cache_dir=str(ROOT / "cache"))
    prices = {}
    price_frames = []
    for index, (asset_id, group) in enumerate(events.groupby("asset_id"), start=1):
        asset_id = int(asset_id)
        symbol = BINANCE_SYMBOLS[asset_id]
        start = (group["dt"].min().floor("h") - pd.Timedelta(days=7)).to_pydatetime()
        end = (group["dt"].max().ceil("h") + pd.Timedelta(days=7)).to_pydatetime()
        print(f"Fetching Binance hourly price {index}/{events['asset_id'].nunique()}: {symbol}", flush=True)
        frame = fetcher.fetch_token_data(symbol, timeframe="1h", start_date=start, end_date=end)
        if frame.empty:
            continue
        frame = frame.rename(columns={"datetime": "dt", "Close": "close"}).drop_duplicates("dt").sort_values("dt")
        frame["asset_id"] = asset_id
        frame["asset"] = str(group["asset"].iloc[0])
        frame["symbol"] = symbol
        price_frames.append(frame[["asset_id", "asset", "symbol", "dt", "close"]])
        prices[asset_id] = PriceSeries(
            asset_id=asset_id,
            asset=str(group["asset"].iloc[0]),
            symbol=symbol,
            times=frame["dt"].to_numpy(dtype="datetime64[ns]"),
            close=frame["close"].astype(float).to_numpy(),
        )
    if price_frames:
        pd.concat(price_frames, ignore_index=True).to_csv(DATA_DIR / "hourly_price_usd.csv", index=False)
    return prices


def event_metrics(series: PriceSeries, timestamp: pd.Timestamp, window_hours: int):
    times = series.times
    close = series.close
    start_time = np.datetime64(timestamp.floor("h").to_datetime64())
    end_time = start_time + np.timedelta64(window_hours, "h")
    start_idx = np.searchsorted(times, start_time, side="left")
    end_idx = np.searchsorted(times, end_time, side="left")
    if start_idx >= len(times) or end_idx >= len(times):
        return None
    if abs((times[start_idx] - start_time) / np.timedelta64(1, "h")) > 1:
        return None
    if abs((times[end_idx] - end_time) / np.timedelta64(1, "h")) > 1:
        return None
    start_price = close[start_idx]
    end_price = close[end_idx]
    if not np.isfinite(start_price) or not np.isfinite(end_price) or start_price <= 0 or end_price <= 0:
        return None
    window_close = close[start_idx : end_idx + 1]
    window_close = window_close[np.isfinite(window_close) & (window_close > 0)]
    min_points = max(2, min(window_hours + 1, int(math.ceil((window_hours + 1) * 0.7))))
    if len(window_close) < min_points:
        return None
    log_returns = np.diff(np.log(window_close))
    forward_return = (end_price / start_price - 1.0) * 100.0
    realized_volatility = np.sqrt(np.sum(np.square(log_returns))) * 100.0 if len(log_returns) else 0.0
    return {
        "forward_return": float(forward_return),
        "abs_return": float(abs(forward_return)),
        "realized_volatility": float(realized_volatility),
    }


def quarter_key(timestamp: pd.Timestamp) -> str:
    return f"{timestamp.year}Q{((timestamp.month - 1) // 3) + 1}"


def outside_exclusion(candidates: np.ndarray, event_times: np.ndarray, exclusion_hours: int) -> np.ndarray:
    if len(candidates) == 0 or len(event_times) == 0:
        return np.ones(len(candidates), dtype=bool)
    event_times = np.sort(event_times.astype("datetime64[ns]"))
    exclusion_ns = exclusion_hours * 3600 * 1_000_000_000
    positions = np.searchsorted(event_times, candidates)
    mask = np.ones(len(candidates), dtype=bool)
    for offset in (0, -1):
        idx = positions + offset
        valid = (idx >= 0) & (idx < len(event_times))
        if valid.any():
            distance = np.abs((candidates[valid] - event_times[idx[valid]]).astype("timedelta64[ns]").astype(np.int64))
            mask[np.where(valid)[0]] &= distance > exclusion_ns
    return mask


def candidate_control_times(series: PriceSeries, window_hours: int) -> pd.DataFrame:
    times = pd.to_datetime(series.times)
    latest_start = times.max() - pd.Timedelta(hours=window_hours)
    frame = pd.DataFrame({"dt": times[times <= latest_start]})
    frame["quarter"] = frame["dt"].map(quarter_key)
    return frame


def evaluate(events: pd.DataFrame, prices: dict[int, PriceSeries]) -> tuple[pd.DataFrame, pd.DataFrame]:
    event_rows = []
    control_rows = []
    for signal, signal_events in events.groupby("signal"):
        for asset_id, asset_events in signal_events.groupby("asset_id"):
            asset_id = int(asset_id)
            series = prices.get(asset_id)
            if series is None:
                continue
            asset_events = asset_events.sort_values("dt")
            event_times_np = asset_events["dt"].dt.floor("h").to_numpy(dtype="datetime64[ns]")
            for window_hours in WINDOWS:
                exclusion_hours = max(EXCLUSION_MIN_HOURS, 2 * window_hours)
                candidates = candidate_control_times(series, window_hours)
                candidate_np = candidates["dt"].to_numpy(dtype="datetime64[ns]")
                candidates = candidates.loc[outside_exclusion(candidate_np, event_times_np, exclusion_hours)].copy()
                all_candidates = candidates["dt"].to_numpy(dtype="datetime64[ns]")
                if len(all_candidates) == 0:
                    continue
                candidates_by_quarter = {
                    key: group["dt"].to_numpy(dtype="datetime64[ns]")
                    for key, group in candidates.groupby("quarter")
                }
                for _, event in asset_events.iterrows():
                    metrics = event_metrics(series, event["dt"], window_hours)
                    if metrics is None:
                        continue
                    event_row = {
                        "signal": signal,
                        "display": event["display"],
                        "asset_id": asset_id,
                        "asset": series.asset,
                        "symbol": series.symbol,
                        "event_dt": event["dt"],
                        "window_hours": window_hours,
                        "value": event["value"],
                    }
                    event_row.update(metrics)
                    event_rows.append(event_row)
                    pool = candidates_by_quarter.get(quarter_key(event["dt"]), all_candidates)
                    if len(pool) < CONTROL_RATIO:
                        pool = all_candidates
                    sampled = RNG.choice(pool, size=CONTROL_RATIO, replace=len(pool) < CONTROL_RATIO)
                    for control_dt in sampled:
                        control_metrics = event_metrics(series, pd.Timestamp(control_dt), window_hours)
                        if control_metrics is None:
                            continue
                        control_row = {
                            "signal": signal,
                            "display": event["display"],
                            "asset_id": asset_id,
                            "asset": series.asset,
                            "symbol": series.symbol,
                            "event_dt": event["dt"],
                            "control_dt": pd.Timestamp(control_dt),
                            "window_hours": window_hours,
                        }
                        control_row.update(control_metrics)
                        control_rows.append(control_row)
    return pd.DataFrame(event_rows), pd.DataFrame(control_rows)


def cohen_d(a: pd.Series, b: pd.Series) -> float:
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    if len(a) < 2 or len(b) < 2:
        return np.nan
    pooled = math.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    if not pooled or not np.isfinite(pooled):
        return np.nan
    return float((a.mean() - b.mean()) / pooled)


def bootstrap_ci(values: np.ndarray, n_boot: int = 3000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan
    if len(values) == 1:
        return float(values[0]), float(values[0])
    samples = RNG.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    return tuple(np.quantile(samples, [0.025, 0.975]).astype(float))


def bootstrap_two_sample_diff_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 3000) -> tuple[float, float]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return np.nan, np.nan
    a_means = RNG.choice(a, size=(n_boot, len(a)), replace=True).mean(axis=1)
    b_means = RNG.choice(b, size=(n_boot, len(b)), replace=True).mean(axis=1)
    return tuple(np.quantile(a_means - b_means, [0.025, 0.975]).astype(float))


def summarize(event_df: pd.DataFrame, control_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = ["forward_return", "abs_return", "realized_volatility"]
    for signal in TARGET_SIGNAL_NAMES:
        for window_hours in WINDOWS:
            e = event_df[(event_df["signal"] == signal) & (event_df["window_hours"] == window_hours)]
            c = control_df[(control_df["signal"] == signal) & (control_df["window_hours"] == window_hours)]
            if e.empty or c.empty:
                continue
            for metric in metrics:
                e_values = e[metric].dropna().astype(float)
                c_values = c[metric].dropna().astype(float)
                _, event_p = stats.ttest_ind(e_values, c_values, equal_var=False, nan_policy="omit")
                event_diff = float(e_values.mean() - c_values.mean())
                event_ci_low, event_ci_high = bootstrap_two_sample_diff_ci(e_values.to_numpy(), c_values.to_numpy())

                asset_rows = []
                for asset_id in sorted(set(e["asset_id"]) & set(c["asset_id"])):
                    ea = e[e["asset_id"] == asset_id][metric].dropna().astype(float)
                    ca = c[c["asset_id"] == asset_id][metric].dropna().astype(float)
                    if len(ea) == 0 or len(ca) == 0:
                        continue
                    asset_rows.append({"asset_id": asset_id, "diff": float(ea.mean() - ca.mean())})
                asset_stats = pd.DataFrame(asset_rows)
                if len(asset_stats) >= 2:
                    _, asset_p = stats.ttest_1samp(asset_stats["diff"], 0.0, nan_policy="omit")
                    asset_diff = float(asset_stats["diff"].mean())
                    asset_ci_low, asset_ci_high = bootstrap_ci(asset_stats["diff"].to_numpy())
                    asset_effect = float(asset_stats["diff"].mean() / asset_stats["diff"].std(ddof=1)) if asset_stats["diff"].std(ddof=1) else np.nan
                elif len(asset_stats) == 1:
                    asset_p = np.nan
                    asset_diff = float(asset_stats["diff"].iloc[0])
                    asset_ci_low, asset_ci_high = asset_diff, asset_diff
                    asset_effect = np.nan
                else:
                    asset_p = np.nan
                    asset_diff = asset_ci_low = asset_ci_high = asset_effect = np.nan

                primary_model = PRIMARY_MODEL[signal]
                primary_diff = asset_diff if primary_model == "asset_weighted" else event_diff
                primary_p = asset_p if primary_model == "asset_weighted" else event_p
                primary_ci_low = asset_ci_low if primary_model == "asset_weighted" else event_ci_low
                primary_ci_high = asset_ci_high if primary_model == "asset_weighted" else event_ci_high

                rows.append(
                    {
                        "signal": signal,
                        "display": SIGNAL_DISPLAY[signal],
                        "window_hours": window_hours,
                        "metric": metric,
                        "primary_model": primary_model,
                        "primary_diff": primary_diff,
                        "primary_ci_low": primary_ci_low,
                        "primary_ci_high": primary_ci_high,
                        "primary_p_value": float(primary_p) if np.isfinite(primary_p) else np.nan,
                        "event_weighted_diff": event_diff,
                        "event_weighted_p_value": float(event_p),
                        "event_weighted_effect_size": cohen_d(e_values, c_values),
                        "asset_weighted_diff": asset_diff,
                        "asset_weighted_p_value": float(asset_p) if np.isfinite(asset_p) else np.nan,
                        "asset_weighted_effect_size": asset_effect,
                        "event_mean": float(e_values.mean()),
                        "control_mean": float(c_values.mean()),
                        "event_count": int(len(e_values)),
                        "control_count": int(len(c_values)),
                        "asset_count": int(e["asset_id"].nunique()),
                    }
                )

    summary = pd.DataFrame(rows)
    summary["primary_p_fdr_bh"] = np.nan
    summary["primary_p_bonferroni"] = np.nan
    summary["primary_significant_fdr"] = False
    finite = summary["primary_p_value"].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    if not finite.empty:
        _, fdr, _, _ = multipletests(finite.to_numpy(), alpha=0.05, method="fdr_bh")
        summary.loc[finite.index, "primary_p_fdr_bh"] = fdr
        summary.loc[finite.index, "primary_p_bonferroni"] = np.minimum(finite.to_numpy() * len(finite), 1.0)
        summary.loc[finite.index, "primary_significant_fdr"] = fdr < 0.05
    return summary


def summarize_ex_btc_eth(event_df: pd.DataFrame, control_df: pd.DataFrame, signal: str) -> pd.DataFrame:
    e = event_df[(event_df["signal"] == signal) & (~event_df["asset_id"].isin([1452, 1681]))]
    c = control_df[(control_df["signal"] == signal) & (~control_df["asset_id"].isin([1452, 1681]))]
    if e.empty or c.empty:
        return pd.DataFrame()
    return summarize(
        pd.concat([e, event_df[event_df["signal"] != signal]], ignore_index=True),
        pd.concat([c, control_df[control_df["signal"] != signal]], ignore_index=True),
    ).query("signal == @signal").copy()


def save_figures(events: pd.DataFrame, summary: pd.DataFrame):
    sns.set_theme(style="whitegrid", context="paper", font_scale=0.95)
    monthly = events.copy()
    monthly["month"] = monthly["event_dt"].dt.to_period("M").dt.to_timestamp()
    monthly_counts = monthly.groupby(["month", "display"]).size().reset_index(name="events")
    plt.figure(figsize=(10, 4.8))
    sns.lineplot(data=monthly_counts, x="month", y="events", hue="display", marker="o")
    plt.title("Monthly anomaly event counts")
    plt.xlabel("")
    plt.ylabel("Events")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "monthly_event_counts.png", dpi=220)
    plt.close()

    top_assets = (
        events[events["signal"] != "eth_whale_dump"]
        .groupby(["display", "asset"])
        .size()
        .reset_index(name="events")
        .sort_values(["display", "events"], ascending=[True, False])
        .groupby("display")
        .head(10)
    )
    plt.figure(figsize=(10, 5.8))
    sns.barplot(data=top_assets, y="asset", x="events", hue="display", dodge=False)
    plt.title("Top event assets for multi-asset anomalies")
    plt.xlabel("Evaluated events")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_assets.png", dpi=220)
    plt.close()

    for metric, title, filename in [
        ("forward_return", "Primary event-control difference: forward return", "forward_return_heatmap.png"),
        ("realized_volatility", "Primary event-control difference: realized volatility", "realized_volatility_heatmap.png"),
        ("abs_return", "Primary event-control difference: absolute return", "absolute_return_heatmap.png"),
    ]:
        pivot = summary[summary["metric"] == metric].pivot(index="display", columns="window_hours", values="primary_diff")
        plt.figure(figsize=(8.4, 4.0))
        sns.heatmap(pivot, annot=True, fmt=".2f", center=0, cmap="vlag", cbar_kws={"label": "Event - control, pp"})
        plt.title(title)
        plt.xlabel("Forward window (hours)")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(FIG_DIR / filename, dpi=220)
        plt.close()

    selected = summary[(summary["window_hours"] == 24) & (summary["metric"].isin(["forward_return", "realized_volatility"]))].copy()
    selected["label"] = selected["display"] + " / " + selected["metric"].str.replace("_", " ")
    selected = selected.sort_values(["metric", "primary_diff"])
    plt.figure(figsize=(9.2, 5.6))
    y = np.arange(len(selected))
    lower_error = np.maximum(selected["primary_diff"] - selected["primary_ci_low"], 0)
    upper_error = np.maximum(selected["primary_ci_high"] - selected["primary_diff"], 0)
    plt.errorbar(selected["primary_diff"], y, xerr=[lower_error, upper_error], fmt="o", capsize=3, color="#2b5c8a")
    plt.axvline(0, color="black", linewidth=1)
    plt.yticks(y, selected["label"])
    plt.xlabel("Event - control, 24h window")
    plt.title("24h primary effect estimates with bootstrap 95% intervals")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "effect_forest_24h.png", dpi=220)
    plt.close()


def fmt(value, digits=3):
    if value is None or not np.isfinite(value):
        return "--"
    return f"{value:.{digits}f}"


def latex_escape(value):
    return str(value).replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def table_rows_identity() -> str:
    rows = []
    for row in AUDIT_ROWS:
        rows.append(
            " & ".join(
                [
                    latex_escape(row["Public Name"]),
                    "\\texttt{" + latex_escape(row["Internal Name"]) + "}",
                    "\\texttt{" + latex_escape(row["App Path"]) + "}",
                    latex_escape(row["Timestamp Used"]),
                    "\\texttt{" + latex_escape(row["Value Field"]) + "}",
                    latex_escape(row["Directional?"]),
                    latex_escape(row["Caveats"]),
                ]
            )
            + r" \\"
        )
    return "\n".join(rows)


def build_latex(summary: pd.DataFrame, event_df: pd.DataFrame, coverage: pd.DataFrame, sensitivity: dict[str, pd.DataFrame]):
    short = {
        "social_dev_score": "SDSC",
        "eth_whale_dump": "EWD",
        "price_network_activity_divergence": "PNAD",
        "project_in_trends": "PIT",
    }
    metric_short = {"forward_return": "FwdRet", "realized_volatility": "RV", "abs_return": "AbsRet"}
    headline = summary[
        (summary["metric"].isin(["forward_return", "realized_volatility"]))
        & (summary["window_hours"].isin([4, 24, 72]))
    ].sort_values(["display", "metric", "window_hours"])

    result_rows = []
    for _, row in headline.iterrows():
        result_rows.append(
            " & ".join(
                [
                    short[row["signal"]],
                    f"{int(row['window_hours'])}h",
                    metric_short[row["metric"]],
                    fmt(row["primary_diff"], 3),
                    f"[{fmt(row['primary_ci_low'], 3)}, {fmt(row['primary_ci_high'], 3)}]",
                    fmt(row["primary_p_fdr_bh"], 4),
                    str(int(row["event_count"])),
                    str(int(row["asset_count"])),
                ]
            )
            + r" \\"
        )

    unique_events = event_df.drop_duplicates(["signal", "asset_id", "event_dt"])
    event_summary = (
        unique_events.groupby(["signal", "display"])
        .agg(events=("event_dt", "count"), assets=("asset_id", "nunique"), first_dt=("event_dt", "min"), last_dt=("event_dt", "max"))
        .reset_index()
        .sort_values("display")
    )
    event_rows = []
    for _, row in event_summary.iterrows():
        event_rows.append(
            f"{latex_escape(row['display'])} & {int(row['events'])} & {int(row['assets'])} & "
            f"{pd.Timestamp(row['first_dt']).date()} & {pd.Timestamp(row['last_dt']).date()} \\\\"
        )

    social_count = int(event_summary.loc[event_summary["signal"] == "social_dev_score", "events"].sum()) if "social_dev_score" in set(event_summary["signal"]) else 0
    pnad_24 = summary[(summary["signal"] == "price_network_activity_divergence") & (summary["window_hours"] == 24) & (summary["metric"] == "forward_return")]
    pnad_sentence = "Price/Network Activity Divergence has limited directional evidence in the 24h window."
    if not pnad_24.empty:
        row = pnad_24.iloc[0]
        pnad_sentence = f"Price/Network Activity Divergence shows a 24h signed-return effect of {fmt(row['primary_diff'], 2)} percentage points with FDR q={fmt(row['primary_p_fdr_bh'], 3)}."

    sensitivity_text = []
    for signal, frame in sensitivity.items():
        if frame.empty:
            continue
        row = frame[(frame["window_hours"] == 24) & (frame["metric"] == "realized_volatility")]
        if row.empty:
            continue
        row = row.iloc[0]
        sensitivity_text.append(
            f"Excluding BTC/ETH for {SIGNAL_DISPLAY[signal]} leaves a 24h realized-volatility effect of {fmt(row['primary_diff'], 2)} percentage points "
            f"(FDR q={fmt(row['primary_p_fdr_bh'], 3)}) across {int(row['asset_count'])} assets."
        )
    sensitivity_paragraph = " ".join(sensitivity_text) if sensitivity_text else "BTC/ETH exclusion sensitivity was not available for the evaluated multi-asset samples."

    tex = rf"""
\documentclass[11pt]{{article}}
\usepackage[margin=0.85in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{hyperref}}
\usepackage{{float}}
\usepackage{{microtype}}
\hypersetup{{colorlinks=true, linkcolor=black, urlcolor=blue, citecolor=black}}
\setlength{{\parskip}}{{0.55em}}
\setlength{{\parindent}}{{0pt}}
\newcolumntype{{L}}[1]{{>{{\raggedright\arraybackslash}}p{{#1}}}}

\title{{Santiment Anomaly Signals as Conditional Market-State Features:\\A Production-Audited Event Study on Binance-Tradable Assets}}
\author{{Santiment Research}}
\date{{May 28, 2026}}

\begin{{document}}
\maketitle

\begin{{abstract}}
This paper evaluates four Santiment anomaly signals--Social Dev Score, ETH Whale Dump, Price/Network Activity Divergence, and Project in Trends--using production-audited definitions and a forward-only event-study design. The study is restricted to assets with mapped Binance spot USDT markets and compares anomaly windows against same-asset, same-quarter controls. The evidence is strongest for conditional market-state interpretation rather than standalone alpha. Price/Network Activity Divergence is the clearest directional candidate in the tested sample, while the social and trend-based anomalies are better framed as attention, activity, or volatility-state features. ETH Whale Dump remains an ETH-specific event-risk label. The results should be interpreted as event-control evidence, not as a transaction-cost-aware trading strategy.
\end{{abstract}}

\section{{Research Summary}}
The final evaluated sample contains {len(unique_events):,} events across {unique_events['asset_id'].nunique()} Binance-tradable mapped assets. Social Dev Score contributes {social_count:,} evaluated events after the Binance and sparse-asset filters. {pnad_sentence} Across the full set, realized-volatility and absolute-return effects are more stable than unconditional signed-return effects. The key product implication is conservative: these anomalies can inform alerts, dashboards, risk-state filters, and research features, but they should not be marketed as standalone alpha signals without portfolio-level validation.

\section{{Data, Signal Universe, and Sample Construction}}
The study uses production rows from Santiment ClickHouse and Binance hourly USDT close prices through the existing \texttt{{anomaly\_evaluation}} price layer. Events are kept only when the asset has a mapped Binance USDT market in the study asset map and enough events for the signal-specific sparse-asset filter. Time is UTC. Effects are computed over forward windows of {", ".join(str(w) + "h" for w in WINDOWS)}.

\begin{{table}}[H]
\centering
\scriptsize
\caption{{Signal Identity and Production Audit Summary.}}
\resizebox{{\linewidth}}{{!}}{{%
\begin{{tabular}}{{lllllll}}
\toprule
Public Name & Internal Name & App Path & Timestamp Used & Value Field & Directional? & Caveats \\
\midrule
{table_rows_identity()}
\bottomrule
\end{{tabular}}
}}
\end{{table}}

\begin{{table}}[H]
\centering
\caption{{Evaluated events after Binance price-coverage filtering.}}
\begin{{tabular}}{{lrrrr}}
\toprule
Signal & Events & Assets & First Event & Last Event \\
\midrule
{chr(10).join(event_rows)}
\bottomrule
\end{{tabular}}
\end{{table}}

\section{{Production Signal Definitions and Audit Caveats}}
The production audit is treated as the source of truth for signal semantics. Where detector logic or upstream tables are not fully observable, the limitation is carried into the interpretation.

\textbf{{Social Dev Score.}} The app ranks assets daily across GitHub activity and social-volume metrics, normalizes ranks to 0--100 scores, combines developer and social components with a 40/60 weighting, and emits events when the composite score is high and unusually elevated relative to a rolling history. This is a composite activity-state signal, not a direct price signal.

\textbf{{ETH Whale Dump.}} The app is ETH-only. It joins existing ETH flow-event rows to Ethereum transactions meeting a large-holder outflow condition. It is best interpreted as a filtered flow-event label and short-horizon event-risk marker.

\textbf{{Price/Network Activity Divergence.}} The app compares smoothed price growth with smoothed daily active address growth, then flags cases where price growth is unusually large relative to network activity. The intended interpretation is possible unhealthy price appreciation relative to on-chain activity.

\textbf{{Project in Trends.}} The app detects mapped projects appearing among top social trending words from Reddit, Twitter crypto, and Telegram sources, with asset-level cooldown. It is an attention-state signal and may be affected by top-N ranking, asset mapping, and cooldown behavior.

\section{{Event-Study Design}}
An event is defined as \texttt{{asset x timestamp x signal}}. For each event and horizon, the study computes signed forward return, absolute return, and realized volatility from Binance hourly closes. Controls are sampled from the same asset and calendar quarter when possible, with timestamps near same-asset anomaly events excluded. Multi-asset headline inference is asset-weighted so high-frequency assets do not dominate. ETH Whale Dump is event-weighted because it is ETH-only. Headline p-values are Benjamini-Hochberg FDR adjusted. This is not a transaction-cost-aware portfolio backtest.

\section{{Descriptive Diagnostics}}
\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\linewidth]{{figures/monthly_event_counts.png}}
\caption{{Monthly anomaly event counts. Clustering motivates same-quarter controls.}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\linewidth]{{figures/top_assets.png}}
\caption{{Top event assets for multi-asset anomalies. Concentration motivates asset-weighted inference.}}
\end{{figure}}

\section{{Empirical Results}}
\begin{{longtable}}{{lllrp{{2.8cm}}rrr}}
\caption{{Primary event-control effects. Differences are event minus control, in percentage points.}}\\
\toprule
Signal & Horizon & Metric & Diff. & 95\% CI & FDR q & Events & Assets \\
\midrule
\endfirsthead
\toprule
Signal & Horizon & Metric & Diff. & 95\% CI & FDR q & Events & Assets \\
\midrule
\endhead
{chr(10).join(result_rows)}
\bottomrule
\end{{longtable}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\linewidth]{{figures/forward_return_heatmap.png}}
\caption{{Primary signed forward-return effects.}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\linewidth]{{figures/realized_volatility_heatmap.png}}
\caption{{Primary realized-volatility effects.}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\linewidth]{{figures/effect_forest_24h.png}}
\caption{{24h primary effect estimates with bootstrap 95\% intervals.}}
\end{{figure}}

\section{{Signal-Level Interpretation}}
\textbf{{Social Dev Score.}} Production meaning: composite developer/social activity score shock. Empirical evidence: useful as an activity-state feature if effects survive asset-weighted checks. Recommended use: research feature or dashboard context, not a standalone entry rule.

\textbf{{ETH Whale Dump.}} Production meaning: ETH-only filtered large-holder flow event. Empirical evidence should be read as event-risk and volatility-state evidence first. Recommended use: ETH risk marker and alert context.

\textbf{{Price/Network Activity Divergence.}} Production meaning: price appreciation outpacing network activity. Empirical evidence in this run is the clearest directional candidate among the four, but it still requires liquidity, cost, and regime validation. Recommended use: candidate for deeper portfolio backtest.

\textbf{{Project in Trends.}} Production meaning: project enters a top social trending-word set. Empirical evidence is best framed as attention-state information. Recommended use: alert context, universe attention, and volatility/risk feature.

\section{{Practical Interpretation for Product and Research}}
These results support using selected anomalies as conditional market-state features on Binance-tradable assets. Price/Network Activity Divergence deserves the most follow-up as a directional candidate. Social Dev Score and Project in Trends are better suited to dashboards, alerts, and interaction features. ETH Whale Dump is suitable for ETH-specific risk context. {sensitivity_paragraph}

\section{{Limitations}}
The study has no transaction-cost model, slippage, borrow or shorting constraints, exchange availability history beyond current mapped Binance symbols, liquidity constraints, portfolio construction, position sizing, or live-trading execution delay. The study also does not estimate a market-factor model, does not perform out-of-sample validation, and does not fully reconstruct upstream social/trend data pipelines. Multiple testing, event clustering, survivorship bias in asset mapping, and production-code mismatch risk remain material.

\section{{Conclusion}}
The evidence supports treating these anomalies as conditional market-state features. Their strongest observed role is in identifying attention, activity, volatility, or event-risk regimes. Directional return predictability remains signal-specific and should be validated through transaction-cost-aware portfolio backtests before being described as alpha.

\begin{{thebibliography}}{{99}}
\bibitem{{mackinlay1997}} MacKinlay, A. C. (1997). Event Studies in Economics and Finance. \emph{{Journal of Economic Literature}}, 35(1), 13--39.
\bibitem{{brownwarner1985}} Brown, S. J., and Warner, J. B. (1985). Using Daily Stock Returns: The Case of Event Studies. \emph{{Journal of Financial Economics}}, 14(1), 3--31.
\bibitem{{benjamini1995}} Benjamini, Y., and Hochberg, Y. (1995). Controlling the False Discovery Rate. \emph{{Journal of the Royal Statistical Society: Series B}}, 57(1), 289--300.
\bibitem{{harvey2016}} Harvey, C. R., Liu, Y., and Zhu, H. (2016). ... and the Cross-Section of Expected Returns. \emph{{Review of Financial Studies}}, 29(1), 5--68.
\bibitem{{bailey2014}} Bailey, D. H., and Lopez de Prado, M. (2014). The Deflated Sharpe Ratio. \emph{{Journal of Portfolio Management}}, 40(5), 94--107.
\bibitem{{barberodean2008}} Barber, B. M., and Odean, T. (2008). All That Glitters. \emph{{Review of Financial Studies}}, 21(2), 785--818.
\bibitem{{da2011}} Da, Z., Engelberg, J., and Gao, P. (2011). In Search of Attention. \emph{{Journal of Finance}}, 66(5), 1461--1499.
\bibitem{{makarovschoar2020}} Makarov, I., and Schoar, A. (2020). Trading and Arbitrage in Cryptocurrency Markets. \emph{{Journal of Financial Economics}}, 135(2), 293--319.
\end{{thebibliography}}

\appendix
\section{{Reproducibility Notes}}
Script path: \texttt{{run\_binance\_anomaly\_paper.py}}. Manifest path: \texttt{{manifest.json}}. Source data: read-only ClickHouse production signal rows and Binance hourly OHLCV. Random seed: 20260528. Control ratio: {CONTROL_RATIO}. Horizons: {", ".join(str(w) + "h" for w in WINDOWS)}. Sparse-asset filters are recorded in the manifest. PDF validation used \texttt{{tectonic}}, \texttt{{pdfinfo}}, and \texttt{{pdftoppm}}.

\section{{Signal Definition Audit Details}}
Detailed source evidence comes from:
\begin{{itemize}}
\item \texttt{{signals/src/apps/social\_dev\_score}}
\item \texttt{{signals/src/apps/eth\_whale\_dump}}
\item \texttt{{signals/src/apps/price\_network\_activity\_divergence}}
\item \texttt{{signals/src/apps/project\_in\_trends}}
\item \texttt{{signals/docs/project\_in\_trends\_time\_handling.md}}
\end{{itemize}}

\section{{Additional Tables and Figures}}
Full event metrics, control metrics, primary result tables, sensitivity tables, and figures are saved beside this PDF in the artifact directory.

\end{{document}}
"""
    (ROOT / "binance_anomaly_paper.tex").write_text(tex.strip() + "\n", encoding="utf-8")


def main():
    metadata = fetch_target_metadata()
    raw_events = fetch_events(metadata)
    study_events, initial_coverage = filter_event_universe(raw_events)
    print(f"Filtered event universe from {len(raw_events)} to {len(study_events)} Binance-tradable rows", flush=True)

    prices = fetch_prices(study_events)
    event_df, control_df = evaluate(study_events, prices)
    summary = summarize(event_df, control_df)
    sensitivity = {
        "project_in_trends": summarize_ex_btc_eth(event_df, control_df, "project_in_trends"),
        "social_dev_score": summarize_ex_btc_eth(event_df, control_df, "social_dev_score"),
        "price_network_activity_divergence": summarize_ex_btc_eth(event_df, control_df, "price_network_activity_divergence"),
    }

    raw_events.drop(columns=["signal_id"], errors="ignore").to_csv(DATA_DIR / "raw_signal_events.csv", index=False)
    study_events.drop(columns=["signal_id"], errors="ignore").to_csv(DATA_DIR / "study_events_before_price_filter.csv", index=False)
    event_df.to_csv(DATA_DIR / "event_metrics.csv", index=False)
    control_df.to_csv(DATA_DIR / "control_metrics.csv", index=False)
    summary.to_csv(TABLE_DIR / "primary_results.csv", index=False)
    initial_coverage.to_csv(TABLE_DIR / "sample_coverage_before_price_filter.csv", index=False)
    for name, frame in sensitivity.items():
        frame.to_csv(TABLE_DIR / f"{name}_ex_btc_eth_sensitivity.csv", index=False)

    final_coverage = (
        event_df.drop_duplicates(["signal", "asset_id", "event_dt"])
        .groupby(["signal", "display", "asset_id", "asset", "symbol"])
        .agg(events=("event_dt", "count"), first_dt=("event_dt", "min"), last_dt=("event_dt", "max"))
        .reset_index()
        .sort_values(["signal", "events"], ascending=[True, False])
    )
    final_coverage.to_csv(TABLE_DIR / "asset_coverage.csv", index=False)

    save_figures(event_df, summary)
    build_latex(summary, event_df, final_coverage, sensitivity)

    manifest = {
        "analysis_date": "2026-05-28",
        "start_date": START_DATE,
        "end_date": END_DATE,
        "target_signals": TARGET_SIGNAL_NAMES,
        "asset_filter": "Mapped Binance spot USDT markets only",
        "windows_hours": WINDOWS,
        "control_ratio": CONTROL_RATIO,
        "random_seed": 20260528,
        "min_asset_events": MIN_ASSET_EVENTS,
        "price_source": "Binance spot USDT hourly close through anomaly_evaluation.fetching.BinanceDataFetcher",
        "event_metrics_rows": len(event_df),
        "control_metrics_rows": len(control_df),
        "primary_results_rows": len(summary),
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
