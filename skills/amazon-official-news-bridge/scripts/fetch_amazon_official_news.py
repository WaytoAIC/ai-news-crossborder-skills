#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape


PAGE_URL = "https://www.aboutamazon.com/stores-amazon-shopping-news"
RSS_URL = "https://www.aboutamazon.com/rss/feed.rss"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AmazonOfficialNewsBridge/1.0"


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def canonical_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def parse_rss_dates() -> dict[str, dict[str, str]]:
    rss = fetch(RSS_URL)
    root = ET.fromstring(rss)
    channel = root.find("channel")
    if channel is None:
        return {}
    dates: dict[str, dict[str, str]] = {}
    for item in channel.findall("item"):
        link = item.findtext("guid") or item.findtext("link") or ""
        if not link:
            continue
        pub_date = item.findtext("pubDate") or ""
        published_at = ""
        if pub_date:
            try:
                published_at = parsedate_to_datetime(pub_date).astimezone(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            except (TypeError, ValueError):
                published_at = pub_date
        dates[canonical_url(link)] = {
            "publishedAt": published_at,
            "category": item.findtext("category") or "",
        }
    return dates


def parse_cards(html: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r'<div class="promo-card-v2__title"><a href="([^"]+)"[^>]*data-testid="PromoCardV2-title">(.*?)</a></div>'
        r'<div class="promo-card-v2__excerpt"><span class="text">(.*?)</span></div>.*?'
        r'<div class="card-meta__category"><a href="([^"]+)">(.*?)</a>',
        re.S,
    )
    cards: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in pattern.finditer(html):
        url, title, description, category_url, category = match.groups()
        url = canonical_url(url)
        if url in seen:
            continue
        seen.add(url)
        cards.append(
            {
                "title": clean_text(title),
                "url": url,
                "summary": clean_text(description),
                "amazonCategory": clean_text(category),
                "categoryUrl": category_url,
            }
        )
    return cards


def analyze_signal(title: str, summary: str, category: str) -> dict[str, str]:
    text = f"{title} {summary} {category}".lower()
    if any(keyword in text for keyword in ["rufus", "alexa", "agentic", "ai assistant", "price history", "shop direct"]):
        return {
            "signal": "AI 购物入口与消费者路径",
            "priority": "高",
            "sellerAnalysis": "Amazon 正在把搜索、比价、推荐和购买动作前移到 AI 助手里。跨境卖家要把产品结构化信息、价格竞争力、评价证据和站外承接页做得更机器可读。",
            "recommendedAction": "检查主推 ASIN 的标题、要点、图片、Review 证据和价格历史；针对 Rufus/Alexa 问答补齐 FAQ 与对比卖点。",
        }
    if any(keyword in text for keyword in ["supply chain", "logistics", "delivery", "same-day", "30-minute", "grocery", "fresh"]):
        return {
            "signal": "履约速度与供应链服务",
            "priority": "高",
            "sellerAnalysis": "Amazon 在把更快配送、即时零售和供应链能力变成消费者预期。对卖家来说，履约速度、库存位置和补货稳定性会继续影响转化。",
            "recommendedAction": "复盘核心 SKU 的 FBA/多渠道履约、缺货率和补货提前期；对高频消耗品建立更保守的库存安全线。",
        }
    if any(keyword in text for keyword in ["prime day", "deals", "pet days", "save with prime", "discount"]):
        return {
            "signal": "促销节奏与类目需求",
            "priority": "中高",
            "sellerAnalysis": "官方促销节点会改变类目流量分配。宠物、日用品、品牌大促等信号可用于提前判断广告预算与 Deal 报名节奏。",
            "recommendedAction": "把相关类目加入促销日历，提前 2-3 周准备 Deal、优惠券、预算上限和素材版本。",
        }
    if any(keyword in text for keyword in ["seller", "small business", "seller wallet", "independent sellers", "business customers"]):
        return {
            "signal": "卖家经营与 B2B 机会",
            "priority": "中高",
            "sellerAnalysis": "官方在强调卖家经营工具、独立卖家增长和 B2B 采购场景。现金流、企业采购和账户基础设施可能成为卖家效率差异点。",
            "recommendedAction": "关注 Seller Wallet、Amazon Business、B2B 报价和企业采购关键词；把适合办公/机构采购的 SKU 单独建策略。",
        }
    if any(keyword in text for keyword in ["returns", "second life", "return"]):
        return {
            "signal": "退货与逆向物流",
            "priority": "中",
            "sellerAnalysis": "退货体验是 Amazon 继续强化的信任基础。高退货类目会受到更强的质量、包装、尺码和预期管理约束。",
            "recommendedAction": "按 ASIN 拉退货原因，优先修正尺码/兼容性/安装预期；把包装保护和售前说明纳入 Listing 迭代。",
        }
    if any(keyword in text for keyword in ["pharmacy", "health", "medical", "one medical"]):
        return {
            "signal": "健康类目与合规边界",
            "priority": "观察",
            "sellerAnalysis": "健康服务相关更新对普通卖家不是直接机会，但说明 Amazon 对健康、药房和会员服务的合规要求会更严格。",
            "recommendedAction": "健康、个护、补剂类卖家检查功效宣称、图片暗示和合规证据；无资质卖家不要跟进医疗化表达。",
        }
    return {
        "signal": "Amazon 官方运营信号",
        "priority": "观察",
        "sellerAnalysis": "这是 Amazon 官方对购物体验、会员权益或零售服务的公开叙事。可作为平台方向观察，但需要结合类目数据再行动。",
        "recommendedAction": "先记录到官方信号库；只有当它影响你的类目流量、履约、促销或转化路径时再进入执行清单。",
    }


def build_items(take: int) -> dict:
    rss_dates = parse_rss_dates()
    cards = parse_cards(fetch(PAGE_URL))
    items: list[dict[str, str]] = []
    for card in cards[:take]:
        rss_meta = rss_dates.get(canonical_url(card["url"]), {})
        analysis = analyze_signal(card["title"], card["summary"], card["amazonCategory"])
        source_core = f"{card['title']}: {card['summary']}"
        items.append(
            {
                "id": f"amazonnews:{card['url']}",
                "title": card["title"],
                "title_en": card["title"],
                "url": card["url"],
                "source": "Amazon News：Stores and Shopping",
                "publishedAt": rss_meta.get("publishedAt", ""),
                "summary": card["summary"],
                "sourceCore": source_core,
                "sellerAnalysis": analysis["sellerAnalysis"],
                "recommendedAction": analysis["recommendedAction"],
                "amazonSignal": analysis["signal"],
                "priority": analysis["priority"],
                "amazonCategory": rss_meta.get("category") or card["amazonCategory"],
                "category": "amazon-official-news",
                "sourceFeed": "amazonnews",
            }
        )
    return {
        "source": "amazonnews",
        "mode": "stores-shopping-news",
        "index_url": PAGE_URL,
        "rss_url": RSS_URL,
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--take", type=int, default=12, help="Number of official store/shopping items to emit.")
    parser.add_argument("--items-json", action="store_true", help="Emit standard item JSON packet.")
    args = parser.parse_args()

    packet = build_items(max(1, args.take))
    if args.items_json:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        for item in packet["items"]:
            print(f"- {item['title']} ({item['url']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
