#!/usr/bin/env python3
"""Fetch AI HOT items as a source packet for cross-border ecommerce analysis."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


BASE_URL = "https://aihot.virxact.com/api/public/items"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch AI HOT public items for ecommerce-value analysis."
    )
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours.")
    parser.add_argument(
        "--mode",
        choices=["selected", "all"],
        default="selected",
        help="Use selected unless the user explicitly asks for all items.",
    )
    parser.add_argument(
        "--category",
        choices=["ai-models", "ai-products", "industry", "paper", "tip"],
        help="Optional AI HOT category filter.",
    )
    parser.add_argument("--query", help="Optional keyword search.")
    parser.add_argument("--take", type=int, default=50, help="Items to request, 1-100.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument("--output", help="Optional output file path.")
    return parser.parse_args()


def fetch_items(args: argparse.Namespace) -> dict:
    take = max(1, min(args.take, 100))
    since = datetime.now(timezone.utc) - timedelta(hours=max(1, args.hours))
    params = {
        "mode": args.mode,
        "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "take": str(take),
    }
    if args.category:
        params["category"] = args.category
    if args.query:
        params["q"] = args.query.strip()

    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"AI HOT request failed: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"AI HOT request failed: {exc.reason}") from exc

    data = json.loads(raw)
    data["_request"] = {
        "mode": args.mode,
        "hours": args.hours,
        "category": args.category,
        "query": args.query,
        "take": take,
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return data


def render_markdown(data: dict) -> str:
    request = data.get("_request", {})
    items = data.get("items", [])
    lines = [
        "# AI HOT Source Packet",
        "",
        f"- Fetched at: {request.get('fetchedAt')}",
        f"- Window: last {request.get('hours')} hours",
        f"- Mode: {request.get('mode')}",
        f"- Count: {len(items)}",
    ]
    if request.get("category"):
        lines.append(f"- Category: {request['category']}")
    if request.get("query"):
        lines.append(f"- Query: {request['query']}")
    lines.append("")

    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"## {index}. {item.get('title') or '(untitled)'}",
                "",
                f"- Source: {item.get('source') or ''}",
                f"- Published: {item.get('publishedAt') or ''}",
                f"- Category: {item.get('category') or ''}",
                f"- URL: {item.get('url') or ''}",
                "",
                item.get("summary") or "",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    data = fetch_items(args)
    if args.format == "json":
        output = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    else:
        output = render_markdown(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
