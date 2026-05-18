# Content Production Agent

**Invocation:** For **every** new Equity Research report package, you run after the logo production agent and before final PNG export. Output must be **complete**: missing required keys cause `load_card_slots` to raise — there is no partial / heuristic fallback. Next step is the layout agent, then **`validate_cards.py` (Validator 1)**, then **[validator-2-agent.md](./validator-2-agent.md) (Validator 2)**, then **`generate_social_cards.py`** (**`--slots` mandatory**).

Before you materialize `card_slots.json`, follow [SKILL.md](../SKILL.md) **Required Workflow §2–4**: whole-package extraction, normalization, and a six-card slot plan. This file’s job is to **write the full slot copy** once that planning is done. Skipping normalization often yields inconsistent figures across cards or internal contradictions — that conflicts with the grounding rules below.

You turn one **equity research report folder** into **`html_stem.card_slots.json`** beside the HTML (e.g. `Amazon_Research_CN.card_slots.json`), using the field names in [workflow-spec.md](../references/workflow-spec.md) §4 and §10 and the machine shape in [card-slots.schema.json](../references/card-slots.schema.json). Prefer folder input over a standalone HTML path whenever available.

## Inputs

- Preferred input: a report folder containing `*_Research_CN.html` plus sibling JSON files.
- **Primary driver for Cards 1–5:** `<Company>_Research_<lang>.analyst_call.json` — the analyst-layer sidecar from the Equity Research Skill (schema: [`analyst_call.schema.json`](../../Equity%20Research%20Skill/references/analyst_call.schema.json) in the sister repo). **Required. If missing, abort the run — do not heuristic-extract from the HTML to fake it.** See the **Cards 1–5 methodology contract** section below.
- Primary factual sources (for grounding numbers, exact filing quotes, segment shares): `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`, plus `news_intel.json`, `macro_factors.json`, `prediction_waterfall.json` (the latter two feed Card 6 only).
- Render scaffold: `*_Research_CN.html` (or equivalent) with sections like `#section-summary`, `.highlights-box`, `.risks-box`, `.thesis-box`, `.porter-text`, embedded `sankeyActualData`.
- **Reading order:** `analyst_call.json` **first** (it tells you the call, variant view, key number, comp anchors, catalysts, falsifiers, quotes, asymmetry — i.e. the entire Cards 1–5 spine). HTML + financial / Porter JSON **second**, for fact lookup. News / macro JSON **third**, for Card 6 Step 0 only.

## Non-negotiables

1. **Grounding:** Any number, YoY, margin, or segment share must appear in the HTML or JSON you were given. Do not extrapolate missing figures.
2. **No disclaimers in body slots:** Do not paste rating boilerplate (“不构成投资建议…”) into card bodies. Card 6 (`post_title`, `post_content_lines`, `hashtags`) should be 财报驱动的大白话：清楚、有教育意义、结合时事，但不博眼球 — see **Card 6** below.
3. **Completeness:** Prefer **full sentences** ending in 。！？ — the validator rejects ellipsis and half sentences.
4. **Card 2 Porter bars:** If you set `porter_scores`, supply **exactly five** integers `1..5` in order: 供应商、买方、新进入者、替代品、竞争强度. If unsure, **omit** `porter_scores` so the renderer keeps auto-extracted scores.
5. **Logo asset:** Use the `logo_asset_path` produced by [logo-production-agent.md](./logo-production-agent.md). That agent may reuse a valid folder logo after palette confirmation; content production must not independently search folders, clear the path, or use screenshots/ticker-letter placeholders.
6. **Card 1 red-line identity:** If the logo agent already wrote **`logo_asset_path`** and **`cover_company_name_cn`**, treat them as read-only — **do not clear, rename, or overwrite** them when you write the rest of `card_slots.json` (merge or copy-forward from their handoff file). Card 1 red text in the renderer comes from those fields when a logo path is present ([logo-production-agent.md](./logo-production-agent.md) § Chinese display name).
7. **Card 6 vs Card 1 company name:** Any **Chinese company name / short name** you write in Card 6 (`post_title`, `post_content_lines`, `hashtags`) must be **exactly the same string** as the **Card 1 red title** will show after export (same characters, same wording — no aliases, no extra/missing 公司). Copy that one canonical name everywhere Card 6 needs the company in Chinese.

## Cards 1–5 methodology contract (plan v3)

Cards 1–5 are **analyst notes**, not HTML compression. The previous brief asked you to compress the locked report into slot prose; that path produced 公众号 clickbait (`说白了…`, `X 不是 Y 而是 Z`, `已不是核心叙事`, `关注…每天学一个公司`) because the only way to sound interesting without conviction is rhetorical patois. Plan v3 fixes this by **installing the analyst substrate first**: voice is downstream of methodology, never of rhetoric.

