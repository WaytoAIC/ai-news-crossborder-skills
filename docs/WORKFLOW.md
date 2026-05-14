# AI HOT + HEX2077 Cross-Border Daily Workflow

## Design

The workflow separates upstream collection from business judgment:

| Layer | Responsibility |
|---|---|
| AI HOT | Recent selected AI-industry items via public API. |
| HEX2077 | Latest daily report parsed into item JSON. |
| Report generator | Merge, dedupe, score, and render Markdown. |
| Human/editor pass | Remove low-value or risky items before publishing when needed. |
| Feishu publisher | Append the final Markdown to a configured document. |

## Source Rules

- Use both sources by default.
- If one source fails, keep the run alive when the other source succeeds.
- Record source errors in the report and raw JSON.
- Never update `last_published_date` unless Feishu publish succeeds.

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
