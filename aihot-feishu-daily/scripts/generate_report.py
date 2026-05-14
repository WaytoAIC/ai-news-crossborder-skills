#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path


BASE_URL = "https://aihot.virxact.com"
REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_HEX2077_SCRIPT = (
    REPO_ROOT / "skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py"
)
INSTALLED_HEX2077_SCRIPT = Path(
    "/Users/wesleyzane/.codex/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py"
)
LOCAL_AMAZONNEWS_SCRIPT = (
    REPO_ROOT / "skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py"
)
INSTALLED_AMAZONNEWS_SCRIPT = Path(
    "/Users/wesleyzane/.codex/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py"
)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

THEMES = [
    {
        "name": "广告素材与内容生产",
        "keywords": [
            "广告",
            "Reels",
            "推荐",
            "短视频",
            "配图",
            "封面",
            "PPT",
            "Slides",
            "素材",
            "视觉",
            "Suno",
            "HappyHorse",
            "GPT Image",
            "唇形",
            "AI视频",
            "图像生成",
            "文生图",
            "视频引擎",
            "Model Studio",
            "小红书",
            "视频号",
            "公众号",
            "特效",
            "低代码",
        ],
        "value": "可用于产品短视频、社媒封面、A+ 辅助图、广告素材初稿的批量生产。",
        "action": "选 1 个主推 SKU 做小样测试：至少生成 10 条素材，按 CTR、停留、转化线索筛掉无效风格。",
    },
    {
        "name": "运营 Agent 与浏览器自动化",
        "keywords": [
            "Agent",
            "智能体",
            "Codex",
            "Chrome",
            "OpenCLI",
            "连接器",
            "Connectors",
            "SDK",
            "人工审核",
            "技能",
            "自动化",
            "工具调用",
            "OpenClaw",
            "私域",
            "微信",
            "Telegram",
            "Discord",
            "浏览器",
            "后台",
            "安全沙盒",
            "低代码",
            "智能工具",
            "桌面自动化",
            "计算机使用",
            "CUA",
        ],
        "value": "可把竞品采集、后台巡检、社群情报、重复资料整理接入半自动流程。",
        "action": "先限定低风险任务：竞品页面采集、Review 摘要、后台截图巡检；改价、改广告、发消息必须人工审批。",
    },
    {
        "name": "数据分析与知识库",
        "keywords": [
            "Excel",
            "Sheets",
            "表格",
            "Notebook",
            "笔记本",
            "知识",
            "第二大脑",
            "GBrain",
            "RAG",
            "文件",
            "搜索",
            "多模态",
            "资料",
            "Source organization",
        ],
        "value": "可沉淀关键词、广告报表、竞品资料、VOC、Listing 迭代记录，减少反复找资料。",
        "action": "把选品、广告、Listing、竞品、Review 分成固定目录或表格，再让 AI 每天追加摘要和异常点。",
    },
    {
        "name": "客服与多语言沟通",
        "keywords": [
            "语音",
            "Realtime",
            "TTS",
            "CRM",
            "客服",
            "翻译",
            "同声传译",
            "邮件",
            "Outlook",
            "Gmail",
            "多语言",
            "沟通",
            "语音合成",
            "端侧语音",
        ],
        "value": "可用于售后分诊、语音转工单、多语言回复草稿和客户跟进记录。",
        "action": "从“识别意图 + 生成回复草稿 + 人工确认”开始，不要直接自动发送给客户。",
    },
    {
        "name": "产品开发与供应链",
        "keywords": [
            "制造",
            "CNC",
            "可制造性",
            "报价",
            "STEP",
            "材料",
            "公差",
            "供应链",
            "硬件",
            "配件",
            "3D",
            "扫描",
            "MachinaCheck",
        ],
        "value": "对结构件、配件、定制件卖家有用，可辅助打样前评估和供应商沟通。",
        "action": "用于打样前的可制造性检查和问题清单，不替代工程师或供应商最终报价。",
    },
    {
        "name": "合规与风险",
        "keywords": [
            "安全",
            "审核",
            "隐私",
            "版权",
            "侵权",
            "伦理",
            "风险",
            "数据泄露",
            "隐私",
            "安全飞地",
            "人声",
            "盗录",
            "著作权",
            "人工介入",
        ],
        "value": "提示 AI 内容、客户数据、后台操作、素材版权等风险正在变成真实运营约束。",
        "action": "建立素材来源、授权、人工审批、客户隐私四张检查表，高风险动作保留人工确认。",
    },
]

