"""
Social Copy Style Switcher — 社媒文案风格切换器
A lightweight marketing content generation tool.

Multi-provider: OpenAI · DeepSeek · 通义千问 · 智谱 GLM · Moonshot Kimi

Input: product + platform + audience + desired styles
Output: multi-style copy variants with hooks, body, tags, visual direction
"""

import os
import json
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="社媒文案风格切换器 · Content Style Switcher",
    page_icon="🎨",
    layout="wide",
)

# ─────────────────────────────────────────────
# Style
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
.block-container { padding-top: 2rem; max-width: 1200px; }
h1 { font-weight: 700; letter-spacing: -0.02em; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background: #f3f4f6; border-radius: 10px 10px 0 0; padding: 10px 18px;
}
.stTabs [aria-selected="true"] { background: #1f2937; color: white; }
.tag-pill {
    display: inline-block; background: #eef2ff; color: #4338ca;
    padding: 3px 10px; border-radius: 999px; margin: 2px 4px 2px 0;
    font-size: 13px; font-weight: 500;
}
.hook { font-size: 18px; font-weight: 600; color: #111827; line-height: 1.5; }
.meta-box { background: #f9fafb; border-left: 3px solid #4338ca;
    padding: 10px 14px; border-radius: 4px; font-size: 14px; }
.provider-badge { display: inline-block; background: #ecfdf5; color: #047857;
    padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 500; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🎨 社媒文案风格切换器")
st.caption(
    "Content Style Switcher · 输入一次产品卖点，一次生成多个风格版本 "
    "· 适配小红书 / 抖音 / 微博 / 朋友圈 · 支持 5 种 LLM 接口"
)

# ─────────────────────────────────────────────
# LLM Provider registry
# All providers are OpenAI-compatible; we just swap base_url + api_key.
# ─────────────────────────────────────────────
PROVIDERS = {
    "OpenAI": {
        "base_url": None,
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "default_model": "gpt-4o-mini",
        "key_url": "https://platform.openai.com/api-keys",
        "env_var": "OPENAI_API_KEY",
        "note": "通用首选，中文能力好，需境外网络。",
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "key_url": "https://platform.deepseek.com/api_keys",
        "env_var": "DEEPSEEK_API_KEY",
        "note": "国内可直连，中文强，价格极低（约 1/10 于 GPT-4）。",
    },
    "通义千问 (Qwen)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max"],
        "default_model": "qwen-plus",
        "key_url": "https://dashscope.console.aliyun.com/apiKey",
        "env_var": "DASHSCOPE_API_KEY",
        "note": "阿里云，中文营销场景理解好，国内直连。",
    },
    "智谱 GLM": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": ["glm-4-plus", "glm-4-air", "glm-4-flash"],
        "default_model": "glm-4-air",
        "key_url": "https://bigmodel.cn/usercenter/apikeys",
        "env_var": "ZHIPU_API_KEY",
        "note": "清华系，中文长文本表现稳，国内直连。",
    },
    "Moonshot Kimi": {
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "key_url": "https://platform.moonshot.cn/console/api-keys",
        "env_var": "MOONSHOT_API_KEY",
        "note": "月之暗面，长上下文强，适合跑大量参考资料。",
    },
    "自定义 (OpenAI 兼容)": {
        "base_url": "",
        "models": [],
        "default_model": "",
        "key_url": "",
        "env_var": "",
        "note": "任意 OpenAI 兼容端点（火山方舟 / 百度千帆 / 本地 Ollama 等）。",
    },
}

# ─────────────────────────────────────────────
# Platform / Style presets
# ─────────────────────────────────────────────
PLATFORMS = {
    "小红书": {
        "tone": "亲切真实、口语化、善用 emoji、开头强钩子",
        "length": "标题 ≤ 20 字；正文 200-400 字；分段短；结尾引互动",
        "tags": "3-5 个话题标签，混合精准人群标签 + 大流量泛标签",
        "avoid": "避免过度推销语气、避免太长的段落、避免生硬的广告词",
    },
    "抖音": {
        "tone": "更口语、节奏快、第一句定生死、有画面感",
        "length": "80-150 字口播脚本感、句子短、听得懂",
        "tags": "1-3 个话题标签，不宜过多",
        "avoid": "避免书面语、避免复杂结构、避免没有钩子的开头",
    },
    "微博": {
        "tone": "直接、幽默、可带梗、可自嘲",
        "length": "140-300 字、段落少、可 @ 相关账号",
        "tags": "2-4 个话题标签",
        "avoid": "避免过度煽情、避免长篇说教",
    },
    "微信朋友圈": {
        "tone": "克制、生活化、第一人称、不过度推销",
        "length": "100-200 字、少 emoji、像真实分享",
        "tags": "不需要话题标签",
        "avoid": "避免明显的广告词、避免配过多商品图感",
    },
}

