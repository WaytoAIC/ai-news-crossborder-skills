## 🚀 Way to AIC | 通往 AI 电商之路
---
### 🌐 官网 Website
- https://waytoaic.com
- https://www.waytoaic.com
---

### 👥 社群招募 Community
`Way to AIC 社群招募 | WaytoAIC.com`

<p align="center">
  <img src="https://github.com/user-attachments/assets/d9f8bbf4-2056-4780-975d-86c885b52bab" width="70%">
</p>

---

### 📣 公众号 WeChat Official Account
`维正 WaytoAIC`

<p align="center">
  <img src="https://github.com/user-attachments/assets/71c71a5c-e68a-4f30-9afb-f2b056619991" width="300">
</p>

---

### 🧠 知识星球 Xiaozhixing
`AI电商之路 WaytoAIC`

<p align="center">
  <img src="https://github.com/user-attachments/assets/9eccef07-0e84-45a7-a415-affcb18c928d" width="200">
  <img src="https://github.com/user-attachments/assets/4e99fbc3-1981-4fee-b113-c9821141102d" width="400">
</p>

---

### 🧩 About Way to AIC

**AIC = AI Commerce**

在 AI 重塑商业的时代，我们希望和每一个拥抱 AI 的卖家：

- 找到场景
- 定义问题
- 积累能力
- 设计系统

共同通往 AI 电商之路。

> Way to AIC 不是教学，不是工具，
> 而是一条所有电商人共同走的进化之路。

### WaytoAIC 理念 | Principles

| 中文 | English |
|---|---|
| 场景先于方法 | Context before method |
| AI 的价值来自真实业务场景，而不是技术本身。 | AI creates value through real business contexts, not through technology alone. |
| 问题先于答案 | Problem before answer |
| 定义问题，比拥有工具更重要。 | Defining the problem matters more than collecting tools. |
| 系统胜过技巧 | System over tricks |
| 技巧是术，系统才是道，决定卖家的上限。 | Tricks are tactical; systems define long-term leverage and ceiling. |
| 共创优于独行 | Co-creation over solo progress |
| 我们相信，真正的进化发生在共同探索的过程中。 | Real evolution happens through shared exploration. |

# AI News Cross-Border Skills

AI HOT + HEX2077 + Amazon 官方三源默认接入，并支持网页、公众号 URL、RSS 和其他脚本来源的可插拔跨境电商价值日报技能包。

This repository packages Codex skills and one daily reporting workflow that turn AI-industry and Amazon official platform news into seller-facing actions for cross-border ecommerce teams.

## What It Does

- Pulls recent selected items from AI HOT.
- Pulls the latest daily report from HEX2077.
- Scans Amazon's official Stores and Shopping News page for platform-side retail, Prime, AI shopping, logistics, seller, returns, and deal-calendar signals.
- Normalizes all sources into one item schema through a source-adapter pipeline.
- Deduplicates by URL/title.
- Filters for ecommerce value: ad creatives, listing/content, VOC, customer service, back-office automation, product development, supply chain, and compliance risk.
- Adds a dedicated `Amazon 官方信号` section with official source core summary, seller analysis, and recommended actions.
- Generates a Markdown candidate report that can be appended to a Feishu document.

## Quick Install

```bash
git clone https://github.com/WaytoAIC/ai-news-crossborder-skills.git
cd ai-news-crossborder-skills
bash install.sh --target codex
```

Version-pinned install after releases:

```bash
bash install.sh --target codex --ref v1.2.0
```

## Included Skills

| Skill | Purpose |
|---|---|
| `aihot-crossborder-intel` | Turns AI news into cross-border ecommerce actions and report topics. |
| `hex2077-intelligence-bridge` | Fetches latest HEX2077 daily/weekly entries and emits standard daily item JSON. |
| `amazon-official-news-bridge` | Scans Amazon official Stores and Shopping News and converts official excerpts into ecommerce analysis. |

See [docs/SKILLS_SUMMARY.md](docs/SKILLS_SUMMARY.md) for the full skill summary.

## Daily Report Workflow

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources aihot,hex2077,amazonnews \
  --output aihot-feishu-daily/reports/aihot-crossborder-$(TZ=Asia/Shanghai date +%F).md \
  --state-dir aihot-feishu-daily/state
```

List available source adapters and configured sources:

```bash
python3 aihot-feishu-daily/scripts/generate_report.py --list-sources
```

To add recurring sources without code changes, copy `aihot-feishu-daily/sources.example.json` to `sources.local.json` and enable `rss`, `webpage`, `wechat_url`, `command_json`, or `manual_items` entries. See [docs/SOURCE_ADAPTERS.md](docs/SOURCE_ADAPTERS.md).

To publish to Feishu, copy `aihot-feishu-daily/config.example.json` to `config.json`, fill in your document URL and identity, then run:

```bash
bash aihot-feishu-daily/scripts/run_daily.sh
```

`config.json`, `sources.local.json`, generated reports, and state files are intentionally ignored by Git.

## Validation

```bash
python3 scripts/quick_validate.py
```

The validator checks Python syntax, required skill files, source config listing, and live HEX2077 + Amazon official JSON fetches.

## Repository Layout

```text
.
├── aihot-feishu-daily/
│   ├── config.example.json
│   ├── sources.example.json
│   ├── scripts/
│   └── README.md
├── docs/
│   └── SOURCE_ADAPTERS.md
├── scripts/
└── skills/
    ├── amazon-official-news-bridge/
    ├── aihot-crossborder-intel/
    └── hex2077-intelligence-bridge/
```

## License

Source-available. See [LICENSE.md](LICENSE.md) and [ADDITIONAL_TERMS.md](ADDITIONAL_TERMS.md).
