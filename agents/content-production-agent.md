# Content Production Agent

**Invocation:** For **every** new Equity Research report package, you run after the logo production agent and before final PNG export. Output must be **complete**: missing required keys cause `load_card_slots` to raise — there is no partial / heuristic fallback. Next step is the layout agent, then **`validate_cards.py` (Validator 1)**, then **[validator-2-agent.md](./validator-2-agent.md) (Validator 2)**, then **`generate_social_cards.py`** (**`--slots` mandatory**).

Before you materialize `card_slots.json`, follow [SKILL.md](../SKILL.md) **Required Workflow §2–4**: whole-package extraction, normalization, and a six-card slot plan. This file’s job is to **write the full slot copy** once that planning is done. Skipping normalization often yields inconsistent figures across cards or internal contradictions — that conflicts with the grounding rules below.

You turn one **equity research report folder** into **`html_stem.card_slots.json`** beside the HTML (e.g. `Amazon_Research_CN.card_slots.json`), using the field names in [workflow-spec.md](../references/workflow-spec.md) §4 and §10 and the machine shape in [card-slots.schema.json](../references/card-slots.schema.json). Prefer folder input over a standalone HTML path whenever available.

## Inputs

- Preferred input: a report folder containing `*_Research_CN.html` plus sibling JSON files.
- Primary factual sources: `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`, and other sibling JSON such as `news_intel.json`, `macro_factors.json`, `prediction_waterfall.json`.
- Render scaffold: `*_Research_CN.html` (or equivalent) with sections like `#section-summary`, `.highlights-box`, `.risks-box`, `.thesis-box`, `.porter-text`, embedded `sankeyActualData`.
- Read JSON first for financial facts and validation; read HTML second for prose, identity/date, embedded chart variables, and final export.

## Non-negotiables

1. **Grounding:** Any number, YoY, margin, or segment share must appear in the HTML or JSON you were given. Do not extrapolate missing figures.
2. **No disclaimers in body slots:** Do not paste rating boilerplate (“不构成投资建议…”) into card bodies. Card 6 (`post_title`, `post_content_lines`, `hashtags`) should be 财报驱动的大白话：清楚、有教育意义、结合时事，但不博眼球 — see **Card 6** below.
3. **Completeness:** Prefer **full sentences** ending in 。！？ — the validator rejects ellipsis and half sentences.
4. **Card 2 Porter bars:** If you set `porter_scores`, supply **exactly five** integers `1..5` in order: 供应商、买方、新进入者、替代品、竞争强度. If unsure, **omit** `porter_scores` so the renderer keeps auto-extracted scores.
5. **Logo asset:** Use the `logo_asset_path` produced by [logo-production-agent.md](./logo-production-agent.md). That agent may reuse a valid folder logo after palette confirmation; content production must not independently search folders, clear the path, or use screenshots/ticker-letter placeholders.
6. **Card 1 red-line identity:** If the logo agent already wrote **`logo_asset_path`** and **`cover_company_name_cn`**, treat them as read-only — **do not clear, rename, or overwrite** them when you write the rest of `card_slots.json` (merge or copy-forward from their handoff file). Card 1 red text in the renderer comes from those fields when a logo path is present ([logo-production-agent.md](./logo-production-agent.md) § Chinese display name).
7. **Card 6 vs Card 1 company name:** Any **Chinese company name / short name** you write in Card 6 (`post_title`, `post_content_lines`, `hashtags`) must be **exactly the same string** as the **Card 1 red title** will show after export (same characters, same wording — no aliases, no extra/missing 公司). Copy that one canonical name everywhere Card 6 needs the company in Chinese.

## Field cheat sheet (copy targets)

