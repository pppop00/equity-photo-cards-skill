# Workflow Spec

This file defines the canonical workflow for turning a research report package into the fixed 6-card output. It is the contract between extraction, planning, copy generation, validation, and rendering.

The pipeline is:

0. **customer or `USER.md` sticky confirms color palette** (`macaron` | `default` | `b` | `c`) — **no ingestion, extraction, slot writing, validation, or export until confirmed**; see [SKILL.md](../SKILL.md) § 配色选择.
1. ingest
2. extract
3. normalize
4. plan card slots
5. write copy into slots
6. audit hardcoded wording and logic
7. validate (**Validator 1** — `validate_cards.py`)
8. rewrite until Validator 1 passes
9. **Validator 2** — external fact-check of all material claims in slots via web search (see [validator-2-agent.md](../agents/validator-2-agent.md)); rewrite and repeat steps 7–8 until Validator 2 passes
10. export (`generate_social_cards.py` only after Validator 1 **and** Validator 2 pass)

## 1. Input Contract

Preferred primary input:

- one report folder containing `*_Research_CN.html` plus sibling JSON files

Expected package files when available:

- **`<Company>_Research_<lang>.analyst_call.json`** — the analyst-layer sidecar from the Equity Research Skill (schema: [`analyst_call.schema.json`](../../Equity%20Research%20Skill/references/analyst_call.schema.json) in the sister repo). **Required driver for Cards 1–5.** If absent, the content production agent must abort the run rather than heuristic-extract from the HTML. Cards 1–5 slot prose maps directly to this file's `call`, `consensus_view`, `variant_view`, `key_number`, `comp_anchors`, `catalysts_positive`, `catalysts_negative`, `falsifiers`, `primary_quotes`, `asymmetry`, and `conviction` fields — see §4 per-card slot rules.
- `financial_data.json`
- `financial_analysis.json`
- `porter_analysis.json`
- `news_intel.json`, `macro_factors.json`, `prediction_waterfall.json`, and other research JSON
- one report HTML file for rendered prose, embedded chart variables, and PNG export

The workflow should assume the report package may have schema drift. It should not assume every report uses the exact same field names.

**Reading order:** `analyst_call.json` **first** (it carries the analyst layer the cards quote). HTML + financial / Porter JSON **second** for grounding numbers, segment shares, and verbatim filing quotes. News / macro JSON **third** for Card 6 Step 0 only. If only HTML is provided, locate sibling JSON in the same folder. If only JSON is provided, draft analysis/copy from it but do not export final cards until the HTML is available.

## 2. Extraction Contract

Extraction should gather raw source facts without forcing them into card language yet.

Required raw extraction buckets:

- `identity`
- `dates`
- `summary`
- `highlights`
- `risks`
- `thesis`
- `porter`
- `financials`
- `segments_or_products`
- `operational_kpis`
- `competitors`
- `five_year_change`
- `operating_geography`
- `revenue_geography`
- `forward_outlook_variables`
- `available_assets`

Extraction should preserve source detail even if some of it is not used later.

Logo acquisition starts only after palette confirmation. First inspect `card_slots.logo_asset_path`, the final output folder, and the report folder for an existing valid logo image. If no valid logo exists, search for the company's official logo, brand assets, press kit, IR media kit, or reputable official logo file. Use that official reference to regenerate a clean transparent PNG/WEBP asset at sufficient resolution (e.g. **≥840 px** wide for horizontal wordmarks at default `LAYOUT_SCALE` — see `logo_asset_dimension_issues` in `generate_social_cards.py`), and preserve its file path and source URL in working notes. Do not use screenshots, search-result thumbnails, favicons, or ticker-letter placeholders; never upscale a small raster into a “large” PNG. **Save order:** create the output folder first, copy/save the logo there (not a temp path), then set `logo_asset_path` — see [logo-production-agent.md](../agents/logo-production-agent.md) §Output for the mandatory sequence.

## 3. Normalized Report Model

