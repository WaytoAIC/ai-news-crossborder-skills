# Skills Summary

## `aihot-crossborder-intel`

Purpose: analyze AI HOT, HEX2077, and broader AI-industry updates through a cross-border ecommerce lens.

Use it when the user asks:

- 哪些 AI 新闻对跨境电商有价值
- 哪些 AI 工具值得 Amazon/TikTok Shop 卖家测试
- AI 日报里哪些能转成广告素材、Listing、VOC、客服、合规或团队自动化动作
- 公众号、飞书日报、WaytoAIC 选题池需要从 AI 新闻里筛选业务机会

Main output: a seller-facing table with source item, ecommerce value, suggested action, risk, seller type, and priority.

## `hex2077-intelligence-bridge`

Purpose: retrieve latest HEX2077 AI daily or weekly entries and expose the latest daily report as standard item JSON.

Useful commands:

```bash
python3 skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py daily --items-json
python3 skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py weekly --json
```

Main output: a JSON packet with `latest_url`, `title_hint`, and normalized `items[]`.

## Combined Daily Workflow

The daily workflow chains both sources:

```text
AI HOT selected items
  + HEX2077 latest daily items
  -> normalize item schema
  -> dedupe by URL/title
  -> score by ecommerce relevance
  -> generate Markdown report
  -> optional Feishu publish
```

Default command:

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources aihot,hex2077 \
  --output /tmp/aihot-crossborder.md \
  --state-dir /tmp/aihot-state
```
