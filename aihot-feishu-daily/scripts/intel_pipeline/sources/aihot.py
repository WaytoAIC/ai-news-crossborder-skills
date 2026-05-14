from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from .base import SourceAdapter, SourceResult


BASE_URL = "https://aihot.virxact.com"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class AIHotSelectedAdapter(SourceAdapter):
    def fetch_json(self, path: str, params: dict[str, str]) -> dict:
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{BASE_URL}{path}?{query}",
            headers={"User-Agent": UA},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch(self) -> SourceResult:
        days = int(self.config.get("days") or self.context.days)
        take = str(max(1, min(int(self.config.get("take") or 100), 100)))
        since = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0)
        params = {
            "mode": str(self.config.get("mode") or "selected"),
            "since": since.isoformat().replace("+00:00", "Z"),
            "take": take,
        }
        if self.config.get("category"):
            params["category"] = str(self.config["category"])
        if self.config.get("query"):
            params["q"] = str(self.config["query"]).strip()

        items: list[dict] = []
        cursor = ""
        while True:
            page_params = dict(params)
            if cursor:
                page_params["cursor"] = cursor
            page = self.fetch_json("/api/public/items", page_params)
            for item in page.get("items") or []:
                item["sourceFeed"] = self.config["id"]
                items.append(item)
            if not page.get("hasNext"):
                break
            cursor = page.get("nextCursor") or ""
            if not cursor:
                break

        return SourceResult(
            items=items,
            packet={
                "items": len(items),
                "adapter": self.config["adapter"],
                "mode": params["mode"],
                "days": days,
            },
        )

