#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from html import unescape


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Hex2077Skill/1.0"
BASE = "https://hex2077.dev"
INDEX = {
    "daily": f"{BASE}/docs",
    "weekly": f"{BASE}/blog",
}


class DailyItemParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, str]] = []
        self._skip_depth = 0
        self._li_depth = 0
        self._current: dict[str, object] | None = None
        self._strong_active = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "li" and "leading-relaxed" in attrs_dict.get("class", ""):
            self._li_depth = 1
            self._current = {"text": [], "links": [], "strong": []}
            self._strong_active = False
            return
        if not self._current:
            return
        self._li_depth += 1
        if tag == "a" and attrs_dict.get("href"):
            self._current["links"].append(attrs_dict["href"])  # type: ignore[index, union-attr]
        if tag == "strong":
            self._strong_active = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth or not self._current:
            return
        if tag == "strong":
            self._strong_active = False
        self._li_depth -= 1
        if self._li_depth <= 0:
            text = clean_text("".join(self._current["text"]))  # type: ignore[arg-type]
            strong = self._current["strong"]  # type: ignore[assignment]
            links = self._current["links"]  # type: ignore[assignment]
            title = clean_text(strong[0]) if strong else text[:60]  # type: ignore[index]
            url = str(links[0]) if links else ""  # type: ignore[index]
            if title and text and url and not is_navigation_item(title, url):
                self.items.append(
                    {
                        "id": f"hex2077:{url}",
                        "title": title,
                        "title_en": None,
                        "url": url,
                        "source": "HEX2077：AI日报",
                        "publishedAt": "",
                        "summary": text,
                        "category": "hex2077-daily",
                    }
                )
            self._current = None
            self._strong_active = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth or not self._current:
            return
        self._current["text"].append(data)  # type: ignore[index, union-attr]
        if self._strong_active:
            text = clean_text(data)
            if text:
                self._current["strong"].append(text)  # type: ignore[index, union-attr]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def strip_tags(text: str) -> str:
    return clean_text(text)


def is_navigation_item(title: str, url: str) -> bool:
    if url.startswith("/docs/") or url.startswith("/blog/"):
        return True
    return title.startswith("2026 ") or title.endswith("AI资讯")


def find_candidates(html: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    pattern = re.compile(r'href="(/(?:docs|blog)(?:/[^"#?]+)+)"')
    for match in pattern.finditer(html):
        href = match.group(1)
        start = max(0, match.start() - 400)
        end = min(len(html), match.end() + 400)
        chunk = html[start:end]
        title_match = re.search(r">([^<>]{6,120})<", chunk)
        title = strip_tags(title_match.group(1)) if title_match else href.rsplit("/", 1)[-1]
        hits.append((href, title))
    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for href, title in hits:
        if href in seen:
            continue
        seen.add(href)
        unique.append((href, title))
    return unique


def choose_latest(mode: str, candidates: list[tuple[str, str]]) -> tuple[str, str]:
    expected = f"/{'docs' if mode == 'daily' else 'blog'}"
    filtered = [item for item in candidates if item[0].startswith(expected)]
    if not filtered:
        raise SystemExit(f"No {mode} entries found from index page")
    filtered.sort(key=lambda item: item[0], reverse=True)
    href, title = filtered[0]
    return f"{BASE}{href}", title


def normalize_url(url: str) -> str:
    if url.startswith("/"):
        return f"{BASE}{url}"
    return url


def fetch_daily_items() -> dict:
    html = fetch(INDEX["daily"])
    latest_url, title = choose_latest("daily", find_candidates(html))
    page = fetch(latest_url)
    parser = DailyItemParser()
    parser.feed(page)
    published_at = ""
    date_match = re.search(r"/docs/(\d{4})-(\d{2})/(\d{4})-(\d{2})-(\d{2})/", latest_url)
    if date_match:
        published_at = f"{date_match.group(3)}-{date_match.group(4)}-{date_match.group(5)}T03:00:00Z"
    for item in parser.items:
        item["url"] = normalize_url(str(item.get("url") or ""))
        item["id"] = f"hex2077:{item['url']}"
        item["publishedAt"] = published_at
    return {
        "source": "hex2077",
        "mode": "daily",
        "index_url": INDEX["daily"],
        "latest_url": latest_url,
        "title_hint": title,
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": parser.items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["daily", "weekly"])
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--items-json",
        action="store_true",
        help="For daily mode, fetch and parse the latest daily page into standard item JSON.",
    )
    args = parser.parse_args()

    if args.items_json:
        if args.mode != "daily":
            raise SystemExit("--items-json is currently supported for daily mode only")
        print(json.dumps(fetch_daily_items(), ensure_ascii=False, indent=2))
        return 0

    html = fetch(INDEX[args.mode])
    latest_url, title = choose_latest(args.mode, find_candidates(html))
    result = {
        "mode": args.mode,
        "index_url": INDEX[args.mode],
        "latest_url": latest_url,
        "title_hint": title,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(latest_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
