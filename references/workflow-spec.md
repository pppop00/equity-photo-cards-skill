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

- `financial_data.json`
- `financial_analysis.json`
- `porter_analysis.json`
- `news_intel.json`, `macro_factors.json`, `prediction_waterfall.json`, and other research JSON
- one report HTML file for rendered prose, embedded chart variables, and PNG export

The workflow should assume the report package may have schema drift. It should not assume every report uses the exact same field names.

Read JSON first. JSON is the canonical source for numeric facts, margins, segments, cash flow, Porter details, and latest operating updates. Read HTML second for identity/date, rendered section prose, embedded data blocks such as `sankeyActualData`, and the render scaffold. If only HTML is provided, locate sibling JSON in the same folder. If only JSON is provided, draft analysis/copy from it but do not export final cards until the HTML is available.

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
- `available_assets`

Extraction should preserve source detail even if some of it is not used later.

Logo acquisition is part of extraction and must use web search. Do not rely on local logo discovery. Search for the company's official logo, brand assets, press kit, IR media kit, or reputable official logo file. Use that official reference to regenerate a clean transparent PNG/WEBP asset at sufficient resolution (e.g. **≥840 px** wide for horizontal wordmarks at default `LAYOUT_SCALE` — see `logo_asset_dimension_issues` in `generate_social_cards.py`), and preserve its file path and source URL in working notes. Do not use screenshots, search-result thumbnails, favicons, or ticker-letter placeholders; never upscale a small raster into a “large” PNG. **Save order:** create the output folder first, save the logo there (not in the source report folder), then set `logo_asset_path` — see [logo-production-agent.md](../agents/logo-production-agent.md) §Output for the mandatory sequence.

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

- `intro_sentence` should state the central tension or what the market is really watching
- `company_focus_paragraph` should explain the current setup in 150–165 characters, usually 2 complete sentences
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

- `background_bullets` explain company setup, scale, mix, and economics
- `industry_paragraph` explains how the industry works and where current pressure sits
- `conclusion_block` compresses the Porter takeaway into one short judgement

### Card 3 Slots

```text
revenue_flow_rows[5]
margin_metric_cards[3]
revenue_explainer_points[3]
```

Planning rule:

- this is the data-forward card
- use `financial_data.income_statement.current_year` as fallback when the HTML Sankey omits net income or margin fields
- do not allow `0.0` net income or `--` margin cards when source financial data can compute those values
- the explanatory bullets should interpret the flow, not repeat the numbers blindly

### Card 4 Slots

```text
current_business_points[4]
future_watch_points[4]
judgement_paragraph
```

Planning rule:

- left column explains where money is made now
- right column explains what changes the story over the next 2 to 3 years
- judgement compresses the full card into one investable view

### Card 5 Slots

```text
brand_subheading
brand_statement
memory_points[3]
cta_line
```

Planning rule:

- `brand_statement` is the strongest single-line company take
- `memory_points` should help the reader remember the company in 3 facts or frames

### Card 6 Slots

```text
post_title
post_content_lines[4]
hashtags[3..5 authored, renderer appends #A股/#美股; final max 7]
```

Planning rule:

- this should read like a **Chinese forum / 贴吧** hot thread: emotional, meme-adjacent, argumentative — **not** sell-side deck tone
- every line must be publishable without additional editing
- **`post_content_lines`:** exactly four lines as **three statements + one question**; ground facts in the report but **voice** should feel like **recent gossip + hot takes** (products, news, sentiment — good, bad, funny, angry), and dig into the hidden insight instead of just recapping numbers — see [content-production-agent.md](../agents/content-production-agent.md) Card 6 and `CARD6_COLLOQUIAL_MARKERS` in `generate_social_cards.py`
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
- strong human voice
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

1. **Content production agent** writes **`html_stem.card_slots.json`** beside the HTML — see [content-production-agent.md](../agents/content-production-agent.md) and [card-slots.schema.json](./card-slots.schema.json).
2. **Layout fill agent** refines copy per [design-spec.md](./design-spec.md) and [validation-agent.md](../agents/validation-agent.md) (Validator 1 policy).
3. `python3 scripts/validate_cards.py --input …/Report_CN.html --slots … --palette <confirmed_palette>` until clean (**Validator 1**).
4. **Validator 2:** follow [validator-2-agent.md](../agents/validator-2-agent.md) — web-search every material fact in the cards; fix copy and repeat step 3 until **both** Validator 1 and Validator 2 pass.
5. `python3 scripts/generate_social_cards.py --input …/Report_CN.html --slots … --palette <confirmed_palette>` using the same palette used by Validator 1.

**`--slots` argument:** For **one** HTML file, pass the JSON file path **or** the **folder** that contains `<stem>.card_slots.json`. For **several** HTML files under `--input`, `--slots` **must** be a **directory** containing one `<stem>.card_slots.json` per HTML.

Hand-off overview: [agent-slot-pipeline.md](../agents/agent-slot-pipeline.md).

**流程图（Mermaid）:** [workflow-flowchart.md](./workflow-flowchart.md)

Example (PDD-shaped): [examples/pdd_holdings_card_slots.example.json](./examples/pdd_holdings_card_slots.example.json).
