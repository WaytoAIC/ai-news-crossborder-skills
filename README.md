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

AI HOT + HEX2077 双源 AI 资讯采集与跨境电商价值日报技能包。

This repository packages two Codex skills and one daily reporting workflow that turn AI-industry news into seller-facing actions for cross-border ecommerce teams.

## What It Does

- Pulls recent selected items from AI HOT.
- Pulls the latest daily report from HEX2077.
- Normalizes both sources into one item schema.
- Deduplicates by URL/title.
- Filters for ecommerce value: ad creatives, listing/content, VOC, customer service, back-office automation, product development, supply chain, and compliance risk.
- Generates a Markdown candidate report that can be appended to a Feishu document.

## Quick Install

```bash
git clone https://github.com/WaytoAIC/ai-news-crossborder-skills.git
cd ai-news-crossborder-skills
bash install.sh --target codex
```

Version-pinned install after releases:

```bash
bash install.sh --target codex --ref v1.0.0
```

## Included Skills

| Skill | Purpose |
|---|---|
| `aihot-crossborder-intel` | Turns AI news into cross-border ecommerce actions and report topics. |
| `hex2077-intelligence-bridge` | Fetches latest HEX2077 daily/weekly entries and emits standard daily item JSON. |

See [docs/SKILLS_SUMMARY.md](docs/SKILLS_SUMMARY.md) for the full skill summary.

## Daily Report Workflow

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources aihot,hex2077 \
  --output aihot-feishu-daily/reports/aihot-crossborder-$(TZ=Asia/Shanghai date +%F).md \
  --state-dir aihot-feishu-daily/state
```

To publish to Feishu, copy `aihot-feishu-daily/config.example.json` to `config.json`, fill in your document URL and identity, then run:

```bash
bash aihot-feishu-daily/scripts/run_daily.sh
```

`config.json`, generated reports, and state files are intentionally ignored by Git.

## Validation

```bash
python3 scripts/quick_validate.py
```

The validator checks Python syntax, required skill files, and a live HEX2077 daily JSON fetch.

## Repository Layout

```text
.
├── aihot-feishu-daily/
│   ├── config.example.json
│   ├── scripts/
│   └── README.md
├── docs/
├── scripts/
└── skills/
    ├── aihot-crossborder-intel/
    └── hex2077-intelligence-bridge/
```

## License

Source-available. See [LICENSE.md](LICENSE.md) and [ADDITIONAL_TERMS.md](ADDITIONAL_TERMS.md).