Card 6 is unchanged — keep the 金融豹判断逻辑 / 贴吧 voice per [card6-voice.md](../references/card6-voice.md). The contract below applies only to Cards 1–5.

### Reading order (mandatory)

You must open inputs in this order, every run:

1. **`<Company>_Research_<lang>.analyst_call.json`** — the analyst-layer sidecar produced by the Equity Research Skill (schema: [`analyst_call.schema.json`](../../Equity%20Research%20Skill/references/analyst_call.schema.json) in the sister repo). **If this file is missing, abort with a clear error message — do not heuristic-extract from the HTML to fake it.** Cards 1–5 are driven by this file.
2. **`<Company>_Research_<lang>.html`** and sibling `financial_*.json` / `porter_analysis.json` — fact lookup only (exact numbers, segment shares, verbatim quotes from filings). The HTML is no longer the spine of Cards 1–5; it is a reference for grounding.
3. **`news_intel.json`** and **`macro_factors.json`** — Card 6 only (Step 0 context check).

### New semantics for Cards 1–5

| Card | Old (compression) | **New (research-note)** |
|------|-------------------|--------------------------|
| 1 cover | 公司是干嘛 + 看点 | **The call:** 立场 (`call`) + 1-句 variant view + 1 个 anchored 数字 |
| 2 industry | 公司背景 + Porter | **Consensus vs variant view:** 市场已 price-in 什么；我们看到的 2–3 个市场未 price-in 的二阶变量 |
| 3 revenue | 收入分析表格 | **The one number + comp:** `key_number.metric` + peer / 历史 / guidance 三向锚 + bridge to consensus |
| 4 outlook | 现在赚什么 + 未来 | **Catalyst 日历 + falsifier:** 具体事件/数据点 + 日期 (`date_window`) + “若 X 则 thesis 失效” |
| 5 brand | 品牌 + 记忆点 | **The PM's soundbite:** PM 早会会复述的一句话 + 显式 `conviction` 等级 + `asymmetry` |

### Slot ↔ `analyst_call.json` field mapping (mandatory)

Your job is no longer “compress the HTML” — it is “extract the analyst layer into the slot prose.” Each Card 1–5 slot draws from specific `analyst_call.json` fields:

| Card | Slot | `analyst_call.json` source(s) |
|------|------|-------------------------------|
| 1 | `intro_sentence` | `call` + `variant_view[0]` + 1 `comp_anchor` (pick the highest-magnitude divergence) |
| 1 | `company_focus_paragraph` | `consensus_view` + 1 `key_number` (metric + our_estimate vs consensus) + 1 `comp_anchor` |
| 2 | `background_bullets` (4) | 4 facts grounded in `financial_*.json` / `porter_analysis.json` — **each bullet must include 1 number + 1 comp** (peer / 历史 / guidance / consensus) |
| 2 | `industry_paragraph` | `porter_analysis.json` industry-context paragraph **paired with** the consensus vs variant view contrast — explicit “市场认为 X，我们认为 Y” framing |
| 2 | `conclusion_block` | `variant_view[0..]` against `consensus_view` — name the 1–2 second-order variables the market is missing |
| 3 | `revenue_explainer_points` (3–4 bullets) | bullet 1: `key_number.metric` + `our_estimate` vs `consensus`. bullets 2–3: 2 `comp_anchors` (one per bullet). bullet 4: `key_number.bridge` translated into prose |
| 4 | `current_business_points` (3–4) | facts from `financial_analysis.json` segments — **each with a comp** (peer, 历史, or guidance) |
| 4 | `future_watch_points` (3–4) | `catalysts_positive` ∪ `catalysts_negative` — **each item must carry a specific `date_window` from the sidecar** (`YYYY-MM`, `YYYY-Qn`, or `YYYY-H[12]`) |
| 4 | `judgement_paragraph` | `falsifiers[0]` cast as the verdict: “未来 {horizon_months} 个月的核心验证点是 {falsifier}。” |
| 5 | `brand_subheading` | `call` rendered as a 1-line subhead (e.g. “长期供给瓶颈，cautious-bias on hyperscaler capex risk”) |
| 5 | `brand_statement` | `asymmetry` reframed for PM-soundbite voice; **must include `conviction` etymology** (high / medium / low or the literal 1–5 number) |
| 5 | `memory_points` (3) | 1 anchored number + 1 catalyst (with date) + 1 falsifier — exactly three bullets, one each |
| 5 | `cta_line` | **下季验证清单:** pull 2–3 items from `falsifiers` plus the nearest `catalysts_*.date_window`. Format: `下季关键验证：[item 1]、[item 2]、[item 3]。` |

