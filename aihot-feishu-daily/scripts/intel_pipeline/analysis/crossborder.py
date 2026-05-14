from __future__ import annotations

from intel_pipeline.schema import has_feed


THEMES = [
    {
        "name": "广告素材与内容生产",
        "keywords": [
            "广告",
            "Reels",
            "推荐",
            "短视频",
            "配图",
            "封面",
            "PPT",
            "Slides",
            "素材",
            "视觉",
            "Suno",
            "HappyHorse",
            "GPT Image",
            "唇形",
            "AI视频",
            "图像生成",
            "文生图",
            "视频引擎",
            "Model Studio",
            "小红书",
            "视频号",
            "公众号",
            "特效",
            "低代码",
        ],
        "value": "可用于产品短视频、社媒封面、A+ 辅助图、广告素材初稿的批量生产。",
        "action": "选 1 个主推 SKU 做小样测试：至少生成 10 条素材，按 CTR、停留、转化线索筛掉无效风格。",
    },
    {
        "name": "运营 Agent 与浏览器自动化",
        "keywords": [
            "Agent",
            "智能体",
            "Codex",
            "Chrome",
            "OpenCLI",
            "连接器",
            "Connectors",
            "SDK",
            "人工审核",
            "技能",
            "自动化",
            "工具调用",
            "OpenClaw",
            "私域",
            "微信",
            "Telegram",
            "Discord",
            "浏览器",
            "后台",
            "安全沙盒",
            "低代码",
            "智能工具",
            "桌面自动化",
            "计算机使用",
            "CUA",
        ],
        "value": "可把竞品采集、后台巡检、社群情报、重复资料整理接入半自动流程。",
        "action": "先限定低风险任务：竞品页面采集、Review 摘要、后台截图巡检；改价、改广告、发消息必须人工审批。",
    },
    {
        "name": "数据分析与知识库",
        "keywords": [
            "Excel",
            "Sheets",
            "表格",
            "Notebook",
            "笔记本",
            "知识",
            "第二大脑",
            "GBrain",
            "RAG",
            "文件",
            "搜索",
            "多模态",
            "资料",
            "Source organization",
        ],
        "value": "可沉淀关键词、广告报表、竞品资料、VOC、Listing 迭代记录，减少反复找资料。",
        "action": "把选品、广告、Listing、竞品、Review 分成固定目录或表格，再让 AI 每天追加摘要和异常点。",
    },
    {
        "name": "客服与多语言沟通",
        "keywords": [
            "语音",
            "Realtime",
            "TTS",
            "CRM",
            "客服",
            "翻译",
            "同声传译",
            "邮件",
            "Outlook",
            "Gmail",
            "多语言",
            "沟通",
            "语音合成",
            "端侧语音",
        ],
        "value": "可用于售后分诊、语音转工单、多语言回复草稿和客户跟进记录。",
        "action": "从“识别意图 + 生成回复草稿 + 人工确认”开始，不要直接自动发送给客户。",
    },
    {
        "name": "产品开发与供应链",
        "keywords": [
            "制造",
            "CNC",
            "可制造性",
            "报价",
            "STEP",
            "材料",
            "公差",
            "供应链",
            "硬件",
            "配件",
            "3D",
            "扫描",
            "MachinaCheck",
        ],
        "value": "对结构件、配件、定制件卖家有用，可辅助打样前评估和供应商沟通。",
        "action": "用于打样前的可制造性检查和问题清单，不替代工程师或供应商最终报价。",
    },
    {
        "name": "合规与风险",
        "keywords": [
            "安全",
            "审核",
            "隐私",
            "版权",
            "侵权",
            "伦理",
            "风险",
            "数据泄露",
            "隐私",
            "安全飞地",
            "人声",
            "盗录",
            "著作权",
            "人工介入",
        ],
        "value": "提示 AI 内容、客户数据、后台操作、素材版权等风险正在变成真实运营约束。",
        "action": "建立素材来源、授权、人工审批、客户隐私四张检查表，高风险动作保留人工确认。",
    },
]

LOW_VALUE_KEYWORDS = [
    "融资",
    "估值",
    "IPO",
    "芯片",
    "数学",
    "博士级",
    "医生",
    "医保",
    "临床",
    "肿瘤",
    "患者",
    "急诊",
    "Health API",
    "Fitbit",
    "航天",
    "SpaceX",
    "Tesla",
    "碰撞",
    "医疗",
    "算法论文",
    "榜单",
]


def score_item(item: dict) -> tuple[int, list[dict]]:
    text = " ".join(
        str(item.get(key) or "")
        for key in ["title", "title_en", "summary", "source", "category", "sourceCore"]
    )
    text_lc = text.lower()
    matched_with_scores: list[tuple[int, dict]] = []
    for theme in THEMES:
        hits = [keyword for keyword in theme["keywords"] if keyword.lower() in text_lc]
        if hits:
            matched_with_scores.append((10 + min(len(hits), 6) * 3, theme))
    matched_with_scores.sort(key=lambda item: item[0], reverse=True)
    matched = [theme for _, theme in matched_with_scores]
    score = sum(theme_score for theme_score, _ in matched_with_scores[:2])
    if item.get("category") in {"ai-products", "tip"}:
        score += 3
    if any(keyword.lower() in text_lc for keyword in LOW_VALUE_KEYWORDS):
        score -= 14
    return score, matched


def priority_label(score: int) -> str:
    if score >= 28:
        return "高"
    if score >= 18:
        return "中高"
    if score >= 10:
        return "中"
    return "观察"


def is_separate_section_item(item: dict) -> bool:
    return str(item.get("analysisSection") or "") == "official_signals"


def official_signal_reportable(item: dict) -> bool:
    if not is_separate_section_item(item):
        return False
    signal = str(item.get("amazonSignal") or item.get("platformSignal") or "")
    priority = str(item.get("priority") or "")
    if has_feed(item, "amazonnews") and signal == "健康类目与合规边界":
        return False
    if signal in {"Amazon 官方运营信号", "平台官方运营信号"} and priority == "观察":
        return False
    return True


def build_high_value_rows(items: list[dict], limit: int = 12) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        if is_separate_section_item(item):
            continue
        score, themes = score_item(item)
        if score < 10 or not themes:
            continue
        primary = themes[0]
        rows.append(
            {
                "score": score,
                "priority": priority_label(score),
                "theme": primary["name"],
                "value": primary["value"],
                "action": primary["action"],
                "item": item,
            }
        )
    rows.sort(key=lambda row: (row["score"], row["item"].get("publishedAt") or ""), reverse=True)
    return rows[:limit]


def build_official_signal_items(items: list[dict], limit: int = 12) -> list[dict]:
    return [item for item in items if official_signal_reportable(item)][:limit]