STYLES = {
    "真实种草": "像朋友真诚推荐，有真实使用体验感，有细节，少夸张词",
    "测评对比": "理性对比优劣，给出数据或量化描述，有明确结论",
    "小众文艺": "文艺调性，有画面感和氛围感，克制的审美表达",
    "幽默段子": "有梗、自嘲式幽默、能被转发分享",
    "专业测评": "成分 / 技术 / 工艺角度切入，有干货，建立专业权威感",
    "情绪共鸣": "戳中痛点或生活情绪，有故事感，有代入感",
    "紧迫种草": "限时、限量、价格锚点，适合促销节点",
}

AUDIENCES = [
    "学生党",
    "职场新人",
    "精致妈妈",
    "Z 世代男性",
    "都市白领女性",
    "小镇青年",
    "高端消费者",
    "新手爸妈",
    "其他（自填）",
]

# ─────────────────────────────────────────────
# Sidebar — Provider & Settings
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ LLM 接口")

    provider_name = st.selectbox(
        "选择接口",
        list(PROVIDERS.keys()),
        index=1,  # DeepSeek default — accessible in CN
        help="所有接口使用 OpenAI 兼容协议，同一套 prompt 共用。",
    )
    p = PROVIDERS[provider_name]
    st.markdown(
        f"<span class='provider-badge'>{provider_name}</span> &nbsp; "
        f"<span style='font-size:12px;color:#6b7280'>{p['note']}</span>",
        unsafe_allow_html=True,
    )

    # Reset model cache if user switched provider
    if st.session_state.get("_last_provider") != provider_name:
        st.session_state.pop("available_models", None)
        st.session_state.pop("conn_status", None)
        st.session_state["_last_provider"] = provider_name

    is_custom = provider_name == "自定义 (OpenAI 兼容)"

    # ① 地址
    if is_custom:
        base_url = st.text_input(
            "① 地址 (Base URL)",
            value=st.session_state.get("custom_base", ""),
            placeholder="https://api.blanka.cc/v1",
            help="OpenAI 兼容端点，例：中转站 / 火山方舟 / 本地 Ollama",
            key="custom_base",
        )
    else:
        base_url = p["base_url"]
        st.text_input("① 地址 (Base URL)", value=base_url or "OpenAI 默认", disabled=True)

    # ② 密钥
    api_key = st.text_input(
        "② 密钥 (API Key)",
        type="password",
        value=os.getenv(p["env_var"], "") if p["env_var"] else "",
        help=f"[在哪拿 key →]({p['key_url']})" if p["key_url"] else "你的中转站或自建端点的 key",
    )
    if p["key_url"]:
        st.caption(f"[获取 API Key →]({p['key_url']})")

    # ③ 获取模型列表
    fetch_col, _ = st.columns([1, 1])
    with fetch_col:
        if st.button("③ 获取模型列表", disabled=not (api_key and (base_url or not is_custom)), use_container_width=True):
            try:
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                client = OpenAI(**kwargs)
                resp = client.models.list()
                ids = sorted({getattr(m, "id", str(m)) for m in resp.data})
                if ids:
                    st.session_state["available_models"] = ids
                    st.success(f"✅ 拉到 {len(ids)} 个模型")
                else:
                    st.warning("服务器返回空列表。")
            except Exception as e:
                st.session_state.pop("available_models", None)
                st.error(f"拉取失败：{str(e)[:200]}")

    fetched = st.session_state.get("available_models")

    # ④ 选模型
    if fetched:
        # Prefer the preset default if it's in the fetched list
        default_idx = 0
        if not is_custom and p["default_model"] in fetched:
            default_idx = fetched.index(p["default_model"])
        model = st.selectbox("④ 选模型 (已从服务器拉取)", fetched, index=default_idx)
    elif is_custom:
        model = st.text_input(
            "④ 模型名 (手填 or 先点③)",
            placeholder="e.g. grok-4.6, claude-sonnet-4.5, deepseek-chat",
        )
    else:
        model = st.selectbox(
            "④ 选模型 (预设列表)",
            p["models"],
            index=p["models"].index(p["default_model"]) if p["default_model"] in p["models"] else 0,
        )

    # ⑤ 测试连接
    if st.button("⑤ 测试连接", disabled=not (api_key and model), use_container_width=True):
        try:
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            client = OpenAI(**kwargs)
            test_resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "回复一个字：好"}],
                max_tokens=10,
            )
            reply = test_resp.choices[0].message.content.strip()
            st.session_state["conn_status"] = ("ok", f"✅ 连接成功 · 模型返回：{reply[:30]}")
        except Exception as e:
            st.session_state["conn_status"] = ("err", f"❌ 测试失败：{str(e)[:200]}")

    status = st.session_state.get("conn_status")
    if status:
        (st.success if status[0] == "ok" else st.error)(status[1])

    st.divider()
    temperature = st.slider("创意度 (temperature)", 0.3, 1.2, 0.85, 0.05)
    st.divider()
    use_example = st.button("📋 载入示例（Clinique 烟酰胺精华）", use_container_width=True)
    st.divider()
    st.markdown(
        """
**About**

Lightweight marketing content generation tool for integrated-marketing
and KOL workflows.

**Multi-provider**: swap LLM backend with one dropdown — same prompt,
one of 5 built-in providers or any OpenAI-compatible endpoint.

**Stack:** Streamlit · OpenAI-compatible SDK · Python
"""
    )

