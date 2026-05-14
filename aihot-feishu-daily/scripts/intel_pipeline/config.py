from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from pathlib import Path


DEFAULT_SOURCE_DEFINITIONS: list[dict] = [
    {
        "id": "aihot",
        "name": "AI HOT",
        "adapter": "aihot_selected",
        "enabled": True,
        "source_type": "ai_news_api",
        "take": 100,
    },
    {
        "id": "hex2077",
        "name": "HEX2077",
        "adapter": "command_json",
        "enabled": True,
        "source_type": "ai_daily_report",
        "timeout": 90,
        "command_candidates": [
            [
                "{python}",
                "{repo_root}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py",
                "daily",
                "--items-json",
            ],
            [
                "{python}",
                "{codex_home}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py",
                "daily",
                "--items-json",
            ],
        ],
        "packet_meta_keys": ["latest_url", "title_hint"],
    },
    {
        "id": "amazonnews",
        "name": "Amazon 官方",
        "adapter": "command_json",
        "enabled": True,
        "source_type": "official_platform_news",
        "timeout": 90,
        "command_candidates": [
            [
                "{python}",
                "{repo_root}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py",
                "--take",
                "12",
                "--items-json",
            ],
            [
                "{python}",
                "{codex_home}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py",
                "--take",
                "12",
                "--items-json",
            ],
        ],
        "packet_meta_keys": ["index_url", "rss_url"],
        "default_item_fields": {
            "analysisSection": "official_signals",
            "sourceType": "official_platform_news",
        },
    },
]


def load_source_definitions(config_path: str | None) -> list[dict]:
    definitions = {item["id"]: deepcopy(item) for item in DEFAULT_SOURCE_DEFINITIONS}
    if config_path:
        path = Path(config_path).expanduser().resolve()
        payload = json.loads(path.read_text(encoding="utf-8"))
        for source in payload.get("sources") or []:
            source_id = source.get("id")
            if not source_id:
                raise SystemExit(f"Source entry in {path} is missing id")
            existing = definitions.get(source_id, {})
            merged = {**existing, **source}
            definitions[source_id] = merged
    return list(definitions.values())


def select_source_definitions(definitions: list[dict], sources_arg: str | None) -> list[dict]:
    by_id = {str(item["id"]): item for item in definitions}
    if not sources_arg:
        selected = [item for item in definitions if item.get("enabled", False)]
    else:
        requested = [source.strip() for source in sources_arg.split(",") if source.strip()]
        if requested == ["enabled"]:
            selected = [item for item in definitions if item.get("enabled", False)]
        elif requested == ["all"]:
            selected = definitions
        else:
            missing = sorted(set(requested) - set(by_id))
            if missing:
                raise SystemExit(f"Unsupported source(s): {', '.join(missing)}")
            selected = [by_id[source_id] for source_id in requested]
    if not selected:
        raise SystemExit("No enabled sources selected")
    return selected


def expand_command_arg(value: str, repo_root: Path) -> str:
    codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return (
        value.replace("{python}", sys.executable)
        .replace("{repo_root}", str(repo_root))
        .replace("{codex_home}", codex_home)
        .replace("{home}", str(Path.home()))
    )

