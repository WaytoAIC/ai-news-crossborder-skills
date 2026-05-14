---
name: amazon-official-news-bridge
description: Scan Amazon's official Stores and Shopping News source and turn official source summaries into cross-border ecommerce analysis. Use when the user asks to monitor Amazon official news, Amazon shopping/store updates, Prime/store/logistics/seller signals, or add Amazon official news to daily ecommerce intelligence.
---

# Amazon Official News Bridge

Target source: `https://www.aboutamazon.com/stores-amazon-shopping-news`

This skill treats Amazon's own Stores and Shopping News page as an official upstream signal. It preserves the official title and excerpt as the source core, then adds cross-border ecommerce analysis and recommended actions.

## When to Use

- The user wants to monitor Amazon official shopping/store news.
- The daily AI-commerce report needs platform-side Amazon signals.
- The user asks what Amazon official updates imply for sellers.
- The user wants Prime, Rufus, Alexa shopping, delivery, supply chain, seller wallet, returns, grocery, deals, or small-business updates summarized.

## Command

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py" --items-json
```

Repository-local development command:

```bash
python3 skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py --take 12 --items-json
```

## Output Shape

The script returns a standard item packet:

```json
{
  "source": "amazonnews",
  "items": [
    {
      "title": "Official Amazon title",
      "summary": "Official excerpt",
      "sourceCore": "Official title and excerpt",
      "sellerAnalysis": "Chinese ecommerce analysis",
      "recommendedAction": "Concrete seller action",
      "category": "amazon-official-news"
    }
  ]
}
```

## Analysis Rules

- Preserve Amazon's official title, link, category, and excerpt.
- Do not rewrite official claims as if they were third-party verified facts.
- Add seller analysis in Chinese.
- Focus on what changes for Amazon sellers: consumer path, AI shopping assistants, delivery expectations, Prime/deal calendar, supply-chain services, seller finance, returns, and compliance.
- Exclude entertainment-only, corporate/community-only, generic management, and medical-service items from the final report unless they affect shopping behavior, marketplace operations, seller compliance, or a concrete ecommerce action.
- Raw JSON may keep non-actionable official cards for traceability; the final Markdown should only surface reportable items.

## Daily Workflow Role

In the combined daily workflow:

```text
AI HOT + HEX2077 + Amazon official news
  -> normalize
  -> dedupe
  -> AI/cross-border filtering
  -> Amazon official signal section
  -> Feishu publish
```
