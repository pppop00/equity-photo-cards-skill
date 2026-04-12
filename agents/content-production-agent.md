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
2. **No disclaimers in body slots:** Do not paste rating boilerplate (“不构成投资建议…”) into card bodies; keep tone analytical like the report prose **except Card 6** (`post_title`, `post_content_lines`, `hashtags`), where **贴吧/嘴炮楼**口语 is required — see **Card 6** below.
3. **Completeness:** Prefer **full sentences** ending in 。！？ — the validator rejects ellipsis and half sentences.
4. **Card 2 Porter bars:** If you set `porter_scores`, supply **exactly five** integers `1..5` in order: 供应商、买方、新进入者、替代品、竞争强度. If unsure, **omit** `porter_scores` so the renderer keeps auto-extracted scores.
5. **Logo asset:** Use the `logo_asset_path` produced by [logo-production-agent.md](./logo-production-agent.md). Do not search local folders for logos, and do not use screenshots or ticker-letter placeholders.

## Field cheat sheet (copy targets)

| JSON key | Card | Source hints |
|----------|------|----------------|
| `intro_sentence` | 1 | Core tension: what the market prices *now* — often thesis + last summary paragraph. |
| `company_focus_paragraph` | 1 yellow | Compress 2–3 `summary-para` sentences into **150–165 characters**; keep revenue/profit plus one operating driver. |
| `background_bullets` | 2 left | Highlights + first summary facts; exactly **4** bullets later validated. |
| `industry_paragraph` | 2 left | Porter “industry” block + sector context from HTML. |
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
| `post_title` | 6 | **贴吧味标题：** 像热帖标题一样勾人，不要研报目录体。 |
| `post_content_lines` | 6 | **Exactly four** complete sentences. See **Card 6** — colloquial markers / `CARD6_COLLOQUIAL_MARKERS` in `generate_social_cards.py`. |
| `hashtags` | 6 | 3–5 tags; renderer adds `#`. |

### Card 6 — social post image (this agent owns the copy)

Write like a **中国贴吧热帖** or **嘴炮楼楼主**：有梗、有情绪、像真人在冲浪吐槽或兴奋安利 — **不是**卖方路演腔，**不是**把前五张图再念一遍。

The validator still requires **four** complete `post_content_lines`. Each line must pass **`card6_line_sounds_human`** in `generate_social_cards.py`: either a standard **human marker** (`说白了`, `真要看`, `别看`, `本质上`, `眼下`, …) **or** a token from **`CARD6_COLLOQUIAL_MARKERS`** (e.g. 这波、离谱、吃瓜、吐槽、笑死、好家伙、上头、麻了、整活、阴阳、蚌埠住了、破防、扎心、翻车、爆款、杀疯了 — extend in code if needed). **Vary** openers — four lines all starting with “说白了，” reads robotic.

**Content mix (ground everything in the report or sibling JSON):**

- **最近有意思的事：** 产品上新、业务线打架、管理层表态、竞品名场面 — 用贴吧语气讲出来。
- **最近火的东西：** 爆款 SKU、爆款功能、流量入口 — 哪条在报告里真火、哪条被高估，都可以怼一句。
- **最近发生的事：** 政策、舆情、监管、价格战、组织变动 — **好的坏的、开心的搞笑的愤怒的阴阳的** 都可以，只要事实锚点还在 HTML/JSON 里。
- **禁止：** 元叙事（“前五张图说了…”）、正确的废话、排比式年报摘要。若必须带数字，用 **“这数字离谱在…”** 这种帖感，而不是复读 YoY。

`post_title` 要让人 **忍不住点进来**；`hashtags` 可以偏话题梗，但仍需与该公司/行业相关。

## Length

Do **not** micro-fit in Agent A. Write natural copy; Agent B (layout) will compress to [design-spec.md](../references/design-spec.md) budgets. If a slot is obviously long, still prefer substance — B will cut repetition first.

## Output

Valid JSON only, UTF-8, `schema_version: 1`. Save next to the report or in CI artifacts as `card_slots.json`.

See worked shape: [examples/pdd_holdings_card_slots.example.json](../references/examples/pdd_holdings_card_slots.example.json).
