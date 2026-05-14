# AI HOT × 跨境电商价值日报

这个目录维护一个每日自动化流程：

1. 拉取 AI HOT 最近 3 天精选条目。
2. 拉取 HEX2077 最新 AI 日报，并转换成与 AI HOT 兼容的条目结构。
3. 扫描 Amazon 官方 Stores and Shopping News，并保留官方标题、摘要、分类和链接。
4. 可选读取 `sources.local.json`，接入 RSS、网页、公众号 URL 或其他命令型来源。
5. 合并、按 URL/标题去重，再按跨境电商价值筛选：广告素材、运营 Agent、数据知识库、客服、多语言、供应链、合规风险。
6. 在 Markdown 中单独输出 `Amazon 官方信号`：原文核心、跨境分析和建议动作。
7. 生成本地 Markdown 日报到 `reports/`，同日 raw JSON 会记录 `sources`、`sourceDefinitions`、`sourcePackets`、`errors` 和合并后的 `items`。
8. 通过 `lark-cli` 追加到同一个飞书文档。

## 手动运行

```bash
bash aihot-feishu-daily/scripts/run_daily.sh
```

默认使用 `aihot,hex2077,amazonnews` 三源。调试单一来源时可以直接运行生成器：

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources amazonnews \
  --output /tmp/amazonnews-only.md \
  --state-dir /tmp/aihot-state
```

查看当前可用来源：

```bash
python3 aihot-feishu-daily/scripts/generate_report.py --list-sources
```

## 信息源配置

需要长期新增来源时，复制样例：

```bash
cp aihot-feishu-daily/sources.example.json aihot-feishu-daily/sources.local.json
```

`sources.local.json` 支持：

- `rss`：RSS / Atom 订阅源。
- `webpage`：普通网页文章。
- `wechat_url`：公众号文章 URL。
- `command_json`：其他技能或脚本，只要输出 `items[]` JSON。
- `manual_items`：临时手工条目。

`run_daily.sh` 会自动检测 `sources.local.json`。存在时使用本地配置；不存在时使用默认三源。

如果当天已经发布过，脚本会跳过。需要强制重发：

```bash
bash aihot-feishu-daily/scripts/run_daily.sh --force
```

## 配置

复制 `config.example.json` 为 `config.json`，再维护飞书文档 URL 和 lark 身份：

```json
{
  "feishu_doc_url": "https://...",
  "lark_identity": "bot"
}
```

当前 user token 已过期时可先使用 `bot`。如果要写入用户自己的云文档，重新登录后把 `lark_identity` 改为 `user`。

`config.json` 和 `sources.local.json` 包含私有配置，默认不会提交到 GitHub。