LOW_VALUE_KEYWORDS = [
    "融资",
    "估值",
    "IPO",
    "芯片",
    "数学",
    "博士级",
    "医生",
    "医保",
    "临床",
    "肿瘤",
    "患者",
    "急诊",
    "Health API",
    "Fitbit",
    "航天",
    "SpaceX",
    "Tesla",
    "碰撞",
    "医疗",
    "算法论文",
    "榜单",
]


def fetch_json(path: str, params: dict[str, str]) -> dict:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{BASE_URL}{path}?{query}",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_aihot_items(days: int) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0)
    params = {
        "mode": "selected",
        "since": since.isoformat().replace("+00:00", "Z"),
        "take": "100",
    }
    items: list[dict] = []
    cursor = ""
    while True:
        page_params = dict(params)
        if cursor:
            page_params["cursor"] = cursor
        page = fetch_json("/api/public/items", page_params)
        for item in page.get("items") or []:
            item["sourceFeed"] = "aihot"
            items.append(item)
        if not page.get("hasNext"):
            break
        cursor = page.get("nextCursor") or ""
        if not cursor:
            break
    return items


def fetch_hex2077_items() -> tuple[list[dict], dict]:
    hex2077_script = LOCAL_HEX2077_SCRIPT if LOCAL_HEX2077_SCRIPT.exists() else INSTALLED_HEX2077_SCRIPT
    if not hex2077_script.exists():
        raise FileNotFoundError(
            f"HEX2077 skill script not found: {LOCAL_HEX2077_SCRIPT} or {INSTALLED_HEX2077_SCRIPT}"
        )
    result = subprocess.run(
        [sys.executable, str(hex2077_script), "daily", "--items-json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"HEX2077 fetch failed: {message}")
    packet = json.loads(result.stdout)
    items = packet.get("items") or []
    for item in items:
        item["sourceFeed"] = "hex2077"
    return items, packet


def fetch_amazonnews_items(take: int = 12) -> tuple[list[dict], dict]:
    amazonnews_script = (
        LOCAL_AMAZONNEWS_SCRIPT if LOCAL_AMAZONNEWS_SCRIPT.exists() else INSTALLED_AMAZONNEWS_SCRIPT
    )
    if not amazonnews_script.exists():
        raise FileNotFoundError(
            f"Amazon official news skill script not found: {LOCAL_AMAZONNEWS_SCRIPT} "
            f"or {INSTALLED_AMAZONNEWS_SCRIPT}"
        )
    result = subprocess.run(
        [sys.executable, str(amazonnews_script), "--take", str(take), "--items-json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Amazon official news fetch failed: {message}")
    packet = json.loads(result.stdout)
    items = packet.get("items") or []
    for item in items:
        item["sourceFeed"] = "amazonnews"
    return items, packet


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


def fetch_items(days: int, sources: list[str], errors: list[dict]) -> tuple[list[dict], dict]:
    source_items: list[list[dict]] = []
    packets: dict[str, dict] = {}
    if "aihot" in sources:
        try:
            items = fetch_aihot_items(days)
            source_items.append(items)
            packets["aihot"] = {"items": len(items)}
        except Exception as exc:
            errors.append({"source": "aihot", "error": str(exc)})
    if "hex2077" in sources:
        try:
            items, packet = fetch_hex2077_items()
            source_items.append(items)
            packets["hex2077"] = {
                "items": len(items),
                "latest_url": packet.get("latest_url"),
                "title_hint": packet.get("title_hint"),
            }
        except Exception as exc:
            errors.append({"source": "hex2077", "error": str(exc)})
    if "amazonnews" in sources:
        try:
            items, packet = fetch_amazonnews_items()
            source_items.append(items)
            packets["amazonnews"] = {
                "items": len(items),
                "index_url": packet.get("index_url"),
                "rss_url": packet.get("rss_url"),
            }
        except Exception as exc:
            errors.append({"source": "amazonnews", "error": str(exc)})
    return merge_items(source_items), packets


def score_item(item: dict) -> tuple[int, list[dict]]:
    text = " ".join(
        str(item.get(key) or "")
        for key in ["title", "title_en", "summary", "source", "category"]
    )
    text_lc = text.lower()
    matched_with_scores: list[tuple[int, dict]] = []
    for theme in THEMES:
        hits = [keyword for keyword in theme["keywords"] if keyword.lower() in text_lc]
        if hits:
            matched_with_scores.append((10 + min(len(hits), 6) * 3, theme))
    matched_with_scores.sort(key=lambda item: item[0], reverse=True)
    matched = [theme for _, theme in matched_with_scores]
    score = sum(theme_score for theme_score, _ in matched_with_scores[:2])
    if item.get("category") in {"ai-products", "tip"}:
        score += 3
    if any(keyword.lower() in text_lc for keyword in LOW_VALUE_KEYWORDS):
        score -= 14
    return score, matched


def priority_label(score: int) -> str:
    if score >= 28:
        return "高"
    if score >= 18:
        return "中高"
    if score >= 10:
        return "中"
    return "观察"


def fmt_date(value: str) -> str:
    if not value:
        return ""
    return value.replace("T", " ")[:16] + " UTC"


def source_counts(items: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        feed = str(item.get("sourceFeed") or "unknown")
        counts[feed] = counts.get(feed, 0) + 1
    return counts


def has_feed(item: dict, feed: str) -> bool:
    feeds = {value for value in str(item.get("sourceFeed") or "").split("+") if value}
    return feed in feeds


def escape_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def amazon_reportable(item: dict) -> bool:
    signal = str(item.get("amazonSignal") or "")
    priority = str(item.get("priority") or "")
    if signal == "健康类目与合规边界":
        return False
    if signal == "Amazon 官方运营信号" and priority == "观察":
        return False
    return True


def build_report(items: list[dict], days: int, sources: list[str], errors: list[dict]) -> str:
    now_cn = datetime.now(timezone(timedelta(hours=8)))
    amazon_items = [
        item for item in items if has_feed(item, "amazonnews") and amazon_reportable(item)
    ][:12]
    rows: list[dict] = []
    for item in items:
        if has_feed(item, "amazonnews"):
            continue
        score, themes = score_item(item)
        if score < 10 or not themes:
            continue
        primary = themes[0]
        rows.append(
            {
                "score": score,
                "priority": priority_label(score),
                "theme": primary["name"],
                "value": primary["value"],
                "action": primary["action"],
                "item": item,
            }
        )
    rows.sort(key=lambda row: (row["score"], row["item"].get("publishedAt") or ""), reverse=True)
    rows = rows[:12]

    category_counts: dict[str, int] = {}
    for item in items:
        category = item.get("category") or "unknown"
        category_counts[category] = category_counts.get(category, 0) + 1

    lines = [
        f"## {now_cn:%Y-%m-%d} AI HOT + HEX2077 + Amazon 官方 × 跨境电商价值日报",
        "",
        f"- 分析时间：{now_cn:%Y-%m-%d %H:%M} 北京时间",
        f"- 数据口径：{', '.join(sources)} 多源合并；AI HOT 最近 {days} 天精选 + HEX2077 最新日报 + Amazon 官方 Stores and Shopping News，共 {len(items)} 条",
        "- 筛选原则：优先保留能影响跨境团队选品、广告素材、Listing/VOC、客服、自动化和合规的条目",
        "",
    ]
    if errors:
        lines.extend(["### 采集提示", ""])
        for error in errors:
            lines.append(f"- {error.get('source')}: {error.get('error')}")
        lines.append("")

    lines.extend(["### 今日结论", ""])

    if rows:
        top_themes = []
        for row in rows:
            if row["theme"] not in top_themes:
                top_themes.append(row["theme"])
            if len(top_themes) == 3:
                break
        lines.append("最值得关注的方向：" + "、".join(top_themes) + "。")
    else:
        lines.append("今天没有明显高价值跨境电商条目，建议只做观察，不投入流程改造。")
    if amazon_items:
        amazon_signals = []
        for item in amazon_items:
            signal = str(item.get("amazonSignal") or "")
            if signal and signal not in amazon_signals:
                amazon_signals.append(signal)
            if len(amazon_signals) == 3:
                break
        if amazon_signals:
            lines.append("Amazon 官方信号重点：" + "、".join(amazon_signals) + "。")

    lines.extend(
        [
            "",
            "### 高价值条目",
            "",
            "| 优先级 | 热点 | 方向 | 跨境价值 | 建议动作 |",
            "|---|---|---|---|---|",
        ]
    )

    for row in rows:
        item = row["item"]
        title = str(item.get("title") or "未命名").replace("|", "\\|")
        url = item.get("url") or ""
        source = str(item.get("source") or "").replace("|", "\\|")
        hot = f"[{title}]({url})<br>{source}<br>{fmt_date(item.get('publishedAt') or '')}"
        lines.append(
            "| {priority} | {hot} | {theme} | {value} | {action} |".format(
                priority=row["priority"],
                hot=hot,
                theme=row["theme"],
                value=row["value"],
                action=row["action"],
            )
        )

    if amazon_items:
        lines.extend(
            [
                "",
                "### Amazon 官方信号",
                "",
                "| 优先级 | 官方新闻 | 原文核心 | 跨境分析 | 建议动作 |",
                "|---|---|---|---|---|",
            ]
        )
        for item in amazon_items:
            title = escape_cell(item.get("title") or "未命名")
            url = item.get("url") or ""
            source = escape_cell(item.get("source") or "Amazon News：Stores and Shopping")
            official_news = f"[{title}]({url})<br>{source}<br>{fmt_date(item.get('publishedAt') or '')}"
            lines.append(
                "| {priority} | {official_news} | {source_core} | {analysis} | {action} |".format(
                    priority=escape_cell(item.get("priority") or "观察"),
                    official_news=official_news,
                    source_core=escape_cell(item.get("sourceCore") or item.get("summary") or ""),
                    analysis=escape_cell(item.get("sellerAnalysis") or ""),
                    action=escape_cell(item.get("recommendedAction") or ""),
                )
            )

    lines.extend(
        [
            "",
            "### 观察但暂不动作",
            "",
            "融资、估值、芯片、纯模型榜单、医学和数学研究类新闻，除非直接影响工具成本或现有工作流，默认只做趋势观察。",
            "",
            "### 来源分布",
            "",
            "| 来源 | 数量 |",
            "|---|---:|",
        ]
    )
    for source, count in sorted(source_counts(items).items()):
        lines.append(f"| {source} | {count} |")

    lines.extend(
        [
            "",
            "### 数据分布",
            "",
            "| 类别 | 数量 |",
            "|---|---:|",
        ]
    )
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--output", required=True)
    parser.add_argument("--state-dir", default="state")
    parser.add_argument(
        "--sources",
        default="aihot,hex2077,amazonnews",
        help="Comma-separated source list. Supported: aihot,hex2077,amazonnews.",
    )
    parser.add_argument(
        "--strict-sources",
        action="store_true",
        help="Fail if any configured source fails. Default keeps working if at least one source succeeds.",
    )
    args = parser.parse_args()

    sources = [source.strip() for source in args.sources.split(",") if source.strip()]
    unsupported = sorted(set(sources) - {"aihot", "hex2077", "amazonnews"})
    if unsupported:
        raise SystemExit(f"Unsupported source(s): {', '.join(unsupported)}")

    errors: list[dict] = []
    items, packets = fetch_items(args.days, sources, errors)
    if not items:
        raise SystemExit("No items fetched from configured sources: " + json.dumps(errors, ensure_ascii=False))
    if args.strict_sources and errors:
        raise SystemExit("One or more sources failed: " + json.dumps(errors, ensure_ascii=False))

    output = Path(args.output).expanduser().resolve()
    state_dir = Path(args.state_dir).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(items, args.days, sources, errors)
    output.write_text(report, encoding="utf-8")
    raw_path = state_dir / f"aihot-selected-{datetime.now(timezone(timedelta(hours=8))):%Y-%m-%d}.json"
    raw_payload = {
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": sources,
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
