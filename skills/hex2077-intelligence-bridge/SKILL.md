---
name: hex2077-intelligence-bridge
description: Use when an Agent needs to retrieve the latest HEX2077 AI daily notes or weekly reports, while preserving full category coverage and adding a deep summary layer.
---

# HEX2077 Intelligence Bridge

Target site: `https://hex2077.dev`

Core rule: capture all items from the source structure first, then add downstream analysis. Do not silently drop categories or entries when using this source as the upstream feed.

## When to Use

- The user wants the latest HEX2077 AI daily report.
- The user wants the latest HEX2077 AI weekly report.
- The user wants this source added as an upstream signal for another workflow.
- The user wants a full-category digest first, then a second-pass business filter.

## Source Paths

- Daily reports index: `https://hex2077.dev/docs`
- Weekly reports index: `https://hex2077.dev/blog`
- Protocol page: `https://hex2077.dev/agent`

## Working Rules

1. Treat HEX2077 as an upstream intelligence source, not the final business judgment.
2. Preserve the original category structure when doing a full extraction.
3. Keep the original links for each item whenever possible.
4. Avoid duplicate fetches if a same-day snapshot already exists locally and is still usable.
5. For cross-border ecommerce workflows, do a second pass after extraction:
   - Remove items that are only funding, model ranking, math, medical, or pure developer infra.
   - Prioritize ad creative, listing/content, VOC, private-domain traffic, customer service, browser/back-office automation with human approval, data analysis, product development, supply chain, and compliance.

## Commands

Use the helper script in this skill to resolve the latest entry URL first:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" daily
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" weekly
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" daily --json
python3 "${CODEX_HOME:-$HOME/.codex}/skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py" daily --items-json
```

`--items-json` returns a standard packet with `items[]` shaped like the AI HOT item schema:

```json
{
  "source": "hex2077",
  "latest_url": "https://hex2077.dev/docs/...",
  "items": [
    {
      "title": "...",
      "url": "...",
      "source": "HEX2077：AI日报",
      "publishedAt": "...",
      "summary": "...",
      "category": "hex2077-daily"
    }
  ]
}
```

If the user wants a full daily extraction, follow this pattern:

```text
Visit the latest entry from https://hex2077.dev/docs.
Output all categories and all items without omission.
For each item, preserve the original link and add a concise logic summary.
Then add a final section with trend summary and practical implications.
```

If the user wants a weekly strategic review, follow this pattern:

```text
Visit the latest entry from https://hex2077.dev/blog.
Output all original sections without omission.
Keep the reference links.
Then add a weekly strategic summary and what to watch next.
```

## Notes for This Workspace

- This skill is a supplement to the existing `aihot` workflow, useful when the primary AI HOT source is stale or unreachable.
- For the `AI HOT 跨境电商价值日报` automation, the intended chain is: AI HOT fetcher + HEX2077 `--items-json` -> normalized item list -> cross-border scoring/filtering -> Feishu publishing.
