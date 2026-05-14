from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import parsedate_to_datetime
from html import unescape

from .base import SourceAdapter, SourceResult


UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def iso_from_pubdate(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return value


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(element: ET.Element, names: set[str]) -> str:
    for child in list(element):
        if local_name(child.tag) in names:
            if local_name(child.tag) == "link" and child.attrib.get("href"):
                return child.attrib["href"]
            return "".join(child.itertext()).strip()
    return ""


class RSSAdapter(SourceAdapter):
    def fetch(self) -> SourceResult:
        url = str(self.config["url"])
        take = max(1, int(self.config.get("take") or 20))
        root = ET.fromstring(fetch_text(url))
        entries: list[ET.Element]
        if local_name(root.tag) == "rss":
            channel = next((child for child in list(root) if local_name(child.tag) == "channel"), root)
            entries = [child for child in list(channel) if local_name(child.tag) == "item"]
        else:
            entries = [child for child in root.iter() if local_name(child.tag) == "entry"]

        items: list[dict] = []
        for entry in entries[:take]:
            title = clean_text(child_text(entry, {"title"}))
            link = child_text(entry, {"link", "guid", "id"})
            summary = clean_text(child_text(entry, {"description", "summary", "content"}))
            published_at = iso_from_pubdate(child_text(entry, {"pubdate", "published", "updated"}))
            if not title and not summary:
                continue
            items.append(
                {
                    "id": f"{self.config['id']}:{link or title}",
                    "title": title or summary[:80],
                    "url": link,
                    "source": self.config.get("source_name") or self.config.get("name") or self.config["id"],
                    "publishedAt": published_at,
                    "summary": summary,
                    "sourceCore": f"{title}: {summary}" if title and summary else summary or title,
                    "category": self.config.get("category") or "rss",
                    "sourceFeed": self.config["id"],
                    "sourceType": self.config.get("source_type") or "rss",
                }
            )

        return SourceResult(
            items=items,
            packet={"items": len(items), "adapter": self.config["adapter"], "url": url},
        )


def first_match(html: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, html, re.I | re.S)
        if match:
            return clean_text(match.group(1))
    return ""


class WebPageAdapter(SourceAdapter):
    def fetch(self) -> SourceResult:
        urls = self.config.get("urls") or [self.config.get("url")]
        urls = [str(url) for url in urls if url]
        items: list[dict] = []
        for url in urls:
            html = fetch_text(url)
            title = first_match(
                html,
                [
                    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<title[^>]*>(.*?)</title>',
                    r"var\s+msg_title\s*=\s*'([^']+)'",
                ],
            )
            summary = first_match(
                html,
                [
                    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
                    r"var\s+msg_desc\s*=\s*'([^']+)'",
                ],
            )
            items.append(
                {
                    "id": f"{self.config['id']}:{url}",
                    "title": title or url,
                    "url": url,
                    "source": self.config.get("source_name") or self.config.get("name") or self.config["id"],
                    "publishedAt": "",
                    "summary": summary,
                    "sourceCore": f"{title}: {summary}" if title and summary else summary or title or url,
                    "category": self.config.get("category") or self.config.get("adapter") or "webpage",
                    "sourceFeed": self.config["id"],
                    "sourceType": self.config.get("source_type") or self.config.get("adapter") or "webpage",
                }
            )
        return SourceResult(
            items=items,
            packet={"items": len(items), "adapter": self.config["adapter"], "urls": urls},
        )


class ManualItemsAdapter(SourceAdapter):
    def fetch(self) -> SourceResult:
        items = [dict(item) for item in self.config.get("items") or []]
        for item in items:
            item.setdefault("sourceFeed", self.config["id"])
        return SourceResult(
            items=items,
            packet={"items": len(items), "adapter": self.config["adapter"]},
        )