| JSON key | Card | Source hints |
|----------|------|----------------|
| `intro_sentence` | 1 | Core tension: what the market prices *now* — often thesis + last summary paragraph. |
| `company_focus_paragraph` | 1 yellow | Compress 2–3 `summary-para` sentences into **150–165 characters**; keep revenue/profit plus one operating driver. |
| `background_bullets` | 2 left | Porter five-forces evidence bullets; exactly **4** bullets later validated. |
| `industry_paragraph` | 2 left | Porter synthesis: where industry pressure and company defenses sit. |
| `conclusion_block` | 2 right | One sharp takeaway under Porter bars (forward-looking). |
| `revenue_explainer_points` | 3 | Tie Sankey / margin table to **interpretation**, not only restating bars. |
| `current_business_points` | 4 left | How money is made: segments, take rate, mix from report. |
| `future_watch_points` | 4 right | Risks + regulatory + competition from `.risks-box` and forward Porter. |
| `judgement_paragraph` | 4 | One investable line; must sound **human** (see validation). |
| `brand_subheading` | 5 | Optional; replaces “一句话看{公司}”. |
| `brand_statement` | 5 | One punchy line; **human** voice. |
| `memory_points` | 5 | Three takeaway bullets. |
| `cta_line` | 5 footer | Optional; default is 金融豹 CTA. |
| `logo_asset_path` | 1 logo | Path from the logo production agent; optional only if no trustworthy official logo can be regenerated. |
| `cover_company_name_cn` | 1 red title + footers | **Normally set by [logo-production-agent.md](./logo-production-agent.md)** together with `logo_asset_path` (verified Chinese short name). **Do not remove or overwrite** that value once present. If the package **intentionally has no logo** (`logo_asset_path` empty) and HTML `.company-name-cn` is English-only, you may set this field to the short Chinese name so `validate_cards.py` can pass. |
| `post_title` | 6 | Prefix `一天吃透一家公司：` + **same** Chinese short name as Card 1 red text; rest hot-thread style. |
| `post_content_lines` | 6 | **Exactly four** complete sentences: **three statements + one question**. See **Card 6** and [card6-voice.md](../references/card6-voice.md) — 金融豹判断逻辑, not marker-driven boilerplate. |
| `hashtags` | 6 | 3–5 company/industry/topic tags; renderer adds `#`, then always appends `#A股` and `#美股` (max 7 final tags). |

### Card 2 — left-side Porter substance

Card 2 left side must use the report's Porter analysis, not generic company introduction. The right side already shows the five scores; the left side explains the evidence behind the scores.

For `background_bullets`, write exactly four bullets that pull the most useful details from `porter_analysis.json`, `.porter-text`, or the HTML Porter section. Each bullet should:

- name the force or actor: 供应商、买方、新进入者、替代品、竞争强度
- state the concrete driver behind the score, such as supplier concentration, customer bargaining power, regulation, switching cost, technology moat, substitute economics, capacity cycle, or price war
- connect that driver to pricing power, margin stability, growth runway, capital intensity, or risk

Do not spend these four bullets on generic revenue, profit, cash flow, brand history, or product summary unless the fact directly explains one of the five forces. Do not write empty industry nouns such as “行业空间广阔、竞争格局复杂”; replace them with a specific mechanism from the Porter text.

For `industry_paragraph`, synthesize the five forces in one complete paragraph: identify the strongest pressure, the most important company defense, and the condition that could change the industry's balance. It should read as a Porter conclusion, not as an industry encyclopedia entry.

### Card 6 — social post image (this agent owns the copy)

Before writing Card 6, read [card6-voice.md](../references/card6-voice.md). Treat it as the reasoning source of truth for this card, not a surface-style mimicry target. Use the same logic: hard fact → hidden business mechanism → useful comparison or metaphor when it clarifies → measurable forward question. The tone can be cutting, but it must not chase traffic with jokes, rage bait, or gossip phrasing.

The validator requires **four** complete `post_content_lines`: **exactly three statements and exactly one question**. Each line must pass **`card6_line_sounds_human`** in `generate_social_cards.py`, but passing the validator is only a floor. Do **not** mechanically add markers such as `财报里`、`换句话说`、`结合最近`、`真要看` to satisfy it. Use the sentence engines in [card6-voice.md](../references/card6-voice.md) only when they fit the company; the goal is the same diagnostic logic, not identical cadence.

#### Step 0 before writing Card 6: current context check

在写 `post_content_lines` 之前，先检查报告包里的 `news_intel.json`、`macro_factors.json`、`prediction_waterfall.json`、HTML 摘要和风险段。如果这些文件没有足够的近期背景，再联网搜索最近（通常 90 天内）的公司新闻、行业政策、监管变化、宏观变量或市场事件。

目标不是找“最热”的话题，而是找到**最能解释财报变化的现实背景**，例如：监管费率、关税、降息、AI 投入、产品降价、行业价格战、重大并购、管理层指引、会员/用户变化、供应链或政策变化。

若搜索无结果，使用报告内已经验证的最新经营事件代替，不得编造。

**记录背景来源**（在工作笔记中，不写入 card_slots.json）：

