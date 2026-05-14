# Changelog

## Unreleased

暂无未发布变更。

## v1.2.0

- Refactor daily workflow into a decoupled left-side source adapter layer and right-side cross-border analysis layer.
- Add config-driven source expansion via `aihot-feishu-daily/sources.example.json` and local ignored `sources.local.json`.
- Add adapters for RSS/Atom, generic webpages, WeChat article URLs, command JSON packets, and manual items.
- Move ecommerce scoring and Markdown rendering into `intel_pipeline/analysis` and `intel_pipeline/renderers`.

## v1.1.0

- Add Amazon official Stores and Shopping News as a third daily source with `amazon-official-news-bridge`.
- Add a dedicated `Amazon 官方信号` report section with official source core, seller analysis, and recommended actions.

## v1.0.0

- Add dual-source AI HOT + HEX2077 daily report orchestration.
- Add `hex2077-intelligence-bridge` skill with standard item JSON output.
- Add `aihot-crossborder-intel` skill updates for combined upstream analysis.
- Add installer, validation script, and publish-ready documentation.