# ─────────────────────────────────────────────
# Example data
# ─────────────────────────────────────────────
if use_example or "example_loaded" in st.session_state:
    st.session_state["example_loaded"] = True
    st.session_state.setdefault("brand_val", "Clinique 10% 烟酰胺精华")
    st.session_state.setdefault(
        "points_val",
        "添加 10% 高浓度烟酰胺\n临床测试 28 天提亮肤色\n敏感肌友好配方，无酒精无香精\n小众但口碑扎实",
    )

# ─────────────────────────────────────────────
# Inputs
# ─────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    brand = st.text_input(
        "品牌 / 产品名",
        value=st.session_state.get("brand_val", ""),
        placeholder="e.g. Alfa Romeo Tonale 混动",
    )
    selling_points = st.text_area(
        "核心卖点（每行一条）",
        value=st.session_state.get("points_val", ""),
        height=160,
        placeholder="e.g.\n首款插电混动车型\n意式设计语言\n百公里 0 油耗通勤",
    )

with col2:
    platform = st.radio("投放平台", list(PLATFORMS.keys()), index=0)
    audience_sel = st.selectbox("目标人群", AUDIENCES, index=0)
    if audience_sel == "其他（自填）":
        audience = st.text_input("输入目标人群", placeholder="e.g. 油皮大学生")
    else:
        audience = audience_sel

styles = st.multiselect(
    "选择 2-4 个风格（推荐 3 个）",
    list(STYLES.keys()),
    default=["真实种草", "测评对比", "情绪共鸣"],
    max_selections=4,
)

can_go = all([api_key, brand, selling_points, styles, model])
go = st.button(
    "🚀 生成文案",
    type="primary",
    use_container_width=True,
    disabled=not can_go,
)
if not can_go:
    missing = []
    if not api_key:
        missing.append("API Key")
    if not model:
        missing.append("模型名")
    if not brand:
        missing.append("品牌/产品名")
    if not selling_points:
        missing.append("核心卖点")
    if not styles:
        missing.append("至少选 1 个风格")
    st.caption(f"⏳ 还需要：{' · '.join(missing)}")