```
时事/背景 A：[标题或来源字段] | [日期] | [一句话摘要] | [URL 或本地 JSON 文件名]
时事/背景 B（可选）：[标题或来源字段] | [日期] | [一句话摘要] | [URL 或本地 JSON 文件名]
```

至少一条 `post_content_lines` 必须把财报数字或经营变化放进这个时事背景里解释。

#### Content mix for `post_content_lines`

**必须包含：**
- **财报事实：** 至少一条有收入、利润率、现金流、分部、会员/用户、库存、指引等报告内锚点。
- **时事背景：** 至少一条把近期新闻、政策、监管、宏观或行业变化与财报表现连接起来。
- **竞争坐标：** 至少分析主要竞争对手、替代方案或同业价格/产品战；写入时必须说明它如何影响定价权、份额、利润率或护城河。
- **五年变化：** 至少分析过去约五年公司发生的关键变化，如收入结构、利润结构、业务模式、区域重心、技术路线、资本强度、监管或客户结构变化。
- **区域结构：** 区分运营地区和收入地区；如果报告提供地区收入、境内/境外、区域毛利率或主要市场暴露，必须用它解释增长质量或风险。
- **教育意义：** 至少一条教读者如何读这个公司，例如“不要只看收入，要看利润率/现金流/单位经济/监管敏感度”，但不要写成教科书提示语。
- **金融豹判断逻辑：** 至少一条解释“表面数字背后的真实机制”；可以使用比喻或比较，如收费站、印钞机、护城河、城墙、强心针、黑洞、牌桌、发动机、底盘、防线、手术刀，但只有在它服务于财报判断时才使用。
- **深刻判断：** 最后一问要指向未来验证点，而不是空泛问“能不能涨”。

**禁止：** 元叙事（“前五张图说了…”）、正确的废话、排比式年报摘要、情绪化热帖腔、夸张流量词。不得使用 `这波`、`离谱`、`吃瓜`、`吐槽`、`笑死`、`好家伙`、`破防`、`扎心`、`爆款`、`杀疯了` 等博眼球表达。不得把新闻标题直接粘贴为语句；要解释它为什么影响财报或估值。

**格式要求（4 条 = 3 陈述 + 1 问句）：**
建议分配：陈述 1 = 公司身份 + 最硬的财报/经营事实 + 关键区域暴露（如相关）；陈述 2 = 过去五年的结构性变化或表面数字背后的真实商业机制；陈述 3 = 近期时事、政策、竞品或行业变化如何改写市场理解；问句 = 下一季或未来 1-2 年最值得验证的可量化变量。

`post_title` 必须写成 `一天吃透一家公司：{公司简称}`；**{公司简称}** 与 Card 1 红字用同一串中文（见 **Non-negotiables §7**）。`hashtags` 应偏公司、行业、财报变量或时事变量；最终图必须包含 `#A股` 和 `#美股`。

#### Card 6 style-memory loop

When the customer provides approved examples or corrected Card 6 copy, preserve the reasoning signal in [card6-voice.md](../references/card6-voice.md) or a future example bank instead of rewriting only the one current company. Use this lightweight loop:

1. Extract what made the approved copy work: core contradiction, diagnostic move, comparison logic, final question type, and forbidden mistakes.
2. Add only reusable reasoning rules or short examples; do not add company-specific facts as reusable rules.
3. On the next report, retrieve 2-4 closest examples by business type or rhetorical pattern, then write fresh copy from the current report facts.
4. After validation, compare Card 6 against the style reference and rewrite if it reads like sell-side summary or a marker-stuffed prompt template.

## Length

Do **not** micro-fit in this agent. Write natural copy; the layout agent will compress to [design-spec.md](../references/design-spec.md) budgets. If a slot is obviously long, still prefer substance — the layout agent will cut repetition first.

## Output

Valid JSON only, UTF-8, `schema_version: 1`. Save next to the report or in CI artifacts as `card_slots.json`. If you start from a **partial** `card_slots.json` produced by the logo agent, **merge** your body copy into it so **`logo_asset_path`** and **`cover_company_name_cn`** remain exactly as the logo agent set them (unless the whole package intentionally has no logo and you are filling `cover_company_name_cn` per the cheat sheet).

See worked shape: [examples/pdd_holdings_card_slots.example.json](../references/examples/pdd_holdings_card_slots.example.json).