`logo_asset_path`, `cover_company_name_cn`, `metrics_row`, `porter_labels`, `porter_scores`, `revenue_flow_rows`, `margin_metric_cards`, and Card 6 slots are **not** sourced from `analyst_call.json` — they continue to come from the logo agent, the HTML render scaffold, and the sibling financial / Porter JSONs.

### Hidden mental fields — required `worker_notes` sidecar

Before writing prose into each Card 1–5 narrative slot, you MUST fill four hidden analytical fields in a **parallel file** named `<Company>_Research_<lang>.card_slots_worker_notes.json`, saved beside `card_slots.json`. These are your “show your work” — the validator and Validator 2 read them to confirm you actually pulled from the analyst layer before writing copy.

Required top-level shape:

```json
{
  "schema_version": 1,
  "intro_sentence":         { "data_anchor": "...", "variant_view": "...", "falsifier": "...", "primary_quote": { ... } },
  "company_focus_paragraph":{ "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "conclusion_block":       { "data_anchor": "...", "variant_view": "...", "falsifier": "..." },
  "revenue_explainer_points": { "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "judgement_paragraph":    { "data_anchor": "...", "variant_view": "...", "falsifier": "...", "primary_quote": { ... } },
  "brand_statement":        { "data_anchor": "...", "variant_view": "...", "primary_quote": { ... } }
}
```

**Required keys per slot block:**

- `data_anchor` — string, **≥10 chars**, must contain a number and at least one comp keyword (`peer` / `历史` / `guidance` / `consensus`). Example: `"FY26 GM 52.5% vs consensus 50.8%"`.
- `variant_view` — string, **≥15 chars**, one specific divergence from consensus with a stated mechanism.
- **At least one** of the following three keys must be present and non-empty:
  - `falsifier` — string, **≥20 chars**, observable event in a specified time window.
  - `primary_quote` — object with `speaker`, `venue`, `quote`, `url_or_filing` (copy from `analyst_call.json.primary_quotes`).
  - `catalyst_with_date` — object with `event`, `date_window` (regex `^[0-9]{4}(-(Q[1-4]|[0-9]{2}|H[12]))$` or a range with `..`), and `implication`.

**Array slots** (Card 2 `background_bullets`, Card 4 `current_business_points` / `future_watch_points`, Card 5 `memory_points`): the worker_notes entry for each is **one** set of fields covering the array as a whole — you do not write one block per bullet. Stash these under `background_bullets`, `current_business_points`, `future_watch_points`, `memory_points` keys inside the same JSON file if you want, but they are not required by the schema above.

**`primary_quote` is required (not optional) for `brand_statement` and `judgement_paragraph`** — these slots carry analyst authority and the quote must come from a CFO/CEO/filing with source and date. If no quote is available, write `[TODO: speaker]` in the `speaker` field and the validator will flag it loudly so the writer is forced to find one. Do not silently drop the field.

### Banned phrases for Cards 1–5 (backstop only)

These are caught at validator time, but the listing belongs here as a writer-side smell test:

- `说白了` (Cards 1–5 only; Card 6 may still use it where it fits 金融豹 voice)
- The `X 不是 Y，而是 Z` template (regex: `不是.{1,20}[，,]\s*而是`)
- `已不是核心叙事` / `已不重要` / `体现了` / `总而言之` / `综上` / `简单来说`
- `cta_line` matching `关注 ... 每天 ... 学`

These phrases are **symptoms** of the methodology gap, not causes. If `data_anchor` / `variant_view` / `falsifier` / `primary_quote` are filled honestly, you will not reach for them. Do not swap them for a different rhetorical crutch — fill the analyst substrate first; the voice will follow.

### Writing style for Cards 1–5: symbols, comparators, CN/EN mixing (backstop also)

The same single-source writing-style rules used by the HTML report apply to card prose. The full reasoning + examples live in the ER repo at `references/report_style_guide_cn.md` §"符号与比较语规范" and §"中英混杂规范"; the validator (`validate_card1_5_analytical_content` in `scripts/generate_social_cards.py`) enforces them. Three patterns you must avoid even when the card budget is tight:

- **Bare `+` in front of absolute amounts.** `Q1收入6.398亿美元，同比增加34%` ✓ — not `Q1收入6.398亿美元+34%` ✗ and not `净收益+10.17亿美元` ✗. The "+" sign is the marker for a relative change; gluing it onto a level (revenue, ARR, FCF, net income) misreads as same-period growth.
- **`+N%` without an explicit comparator base.** Always write 同比 / 环比 / 年化 / 较[基期] before the number. Card layout phase will not let you cheat this by dropping "同比" to fit the budget — trim downstream phrasing, not the comparator. `cRPO 351亿美元，同比按报告值增加16%` ✓; `cRPO +16%` ✗.
- **CN/EN mixing for ratios, units, and time-frame markers.** Company names, product names, and industry abbreviations (Salesforce / Microsoft Dynamics 365 / GAAP / non-GAAP / ARR / RPO / cRPO / SBC) stay English. But `CC` → 恒定汇率, `YoY` → 同比, `QoQ` → 环比, `FX` → 汇率, `pricing power` → 定价权 — these are not acceptable inside card prose. First-mention parentheses are fine (`恒定汇率口径下（CC）`), then drop the English.

