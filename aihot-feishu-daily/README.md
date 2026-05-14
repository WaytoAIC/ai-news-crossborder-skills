# AI HOT × 跨境电商价值日报

这个目录维护一个每日自动化流程：

1. 拉取 AI HOT 最近 3 天精选条目。
2. 拉取 HEX2077 最新 AI 日报，并转换成与 AI HOT 兼容的条目结构。
3. 合并、按 URL/标题去重，再按跨境电商价值筛选：广告素材、运营 Agent、数据知识库、客服、多语言、供应链、合规风险。
4. 生成本地 Markdown 日报到 `reports/`，同日 raw JSON 会记录 `sources`、`sourcePackets`、`errors` 和合并后的 `items`。
5. 通过 `lark-cli` 追加到同一个飞书文档。

## 手动运行

```bash
bash aihot-feishu-daily/scripts/run_daily.sh
```

默认使用 `aihot,hex2077` 双源。调试单一来源时可以直接运行生成器：

```bash
python3 aihot-feishu-daily/scripts/generate_report.py \
  --days 3 \
  --sources aihot \
  --output /tmp/aihot-only.md \
  --state-dir /tmp/aihot-state
```

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

`config.json` 包含私有文档地址，默认不会提交到 GitHub。
