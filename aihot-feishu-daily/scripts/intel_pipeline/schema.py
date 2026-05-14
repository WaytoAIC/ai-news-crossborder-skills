from __future__ import annotations


def item_key(item: dict) -> str:
    url = str(item.get("url") or "").strip().rstrip("/")
    if url:
        return "url:" + url
    title = str(item.get("title") or "").strip().lower()
    return "title:" + title


def merge_items(source_items: list[list[dict]]) -> list[dict]:
    merged: list[dict] = []
    seen: dict[str, dict] = {}
    for items in source_items:
        for item in items:
            key = item_key(item)
            if not key or key == "title:":
                continue
            if key in seen:
                existing = seen[key]
                feeds = {
                    feed
                    for feed in str(existing.get("sourceFeed") or "").split("+")
                    if feed
                }
                feed = str(item.get("sourceFeed") or "")
                if feed:
                    feeds.add(feed)
                existing["sourceFeed"] = "+".join(sorted(feeds))
                continue
            seen[key] = item
            merged.append(item)
    return merged


def source_counts(items: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        feed = str(item.get("sourceFeed") or "unknown")
        counts[feed] = counts.get(feed, 0) + 1
    return counts


def category_counts(items: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        category = str(item.get("category") or "unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts


def has_feed(item: dict, feed: str) -> bool:
    feeds = {value for value in str(item.get("sourceFeed") or "").split("+") if value}
    return feed in feeds


def normalize_item(item: dict, source_config: dict) -> dict:
    normalized = dict(item)
    source_id = str(source_config["id"])
    defaults = source_config.get("default_item_fields") or {}
    for key, value in defaults.items():
        normalized.setdefault(key, value)
    normalized.setdefault("sourceFeed", source_id)
    normalized.setdefault("sourceId", source_id)
    normalized.setdefault("sourceType", source_config.get("source_type") or source_config.get("adapter"))
    normalized.setdefault("sourceLabel", source_config.get("name") or source_id)
    normalized.setdefault("category", source_config.get("category") or normalized.get("sourceType") or "source")
    if normalized.get("summary") and not normalized.get("sourceCore"):
        title = str(normalized.get("title") or "").strip()
        summary = str(normalized.get("summary") or "").strip()
        normalized["sourceCore"] = f"{title}: {summary}" if title else summary
    return normalized