Before card planning, convert source data into one canonical report object.

Minimum normalized fields:

```text
company_display_cn
company_display_en
ticker
report_date
fiscal_year
sector
industry
summary_points[]
highlight_points[]
risk_points[]
thesis
porter_industry_text
porter_forward_text
porter_scores[]
revenue
revenue_yoy
gross_profit
gross_margin
operating_income
operating_margin
net_income
net_income_yoy
net_margin
operating_cash_flow
capex
free_cash_flow
segment_mix[]
key_products[]
operational_kpis[]
competitors[]
five_year_change[]
operating_geography[]
revenue_geography[]
forward_outlook_variables[]
logo_asset_path
theme_hint
```

Normalization rules:

- compute missing YoY when current and prior values exist
- normalize margin fields to one naming convention
- normalize segment revenue to one unit convention
- convert legal names into short display names when needed
- preserve approved English product names only when helpful
- map product-heavy healthcare reports into usable product / franchise summaries

## 4. Card Planning Contract

Each card should be planned as a dictionary of fixed placeholders. Rendering should consume placeholders, not raw source data.

**Cards 1–5 are analyst notes, not HTML compression.** Their narrative slots draw from `analyst_call.json` (the analyst-layer sidecar — see §1) using the slot ↔ field mapping table in [content-production-agent.md](../agents/content-production-agent.md) § Cards 1–5 methodology contract. Card 6 keeps its existing 金融豹判断逻辑 voice (see [card6-voice.md](card6-voice.md)).

### Card 1 Slots

```text
cover_title
company_name
english_ticker_line
intro_sentence
metrics_row[3]
company_focus_paragraph
cover_company_name_cn (optional in schema; **required when `logo_asset_path` is set** — written by logo production agent together with the logo file)
logo_asset_path (optional)
```

Planning rule:

- **`intro_sentence` is the analyst's call.** Compose from `analyst_call.json.call` + `variant_view[0]` + the highest-magnitude `comp_anchor`. State the position and one anchored number; do not write a generic “market is watching X” line.
- **`company_focus_paragraph` is consensus vs the one number.** Use `consensus_view` + `key_number` (metric, our_estimate, consensus, bridge) + 1 `comp_anchor`. 150–165 characters, usually 2 complete sentences. Keep one operating driver as grounding.
- use actual metrics to support the framing, not replace it
- **`cover_company_name_cn` + `logo_asset_path`:** Logo production agent sets both when a logo is used — reconcile or translate vs HTML `.company-name-cn`, short Chinese for Card 1 red line (strip trailing `公司` in slot or rely on `display_name` in code). Later agents must not clear these keys.
- without a logo: `company_short_cn()` may use HTML `.company-name-cn` when it contains CJK, or **`cover_company_name_cn`** if the content agent fills it for English-only HTML; Validator 1 still requires CJK in the resolved string
- set `logo_asset_path` from the logo production agent's regenerated official logo asset; otherwise omit it and never synthesize a ticker-letter logo
- after export, remove logo source downloads and unused logo variants so only the `logo_asset_path` file remains

### Card 2 Slots

```text
background_bullets[4]
industry_paragraph
porter_labels[5]
porter_scores[5]
conclusion_block
```

Planning rule:

- `background_bullets` are Card 2 left-side Porter evidence — **each of the 4 bullets must include 1 number + 1 comp** (peer / 历史 / guidance / consensus). Pull facts from `financial_*.json` / `porter_analysis.json`; map each bullet to a Porter force (供应商、买方、新进入者、替代品、竞争强度) and tie the driver (concentration, switching cost, regulation, moat, capacity cycle, price war, bargaining power) to margins, pricing power, growth, or risk.
- `industry_paragraph` synthesizes the five forces **paired with explicit consensus-vs-variant framing** from `consensus_view` / `variant_view`. Read as: industry structure + “市场认为 X，我们认为 Y” — not as an industry encyclopedia entry.
- `conclusion_block` names the 1–2 second-order variables the market is missing, drawn from `variant_view` against `consensus_view`. Forward-looking and specific.

