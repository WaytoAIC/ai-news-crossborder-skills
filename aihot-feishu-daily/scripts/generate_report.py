#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from intel_pipeline.config import load_source_definitions, select_source_definitions
from intel_pipeline.renderers.markdown import build_report
from intel_pipeline.sources.base import SourceContext
from intel_pipeline.sources.registry import fetch_sources
from intel_pipeline.schema import source_counts


REPO_ROOT = Path(__file__).resolve().parents[2]


def source_ids(source_configs: list[dict]) -> list[str]:
    return [str(config["id"]) for config in source_configs]


def list_sources(definitions: list[dict]) -> str:
    lines = [
        "| ID | Adapter | Type | Enabled | Name |",
        "|---|---|---|---|---|",
    ]
    for source in definitions:
        lines.append(
            "| {id} | {adapter} | {source_type} | {enabled} | {name} |".format(
                id=source.get("id") or "",
                adapter=source.get("adapter") or "",
                source_type=source.get("source_type") or "",
                enabled="yes" if source.get("enabled") else "no",
                name=source.get("name") or "",
            )
        )
    return "\n".join(lines)


def public_source_definition(config: dict) -> dict:
    allowed_keys = {
        "id",
        "name",
        "adapter",
        "enabled",
        "source_type",
        "category",
        "url",
        "urls",
        "take",
        "mode",
        "query",
    }
    return {key: config[key] for key in allowed_keys if key in config}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--output")
    parser.add_argument("--state-dir", default="state")
    parser.add_argument(
        "--sources",
        help=(
            "Comma-separated source IDs from built-ins or --source-config. "
            "Default: all enabled sources. Special values: enabled, all."
        ),
    )
    parser.add_argument(
        "--source-config",
        help="Optional JSON source config. Custom entries overlay built-in source definitions.",
    )
    parser.add_argument("--list-sources", action="store_true", help="List configured sources and exit.")
    parser.add_argument(
        "--strict-sources",
        action="store_true",
        help="Fail if any configured source fails. Default keeps working if at least one source succeeds.",
    )
    args = parser.parse_args()

    definitions = load_source_definitions(args.source_config)
    if args.list_sources:
        print(list_sources(definitions))
        return 0
    if not args.output:
        raise SystemExit("--output is required unless --list-sources is used")

    configs = select_source_definitions(definitions, args.sources)
    selected_ids = source_ids(configs)
    context = SourceContext(repo_root=REPO_ROOT, days=args.days)
    items, packets, errors = fetch_sources(configs, context)
    if not items:
        raise SystemExit("No items fetched from configured sources: " + json.dumps(errors, ensure_ascii=False))
    if args.strict_sources and errors:
        raise SystemExit("One or more sources failed: " + json.dumps(errors, ensure_ascii=False))

    output = Path(args.output).expanduser().resolve()
    state_dir = Path(args.state_dir).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(items, args.days, selected_ids, packets, errors)
    output.write_text(report, encoding="utf-8")
    raw_path = state_dir / f"aihot-selected-{datetime.now(timezone(timedelta(hours=8))):%Y-%m-%d}.json"
    raw_payload = {
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": selected_ids,
        "sourceDefinitions": [public_source_definition(config) for config in configs],
        "sourcePackets": packets,
        "errors": errors,
        "items": items,
    }
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "items": len(items),
                "sources": source_counts(items),
                "errors": errors,
                "report": str(output),
                "raw": str(raw_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
