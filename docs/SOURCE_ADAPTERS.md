# Source Adapter Architecture

这个项目现在按“左边信息渠道 / 右边分析”解耦。

```text
信息渠道 sources
  -> 标准化 NormalizedItem
  -> 跨境电商分析 analysis
  -> Markdown / Feishu 输出 renderers
```

## Left Side: Information Channels

所有信息源都通过 `aihot-feishu-daily/scripts/intel_pipeline/sources/` 下的 adapter 接入。

| Adapter | 适用来源 | 配置方式 |
|---|---|---|
| `aihot_selected` | AI HOT selected API | 内置 `aihot` |
| `command_json` | 其他技能、脚本、MCP 包装器，只要能输出 `items[]` JSON | 配 `command` 或 `command_candidates` |
| `rss` | RSS / Atom 订阅源 | 配 `url`、`take`、`category` |
| `webpage` | 普通网页文章 | 配 `urls` |
| `wechat_url` | 公众号文章 URL | 配 `urls`，内部复用网页解析 |
| `manual_items` | 临时手工来源、无法自动抓取的来源 | 直接配 `items[]` |

## Right Side: Analysis

分析层只读取标准 item，不关心 item 来自哪里。

| Module | Responsibility |
|---|---|
| `schema.py` | 统一 item 字段、去重、来源计数 |
| `analysis/crossborder.py` | 过滤低价值条目、主题评分、优先级、官方信号判断 |
| `renderers/markdown.py` | 生成日报 Markdown 和来源/类别分布 |

## Standard Item Contract

每个 adapter 最终都应该输出接近下面的结构：

```json
{
  "title": "Source title",
  "url": "https://example.com/article",
  "source": "Source display name",
  "publishedAt": "2026-05-14T00:00:00Z",
  "summary": "Original source summary",
  "sourceCore": "Original source core content",
  "category": "rss",
  "sourceFeed": "source_id",
  "sourceType": "rss"
}
```

平台官方信号可以额外带：

```json
{
  "analysisSection": "official_signals",
  "sellerAnalysis": "跨境电商分析",
  "recommendedAction": "建议动作",
  "priority": "高"
}
```

## Adding Sources Without Code Changes

复制样例配置：

```bash
cp aihot-feishu-daily/sources.example.json aihot-feishu-daily/sources.local.json
```

添加 RSS：

```json
{
  "id": "amazon_ads_blog_rss",
  "name": "Amazon Ads Blog",
  "adapter": "rss",
  "enabled": true,
  "source_type": "rss",
  "url": "https://example.com/feed.xml",
  "take": 20,
  "category": "amazon-ads-rss"
}
```

添加网页或公众号文章：

```json
{
  "id": "wechat_ai_commerce",
  "name": "公众号 AI 电商文章",
  "adapter": "wechat_url",
  "enabled": true,
  "source_type": "wechat_url",
  "urls": [
    "https://mp.weixin.qq.com/s/..."
  ],
  "category": "wechat-url"
}
```

添加其他技能或脚本：

```json
{
  "id": "custom_skill_source",
  "name": "Custom Skill Source",
  "adapter": "command_json",
  "enabled": true,
  "source_type": "external_command",
  "command": [
    "{python}",
    "{repo_root}/skills/custom-source/scripts/fetch.py",
    "--items-json"
  ]
}
```

## Running With Config

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --source-config aihot-feishu-daily/sources.local.json \
  --output /tmp/aihot-crossborder.md \
  --state-dir /tmp/aihot-state
```

`run_daily.sh` 会自动检测 `aihot-feishu-daily/sources.local.json`。存在时使用本地配置；不存在时回退到默认三源。

