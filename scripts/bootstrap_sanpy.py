from __future__ import annotations

import os
from pathlib import Path

import san


def _read_api_key(env_path: Path) -> str | None:
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() == "SAN_API_KEY":
            return value.strip().strip('"').strip("'")

    return None


def configure_san(repo_root: str | Path | None = None) -> str:
    api_key = os.getenv("SAN_API_KEY")

    if not api_key:
        root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
        api_key = _read_api_key(root / ".env")

    if not api_key:
        raise RuntimeError("SAN_API_KEY is required in the environment or the repository .env file.")

    san.ApiConfig.api_key = api_key
    return api_key