# ─────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────
def build_prompt(brand, selling_points, platform, audience, styles):
    cfg = PLATFORMS[platform]
    styles_desc = "\n".join(f"- **{s}**：{STYLES[s]}" for s in styles)
    return f"""你是一位资深的中文社媒内容策划，专攻 {platform} 平台的品牌营销内容。
请为以下产品生成 {len(styles)} 个不同风格的文案。

===== 产品信息 =====
品牌 / 产品：{brand}
核心卖点：
{selling_points}

===== 投放目标 =====
平台：{platform}
目标人群：{audience}

===== 平台规范（务必遵守） =====
语气：{cfg['tone']}
长度与格式：{cfg['length']}
话题标签：{cfg['tags']}
避雷：{cfg['avoid']}

===== 需要生成的 {len(styles)} 个风格 =====
{styles_desc}

===== 要求 =====
1. 每个风格生成一个完整文案，风格之间要有明显差异
2. 开头钩子要强，第一句话决定要不要继续读
3. 话题标签要混合精准 + 流量，不要只给大词
4. 视觉建议要具体（配图场景 / 画面构图 / 色调）
5. 策略逻辑要说清楚：这个风格为什么对"{audience}"这个人群有效

严格按以下 JSON 结构返回，不要输出 JSON 以外的任何内容：

{{
  "variants": [
    {{
      "style": "风格名（与输入一致）",
      "hook": "开头钩子（1 句，不超过 25 字）",
      "body": "正文全文",
      "tags": ["#话题1", "#话题2", "#话题3"],
      "visual_tip": "配图/视觉建议（1-2 句具体描述）",
      "why_it_works": "为什么这个风格对这个人群有效（1-2 句）"
    }}
  ]
}}
"""

# ─────────────────────────────────────────────
# LLM call — provider-agnostic
# ─────────────────────────────────────────────
def call_llm(api_key, base_url, model, prompt, temperature):
    """All providers are OpenAI-compatible; swap base_url only."""
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    # Not every provider supports response_format=json_object; try then fallback.
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
    except Exception:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt + "\n\n再次强调：只返回 JSON，不要任何其它内容。"}],
            temperature=temperature,
        )
    return resp.choices[0].message.content


def extract_json(raw):
    """Parse JSON; strip markdown fencing if present; grab outermost braces."""
    s = raw.strip()
    if s.startswith("```"):
        parts = s.split("```")
        if len(parts) >= 2:
            s = parts[1]
        if s.lstrip().lower().startswith("json"):
            s = s.lstrip()[4:]
        s = s.strip("`").strip()
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        s = s[start : end + 1]
    return json.loads(s)


# ─────────────────────────────────────────────
# Generation
# ─────────────────────────────────────────────
if go:
    with st.spinner(f"正在用 {provider_name} · {model} 生成 {len(styles)} 个风格..."):
        try:
            prompt = build_prompt(brand, selling_points, platform, audience, styles)
            raw = call_llm(api_key, base_url, model, prompt, temperature)
            data = extract_json(raw)
            variants = data.get("variants", [])
            if not variants:
                st.error("生成为空，请重试或调整输入。")
                st.code(raw)
            else:
                st.success(
                    f"✅ 已生成 {len(variants)} 个风格版本 · 平台：{platform} "
                    f"· 接口：{provider_name} ({model})"
                )
                tabs = st.tabs([v["style"] for v in variants])
                for tab, v in zip(tabs, variants):
                    with tab:
                        st.markdown(
                            f"<div class='hook'>🪝 {v['hook']}</div>",
                            unsafe_allow_html=True,
                        )
                        st.write("")
                        st.markdown("**📝 正文**")
                        st.write(v["body"])
                        st.divider()

                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.markdown("**🏷️ 话题标签**")
                            tag_html = " ".join(
                                f"<span class='tag-pill'>{t}</span>" for t in v["tags"]
                            )
                            st.markdown(tag_html, unsafe_allow_html=True)
                        with c2:
                            st.markdown("**🎨 视觉建议**")
                            st.write(v["visual_tip"])

                        st.markdown("**💡 策略逻辑**")
                        st.markdown(
                            f"<div class='meta-box'>{v['why_it_works']}</div>",
                            unsafe_allow_html=True,
                        )

                        st.divider()
                        full = (
                            f"{v['hook']}\n\n{v['body']}\n\n" + " ".join(v["tags"])
                        )
                        st.markdown("**📋 一键复制全文**")
                        st.code(full, language=None)

        except json.JSONDecodeError:
            st.error("模型返回的内容不是合法 JSON。可能是模型不支持 JSON 模式——换一个更强的模型或点击重新生成。")
            st.code(raw if "raw" in dir() else "")
        except Exception as e:
            st.error(f"生成失败：{e}")
            st.caption("常见原因：API Key 无效、模型名拼错、网络不通、未开通该模型权限。")

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ 本工具仅做营销内容创意辅助，生成结果需人工审核。 · "
    "Not therapy / Not legal advice / Not impersonation."
)
