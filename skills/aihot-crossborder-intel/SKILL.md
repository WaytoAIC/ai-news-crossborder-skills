---
name: aihot-crossborder-intel
description: Analyze AI HOT, HEX2077, and Amazon official news updates through a cross-border ecommerce lens. Use when the user asks which AI HOT / HEX2077 / Amazon official / AI news / AI industry updates matter to Amazon sellers, cross-border ecommerce, TikTok Shop, listing work, ad creatives, Amazon Ads, product research, VOC, seller operations, compliance, team automation, Feishu daily reports, WeChat article topic selection, or WaytoAIC-style AI commerce intelligence.
---

# AI HOT Cross-Border Intel

## Overview

Turn AI HOT, HEX2077, and Amazon official Stores and Shopping News into an action-oriented intelligence layer for cross-border ecommerce operators. Treat all three as upstream signal sources; add seller relevance, operational impact, action steps, and publishing suitability.

## Default Workflow

1. Collect recent upstream items.
   - Prefer the existing `aihot` skill when it is already triggered or loaded.
   - Use `hex2077-intelligence-bridge` when the user asks to include HEX2077, or when the daily automation needs the combined source pool.
   - Use `amazon-official-news-bridge` when the daily automation needs Amazon official platform-side signals.
   - For deterministic collection, run:

```bash
python3 scripts/fetch_aihot_items.py --hours 24 --take 50 --format markdown
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" daily --items-json
python3 "${CODEX_HOME:-$HOME/.codex}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py" --items-json
```

For the configured Feishu daily automation, prefer the repository orchestrator because it already normalizes and deduplicates all sources through source adapters:

```bash
python3 aihot-feishu-daily/scripts/generate_report.py --days 3 --sources aihot,hex2077,amazonnews --output <report.md> --state-dir aihot-feishu-daily/state
```

If additional sources are configured, use the local source config instead of hardcoding a larger source list:

```bash
python3 aihot-feishu-daily/scripts/generate_report.py --days 3 --source-config aihot-feishu-daily/sources.local.json --output <report.md> --state-dir aihot-feishu-daily/state
```

2. Filter for ecommerce value.
   - Read `references/scoring.md` when making a scored report, ranking items, or explaining why items were excluded.
   - Default to strict filtering: no seller action, no inclusion.

3. Convert each retained item into seller-facing judgment.
   - Always answer: "what changes for sellers?", "what should be tested?", and "what should not be over-followed?"
   - Do not stop at summarizing the AI news.

4. Choose output format.
   - For quick requests: compact table first.
   - For daily reports, Feishu docs, or WeChat topic pools: read `references/output_templates.md`.

## Collection Rules

- Default window: last 24 hours.
- If the user says "最近三天" or "这几天", use 72 hours.
- If the user says "本周", use 7 days.
- If the user explicitly asks for "全部/完整/全量", collect all mode; otherwise stay on selected items.
- If the user names a company, tool, or topic, use keyword search instead of fetching only the first page.
- Keep AI HOT / HEX2077 endpoint details out of user-facing output unless the user asks for implementation details.
- Amazon official news should keep the official title/excerpt as `sourceCore`, then add seller analysis separately.
- New upstream channels should be added on the left side as source adapters or `sources.local.json` entries. Do not mix source fetching logic into the analysis rules.

Useful script examples:

```bash
# 24-hour selected source packet
python3 scripts/fetch_aihot_items.py --hours 24 --take 50 --format markdown

# Latest HEX2077 daily packet
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" daily --items-json

# Combined daily packet and report candidate
python3 aihot-feishu-daily/scripts/generate_report.py --days 3 --sources aihot,hex2077,amazonnews --output /tmp/aihot-crossborder.md --state-dir /tmp/aihot-state

# Amazon official stores and shopping packet
python3 "${CODEX_HOME:-$HOME/.codex}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py" --take 12 --items-json

# List configured source adapters
python3 aihot-feishu-daily/scripts/generate_report.py --list-sources

# Run with local source config
python3 aihot-feishu-daily/scripts/generate_report.py --days 3 --source-config aihot-feishu-daily/sources.local.json --output /tmp/aihot-crossborder.md --state-dir /tmp/aihot-state

# 3-day source packet
python3 scripts/fetch_aihot_items.py --hours 72 --take 100 --format markdown

# Search a specific company or topic
python3 scripts/fetch_aihot_items.py --query OpenAI --hours 168 --take 30 --format markdown
```

## Ecommerce Judgment Dimensions

Use these buckets when classifying relevance:

- `creative`: main images, A+, ad creatives, short video, UGC, TikTok Shop assets.
- `listing`: title, bullets, search terms, localization, Rufus/search visibility.
- `ads`: Amazon Ads, media buying, bid/placement operations, ad analysis.
- `research`: product research, trends, Reddit/VOC, review mining, competitor monitoring.
- `ops`: Codex/Agent/MCP/team workflow automation, reporting, Feishu, spreadsheet workflows.
- `compliance`: AI-generated reviews, fake endorsements, copyright, platform policy, claims risk.
- `consumer_path`: AI search, shopping agents, browser agents, recommendation changes.
- `security`: dependency attacks, account safety, tokens, workflow or plugin risk.

## Output Rules

- Lead with a table unless the user asks for a narrative article.
- Include excluded items when useful: "暂时不建议跟进" is often more valuable than listing every hot item.
- For each included item, include source title, original URL, cross-border impact, action, risk, seller type, and priority.
- Public-facing drafts must be original commentary. Do not copy AI HOT summaries as article body. Use AI HOT as a clue source, keep original source links, and verify key claims from the original URL when possible.
- Avoid raw API route names, cursor values, and endpoint parameters in normal user-facing reports.

## Quality Bar

An item is worth including only if it changes at least one seller decision:

- What to test this week.
- What workflow to adopt or ignore.
- What risk to avoid.
- What content topic to publish.
- What team capability to build.

If the only conclusion is "AI industry is moving fast", exclude it.

## Resources

- `scripts/fetch_aihot_items.py`: Fetches AI HOT source packets with the required browser User-Agent.
- `${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py`: Fetches HEX2077 latest daily and emits standard item JSON.
- `${CODEX_HOME:-$HOME/.codex}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py`: Fetches Amazon official Stores and Shopping News and emits standard item JSON with seller analysis.
- `aihot-feishu-daily/scripts/generate_report.py`: Orchestrates AI HOT + HEX2077 + Amazon official merged daily reports for Feishu publishing.
- `aihot-feishu-daily/sources.example.json`: Shows how to add RSS, webpage, WeChat URL, command JSON, and manual item sources.
- `aihot-feishu-daily/scripts/intel_pipeline/`: Left-side source adapters, right-side analysis, and output renderers.
- `references/scoring.md`: Relevance scorecard and include/exclude rules.
- `references/output_templates.md`: Daily report, Feishu, and public-topic templates.
