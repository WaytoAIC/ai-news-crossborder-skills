from __future__ import annotations

from intel_pipeline.schema import merge_items, normalize_item

from .aihot import AIHotSelectedAdapter
from .base import SourceAdapter, SourceContext
from .command_json import CommandJsonAdapter
from .generic import ManualItemsAdapter, RSSAdapter, WebPageAdapter


ADAPTERS: dict[str, type[SourceAdapter]] = {
    "aihot_selected": AIHotSelectedAdapter,
    "command_json": CommandJsonAdapter,
    "rss": RSSAdapter,
    "webpage": WebPageAdapter,
    "wechat_url": WebPageAdapter,
    "manual_items": ManualItemsAdapter,
}


def fetch_sources(
    source_configs: list[dict], context: SourceContext
) -> tuple[list[dict], dict[str, dict], list[dict]]:
    source_items: list[list[dict]] = []
    packets: dict[str, dict] = {}
    errors: list[dict] = []

    for config in source_configs:
        source_id = str(config["id"])
        adapter_id = str(config.get("adapter") or "")
        adapter_cls = ADAPTERS.get(adapter_id)
        if not adapter_cls:
            errors.append({"source": source_id, "error": f"Unsupported adapter: {adapter_id}"})
            continue
        try:
            result = adapter_cls(config, context).fetch()
            items = [normalize_item(item, config) for item in result.items]
            source_items.append(items)
            packets[source_id] = {
                "name": config.get("name") or source_id,
                "adapter": adapter_id,
                "source_type": config.get("source_type") or adapter_id,
                **result.packet,
            }
        except Exception as exc:
            errors.append({"source": source_id, "error": str(exc)})

    return merge_items(source_items), packets, errors

