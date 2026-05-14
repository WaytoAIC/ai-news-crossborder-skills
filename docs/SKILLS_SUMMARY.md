# Skills Summary

## `aihot-crossborder-intel`

Purpose: analyze AI HOT, HEX2077, Amazon official news, and broader AI-industry updates through a cross-border ecommerce lens.

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

## `amazon-official-news-bridge`

Purpose: scan Amazon's official Stores and Shopping News page and turn official title/excerpt pairs into seller-facing analysis.

Useful command:

```bash
python3 skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py --take 12 --items-json
```

Main output: a JSON packet with `index_url`, `rss_url`, and normalized `items[]`. Each item keeps `sourceCore` for the official original title + excerpt, then adds `sellerAnalysis`, `recommendedAction`, `amazonSignal`, and `priority`.

## Combined Daily Workflow

The daily workflow chains all three sources:

```text
AI HOT selected items
  + HEX2077 latest daily items
  + Amazon official Stores and Shopping News
  + optional RSS / webpage / WeChat URL / command JSON sources
  -> source adapters normalize item schema
  -> dedupe by URL/title
  -> analysis layer scores by ecommerce relevance
  -> render separate Amazon official signal section
  -> generate Markdown report
  -> optional Feishu publish
```

Default command:

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources aihot,hex2077,amazonnews \
  --output /tmp/aihot-crossborder.md \
  --state-dir /tmp/aihot-state
```

Config-driven sources:

```bash
cp aihot-feishu-daily/sources.example.json aihot-feishu-daily/sources.local.json
python3 aihot-feishu-daily/scripts/generate_report.py \
  --source-config aihot-feishu-daily/sources.local.json \
  --output /tmp/aihot-crossborder.md \
  --state-dir /tmp/aihot-state
```

See `docs/SOURCE_ADAPTERS.md` for the left-side source adapter contract.
