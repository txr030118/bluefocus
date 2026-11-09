# 🎨 Social Copy Style Switcher · 社媒文案风格切换器

A lightweight AI tool for integrated-marketing and KOL workflows.
Enter a product once — generate multiple style variants, adapted to each
Chinese social platform.

一个面向整合营销 / KOL 投放的轻量 AI 工具：输入一次产品卖点，一次生成多个风格的
文案版本，按平台规范自动适配。**支持 5 种主流 LLM 接口**，国内外 key 都能用。

**Live demo:** _(add your Streamlit Cloud URL here after deployment)_

---

## Why this tool

In Chinese social campaigns, the same product usually ships as 3–5 different
copy variants: one for 小红书, one for 抖音, one for 微博, each with a
different voice (真实种草, 测评对比, 情绪共鸣, 幽默段子…).

Writing those variants by hand is slow and inconsistent. This tool turns the
inputs a marketing planner already has — product, selling points, platform,
target audience — into structured, platform-aware copy variants in one call.

在中国社媒营销中，一个产品往往要产出 3–5 个风格的文案，分别投到不同平台、不同
KOL。手工写耗时且难保持统一。这个工具把策划已有的基础输入一次转化成多风格、
分平台适配的结构化文案。

---

## Multi-provider support · 多接口支持

One prompt, pluggable backend. Pick the LLM you have access to:

| Provider | 国内直连 | 中文能力 | 费用 | 获取 API Key |
|----------|---------|---------|------|-------------|
| **OpenAI** (GPT-4o / mini) | ❌ 需境外网络 | ⭐⭐⭐⭐⭐ | 中 | [platform.openai.com](https://platform.openai.com/api-keys) |
| **DeepSeek** (chat / reasoner) | ✅ | ⭐⭐⭐⭐⭐ | **极低** (~1/10) | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| **通义千问** (qwen-plus / max) | ✅ | ⭐⭐⭐⭐⭐ | 低 | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/apiKey) |
| **智谱 GLM** (glm-4-plus / air) | ✅ | ⭐⭐⭐⭐ | 低 | [bigmodel.cn](https://bigmodel.cn/usercenter/apikeys) |
| **Moonshot Kimi** (8k / 32k / 128k) | ✅ | ⭐⭐⭐⭐ | 中 | [platform.moonshot.cn](https://platform.moonshot.cn/console/api-keys) |
| **自定义 OpenAI 兼容端点** | — | — | — | 火山方舟 / 百度千帆 / Ollama 等 |

All six go through the same OpenAI-compatible SDK — the code swaps only
`base_url` and `api_key`. No separate SDKs, no per-provider branch logic.

> 面向蓝标/中国市场的现实：OpenAI 不是人人能拿到 key，且国内团队跨境调用延迟高。
> 本工具默认选择 DeepSeek（国内直连、中文表现强、价格仅为 GPT-4 的 1/10）。

### 5 步接入任意 OpenAI 兼容服务（含中转站 / 聚合网关）

选择 `自定义 (OpenAI 兼容)` 时，侧边栏引导 5 步：

1. **地址 (Base URL)** — 中转站或自建端点，如 `https://api.blanka.cc/v1`
2. **密钥 (API Key)** — 证明权限，费用从该账户扣
3. **获取模型列表** — 用前两项向 `/models` 端点询问可用模型；能拉到就说明地址和密钥都对
4. **选模型** — 从下拉里选，如 `grok-4.6`、`claude-sonnet-4.5`、`deepseek-chat`
5. **测试连接** — 发一条小消息验证账户有余额、模型可用

这个流程既支持中转站 / 聚合网关（一个 key 用多家模型），也支持本地 Ollama 和企业自建推理服务。

---

## What it does

Given:

- 品牌 / 产品名
- 核心卖点（多行）
- 投放平台（小红书 / 抖音 / 微博 / 朋友圈）
- 目标人群（学生党 / 职场新人 / 精致妈妈 / ...）
- 想要的风格（真实种草 / 测评对比 / 小众文艺 / 幽默段子 / 专业测评 / 情绪共鸣 /
  紧迫种草）

Returns, per selected style:

1. **Hook** — 开头钩子（≤ 25 字）
2. **Body** — 正文全文（按平台长度适配）
3. **Tags** — 话题标签（混合精准 + 流量）
4. **Visual tip** — 配图 / 画面构图 / 色调建议
5. **Why it works** — 为什么这个风格对这个人群有效（策略逻辑）

Each style comes out as a separate tab with a one-click copy block.

---

## Platform adaptation

Each platform has built-in rules the model is instructed to follow — tone,
length, tag density, and what to avoid:

| 平台 | 语气 | 长度 | 标签 |
|------|------|------|------|
| 小红书 | 亲切真实、善用 emoji、强钩子 | 标题 ≤ 20 字 / 正文 200–400 字 | 3–5 个 |
| 抖音 | 口语、节奏快、第一句定生死 | 80–150 字口播感 | 1–3 个 |
| 微博 | 直接、幽默、可带梗 | 140–300 字 | 2–4 个 |
| 朋友圈 | 克制、生活化、第一人称 | 100–200 字 | 不需要 |

---

## Design principles

- **Platform-first**，不是 style-first — 先按平台卡语气和长度，再套风格
- **Provider-agnostic** — 同一套 prompt 跑在不同 LLM 上，策划挑便宜/合规的用
- **Structured output** — JSON schema 约束模型输出，字段完整；失败时自动降级
- **Transparent reasoning** — 每条文案都带"策略逻辑"字段，说明为什么这么写
- **Human in the loop** — 工具是创意辅助，最终稿需要人工审核
- **BYO key** — 用户用自己的 API Key，数据不落地

---

## Tech stack

- **Frontend:** Streamlit
- **LLM gateway:** OpenAI-compatible SDK (`openai` v1+) with runtime `base_url` swap
- **Supported endpoints:** OpenAI, DeepSeek, Qwen (DashScope), Zhipu GLM, Moonshot Kimi, 任意 OpenAI 兼容端点
- **JSON robustness:** `response_format=json_object` 优先，不支持时降级到 prompt-only JSON + 容错解析
- **Deployment:** Streamlit Community Cloud

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501, pick a provider in the sidebar, paste your key.

---

## Deploy to Streamlit Cloud

1. Push this folder to a public GitHub repository.
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. New app → point at this repo → Main file: `streamlit_app.py` → Deploy.
4. Share the resulting `https://*.streamlit.app` URL.

Viewers paste their own API key for whichever provider they prefer. Nothing
is stored.

---

## Roadmap

- 多语言：英文 / 日文 / 东南亚本地化
- KOL 匹配：输入文案风格 → 推荐适配的达人类型
- Brand voice 预设：一个品牌一次训练，后续直接复用
- A/B 评分：批量生成 + 预估点击率 / 互动率
- Claude / Gemini 原生 SDK 接入（当前通过 OpenRouter 可用）

---

## Author

Built by **Xiaorui (Grace) Tang** — MSc Business Analytics, UCL School of
Management. Marketing-side context from a previous internship at BlueFocus
Communication (KOL management for Alfa Romeo and Clinique, Shanghai 2023).

---

## Disclaimer

This is a creative-assistance tool. All generated content must be reviewed
by a human before publication. Not legal advice. Not a replacement for
brand guidelines or compliance review.

本工具仅为创意辅助，所有生成内容发布前需人工审核。不构成法律建议，不替代品牌
指引与合规审查。