### Card 3 Slots

```text
revenue_flow_rows[5]
margin_metric_cards[3]
revenue_explainer_points[3]
```

Planning rule:

- **`revenue_explainer_points` is the one number + comp triangle.** Bullet 1 = `analyst_call.json.key_number.metric` + `our_estimate` vs `consensus`. Bullets 2–3 = two `comp_anchors` (one each — peer / 历史 / guidance). Optional bullet 4 = `key_number.bridge` translated to prose explaining the gap.
- `revenue_flow_rows` and `margin_metric_cards` come from the HTML Sankey and `financial_data.income_statement.current_year` (fallback when HTML omits net income or margin fields); this is the data-forward card.
- do not allow `0.0` net income or `--` margin cards when source financial data can compute those values
- the explanatory bullets should interpret the gap to consensus, not just restate the Sankey bars

### Card 4 Slots

```text
current_business_points[4]
future_watch_points[4]
judgement_paragraph
```

Planning rule:

- `current_business_points` — 3–4 segment facts from `financial_analysis.json`, **each with a comp** (peer / 历史 / guidance).
- `future_watch_points` — **catalyst calendar** merged from `analyst_call.json.catalysts_positive` and `catalysts_negative`. **Every item must carry a `date_window`** (`YYYY-MM`, `YYYY-Qn`, `YYYY-H[12]`, or range with `..`).
- `judgement_paragraph` casts `falsifiers[0]` as the verdict: `未来 {horizon_months} 个月的核心验证点是 {falsifier}。` `worker_notes.judgement_paragraph.primary_quote` is required (CFO/CEO/filing).

### Card 5 Slots

```text
brand_subheading
brand_statement
memory_points[3]
cta_line
```

Planning rule:

- `brand_subheading` — `analyst_call.json.call` rendered as a 1-line subhead (e.g. `长期供给瓶颈，cautious-bias on hyperscaler capex risk`).
- `brand_statement` — `asymmetry` reframed as a PM-soundbite; **must include explicit `conviction`** (high / medium / low or literal 1–5). `worker_notes.brand_statement.primary_quote` is required.
- `memory_points` — exactly 3 bullets: 1 anchored number, 1 catalyst (with date), 1 falsifier. One each, in that order.
- `cta_line` — 下季验证清单: 2–3 items pulled from `falsifiers` + nearest `catalysts_*.date_window`. Format: `下季关键验证：[item 1]、[item 2]、[item 3]。` Banned: `关注 ... 每天 ... 学`.

### Card 6 Slots

```text
post_title
post_content_lines[4]
hashtags[3..5 authored, renderer appends #A股/#美股; final max 7]
```

Planning rule:

- this should follow the 金融豹判断逻辑 in [card6-voice.md](card6-voice.md): grounded, educational, mechanism-first, and connected to competitors, past-five-year changes, future outlook, operating/revenue geography, and recent company / industry / policy / market context — not clickbait, not sell-side boilerplate, not marker-stuffed prompt output, and not forced surface imitation
- every line must be publishable without additional editing
- **`post_content_lines`:** exactly four lines as **three statements + one question**; ground facts in the report, include at least one financial / operating anchor and one current-context anchor, analyze competitors, past-five-year changes, future outlook, and operating/revenue geography where material, and explain the hidden insight with the same diagnostic logic as 金融豹大白话 — see [content-production-agent.md](../agents/content-production-agent.md) Card 6, [card6-voice.md](card6-voice.md), and `CARD6_EDUCATIONAL_MARKERS` in `generate_social_cards.py`
- **`post_title`:** must start with `一天吃透一家公司：`; after the colon use the company short name
- **`hashtags`:** author 3–5 company/industry/topic tags; renderer guarantees final `#A股` and `#美股`

## 5. Copywriting Rules

When turning slots into copy:

