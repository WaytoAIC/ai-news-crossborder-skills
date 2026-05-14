from __future__ import annotations

from datetime import datetime, timedelta, timezone

from intel_pipeline.analysis.crossborder import build_high_value_rows, build_official_signal_items
from intel_pipeline.schema import category_counts, has_feed, source_counts


def fmt_date(value: str) -> str:
    if not value:
        return ""
    return value.replace("T", " ")[:16] + " UTC"


def escape_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def source_summary(source_ids: list[str], source_packets: dict[str, dict]) -> str:
    labels = [str(source_packets.get(source_id, {}).get("name") or source_id) for source_id in source_ids]
    return " + ".join(labels)


def official_section_title(items: list[dict]) -> str:
    if items and all(has_feed(item, "amazonnews") for item in items):
        return "Amazon 官方信号"
    return "平台官方信号"


def build_report(
    items: list[dict],
    days: int,
    sources: list[str],
    source_packets: dict[str, dict],
    errors: list[dict],
) -> str:
    now_cn = datetime.now(timezone(timedelta(hours=8)))
    rows = build_high_value_rows(items)
    official_items = build_official_signal_items(items)
    source_label = source_summary(sources, source_packets)

    lines = [
        f"## {now_cn:%Y-%m-%d} {source_label} × 跨境电商价值日报",
        "",
        f"- 分析时间：{now_cn:%Y-%m-%d %H:%M} 北京时间",
        f"- 数据口径：{', '.join(sources)} 多源合并；共采集归一化 {len(items)} 条；信息源：{source_label}",
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
    if official_items:
        signals = []
        for item in official_items:
            signal = str(item.get("amazonSignal") or item.get("platformSignal") or "")
            if signal and signal not in signals:
                signals.append(signal)
            if len(signals) == 3:
                break
        if signals:
            lines.append(f"{official_section_title(official_items)}重点：" + "、".join(signals) + "。")

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
        title = escape_cell(item.get("title") or "未命名")
        url = item.get("url") or ""
        source = escape_cell(item.get("source") or item.get("sourceLabel") or "")
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

    if official_items:
        lines.extend(
            [
                "",
                f"### {official_section_title(official_items)}",
                "",
                "| 优先级 | 官方新闻 | 原文核心 | 跨境分析 | 建议动作 |",
                "|---|---|---|---|---|",
            ]
        )
        for item in official_items:
            title = escape_cell(item.get("title") or "未命名")
            url = item.get("url") or ""
            source = escape_cell(item.get("source") or item.get("sourceLabel") or "")
            official_news = f"[{title}]({url})<br>{source}<br>{fmt_date(item.get('publishedAt') or '')}"
            lines.append(
                "| {priority} | {official_news} | {source_core} | {analysis} | {action} |".format(
                    priority=escape_cell(item.get("priority") or "观察"),
                    official_news=official_news,
                    source_core=escape_cell(item.get("sourceCore") or item.get("summary") or ""),
                    analysis=escape_cell(item.get("sellerAnalysis") or item.get("platformAnalysis") or ""),
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
    for category, count in sorted(category_counts(items).items()):
        lines.append(f"| {category} | {count} |")
    lines.append("")
    return "\n".join(lines)

