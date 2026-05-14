# AI HOT + HEX2077 + Amazon Official Cross-Border Daily Workflow

## Design

The workflow separates upstream collection from business judgment:

| Layer | Responsibility |
|---|---|
| Source adapters | Left side information channels: AI HOT, HEX2077, Amazon official news, RSS, webpage, WeChat URL, command JSON, or manual items. |
| Standard schema | Normalize every source into the same item contract. |
| Analysis layer | Right side business judgment: ecommerce relevance, priority, action, official signal filtering. |
| Report renderer | Merge, dedupe, score, and render Markdown. |
| Human/editor pass | Remove low-value or risky items before publishing when needed. |
| Feishu publisher | Append the final Markdown to a configured document. |

## Source Rules

- Use all three sources by default: `aihot`, `hex2077`, and `amazonnews`.
- If `aihot-feishu-daily/sources.local.json` exists, `run_daily.sh` uses that config and all enabled sources.
- If one source fails, keep the run alive when at least one source succeeds.
- Record source errors in the report and raw JSON.
- For Amazon official news, keep the official title, excerpt, category, and URL as `sourceCore`; add seller analysis separately.
- Never update `last_published_date` unless Feishu publish succeeds.

## Adding More Sources

Use configuration first:

- `rss`: RSS or Atom subscriptions.
- `webpage`: regular web articles.
- `wechat_url`: public-account article URLs.
- `command_json`: any script or skill that emits standard `items[]` JSON.
- `manual_items`: temporary hand-curated source items.

Only add a new Python adapter when the source cannot be represented by the existing adapters.

## Filtering Rules

Exclude by default:

- Funding-only news.
- Pure model rankings.
- Medical or math research without a concrete ecommerce action.
- Generic coding updates without operations, automation, or cost impact.
- Developer-only infrastructure with no seller workflow implication.

Prioritize:

- Advertising creative and short video.
- Listing, A+, product images, localization, and content production.
- VOC, review mining, private-domain traffic, and customer service.
- Browser/back-office automation with human approval.
- Data/report analysis and knowledge-base workflows.
- Product development, supply chain, and compliance risk.