- facts first
- interpretation second
- filler never
- character budget before sentence count

Required style rules:

- publishable Chinese prose
- complete sentences
- concise but not skeletal
- strong human reasoning aligned with [card6-voice.md](card6-voice.md) for Card 6
- voice consistency may be standardized, but substantive claims must be derived from the current report's extracted facts
- no internal strategy notes
- no clipped thesis fragments
- no generic industry filler that could fit any company

Copy priority:

1. say what the company actually does
2. say what drives the numbers now
3. say what the market is really watching
4. say why the next 2 to 3 years matter

## 6. Validation Loop

Validation is not a final polish step. It is part of generation.
Hardcode and logic audit runs before **Validator 1**, not after export.

**Validator 1** (`validate_cards.py`) covers structure, layout, and internal consistency with the report package. **Validator 2** ([validator-2-agent.md](../agents/validator-2-agent.md)) runs only after Validator 1 passes and checks **external** factual accuracy via web search before any PNG export.

For each failed **Validator 1** run:

1. identify the failing slot
2. rewrite the slot, not the entire report
3. re-run `validate_cards.py`
4. repeat until Validator 1 passes

Then run **Validator 2**. If any public fact is wrong, fix slots (and re-run Validator 1), then Validator 2 again, until both pass.

Rewrite order:

1. slot meaning
2. slot completeness
3. slot density
4. slot tone
5. slot length

If a slot is too empty:

- add one more factual clause or interpretive clause
- do not immediately shrink the text size

If a slot is too long:

- remove repetition
- compress phrasing
- preserve the central idea and metrics
- obey the slot's character budget before relying on max-lines clipping

If a slot sounds dead:

- rewrite with a sharper market-facing framing
- keep the same facts

## 7. What Should Not Trigger A New Template

These should be handled by extraction, normalization, or planning, not by creating a new company-specific hardcoded template:

- different field names for the same metric
- different legal company names
- product-led vs segment-led business mix
- missing direct YoY fields when current and prior values exist
- healthcare reports using products instead of segments
- cloud / software reports using business units instead of product SKUs

## 8. What May Require A New Planner Branch

Add a new planner branch only when a category repeatedly needs different framing logic, for example:

- ad platform economics
- EV + autonomy + energy systems
- enterprise software / cloud
- branded pharma / biotech
- consumer marketplace / e-commerce

A planner branch should change emphasis and narrative framing, not bypass the normalized slot contract.

## 9. Export Contract

The renderer should only receive already-planned slot content.

Expected final output:

- `01_cover.png`
- `02_background_industry.png`
- `03_revenue.png`
- `04_business_outlook.png`
- `05_brand.png`
- `06_post_copy.png`

If **Validator 1** or **Validator 2** fails, do not export.

## 10. Standard copy pipeline (only path; enforced in CLI)

**Every** export uses **`--slots`** and a P0-recorded **`--palette`** (`macaron` | `default` | `b` | `c`). Incomplete JSON is rejected at load time (`assert_card_slots_complete` in `scripts/generate_social_cards.py`) so body copy cannot silently fall back to `company_theme` / `fit_copy` heuristics.

**Required slot keys (non-empty; list lengths as shown):** `intro_sentence`, `company_focus_paragraph`, `background_bullets` (≥4), `industry_paragraph`, `conclusion_block`, `revenue_explainer_points` (≥3), `current_business_points` (≥4), `future_watch_points` (≥4), `judgement_paragraph`, `brand_statement`, `memory_points` (≥3), `post_title`, `post_content_lines` (≥4), `hashtags` (≥3). **`porter_scores`** is optional (exactly five integers if present); otherwise Porter scores come from the HTML package.

**Standard flow (every new `*_Research_CN.html`):**

1. **Content production agent** writes two files beside the HTML — see [content-production-agent.md](../agents/content-production-agent.md) and [card-slots.schema.json](./card-slots.schema.json):
   - **`<stem>.card_slots.json`** — the slot file the renderer consumes.
   - **`<stem>.card_slots_worker_notes.json`** — parallel hidden analytical fields for Cards 1–5 narrative slots; written **before** the prose. Schema documented in §11 below.