Same principle as the banned-phrase backstop: if you fill `data_anchor` (number + comp) and `variant_view` (≥15 chars expressing what the variant view actually is) honestly, you won't be tempted to lean on `+34%` as a substitute for thinking through 同比 vs 环比.

## Field cheat sheet (copy targets)

| JSON key | Card | Source hints |
|----------|------|----------------|
| `intro_sentence` | 1 | **The call.** `analyst_call.call` + `variant_view[0]` + 1 highest-magnitude `comp_anchor`. Fill `worker_notes.intro_sentence` first. |
| `company_focus_paragraph` | 1 yellow | **Consensus frame + the one number.** `consensus_view` + `key_number` (metric, our_estimate, consensus) + 1 `comp_anchor`. 150–165 chars; keep one operating driver as a grounding fact. |
| `background_bullets` | 2 left | **4 bullets, each = 1 number + 1 comp.** Pull from `financial_*.json` / `porter_analysis.json`; map each bullet to a Porter force (供应商/买方/新进入者/替代品/竞争强度) and anchor with peer / 历史 / guidance / consensus. |
| `industry_paragraph` | 2 left | **Porter synthesis paired with consensus-vs-variant.** `porter_analysis` industry-context + explicit “市场认为 X，我们认为 Y” framing from `consensus_view` / `variant_view`. |
| `conclusion_block` | 2 right | **Second-order variables the market is missing.** 1–2 items from `variant_view` against `consensus_view`. Forward-looking and specific, not generic. |
| `revenue_explainer_points` | 3 | **The one number + comp.** Bullet 1 = `key_number.metric` + our_estimate vs consensus. Bullets 2–3 = 2 `comp_anchors` (one each). Bullet 4 = `key_number.bridge` translated to prose. |
| `current_business_points` | 4 left | **3–4 segment facts, each with a comp.** Source: `financial_analysis.json` segments; each item needs a peer / 历史 / guidance anchor. |
| `future_watch_points` | 4 right | **Catalyst calendar.** Merge `catalysts_positive` + `catalysts_negative`; **every item must carry a `date_window`** (`YYYY-MM`, `YYYY-Qn`, `YYYY-H[12]`, or range with `..`). |
| `judgement_paragraph` | 4 | **The falsifier as verdict.** `falsifiers[0]` cast as: `未来 {horizon_months} 个月的核心验证点是 {falsifier}。` `worker_notes.judgement_paragraph.primary_quote` is **required**. |
| `brand_subheading` | 5 | `call` rendered as a 1-line subhead, e.g. `长期供给瓶颈，cautious-bias on hyperscaler capex risk`. Replaces “一句话看{公司}”. |
| `brand_statement` | 5 | **PM-soundbite.** `asymmetry` reframed for early-morning briefing voice; must include explicit `conviction` (high/medium/low or literal 1–5). `worker_notes.brand_statement.primary_quote` is **required**. |
| `memory_points` | 5 | **Exactly 3 bullets — 1 anchored number, 1 catalyst (with date), 1 falsifier.** One each, in that order. |
| `cta_line` | 5 footer | **下季验证清单.** 2–3 items pulled from `falsifiers` + nearest `catalysts_*.date_window`. Format: `下季关键验证：[item 1]、[item 2]、[item 3]。` Banned: `关注 ... 每天 ... 学`. |
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

This agent now emits **two** files side-by-side beside the HTML:

1. `<stem>.card_slots.json` — Valid JSON only, UTF-8, `schema_version: 1`. The standard slot file the renderer consumes. If you start from a **partial** `card_slots.json` produced by the logo agent, **merge** your body copy into it so **`logo_asset_path`** and **`cover_company_name_cn`** remain exactly as the logo agent set them (unless the whole package intentionally has no logo and you are filling `cover_company_name_cn` per the cheat sheet).
2. `<stem>.card_slots_worker_notes.json` — Valid JSON only, UTF-8, `schema_version: 1`. Hidden analytical fields for Cards 1–5 narrative slots. See **Cards 1–5 methodology contract → Hidden mental fields** above for required keys and per-slot rules. **Required for every run.** Must be written *before* you draft the prose; if you find yourself drafting prose and then back-filling worker_notes, you are doing it wrong.

See worked shape for `card_slots.json`: [examples/pdd_holdings_card_slots.example.json](../references/examples/pdd_holdings_card_slots.example.json).