2. **Layout fill agent** refines copy per [design-spec.md](./design-spec.md) and [validation-agent.md](../agents/validation-agent.md) (Validator 1 policy).
3. `python3 scripts/validate_cards.py --input …/Report_CN.html --slots … --palette <confirmed_palette>` until clean (**Validator 1**).
4. **Validator 2:** follow [validator-2-agent.md](../agents/validator-2-agent.md) — web-search every material fact in the cards; fix copy and repeat step 3 until **both** Validator 1 and Validator 2 pass.
5. `python3 scripts/generate_social_cards.py --input …/Report_CN.html --slots … --palette <confirmed_palette>` using the same palette used by Validator 1.

**`--slots` argument:** For **one** HTML file, pass the JSON file path **or** the **folder** that contains `<stem>.card_slots.json`. For **several** HTML files under `--input`, `--slots` **must** be a **directory** containing one `<stem>.card_slots.json` per HTML.

Hand-off overview: [agent-slot-pipeline.md](../agents/agent-slot-pipeline.md).

**流程图（Mermaid）:** [workflow-flowchart.md](./workflow-flowchart.md)

Example (PDD-shaped): [examples/pdd_holdings_card_slots.example.json](./examples/pdd_holdings_card_slots.example.json).

## 11. `card_slots_worker_notes.json` schema

A parallel JSON file produced by the content production agent for **every** Cards 1–5 run. It captures the analytical substrate the writer pulled from `analyst_call.json` *before* drafting slot prose, so Validator 1 / Validator 2 can confirm the writer did not skip straight to rhetoric.

**File name:** `<Company>_Research_<lang>.card_slots_worker_notes.json` (saved beside `card_slots.json`).

**Top-level shape:**

```json
{
  "schema_version": 1,
  "intro_sentence":           { "data_anchor": "...", "variant_view": "...", "falsifier": "...", "primary_quote": { ... } },
  "company_focus_paragraph":  { "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "conclusion_block":         { "data_anchor": "...", "variant_view": "...", "falsifier": "..." },
  "revenue_explainer_points": { "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "judgement_paragraph":      { "data_anchor": "...", "variant_view": "...", "falsifier": "...", "primary_quote": { ... } },
  "brand_statement":          { "data_anchor": "...", "variant_view": "...", "primary_quote": { ... } }
}
```

**Required keys per slot block:**

- `data_anchor` (string, ≥10 chars) — must contain a number and at least one comp keyword (`peer`, `历史`, `guidance`, `consensus`).
- `variant_view` (string, ≥15 chars) — one specific divergence from consensus with a stated mechanism.
- **At least one** of:
  - `falsifier` (string, ≥20 chars) — observable event in a specified time window.
  - `primary_quote` (object with `speaker`, `venue`, `quote`, `url_or_filing`) — copied from `analyst_call.json.primary_quotes`.
  - `catalyst_with_date` (object with `event`, `date_window` matching `^[0-9]{4}(-(Q[1-4]|[0-9]{2}|H[12]))$` or a range with `..`, and `implication`).

**`primary_quote` is required (not optional)** for `brand_statement` and `judgement_paragraph`. These slots carry analyst authority; if no quote is available, write `[TODO: speaker]` so the validator flags it.

**Array slots** (Card 2 `background_bullets`, Card 4 `current_business_points` / `future_watch_points`, Card 5 `memory_points`) — the worker_notes entry is **one** set of fields covering the array as a whole, not one block per bullet. These may be added as additional top-level keys in the same JSON file when the writer wants the audit trail per array.

Card 6 slots are **not** represented in `card_slots_worker_notes.json` — Card 6's substrate is Step 0 news/macro lookup plus [card6-voice.md](card6-voice.md), not the analyst-call sidecar.
